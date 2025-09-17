from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
from contextlib import asynccontextmanager

from app.config import settings
from app.api import products, chat
from app.services.product_service import ProductService
from app.services.elasticsearch_service import ElasticsearchService

# ...existing code...
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    es_service = ElasticsearchService()
    product_service = ProductService()
=======
=======
>>>>>>> Stashed changes
    es_service = get_elasticsearch_service()
    product_service = get_product_service()

    # Wait for Elasticsearch to be ready
    import aiohttp
    import time

    es_url = settings.elasticsearch_url
    max_wait = 60  # seconds
    start = time.time()
    while True:
        try:
<<<<<<< Updated upstream
<<<<<<< Updated upstream
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{es_url}/_cluster/health") as resp:
                    if resp.status == 200:
                        break
        except Exception:
            pass
=======
=======
>>>>>>> Stashed changes
            if not session:
                timeout = aiohttp.ClientTimeout(total=10)
                session = aiohttp.ClientSession(timeout=timeout)
            async with session.get(f"{es_url}/_cluster/health") as resp:
                if resp.status == 200:
                    break
        except Exception as e:
            print(f"ES health check failed: {e}")
        
>>>>>>> Stashed changes
        if time.time() - start > max_wait:
            print("Elasticsearch did not become ready in time.")
            break
        await asyncio.sleep(2)

    await es_service.create_product_index()
    await es_service.create_category_index()  # ← ADD THIS

    await product_service.fetch_and_index_products()
    await product_service.fetch_and_index_categories()  # ← ADD THIS

    yield
    print("Shutting down...")
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
=======
>>>>>>> Stashed changes
    # Cleanup all services
    await cleanup_services()
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
