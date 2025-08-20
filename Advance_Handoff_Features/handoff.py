import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool , handoff , RunContextWrapper

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
def dynamic_initiate(ctx:RunContextWrapper):
    return "[Logging] The News Agent is being called."
    print("\n [Logging] The News Agent is being called.\n ")
    
@function_tool
def get_weather(city: str) -> str:
    """A simple function to get the weather for a user."""
    return f"The weather for {city} is sunny."

news_agent : Agent = Agent(
    name = "News_Agent",
    instructions = "You are to give latest information about tech and Anything ",
    model = llm_model,
    tools = [get_weather],
    handoff_description="Expert News Agent",
) 

base_agent: Agent = Agent(
    name="Agent",
    instructions="You are a helpful assistant.Handoff to the News Agent for news-related queries.",
    model=llm_model,
    tools=[get_weather],
    handoffs = [handoff(agent = news_agent,tool_name_override="news_expert_agent",tool_description_override="Expert News Agent", on_handoff=dynamic_initiate)]
)

res = Runner.run_sync(base_agent, "What's the latest news about ChatGpt 5 ?")
print(res.final_output)
print(res.last_agent.name)

