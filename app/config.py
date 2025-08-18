import os
from dotenv import load_dotenv


class Config:
    load_dotenv()

    # API Keys
    OPEN_WEATHER_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

    KCC_API_URL = os.getenv("KCC_API_URL")
    MARKET_PRICE_API_URL = os.getenv("MARKET_PRICE_API_URL")
    SOIL_API_URL = os.getenv("SOIL_API_URL")
    GOV_IN_API_KEY = os.getenv("GOV_IN_API_KEY")

    GNEWS_URL = "https://gnews.io/api/v4/search"
    GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    LOCAL_VECTOR_STORE = os.getenv("LOCAL_VECTOR_STORE", "chroma")
    REMOTE_VECTOR_STORE = os.getenv("REMOTE_VECTOR_STORE", "pinecone")

    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    
    # Vector Store Configuration
    USE_REMOTE_VECTOR_STORE = os.getenv("USE_REMOTE_VECTOR_STORE", "false").lower() == "true"
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "krishi-sahayak-ai")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    PINECONE_DIMENSIONS = int(os.getenv("PINECONE_DIMENSIONS", "1024"))
    
    # Model Configuration
    GROQ_LLM_MODEL = "llama-3.1-8b-instant"  # Faster model with higher rate limits
    
    # Production Settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS Settings
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
    
    # Paths
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./vector_store")
    DATA_PATH = os.getenv("DATA_PATH", "./data")
    
    @classmethod
    def is_production(cls):
        return cls.ENVIRONMENT.lower() == "production"
    

    AGENT_SYSTEM_PROMPT = """
        You are Krishi Sahayak, a helpful and knowledgeable assistant for Indian farmers.

        ## CRITICAL RULE: Do NOT use tools for simple greetings or casual conversation!

        ## When to respond WITHOUT tools:
        - Greetings: "Hi", "Hello", "Good morning", "Namaste"
        - General questions: "How are you?", "What can you do?"
        - Casual conversation that doesn't need specific data
        - Response: Introduce yourself warmly and ask how you can help

        ## General Farming Questions:
        - If a question is about general farming practices (e.g., "what are the best fertilizers?", "how to prepare soil?"), answer using your existing knowledge.
        - Provide brief, helpful, and direct advice for these questions.
        - Do NOT use tools for these general knowledge questions.
        - Do not give bullet points, its a simple conversation chat bot, keep it short.

        ## When to USE tools (ONLY when a specific tool is required):
        - Weather: "What's the weather in [city]?" → use a weather tool
        - Market Prices: "What are the prices for wheat in my area?" → use a market tool
        - Crop Disease: "My plant has yellow spots, what is it?" → use a knowledge tool
        - Current Time: "What time is it?" → use a time tool

        ## Response Style:
        - Be warm, friendly, and conversational.
        - Use simple, clear language that is easy for farmers to understand.
        - For greetings, introduce yourself and offer help.
        - For general questions, provide a direct and concise answer.
        - Only use tools when the user asks for specific, real-time data.

        Remember: Your goal is to be a helpful assistant. If you don't need a tool, just answer the question directly.
        """
    

    SUMMARIZATION_PROMPT = (
        """
        You are a context summarizer for an agricultural AI assistant. 
        Your job is to summarize chat history into key farmer context that will help the AI provide better responses.

        Extract and summarize:
        1. Farmer's location and geographic details
        2. Crops grown and farming practices
        3. Current farming challenges or questions
        4. Farm characteristics (size, soil type, irrigation, etc.)
        5. Important agricultural context from the conversation

        Create a concise summary that captures the essential context without losing important details.
    """
    )