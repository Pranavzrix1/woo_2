# app/services/coupon_service.py
import asyncio
import httpx
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import settings
from app.services.elasticsearch_service import ElasticsearchService

JSONRPC_TEMPLATE = lambda method: {
    "jsonrpc": "2.0",
    "method": method,
    "params": {},
    "id": 1
}

class CouponService:
    def __init__(self, es_service=None):
        self.es = es_service or ElasticsearchService()
        self.index = getattr(settings, "coupon_index", "coupons")
        self.rpc_endpoint = getattr(settings, "product_endpoint", None)
    
    async def close(self):
        """Close ES client"""
        try:
            if hasattr(self, 'es') and self.es:
                await self.es.close()
        except Exception as e:
            print(f"CouponService.close error: {e}")

    async def fetch_coupons_from_rpc(self) -> List[Dict[str, Any]]:
        """Fetch coupons via JSON-RPC get_coupons"""
        if not self.rpc_endpoint:
            return []
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self.rpc_endpoint, json=JSONRPC_TEMPLATE("get_coupons"),
                                             headers={"Content-Type": "application/json"})
                if response.status_code == 200:
                    data = response.json()
                    raw = data.get("result", [])
                    return raw if isinstance(raw, list) else []
                else:
                    return []
            except Exception:
                return []

    def _normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize coupon fields and coerce types for Elasticsearch"""
        c = dict(raw)  # shallow copy
        # Uppercase code for consistency
        code = c.get("code") or c.get("coupon") or c.get("name") or ""
        c["code"] = str(code).strip()
        # numeric amount
        try:
            c["amount_numeric"] = float(c.get("amount", 0) or 0)
        except Exception:
            c["amount_numeric"] = 0.0
        # discount type
        c["discount_type"] = c.get("discount_type", "fixed_cart")
        # boolean fields normalization
        for b in ("individual_use", "free_shipping", "exclude_sale_items"):
            c[b] = bool(c.get(b, False))
        # list fields
        for arr in ("product_ids", "exclude_product_ids", "product_categories", "exclude_product_categories", "email_restrictions"):
            val = c.get(arr, []) or []
            if isinstance(val, str):
                # try comma separated
                val = [x.strip() for x in val.split(",") if x.strip()]
            c[arr] = val
        # parse dates
        def _parse_date(v):
            if v is None:
                return None
            if isinstance(v, (int, float)):
                return int(v)
            for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
                try:
                    dt = datetime.strptime(str(v), fmt)
                    return int(dt.timestamp())
                except Exception:
                    continue
            # fallback: try to parse with datetime.fromisoformat
            try:
                dt = datetime.fromisoformat(str(v))
                return int(dt.timestamp())
            except Exception:
                return None
        c["date_start_epoch"] = _parse_date(c.get("date_start"))
        c["date_expires_epoch"] = _parse_date(c.get("date_expires"))
        c["active_bool"] = (c.get("status") in ("active", "publish", "enabled", True))
        c["last_synced_at"] = int(time.time())
        return c

    async def upsert_coupons(self, coupons: List[Dict[str, Any]]):
        """Bulk upsert to ES coupons index"""
        if not coupons:
            return
        actions = []
        for c in coupons:
            doc = self._normalize(c)
            # use code as id if present else numeric id
            doc_id = str(doc.get("code") or doc.get("id") or "")
            if not doc_id:
                doc_id = str(doc.get("id", "") or "")
            actions.append({"index": {"_index": self.index, "_id": doc_id}})
            actions.append(doc)


        # ensure coupons index exists with mapping
        await self.es.create_coupons_index_if_not_exists(self.index)
        # use ES service bulk helper
        await self.es.bulk_index(actions)

    async def refresh_coupons(self):
        raw = await self.fetch_coupons_from_rpc()
        await self.upsert_coupons(raw)
        return len(raw)

    async def get_applicable_coupons(self, product: Dict[str, Any], cart_total: float = 0.0, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Query ES to find coupons that might apply to this product/cart.
        This uses ES filters to narrow candidates then applies business logic locally.
        """
        # basic ES query by product id or category
        product_id = product.get("id")
        categories = product.get("categories", []) or []
        must_clauses = []
        # match active coupons
        must_clauses.append({"term": {"active_bool": True}})
        # either product id in product_ids or categories match or apply_to == 'cart'
        # we'll fetch candidates and then filter in Python
        q = {
            "query": {
                "bool": {
                    "must": must_clauses
                }
            },
            "size": 50
        }
        raw_candidates = await self.es.search(index=self.index, body=q)
        hits = raw_candidates.get("hits", {}).get("hits", [])
        candidates = [h["_source"] for h in hits]

        # FILTER & DEBUG: ensure only real dict sources are returned
        candidates = [h.get("_source") for h in hits if h.get("_source")]

        # Debugging helpful log (won't crash production)
        try:
            print(f"[CouponService] found {len(candidates)} candidate coupon docs from ES (index={self.index})")
            for s in candidates[:3]:
                print("[CouponService] sample candidate:", s)
        except Exception:
            pass

        applicable = []
        for c in candidates:
            # basic date check
            now = int(time.time())
            ds = c.get("date_start_epoch")
            de = c.get("date_expires_epoch")
            if ds and now < ds:
                continue
            if de and now > de:
                continue
            # product / category restrictions
            pids = c.get("product_ids", []) or []
            if pids and product_id and int(product_id) not in [int(x) for x in pids]:
                # not targeted to this product
                # but if apply_to is cart and no pids provided it may still apply
                if c.get("apply_to") != "cart":
                    continue
            cats = c.get("product_categories", []) or []
            if cats and categories:
                if not any(cat in cats for cat in categories):
                    continue
            # min/max amount limits
            min_amt = float(c.get("minimum_amount") or 0.0)
            max_amt = float(c.get("maximum_amount") or 1e12)
            if cart_total < min_amt or cart_total > max_amt:
                continue
            # email restrictions
            emails = c.get("email_restrictions") or []
            if emails and user_email and user_email not in emails:
                continue
            applicable.append(c)
        return applicable

    def compute_final_price(self, product: Dict[str, Any], coupon: Dict[str, Any], cart_total: Optional[float] = None) -> Dict[str, Any]:
        """
        Compute final price for product given coupon. Returns a dict with original_price, final_price, savings.
        Basic implementation:
          - percent: product.price * (1 - pct/100)
          - fixed_product: subtract fixed amount from product.price
          - fixed_cart: if cart_total provided, subtract proportionally (or allocate all to product if single)
        """
        price = float(product.get("price", 0.0) or 0.0)
        dtype = coupon.get("discount_type", "fixed_cart")
        amt = float(coupon.get("amount_numeric", coupon.get("amount", 0) or 0) or 0.0)

        original = price
        final = price
        savings = 0.0

        if dtype == "percent":
            savings = (amt / 100.0) * price
            final = price - savings
        elif dtype == "fixed_product":
            savings = min(price, amt)
            final = price - savings
        elif dtype == "fixed_cart":
            # if cart_total provided, pro-rate by product share, else apply up to product price
            if cart_total:
                # avoid division by zero
                try:
                    ratio = price / cart_total
                    savings = amt * ratio
                except Exception:
                    savings = min(price, amt)
            else:
                savings = min(price, amt)
            final = max(0.0, price - savings)
        else:
            # unknown type, no discount
            savings = 0.0
            final = price

        return {"original_price": round(original, 2), "final_price": round(final, 2), "savings": round(savings, 2)}
