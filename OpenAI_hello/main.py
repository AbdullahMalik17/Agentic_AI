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
    instructions="You are Hamna, a personal assistant. You can answer questions, provide information, and assist with various tasks. Always respond in a helpful and friendly manner.",
)
# It is used to show the display message in the chat 
@cl.on_chat_start
async def handle_message():
    cl.user_session.set("History",[])
    # Send a welcome message when the chat starts
    await cl.Message(content="Hello! I am Hamna , Your personal assistant. How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
  try :  
    history = cl.user_session.get("History",[])
    # save the user Message in the hstroy .
    history.append({"role":"user","content":message.content})
    result = await Runner.run(
        starting_agent = agent,
        input = message.content,
        run_config=run_config
    )
    # Save the result in the histroy .
    history.append({"role":"assistant","content":result.final_output})
    cl.user_session.set("History",history)
    await cl.Message(content=result.final_output).send()
  except Exception as e:
    cl.Message(content={str(e)}).send()

 #   await cl.Message(content=result.final_output).send()  # Send the result back to the user















































































































































































































































