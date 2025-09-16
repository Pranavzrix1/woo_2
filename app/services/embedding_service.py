import httpx
from typing import List
from app.config import settings

class EmbeddingService:
    def __init__(self):
        self.ollama_url = settings.ollama_url
        self._client = None
    
    async def get_client(self):
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding from Ollama"""
        try:
            client = await self.get_client()
            response = await client.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={
                        "model": "mxbai-embed-large:335m",
                        "prompt": text
                    }
                )
                
            if response.status_code == 200:
                return response.json()["embedding"]
            else:
                print(f"Embedding error: {response.status_code}")
                return [0.0] * 1024  # Return zero vector as fallback
                
        except Exception as e:
            print(f"Embedding exception: {e}")
            return [0.0] * 1024
