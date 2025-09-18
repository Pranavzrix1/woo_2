from fastapi import APIRouter
from app.services.service_manager import service_manager

router = APIRouter()

@router.post("/clear")
async def clear_cache():
    """Clear all search cache"""
    try:
        redis_service = service_manager.get_redis_service()
        await redis_service.invalidate_search_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        return {"error": str(e)}