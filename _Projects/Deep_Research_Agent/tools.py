from agents import RunContextWrapper , function_tool 
from dataclasses import dataclass
import os 

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
