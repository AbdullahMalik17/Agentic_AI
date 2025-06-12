import chainlit as cl
from run_level import gemini_api_key
from agents import Agent, Runner, AsyncOpenAI, set_default_openai_client, set_tracing_disabled, set_default_openai_api

set_tracing_disabled(True)
set_default_openai_api("chat_completions")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_default_openai_client(external_client)

agent: Agent = Agent(name="Assistant", instructions="You are a English Teacher . You also help the user in teaching English . You must teach latest words. ", model="gemini-2.0-flash")
@cl.on_chat_start
async def handle_message():
    await cl.Message(content="Assalam o Alaikum! I am your English teacher . I will teach you English.").send()

@cl.on_message
async def main(message:cl.Message):
    try:
        result = await Runner.run(
            agent,
            message.content
        )
        await cl.Message(content = result.final_output).send()
    except Exception as e:
        await  cl.Message(content=str(e)).send()
