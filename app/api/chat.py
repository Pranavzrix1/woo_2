from fastapi import APIRouter
from pydantic import BaseModel
from app.services.intent_handler import IntentHandler

from typing import Optional

from app.agents.sales_executive_agent import SalesExecutiveAgent
from app.agents.product_finder_agent import ProductFinderAgent
from app.agents.general_agent import GeneralAgent
from app.agents.category_finder_agent import CategoryFinderAgent
from app.agents.multilingual_agent import MultilingualAgent


class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    message: str
    context: Optional[dict] = None
    last_viewed_product: Optional[dict] = None
    cart: Optional[dict] = None
    user_email: Optional[str] = None
    session_id: Optional[str] = None


router = APIRouter()


@router.post("")
@router.post("/")
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint: classify intent, route to appropriate agent.
    If a coupon-related query is detected, it routes to CouponAgent and returns immediately.
    """
    intent_service = IntentHandler()

    # First detect language and translate for intent classification
    multilingual_agent = MultilingualAgent()
    
    # Get English version for intent detection
    try:
        lang_result = multilingual_agent.language_processor(user_query=request.message)
        english_query = lang_result.english_query
        detected_language = lang_result.detected_language
    except:
        english_query = request.message
        detected_language = 'en'
    
    # classify intent on English query
    intent, confidence = intent_service.classify_intent(english_query)
    print(f"[chat] intent='{intent}', confidence='{confidence}', lang='{detected_language}', message='{request.message[:120]}'")
    
    # Simple session memory for coupon context
    session_memory = {}
    if hasattr(request, 'session_id') and request.session_id:
        if not hasattr(chat_endpoint, '_sessions'):
            chat_endpoint._sessions = {}
        session_memory = chat_endpoint._sessions.get(request.session_id, {})
        
        # Remember last coupon query
        if intent == 'coupon':
            session_memory['last_coupon_query'] = request.message
            session_memory['coupon_context'] = True
        
        chat_endpoint._sessions[request.session_id] = session_memory

    # --- coupon routing: check on English query ---
    msg_lower = english_query.lower()
    coupon_keywords = ("coupon", "discount", "promo", "promocode", "code", "sale", "offer", "voucher")
    coupon_phrases = ("can i use", "how much will i save", "calculate price", "final price", "use on", "apply to", 
                     "be applied to", "savings with", "discount for", "final amount", "final cost")
    is_coupon_query = any(k in msg_lower for k in coupon_keywords) or any(p in msg_lower for p in coupon_phrases)

    if is_coupon_query or intent == "coupon":
        try:
            from app.agents.coupon_agent import CouponAgent
            coupon_agent = CouponAgent()

            # Build minimal chat_context from request.context or other fields
            chat_context = {}
            if getattr(request, "context", None):
                chat_context = request.context
            if hasattr(request, "last_viewed_product"):
                chat_context["last_viewed_product"] = request.last_viewed_product
            if hasattr(request, "cart"):
                chat_context["cart"] = request.cart

            user_email = getattr(request, "user_email", None)

            # Let coupon agent handle the query
            agent_res = await coupon_agent.handle_query(chat_context or {}, request.message, user_email=user_email)

            # agent_res expected to be {"text": "...", "pitches": [...]}
            response_text = agent_res.get("text") if isinstance(agent_res, dict) else str(agent_res)
            intent = "coupon"
            confidence = 0.9

            # include pitches if present
            result = {"response": response_text, "intent": intent, "confidence": confidence}
            if isinstance(agent_res, dict) and "pitches" in agent_res:
                result["pitches"] = agent_res.get("pitches")

            # return immediately so later agents don't overwrite
            return result
        except Exception as e:
            # If coupon agent fails, fallback to previous pipeline
            print(f"CouponAgent error: {e}")
    # --- end coupon routing override ---

    # AUTO override: check English query for sales intent
    if intent != "sales_executive":
        _kw = ("buy", "purchase", "recommend", "suggest", "looking for", "need", "want", "show me", "find me")
        if any(k in english_query.lower() for k in _kw):
            intent = "sales_executive"
    
    # Build context for multilingual agent
    context = {
        'user_id': request.user_id,
        'session_id': getattr(request, 'session_id', None),
        'last_viewed_product': getattr(request, 'last_viewed_product', None),
        'cart': getattr(request, 'cart', None),
        'user_email': getattr(request, 'user_email', None)
    }
    
    # Process through multilingual agent
    try:
        ml_result = await multilingual_agent.process(request.message, intent, context)
        
        # Normalize response structure for frontend compatibility
        if isinstance(ml_result, dict) and 'response' in ml_result:
            nested_response = ml_result['response']
            # If nested response has recommendations, use it directly
            if isinstance(nested_response, dict) and 'recommendations' in nested_response:
                result = {
                    "response": nested_response,
                    "intent": intent, 
                    "confidence": confidence
                }
                if detected_language != 'en':
                    result["detected_language"] = detected_language
                return result
            else:
                response = nested_response
        else:
            response = ml_result

        # Final return with language info
        result = {"response": response, "intent": intent, "confidence": confidence}
        if detected_language != 'en':
            result["detected_language"] = detected_language
        return result
        
    except Exception as e:
        print(f"Multilingual processing error: {e}")
        # Fallback to English processing
        from app.agents.general_agent import GeneralAgent
        general_agent = GeneralAgent()
        response = await general_agent.process(english_query)
        return {"response": response, "intent": "general", "confidence": 0.5}






# from fastapi import APIRouter
# from pydantic import BaseModel
# from app.services.intent_handler import IntentHandler

# from typing import Optional
# from app.agents.sales_executive_agent import SalesExecutiveAgent

# from app.agents.product_finder_agent import ProductFinderAgent
# from app.agents.general_agent import GeneralAgent
# from app.agents.category_finder_agent import CategoryFinderAgent

# # from app.agents.product_finder_agent import ProductFinderAgent  # ← ADD THIS


# class ChatRequest(BaseModel):
#     message: str
#     user_id: Optional[str] = None

# router = APIRouter()

# intent_service = IntentHandler()
# general_agent = GeneralAgent()
# category_agent = CategoryFinderAgent()

# @router.post("")
# @router.post("/")
# async def chat_endpoint(request: ChatRequest):

#     # intent, confidence = await intent_service.classify_intent(request.message)
#     intent, confidence = intent_service.classify_intent(request.message)
#     print(f"[chat] intent='{intent}', confidence='{confidence}', message='{request.message[:120]}'")


#     # --- coupon routing: quick keyword-based override ---
#     msg_lower = (request.message or "").lower()
#     coupon_keywords = ("coupon", "discount", "promo", "promocode", "code", "sale", "offer", "voucher")
#     is_coupon_query = any(k in msg_lower for k in coupon_keywords)

#     if is_coupon_query or intent == "coupon":
#         try:
#             from app.agents.coupon_agent import CouponAgent
#             coupon_agent = CouponAgent()

#             # Build minimal chat_context from request.context or other fields
#             chat_context = {}
#             if getattr(request, "context", None):
#                 chat_context = request.context
#             if hasattr(request, "last_viewed_product"):
#                 chat_context["last_viewed_product"] = request.last_viewed_product
#             if hasattr(request, "cart"):
#                 chat_context["cart"] = request.cart

#             user_email = getattr(request, "user_email", None)

#             agent_res = await coupon_agent.handle_query(chat_context or {}, request.message, user_email=user_email)

#             response = agent_res.get("text") if isinstance(agent_res, dict) else str(agent_res)
#             intent = "coupon"
#             confidence = 0.9
#         except Exception as e:
#             # Log and continue to fallback
#             print(f"CouponAgent error: {e}")
#     # --- end coupon routing override ---



#     # AUTO override: if message looks like a buying/recommendation request, treat as sales_executive
#     if intent != "sales_executive":
#         _m = (request.message or "").lower()
#         _kw = ("buy", "purchase", "recommend", "suggest", "looking for", "need", "want")
#         if any(k in _m for k in _kw):
#             intent = "sales_executive"

#     if intent == "product_finder":
#         product_agent = ProductFinderAgent()  # Use the intelligent agent
#         response = await product_agent.process(request.message)

#     elif intent == "category_finder":  # ← ADD THIS
#         response = await category_agent.process(request.message)

#     elif intent == "sales_executive":
#         sales_agent = SalesExecutiveAgent()
#         response = await sales_agent.process(request.message, user_id=request.user_id)


#     else:
#         # Use LLM for general queries

#         response = await general_agent.process(request.message)
    
#     # persist user message + assistant reply (best-effort, background)
#     import asyncio, datetime, uuid
#     from app.services.elasticsearch_service import ElasticsearchService
#     from app.services.embedding_service import EmbeddingService
#     from app.services.product_service import ProductService

#     async def _index_chat_async(user_id: str, text: str):
#         try:
#             es = ElasticsearchService()
#             emb_svc = EmbeddingService()
#             prod = ProductService()
#             # create a one-line summary (LLM wrapper); fallback to truncated text
#             try:
#                 summary = await prod.generate_short_text(f"Summarize in one short sentence: {text}", max_tokens=40)
#             except Exception:
#                 summary = (text[:200] + "...") if len(text) > 200 else text

#             # attempt embedding (optional)
#             embedding = None
#             try:
#                 embedding = await emb_svc.get_embedding(text)
#             except Exception:
#                 embedding = None

#             doc = {
#                 "user_id": user_id,
#                 "text": text,
#                 "summary": summary,
#                 "created_at": datetime.datetime.utcnow().isoformat()
#             }
#             if embedding:
#                 doc["embedding"] = embedding

#             # index without forcing a refresh (non-blocking)
#             await es.es.index(index="chat_history", id=str(uuid.uuid4()), body=doc, refresh=False)
#         except Exception:
#             # swallow errors so we don't break the chat response
#             pass

#     if request.user_id:
#         try:
#             # index user message and assistant reply in background
#             asyncio.create_task(_index_chat_async(request.user_id, request.message))
#             _reply_text = response if isinstance(response, str) else str(response)
#             asyncio.create_task(_index_chat_async(request.user_id, _reply_text))
#         except Exception:
#             pass

#         # ensure nested objects are JSON serializable
#     from fastapi.encoders import jsonable_encoder
#     from fastapi.responses import JSONResponse

#     payload = {
#         "response": jsonable_encoder(response),
#         "intent": intent,
#         "confidence": confidence
#     }
#     return JSONResponse(content=payload)

