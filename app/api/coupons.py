# app/api/coupons.py
from fastapi import APIRouter, HTTPException
from app.services.coupon_service import CouponService

router = APIRouter()

@router.post("/refresh")
async def refresh_coupons():
    try:
        from app.services.service_manager import service_manager
        svc = service_manager.get_coupon_service()
        count = await svc.refresh_coupons()
        return {"message": "Coupons refreshed", "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
