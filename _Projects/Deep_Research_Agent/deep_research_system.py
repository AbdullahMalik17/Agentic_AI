import os
import chainlit as cl 
from agents import(
    Agent,
    MaxTurnsExceeded,
    Runner,
    AsyncOpenAI ,
    OpenAIChatCompletionsModel ,
    ModelSettings ,
    RunConfig,
    RunContextWrapper,
    RunHooks , 
    SQLiteSession
)
from dotenv import load_dotenv, find_dotenv 
from research_agents import  requirement_gathering_agent , lead_agent
from tools import Info ,save_user_memory, search_user_memory
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
# Step 3:  Create a RunConfig to pass the session name for tracing
run_config = RunConfig(workflow_name="Deep Research Session")

def deep_research_instructions(Wrapper: RunContextWrapper, agent: Agent) -> str:
    return f"""You are {agent.name}, an advanced AI research coordinator.
Your primary task is to manage the research workflow.

1. Your task is to receive the user's research query and  hand it off to the 'Requirement Gathering Agent' to begin the research process. If the Query is simple , you can directly hand it off to the 'Lead Agent' for immediate action.
2. Do not analyze the query, answer the user, or perform any other actions. Your sole function is to initiate the multi-agent workflow.
3. [Note: You are allowed to use get and save memories tools for better performance]"""

# Create the main DeepSearch Agent with improved configuration
agent : Agent = Agent(
    name="DeepSearch Agent",
    instructions=deep_research_instructions,
    model=model,
    tools=[search_user_memory, save_user_memory],
    handoffs=[requirement_gathering_agent,lead_agent],
    model_settings=ModelSettings(
        temperature=0.7,  # Lower temperature for more focused coordination
        )
)

class DeepResearchHooks(RunHooks):
    def __init__(self):
        self.active_agents = []
        self.handoffs = 0
        self.tool_usage = {}
    
    async def on_agent_start(self, context : RunContextWrapper, agent:Agent):
        self.active_agents.append(agent.name)
        print(f"🌅 SYSTEM: {agent.name} is now working")
        print(f"   Active agents so far: {self.active_agents}")
    
    async def on_llm_start(self,context:RunContextWrapper, agent:Agent, system_prompt, input_items):
        print(f"📞 SYSTEM: {agent.name} is thinking with all his capabilities ...")
    
    async def on_llm_end(self, context:RunContextWrapper, agent:Agent, response):
        print(f"🧠✨ SYSTEM: {agent.name} finished thinking")
    
    async def on_tool_start(self, context:RunContextWrapper, agent:Agent, tool):
        tool_name = tool.name
        if tool_name not in self.tool_usage:
            self.tool_usage[tool_name] = 0
        self.tool_usage[tool_name] += 1
        print(f"🔨 SYSTEM: {tool_name} used {self.tool_usage[tool_name]} times")
    
    async def on_tool_end(self, context:RunContextWrapper, agent:Agent, tool, result):
        print(f"✅🔨 SYSTEM: {agent.name} finished using {tool.name}")
    
    async def on_handoff(self, context:RunContextWrapper, from_agent, to_agent):
        self.handoffs += 1
        print(f"🏃‍♂️➡️🏃‍♀️ HANDOFF #{self.handoffs}: {from_agent.name} → {to_agent.name}")
    
    async def on_agent_end(self, context:RunContextWrapper, agent:Agent, output):
        print(f"✅ SYSTEM: {agent.name} completed their work")
        print(f"📊 STATS: {len(self.active_agents)} agents used, {self.handoffs} handoffs")
    
@cl.on_chat_start
async def handle_message():
    """Handle the chat start event."""
    # Create a new session for each chat, identified by the user's session ID.
    # This ensures that conversation history is isolated between chats.
    session = SQLiteSession("abdullah","Database.bd")
    cl.user_session.set("session", session)

    # Send a welcome message when the chat starts
    await cl.Message(content="Hello! I am DeepSearch Agent , your personal assistant. How can I help you today?").send()


@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages and generate responses."""
    # Retrieve the session for the current user chat
    session = cl.user_session.get("session")

    delete_commands = [
        "remove session",
        "delete session",
        "remove session history",
        "delete session history",
    ]
    if message.content.lower().strip() in delete_commands:
        """It removes the session history for the current chat when the User asks."""
        if session:
            await session.clear_session()
            print(f"Session History Removed for session_id: {session.session_id}")
        await cl.Message(content="Your session history has been cleared.").send()
        return

    msg = cl.Message(content="Thinking...")
    await msg.send()

    try:
        # give the data of the user to the agent
        user_Info1 = Info(name="abdullah", interests=["AI", "Web development", "Agentic AI"])

        result = Runner.run_sync(
            starting_agent=agent,
            input=message.content,  
            context=user_Info1,
            run_config=run_config,
            max_turns=50,  
            hooks=DeepResearchHooks(),
            session=session,
        )
        
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

        await cl.Message(content=result.final_output).send()


    except MaxTurnsExceeded as e:
        await cl.Message(content="Max Turns Exceeded. Please ask your Question again.").send()
  
    except Exception as e:
        await cl.Message(content=f"Error:{str(e)}").send()
        print(f"Error:{str(e)}")
