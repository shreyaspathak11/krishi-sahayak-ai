
# Import the tool functions from the organized tools package
from app import tools
from app.services.language_service import language_service

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Optional

from app.config import Config


# --- AGENT SETUP ---

def create_krishi_agent():
    """
    Creates and returns the main agent executor for Krishi Sahayak AI.
    """
    print("--- Initializing Krishi Sahayak AI Agent ---")
    
    # 1. Define the LLM (Language Model)
    # We use Groq's Llama 3.1 for its advanced reasoning and tool-calling capabilities.
    # Temperature=0 ensures deterministic, fact-based responses.
    llm = ChatGroq(
        model=Config.GROQ_LLM_MODEL,  # Llama 3 70B - excellent for reasoning and tool calling
        temperature=0,
        api_key=Config.GROQ_API_KEY  # Make sure to set this in your .env file
    )
    
    # 2. Define the available tools
    # These are the functions the AI can decide to call.
    available_tools = [
        tools.get_general_weather_forecast,
        tools.get_weather_forecast,
        tools.get_air_pollution_data,
        tools.get_uv_index,
        tools.get_crop_advisory,
        tools.get_market_prices,
        tools.get_soil_moisture_data,
        tools.get_current_datetime,
    ]
    
    # This is the instruction manual for the AI. It tells it how to behave.
    # Note: We don't have a `chat_history` variable yet, but we design the
    # prompt to be ready for it when we build the chat interface.
    prompt = ChatPromptTemplate.from_messages([
        ("system", Config.AGENT_SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # 4. Create the Tool-Calling Agent
    # This binds the LLM, the tools, and the prompt together.
    agent = create_tool_calling_agent(llm, available_tools, prompt)
    
    # 5. Create the Agent Executor
    # This is the runtime environment that actually executes the agent's decisions.
    # `verbose=True` is extremely helpful for debugging as it prints the AI's "thoughts".
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=available_tools, 
        verbose=True,
        handle_parsing_errors=True # Gracefully handle any unexpected outputs
    )
    
    print("--- Agent Initialized Successfully ---")
    return agent_executor


def get_response(agent_executor, user_query, language_code: str = "en", farmer_context: Dict = None):
    """
    Invokes the agent with a user query and returns the response.
    Includes multilingual support and fallback handling.
    
    Args:
        agent_executor: The initialized agent executor
        user_query: User's input query
        language_code: ISO 639-1 language code (en, hi, pa, bn, etc.)
        farmer_context: Optional farmer context for personalized responses
    """
    print(f"\n--- Invoking Agent with Query: '{user_query}' (Language: {language_code}) ---")
    
    # Auto-detect language if not specified or if detection is needed
    if language_code == "auto" or not language_service.is_language_supported(language_code):
        detected_language = language_service.detect_language(user_query)
        print(f"Detected language: {detected_language}")
        language_code = detected_language
    
    # Build language-specific system prompt
    language_prompt = language_service.build_system_prompt_with_language(
        language_code, farmer_context
    )
    
    # Combine the base system prompt with language-specific instructions
    enhanced_query = f"{language_prompt}\n\nUser Query: {user_query}"
    
    try:
        # The `invoke` method runs the full agentic chain:
        # 1. AI thinks which tool to use.
        # 2. AgentExecutor runs the chosen tool.
        # 3. The tool's output is fed back to the AI.
        # 4. The AI formulates a final answer in the specified language.
        response = agent_executor.invoke({
            "input": enhanced_query,
            "chat_history": [] # We'll add memory later
        })
        
        # Format the response with language-specific formatting
        formatted_response = language_service.format_response_with_language(
            response['output'], language_code
        )
        
        return formatted_response
        
    except Exception as e:
        print(f"Error during agent execution: {e}")
        # Return language-specific error message
        error_message = language_service.get_template(language_code, "error")
        return error_message


def get_response_streaming(agent_executor, user_query, language_code: str = "en", farmer_context: Dict = None):
    """
    Get streaming response from the agent (for future streaming implementation).
    For now, this is a placeholder that yields the complete response in chunks.
    """
    response = get_response(agent_executor, user_query, language_code, farmer_context)
    
    # Split response into words for streaming effect
    words = response.split()
    for word in words:
        yield word + " "
    
    # Mark completion
    yield ""


# --- Example Usage (for testing the agent directly) ---
if __name__ == '__main__':
    krishi_agent = create_krishi_agent()
    
    # Test Case 1: Simple weather query
    # query1 = "What is the weather forecast for the next few days?"
    # response1 = get_response(krishi_agent, query1)
    # print(f"\nFinal Answer:\n{response1}")
    
    # Test Case 2: Complex, multi-step agricultural query
    query2 = "My wheat crop is at the crown root initiation stage. The temperature is expected to drop to 4 degrees Celsius next week. Should I irrigate? What precautions should I take?"
    response2 = get_response(krishi_agent, query2)
    print(f"\nFinal Answer:\n{response2}")