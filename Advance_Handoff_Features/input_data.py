import os
from tkinter.constants import ON
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool , handoff , RunContextWrapper, handoff 
from dataclasses import dataclass

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
@dataclass 
class Data :
    name: str
    age: int
    city: str
def dynamic_initiate(ctx:RunContextWrapper[Data] , ):
    return "The name of the person is " + ctx.context.name + " and the age is " + str(ctx.context.age) + " and the city is " + ctx.context.city

@function_tool
def get_weather(city: str) -> str:
    """A simple function to get the weather for a user."""
    return f"The weather for {city} is sunny."

news_agent : Agent = Agent(
    name = "News_Agent",
    instructions = "You are to give latest information about tech and Anything ",
    model = llm_model,
    tools = [get_weather],
    handoff_description = "News Expert Agent"
) 
agent  : Agent = Agent(
    name = "Assistant Agent",
    instructions="You are a helpful assistant. If the prompt is related to news, hand it off to the News Agent. Otherwise, answer the question directly.",
    model = llm_model,
    handoffs = [handoff(news_agent,
                        tool_name_override="get_news",
                        tool_description="Get the latest news about a topic",
                        on_handoff=dynamic_initiate,
                        input_type=Data)]
)

res = Runner.run_sync(agent,"What's the latest news about ChatGpt 5 ?")
print(res.final_output)
print(res.last_agent.name)