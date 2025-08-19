from typing import Dict, List, Any

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from app.config import Config
from app.services.language_service import language_service
from app.services.context_service import context_service
import app.tools as tools

# --- AGENT SETUP ---

def create_krishi_agent():
    """
    Creates and returns the main agent executor for Krishi Sahayak AI.
    """
    print("--- Initializing Krishi Sahayak AI Agent ---")
    
    llm = ChatGroq(
        model=Config.GROQ_LLM_MODEL,
        temperature=0,
        api_key=Config.GROQ_API_KEY,
        max_retries=2,
        request_timeout=30
    )
    
    # 1. Consolidate and simplify the list of available tools
    available_tools = [
        tools.get_weather_forecast,
        tools.get_air_pollution_data,
        tools.get_uv_index,
        tools.get_crop_advisory,
        tools.get_market_prices,
        tools.get_soil_and_irrigation_advice,
        tools.get_agricultural_news,
        tools.get_current_datetime,
    ]
    
    # 2. Create a simpler prompt template that works with the agent framework
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
Config.AGENT_SYSTEM_PROMPT
        )),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, available_tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=available_tools, 
        verbose=False,  # Turn off verbose to reduce noise
        max_iterations=3,  # Limit iterations to prevent infinite loops
        max_execution_time=30,  # Stop after 30 seconds
        early_stopping_method="generate",  # Stop early if possible
        handle_parsing_errors="Check your output and make sure it follows the correct format! For simple greetings, just respond naturally without using tools."
    )
    
    print("--- Agent Initialized Successfully ---")
    return agent_executor

def get_response(
    agent_executor: AgentExecutor, 
    user_input: str, 
    language_code: str = "en",
    chat_history: List[Dict[str, str]] = None
) -> str:
    """
    Invokes the agent with the user's query.
    Context management and farmer context are handled internally by the backend.
    
    Args:
        agent_executor: The initialized agent executor.
        user_input: The user's current message.
        language_code: The language code for the response.
        chat_history: The conversation history from frontend (optional).
        
    Returns:
        The AI's response as a string.
    """
    print(f"\n--- Invoking Agent with Query: '{user_input}' ---")

    # Initialize defaults
    if chat_history is None:
        chat_history = []

    # 1. Determine the language for the response
    if not language_code:
        language_code = language_service.detect_language(user_input)
    language_name = language_service.get_language_name(language_code)
    
    # 2. Process context internally (backend handles this, not frontend)
    context_summary = ""
    if chat_history:
        # Use context service to get optimized context
        context_summary = context_service.get_context_for_ai(chat_history)
    
    try:
        # 3. Invoke the agent with context if available
        if context_summary:
            # Include context in the input for better responses
            input_with_context = f"Context from previous conversation: {context_summary}\n\nUser question: {user_input}"
        else:
            input_with_context = user_input
            
        # Add a simple check for greetings to avoid tool usage
        simple_greetings = ['hi', 'hello', 'hey', 'namaste', 'good morning', 'good evening', 'how are you']
        if user_input.lower().strip() in simple_greetings:
            return "Hello! I'm Krishi Sahayak, your agricultural assistant. I can help you with weather forecasts, crop advice, market prices, and farming guidance. What would you like to know today?"
            
        response = agent_executor.invoke({
            "input": input_with_context
        })
        
        # 5. Translate the final answer if necessary
        final_response = language_service.translate_to(response['output'], language_code)
        
        return final_response
        
    except Exception as e:
        print(f"Error during agent execution: {e}")
        # Return a language-specific error message
        return language_service.get_template(language_code, "error")

# --- Example Usage ---
if __name__ == '__main__':
    krishi_agent = create_krishi_agent()
    
    # Test with a simple query
    current_query = "Hello, what can you help me with?"
    
    # Get the response
    final_answer = get_response(
        agent_executor=krishi_agent,
        user_input=current_query,
        language_code="en"
    )
    
    print(f"\nFinal Answer:\n{final_answer}")