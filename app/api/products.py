from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
from app.services.product_service import ProductService
import traceback

router = APIRouter()

@router.get("/search")
async def search_products(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    no_cache: bool = Query(False, description="Skip cache")
) -> List[Dict[str, Any]]:
    """Search products with Redis caching"""
    try:
        from app.services.service_manager import service_manager
        product_service = service_manager.get_product_service()
        results = await product_service.search_products(q, limit, use_cache=not no_cache)
        return results
    except Exception as e:
        print(f"Search endpoint error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return []

@router.post("/refresh")
async def refresh_products():
    """Refresh products from endpoint with error handling"""
    try:
        from app.services.service_manager import service_manager
        product_service = service_manager.get_product_service()
        await product_service.fetch_and_index_products()
        return {"message": "Products refreshed successfully"}
    except Exception as e:
        print(f"Refresh endpoint error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error refreshing products: {str(e)}")
    

@router.post("/refresh-categories")
async def refresh_categories():
    """Refresh categories from endpoint with error handling"""
    try:
        product_service = ProductService()
        await product_service.fetch_and_index_categories()
        return {"message": "Categories refreshed successfully"}
    except Exception as e:
        print(f"Category refresh endpoint error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error refreshing categories: {str(e)}")

@router.post("/refresh-all")
# async def refresh_everything():
#     """Refresh both products and categories"""
#     try:
#         product_service = ProductService()
#         await product_service.fetch_and_index_products()
#         await product_service.fetch_and_index_categories()
#         return {"message": "Products and categories refreshed successfully"}
#     except Exception as e:
#         print(f"Full refresh error: {e}")
#         raise HTTPException(status_code=500, detail=f"Error refreshing: {str(e)}")

async def refresh_everything():
    """Refresh both products, categories and coupons"""
    try:
        product_service = ProductService()
        await product_service.fetch_and_index_products()
        await product_service.fetch_and_index_categories()

        # NEW: refresh coupons and index to Elasticsearch
        from app.services.coupon_service import CouponService
        coupon_service = CouponService()
        await coupon_service.refresh_coupons()

        coupon_count = await coupon_service.refresh_coupons()

        return {
            "message": "Products, categories and coupons refreshed successfully",
            "coupons_indexed": coupon_count
        }

        # return {"message": "Products, categories and coupons refreshed successfully"}
    except Exception as e:
        print(f"Full refresh error: {e}")
        raise HTTPException(status_code=500, detail=f"Error refreshing: {str(e)}")

