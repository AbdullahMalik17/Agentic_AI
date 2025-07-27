import os 
import chainlit as cl  
from agents import Agent, Runner , AsyncOpenAI, set_tracing_disabled, OpenAIChatCompletionsModel
from dotenv import load_dotenv
load_dotenv()
gemini_api_key=os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
set_tracing_disabled(True)    
external_client  : AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)
agent = Agent(
    name="Doctor Assistant",
    instructions="A helpful doctor assistant that can answer questions and provide information about only medical.",
    model=model
)
@cl.on_message 
async def main(message: cl.Message):
    result = await Runner.run(
        agent,
        message.content,
        run_config=None
    )
    await cl.Message(content=result.final_output).send()
    print(message.content)
    print(result.final_output)
   