from typing import List, Dict, Any
from app.services.agentic_core import get_response
from app.services.context_service import context_service 

class ChatService:
    """Simplified service to handle chat with automatic context management."""
    
    def __init__(self, krishi_agent):
        self.krishi_agent = krishi_agent
    
    def process_chat(
        self,
        user_message: str,
        chat_history: List[Dict[str, Any]]
    ) -> str:
        """
        Processes a user message, manages context, and gets a response.

        Args:
            user_message: The user's input message.
            chat_history: The full conversation history for the current session.
            
        Returns:
            The AI's response as a string.
        """
        # 1. Get the current context (either a summary or recent messages)
        # The context_service handles all the logic automatically.
        farmer_context_summary = context_service.get_context_for_ai(chat_history)

        # 2. Call your main AI agent with the user's message and the optimized context
        ai_response = get_response(
            self.krishi_agent,
            user_input=user_message,
            farmer_context=farmer_context_summary, 
        )
        
        return ai_response


class FallbackResponseService:
    """Service to provide fallback responses when AI is unavailable."""
    
    @staticmethod
    def get_fallback_response(user_message: str) -> str:
        """Get appropriate fallback response based on user message."""
        message = user_message.lower()
        
        if any(keyword in message for keyword in ['weather', 'rain', 'temperature']):
            return "I'd love to help you with weather information! However, I'm currently having trouble connecting to my weather services. Please try again in a moment."
        
        elif any(keyword in message for keyword in ['crop', 'plant', 'seed', 'harvest']):
            return "I can provide crop advisory, but I'm currently experiencing some technical difficulties. In the meantime, ensure your crops are getting adequate water and check for any signs of pests or diseases."
        
        elif any(keyword in message for keyword in ['price', 'market', 'sell', 'buy']):
            return "I apologize, but I can't access current market prices right now. I recommend checking your local market or agricultural department for the latest pricing information."
        
        elif any(keyword in message for keyword in ['soil', 'fertilizer', 'manure']):
            return "Soil health is crucial for good crops! While I can't access specific soil data right now, remember to maintain proper pH levels and organic matter in your soil."
        
        elif any(keyword in message for keyword in ['pest', 'disease', 'insect']):
            return "For pest and disease management, I recommend consulting your local agricultural extension officer. In general, regular monitoring and early intervention are key to preventing major infestations."
        
        else:
            return "Thank you for your question! I'm experiencing some technical difficulties right now, but I'm here to help with all your farming needs. Please try asking again in a moment."
