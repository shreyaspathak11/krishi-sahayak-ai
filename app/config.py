import os
from dotenv import load_dotenv


class Config:
    """Configuration class for Krishi Sahayak"""
    
    # Load environment variables
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

    # Vector Store Configuration
    LOCAL_VECTOR_STORE = os.getenv("LOCAL_VECTOR_STORE", "chroma")
    REMOTE_VECTOR_STORE = os.getenv("REMOTE_VECTOR_STORE", "pinecone")
    USE_REMOTE_VECTOR_STORE = os.getenv("USE_REMOTE_VECTOR_STORE", "false").lower() == "true"
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "krishi-sahayak-ai")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    PINECONE_DIMENSIONS = int(os.getenv("PINECONE_DIMENSIONS", "1024"))

    PINECONE_EMBEDDINGS_MODEL = "BAAI/bge-large-en-v1.5"
    CHROMA_EMBEDDINGS_MODEL = "sentence-transformers/all-mpnet-base-v2"

    # Model Configuration
    GROQ_LLM_MODEL = os.getenv("GROQ_LLM_MODEL", "llama-3.1-8b-instant")
    SUMMARIZATION_MODEL = os.getenv("SUMMARIZATION_MODEL", "llama-3.1-8b-instant")

    # Production Settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS Settings - More flexible for deployment
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
    
    # Paths - More flexible for different deployment environments
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./vector_store")
    DATA_PATH = os.getenv("DATA_PATH", "./data")
    
    @classmethod
    def is_production(cls):
        """Check if running in production environment"""
        return cls.ENVIRONMENT.lower() == "production"

    AGENT_SYSTEM_PROMPT = """
        You are Krishi Sahayak, a helpful and knowledgeable assistant for Indian farmers.

        ## IMPORTANT: Always respond in valid JSON format with this exact structure:
        {
            "response_type": "greeting|general_knowledge|tool_required|error",
            "needs_tools": false,
            "content": "Your response text here",
            "language": "detected_language_code",
            "confidence": 0.95,
            "tools_to_use": ["tool_name1", "tool_name2"] or [],
            "context_type": "weather|market|crop|soil|pest|general|greeting"
        }

        ## Response Classification Rules:

        ### response_type: "greeting" (needs_tools: false)
        - Greetings: "Hi", "Hello", "Good morning", "Namaste"
        - General questions: "How are you?", "What can you do?"
        - Introduction requests
        - Example: {"response_type": "greeting", "needs_tools": false, "content": "Namaste! I'm Krishi Sahayak, your agricultural assistant. How can I help you today?", "language": "en", "confidence": 0.95, "tools_to_use": [], "context_type": "greeting"}

        ### response_type: "general_knowledge" (needs_tools: false)
        - General farming practices questions
        - Basic agricultural advice that doesn't need real-time data
        - Crop rotation, fertilizer basics, soil preparation, etc.
        - Example: {"response_type": "general_knowledge", "needs_tools": false, "content": "For better tomato growth, use well-drained soil with pH 6.0-6.8, and ensure adequate spacing between plants.", "language": "en", "confidence": 0.90, "tools_to_use": [], "context_type": "crop"}

        ### response_type: "tool_required" (needs_tools: true)
        - Weather queries: "What's the weather in Delhi?"
        - Market prices: "What are wheat prices today?"
        - Current time/date requests
        - Specific location-based or real-time data needs
        - Example: {"response_type": "tool_required", "needs_tools": true, "content": "Let me check the current weather in Delhi for you.", "language": "en", "confidence": 0.95, "tools_to_use": ["get_weather_forecast"], "context_type": "weather"}

        ### response_type: "error" (needs_tools: false)
        - When unable to understand or process the request
        - Technical difficulties
        - Example: {"response_type": "error", "needs_tools": false, "content": "I apologize, but I couldn't understand your request. Could you please rephrase it?", "language": "en", "confidence": 0.80, "tools_to_use": [], "context_type": "general"}

        ## Guidelines:
        - Always return valid JSON
        - Set confidence based on your certainty about the response
        - Use appropriate context_type for better categorization
        - Keep content concise and farmer-friendly
        - Detect language from input and set accordingly
        """

    @classmethod
    def SUMMARIZATION_PROMPT(cls, chat_history):
        return f"""
        You are a context summarizer for an agricultural AI assistant. 
        Your job is to summarize chat history into key farmer context that will help the AI provide better responses.

        Extract and summarize:
        1. Farmer's location and geographic details
        2. Crops grown and farming practices
        3. Current farming challenges or questions
        4. Farm characteristics (size, soil type, irrigation, etc.)
        5. Important agricultural context from the conversation
        {chat_history}

        Create a concise summary that captures the essential context without losing important details.
        """

    JSON_RESPONSE_SCHEMA = {
        "type": "object",
        "properties": {
            "response_type": {
                "type": "string",
                "enum": ["greeting", "general_knowledge", "tool_required", "error"]
            },
            "needs_tools": {"type": "boolean"},
            "content": {"type": "string"},
            "language": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "tools_to_use": {
                "type": "array",
                "items": {"type": "string"}
            },
            "context_type": {
                "type": "string",
                "enum": ["weather", "market", "crop", "soil", "pest", "general", "greeting"]
            }
        },
        "required": ["response_type", "needs_tools", "content", "language", "confidence", "tools_to_use", "context_type"]
    }