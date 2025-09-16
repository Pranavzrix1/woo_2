import dspy
from app.agents.base_agent import BaseAgent

class GeneralChat(dspy.Signature):
    """Handle general conversations and questions"""
    user_query = dspy.InputField(desc="The user's general query or question")
    response = dspy.OutputField(desc="A helpful and informative response")

class GeneralAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.chat = dspy.ChainOfThought(GeneralChat)
    
    async def process(self, query: str) -> str:
        """Process general queries"""
        try:
            result = self.chat(user_query=query)
            return result.response
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
