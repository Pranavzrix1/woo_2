# tests/test_coupon_agent_flow.py
import pytest
import asyncio
from app.agents.coupon_agent import CouponAgent

@pytest.mark.asyncio
async def test_agent_returns_pitch(monkeypatch):
    # stub coupon_service.get_applicable_coupons and compute_final_price
    agent = CouponAgent()

    async def fake_get_applicable(product, cart_total=0.0, user_email=None):
        return [{
            "code": "TEST10",
            "description": "10 off",
            "discount_type": "percent",
            "amount_numeric": 10,
        }]
    agent.coupon_service.get_applicable_coupons = fake_get_applicable
    agent.coupon_service.compute_final_price = lambda product, coupon, cart_total=None: {"original_price": 100.0, "final_price": 90.0, "savings": 10.0}

    chat_context = {"last_viewed_product": {"id": 123, "name": "Test Product", "price": 100.0, "short_description": "short", "link": "https://example.com/p/123", "image": "https://example.com/img.jpg", "status": "active"}}
    res = await agent.handle_query(chat_context, "what coupon do you have for this product")
    assert "pitches" in res
    assert res["pitches"][0]["coupon_code"] == "TEST10"
    assert res["pitches"][0]["final_price"] == 90.0
