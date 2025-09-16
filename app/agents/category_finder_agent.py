from app.services.product_service import ProductService
import dspy

class CategoryQuery(dspy.Signature):
    """Convert natural language to category search query"""
    user_query = dspy.InputField(desc="User's natural language query about categories")
    search_terms = dspy.OutputField(desc="Optimized search terms for category search")
    response_template = dspy.OutputField(desc="How to present the categories to user")

class CategoryFinderAgent:
    def __init__(self):
        self.product_service = ProductService()
        self.query_optimizer = dspy.ChainOfThought(CategoryQuery)

    async def process(self, user_query: str) -> str:
        # Check for "all categories" intent
        show_all_keywords = ["all categories", "show all categories", "list all categories", 
                           "what categories", "categories do you have", "product categories"]
        is_show_all = any(keyword in user_query.lower() for keyword in show_all_keywords)
        
        if is_show_all:
            # Get all categories
            categories = await self.product_service.search_categories("", limit=50)
            intro_text = "Here are all our product categories:"
        else:
            # Search specific categories
            result = self.query_optimizer(user_query=user_query)
            search_terms = result.search_terms
            categories = await self.product_service.search_categories(search_terms, limit=20)
            intro_text = "Here are the categories I found:"
        
        if categories:
            category_list = "\n".join([
                f"• {cat['name']} ({cat['count']} products)"
                for cat in categories
            ])
            return f"{intro_text}\n\n{category_list}\n\nWould you like to see products from any of these categories?"
        else:
            if is_show_all:
                return "I don't have any categories available right now. Please try refreshing the catalog."
            else:
                return "I don't have any categories matching your request. Could you try a different search?"
