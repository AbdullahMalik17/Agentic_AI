from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel, RunConfig , RunContextWrapper , function_tool 
import os 
import asyncio
from dotenv import load_dotenv , find_dotenv
from dataclasses import dataclass
from agents import set_default_openai_api

# load the environment variables
load_dotenv(find_dotenv())
set_default_openai_api("chat_completions")

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
def basic_dynamic( context: RunContextWrapper, agent: Agent) -> str:
    return f"You are {agent.name}. You give the user information about the user based on the context provided."
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
        instructions = basic_dynamic,
        tools=[get_information]
    )    

    user_info = Information("Abdullah",18,"muhammadabdullah51700@gmail.com")
    print(f"Created user info: {user_info}")
    result = Runner.run_streamed(starting_agent=agent ,input = "What is your name? How can you help me ?", run_config=run_config , context=user_info)
    print("Final output:")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and hasattr(event.data, "delta"):
            print(event.data.delta, end="", flush=True)
if __name__ == "__main__":
    asyncio.run(main())
