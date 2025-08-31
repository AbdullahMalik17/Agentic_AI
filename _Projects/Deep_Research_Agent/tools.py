from agents import RunContextWrapper , function_tool 
from dataclasses import dataclass
import os 
from mem0 import MemoryClient
from dotenv import load_dotenv
load_dotenv()

mem0_api_key = os.getenv("MEM0_API_KEY")
client = MemoryClient()
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
@function_tool
async def save_memories(Wrapper: RunContextWrapper,query:str):
    """Use this tool to save the memory of the user""" 
    response = client.add(query, user_id="Abdullah")
    return response
@function_tool
async def get_memories(Wrapper: RunContextWrapper,query:str):
    """Use this tool to get the memory of the user""" 
    response = client.search(query, user_id="Abdullah")
    return response