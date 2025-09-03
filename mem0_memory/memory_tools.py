import os 
from dotenv import load_dotenv, find_dotenv
from mem0 import MemoryClient
from agents import function_tool
_: bool = load_dotenv(find_dotenv())

client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

@function_tool
async def save_memory(query: str) -> str:
    """Save the memory of the user"""
    response = client.add([{"role":"User","Content":f"{query}"}], user_id="User_Abdullah")
    return response

@function_tool
async def get_memory(query: str) -> str:
    """Get the memory of the user"""
    response = client.get([{"role":"User","Content":f"{query}"}], user_id="User_Abdullah")
    return response
    