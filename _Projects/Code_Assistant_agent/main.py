# This file is part of the Coder AI Assistant project.
import chainlit as cl
from chainlit import on_message, on_chat_start
from agent_definations import triage_agent , Info 

from agents import Runner , MaxTurnsExceeded , RunConfig
@on_chat_start
async def start():  
    """
    Initializes the agent and tool setup for a new chat session.
    This function is called once when a user starts a new chat.
    """
    cl.user_session.set("history", [])

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
    triage_agent = cl.user_session.get("triage_agent")
    history = cl.user_session.get("history")
    msg = cl.Message(content="")
    await msg.send() 

    # Append the user's message to the history
    history.append({"role": "user", "content": message.content})

    try:
        run_config = RunConfig(
            workflow_name="Code_Assistant_Workflow",
        )
        info = Info("Abdullah","I am a software engineer with expertise in AI and web development.")
        try:    
        # Run the agent with the latest message and context
            result = Runner.run_streamed(starting_agent=triage_agent,
                                         input=history,
                                         run_config=run_config,
                                         context=info,
                                         max_turns=30)
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
        history.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("history", history)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(e)
        await cl.Message(content=error_message).send()
        print(error_message)