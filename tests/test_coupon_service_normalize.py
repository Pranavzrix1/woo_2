# tests/test_coupon_service_normalize.py
import pytest
from app.services.coupon_service import CouponService

def test_normalize_basic():
    svc = CouponService()
    raw = {
        "id": 111,
        "code": "sale 30",
        "amount": "10",
        "discount_type": "percent",
        "description": "We are offering 10%",
        "date_start": "2025-09-15",
        "date_expires": "2025-10-31",
        "product_ids": [123],
        "minimum_amount": "10.00"
    }
    normalized = svc._normalize(raw)
    assert normalized["code"].lower().startswith("sale")
    assert isinstance(normalized["amount_numeric"], float)
    assert normalized["active_bool"] in (True, False)
    assert "date_expires_epoch" in normalized
