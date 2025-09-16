from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
from contextlib import asynccontextmanager

from app.config import settings
from app.api import products, chat
from app.dependencies import get_product_service, get_elasticsearch_service, cleanup_services

# ...existing code...
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
<<<<<<< Updated upstream
    es_service = ElasticsearchService()
    product_service = ProductService()
    
    # Store services for cleanup
    app.state.product_service = product_service
=======
    es_service = get_elasticsearch_service()
    product_service = get_product_service()
>>>>>>> Stashed changes

    # Wait for Elasticsearch to be ready
    import aiohttp
    import time

    es_url = settings.elasticsearch_url
    max_wait = 60  # seconds
    start = time.time()
    session = None
    
    while True:
        try:
            if not session:
<<<<<<< Updated upstream
                session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
=======
                timeout = aiohttp.ClientTimeout(total=10)
                session = aiohttp.ClientSession(timeout=timeout)
>>>>>>> Stashed changes
            async with session.get(f"{es_url}/_cluster/health") as resp:
                if resp.status == 200:
                    break
        except Exception as e:
            print(f"ES health check failed: {e}")
        
        if time.time() - start > max_wait:
            print("Elasticsearch did not become ready in time.")
            break
        await asyncio.sleep(2)
    
    # Cleanup session
    if session:
        await session.close()

    await es_service.create_product_index()
    await es_service.create_category_index()  # ← ADD THIS

    await product_service.fetch_and_index_products()
    await product_service.fetch_and_index_categories()  # ← ADD THIS
    
    # Store services for cleanup
    app.state.product_service = product_service

    yield
    print("Shutting down...")
<<<<<<< Updated upstream
    # Cleanup HTTP clients
    await product_service.close()
    # Also cleanup embedding service if it exists
    if hasattr(es_service, '_embedding_service'):
        await es_service._embedding_service.close()
=======
    # Cleanup all services
    await cleanup_services()
>>>>>>> Stashed changes
# ...existing code...



app = FastAPI(
    title="AI Product Search",
    description="AI-powered product search with intent detection",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
