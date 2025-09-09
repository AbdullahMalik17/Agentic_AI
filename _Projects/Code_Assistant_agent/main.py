# This file is part of the Coder AI Assistant project.
import chainlit as cl
from chainlit import on_message, on_chat_start
from agent_definations import triage_agent , Info 

from agents import Agent,Runner , MaxTurnsExceeded , RunConfig , SQLiteSession , RunHooks , RunContextWrapper,InputGuardrailTripwireTriggered

# Session for memory Management .
session = SQLiteSession("Umer","Code_Assistant.db")
class RunHookCycle(RunHooks):
    def __init__(self):
        self.active_agents = []
        self.handoffs = 0
        self.tool_usage = {}
        
    async def on_agent_start(self, context: RunContextWrapper, agent: Agent):
        self.active_agents.append(agent.name)
        print(self.active_agents)
        print(f"{agent.name} is started working...")
        
    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool):
        print(f"{tool.name} is started working by an agent {agent.name}...")
        self.tool_usage=+1
    async def on_tool_end(self, context: RunContextWrapper, agent: Agent, tool, result: str):
        print(f"{tool.name} has finished working...")
     
    async def on_handoff(self, context: RunContextWrapper, from_agent:Agent, to_agent:Agent):
        self.handoffs=+1
        print(f"{from_agent} handoffs to the {to_agent}")    
 
    async def on_agent_end(self, context: RunContextWrapper, agent: Agent , output):    
        print(f"{agent.name} is finished working with final output....")
        print(f"Active agents are : {self.active_agents}")
        print(f"Total Handoffs are : {self.handoffs}")
        print(f"Tools Usage are : {self.tool_usage}")
        
@on_chat_start
async def start():  
    """
    Initializes the agent and tool setup for a new chat session.
    This function is called once when a user starts a new chat.
    """

    # Store the main entry-point agent in the user session
    cl.user_session.set("triage_agent", triage_agent)

    await cl.Message(
        content="Welcome to the  Bushra Code AI Assistant! How can I help you today?"
    ).send()


@on_message
async def main(message: cl.Message):
    """
    Handles incoming user messages and runs the agentic workflow.
    """
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

    
    triage_agent = cl.user_session.get("triage_agent")
    msg = cl.Message(content="Thinking ...")
    await msg.send() 
    try:
        run_config = RunConfig(
            workflow_name="Code_Assistant_Workflow",
        )
        info = Info("Abdullah","I am a software engineer with expertise in AI and web development.")
        try:    
        # Run the agent with the latest message and context
            result = Runner.run_streamed(starting_agent=triage_agent,
                                         input=message.content,
                                         run_config=run_config,
                                         context=info,
                                         max_turns=30,
                                         session=session,
                                         hooks=RunHookCycle())
        # Stream the response token by token and surface tool outputs
        except MaxTurnsExceeded as e:
            await cl.Message(content=f"Max turns exceeded: {e}").send()
            
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
    except InputGuardrailTripwireTriggered as e:
        await cl.Message(content=f"Your input is invalid . I am here to help you in programming and coding .").send()   
        print("Error1",e) 
    except Exception as e:
        await cl.Message(content=f"An error occur {e}").send()
        print("Error2",e)
        