# app/agents/coupon_agent.py
from typing import Dict, Any, List, Optional
from app.services.coupon_service import CouponService
from app.services.product_service import ProductService
# from app.core.memory_manager import MemoryManager  # adjust if your project uses different memory API
try:
    from app.core.memory_manager import MemoryManager
except Exception:
    MemoryManager = None
# import asyncio
import asyncio

class CouponAgent:
    def __init__(self):
        self.coupon_service = CouponService()
        self.product_service = ProductService()
        # memory manager / chat history retrieval - adapt to your project
        try:
            self.memory = MemoryManager()
        except Exception:
            self.memory = None

    async def handle_query(self, chat_context: Dict[str, Any], user_query: str, user_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point to handle a coupon-related user query.
        """
        query_lower = user_query.lower()
        
        # Mode 1: List all coupons
        if any(phrase in query_lower for phrase in ["what coupons", "all coupons", "available coupons", "do you have coupons"]):
            return await self._list_all_coupons()
        
        # Mode 2: Check specific coupon eligibility
        if any(phrase in query_lower for phrase in ["which product", "what can use", "eligible for", "apply to"]):
            coupon_code = self._extract_coupon_code(user_query)
            if coupon_code:
                return await self._check_coupon_eligibility(coupon_code)
        
        # Mode 3: Calculate final price
        if any(phrase in query_lower for phrase in ["final price", "calculate", "how much", "total cost"]):
            return await self._calculate_price_with_coupon(chat_context, user_query, user_email)
        
        # Default: Show applicable coupons for context
        return await self._show_applicable_coupons(chat_context, user_query, user_email)


        # compute final prices and build pitches
        # pitches = []
        # for coupon in applicable:
        #     comp = self.coupon_service.compute_final_price(product or {"price": 0.0}, coupon, cart_total)
        #     # build product presentation
        #     prod_name = (product.get("name") or "") if product else ""
        #     prod_image = (product.get("image") or "") if product else ""
        #     prod_desc = (product.get("short_description") or product.get("description") or "") if product else ""
        #     prod_link = (product.get("link") or product.get("url") or "")
        #     pitch_text = self._build_pitch_text(coupon, prod_name, comp, prod_link)
        #     pitches.append({
        #         "coupon_code": coupon.get("code"),
        #         "description": coupon.get("description"),
        #         "product": {
        #             "name": prod_name,
        #             "image": prod_image,
        #             "status": product.get("status") if product else None,
        #             "short_description": prod_desc,
        #             "link": prod_link,
        #         },
        #         "original_price": comp["original_price"],
        #         "final_price": comp["final_price"],
        #         "savings": comp["savings"],
        #         "pitch_text": pitch_text,
        #         "raw_coupon": coupon
        #     })


        pitches = []
        for coupon in applicable or []:
            # defensive guard - skip None / non-dict objects
            if not coupon or not isinstance(coupon, dict):
                print("[CouponAgent] skipping invalid coupon entry:", coupon)
                continue

            try:
                comp = self.coupon_service.compute_final_price(product or {"price": 0.0}, coupon, cart_total)
            except Exception as e:
                print(f"[CouponAgent] compute_final_price error for coupon {coupon.get('code') if isinstance(coupon, dict) else coupon}: {e}")
                continue

            # now safe to access coupon.get(...)
            prod_name = (product.get("name") or "") if product else ""
            prod_image = (product.get("image") or "") if product else ""
            prod_desc = (product.get("short_description") or product.get("description") or "") if product else ""
            prod_link = (product.get("link") or product.get("url") or "")
            pitch_text = self._build_pitch_text(coupon, prod_name, comp, prod_link)

            pitches.append({
                "coupon_code": coupon.get("code"),
                "description": coupon.get("description"),
                "product": {
                    "name": prod_name,
                    "image": prod_image,
                    "status": product.get("status") if product else None,
                    "short_description": prod_desc,
                    "link": prod_link,
                },
                "original_price": comp.get("original_price") if isinstance(comp, dict) else None,
                "final_price": comp.get("final_price") if isinstance(comp, dict) else None,
                "savings": comp.get("savings") if isinstance(comp, dict) else 0.0,
                "pitch_text": pitch_text
            })





        if not coupon:
            return ""
        code = coupon.get("code")
        desc = coupon.get("description") or f"Save ${comp.get('savings', 0)}"
        
        if product_name and product_name != "unspecified item":
            return f"Use coupon {code} on {product_name} — {desc}. Original: ${comp['original_price']}, Final: ${comp['final_price']}, You save: ${comp['savings']}!"
        else:
            return f"Use coupon {code} — {desc}. Applies to cart total for additional savings!"

    async def _list_all_coupons(self) -> Dict[str, Any]:
        """List all available coupons with their details"""
        try:
            # Get all coupons from ES (active + inactive)
            q = {"query": {"match_all": {}}, "size": 50}
            result = await self.coupon_service.es.search(index=self.coupon_service.index, body=q)
            coupons = [hit["_source"] for hit in result.get("hits", {}).get("hits", [])]
            
            if not coupons:
                return {"text": "No coupons available right now.", "coupons": []}
            
            coupon_list = []
            for c in coupons:
                discount_text = f"{c.get('amount_numeric', 0)}% off" if c.get('discount_type') == 'percent' else f"${c.get('amount_numeric', 0)} off"
                expires = f" (expires {c.get('date_expires', 'never')})" if c.get('date_expires') else ""
                status = "✅ Active" if c.get('active_bool') else "❌ Inactive"
                coupon_list.append(f"• **{c.get('code')}** - {discount_text}{expires} {status}")
            
            response = f"Here are all available coupons:\n\n" + "\n".join(coupon_list)
            return {"text": response, "coupons": coupons}
        except Exception as e:
            return {"text": "Error fetching coupons.", "coupons": []}
    
    async def _check_coupon_eligibility(self, coupon_code: str) -> Dict[str, Any]:
        """Check which products are eligible for a specific coupon"""
        try:
            # Find the coupon (handle spaced codes)
            q = {"query": {"bool": {"should": [
                {"term": {"code": coupon_code.lower()}},
                {"term": {"code": coupon_code.lower().replace(' ', '')}}
            ]}}}
            result = await self.coupon_service.es.search(index=self.coupon_service.index, body=q)
            hits = result.get("hits", {}).get("hits", [])
            
            if not hits:
                return {"text": f"Coupon '{coupon_code}' not found.", "eligibility": []}
            
            coupon = hits[0]["_source"]
            
            # Check restrictions
            restrictions = []
            if coupon.get("product_ids"):
                restrictions.append(f"Specific products only (IDs: {coupon['product_ids']})")
            elif coupon.get("product_categories"):
                restrictions.append(f"Categories: {', '.join(coupon['product_categories'])}")
            else:
                restrictions.append("All products")
            
            if coupon.get("minimum_amount"):
                restrictions.append(f"Minimum order: ${coupon['minimum_amount']}")
            
            response = f"**{coupon_code}** eligibility:\n" + "\n".join([f"• {r}" for r in restrictions])
            return {"text": response, "eligibility": restrictions}
        except Exception as e:
            return {"text": f"Error checking coupon '{coupon_code}'.", "eligibility": []}
    
    async def _calculate_price_with_coupon(self, chat_context: Dict[str, Any], user_query: str, user_email: Optional[str]) -> Dict[str, Any]:
        """Calculate final price when coupon is applied"""
        # Extract product and coupon from query
        coupon_code = self._extract_coupon_code(user_query)
        if not coupon_code:
            return {"text": "Please specify which coupon you'd like to use for the calculation.", "calculation": None}
        
        # Get product from context or query
        product = await self._get_product_from_context(chat_context, user_query)
        if not product:
            return {"text": "Please specify which product you'd like to calculate the price for.", "calculation": None}
        
        # Find and apply coupon
        try:
            q = {"query": {"bool": {"should": [
                {"term": {"code": coupon_code.lower()}},
                {"term": {"code": coupon_code.lower().replace(' ', '')}}
            ]}}}
            result = await self.coupon_service.es.search(index=self.coupon_service.index, body=q)
            hits = result.get("hits", {}).get("hits", [])
            
            if not hits:
                return {"text": f"Coupon '{coupon_code}' not found.", "calculation": None}
            
            coupon = hits[0]["_source"]
            calc = self.coupon_service.compute_final_price(product, coupon)
            
            response = f"Price calculation for **{product.get('name')}** with **{coupon_code}**:\n"
            response += f"• Original: ${calc['original_price']}\n"
            response += f"• Final: ${calc['final_price']}\n"
            response += f"• You save: ${calc['savings']}"
            
            return {"text": response, "calculation": calc}
        except Exception as e:
            return {"text": "Error calculating price.", "calculation": None}
    
    def _extract_coupon_code(self, query: str) -> Optional[str]:
        """Extract coupon code from user query"""
        import re
        # Look for common coupon patterns (handle spaces and variations)
        patterns = [
            r'\b(test10|weekend20|winter50|diwali40|newyear100)\b',
            r'\b(sale\s*30)\b',  # Handle "sale 30" with optional space
        ]
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                code = match.group(1)
                # Keep original spacing as stored in ES
                return "sale 30" if "sale" in code else code
        return None
    
    async def _get_product_from_context(self, chat_context: Dict[str, Any], user_query: str) -> Optional[Dict[str, Any]]:
        """Get product from context or extract from query"""
        # Check context first
        if chat_context and chat_context.get("last_viewed_product"):
            return chat_context["last_viewed_product"]
        
        # Extract product keywords from query and search dynamically
        query_lower = user_query.lower()
        product_keywords = ["hoodie", "shirt", "hat", "hats", "cap", "beverage", "drink", "towel", "bag", "sauce", "tea", "umbrella"]
        
        for keyword in product_keywords:
            if keyword in query_lower:
                try:
                    products = await self.product_service.search_products(keyword, limit=1)
                    if products:
                        return products[0]
                except Exception as e:
                    print(f"Product search error for '{keyword}': {e}")
                    continue
        
        return None
    
    async def _show_applicable_coupons(self, chat_context: Dict[str, Any], user_query: str, user_email: Optional[str]) -> Dict[str, Any]:
        """Original functionality - show applicable coupons for context"""
        product = await self._get_product_from_context(chat_context, user_query) or {"id": None, "name": "items", "price": 0.0}
        applicable = await self.coupon_service.get_applicable_coupons(product, 0.0, user_email)
        
        if not applicable:
            return {"text": "No coupons apply to your current selection. Ask 'what coupons do you have' to see all available coupons.", "pitches": []}
        
        # Just show the first applicable coupon without auto-calculating
        coupon = applicable[0]
        response = f"You can use coupon **{coupon.get('code')}** on {product.get('name')}. Ask me to calculate the final price if you'd like!"
        return {"text": response, "applicable": applicable}
