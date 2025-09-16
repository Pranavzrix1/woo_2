from elasticsearch import AsyncElasticsearch
from typing import List, Dict, Any
from app.config import settings

class ElasticsearchService:
    def __init__(self):
        self.es = AsyncElasticsearch([settings.elasticsearch_url])
        self.index_name = "products"
    
    async def create_product_index(self):
        """Create the products index with mapping"""
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "text", "analyzer": "standard"},
                    "description": {"type": "text", "analyzer": "standard"},
                    "price": {"type": "float"},
                    "category": {"type": "text", "analyzer": "standard"},
                    "sku": {"type": "keyword"},
                    "embedding": {"type": "dense_vector", "dims": 1024},


                    "status": {"type": "keyword"},
                    "stock_status": {"type": "keyword"},
                    "image": {"type": "keyword"},
                    "images": {"type": "keyword"},

                    "url": {"type": "keyword"},        # ✅ CORRECT PLACE - In mapping
                    "slug": {"type": "keyword"} 

                }
            }
        }
        
        try:
            exists = await self.es.indices.exists(index=self.index_name)
            if not exists:
                await self.es.indices.create(index=self.index_name, body=mapping)
                print(f"Created index: {self.index_name}")
        except Exception as e:
            print(f"Error with index: {e}")


    async def create_category_index(self):
        """Create the categories index with mapping"""
        category_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "text", "analyzer": "standard"},
                    "slug": {"type": "keyword"},
                    "description": {"type": "text", "analyzer": "standard"},
                    "count": {"type": "integer"},
                    "parent": {"type": "integer"}
                }
            }
        }
        
        try:
            category_index = "categories"
            exists = await self.es.indices.exists(index=category_index)
            if not exists:
                await self.es.indices.create(index=category_index, body=category_mapping)
                print(f"Created index: {category_index}")
        except Exception as e:
            print(f"Error creating category index: {e}")

    async def index_categories(self, categories: List[Dict[str, Any]]):
        """Index product categories"""
        category_index = "categories"
        
        for category in categories:
            try:
                doc = {
                    "id": category.get("id"),
                    "name": category.get("name", ""),
                    "slug": category.get("slug", ""),
                    "description": category.get("description", ""),
                    "count": category.get("count", 0),
                    "parent": category.get("parent", 0)
                }
                
                await self.es.index(index=category_index, id=category.get("id"), body=doc)
            except Exception as e:
                print(f"Error indexing category {category.get('id')}: {e}")

    async def search_categories(self, query: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """Search categories or get all if query is empty"""
        category_index = "categories"
        
        try:
            if not query:
                # Get all categories
                search_query = {"query": {"match_all": {}}, "size": limit}
            else:
                # Search specific categories
                search_query = {
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": ["name^2", "description"],
                            "type": "best_fields"
                        }
                    },
                    "size": limit
                }
            
            result = await self.es.search(index=category_index, body=search_query)
            return [hit["_source"] for hit in result["hits"]["hits"]]
        except Exception as e:
            print(f"Category search error: {e}")
            return []

    
    async def index_products(self, products: List[Dict[str, Any]]):
        """Index products with embeddings"""
        from app.services.embedding_service import EmbeddingService
        embedding_service = EmbeddingService()
        
        for product in products:
            try:
                text_to_embed = f"{product.get('name', '')} {product.get('description', '')} {product.get('category', '')}"
                embedding = await embedding_service.get_embedding(text_to_embed)
                
                doc = {
                    "id": product.get("id"),
                    "name": product.get("name", ""),
                    "description": product.get("description", ""),
                    "price": product.get("price", 0),
                    "category": product.get("category", ""),
                    "sku": product.get("sku", ""),
                    "embedding": embedding,


                    "status": product.get("status", "publish"),           # ✅ Actual value
                    "stock_status": product.get("stock_status", "instock"), # ✅ Actual value
                    "image": product.get("image"),                        # ✅ Actual value
                    "images": product.get("images", []),                   # ✅ Actual value


                    "url": product.get("url", ""),           # ✅ FIXED - Actual URL value
                    "slug": product.get("slug", "")          # ✅ FIXED - Actual slug value


                }
                
                await self.es.index(index=self.index_name, id=product.get("id"), body=doc)
            except Exception as e:
                print(f"Error indexing product {product.get('id')}: {e}")
    
    async def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search products with comprehensive error handling"""
        try:
            # Strategy 1: Simple wildcard search
            wildcard_query = {
                "query": {
                    "bool": {
                        "should": [
                            {"wildcard": {"name": f"*{query.lower()}*"}},
                            {"wildcard": {"description": f"*{query.lower()}*"}},
                            {"wildcard": {"category": f"*{query.lower()}*"}}
                        ],
                        "minimum_should_match": 1
                    }
                },
                "size": limit
            }
            
            result = await self.es.search(index=self.index_name, body=wildcard_query)
            products = [hit["_source"] for hit in result["hits"]["hits"]]
            
            # Strategy 2: If no results, try match query
            if not products:
                match_query = {
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": ["name^3", "description^2", "category"],
                            "type": "best_fields",
                            "fuzziness": "AUTO"
                        }
                    },
                    "size": limit
                }
                
                result = await self.es.search(index=self.index_name, body=match_query)
                products = [hit["_source"] for hit in result["hits"]["hits"]]
            
            # Strategy 3: Fallback to show some products
            if not products:
                fallback_query = {
                    "query": {"match_all": {}},
                    "size": limit
                }
                
                result = await self.es.search(index=self.index_name, body=fallback_query)
                products = [hit["_source"] for hit in result["hits"]["hits"]]
            
            return products
        except Exception as e:
            print(f"Search error: {e}")
            return []

        

    async def fetch_relevant_chats(self, user_id: str, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Return top-k relevant past chat summaries for a user.
        - Prefer vector similarity if chat index has embeddings.
        - Else fallback to recent chats by created_at.
        Each item: {id, summary, snippet, created_at}
        """
        # try vector search on a 'chat_history' index
        try:
            idx = "chat_history"
            # if embeddings exist, do an embedding similarity query
            body = {
                "size": k,
                "query": {
                    "script_score": {
                        "query": {"term": {"user_id": user_id}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                            "params": {"query_vector": await self._embed_vector(query_text)}
                        }
                    }
                }
            }
            res = await self.es.search(index=idx, body=body)
            hits = res.get("hits", {}).get("hits", [])
            out = []
            for h in hits:
                s = h["_source"]
                out.append({"id": s.get("id"), "summary": s.get("summary"), "snippet": s.get("message_snippet") or s.get("text",""), "created_at": s.get("created_at")})
            if out:
                return out
        except Exception:
            # ignore vector path and fallback
            pass

        # fallback: recent chats for the user
        try:
            q = {
                "size": k,
                "query": {"bool": {"must": [{"term": {"user_id": user_id}}]}},
                "sort": [{"created_at": {"order": "desc"}}]
            }
            res = await self.es.search(index="chat_history", body=q)
            hits = res.get("hits", {}).get("hits", [])
            return [{"id": h["_id"], "summary": h["_source"].get("summary"), "snippet": (h["_source"].get("text") or "")[:200], "created_at": h["_source"].get("created_at")} for h in hits]
        except Exception:
            return []
        

    async def search_products_simple(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Lightweight keyword search for products. Returns list of dicts with at least id & name.
        """
        index = "products"  # change if your product index name is different
        if not query or not query.strip():
            body = {"size": limit, "query": {"match_all": {}}, "sort": [{"_score": {"order": "desc"}}]}
        else:
            body = {
                "size": limit,
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["name^3", "title^3", "description", "short_description", "category", "tags"],
                        "type": "best_fields",
                        "operator": "or"
                    }
                }
            }
        try:
            res = await self.es.search(index=index, body=body)
            hits = res.get("hits", {}).get("hits", [])
            out = []
            for h in hits:
                src = h.get("_source", {})
                out.append({
                    "id": src.get("id") or h.get("_id"),
                    "name": src.get("name") or src.get("title") or src.get("product_name"),
                    "score": h.get("_score"),
                    "raw": src
                })
            return out
        except Exception:
            print("ElasticsearchService.search_products_simple: search failed")
            return []


        
            

