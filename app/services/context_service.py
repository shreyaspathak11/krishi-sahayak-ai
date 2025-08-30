"""
Simplified Context Management Service for Krishi Sahayak
Handles automatic chat history summarization to manage token limits.
"""
from typing import List, Dict
from langchain_groq import ChatGroq
from app.config import Config
class ContextService:
    """
    Manages chat history. If the history gets too long, it automatically
    creates a summary to keep the context concise for the main AI.
    """
    def __init__(self):
        self.summarizer_llm = ChatGroq(
            model=Config.SUMMARIZATION_MODEL,
            temperature=0.1,
            api_key=Config.GROQ_API_KEY
        )
        self.summarization_prompt = Config.SUMMARIZATION_PROMPT(chat_history="{chat_history}")

    def _summarize_history(self, chat_history: List[Dict[str, str]]) -> str:
        """Private method to perform the actual summarization."""
        formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
        
        chain = self.summarization_prompt | self.summarizer_llm
        summary_response = chain.invoke({"chat_history": formatted_history})
        
        return summary_response.content

    def get_context_for_ai(self, chat_history: List[Dict[str, str]]) -> str:
        """
        The main function. It decides whether to summarize or use recent history.
        """
        if len(chat_history) >= 10:
            return self._summarize_history(chat_history)
        elif chat_history:
            recent_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-6:]])
            return f"This is a recent conversation. Here are the last few messages:\n{recent_history}"
        else:
            return "This is the beginning of the conversation."

context_service = ContextService()