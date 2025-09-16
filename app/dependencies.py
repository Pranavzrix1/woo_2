from functools import lru_cache
from app.services.product_service import ProductService
from app.services.elasticsearch_service import ElasticsearchService
from app.services.embedding_service import EmbeddingService
from app.services.intent_handler import IntentHandler
from app.services.cache_service import CacheService
from app.agents.general_agent import GeneralAgent
from app.agents.category_finder_agent import CategoryFinderAgent

# Singleton instances
_product_service = None
_elasticsearch_service = None
_embedding_service = None
_intent_handler = None
_general_agent = None
_category_agent = None
_cache_service = None

@lru_cache()
def get_product_service() -> ProductService:
    global _product_service
    if _product_service is None:
        _product_service = ProductService()
    return _product_service

@lru_cache()
def get_elasticsearch_service() -> ElasticsearchService:
    global _elasticsearch_service
    if _elasticsearch_service is None:
        _elasticsearch_service = ElasticsearchService()
    return _elasticsearch_service

@lru_cache()
def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

@lru_cache()
def get_intent_handler() -> IntentHandler:
    global _intent_handler
    if _intent_handler is None:
        _intent_handler = IntentHandler()
    return _intent_handler

@lru_cache()
def get_general_agent() -> GeneralAgent:
    global _general_agent
    if _general_agent is None:
        _general_agent = GeneralAgent()
    return _general_agent

@lru_cache()
def get_category_agent() -> CategoryFinderAgent:
    global _category_agent
    if _category_agent is None:
        _category_agent = CategoryFinderAgent()
    return _category_agent

@lru_cache()
def get_cache_service() -> CacheService:
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service

async def cleanup_services():
    """Cleanup all singleton services"""
    global _product_service, _embedding_service, _cache_service
    if _product_service:
        await _product_service.close()
    if _embedding_service:
        await _embedding_service.close()
    if _cache_service:
        await _cache_service.close()