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
from research_agents import  lead_agent , requirement_gathering_agent , planning_agent 
from tools import Info , get_memories , save_memories
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

# Step 4: Create a session memory by using SQLiteSession
session = SQLiteSession("User_Abdullah","Database.bd")
def deep_research_instructions(Wrapper: RunContextWrapper, agent: Agent) -> str:
    return f"""You are {agent.name}, an advanced AI research coordinator.
Your task is to receive the user's research query and  hand it off to the 'Requirement Gathering Agent' to begin the research process. If the Query is simple , you can directly hand it off to the 'Lead Agent' for immediate action.
Do not analyze the query, answer the user, or perform any other actions. Your sole function is to initiate the multi-agent workflow.
[Note: You are allowed to use get and save memories tools for better performance]"""

# Create the main DeepSearch Agent with improved configuration
agent : Agent = Agent(
    name="DeepSearch Agent",
    instructions=deep_research_instructions,
    model=model,
    tools=[get_memories, save_memories],
    handoffs=[requirement_gathering_agent],
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
    # Send a welcome message when the chat starts
    await cl.Message(content="Hello! I am DeepSearch Agent , your personal assistant. How can I help you today?").send()


@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages and generate responses.""" 
 
    msg = cl.Message(content="")
    await msg.send()  
    
    try:

        #give the data of the user to the agent 
        user_Info1 = Info(name="Abdullah", father_name="Athar", mother_name="Bushra",sister_name="Amna")
   
        result = Runner.run_sync(
            starting_agent=agent,
            input=message.content,  
            context=user_Info1,
            run_config=run_config,
            max_turns=50,  
            hooks=DeepResearchHooks(),
            # session = session
        )
        await cl.Message(content=result.final_output).send()      # Send the final output as a message
        
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

    except MaxTurnsExceeded as e:
        await cl.Message(content=f"Max Turns Exceed . Pls ask again your Question .")
  
    except Exception as e:
        await cl.Message(content=f"Error:{str(e)}").send()
        print(f"Error:{str(e)}")
