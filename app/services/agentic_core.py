from typing import Dict, List
import json

from langchain_groq import ChatGroq
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

from app.config import Config
from app.services.language_service import language_service
from app.services.context_service import context_service
import app.tools as tools
from app.utils.logs import logger

# --- AGENT SETUP ---

def create_krishi_agent():
    """
    Creates and returns the main agent executor for Krishi Sahayak.
    Uses create_react_agent which handles multi-input tools properly.
    """
    print("--- Initializing Krishi Sahayak Agent ---")
    
    llm = ChatGroq(
        model=Config.GROQ_LLM_MODEL,
        temperature=0,
        api_key=Config.GROQ_API_KEY,
        max_retries=2,
        request_timeout=30
    )
    
    # Available tools
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
    
    # Create ReAct prompt
    prompt = PromptTemplate.from_template("""You are Krishi Sahayak, an agricultural assistant for Indian farmers.
Help farmers with weather forecasts, market prices, soil advice, crop guidance, and agricultural news.

When a farmer asks about weather, prices, soil, crops, or news:
- MUST use the appropriate tool to get accurate information
- Never guess or make up data
- Respond in the farmer's language
- Be helpful, clear, and practical

You have access to these tools:
{tools}

Use this format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}""")
    
    # Create ReAct agent
    agent = create_react_agent(
        llm=llm,
        tools=available_tools,
        prompt=prompt,
    )
    
    # Create executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=available_tools,
        verbose=False,
        max_iterations=5,
        max_execution_time=60,
        early_stopping_method="generate",
        handle_parsing_errors=True,
    )
    
    print("✓ AI agent initialized successfully with ReAct tool calling")
    return agent_executor

def get_response(
    agent_executor, 
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

    # Determine the language for the response
    if not language_code:
        language_code = language_service.detect_language(user_input)
    
    # Process context if available
    context_summary = ""
    if chat_history:
        context_summary = context_service.get_context_for_ai(chat_history)
    
    try:
        # Prepare input with context if available
        if context_summary:
            final_input = f"Context: {context_summary}\n\nQuestion: {user_input}"
        else:
            final_input = user_input
        
        # Invoke agent - use invoke() instead of run()
        response = agent_executor.invoke({"input": final_input})
        
        # Extract response - AgentExecutor returns dict with 'output' key
        output = response.get('output', 'Unable to process request')
        
        # Translate if necessary
        final_response = language_service.translate_to(output, language_code)
        return final_response
        
    except Exception as e:
        logger.error(f"Error in agent execution: {str(e)}")
        return language_service.translate_to("I encountered an error processing your request. Please try again.", language_code)
