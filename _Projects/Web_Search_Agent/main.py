import os
import asyncio
from agents import Agent,ItemHelpers, Runner, AsyncOpenAI , OpenAIChatCompletionsModel , RunConfig , function_tool , ModelSettings , RunContextWrapper, set_default_openai_api
from dotenv import load_dotenv, find_dotenv 
from tavily import AsyncTavilyClient
from dataclasses import dataclass 
# Load environment variables
load_dotenv(find_dotenv())
# Force Agents SDK to use Chat Completions API to avoid Responses API event types
set_default_openai_api("chat_completions")

# It is an API_key of Gemini 
gemini_api_key = os.getenv("GEMINI_API_KEY")  
if not gemini_api_key:
    raise ValueError("Gemini API key is not set . Please , ensure that it is defined in your env file.")
# It is an API key of Tavily
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("Tavily API key is not set. Please ensure TAVILY_API_KEY is defined in your .env file.")
tavily_client = AsyncTavilyClient(api_key=tavily_api_key)
# It is used to show the display message in the chat 
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
@dataclass
class Info:
    name : str
    father_name : str
    mother_name : str
    sister_name : str
    
@function_tool 
async def web_search(query: str):
    """Search the web using Tavily."""
    response = await tavily_client.search(query)

    formatted_results = []
    
    for result in response['results']:
        result_text = f"""
### {result['title']}
{result['content']}
##### [Source]({result['url']})
---
"""
        formatted_results.append(result_text)
    
    # Join all results and send as one message
    all_results = "\n".join(formatted_results)
    return all_results

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
async def main():
    user_data = Info(
        name="Abdullah",
        father_name="Muhammad Athar",
        mother_name="Bushra",
        sister_name="Hamna"
    )
# here I create Agent . 
    agent = Agent(
        name="DeepSearch Agent",
        instructions=basic_dynamic,  
        # instructions="You are DeepSearch Agent . You can answer questions, provide information and give Example(Code) if necessary . For latest information, you can search through websearch tool. Always respond in a helpful and friendly manner",
        tools=[web_search, get_info],  # <- removed trailing comma
        model_settings=ModelSettings(temperature=1.9, max_tokens=2000, tool_choice="auto"),
    )
    result = Runner.run_streamed(
        starting_agent=agent,
        input="give me information of my profile . make a card according to it ",
        run_config=run_config,
        context=user_data,
    )

    print("=== Run starting ===")

    async for event in result.stream_events():
        # We'll ignore the raw responses event deltas
        if event.type == "raw_response_event":
            continue
        # When the agent updates, print that
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
            continue
        # When items are generated, print them
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                print("-- Tool was called")
            elif event.item.type == "tool_call_output_item":
                print(f"-- Tool output: {event.item.output}")
            elif event.item.type == "message_output_item":
                print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
            else:
                pass  # Ignore other event types

    print("=== Run complete ===")  
asyncio.run(main())  