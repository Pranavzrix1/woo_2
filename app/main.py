# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.api import products, chat, webhooks
from app.services.product_service import ProductService
from app.services.elasticsearch_service import ElasticsearchService
from app.api.coupons import router as coupons_router
from app.api.cache import router as cache_router

app = FastAPI(title="AI Product Search")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    # optional: nothing here if using lifespan below
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.service_manager import service_manager
    
    try:
        # Optionally refresh products and coupons on startup
        if getattr(settings, "coupon_sync_on_start", False):
            try:
                product_service = service_manager.get_product_service()
                await product_service.fetch_and_index_products()
            except Exception as e:
                print("Startup fetch_and_index_products failed:", e)
        yield
    finally:
        # Close all services through service manager
        import asyncio
        try:
            await service_manager.close_all()
        except Exception as e:
            print(f"Error closing services: {e}")
        
        # Allow time for connections to close
        await asyncio.sleep(0.3)

app.router.lifespan_context = lifespan

app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(coupons_router, prefix="/api/coupons")
app.include_router(cache_router, prefix="/api/cache", tags=["cache"])
app.include_router(webhooks.router, prefix="/wp-json/webhooks/woocommerce", tags=["webhooks"])

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    return {"status": "healthy"}




# from fastapi import FastAPI, Request
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import HTMLResponse
# import asyncio
# from contextlib import asynccontextmanager

# from app.config import settings
# from app.api import products, chat
# from app.services.product_service import ProductService
# from app.services.elasticsearch_service import ElasticsearchService

# from app.api.coupons import router as coupons_router


# # ...existing code...
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("Starting up...")
#     es_service = ElasticsearchService()
#     product_service = ProductService()

#     # Wait for Elasticsearch to be ready
#     import aiohttp
#     import time

#     es_url = settings.elasticsearch_url
#     max_wait = 60  # seconds
#     start = time.time()
#     while True:
#         try:
#             async with aiohttp.ClientSession() as session:
#                 async with session.get(f"{es_url}/_cluster/health") as resp:
#                     if resp.status == 200:
#                         break
#         except Exception:
#             pass
#         if time.time() - start > max_wait:
#             print("Elasticsearch did not become ready in time.")
#             break
#         await asyncio.sleep(2)

#     await es_service.create_product_index()
#     await es_service.create_category_index()  # ← ADD THIS

#     await product_service.fetch_and_index_products()
#     await product_service.fetch_and_index_categories()  # ← ADD THIS

#     yield
#     print("Shutting down...")
# # ...existing code...



# app = FastAPI(
#     title="AI Product Search",
#     description="AI-powered product search with intent detection",
#     version="1.0.0",
#     lifespan=lifespan
# )

# # Mount static files
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # Include routers
# app.include_router(products.router, prefix="/api/products", tags=["products"])
# app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

# app.include_router(coupons_router, prefix="/api/coupons")



# @app.get("/", response_class=HTMLResponse)
# async def read_root():
#     with open("static/index.html", "r") as f:
#         return HTMLResponse(content=f.read())

# @app.get("/health")
# async def health_check():
#     return {"status": "healthy"}
