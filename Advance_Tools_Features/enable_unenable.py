import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel , function_tool , RunContextWrapper ,AgentBase
from dataclasses import dataclass
from tavily import TavilyClient
_: bool = load_dotenv(find_dotenv())

# ONLY FOR TRACING
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")

# 1. Which LLM Service?
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 2. Which LLM Model?
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)
@dataclass
class Data:
    user_type: str  
    
def check_user_type(ctx: RunContextWrapper[Data], agent: AgentBase) -> bool:
    """Check if the user type is 'special'."""
    data: Data = ctx.context
    return data.user_type == "Special" 
   
@function_tool(name_override="Search_from_web",is_enabled=check_user_type)
def web_search(query: str) -> str:
    """A simple function to perform a web search."""
    tavily_client = TavilyClient(api_key=tavily_api_key)
    response = tavily_client.search(query)
    return response

data = Data(user_type="free")

base_agent: Agent = Agent(
    name="Agent",
    instructions="You are a helpful assistant.",
    model=llm_model,
    tools=[web_search]
)

res = Runner.run_sync(base_agent, "What is the release date of ChatGPT 5?",context=data)
print(res.final_output)