from agents import RunContextWrapper , function_tool 
from dataclasses import dataclass
import os 
from dotenv import load_dotenv,find_dotenv
from tavily import AsyncTavilyClient

_:bool = load_dotenv(find_dotenv)
tavily_api_key = os.getenv("TAVILY_API_KEY","")
if not tavily_api_key:
    raise ValueError("The Tavily API key is not find in env file ... ")

@dataclass
class Info:
    name: str
    father_name: str
    mother_name: str
    sister_name: str

@function_tool
async def get_info(Wrapper: RunContextWrapper[Info]) -> str:
    """Return the user's profile information from the run context."""
    return (
        f"The name of user is {Wrapper.context.name}, "
        f"his father name is {Wrapper.context.father_name}, "
        f"his mother name is {Wrapper.context.mother_name},"
        f"and his sister name is {Wrapper.context.sister_name}."
    )
# Tavily Client 
tavily_client = AsyncTavilyClient(api_key=tavily_api_key)

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
            result_text = f"""### {result['title']}
{result['content']}
[Source]({result['url']})
---
"""
            formatted_results.append(result_text)

        # Join all results into a single string
        all_results = "\n".join(formatted_results)
        return all_results

    except Exception as e:
        # Handle errors gracefully
        return f"An error occurred during the web search: {str(e)}"
