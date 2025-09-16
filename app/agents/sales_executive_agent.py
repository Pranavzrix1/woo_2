from typing import List, Dict, Any, Optional
import logging
import json
import re
 
from app.services.elasticsearch_service import ElasticsearchService
from app.services.product_service import ProductService
 
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
 
class SalesExecutiveAgent:
    """
    SalesExecutiveAgent: given a user query, generates a short sales pitch and
    a set of enriched product recommendations.
    
    Bugfixes / improvements included:
    - Use ProductService.find_product_by_title and ProductService.search_products to fetch full product _source
      (previous code used a lightweight search that returned only id/name, causing image/price/url to be null).
    - More robust image extraction (handles strings, list[str], list[dict], dict with 'src'/'url').
    - Robust price parsing (strip currency symbols and commas).
    - Graceful fallbacks and logging for easier debugging.
    """
 
    def __init__(
        self,
        es: Optional[ElasticsearchService] = None,
        product_svc: Optional[ProductService] = None,
        top_k: int = 3,
    ):
        self.es = es or ElasticsearchService()
        self.product_svc = product_svc or ProductService()
        self.top_k = top_k
 
    def _clean_html(self, text: Optional[str]) -> str:
        if not text:
            return ""
        return re.sub(r"<[^>]+>", "", text).strip()
 
    def _extract_image(self, image_field: Any) -> Optional[str]:
        """
        Accepts many shapes:
        - None
        - string URL
        - list of strings
        - dict (maybe {'src': '...', 'url': '...'})
        - list of dicts
        Returns a single image URL or None
        """
        try:
            if not image_field:
                return None
            if isinstance(image_field, str):
                return image_field
            if isinstance(image_field, dict):
                return image_field.get("src") or image_field.get("url") or image_field.get("image")
            if isinstance(image_field, (list, tuple)) and image_field:
                first = image_field[0]
                if isinstance(first, str):
                    return first
                if isinstance(first, dict):
                    return first.get("src") or first.get("url") or first.get("image")
            return None
        except Exception:
            return None
 
    def _parse_price(self, price_val: Any) -> Optional[float]:
        if price_val is None:
            return None
        try:
            if isinstance(price_val, (int, float)):
                return float(price_val)
            s = str(price_val).strip()
            # remove currency symbols and commas
            s = re.sub(r"[^\d\.\-]", "", s)
            if s == "":
                return None
            return float(s)
        except Exception:
            return None
 
    def _process_product(self, prod: Dict[str, Any]) -> Dict[str, Any]:
        if not prod:
            return {}
        # Some indexes store product fields under different names; try common fallbacks
        name = prod.get("name") or prod.get("title") or prod.get("product_name") or ""
        description = self._clean_html(prod.get("description") or prod.get("short_description") or "")
        price = self._parse_price(prod.get("price") or prod.get("regular_price") or prod.get("sale_price"))
        # image fields: images, image, featured_image, thumbnail, image_url
        image = None
        for key in ("images", "image", "featured_image", "thumbnail", "image_url", "img", "picture"):
            if key in prod and prod.get(key):
                image = self._extract_image(prod.get(key))
                if image:
                    break
        # url/permalink
        url = prod.get("url") or prod.get("permalink") or prod.get("link") or prod.get("product_url") or ""
        category = prod.get("category") or prod.get("categories") or ""
        # normalize category when list
        if isinstance(category, (list, tuple)) and category:
            category = ", ".join([str(c) for c in category])
        stock_status = prod.get("stock_status") or prod.get("status") or ""
        sku = prod.get("sku") or prod.get("product_sku") or ""
 
        return {
            "name": name,
            "description": description,
            "price": price,
            "image": image,
            "url": url,
            "category": category,
            "stock_status": stock_status,
            "sku": sku,
        }
 
    async def process(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        # 1. Build LLM prompt (ask for strict JSON)
        prompt = (
            "You are a helpful sales executive. Given the user's message, "
            "produce EXACT JSON with keys: 'pitch' (a 1-2 sentence sales pitch for relevant products) "
            "and 'recommendations' (a list of product titles the user is likely to buy, based on their query). "
            "User message:\n"
            f"{query}\n"
            "Return only valid JSON. Example: {\"pitch\": \"Here are some great options!\", \"recommendations\": [\"White Cap\", \"Blue Shirt\"]}"
        )
 
        # 2. Call LLM for pitch and recommendations (ProductService wraps LLM call)
        try:
            llm_text = await self.product_svc.generate_short_text(prompt=prompt, max_tokens=350)
            parsed = json.loads(llm_text)
        except Exception as e:
            logger.exception("LLM call or parsing failed: %s", e)
            parsed = {"pitch": f"I can help with that.", "recommendations": []}
 
        pitch = parsed.get("pitch", "")
        rec_titles = parsed.get("recommendations", [])
        logger.info(f"LLM pitch: {pitch} | Recommendations: {rec_titles}")
 
        # 3. For each recommended title, try to fetch the full product from ES via ProductService
        enriched: List[Dict[str, Any]] = []
        for title in rec_titles:
            if not title:
                continue
            try:
                # 3a. Try exact title lookup
                prod = await self.product_svc.find_product_by_title(title)
                if prod:
                    processed = self._process_product(prod)
                    if processed:
                        enriched.append(processed)
                        continue
 
                # 3b. Try a broader search (returns full _source products)
                results = await self.product_svc.search_products(title, limit=1)
                if results:
                    prod = results[0]
                    processed = self._process_product(prod)
                    if processed:
                        enriched.append(processed)
                        continue
 
                # 3c. If we have ES client and the lightweight search gives only id/name, try to fetch by id
                try:
                    simple_hits = await self.es.search_products_simple(query=title, limit=1)
                    if simple_hits:
                        hit = simple_hits[0]
                        # if we have an id, fetch full doc
                        pid = hit.get("id") or hit.get("_id")
                        if pid and hasattr(self.es, "es") and getattr(self.es, "es") is not None:
                            # AsyncElasticsearch.get requires string id
                            try:
                                doc = await self.es.es.get(index=self.es.index_name, id=str(pid))
                                if doc and doc.get("_source"):
                                    processed = self._process_product(doc["_source"])
                                    if processed:
                                        enriched.append(processed)
                                        continue
                            except Exception:
                                # ignore and continue to minimal fallback
                                logger.debug("Could not get full doc by id from ES for id=%s", pid)
                except Exception:
                    pass
 
                # 3d. Minimal fallback item
                enriched.append({
                    "name": title,
                    "description": "",
                    "price": None,
                    "image": None,
                    "url": None,
                    "category": "",
                    "stock_status": "",
                    "sku": ""
                })
 
            except Exception as e:
                logger.exception("Error while enriching product title '%s': %s", title, e)
                continue
 
        # 4. If still empty, fallback to searching ES with the original query and return top-k real products
        if not enriched:
            try:
                prods = await self.product_svc.search_products(query, limit=self.top_k)
                for p in prods:
                    processed = self._process_product(p)
                    if processed:
                        enriched.append(processed)
            except Exception as e:
                logger.exception("Fallback search failed: %s", e)
 
        return {
            "pitch": pitch,
            "recommendations": enriched,
            "query": query
        }
 