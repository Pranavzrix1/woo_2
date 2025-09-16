import dspy
from abc import ABC, abstractmethod
import os

class BaseAgent(ABC):
    def __init__(self):
        # Configure DSPy once here
        if not hasattr(dspy.settings, 'lm') or dspy.settings.lm is None:
            lm = dspy.LM('openai/gpt-4o-mini', api_key=os.getenv("openai_api_key"))
            dspy.configure(lm=lm)
    
    @abstractmethod
    async def process(self, query: str) -> str:
        pass