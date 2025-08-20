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
    topic : str
def dynamic_initiate(ctx:RunContextWrapper,input_data: Data):
    print("Tool is called with with input data:", input_data)
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
handoff_news_agent = handoff(
    agent=news_agent,
    tool_name_override="get_News_Agent",
    tool_description_override="Get the latest news from the News Agent. This agent specializes in news and current events.",
    on_handoff=dynamic_initiate,  
    input_type=Data,
) 
agent  : Agent = Agent(
    name = "Assistant Agent",
    instructions="You are a helpful assistant. If the prompt is related to news, hand it off to the News Agent. Otherwise, answer the question directly.",
    model = llm_model,
    handoffs = [handoff_news_agent]
)
res = Runner.run_sync(agent,"What's the latest news about ChatGpt 5? Handoff to the news agent, My name is Abdullah, My age is 17 and I live in Karachi ")
print(res.final_output)
print(res.last_agent.name)