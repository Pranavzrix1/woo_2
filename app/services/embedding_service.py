import httpx
from typing import List
from app.config import settings

class EmbeddingService:
    def __init__(self):
        self.ollama_url = settings.ollama_url
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding from Ollama"""
        async with httpx.AsyncClient() as client:
            try:
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
