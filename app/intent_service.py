import dspy
from enum import Enum
 
class Intent(Enum):
    PRODUCT_SEARCH = "product_search"
    PRODUCT_INQUIRY = "product_inquiry" 
    GENERAL_CHAT = "general_chat"
    HELP = "help"
 
class IntentClassifier(dspy.Signature):
    """Classify user intent for routing to appropriate agent"""
    query = dspy.InputField(desc="User's query")
    intent = dspy.OutputField(desc="Detected intent: product_search, product_inquiry, general_chat, or help")
    confidence = dspy.OutputField(desc="Confidence score 0-1")
 
class IntentDetectionService:
    def __init__(self):
        self.classifier = dspy.ChainOfThought(IntentClassifier)
    
    async def detect_intent(self, query: str) -> tuple[Intent, float]:
        result = self.classifier(query=query)
        intent = Intent(result.intent)
        confidence = float(result.confidence)
        return intent, confidence