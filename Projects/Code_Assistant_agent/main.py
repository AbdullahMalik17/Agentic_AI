import chainlit as cl
# this takes the data from prompt files 
from system_prompt import web_developer_prompt, mobile_developer_prompt, agentic_ai_developer_prompt, panacloud_prompt
from chainlit import on_chat_start, on_message
from dotenv import load_dotenv , find_dotenv
import os 
import asyncio
from agents import Agent , Runner ,AsyncOpenAI, set_default_openai_client , set_tracing_disabled , set_default_openai_api
load_dotenv(find_dotenv())
api_key = os.getenv("GEMINI_API_KEY")
external_client = AsyncOpenAI( 
    api_key= api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_default_openai_client(external_client)
set_tracing_disabled(True)
set_default_openai_api("chat_completions")
#we will make the on chat data
# @on_chat_start
# async def start():
#     """Set up the chat session when a user connects."""
#     await cl.Message(content="Welcome to coder AI Assistant! How can you help you today?").send()
@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Making a website",
            message="I want to make a website for my business . This website should contain a homepage, about , contact . The contact page should be beautiful . I want to use HTML, CSS, and JavaScript for the front-end. Can you help me with that?",
            ),

        cl.Starter(
            label="Create a mobile app",
            message="Can you help me design a simple mobile app for my shop? I want it to have a product list and a contact form. Please use the latest mobile development best practices."
),
        cl.Starter(
            label="Agentic AI developer help",
            message="I want to get started with Agentic AI development. Can you explain what it is and how I can build an agentic AI app",
            ),
        cl.Starter(
            label="Integrate AI into my app",
            message="How can I integrate an AI assistant into my web or mobile app? Please provide a code example."
            )
        ]
@on_message
async def main(message :cl.Message):
    web_developer : Agent = Agent(
                        name = "Web DEV" ,
                        instructions=web_developer_prompt,
                        model="gemini-2.0-flash",
                        handoff_description="Web developer expert . "

   )
    mobile_developer : Agent = Agent(
                        name = "Mobile DEV" ,
                        instructions=mobile_developer_prompt,
                        model="gemini-2.0-flash",
                        handoff_description="mobile app developer expert ."
    )

    # Here we make th agent that it is used as tools .
    devops_agent : Agent = Agent(
                        name = "DevOps Expert" ,
                        instructions= """You are a helpful assistant. You only tell the user about DevOps. Generate a code example if necessary. Your role is to provide clear and concise information about DevOps concepts, tools (like Docker, Kubernetes, CI/CD pipelines), and best practices.""",
                        model="gemini-2.0-flash",
                       )
    openai_agent : Agent = Agent(
                        name = "OpenAI Expert" ,
                        instructions="""You are a helpful assistant. Your sole purpose is to provide information about OpenAI. When asked a question, provide a clear and concise answer based on your knowledge of OpenAI. Do not discuss topics unrelated to OpenAI.""",
                        model="gemini-2.0-flash",
                       )
    devops_tool = devops_agent.as_tool(tool_name="DevOps_Tool", tool_description="A tool that provides information about DevOps.")
    openai_tool = openai_agent.as_tool(tool_name="OpenAI_Tool", tool_description="A tool that provides information about OpenAI")
    # Using these agents as tools
    agenticai_developer : Agent = Agent(
                        name = "Agentic DEV" ,
                        instructions=agentic_ai_developer_prompt,
                        model="gemini-2.0-flash",
                        handoff_description="Agentic AI developer expert . ",
                        tools=[devops_tool,openai_tool])
    # Triage Agent .venv\Scripts\activate
    panacloud :Agent = Agent(
                        name = "Panacloud" ,
                        instructions=panacloud_prompt,
                        model="gemini-2.0-flash",
                        handoffs=[web_developer,mobile_developer,agenticai_developer])
#   To make the stateable .
    cl.user_session.set("history",[])
    history = cl.user_session.get("history",[])
    history.append({"role":"user", "content": message.content})
    result = await Runner.run(
        panacloud, 
        message.content,
    )
    print(result)
    print(message.content)
    await cl.Message(content=result.final_output).send()
    print(result.final_output)
    history.append({"role":"system","content":result.final_output})
    cl.user_session.set("history", history)
    print("role: User", message.content)
    print("role: System", result.final_output)
    print(history)