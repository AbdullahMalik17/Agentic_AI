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
class Information:
    name : str 
    age :int 
    email: str 

@function_tool
async def get_information(Wrapper : RunContextWrapper[Information])-> str:
    # print("Retrieving user information from context...")
    # print(f"\n Context received: {Wrapper} \n ")
    user_info1 = f"The name of user is {Wrapper.context.name}, age is {Wrapper.context.age}, email is {Wrapper.context.email}."
    # print(f"Returning: {user_info1}")
    return user_info1


async def main():
    # Create an agent with the model and function tool
  
        
    agent : Agent = Agent(
        name = "InformationAgent",
        tools=[get_information]
    )    

    user_info = Information("Abdullah",18,"muhammadabdullah51700@gmail.com")
    print(f"Created user info: {user_info}")
    result = await Runner.run(agent , "Please use the get_information tool to tell me about Abdullah's age and email. ", run_config=run_config , context=user_info)
    print("Final output:")
    print(result.final_output)
    print(agent.instructions)
if __name__ == "__main__":
    asyncio.run(main())

    