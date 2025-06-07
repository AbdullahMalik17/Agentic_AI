import os
from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    set_default_openai_client,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

set_default_openai_client(external_client)
set_tracing_disabled(True)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client,
)


agent1 = Agent(
        name="Assistant",
        instructions="A helpful assistant that can answer questions and provide information.",
        model=model,
)
@cl.on_message
async def main(message:cl.Message):
    result = await Runner.run(
        agent1,
        message.content,
        run_config=None
    )
    await cl.Message(content=result.).send