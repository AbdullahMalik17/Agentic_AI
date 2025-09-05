from agents import RunContextWrapper , function_tool 
from dataclasses import dataclass
import os 
from mem0 import MemoryClient
from agents.tool_context import ToolContext
mem0_api_key =os.getenv("MEM0_API_KEY")
mem_client = MemoryClient(api_key=mem0_api_key)

@dataclass
class Info:
    name: str
    interests: [str]
# It sanitise that the data is according to the syntax .

mem0_api_key =os.getenv("MEM0_API_KEY")
mem_client = MemoryClient(api_key=mem0_api_key)

def sanitize_user_id(raw_user_id: str) -> str:
    """Sanitizes the user_id for mem0 by replacing problematic characters."""
    import re
    # Replace any character that is not a letter, number, underscore, or hyphen with an underscore.
    return re.sub(r'[^a-zA-Z0-9_-]', '_', raw_user_id)

@function_tool
async def search_user_memory(context: ToolContext[Info], query: str):
    """Use this tool to search user memories."""
    user_id = sanitize_user_id(context.context.name)
    response = mem_client.search(query=query, user_id=user_id, top_k=10)
    return response

@function_tool
async def save_user_memory(context:ToolContext[Info], query: str):
    """Use this tool to save user memories."""
    user_id = sanitize_user_id(context.context.name)
    response = mem_client.add([{"role": "user", "content": query}], user_id=user_id)
    return response

@function_tool
async def save_user_memory(context:ToolContext[Info], query: str):
    """Use this tool to save user memories."""
    user_id = sanitize_user_id(context.context.name)
    response = mem_client.add([{"role": "user", "content": query}], user_id=user_id)
    return response

