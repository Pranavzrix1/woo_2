from fastapi import APIRouter, HTTPException, Depends
from app.models.requests import ChatRequest
from app.dependencies import (
    get_intent_handler, get_general_agent, get_category_agent
)
from app.services.intent_handler import IntentHandler
from app.agents.sales_executive_agent import SalesExecutiveAgent
from app.agents.product_finder_agent import ProductFinderAgent
from app.agents.general_agent import GeneralAgent
from app.agents.category_finder_agent import CategoryFinderAgent

router = APIRouter()


@router.post("/")
async def chat_endpoint(
    request: ChatRequest,
    intent_service: IntentHandler = Depends(get_intent_handler),
    general_agent: GeneralAgent = Depends(get_general_agent),
    category_agent: CategoryFinderAgent = Depends(get_category_agent)
):
    try:
        # Input validation is handled by Pydantic model
        intent, confidence = intent_service.classify_intent(request.message)
        print(f"[chat] intent='{intent}', confidence='{confidence}', message='{request.message[:120]}'")

        # AUTO override: if message looks like a buying/recommendation request, treat as sales_executive
        if intent != "sales_executive":
            _m = (request.message or "").lower()
            _kw = ("buy", "purchase", "recommend", "suggest", "looking for", "need", "want")
            if any(k in _m for k in _kw):
                intent = "sales_executive"

        if intent == "product_finder":
            product_agent = ProductFinderAgent()
            response = await product_agent.process(request.message)

        elif intent == "category_finder":
            response = await category_agent.process(request.message)

        elif intent == "sales_executive":
            sales_agent = SalesExecutiveAgent()
            response = await sales_agent.process(request.message, user_id=request.user_id)

        else:
            # Use LLM for general queries
            response = await general_agent.process(request.message)
        
        # persist user message + assistant reply (best-effort, background)
        import asyncio, datetime, uuid
        from app.services.elasticsearch_service import ElasticsearchService
        from app.services.embedding_service import EmbeddingService
        from app.services.product_service import ProductService

        async def _index_chat_async(user_id: str, text: str):
            try:
                es = ElasticsearchService()
                emb_svc = EmbeddingService()
                prod = ProductService()
                # create a one-line summary (LLM wrapper); fallback to truncated text
                try:
                    summary = await prod.generate_short_text(f"Summarize in one short sentence: {text}", max_tokens=40)
                except Exception:
                    summary = (text[:200] + "...") if len(text) > 200 else text

                # attempt embedding (optional)
                embedding = None
                try:
                    embedding = await emb_svc.get_embedding(text)
                except Exception:
                    embedding = None

                doc = {
                    "user_id": user_id,
                    "text": text,
                    "summary": summary,
                    "created_at": datetime.datetime.utcnow().isoformat()
                }
                if embedding:
                    doc["embedding"] = embedding

                # index without forcing a refresh (non-blocking)
                await es.es.index(index="chat_history", id=str(uuid.uuid4()), body=doc, refresh=False)
            except Exception:
                # swallow errors so we don't break the chat response
                pass

        if request.user_id:
            try:
                # index user message and assistant reply in background
                asyncio.create_task(_index_chat_async(request.user_id, request.message))
                _reply_text = response if isinstance(response, str) else str(response)
                asyncio.create_task(_index_chat_async(request.user_id, _reply_text))
            except Exception:
                pass

        # ensure nested objects are JSON serializable
        from fastapi.encoders import jsonable_encoder
        from fastapi.responses import JSONResponse

        payload = {
            "response": jsonable_encoder(response),
            "intent": intent,
            "confidence": confidence
        }
        return JSONResponse(content=payload)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")