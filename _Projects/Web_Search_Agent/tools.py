from agents import Agent, Runner, AsyncOpenAI, set_tracing_disabled, OpenAIChatCompletionsModel 
import os
import asyncio
from agents import Agent,ItemHelpers, Runner, AsyncOpenAI , OpenAIChatCompletionsModel , RunConfig , function_tool , ModelSettings , RunContextWrapper
from dotenv import load_dotenv, find_dotenv 
from tavily import AsyncTavilyClient
from dataclasses import dataclass 
# Load environment variables
load_dotenv(find_dotenv())

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
async def main():
    agent = Agent(    
           name="Web Search Agent",
           tools = [web_search],       
           )
    result = await Runner.run(agent,"What is the capital of pakistan", run_config=run_config)
    
    print(result.final_output)
asyncio.run(main())
    