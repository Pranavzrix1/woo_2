import httpx
import asyncio
from typing import List, Dict, Any
from app.config import settings
from app.services.elasticsearch_service import ElasticsearchService

class ProductService:
    def __init__(self):
        self.es_service = ElasticsearchService()
        self._client = None
    
    async def get_client(self):
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
        
    async def fetch_products_from_endpoint(self) -> List[Dict[str, Any]]:
        """Fetch products from WordPress with proper data transformation"""
        try:
            client = await self.get_client()
            response = await client.post(
                settings.product_endpoint,
                json={
                    "jsonrpc": "2.0",
                    "method": "get_products",
                    "params": {},
                    "id": 1
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                raw_products = data.get("result", [])
                
                # Transform WordPress data to our format
                products = []
                for item in raw_products:
                    # Only include products with valid prices
                    price_str = item.get("price", "")
                    if not price_str or price_str == "":
                        continue
                        
                    try:
                        price = float(price_str)
                    except (ValueError, TypeError):
                        continue
                        
                    products.append({
                        "id": item.get("id"),
                        "name": item.get("name", "Unknown Product"),
                        "description": item.get("description", ""),
                        "price": price,
                        "category": ", ".join(item.get("categories", ["Uncategorized"])),
                        "sku": str(item.get("id", "")),
                        "status": item.get("status", "publish"),
                        "stock_status": item.get("stock_status", "instock"),
                        "images": item.get("images", []),
                        "image": item.get("images", [None])[0] if item.get("images") else None,
                        "url": item.get("permalink") or (
                            f"https://newscnbnc.webserver9.com/product/{item.get('slug')}/" 
                            if item.get("slug") 
                            else f"https://newscnbnc.webserver9.com/product/{item.get('id')}/"
                        ),
                        "slug": item.get("slug", "")
                    })
                
                return products
            else:
                print(f"Error fetching products: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Exception fetching products: {e}")
            return []
    
    async def fetch_and_index_products(self):
        """Fetch products and index them in Elasticsearch"""
        print("Fetching products from WordPress endpoint...")
        products = await self.fetch_products_from_endpoint()
        
        if products:
            print(f"Found {len(products)} products with valid prices")
            print(f"Indexing {len(products)} products...")
            await self.es_service.index_products(products)
            print("Products indexed successfully!")
        else:
            print("No products found to index")
    
    async def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search products using Elasticsearch with error handling"""
        try:
            return await self.es_service.search_products(query, limit)
        except Exception as e:
            print(f"Product search error: {e}")
            return []

    async def get_product_categories(self) -> List[Dict[str, Any]]:
        """Fetch product categories from WooCommerce endpoint"""
        try:
            client = await self.get_client()
            response = await client.post(
                settings.product_endpoint,
                json={
                    "jsonrpc": "2.0",
                    "method": "get_product_categories",
                    "params": {},
                    "id": 1
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"🔍 Category Response Debug: {data}")
                
                # Try multiple response formats
                if data.get("success"):
                    return data.get("data", [])
                elif data.get("result"):
                    return data.get("result", [])
                elif isinstance(data, list):
                    return data
                else:
                    print(f"❌ Unexpected category response format: {data}")
            
            print(f"Categories fetch failed: {response.status_code}")
            return []
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []

    async def fetch_and_index_categories(self):
        """Fetch categories from WooCommerce and index in Elasticsearch"""
        categories = await self.get_product_categories()
        
        if categories:
            await self.es_service.index_categories(categories)
            print(f"Indexed {len(categories)} categories")
        else:
            print("No categories to index")

    async def search_categories(self, query: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """Search categories using Elasticsearch"""
        return await self.es_service.search_categories(query, limit)

    async def generate_short_text(self, prompt: str, max_tokens: int = 250) -> str:
        # wrapper around your project's LLM helper (dspy or other).
        # Keep it small — this centralizes LLM use.
        from dspy import LM  # adapt if you have a client wrapper
        try:
            # If you have a wrapped client, call that instead
            resp = LM.create(prompt=prompt, max_tokens=max_tokens)
            return resp.text if hasattr(resp, "text") else str(resp)
        except Exception:
            # fallback to empty predictable response
            return '{"pitch":"I can help with that.","recommendations": []}'
    
    async def find_product_by_title(self, title: str):
        # try exact lookup then simple search via ES
        try:
            # exact match in products index
            q = {"query": {"match_phrase": {"name.keyword": title}}, "size": 1}
            res = await self.es.search(index=self.es.index_name, body=q)
            hits = res.get("hits", {}).get("hits", [])
            return hits[0]["_source"] if hits else None
        except Exception:
            return None