import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, StopAtTools , function_tool 

_: bool = load_dotenv(find_dotenv())

# ONLY FOR TRACING
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

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
 
@function_tool
def get_data(client_id:str)-> str:
    """Get data for a specific client."""    
    return f"Data for client {client_id} retrieved successfully."

@function_tool
def del_data(client_id:str)-> str:
    """Delete data for a specific client."""    
    return f"Data for client {client_id} deleted successfully."

base_agent: Agent = Agent(
    name="Manager Agent",
    instructions="You are a helpful assistant.",
    model=llm_model,
    tools=[get_data, del_data], 
    tool_use_behavior=StopAtTools(stop_at_tool_names=["del_data"])
)

res = Runner.run_sync(base_agent, "Get the data from the client_123 and delete it?",context={"role":"user"})
print(res.final_output)