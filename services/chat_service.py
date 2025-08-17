"""
Enhanced Chat Service for Krishi Sahayak AI
Handles farmer profile context and personalized multilingual responses.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from app.services.agentic_core import get_response
from app.services.language_service import language_service


class ChatService:
    """Service to handle enhanced chat with farmer context."""
    
    def __init__(self, krishi_agent):
        self.krishi_agent = krishi_agent
    
    def process_chat_with_context(
        self,
        user_message: str,
        farmer_context: Dict[str, Any],
        chat_history: List[Dict[str, Any]] = None,
        session_id: str = None,
        language_code: str = "en"
    ) -> str:
        """
        Process chat message with farmer context for personalized multilingual responses.
        
        Args:
            user_message: The user's input message
            farmer_context: Dictionary containing farmer profile and session info
            chat_history: Recent conversation history
            session_id: Current session identifier
            language_code: ISO 639-1 language code for response
            
        Returns:
            AI response string in the specified language
        """
        if chat_history is None:
            chat_history = []
            
        # Extract context components
        farmer_profile = farmer_context.get('farmer_profile', {})
        session_info = farmer_context.get('session_info', {})
        
        # Auto-detect language from farmer profile if not provided
        if language_code == "auto" or not language_service.is_language_supported(language_code):
            # Try to get language from farmer profile
            profile_language = farmer_profile.get('language', 'en')
            if language_service.is_language_supported(profile_language):
                language_code = profile_language
            else:
                # Auto-detect from user message
                language_code = language_service.detect_language(user_message)
        
        # Get AI response with multilingual support
        return get_response(
            self.krishi_agent, 
            user_message,
            language_code=language_code,
            farmer_context=farmer_context
        )
    
    def _build_context_prompt(
        self,
        user_message: str,
        farmer_profile: dict,
        session_info: dict,
        chat_history: List[dict]
    ) -> str:
        """
        Build a comprehensive context prompt including farmer profile and session info.
        """
        context_parts = []
        
        # Add farmer profile context if available
        if farmer_profile:
            context_parts.append("=== FARMER PROFILE ===")
            
            if farmer_profile.get('name'):
                context_parts.append(f"Farmer's Name: {farmer_profile['name']}")
            
            if farmer_profile.get('location'):
                context_parts.append(f"Location: {farmer_profile['location']}")
                
            if farmer_profile.get('latitude') and farmer_profile.get('longitude'):
                context_parts.append(f"Coordinates: {farmer_profile['latitude']}, {farmer_profile['longitude']}")
            
            if farmer_profile.get('farm_size'):
                context_parts.append(f"Farm Size: {farmer_profile['farm_size']}")
                
            if farmer_profile.get('crops'):
                crops_list = ", ".join(farmer_profile['crops'])
                context_parts.append(f"Crops Grown: {crops_list}")
                
            if farmer_profile.get('soil_type'):
                context_parts.append(f"Soil Type: {farmer_profile['soil_type']}")
                
            if farmer_profile.get('irrigation_type'):
                context_parts.append(f"Irrigation Method: {farmer_profile['irrigation_type']}")
                
            if farmer_profile.get('farming_experience'):
                context_parts.append(f"Farming Experience: {farmer_profile['farming_experience']}")
                
            if farmer_profile.get('primary_concerns'):
                context_parts.append(f"Primary Concerns: {farmer_profile['primary_concerns']}")
        
        # Add session context
        if session_info:
            context_parts.append("\n=== SESSION CONTEXT ===")
            
            if session_info.get('current_time'):
                context_parts.append(f"Current Time: {session_info['current_time']}")
                
            if session_info.get('local_date'):
                context_parts.append(f"Local Date: {session_info['local_date']}")
        
        # Add recent chat history for context
        if chat_history:
            context_parts.append("\n=== RECENT CONVERSATION ===")
            # Only include last 3 exchanges to avoid token limit
            recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history
            
            for msg in recent_history:
                role = "Farmer" if msg.get('role') == 'user' else "Assistant"
                content = msg.get('content', '')
                context_parts.append(f"{role}: {content}")
        
        # Add current user message
        context_parts.append(f"\n=== CURRENT QUESTION ===")
        context_parts.append(f"Farmer: {user_message}")
        
        # Add personalization instructions
        context_parts.append(f"\n=== INSTRUCTIONS ===")
        context_parts.append("Please provide a personalized response based on the farmer's profile above.")
        context_parts.append("Use the farmer's name when addressing them if provided.")
        context_parts.append("Consider their location, crops, and farming experience in your advice.")
        context_parts.append("If you use weather or location-specific tools, use the provided coordinates.")
        context_parts.append("Be conversational and supportive, like a knowledgeable farming friend.")
        
        return "\n".join(context_parts)


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
