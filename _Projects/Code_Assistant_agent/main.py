import chainlit as cl
# this takes the data from prompt files 
from system_prompt import web_developer_prompt, mobile_developer_prompt, agentic_ai_developer_prompt, panacloud_prompt
from chainlit import on_message , on_chat_start
from dotenv import load_dotenv , find_dotenv
import os 
import asyncio
from agents import Agent , Runner ,AsyncOpenAI, set_default_openai_client , set_tracing_disabled , set_default_openai_api , function_tool, ModelSettings
from tavily import AsyncTavilyClient
from openai.types.responses import ResponseTextDeltaEvent
load_dotenv(find_dotenv())
api_key = os.getenv("GEMINI_API_KEY")
external_client = AsyncOpenAI( 
    api_key= api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

set_default_openai_client(external_client)
set_tracing_disabled(True)
set_default_openai_api("chat_completions")
# This is the Tavily client for web search
tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_client = AsyncTavilyClient(api_key=tavily_api_key)
#we will make the on chat data
@on_chat_start
async def start():
    """Set up the chat session when a user connects."""
    cl.user_session.set("history",[])
    await cl.Message(content="Welcome to coder AI Assistant! How can you help you today?").send()

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Making a website",
            message="I want to make a website for my business . This website should contain a homepage, about , contact . The contact page should be beautiful . I want to use HTML, CSS, and JavaScript for the front-end. Can you help me with that?",
            icon="🌐"
        ),
        cl.Starter(
            label="Create a mobile app",
            message="Can you help me design a simple mobile app for my shop? I want it to have a product list and a contact form. Please use the latest mobile development best practices.",
            icon="📱"
            ),
        cl.Starter(
            label="Agentic AI developer help",
            message="I want to get started with Agentic AI development. Can you explain what it is and how I can build an agentic AI app",
            icon="🤖"
            ),
        cl.Starter(
            label="Integrate AI into my app",
            message="How can I integrate an AI assistant into my web or mobile app? Please provide a code example.",
            icon="💡"
        )
    ]
@on_message
async def main(message :cl.Message):
    @function_tool
    async def web_search(query: str):
        """Search the web using Tavily."""
        results = await tavily_client.search(query)
        return results 

    web_developer: Agent = Agent(
        name="Web DEV",
        instructions=web_developer_prompt,
        model="gemini-2.0-flash",
        handoff_description="Web developer expert",
        tools=[web_search],
        model_settings=ModelSettings(temperature=1.9,tool_choice="auto")
   )
    mobile_developer: Agent = Agent(
        name="Mobile DEV",
        instructions=mobile_developer_prompt,
        model="gemini-2.0-flash",
        handoff_description="mobile app developer expert",
        tools=[web_search],
        model_settings=ModelSettings(temperature=1.9,tool_choice="auto")
    )
    # Here we make th agent that it is used as tools .
    devops_agent: Agent = Agent(
        name="DevOps Expert",
        instructions="""You are a helpful assistant. You only tell the user about DevOps. Generate a code example if necessary. Your role is to provide clear and concise information about DevOps concepts, tools (like Docker, Kubernetes, CI/CD pipelines), and best practices.""",
        model="gemini-2.0-flash",
        tools=[web_search],
        model_settings=ModelSettings(temperature=1.9,tool_choice="auto")
    )
    openai_agent: Agent = Agent(
        name="OpenAI Expert",
        instructions="""You are a helpful assistant. Your sole purpose is to provide information about OpenAI. When asked a question, provide a clear and concise answer based on your knowledge of OpenAI. Do not discuss topics unrelated to OpenAI.""",
        model="gemini-2.0-flash",
        tools=[web_search],
        model_settings=ModelSettings(temperature=1.9,tool_choice="auto")        
    )
    devops_tool = devops_agent.as_tool(tool_name="DevOps_Tool", tool_description="A tool that provides information about DevOps.")
    openai_tool = openai_agent.as_tool(tool_name="OpenAI_Tool", tool_description="A tool that provides information about OpenAI")
    # Using these agents as tools in the agentic AI developer agent .
    agenticai_developer: Agent = Agent(
        name="Agentic DEV",
        instructions=agentic_ai_developer_prompt,
        model="gemini-2.0-flash",
        handoff_description="Agentic AI developer expert . ",
        tools=[devops_tool, openai_tool, web_search],
        model_settings=ModelSettings(temperature=1.9,tool_choice="auto")  
        ) 
    # Triage Agent .venv\Scripts\activate
    panacloud: Agent = Agent(
        name="Panacloud",
        instructions=panacloud_prompt,
        model="gemini-2.0-flash",
        handoffs=[web_developer,mobile_developer,agenticai_developer,web_search],
        tools=[web_search], 
        model_settings=ModelSettings(temperature=1.9,tool_choice="required")
    )
  
    history = cl.user_session.get("history",[])
    # save the user Message in the hstroy .
    # Append the user's message to the history.
    history.append({"role": "user", "content": message.content})  
    # msg = cl.Message(content="")
    # await msg.send()  

    try:
        print("\n[CALLING_AGENT_WITH_CONTEXT]\n", history, "\n")
        # Run the agent with streaming enabled
        result = await Runner.run(panacloud, history)
        print("\n[AGENT_RESULT]\n", result.final_output) 
        # # Stream the response token by token
        # async for event in result.stream_events():
        #     if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
        #         token = event.data.delta
        #         await msg.stream_token(token)
        await cl.Message(result.final_output).send()
        # Append the assistant's response to the history.
        history.append({"role": "assistant", "content": result.final_output})

        # Update the session with the new history.
        cl.user_session.set("history", history)

        # Optional: Log the interaction
        print(f"User: {message.content}")
        print(f"Assistant: {result.final_output}")
  
    except Exception as e:
        await cl.Message(content={str(e)}).send()
        print(f"Error:{str(e)}")
         
        