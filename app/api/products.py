from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.models.requests import ProductSearchRequest
from app.services.product_service import ProductService
from app.services.cache_service import CacheService
from app.dependencies import get_product_service, get_cache_service
import traceback

router = APIRouter()

@router.get("/search")
async def search_products(
    q: str, 
    limit: int = 10,
    product_service: ProductService = Depends(get_product_service),
    cache_service: CacheService = Depends(get_cache_service)
) -> List[Dict[str, Any]]:
    """Search products with comprehensive error handling"""
    try:
        # Validate input
        search_request = ProductSearchRequest(q=q, limit=limit)
        
        # Try cache first
        cached_results = await cache_service.get_search_results(search_request.q, search_request.limit)
        if cached_results is not None:
            return cached_results
        
        # Get from service and cache
        results = await product_service.search_products(search_request.q, search_request.limit)
        await cache_service.cache_search_results(search_request.q, search_request.limit, results)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Search endpoint error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/refresh")
async def refresh_products(product_service: ProductService = Depends(get_product_service)):
    """Refresh products from endpoint with error handling"""
    try:
        await product_service.fetch_and_index_products()
        return {"message": "Products refreshed successfully"}
    except Exception as e:
        from app.utils.error_handler import handle_service_error
        raise handle_service_error(e, "Product refresh")

@router.post("/refresh-categories")
async def refresh_categories(product_service: ProductService = Depends(get_product_service)):
    """Refresh categories from endpoint with error handling"""
    try:
        await product_service.fetch_and_index_categories()
        return {"message": "Categories refreshed successfully"}
    except Exception as e:
        from app.utils.error_handler import handle_service_error
        raise handle_service_error(e, "Category refresh")

@router.post("/refresh-all")
async def refresh_everything(product_service: ProductService = Depends(get_product_service)):
    """Refresh both products and categories"""
    try:
        await product_service.fetch_and_index_products()
        await product_service.fetch_and_index_categories()
        return {"message": "Products and categories refreshed successfully"}
    except Exception as e:
        from app.utils.error_handler import handle_service_error
        raise handle_service_error(e, "Full refresh")