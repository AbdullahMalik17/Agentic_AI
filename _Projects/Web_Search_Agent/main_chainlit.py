
import os
import chainlit as cl 
from agents import(
    Agent,
    Runner,
    AsyncOpenAI ,
    OpenAIChatCompletionsModel ,
    RunConfig ,
    function_tool ,
    ModelSettings ,
    RunContextWrapper,
    set_default_openai_api)
from dotenv import load_dotenv, find_dotenv 
from typing import cast
from tavily import AsyncTavilyClient
from dataclasses import dataclass 
# Load environment variables
load_dotenv(find_dotenv())
# Force Agents SDK to use Chat Completions API to avoid Responses API event types
set_default_openai_api("chat_completions")

# It is an API_key of Gemini 
gemini_api_key = os.environ.get("GEMINI_API_KEY") 
if not gemini_api_key:
    raise ValueError("Gemini API key is not set . Please , ensure that it is defined in your env file.")
# It is an API key of Tavily
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("Tavily API key is not set. Please ensure TAVILY_API_KEY is defined in your .env file.")
# Tavily Client 
tavily_client = AsyncTavilyClient(api_key=tavily_api_key)
# It is used to show the display message in the chat 
@dataclass
class Info:
    name : str
    father_name : str
    mother_name : str
    sister_name : str
    
@cl.on_chat_start
async def handle_message():
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
    run_config = RunConfig(
      model=model,
      tracing_disabled=True,  # Disable tracing
    )
    
    @function_tool 
    async def web_search(query: str):
        """Search the web using Tavily."""
        try:
            # Await the Tavily search response
            response = await tavily_client.search(query=query)

            # Initialize the formatted results list
            formatted_results = []

            # Iterate through the results and format them
            for result in response['results']:
                result_text = f"""
### {result['title']}
{result['content']}
##### [Source]({result['url']})
---
"""
                formatted_results.append(result_text)

            # Join all results into a single string
            all_results = "\n".join(formatted_results)
            return all_results

        except Exception as e:
            # Handle errors gracefully
            return f"An error occurred during the web search: {str(e)}"

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
        return f"You are {agent.name}.You should do deep to the User prompt and provide the latest knowledge by using web search tool . You give the user information about the user based on the context provided.Always respond in a helpful and friendly manner"
# here I create Agent . 
    agent = Agent(
      name="DeepSearch Agent",
      instructions=basic_dynamic,  
      # instructions="You are DeepSearch Agent . You can answer questions, provide information and give Example(Code) if necessary . For latest information, you can search through websearch tool. Always respond in a helpful and friendly manner",
      tools=[web_search, get_info],  # <- removed trailing comma
      model_settings=ModelSettings(temperature=1.9, max_tokens=2000, tool_choice="auto"),
    #   tool_use_behavior="stop_on_first_tool"
    )
    cl.user_session.set("history",[])
    cl.user_session.set("run_config", run_config)
    """Set up the chat session when a user connects."""
    cl.user_session.set("agent", agent)
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
    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("run_config"))
    
    try:
        # print("\n[CALLING_AGENT_WITH_CONTEXT]\n", history, "\n")
        #give the data of the user to the agent 
        user_Info1 = Info(name="Abdullah", father_name="Athar", mother_name="Bushra",sister_name="Amna")
        # Run the agent with streaming enabled
        # Create a RunContextWrapper with the current history
        result = Runner.run_streamed(
            starting_agent=agent,
            input=message.content,
            run_config=config,
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

