"""
Simplified Context Management Service for Krishi Sahayak AI
Handles automatic chat history summarization to manage token limits.
"""
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.config import Config # Assuming you have a config file for your API keys and prompts

class ContextService:
    """
    Manages chat history. If the history gets too long, it automatically
    creates a summary to keep the context concise for the main AI.
    """
    def __init__(self):
        # Use a fast, small model for the summarization task
        self.summarizer_llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.1,
            api_key=Config.GROQ_API_KEY
        )
        # A clear prompt that asks the LLM to extract key facts.
        self.summarization_prompt = ChatPromptTemplate.from_template(
            """
            You are an expert at summarizing conversations. Analyze the following chat history
            between a farmer and an AI assistant. Extract the key facts into a concise summary.
            If a detail is not mentioned, state 'Not specified'.

            **Farmer Profile:**
            - Name: [Farmer's name]
            - Location: [Farmer's state and district]
            - Crops: [Crops mentioned]
            - Primary Concerns: [Main problems or topics discussed]

            **Conversation Summary:**
            [A brief, one-sentence summary of the conversation's goal.]

            Here is the chat history:
            {chat_history}
            """
        )

    def _summarize_history(self, chat_history: List[Dict[str, str]]) -> str:
        """Private method to perform the actual summarization."""
        print("--- Summarizing chat history to save tokens... ---")
        # Format the list of messages into a single string
        formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
        
        chain = self.summarization_prompt | self.summarizer_llm
        summary_response = chain.invoke({"chat_history": formatted_history})
        
        return summary_response.content

    def get_context_for_ai(self, chat_history: List[Dict[str, str]]) -> str:
        """
        The main function. It decides whether to summarize or use recent history.
        """
        # If conversation is long, create a summary.
        if len(chat_history) >= 10:
            return self._summarize_history(chat_history)
        # If conversation is short, just use the last few messages as context.
        elif chat_history:
            recent_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-6:]])
            return f"This is a recent conversation. Here are the last few messages:\n{recent_history}"
        # If there is no history, provide no context.
        else:
            return "This is the beginning of the conversation."

# Create a single, global instance of the service
context_service = ContextService()