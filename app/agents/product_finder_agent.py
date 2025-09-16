# app/agents/product_finder_agent.py
from app.services.product_service import ProductService
import dspy
 
class ProductQuery(dspy.Signature):
    """Convert natural language to product search query"""
    user_query = dspy.InputField(desc="User's natural language query")
    search_terms = dspy.OutputField(desc="Optimized search terms for product search")
    response_template = dspy.OutputField(desc="How to present the results to user")
 
class ProductFinderAgent:
    def __init__(self):
        self.product_service = ProductService()
        self.query_optimizer = dspy.ChainOfThought(ProductQuery)
    
    # async def process(self, user_query: str) -> str:
    #     # Optimize search query
    #     result = self.query_optimizer(user_query=user_query)
    #     search_terms = result.search_terms
        
    #     # Search products
    #     products = await self.product_service.search_products(search_terms, limit=5)



    async def process(self, user_query: str) -> str:
        # Check for "all products" intent
        show_all_keywords = ["all products", "show all", "list all", "every product", "all items", "everything"]
        is_show_all = any(keyword in user_query.lower() for keyword in show_all_keywords)
        
        if is_show_all:
            # Get all products with higher limit
            products = await self.product_service.search_products("", limit=50)
            intro_text = "Here are all our available products:"
        else:
            # Optimize search query for specific searches
            result = self.query_optimizer(user_query=user_query)
            search_terms = result.search_terms
            products = await self.product_service.search_products(search_terms, limit=10)  # Increased from 5 to 10
            intro_text = "Here are the products I found:"
        
        if products:
            product_list = "\n".join([
                f"• {p['name']} - ${p['price']} ({p['category']})"
                for p in products
            ])
            return f"{intro_text}\n\n{product_list}\n\nWould you like more details about any of these?"
        else:
            if is_show_all:
                return "I don't have any products available right now. Please try refreshing the product catalog."
            else:
                return "I don't have any products matching your criteria right now. Could you try a different search term?"

        
        # if products:
        #     product_list = "\n".join([
        #         f"• {p['name']} - ${p['price']} ({p['category']})"
        #         for p in products
        #     ])
        #     return f"Yes! Here are the shirts I found:\n\n{product_list}\n\nWould you like more details about any of these?"
        # else:
        #     return "I don't have any shirts matching your criteria right now. Could you try a different search term?"