import os
from dotenv import load_dotenv, find_dotenv
import time
from datetime import datetime
from mem0 import MemoryClient

from agents import (
    Agent,
    AsyncOpenAI,
    function_tool,
    ModelSettings,
    OpenAIChatCompletionsModel,
    RunContextWrapper,
)
from agents.tool_context import ToolContext
from tavily import AsyncTavilyClient

# this takes the data from prompt files
from system_prompt import (
    web_developer_prompt,
    mobile_developer_prompt,
    agentic_ai_developer_prompt,
    panacloud_prompt,
)

from dataclasses import dataclass
# --- Load Environment Variables ---
_:bool = load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

tavily_api_key= os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY is not set in the environment variables.")

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
mem0_api_key = os.getenv("MEM0_API_KEY","")
if not mem0_api_key:
    raise ValueError("The Mem0 API key is not set in the env file.")
# --- Model and Client Configuration ---
# Note: "gemini-2.5-flash" seems like a custom or placeholder name.
# Ensure it matches the actual model available at your endpoint.
# Common models are "gemini-1.5-flash", "gemini-1.5-pro", etc.
MODEL_NAME = "gemini-2.5-flash" 
TEMPERATURE = 1.8

# Configure the client to use the Gemini API via an OpenAI-compatible endpoint
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
common_model_settings = ModelSettings(temperature=TEMPERATURE, tool_choice="auto")
common_model = OpenAIChatCompletionsModel(
    openai_client=external_client, model=MODEL_NAME
)

# Initialize Tavily client for web search
tavily_client = AsyncTavilyClient(api_key=tavily_api_key)
# --- Tool Definitions ---
@function_tool
async def web_search(query: str) -> str:
    """Search the web using Tavily for latest Information. Returns a formatted string of the results."""
    if not tavily_client:
        return "Tavily client is not initialized."
    try:
        response = await tavily_client.search(query=query, search_depth="advanced")

        # Format results for better readability
        formatted_results = []
        for result in response.get('results', []):
            result_text = f"""#{result.get('title')}
            {result.get('content')}
            [Source]({result.get('url')})\n\n"""
            formatted_results.append(result_text)

        if not formatted_results:
            return "No results found from web search."
        return "\n".join(formatted_results)
    except Exception as e:
        return f"An error occurred during web search: {e}"

@dataclass
class Info:
    name : str
    description: str

@function_tool
def get_info(Wrapper:RunContextWrapper[Info])->str:
    """The name and description of user from the context."""
    return f"The name of user is {Wrapper.context.name} and the description is {Wrapper.context.description}."


mem0_api_key =os.getenv("MEM0_API_KEY")
mem_client = MemoryClient(api_key=mem0_api_key)

def sanitize_user_id(raw_user_id: str) -> str:
    """Sanitizes the user_id for mem0 by replacing problematic characters."""
    import re
    # Replace any character that is not a letter, number, underscore, or hyphen with an underscore.
    return re.sub(r'[^a-zA-Z0-9_-]', '_', raw_user_id)

@function_tool
async def search_user_memory(context: ToolContext[Info], query: str):
    """Use this tool to search user memories."""
    user_id = sanitize_user_id(context.context.name)
    response = mem_client.search(query=query, user_id=user_id, top_k=10)
    return response

@function_tool
async def save_user_memory(context:ToolContext[Info], query: str):
    """Use this tool to save user memories."""
    user_id = sanitize_user_id(context.context.name)
    response = mem_client.add([{"role": "user", "content": query}], user_id=user_id)
    return response

# ------ Here the Agents Definitions -------
web_developer = Agent(
    name="Web_Developer",
    instructions=web_developer_prompt,
    model=common_model,
    handoff_description="An expert in web development technologies like React,Next.js, Node.js, and Python.",
    tools=[web_search,save_user_memory,search_user_memory],
    model_settings=common_model_settings,
)

mobile_developer = Agent(
    name="Mobile_Developer",
    instructions=mobile_developer_prompt,
    model=common_model,
    handoff_description="An expert in mobile app development for iOS and Android.",
    tools=[web_search,save_user_memory,search_user_memory],
    model_settings=common_model_settings,
)

devops_agent = Agent(
    name="DevOps_Expert",
    instructions="You are a helpful assistant focused on DevOps. Provide clear, concise information about DevOps concepts, tools (like Docker, Kubernetes, CI/CD), and best practices. Generate code examples when necessary.\n\nBefore responding, always use the `search_user_memory` tool to check for relevant context from past conversations. After responding, use the `save_user_memory` tool to save key details that could be useful for future interactions.",
    model=common_model,
    tools=[web_search,save_user_memory,search_user_memory],
    model_settings=common_model_settings,
)

openai_agent = Agent(
    name="OpenAI_Expert",
    instructions="You are a helpful assistant with deep knowledge of OpenAI. Your sole purpose is to provide clear and concise answers about OpenAI's models, APIs, and platform. Do not discuss unrelated topics.\n\nBefore responding, always use the `search_user_memory` tool to check for relevant context from past conversations. After responding, use the `save_user_memory` tool to save key details that could be useful for future interactions.",
    model=common_model,
    tools=[web_search,save_user_memory,search_user_memory],
    model_settings=common_model_settings,
)

    # Convert agents to tools for hierarchical agent structures
devops_tool = devops_agent.as_tool(
    tool_name="DevOps_Tool",
    tool_description="Use this tool for any questions related to DevOps, CI/CD, Docker, or Kubernetes.",
)
openai_tool = openai_agent.as_tool(
    tool_name="OpenAISDk_Tool",
    tool_description="Use this tool for any questions about OpenAI SDk, its models (like GPT-4, GPT5), or its APIs.",
)

agentic_ai_developer = Agent(
    name="Agentic_AI_Developer",
    instructions=agentic_ai_developer_prompt,
    model=common_model,
    handoff_description="An expert in building Agentic AI systems and using advanced AI frameworks(openai sdk , Langchain/LanGraph , CrewAI).",
    tools=[devops_tool, openai_tool, web_search,save_user_memory,search_user_memory],
    model_settings=common_model_settings,
)
# Triage Agent: The entry point for all user queries
triage_agent = Agent(
    name="Bushra Code Assistant",
    instructions=panacloud_prompt,
    model=common_model,
    handoffs=[web_developer, mobile_developer, agentic_ai_developer],
    tools=[web_search, get_info,save_user_memory,search_user_memory],
    # 'required' forces the model to choose a handoff, which is good for a triage agent.
    model_settings=ModelSettings(temperature=TEMPERATURE, tool_choice="auto"),
)