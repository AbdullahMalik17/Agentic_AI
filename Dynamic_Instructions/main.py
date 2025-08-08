from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel, RunConfig , RunContextWrapper , function_tool 
import os 
import asyncio
from dotenv import load_dotenv , find_dotenv
from dataclasses import dataclass
from typing import Callable

# load the environment variables
load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GEMINI_API_KEY")

# We create a gemini provider client 

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-pro",
    openai_client=external_client,
)

run_config = RunConfig(
    model = model ,
    model_provider = external_client,
    tracing_disabled=True,
) 
@dataclass   
class User_Info :
   name : str
   email:str
# Here are the tools     
@function_tool
def user_information(local_context: RunContextWrapper[User_Info])->str :
    print(local_context)
    return f"The name of user is {local_context.context.name} and the email is {local_context.context.email}."
# These are the system instructions for the agent      
def system_prompt(local_context: RunContextWrapper[User_Info] , agent)->str :
    return f"You are a {agent.name} . Give the instruction about the user . "
        # Create an agent with the model and function tool    
agent = Agent(
    name = "InformationAgent",
    instructions="",
    tools=[user_information],
)    
user_info = User_Info("Abdullah","muhammadabdullah@gmail.com")
result = Runner.run_sync(agent,"What is the gmail of user . Tell me by using tool", run_config=run_config ,context=user_info )
print("Final output:")
print(result.final_output)

    
