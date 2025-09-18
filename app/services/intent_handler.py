import dspy
from typing import Tuple
import os

class IntentClassifier(dspy.Signature):
    """
    Given a user's message, classify the intent as either:
    - 'product_finder' if the user is searching for, asking about, or describing a product or product category.
    - 'category_finder' if asking about categories/product types
    - 'general' for all other queries.
    """
    user_query = dspy.InputField(desc="The user's query or message")
    intent = dspy.OutputField(desc="Return 'product_finder', 'category_finder', or 'general' only.")
    confidence = dspy.OutputField(desc="Confidence score between 0 and 1.")


class IntentHandler:
    """
    Lightweight rule-based fallback intent handler.
    """

    def __init__(self):
        self.dspy_available = False
        try:
            self._dspy_classifier = dspy.ChainOfThought(IntentClassifier)
            self.dspy_available = True
        except Exception:
            self._dspy_classifier = None

    def classify_intent(self, message: str) -> tuple[str, float]:
        q = (message or "").lower()
        # Enhanced coupon detection
        coupon_keywords = ("coupon", "coupon code", "promo", "promocode", "discount", "coupons", "offers", 
                          "apply", "test10", "sale 30", "which product", "how many total", "any other")
        if any(k in q for k in coupon_keywords):
            return "coupon", 0.98
        if any(k in q for k in ("category", "categories", "kind of", "type of")):
            return "category_finder", 0.90
        if any(k in q for k in ("find", "search", "looking for", "do you have", "available", "show me", "show all", "list all", "all products", "all items")):
            return "product_finder", 0.90
        return "general", 0.6
