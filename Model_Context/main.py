from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel , set_tracing_disabled , RunConfig
import os 
import asyncio
from dotenv import load_dotenv , find_dotenv
# load the environment variables
load_dotenv(find_dotenv())

set_tracing_disabled(True)

gemini_api_key = os.getenv("GEMINI_API_KEY")

# We create a gemini provider client 

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-pro",
    openai_client=external_client,
)

run_config = RunConfig(
    model = model ,
    model_provider = external_client,
    tracing_disabled=True,
)    

agent = Agent(
    name="Gemini Agent",
    instructions="You are a helpful assistant that can answer questions and help with tasks."
    )

async def main():
    result = await Runner.run(agent , "Why do we should learn AI especially Agentic AI ? ", run_config=run_config)
    print(result.final_output )


asyncio.run(main())    