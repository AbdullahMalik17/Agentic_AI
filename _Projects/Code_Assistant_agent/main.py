import os
from dotenv import load_dotenv, find_dotenv

import chainlit as cl
from chainlit import on_message, on_chat_start


from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    set_default_openai_client,
    function_tool,
    ModelSettings,
    OpenAIChatCompletionsModel,
    RunContextWrapper,
)
from tavily import AsyncTavilyClient

# this takes the data from prompt files
from system_prompt import (
    web_developer_prompt,
    mobile_developer_prompt,
    agentic_ai_developer_prompt,
    panacloud_prompt,
)

from dataclasses import dataclass
# --- Load Environment Variables ---
_:bool = load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GEMINI_API_KEY")
tavily_api_key= os.getenv("TAVILY_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# --- Model and Client Configuration ---
# Note: "gemini-2.0-flash" seems like a custom or placeholder name.
# Ensure it matches the actual model available at your endpoint.
# Common models are "gemini-1.5-flash", "gemini-1.5-pro", etc.
MODEL_NAME = "gemini-2.5-pro" 
TEMPERATURE = 1.8

# Configure the client to use the Gemini API via an OpenAI-compatible endpoint
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
common_model_settings = ModelSettings(temperature=TEMPERATURE, tool_choice="auto")
common_model = OpenAIChatCompletionsModel(
    openai_client=external_client, model=MODEL_NAME
)

# Initialize Tavily client for web search
tavily_client = AsyncTavilyClient(api_key=tavily_api_key)


# --- Tool Definitions ---
@function_tool
async def web_search(query: str) -> str:
    """Search the web using Tavily for latest Information. Returns a formatted string of the results."""
    if not tavily_client:
        return "Tavily client is not initialized."
    try:
        response = await tavily_client.search(query=query, search_depth="advanced")

        # Format results for better readability
        formatted_results = []
        for result in response.get('results', []):
            result_text = f"""#{result.get('title')}
            {result.get('content')}
            [Source]({result.get('url')})\n\n"""
            formatted_results.append(result_text)

        if not formatted_results:
            return "No results found from web search."
        return "\n".join(formatted_results)
    except Exception as e:
        return f"An error occurred during web search: {e}"

@dataclass
class Info:
    name : str
    description: str

@function_tool
def get_info(Wrapper:RunContextWrapper[Info])->str:
    """The name and description of user from the context."""
    return f"The name of user is {Wrapper.context.name} and the description is {Wrapper.context.description}."

@on_chat_start

async def start():
    """
    Initializes the agent and tool setup for a new chat session.
    This function is called once when a user starts a new chat.
    """
    cl.user_session.set("history", [])

    # --- Agent Definitions ---
    # These agents are created once per session for efficiency.

    web_developer = Agent(
        name="Web_Developer",
        instructions=web_developer_prompt,
        model=common_model,
        handoff_description="An expert in web development technologies like React,Next.js, Node.js, and Python.",
        tools=[web_search],
        model_settings=common_model_settings,
    )

    mobile_developer = Agent(
        name="Mobile_Developer",
        instructions=mobile_developer_prompt,
        model=common_model,
        handoff_description="An expert in mobile app development for iOS and Android.",
        tools=[web_search],
        model_settings=common_model_settings,
    )

    devops_agent = Agent(
        name="DevOps_Expert",
        instructions="You are a helpful assistant focused on DevOps. Provide clear, concise information about DevOps concepts, tools (like Docker, Kubernetes, CI/CD), and best practices. Generate code examples when necessary.",
        model=common_model,
        tools=[web_search],
        model_settings=common_model_settings,
    )

    openai_agent = Agent(
        name="OpenAI_Expert",
        instructions="You are a helpful assistant with deep knowledge of OpenAI. Your sole purpose is to provide clear and concise answers about OpenAI's models, APIs, and platform. Do not discuss unrelated topics.",
        model=common_model,
        tools=[web_search],
        model_settings=common_model_settings,
    )

    # Convert agents to tools for hierarchical agent structures
    devops_tool = devops_agent.as_tool(
        tool_name="DevOps_Tool",
        tool_description="Use this tool for any questions related to DevOps, CI/CD, Docker, or Kubernetes.",
    )
    openai_tool = openai_agent.as_tool(
        tool_name="OpenAI_Tool",
        tool_description="Use this tool for any questions about OpenAI, its models (like GPT-4), or its APIs.",
    )

    agentic_ai_developer = Agent(
        name="Agentic_AI_Developer",
        instructions=agentic_ai_developer_prompt,
        model=common_model,
        handoff_description="An expert in building agentic AI systems and using advanced AI frameworks(openai sdk , Langchain/LanGraph , CrewAI).",
        tools=[devops_tool, openai_tool, web_search],
        model_settings=common_model_settings,
    )

    # Triage Agent: The entry point for all user queries
    triage_agent = Agent(
        name="Bushra_Triage",
        instructions=panacloud_prompt,
        model=common_model,
        handoffs=[web_developer, mobile_developer, agentic_ai_developer],
        tools=[web_search, get_info],
        # 'required' forces the model to choose a handoff, which is good for a triage agent.
        model_settings=ModelSettings(temperature=TEMPERATURE, tool_choice="auto"),
    )

    # Store the main entry-point agent in the user session
    cl.user_session.set("triage_agent", triage_agent)

    await cl.Message(
        content="Welcome to the Coder AI Assistant! How can I help you today?"
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
        info = Info("Abdullah","I am a software engineer with expertise in AI and web development.")
            
        # Run the agent with the latest message and context
        result = Runner.run_streamed(starting_agent=triage_agent,input=history,context=info,max_turns=30)
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

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(e)
        await cl.Message(content=error_message).send()
        print(error_message)