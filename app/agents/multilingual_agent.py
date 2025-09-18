import dspy
import json
from typing import Dict, Any
from app.agents.product_finder_agent import ProductFinderAgent
from app.agents.sales_executive_agent import SalesExecutiveAgent
from app.agents.category_finder_agent import CategoryFinderAgent
from app.agents.general_agent import GeneralAgent

class LanguageProcessor(dspy.Signature):
    """Detect language and translate if needed"""
    user_query = dspy.InputField(desc="User's query in any language")
    detected_language = dspy.OutputField(desc="ISO language code (e.g., 'en', 'es', 'fr', 'hi', 'ar')")
    english_query = dspy.OutputField(desc="Query translated to English if not already English")

class ResponseTranslator(dspy.Signature):
    """Translate response back to user's language"""
    english_response = dspy.InputField(desc="Response in English")
    target_language = dspy.InputField(desc="Target language code")
    translated_response = dspy.OutputField(desc="Response translated to target language")

class MultilingualAgent:
    def __init__(self):
        self.language_processor = dspy.ChainOfThought(LanguageProcessor)
        self.response_translator = dspy.ChainOfThought(ResponseTranslator)
        
        # Initialize existing agents
        self.agents = {
            'product_finder': ProductFinderAgent(),
            'sales_executive': SalesExecutiveAgent(),
            'category_finder': CategoryFinderAgent(),
            'general': GeneralAgent()
        }
    
    async def process(self, query: str, intent: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            # Step 1: Detect language and translate to English
            lang_result = self.language_processor(user_query=query)
            detected_lang = lang_result.detected_language
            english_query = lang_result.english_query
            
            # Step 2: Route to appropriate agent with English query
            agent_response = await self._route_to_agent(english_query, intent, context)
            
            # Step 3: If not English, translate response back
            if detected_lang.lower() != 'en':
                # Handle object responses (like sales_executive with recommendations)
                if isinstance(agent_response, dict) and 'recommendations' in agent_response:
                    # Translate the pitch but keep recommendations structure
                    pitch_translation = self.response_translator(
                        english_response=agent_response.get('pitch', ''),
                        target_language=detected_lang
                    )
                    final_response = {
                        'pitch': pitch_translation.translated_response,
                        'recommendations': agent_response['recommendations'],
                        'query': query
                    }
                else:
                    # Regular string response translation
                    translation_result = self.response_translator(
                        english_response=str(agent_response),
                        target_language=detected_lang
                    )
                    final_response = translation_result.translated_response
            else:
                final_response = agent_response
            
            return {
                "response": final_response,
                "detected_language": detected_lang,
                "original_query": query,
                "english_query": english_query
            }
            
        except Exception as e:
            print(f"MultilingualAgent error: {e}")
            # Fallback to original agent
            return await self._route_to_agent(query, intent, context)
    
    async def _route_to_agent(self, query: str, intent: str, context: Dict[str, Any] = None):
        """Route query to appropriate agent"""
        try:
            if intent == 'coupon':
                # Handle coupon agent separately due to different signature
                from app.agents.coupon_agent import CouponAgent
                coupon_agent = CouponAgent()
                result = await coupon_agent.handle_query(context or {}, query)
                # Ensure result is returned as-is (object structure preserved)
                return result
            elif intent in self.agents:
                if intent == 'sales_executive':
                    result = await self.agents[intent].process(query, user_id=context.get('user_id') if context else None)
                else:
                    result = await self.agents[intent].process(query)
                # Preserve object structure - don't convert to string
                return result
            else:
                result = await self.agents['general'].process(query)
                return result
        except Exception as e:
            print(f"Agent routing error: {e}")
            return f"I encountered an error processing your request. Please try again."