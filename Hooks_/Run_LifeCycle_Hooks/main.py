from agents import Agent , Runner , OpenAIChatCompletionsModel , AsyncOpenAI , function_tool , RunHooks , RunContextWrapper
import os
from dotenv import load_dotenv , find_dotenv


_: bool = load_dotenv(find_dotenv())
gemini_api_key : str = os.getenv("GEMINI_API_KEY" , "")
openai_api_key : str = os.getenv("OPENAI_API_KEY" , "")

# here the provider of it .
external_client : AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)
@function_tool
def get_weather(city : str) -> str:
    """A simple function to get the weather"""
    return f"The weather for {city} is sunny."

class MyAgentHooks(RunHooks):
    async def on_agent_start(self, context: RunContextWrapper, agent: Agent):
        print(f"[MyAgentHooks] Agent {agent.name} is starting...")
    async def on_llm_start(self, context: RunContextWrapper, agent:Agent, system_prompt, input_items):
        print(f"[MyAgentHooks] LLM is starting with system prompt: {system_prompt} and input items: {input_items}")
    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool):
        print(f"[MyAgentHooks] Tool {tool.name} is starting...")
    async def on_tool_end(self, context: RunContextWrapper, agent: Agent, tool, result):
        print(f"[MyAgentHooks] Tool {tool.name} has finished with result: {result}")
    async def on_llm_end(self, context: RunContextWrapper, agent: Agent, response):
        print(f"[MyAgentHooks] LLM has finished with response: {response}")
    async def on_agent_end(self, context: RunContextWrapper, agent: Agent, output):
        print(f"[MyAgentHooks] Agent {agent.name} has finished with output: {output}")
    
weather_agent : Agent = Agent(
    name = "WeatherAgent",
    instructions="You are a helpful assistant.You are only responsible to tell the weather of the given city .",
    model = model,
    tools = [get_weather]
)
            
base_agent : Agent = Agent(
    name = "NewsAgent",
    instructions="You are a helpful assistant.You are only responsible to tell the weather of the given city by handoff. You should provide the latest information about it ",
    model = model,
    handoffs = [weather_agent],
)
    
res = Runner.run_sync(base_agent , "What's the weather in Karachi?",hooks=MyAgentHooks())
print(res.final_output)
print(res.last_agent.name)