
import os
import chainlit as cl 
from agents import(
    Agent,
    Runner,
    AsyncOpenAI ,
    OpenAIChatCompletionsModel ,
    ModelSettings ,
    RunConfig,
    RunContextWrapper,
)
from dotenv import load_dotenv, find_dotenv 
from research_agents import  lead_agent , requirement_gathering_agent , planning_agent 
from tools import Info 
# Load environment variables
load_dotenv(find_dotenv())
# Force Agents SDK to use Chat Completions API to avoid Responses API event types

# It is an API_key of Gemini 
gemini_api_key = os.environ.get("GEMINI_API_KEY") 
if not gemini_api_key:
    raise ValueError("Gemini API key is not set . Please , ensure that it is defined in your env file.")

# Here The api key of OpenAI 
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key is not set. Please ensure OPENAI_API_KEY is defined in your .env file.")

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

def deep_research_instructions(Wrapper: RunContextWrapper, agent: Agent) -> str:
    return f"""You are {agent.name}, an advanced AI research coordinator.
Your task is to receive the user's research query and  hand it off to the 'Requirement Gathering Agent' to begin the research process. If the Query is simple , you can directly hand it off to the 'Lead Agent' for immediate action.
Do not analyze the query, answer the user, or perform any other actions. Your sole function is to initiate the multi-agent workflow."""

# Create the main DeepSearch Agent with improved configuration
agent : Agent = Agent(
    name="DeepSearch Agent",
    instructions=deep_research_instructions,
    model=model,  
    # The coordinator's only job is to kick off the workflow by handing off to the first agent.
    # The subsequent handoffs are defined within each agent, creating a chain.
    handoffs=[requirement_gathering_agent],
    model_settings=ModelSettings(
        temperature=0.7,  # Lower temperature for more focused coordination
        tool_choice="auto",
        )
)
@cl.on_chat_start
async def handle_message():
    cl.user_session.set("history",[])  # Store the history in the user session
    """Handle the chat start event."""
    # Send a welcome message when the chat starts
    await cl.Message(content="Hello! I am DeepSearch Agent , your personal assistant. How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages and generate responses.""" 

    history = cl.user_session.get("history",[])
    # save the user Message in the histroy .
    # Append the user's message to the history.
    history.append({"role": "user", "content": message.content})  
    msg = cl.Message(content="")
    await msg.send()  
    
    try:

        #give the data of the user to the agent 
        user_Info1 = Info(name="Abdullah", father_name="Athar", mother_name="Bushra",sister_name="Amna")
        # Create a RunConfig to pass the session name for tracing
        run_config = RunConfig(workflow_name="Deep Research Session")

        # Run the agent with streaming enabled
        # Create a RunContextWrapper with the current history
        result = Runner.run_sync(
            starting_agent=agent,
            input=history,  # Use the current message instead of full history
            context=user_Info1,
            run_config=run_config  # Pass the config object
        )
        await cl.Message(content=result.final_output).send()  # Send the final output as a message
        # # Stream the response token by token and surface tool outputs
        # async for event in result.stream_events():
        #     if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
        #         token = event.data.delta
        #         await msg.stream_token(token)
        #     elif event.type == "run_item_stream_event":
        #         item = getattr(event, "item", None)
        #         if item and getattr(item, "type", "") == "tool_call_output_item":
        #             output_text = str(getattr(item, "output", ""))
        #             if output_text:
        #                 await msg.stream_token(output_text)

        # Finalize the streamed message and persist history
        # await msg.update()
        history.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("history", history)

  
    except Exception as e:
        await cl.Message(content=f"Error:{str(e)}").send()
        print(f"Error:{str(e)}")
