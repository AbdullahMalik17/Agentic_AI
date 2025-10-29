import os 
from dotenv import load_dotenv,find_dotenv
from agents import Agent , Runner , OpenAIChatCompletionsModel , AsyncOpenAI , function_tool
from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
from langfuse import get_client
 
OpenAIAgentsInstrumentor().instrument()

_:bool = load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
 
 # Langfuse credentials
langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
langfuse_host = os.getenv("LANGFUSE_HOST")


langfuse = get_client()
 
# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")
# Client
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
# Model
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client = client
)

@function_tool
def get_weather(location:str):
    """To get the Weather information of a location."""
    return f"The weather in {location} is sunny with a high of 25°C."
agent : Agent= Agent(
    name="Assistant",
    instructions="You are a helpful assistant that can answer questions and help with tasks.",
    model=model,    
    tools=[get_weather],
)

result = Runner.run_sync(agent, "What is the weather in Karachi?")
print(result.final_output)
