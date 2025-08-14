
import os
import chainlit as cl 
from agents import(
    Agent,
    Runner,
    AsyncOpenAI ,
    OpenAIChatCompletionsModel ,
    function_tool ,
    ModelSettings ,
    RunContextWrapper,
)
from dotenv import load_dotenv, find_dotenv 
from research_agents import web_search , lead_agent , requirement_gathering_agent , planing_agent 

from dataclasses import dataclass 
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

# It is used to show the display message in the chat 
@dataclass
class Info:
    name : str
    father_name : str
    mother_name : str
    sister_name : str

# Step 1: Create a provider 
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
# Step 2: Create a model
model = OpenAIChatCompletionsModel(
    openai_client=provider,
    model="gemini-2.5-pro"
) 
# Step 3: Define config at run level

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
    # print(f"\n[CALLING_BASIC_DYNAMIC]\nContext: {Wrapper}\nAgent: {agent}\n")
    return f"""You are {agent.name}.You should do deep to the User prompt 
1. You should handoff requirement_gather_agent to gather the requirements from the user .
2. Then , handoff to the planing_agent to plan the solution based on the requirements.
3. Then , handoff to the lead_agent to lead the project and provide the final solution."""

# here I create Agent . 
agent = Agent(
    name="DeepSearch Agent",
    instructions=basic_dynamic, 
    model=model,
    # instructions="You are DeepSearch Agent . You can answer questions, provide information and give Example(Code) if necessary . For latest information, you can search through websearch tool. Always respond in a helpful and friendly manner",
    handoffs=[requirement_gathering_agent,planing_agent,lead_agent],  # <- removed trailing comma
    model_settings=ModelSettings(temperature=1.9,tool_choice="required"),
    #   tool_use_behavior="stop_on_first_tool"
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
        # print("\n[CALLING_AGENT_WITH_CONTEXT]\n", history, "\n")
        #give the data of the user to the agent 
        user_Info1 = Info(name="Abdullah", father_name="Athar", mother_name="Bushra",sister_name="Amna")
        # Run the agent with streaming enabled
        # Create a RunContextWrapper with the current history
        result = Runner.run_streamed(
            starting_agent=agent,
            input=history,
            context=user_Info1,
        )

        # Stream the response token by token and surface tool outputs
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

        # Finalize the streamed message and persist history
        await msg.update()
        history.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("history", history)

        # Optional: Log the interaction
        print(f"User: {message.content}")
        print(f"Assistant: {msg.content}")
  
    except Exception as e:
        await cl.Message(content=str(e)).send()
        print(f"Error:{str(e)}")

