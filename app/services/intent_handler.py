import dspy
from typing import Tuple
import os

class IntentClassifier(dspy.Signature):
    """
    Given a user's message, classify the intent as either:
    - 'product_finder' if the user is searching for, asking about, or describing a product or product category.
    - 'category_finder' if asking about categories/product types  # ← ADD THIS
    - 'general' for all other queries.
    """
    user_query = dspy.InputField(desc="The user's query or message. For example: 'show me shirts', 'what categories do you have?', 'hello'")
    intent = dspy.OutputField(desc="Return 'product_finder', 'category_finder', or 'general' only.")
    confidence = dspy.OutputField(desc="Confidence score between 0 and 1.")

class IntentHandler:
    def __init__(self):
        # No need to configure DSPy again if BaseAgent already did it
        self.classifier = dspy.Predict(IntentClassifier)
    
    def classify_intent(self, user_query: str) -> Tuple[str, float]:
        """Classify user intent using DSPy and OpenAI"""
        try:
            result = self.classifier(user_query=user_query)
            print("LLM result:", result)
            
            intent = result.intent.lower().strip()
            if intent.startswith("intent:"):
                intent = intent.replace("intent:", "").strip()
            
            # Safe confidence parsing
            try:
                confidence = float(getattr(result, "confidence", 1.0))
                confidence = max(0.0, min(1.0, confidence))  # Clamp between 0-1
            except (ValueError, TypeError):
                confidence = 1.0
            
            if intent in ["general", "product_finder", "category_finder"]:
                return intent, confidence
            else:
                return "general", confidence
                
        except Exception as e:
            print(f"Intent classification error: {e}")
            return "general", 0.0