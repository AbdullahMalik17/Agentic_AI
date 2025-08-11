from agents import (Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool)
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Accept either GEMINI_API_KEY or GOOGLE_API_KEY for Gemini's OpenAI-compat endpoint
gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not gemini_api_key:
    raise ValueError("Gemini API key is missing. Set GEMINI_API_KEY or GOOGLE_API_KEY in your environment or .env file.")

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is missing. Set it in your environment or .env file.")

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-pro",
    openai_client=client,
)

@function_tool
def add(a: int | float, b: int | float) -> int | float:
    """Returns the sum of two numbers."""
    return a + b

@function_tool
def subtract(a: int | float, b: int | float) -> int | float:
    """Returns the difference of two numbers."""
    return a - b

agent: Agent = Agent(
    name="Math Expert Agent",
    instructions="You are a math expert agent. You can solve any math problem and explain the solution step by step in an easy manner.",
    model=model,
    tools=[subtract],
)

agent2: Agent = agent.clone(
    name="Math Expert Agent 2",
    instructions="You only give a simple response to the math problem without any explanation.",
    model=OpenAIChatCompletionsModel(model="gemini-1.5-flash", openai_client=client),
    tools=[add],
)

result = Runner.run_sync(agent, "What is the differentiate of x^2 + 3x + 5 ?")
result2 = Runner.run_sync(agent2, "What is the differentiate of x^2 + 3x + 5 ?")
print("The Result of the first agent is :", result)
print("=" * 50)
print("The Result of the second agent is :", result2)