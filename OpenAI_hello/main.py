import os 
import chainlit as cl 
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
from dotenv import load_dotenv, find_dotenv 

# Load environment variables
load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GEMINI_API_KEY")  

# Step 1: Create a provider 
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Step 2: Create a model
model = OpenAIChatCompletionsModel(
    openai_client=provider,
    model="gemini-2.0-flash"
) 

# Step 3: Define config at run level
run_config = RunConfig(
    model=model,
    tracing_disabled=True  # Disable tracing
)

# Step 4: Create an agent
agent = Agent(
    name="Hamna",
    instructions="You are a sacharsit . Help people in teaching in short learning"
)

@cl.on_message
async def main(message: cl.Message):
    result = await Runner.run(
        starting_agent = agent,
        input = message.content,
        run_config=run_config
    )
    await cl.Message(content=result.final_output).send()
 #   await cl.Message(content=result.final_output).send()  # Send the result back to the user















































































































































































































































