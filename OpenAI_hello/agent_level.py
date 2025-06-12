import os 
import chainlit as cl
import asyncio
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from run_level import gemini_api_key


#Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

set_tracing_disabled(disabled=True)
agent = Agent(
        name="Assistant",
        instructions="You are a diet planner . You get the user data and suggest the healthy diet plan.  ",
        model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    )

@cl.on_chat_start
async def handle_message():
    await cl.Message(content = "Hello! I am your diet planner assistant. How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):    
    result = await Runner.run(
        agent,
        "message.content",
    )
    await cl.Message(content=result.final_output).send()