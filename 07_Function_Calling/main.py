import os
import asyncio
from agents import set_default_openai_api
import chainlit as cl 
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
from dotenv import load_dotenv, find_dotenv 
from typing import cast
from agents.tool import function_tool

# Load environment variables
load_dotenv(find_dotenv())
set_default_openai_api("chat_completions")
gemini_api_key = os.getenv("GEMINI_API_KEY")  
if not gemini_api_key:
    raise ValueError("Gemini API key is not set . Please , ensure that it is defined in your env file.")
# Making a tool 
@function_tool("get_weather")
def get_weather(location: str) -> str:
  """
  Fetch the weather for a given location.
  """
  # Example logic
  return f"The weather in {location} is 22 degrees ."

@function_tool("get_data")
def get_data(roll_no:int) -> str:
    "Fetch the data for a given roll number." 
    data = {1: "Hamna", 2: "Ali", 3: "Sara"}
    return data.get(roll_no, "No data found for this roll number.")

# It is used to show the display message in the chat 
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
      model="gemini-2.0-flash"
    ) 
    # Step 3: Define config at run level
    run_config = RunConfig(
      model=model,
      tracing_disabled=True,  # Disable tracing
    )
    # Step 4: Create an agent
    agent = Agent(
      name="Hamna",
      instructions="You are Hamna, a personal assistant. You can answer questions, provide information, and assist with various tasks. Always respond in a helpful and friendly manner.",
      tools=[get_weather, get_data]
    )
    cl.user_session.set("history",[])
    cl.user_session.set("run_config", run_config)
    """Set up the chat session when a user connects."""
    cl.user_session.set("agent", agent)
    # Send a welcome message when the chat starts
    await cl.Message(content="Hello! I am Hamna, your personal assistant. How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages and generate responses."""  
    history = cl.user_session.get("history",[])
    # save the user Message in the hstroy .
    # Append the user's message to the history.
    history.append({"role": "user", "content": message.content})  
    msg = cl.Message(content="")
    await msg.send()  
    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("run_config"))
    
    try:
        print("\n[CALLING_AGENT_WITH_CONTEXT]\n", history, "\n")
        # Run the agent with streaming enabled
        result = Runner.run_streamed(agent, history, run_config=config)

        # Stream the response token by token
        async for event in result.stream_events():
            if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
                token = event.data.delta
                await msg.stream_token(token)

        # Append the assistant's response to the history.
        history.append({"role": "assistant", "content": msg.content})

        # Update the session with the new history.
        cl.user_session.set("chat_history", history)

        # Optional: Log the interaction
        print(f"User: {message.content}")
        print(f"Assistant: {msg.content}")
  
    except Exception as e:
        await cl.Message(content={str(e)}).send()
        print(f"Error:{str(e)}")