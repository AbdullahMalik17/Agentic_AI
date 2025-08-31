import os 
from dotenv import load_dotenv, find_dotenv
from tavily import AsyncTavilyClient
load_dotenv(find_dotenv())
from agents import function_tool
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("Tavily API key is not set. Please ensure TAVILY_API_KEY is defined in your .env file.")

# Initialize Tavily client for web search
tavily_client = AsyncTavilyClient(api_key=tavily_api_key)
# --- Tool Definitions ---    
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


    

        