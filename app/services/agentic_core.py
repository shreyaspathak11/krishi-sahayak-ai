from typing import Dict, List
import json

from langchain_groq import ChatGroq
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

from app.config import Config
from app.services.language_service import language_service
from app.services.context_service import context_service
import app.tools as tools
from app.utils.logs import logger

# --- AGENT SETUP ---

def create_krishi_agent():
    """
    Creates and returns the main agent executor for Krishi Sahayak.
    """
    print("--- Initializing Krishi Sahayak Agent ---")
    
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
    
    # 2. Use JSON prompting system prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", Config.AGENT_SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, available_tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=available_tools, 
        verbose=False,  
        max_iterations=3,
        max_execution_time=30,
        early_stopping_method="generate",
    )
    return agent_executor

def get_response(
    agent_executor: AgentExecutor, 
    user_input: str, 
    language_code: str = "en",
    chat_history: List[Dict[str, str]] = None
) -> str:
    """
    Invokes the agent with the user's query.
    
    Args:
        agent_executor: The initialized agent executor.
        user_input: The user's current message.
        language_code: The language code for the response.
        chat_history: The conversation history from frontend (optional).
        
    Returns:
        The AI's response as a string.
    """

    # Initialize defaults
    if chat_history is None:
        chat_history = []

    # 1. Determine the language for the response
    if not language_code:
        language_code = language_service.detect_language(user_input)
    
    # 2. Process context internally
    context_summary = ""
    if chat_history:
        context_summary = context_service.get_context_for_ai(chat_history)
    
    try:
        # 3. Invoke the agent with context if available
        if context_summary:
            input_with_context = f"Context from previous conversation: {context_summary}\n\nUser question: {user_input}"
        else:
            input_with_context = user_input
            
        
        # 4. Get response from agent
        response = agent_executor.invoke({
            "input": input_with_context
        })
        
        raw_response = response.get('output', '')
        
        # 5. Extract content from JSON response, handle malformed JSON gracefully
        try:
            json_data = json.loads(raw_response.strip())
            content = json_data.get('content', raw_response)
        except json.JSONDecodeError:
            content = raw_response
        
        # Translate if necessary
        final_response = language_service.translate_to(content, language_code)
        return final_response
        
    except Exception as e:
        logger.error(f"Error in agent execution: {str(e)}")
        return language_service.translate_to("Network error", language_code)
