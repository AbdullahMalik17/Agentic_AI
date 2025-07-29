from tavily import AsyncTavilyClient
import os
from dotenv import load_dotenv, find_dotenv
import chainlit as cl

load_dotenv(find_dotenv())
tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_client = AsyncTavilyClient(api_key=tavily_api_key)

@cl.on_message
# Get search response
async def main(message: cl.Message):
    query = message.content
    
    # Await the async search
    response = await tavily_client.search(query=query)
    
    # Create a formatted message with all results
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
    await cl.Message(content=all_results).send()
    
    # Send summary if available
    if 'answer' in response:
        await cl.Message(content=f"## Summary\n{response['answer']}").send()
