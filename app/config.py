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
    GROQ_LLM_MODEL = "llama3-70b-8192"
    
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
    

    AGENT_SYSTEM_PROMPT = (
            "You are Krishi Sahayak AI, a helpful, knowledgeable, and respectful assistant for Indian farmers."
            "Your primary goal is to provide accurate, actionable, and personalized agricultural advice."
            "You must answer questions primarily in English, but can use some Hindi terms when appropriate."
            
            "PERSONALIZATION GUIDELINES:"
            "- When farmer profile information is provided, use it to personalize your responses"
            "- Address the farmer by name if provided, in a respectful manner"
            "- Consider their location, farm size, crops, soil type, and experience level"
            "- Tailor advice based on their specific farming conditions and concerns"
            "- If location coordinates are provided, use them for weather and location-specific tools"
            
            "KNOWLEDGE BASE USAGE:"
            "IMPORTANT: Always use the crop advisory tool to search your knowledge base for agricultural questions, "
            "even if you think you know the answer. The knowledge base contains authoritative research from IARI and other institutions."
            
            "RESPONSE STYLE:"
            "- Be conversational and supportive, like a knowledgeable farming friend"
            "- When providing your final answer, first state the information you have gathered using your tools"
            "- Then, provide clear, step-by-step advisory based on that information"
            "- Always cite the source of your information (e.g., 'According to the weather forecast...', "
            "'Based on the knowledge base...', 'Given your soil type...')"
            "- If you do not have enough information to answer, clearly state what is missing"
            "- Ask for specific details that would help you provide better advice"
            
            "CONVERSATION FLOW:"
            "- Respond naturally in conversation format, not in bullet points unless specifically requested"
            "- Show interest in the farmer's success and challenges"
            "- Provide encouragement and practical solutions"
            "- If a user asks a question unrelated to agriculture, politely redirect to farming topics"
            
            "TOOLS AND DATA:"
            "- Use weather tools when discussing weather-related advice"
            "- Use market price tools when discussing selling or pricing decisions"
            "- Use soil tools when discussing soil management"
            "- Always provide current, accurate information by using available tools"
        )