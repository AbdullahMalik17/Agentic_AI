import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel , RunContextWrapper
from memory_tools import save_memory, get_memory
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

def dynamic_instruction(context: RunContextWrapper , agent: Agent):
    """The Dynamic instruction of the Agent"""
    return f"""You are a helpful assistant.
            You are given a task to help the user with their query.
            You are to use the memory tool to get the memory of the user."""
base_agent: Agent = Agent(
    name="Helpful_Agent",
    instructions=dynamic_instruction,
    model=llm_model,
    tools=[save_memory,get_memory]
)
result = Runner.run_sync(base_agent, "hi , I am  Abdullah and I am interested in AI .")
print(result)
result1 = Runner.run_sync(base_agent, "What is my name?")