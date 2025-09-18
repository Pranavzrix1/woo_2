from fastapi import APIRouter, Request, HTTPException
from app.services.product_service import ProductService
import hashlib
import hmac
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
WEBHOOK_SECRET = "your-super-secret-webhook-key-2025"

@router.get("/test")
async def test_webhook():
    return {"status": "webhook endpoint is accessible", "timestamp": "2025-01-16"}

@router.post("/test")
async def test_webhook_post(request: Request):
    payload = await request.body()
    headers = dict(request.headers)
    return {
        "status": "webhook POST test successful",
        "payload_length": len(payload),
        "headers": headers
    }

def verify_webhook(payload: bytes, signature: str) -> bool:
    expected = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

@router.post("/product-created")
async def product_created(request: Request):
    try:
        payload = await request.body()
        signature = request.headers.get("x-wc-webhook-signature", "")
        
        logger.info(f"Webhook received - Headers: {dict(request.headers)}")
        logger.info(f"Webhook payload length: {len(payload)}")
        
        # Parse payload to get product info
        try:
            data = json.loads(payload.decode('utf-8'))
            logger.info(f"Product created: ID={data.get('id')}, Name={data.get('name')}")
        except Exception as e:
            logger.error(f"Failed to parse webhook payload: {e}")
        
        # Refresh products to include new one
        product_service = ProductService()
        await product_service.fetch_and_index_products()
        logger.info("Products refreshed successfully")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/product-updated") 
async def product_updated(request: Request):
    try:
        payload = await request.body()
        signature = request.headers.get("x-wc-webhook-signature", "")
        
        logger.info(f"Product update webhook received")
        
        try:
            data = json.loads(payload.decode('utf-8'))
            logger.info(f"Product updated: ID={data.get('id')}, Name={data.get('name')}")
        except Exception as e:
            logger.error(f"Failed to parse webhook payload: {e}")
        
        product_service = ProductService()
        await product_service.fetch_and_index_products()
        logger.info("Products refreshed after update")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Update webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/product-deleted")
async def product_deleted(request: Request):
    try:
        payload = await request.body()
        signature = request.headers.get("x-wc-webhook-signature", "")
        
        logger.info(f"Product delete webhook received")
        
        try:
            data = json.loads(payload.decode('utf-8'))
            logger.info(f"Product deleted: ID={data.get('id')}, Name={data.get('name')}")
        except Exception as e:
            logger.error(f"Failed to parse webhook payload: {e}")
        
        product_service = ProductService()
        await product_service.fetch_and_index_products()
        logger.info("Products refreshed after deletion")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Delete webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))