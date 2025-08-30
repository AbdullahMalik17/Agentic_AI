import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, RunContextWrapper, AgentHooks

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

# Here Agent Lie Cycle Hooks are defined 
class WeatherAgentHooks(AgentHooks):
    def __init__(self ,name_cycle:str):
        self.name_cycle = name_cycle
    async def on_start(self, context: RunContextWrapper, agent):
        print(f"[{self.name_cycle}] Agent is starting...")
    async def on_tool_start(self, context: RunContextWrapper, agent, tool):
        print(f"[{self.name_cycle}] Tool {tool.name} is starting...")    
    async def on_tool_end(self, context: RunContextWrapper, agent, tool, result):
        print(f"[{self.name_cycle}] Tool {tool.name} has finished.")
    async def on_end(self, context: RunContextWrapper, agent, result):    
        print(f"[{self.name_cycle}] Agent has finished.The Output is as :{result} ")
            
@function_tool
def get_weather(city: str) -> str:
    """A simple function to get the weather for a user."""
    return f"The weather for {city} is sunny."

weather_agent: Agent = Agent(
    name="WeatherAgent",
    instructions="You are a helpful assistant.",
    model=llm_model,
    tools=[get_weather],
    hooks=WeatherAgentHooks(name_cycle="WeatherCycle")
)

res = Runner.run_sync(weather_agent, "What's the weather in Karachi?")


# Now check the trace in 