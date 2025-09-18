# app/services/elasticsearch_service.py
from elasticsearch import AsyncElasticsearch
from typing import List, Dict, Any
from app.config import settings

class ElasticsearchService:
    def __init__(self):
        # use configured ES url and default index names from settings where possible
        self.es = AsyncElasticsearch([settings.elasticsearch_url])
        self.index_name = getattr(settings, "product_index", "products")

    async def search(self, index: str = None, body: Dict[str, Any] = None, **kwargs):
        idx = index or self.index_name
        try:
            return await self.es.search(index=idx, body=body, **kwargs)
        except Exception as e:
            print(f"ElasticsearchService.search: error: {e}")
            raise

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
                    "url": {"type": "keyword"},
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
        category_index = "categories"
        try:
            if not query:
                search_query = {"query": {"match_all": {}}, "size": limit}
            else:
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
            return [hit["_source"] for hit in result.get("hits", {}).get("hits", [])]
        except Exception as e:
            print(f"Category search error: {e}")
            return []

    async def index_products(self, products: List[Dict[str, Any]]):
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
                    "status": product.get("status", "publish"),
                    "stock_status": product.get("stock_status", "instock"),
                    "image": product.get("image"),
                    "images": product.get("images", []),
                    "url": product.get("url", ""),
                    "slug": product.get("slug", "")
                }
                await self.es.index(index=self.index_name, id=product.get("id"), body=doc)
            except Exception as e:
                print(f"Error indexing product {product.get('id')}: {e}")

    async def bulk_index(self, actions: list):
        try:
            await self.es.bulk(body=actions, refresh='wait_for')
        except Exception as e:
            print(f"ElasticsearchService.bulk_index error: {e}")
            raise

    async def create_coupons_index_if_not_exists(self, index_name: str = "coupons"):
        try:
            exists = await self.es.indices.exists(index=index_name)
            if exists:
                return
            mapping = {
                "mappings": {
                    "properties": {
                        "code": {"type": "keyword"},
                        "amount_numeric": {"type": "double"},
                        "discount_type": {"type": "keyword"},
                        "description": {"type": "text"},
                        "date_start_epoch": {"type": "long"},
                        "date_expires_epoch": {"type": "long"},
                        "product_ids": {"type": "integer"},
                        "product_categories": {"type": "keyword"},
                        "minimum_amount": {"type": "double"},
                        "maximum_amount": {"type": "double"},
                        "active_bool": {"type": "boolean"},
                        "last_synced_at": {"type": "long"}
                    }
                }
            }
            await self.es.indices.create(index=index_name, body=mapping)
            print(f"Created coupons index '{index_name}'")
        except Exception as e:
            print(f"create_coupons_index_if_not_exists error: {e}")
            raise

    async def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            if not query.strip():
                fallback_query = {"query": {"match_all": {}}, "size": limit}
                result = await self.es.search(index=self.index_name, body=fallback_query)
                return [hit["_source"] for hit in result.get("hits", {}).get("hits", [])]
            
            # Strategy 1: Exact phrase match with high boost
            exact_query = {
                "query": {
                    "bool": {
                        "should": [
                            {"match_phrase": {"name": {"query": query, "boost": 10}}},
                            {"match": {"name": {"query": query, "boost": 5}}},
                            {"match": {"description": {"query": query, "boost": 2}}},
                            {"match": {"category": {"query": query, "boost": 3}}}
                        ]
                    }
                },
                "size": limit
            }
            result = await self.es.search(index=self.index_name, body=exact_query)
            products = [hit["_source"] for hit in result.get("hits", {}).get("hits", [])]
            
            # Strategy 2: Wildcard if no exact matches
            if not products:
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
                products = [hit["_source"] for hit in result.get("hits", {}).get("hits", [])]
            
            # Strategy 3: Fuzzy match as last resort
            if not products:
                fuzzy_query = {
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
                result = await self.es.search(index=self.index_name, body=fuzzy_query)
                products = [hit["_source"] for hit in result.get("hits", {}).get("hits", [])]
            
            return products
        except Exception as e:
            print(f"Search error: {e}")
            return []

    async def fetch_relevant_chats(self, user_id: str, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        try:
            idx = "chat_history"
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
            pass
        try:
            q = {"size": k, "query": {"bool": {"must": [{"term": {"user_id": user_id}}]}},"sort": [{"created_at": {"order": "desc"}}]}
            res = await self.es.search(index="chat_history", body=q)
            hits = res.get("hits", {}).get("hits", [])
            return [{"id": h["_id"], "summary": h["_source"].get("summary"), "snippet": (h["_source"].get("text") or "")[:200], "created_at": h["_source"].get("created_at")} for h in hits]
        except Exception:
            return []

    async def search_products_simple(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        index = "products"
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
                })
            return out
        except Exception:
            print("ElasticsearchService.search_products_simple: search failed")
            return []

    async def close(self):
        try:
            if hasattr(self, 'es') and self.es:
                await self.es.close()
        except Exception as e:
            print(f"ElasticsearchService.close: error closing es client: {e}")



# from elasticsearch import AsyncElasticsearch
# from typing import List, Dict, Any
# from app.config import settings

# class ElasticsearchService:
#     def __init__(self):
#         self.es = AsyncElasticsearch([settings.elasticsearch_url])
#         self.index_name = "products"


#     async def search(self, index: str = None, body: Dict[str, Any] = None, **kwargs):
#         """
#         Generic wrapper that delegates to the underlying AsyncElasticsearch client.
#         Other code calls `await self.es.search(index=..., body=...)` so exposing
#         `search` here keeps callers compatible.
#         """
#         # default to wrapper's index if none passed
#         idx = index or self.index_name
#         try:
#             return await self.es.search(index=idx, body=body, **kwargs)
#         except Exception as e:
#             # bubble up or log—keep behaviour consistent with prior code
#             print(f"ElasticsearchService.search: error: {e}")
#             raise

    
#     async def create_product_index(self):
#         """Create the products index with mapping"""
#         mapping = {
#             "mappings": {
#                 "properties": {
#                     "id": {"type": "integer"},
#                     "name": {"type": "text", "analyzer": "standard"},
#                     "description": {"type": "text", "analyzer": "standard"},
#                     "price": {"type": "float"},
#                     "category": {"type": "text", "analyzer": "standard"},
#                     "sku": {"type": "keyword"},
#                     "embedding": {"type": "dense_vector", "dims": 1024},


#                     "status": {"type": "keyword"},
#                     "stock_status": {"type": "keyword"},
#                     "image": {"type": "keyword"},
#                     "images": {"type": "keyword"},

#                     "url": {"type": "keyword"},        # ✅ CORRECT PLACE - In mapping
#                     "slug": {"type": "keyword"} 

#                 }
#             }
#         }
        
#         try:
#             exists = await self.es.indices.exists(index=self.index_name)
#             if not exists:
#                 await self.es.indices.create(index=self.index_name, body=mapping)
#                 print(f"Created index: {self.index_name}")
#         except Exception as e:
#             print(f"Error with index: {e}")


#     async def create_category_index(self):
#         """Create the categories index with mapping"""
#         category_mapping = {
#             "mappings": {
#                 "properties": {
#                     "id": {"type": "integer"},
#                     "name": {"type": "text", "analyzer": "standard"},
#                     "slug": {"type": "keyword"},
#                     "description": {"type": "text", "analyzer": "standard"},
#                     "count": {"type": "integer"},
#                     "parent": {"type": "integer"}
#                 }
#             }
#         }
        
#         try:
#             category_index = "categories"
#             exists = await self.es.indices.exists(index=category_index)
#             if not exists:
#                 await self.es.indices.create(index=category_index, body=category_mapping)
#                 print(f"Created index: {category_index}")
#         except Exception as e:
#             print(f"Error creating category index: {e}")

#     async def index_categories(self, categories: List[Dict[str, Any]]):
#         """Index product categories"""
#         category_index = "categories"
        
#         for category in categories:
#             try:
#                 doc = {
#                     "id": category.get("id"),
#                     "name": category.get("name", ""),
#                     "slug": category.get("slug", ""),
#                     "description": category.get("description", ""),
#                     "count": category.get("count", 0),
#                     "parent": category.get("parent", 0)
#                 }
                
#                 await self.es.index(index=category_index, id=category.get("id"), body=doc)
#             except Exception as e:
#                 print(f"Error indexing category {category.get('id')}: {e}")

#     async def search_categories(self, query: str = "", limit: int = 50) -> List[Dict[str, Any]]:
#         """Search categories or get all if query is empty"""
#         category_index = "categories"
        
#         try:
#             if not query:
#                 # Get all categories
#                 search_query = {"query": {"match_all": {}}, "size": limit}
#             else:
#                 # Search specific categories
#                 search_query = {
#                     "query": {
#                         "multi_match": {
#                             "query": query,
#                             "fields": ["name^2", "description"],
#                             "type": "best_fields"
#                         }
#                     },
#                     "size": limit
#                 }
            
#             result = await self.es.search(index=category_index, body=search_query)
#             return [hit["_source"] for hit in result["hits"]["hits"]]
#         except Exception as e:
#             print(f"Category search error: {e}")
#             return []

    
#     async def index_products(self, products: List[Dict[str, Any]]):
#         """Index products with embeddings"""
#         from app.services.embedding_service import EmbeddingService
#         embedding_service = EmbeddingService()
        
#         for product in products:
#             try:
#                 text_to_embed = f"{product.get('name', '')} {product.get('description', '')} {product.get('category', '')}"
#                 embedding = await embedding_service.get_embedding(text_to_embed)
                
#                 doc = {
#                     "id": product.get("id"),
#                     "name": product.get("name", ""),
#                     "description": product.get("description", ""),
#                     "price": product.get("price", 0),
#                     "category": product.get("category", ""),
#                     "sku": product.get("sku", ""),
#                     "embedding": embedding,


#                     "status": product.get("status", "publish"),           # ✅ Actual value
#                     "stock_status": product.get("stock_status", "instock"), # ✅ Actual value
#                     "image": product.get("image"),                        # ✅ Actual value
#                     "images": product.get("images", []),                   # ✅ Actual value


#                     "url": product.get("url", ""),           # ✅ FIXED - Actual URL value
#                     "slug": product.get("slug", "")          # ✅ FIXED - Actual slug value


#                 }
                
#                 await self.es.index(index=self.index_name, id=product.get("id"), body=doc)
#             except Exception as e:
#                 print(f"Error indexing product {product.get('id')}: {e}")

#     async def bulk_index(self, actions: list):
#         """
#         Bulk index actions into Elasticsearch.
#         `actions` should be a flat list like:
#             [{"index": {"_index": "coupons", "_id": "SALE30"}}, {<doc>}, ...]
#         This wraps AsyncElasticsearch.bulk and waits for refresh so results are searchable immediately.
#         """
#         try:
#             # AsyncElasticsearch.bulk accepts body as list/dict/string
#             await self.es.bulk(body=actions, refresh='wait_for')
#         except Exception as e:
#             print(f"ElasticsearchService.bulk_index error: {e}")
#             # Re-raise so callers (e.g., refresh flow) can fail loudly if needed
#             raise

#     async def close(self):
#         """Close underlying AsyncElasticsearch client to avoid unclosed aiohttp sessions."""
#         try:
#             await self.es.close()
#         except Exception as e:
#             print(f"ElasticsearchService.close: error closing es client: {e}")


#     async def create_coupons_index_if_not_exists(self, index_name: str = "coupons"):
#         """
#         Create a simple coupons index mapping if it doesn't exist.
#         Keeps mapping conservative — add fields as needed.
#         """
#         try:
#             exists = await self.es.indices.exists(index=index_name)
#             if exists:
#                 return
#             mapping = {
#                 "mappings": {
#                     "properties": {
#                         "code": {"type": "keyword"},
#                         "amount_numeric": {"type": "double"},
#                         "discount_type": {"type": "keyword"},
#                         "description": {"type": "text"},
#                         "date_start_epoch": {"type": "long"},
#                         "date_expires_epoch": {"type": "long"},
#                         "product_ids": {"type": "integer"},
#                         "product_categories": {"type": "keyword"},
#                         "minimum_amount": {"type": "double"},
#                         "maximum_amount": {"type": "double"},
#                         "active_bool": {"type": "boolean"},
#                         "last_synced_at": {"type": "long"},
#                     }
#                 }
#             }
#             await self.es.indices.create(index=index_name, body=mapping)
#             print(f"Created coupons index '{index_name}'")
#         except Exception as e:
#             print(f"create_coupons_index_if_not_exists error: {e}")
#             raise

    
#     async def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
#         """Search products with comprehensive error handling"""
#         try:
#             # Strategy 1: Simple wildcard search
#             wildcard_query = {
#                 "query": {
#                     "bool": {
#                         "should": [
#                             {"wildcard": {"name": f"*{query.lower()}*"}},
#                             {"wildcard": {"description": f"*{query.lower()}*"}},
#                             {"wildcard": {"category": f"*{query.lower()}*"}}
#                         ],
#                         "minimum_should_match": 1
#                     }
#                 },
#                 "size": limit
#             }
            
#             result = await self.es.search(index=self.index_name, body=wildcard_query)
#             products = [hit["_source"] for hit in result["hits"]["hits"]]
            
#             # Strategy 2: If no results, try match query
#             if not products:
#                 match_query = {
#                     "query": {
#                         "multi_match": {
#                             "query": query,
#                             "fields": ["name^3", "description^2", "category"],
#                             "type": "best_fields",
#                             "fuzziness": "AUTO"
#                         }
#                     },
#                     "size": limit
#                 }
                
#                 result = await self.es.search(index=self.index_name, body=match_query)
#                 products = [hit["_source"] for hit in result["hits"]["hits"]]
            
#             # Strategy 3: Fallback to show some products
#             if not products:
#                 fallback_query = {
#                     "query": {"match_all": {}},
#                     "size": limit
#                 }
                
#                 result = await self.es.search(index=self.index_name, body=fallback_query)
#                 products = [hit["_source"] for hit in result["hits"]["hits"]]
            
#             return products
#         except Exception as e:
#             print(f"Search error: {e}")
#             return []

        

#     async def fetch_relevant_chats(self, user_id: str, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
#         """
#         Return top-k relevant past chat summaries for a user.
#         - Prefer vector similarity if chat index has embeddings.
#         - Else fallback to recent chats by created_at.
#         Each item: {id, summary, snippet, created_at}
#         """
#         # try vector search on a 'chat_history' index
#         try:
#             idx = "chat_history"
#             # if embeddings exist, do an embedding similarity query
#             body = {
#                 "size": k,
#                 "query": {
#                     "script_score": {
#                         "query": {"term": {"user_id": user_id}},
#                         "script": {
#                             "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
#                             "params": {"query_vector": await self._embed_vector(query_text)}
#                         }
#                     }
#                 }
#             }
#             res = await self.es.search(index=idx, body=body)
#             hits = res.get("hits", {}).get("hits", [])
#             out = []
#             for h in hits:
#                 s = h["_source"]
#                 out.append({"id": s.get("id"), "summary": s.get("summary"), "snippet": s.get("message_snippet") or s.get("text",""), "created_at": s.get("created_at")})
#             if out:
#                 return out
#         except Exception:
#             # ignore vector path and fallback
#             pass

#         # fallback: recent chats for the user
#         try:
#             q = {
#                 "size": k,
#                 "query": {"bool": {"must": [{"term": {"user_id": user_id}}]}},
#                 "sort": [{"created_at": {"order": "desc"}}]
#             }
#             res = await self.es.search(index="chat_history", body=q)
#             hits = res.get("hits", {}).get("hits", [])
#             return [{"id": h["_id"], "summary": h["_source"].get("summary"), "snippet": (h["_source"].get("text") or "")[:200], "created_at": h["_source"].get("created_at")} for h in hits]
#         except Exception:
#             return []
        

#     async def search_products_simple(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
#         """
#         Lightweight keyword search for products. Returns list of dicts with at least id & name.
#         """
#         index = "products"  # change if your product index name is different
#         if not query or not query.strip():
#             body = {"size": limit, "query": {"match_all": {}}, "sort": [{"_score": {"order": "desc"}}]}
#         else:
#             body = {
#                 "size": limit,
#                 "query": {
#                     "multi_match": {
#                         "query": query,
#                         "fields": ["name^3", "title^3", "description", "short_description", "category", "tags"],
#                         "type": "best_fields",
#                         "operator": "or"
#                     }
#                 }
#             }
#         try:
#             res = await self.es.search(index=index, body=body)
#             hits = res.get("hits", {}).get("hits", [])
#             out = []
#             for h in hits:
#                 src = h.get("_source", {})
#                 out.append({
#                     "id": src.get("id") or h.get("_id"),
#                     "name": src.get("name") or src.get("title") or src.get("product_name"),
#                     # "score": h.get("_score"),
#                     # "raw": src
#                 })
#             return out
#         except Exception:
#             print("ElasticsearchService.search_products_simple: search failed")
#             return []


        
            

