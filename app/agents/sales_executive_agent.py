# app/agents/sales_executive_agent.py
from typing import List, Dict, Any, Optional
import logging
import asyncio

from app.services.elasticsearch_service import ElasticsearchService
from app.services.embedding_service import EmbeddingService
from app.services.product_service import ProductService

# Module logger: debug for development; lower in production
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _parse_llm_json_or_fallback(text: str) -> Dict[str, Any]:
    """
    Try to parse LLM output as JSON. If that fails, attempt to extract a JSON blob.
    If still failing, fall back to a simple line-based heuristic:
      - first non-empty line -> pitch
      - subsequent lines that start with '-' -> recommendations (title-only)
    Returns a dict with keys: pitch, recommendations (list), raw.
    """
    import json, re
    if text is None:
        return {"pitch": "", "recommendations": [], "raw": ""}

    # try plain JSON first
    try:
        parsed = json.loads(text)
        # normalize if parsed is something else
        if isinstance(parsed, dict):
            # ensure keys exist
            return {
                "pitch": parsed.get("pitch", ""),
                "recommendations": parsed.get("recommendations", []),
                "raw": text,
            }
        # if model returned list or string, coerce
        if isinstance(parsed, list):
            return {"pitch": "", "recommendations": parsed, "raw": text}
        return {"pitch": str(parsed), "recommendations": [], "raw": text}
    except Exception:
        pass

    # try to extract first JSON object inside text
    try:
        m = re.search(r'(\{.*\})', text, re.S)
        if m:
            parsed = json.loads(m.group(1))
            if isinstance(parsed, dict):
                return {
                    "pitch": parsed.get("pitch", ""),
                    "recommendations": parsed.get("recommendations", []),
                    "raw": text,
                }
    except Exception:
        pass

    # heuristic fallback
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    pitch = lines[0] if lines else ""
    recs: List[Dict[str, Any]] = []
    for ln in lines[1:6]:
        if ln.startswith("-"):
            recs.append({"id": None, "title": ln.lstrip("- ").strip(), "reason": ""})
        else:
            # if line doesn't start with '-', still consider it a candidate title
            recs.append({"id": None, "title": ln.strip(), "reason": ""})
    return {"pitch": pitch, "recommendations": recs, "raw": text}


class SalesExecutiveAgent:
    """
    Sales executive agent:
     - uses past chat context (via ElasticsearchService.fetch_relevant_chats)
     - asks the LLM for a short sales pitch + JSON recommendations
     - parses LLM output robustly
     - if no recs provided by LLM, uses ES fallback search
     - enriches recommendations by resolving to product records (product_service / ES)
    """

    def __init__(
        self,
        es: Optional[ElasticsearchService] = None,
        embed: Optional[EmbeddingService] = None,
        product_svc: Optional[ProductService] = None,
        top_k: int = 5,
    ):
        self.es = es or ElasticsearchService()
        self.embed = embed or EmbeddingService()
        self.product_svc = product_svc or ProductService()
        self.top_k = top_k

    async def process(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        logger.debug("SalesExecutiveAgent.process called; user_id=%s query=%s", user_id, (query or "")[:200])

        # 1) retrieve relevant past chats (best-effort)
        past: List[Dict[str, Any]] = []
        if user_id:
            try:
                logger.debug("Fetching past chats for user_id=%s (k=%d)", user_id, self.top_k)
                past = await self.es.fetch_relevant_chats(user_id=user_id, query_text=query, k=self.top_k)
                logger.debug("Fetched %d past chats", len(past) if past else 0)
            except Exception as e:
                logger.exception("Failed to fetch_relevant_chats: %s", e)
                past = []

        # 2) build strict prompt (ask for JSON)
        prompt_parts = [
            "You are a helpful sales executive. Produce EXACT JSON only with keys: 'pitch' (1-2 short sentences) and 'recommendations' (list of objects with keys 'title', optional 'id_hint', and 'reason').",
            "If you cannot suggest products, return an empty 'recommendations' list.",
            "Current user message:",
            query or "",
        ]
        if past:
            prompt_parts.append("Relevant past interactions (summaries):")
            for p in past:
                prompt_parts.append(f"- {p.get('summary') or p.get('snippet') or p.get('text','')}")
        prompt_parts.append("Return only valid JSON.")
        prompt = "\n".join(prompt_parts)

        logger.debug("SalesAgent prompt:\n%s", prompt)

        # 3) call LLM via product_service (centralized wrapper)
        try:
            llm_text = await self.product_svc.generate_short_text(prompt=prompt, max_tokens=350)
            logger.debug("LLM returned (len=%d)", len(llm_text) if llm_text else 0)
        except Exception as e:
            logger.exception("LLM call failed: %s", e)
            llm_text = '{"pitch":"I can help with that.","recommendations": []}'

        # 4) parse LLM output robustly
        parsed = _parse_llm_json_or_fallback(llm_text)
        logger.debug("Parsed LLM output: %s", parsed)

        # normalize recommendations to list of dicts with at least 'title'
        raw_recs = parsed.get("recommendations") or []
        normalized_recs: List[Dict[str, Any]] = []
        for item in raw_recs:
            if isinstance(item, str):
                normalized_recs.append({"id": None, "title": item, "reason": ""})
            elif isinstance(item, dict):
                # ensure minimal shape
                title = item.get("title") or item.get("name") or item.get("id_hint") or item.get("id") or ""
                normalized_recs.append({"id": item.get("id") or None, "title": title, "reason": item.get("reason") or item.get("why") or ""})
            else:
                # unknown type; stringify
                normalized_recs.append({"id": None, "title": str(item), "reason": ""})

        recs = normalized_recs[:3]

        # 5) fallback: if no LLM recs, run a deterministic ES keyword search
        if not recs:
            try:
                logger.debug("No recommendations from LLM; attempting ES fallback search for query='%s'", query)
                if hasattr(self.es, "search_products_simple"):
                    keyword_hits = await self.es.search_products_simple(query=query or "", limit=3)
                else:
                    # try other search method names if available
                    keyword_hits = []
                    if hasattr(self.es, "search_products"):
                        try:
                            # some services use different signature; attempt safe call
                            keyword_hits = await self.es.search_products(query=query or "", size=3)
                        except Exception:
                            keyword_hits = []
                recs = [{"id": h.get("id"), "title": h.get("name") or h.get("title") or h.get("product_name") or "", "reason": f"Matches your query '{query}'"} for h in (keyword_hits or [])]
                logger.debug("ES fallback returned %d candidates", len(recs))
            except Exception as e:
                logger.exception("ES fallback failure: %s", e)
                recs = []

        # 6) Enrich recs into product records (best-effort). This ensures we return product ids/names when possible.
        enriched: List[Dict[str, Any]] = []
        for r in recs:
            try:
                title = (r.get("title") or "").strip() if isinstance(r, dict) else str(r)
                prod = None

                # prefer exact product lookup via product_service (if available)
                if title:
                    try:
                        prod = await self.product_svc.find_product_by_title(title)
                        logger.debug("find_product_by_title('%s') -> %s", title, bool(prod))
                    except Exception as e:
                        logger.debug("find_product_by_title raised for title='%s': %s", title, e)
                        prod = None

                # if product_service didn't find it, try ES fuzzy search for the title
                if not prod and title:
                    try:
                        if hasattr(self.es, "search_products_simple"):
                            candidates = await self.es.search_products_simple(query=title, limit=1)
                        else:
                            candidates = []
                            if hasattr(self.es, "search_products"):
                                try:
                                    resp = await self.es.search_products(query=title, size=1)
                                    candidates = resp or []
                                except Exception:
                                    candidates = []
                        prod = candidates[0] if candidates else None
                        logger.debug("ES fuzzy search for '%s' -> %d candidates", title, len(candidates) if candidates else 0)
                    except Exception as e:
                        logger.debug("ES fuzzy search failed for title='%s': %s", title, e)
                        prod = None

                out_id = None
                out_title = title
                if prod:
                    # product record may be raw ES hit or product dict
                    if isinstance(prod, dict):
                        # prefer source fields
                        out_id = prod.get("id") or prod.get("_id") or prod.get("sku") or prod.get("product_id")
                        out_title = prod.get("name") or prod.get("title") or out_title
                    else:
                        # generic fallback
                        out_id = getattr(prod, "id", None)
                else:
                    # no product record found; use provided id/title
                    out_id = r.get("id") if isinstance(r, dict) else None
                    out_title = r.get("title") if isinstance(r, dict) else str(r)

                enriched.append({
                    "id": out_id,
                    "title": out_title,
                    "reason": (r.get("reason") or "") if isinstance(r, dict) else ""
                })
            except Exception as e:
                logger.exception("Error enriching recommendation %s: %s", r, e)

        logger.debug("Returning %d enriched recommendations", len(enriched))
        return {
            "pitch": parsed.get("pitch", "") or "",
            "recommendations": enriched,
            "raw": parsed.get("raw", llm_text)
        }





# __________________



# # app/agents/sales_executive_agent.py
# from typing import List, Dict, Any, Optional
# import asyncio

# from app.services.elasticsearch_service import ElasticsearchService
# from app.services.embedding_service import EmbeddingService
# from app.services.product_service import ProductService

# # small helper to keep output stable/compact
# def _parse_llm_json_or_fallback(text: str) -> Dict[str, Any]:
#     import json
#     try:
#         return json.loads(text)
#     except Exception:
#         # fallback: minimal heuristic
#         lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
#         pitch = lines[0] if lines else ""
#         recs = []
#         for ln in lines[1:6]:
#             if ln.startswith("-"):
#                 recs.append({"id": None, "title": ln.lstrip("- ").strip(), "reason": ""})
#         return {"pitch": pitch, "recommendations": recs, "raw": text}

# class SalesExecutiveAgent:
#     """
#     Use current chat + top-K past chats to:
#       - produce a short sales pitch
#       - recommend up to K products with short reasons
#     Keep compute small (top-K retrieval + one LLM call).
#     """

#     def __init__(
#         self,
#         es: Optional[ElasticsearchService] = None,
#         embed: Optional[EmbeddingService] = None,
#         product_svc: Optional[ProductService] = None,
#         top_k: int = 5,
#     ):
#         self.es = es or ElasticsearchService()
#         self.embed = embed or EmbeddingService()
#         self.product_svc = product_svc or ProductService()
#         self.top_k = top_k

#     async def process(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
#         # 1) fetch relevant past chats (top_k)
#         past = []
#         if user_id:
#             # build a small query string from last user message(s)
#             past = await self.es.fetch_relevant_chats(user_id=user_id, query_text=query, k=self.top_k)
#         # 2) build compact prompt
#         prompt_parts = [
#             "You are a friendly sales executive. Produce: 1 short pitch (1-2 sentences) and up to 3 product recommendations with a single-sentence reason each. Return JSON."
#         ]
#         prompt_parts.append("Current user message:")
#         prompt_parts.append(query)
#         if past:
#             prompt_parts.append("Relevant past interactions (summaries):")
#             for p in past:
#                 prompt_parts.append(f"- {p.get('summary') or p.get('snippet') or p.get('text','')}")
#         prompt = "\n".join(prompt_parts)

#         # 3) ask LLM via a small helper function in product_service (keeps MCP use centralized)
#         llm_text = await self.product_svc.generate_short_text(prompt=prompt, max_tokens=350)
#         parsed = _parse_llm_json_or_fallback(llm_text)

#         # 4) enrich recommendations: try to map titles -> product objects (best-effort)
#         recs = parsed.get("recommendations", [])[:3]
#         enriched = []
#         for r in recs:
#             title = r.get("title") or r.get("name") or ""
#             # attempt exact lookup, else best-effort fuzzy search via ES
#             prod = await self.product_svc.find_product_by_title(title) if title else None
#             if not prod:
#                 # fallback: do a short ES search by title keywords
#                 candidates = await self.es.search_products_simple(title, limit=1)
#                 prod = candidates[0] if candidates else None
#             enriched.append({
#                 "id": prod.get("id") if prod else r.get("id"),
#                 "title": prod.get("name") if prod else title,
#                 "reason": r.get("reason") or r.get("why") or "",
#             })
#         return {"pitch": parsed.get("pitch", ""), "recommendations": enriched, "raw": parsed.get("raw", llm_text)}
