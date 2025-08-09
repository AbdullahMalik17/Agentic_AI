import os
import asyncio
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, function_tool, ModelSettings, RunContextWrapper, set_default_openai_api
from dotenv import load_dotenv, find_dotenv
from typing import cast
from tavily import AsyncTavilyClient
from dataclasses import dataclass

# Load environment variables
load_dotenv(find_dotenv())
# Force Agents SDK to use Chat Completions API to avoid Responses API event types
set_default_openai_api("chat_completions")

# API Keys
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("Gemini API key is not set. Please ensure it is defined in your .env file.")
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("Tavily API key is not set. Please ensure TAVILY_API_KEY is defined in your .env file.")

# Tavily Client
tavily_client = AsyncTavilyClient(api_key=tavily_api_key)

# Data Class for User Information
@dataclass
class Info:
    name: str
    father_name: str
    mother_name: str
    sister_name: str

@cl.on_chat_start
async def handle_message():
    # Step 1: Create a provider
    provider = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    # Step 2: Create a model
    model = OpenAIChatCompletionsModel(
        openai_client=provider,
        model="gemini-2.5-flash"
    )
    # Step 3: Define config at run level
    run_config = RunConfig(
        model=model,
        tracing_disabled=True,  # Disable tracing
    )

    @function_tool
    async def web_search(query: str) -> str:
        """Search the web using Tavily."""
        try:
            response = await tavily_client.search(query=query)
            formatted_results = []

            for result in response['results']:
                result_text = f"""
### {result['title']}
{result['content']}
##### [Source]({result['url']})
---
"""
                formatted_results.append(result_text)

            all_results = "\n".join(formatted_results)
            return all_results

        except Exception as e:
            return f"An error occurred during the web search: {str(e)}"

    @function_tool
    async def get_info(Wrapper: RunContextWrapper[Info]) -> str:
        """Return the user's profile information from the run context."""
        return (
            f"The name of user is {Wrapper.context.name}, "
            f"his father name is {Wrapper.context.father_name}, "
            f"his mother name is {Wrapper.context.mother_name},"
            f"and his sister name is {Wrapper.context.sister_name}."
        )

    def basic_dynamic(Wrapper: RunContextWrapper, agent: Agent) -> str:
        """Dynamic instructions for the agent."""
        return f"""You are {agent.name}. You should deeply analyze the User's prompt and provide the latest knowledge by using the web search tool. 
        You also have access to the user's information. Always respond in a helpful and friendly manner."""

    agent = Agent(
        name="DeepSearch Agent",
        instructions=basic_dynamic,
        tools=[web_search, get_info],
        model_settings=ModelSettings(temperature=0.7, max_tokens=2000, tool_choice="auto"), # Reduced temperature
    )
    cl.user_session.set("history", [])
    cl.user_session.set("run_config", run_config)
    cl.user_session.set("agent", agent)
    await cl.Message(content="Hello! I am DeepSearch Agent, your personal assistant. How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages and generate responses."""

    history = cl.user_session.get("history", [])
    history.append({"role": "user", "content": message.content})
    msg = cl.Message(content="")
    await msg.send()
    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("run_config"))

    try:
        user_Info1 = Info(name="Abdullah", father_name="Athar", mother_name="Bushra", sister_name="Amna")

        result = Runner.run_streamed(
            starting_agent=agent,
            input=message.content,
            run_config=config,
            context=user_Info1,
        )

        async for event in result.stream_events():
            if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
                token = event.data.delta
                await msg.stream_token(token)
            elif event.type == "run_item_stream_event":
                item = getattr(event, "item", None)
                if item and getattr(item, "type", "") == "tool_call_output_item":
                    output_text = str(getattr(item, "output", ""))
                    if output_text:
                        await msg.stream_token(output_text)

        await msg.update()
        history.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("history", history)

        print(f"User: {message.content}")
        print(f"Assistant: {msg.content}")

    except Exception as e:
        await cl.Message(content=f"An error occurred: {str(e)}").send()
        print(f"Error: {str(e)}")