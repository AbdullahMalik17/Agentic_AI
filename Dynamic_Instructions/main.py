from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel, RunConfig , RunContextWrapper , function_tool 
import os 
import asyncio
from dotenv import load_dotenv , find_dotenv
from dataclasses import dataclass


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
class User:
    name : str
    email : str
    
@function_tool    
def get_user_info(context: RunContextWrapper[User]) -> str:
    return f"The name of the user is {context.context.name} and the email is {context.context.email}."
# It is the System Prompt 
def basic_dynamic(context: RunContextWrapper[User], agent: Agent) -> str:
    return f"You are {agent.name}.You give the user information about the user based on the context provided."


# Create an agent with the model and function tool    
agent = Agent(
    name="Dynamic Agent",
    instructions=basic_dynamic , 
    tools=[get_user_info]
)  
async def main1():
    user = User("Abdullah", "muhammadabdullah51700@gmail.com")
    result = await Runner.run(agent,"What is the email of Abdullah?", run_config=run_config,context=user)
    print("Final output:")
    print(result.final_output)
    data = agent.instructions
    print(data)

if __name__ == "__main__":
    asyncio.run(main1())
  
    
