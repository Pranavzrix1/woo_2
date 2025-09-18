from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:password@postgres:5432/aiproducts"
    redis_url: str = "redis://redis:6379"
    elasticsearch_url: str = "http://elasticsearch:9200"
    ollama_url: str = "http://ollama:11434"
    # gemini_api_key: str = "AIzaSyClTVTxyvOfo1AxlIkrXkMj7apIUvPRr78"
    openai_api_key: str
    product_endpoint: str = "https://newscnbnc.webserver9.com/wp-json/mcp/v1/rpc"

    coupon_index: str = "coupons"
    coupon_sync_on_start: bool = True
    
    class Config:
        env_file = ".env"
        extra = "allow"
        arbitrary_types_allowed = True

settings = Settings()




# AIzaSyClTVTxyvOfo1AxlIkrXkMj7apIUvPRr78
# AIzaSyCsKJhgTOdQ72syjuBmOpjqE3w4Rmy99lE