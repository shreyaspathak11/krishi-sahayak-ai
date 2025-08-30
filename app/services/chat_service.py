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
        farmer_context_summary = context_service.get_context_for_ai(chat_history)

        # 2. Call your main AI agent with the user's message and the optimized context
        ai_response = get_response(
            self.krishi_agent,
            user_input=user_message,
            farmer_context=farmer_context_summary, 
        )
        
        return ai_response