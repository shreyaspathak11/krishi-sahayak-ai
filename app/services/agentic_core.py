from typing import Dict, List
import json
import re

from langchain_groq import ChatGroq
from langchain.agents import create_react_agent, AgentExecutor
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.prompts import PromptTemplate

from app.config import Config
from app.services.language_service import language_service
from app.services.context_service import context_service
import app.tools as tools
from app.utils.logs import logger

# --- HELPER FUNCTIONS ---

def extract_location_from_parameter(location_param: str) -> str:
    """
    Extracts clean location value from tool parameter.
    Removes context text like 'location = "Hisar"' and returns just 'Hisar'
    """
    if not location_param:
        return None
    
    # Remove 'location = ' prefix if present
    if 'location' in location_param.lower() and '=' in location_param:
        # Extract the quoted or unquoted value after '='
        match = re.search(r'=\s*["\']?([^"\'\n]+)["\']?', location_param)
        if match:
            location_param = match.group(1).strip()
    
    # Remove any trailing context text (e.g., " (default location...")
    location_param = re.sub(r'\s*\([^)]*\).*$', '', location_param)
    location_param = location_param.strip('\'"')
    
    return location_param if location_param else None
    
    return location_param if location_param else None

# --- CALLBACK HANDLER FOR TRACKING TOOL CALLS ---

class ToolCallbackHandler(BaseCallbackHandler):
    """Tracks tool calls for frontend display."""
    
    def __init__(self):
        self.tool_calls: List[Dict] = []
        self.current_tool = None
    
    def on_tool_start(self, serialized: Dict, input_str: str, **kwargs):
        """Called when a tool is about to be invoked."""
        self.current_tool = {
            "name": serialized.get("name", "unknown"),
            "description": serialized.get("description", ""),
            "input": input_str,
            "status": "pending"
        }
    
    def on_tool_end(self, output: str, **kwargs):
        """Called when a tool finishes execution."""
        if self.current_tool:
            self.current_tool["output"] = output
            self.current_tool["status"] = "success"
            self.tool_calls.append(self.current_tool)
            self.current_tool = None
    
    def on_tool_error(self, error: Exception, **kwargs):
        """Called when a tool raises an error."""
        if self.current_tool:
            self.current_tool["output"] = str(error)
            self.current_tool["status"] = "error"
            self.tool_calls.append(self.current_tool)
            self.current_tool = None

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

CRITICAL INSTRUCTIONS FOR TOOL PARAMETERS:
- When calling get_weather_forecast: Extract ONLY the location name or coordinates from context
  - Examples of CORRECT tool input: "Hisar", "Ludhiana", "23.49,87.33"
  - WRONG format: "location = Hisar" or "\"23.49,87.33\"" (quoted coordinates)
  - If user mentions a location in their question, extract just that city name
  - If NO location is mentioned, use "Hisar" as default for North India

- For all tools: Provide ONLY the actual parameter values, NOT variable assignments
- Extract location from user context if available
- NEVER include "location = " or other context text in tool parameters
- NEVER include extra quotes around coordinates like "\"23.49,87.33\""

CRITICAL DECISION RULES:
- ONLY use tools when you need specific, real-time data (weather, market prices, news, etc.)
- For general farming questions that don't require real-time data, answer directly without tools
- Answer once you have the data - don't loop or repeat tool calls
- Stop and provide final answer when you have enough information

Available tools:
{tools}

Format:
Question: the input question to answer
Thought: briefly think about which tool to use and what location/parameters
Action: the tool name from {tool_names}
Action Input: ONLY the actual parameter value (e.g., "Hisar" not "location = Hisar" or "\"Hisar\"")
Observation: the result
Thought: Do I need more information or can I answer now?
Final Answer: clear, practical answer to help the farmer

Begin!

Question: {input}
Thought: {agent_scratchpad}""")
    
    # Create ReAct agent
    agent = create_react_agent(
        llm=llm,
        tools=available_tools,
        prompt=prompt,
    )
    
    # Create executor with callback handler
    agent_executor = AgentExecutor(
        agent=agent,
        tools=available_tools,
        verbose=False,
        max_iterations=5,
        max_execution_time=60,
        handle_parsing_errors=True,
    )
    
    print("[OK] AI agent initialized successfully with ReAct tool calling")
    return agent_executor

def get_response(
    agent_executor, 
    user_input: str, 
    language_code: str = "en",
    chat_history: List[Dict[str, str]] = None,
    location: str = None
) -> tuple:
    """
    Invokes the agent with the user's query and returns both response and tool info.
    
    Args:
        agent_executor: The initialized agent executor.
        user_input: The user's current message.
        language_code: The language code for the response.
        chat_history: The conversation history from frontend (optional).
        
    Returns:
        Tuple of (response_text, tool_calls_list)
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
        # Prepare input with context and location if available
        if context_summary:
            final_input = f"Context: {context_summary}\n\nQuestion: {user_input}"
        else:
            final_input = user_input
        
        # Add location information if provided
        if location:
            final_input = f"User Location: {location}\n\n{final_input}"
        
        # Create callback handler to track tool calls
        callback_handler = ToolCallbackHandler()
        
        # Invoke agent with callback handler - it will handle tool calling automatically
        response = agent_executor.invoke(
            {"input": final_input},
            callbacks=[callback_handler]
        )
        
        # Extract response - AgentExecutor returns dict with 'output' key
        output = response.get('output', 'Unable to process request')
        
        # Translate if necessary
        final_response = language_service.translate_to(output, language_code)
        
        # Return both response and tool calls for frontend
        return final_response, callback_handler.tool_calls
        
    except Exception as e:
        logger.error(f"Error in agent execution: {str(e)}")
        error_msg = language_service.translate_to("I encountered an error processing your request. Please try again.", language_code)
        return error_msg, []
