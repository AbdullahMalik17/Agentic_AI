import os
import asyncio
from agents import Agent, Runner, AsyncOpenAI , OpenAIChatCompletionsModel , RunConfig , function_tool , ModelSettings , RunContextWrapper, set_default_openai_api , SQLiteSession
from dotenv import load_dotenv, find_dotenv 
from tavily import AsyncTavilyClient
from research_agents import requirement_gathering_agent
from dataclasses import dataclass 
# Load environment variables
load_dotenv(find_dotenv())
# Force Agents SDK to use Chat Completions API to avoid Responses API event types
set_default_openai_api("chat_completions")

# It is an API_key of Gemini 
gemini_api_key = os.getenv("GEMINI_API_KEY")  
if not gemini_api_key:
    raise ValueError("Gemini API key is not set . Please , ensure that it is defined in your env file.")
# It is an API key of Tavily
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("Tavily API key is not set. Please ensure TAVILY_API_KEY is defined in your .env file.")
tavily_client = AsyncTavilyClient(api_key=tavily_api_key)
# It is used to show the display message in the chat 
# Step 1: Create a provider 
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
    # Step 2: Create a model
model = OpenAIChatCompletionsModel(
    openai_client=provider,
    model="gemini-2.5-flash"
) 
    # Step 3: Define config at run level
run_config = RunConfig(
    model=model,
    workflow_name="Deep Research Agent in CLI"
)
#   step 4 : Define Session for history 
session = SQLiteSession("User_Bushra","Database.bd")
def deep_research_instructions(Wrapper: RunContextWrapper, agent: Agent) -> str:
    return f"""You are {agent.name}, an advanced AI research coordinator.
Your task is to receive the user's research query and  hand it off to the 'Requirement Gathering Agent' to begin the research process. If the Query is simple , you can directly hand it off to the 'Lead Agent' for immediate action.
Do not analyze the query, answer the user, or perform any other actions. Your sole function is to initiate the multi-agent workflow."""

@dataclass
class Info:
    name : str
    father_name : str
    mother_name : str
    sister_name : str
    
@function_tool 
@cl.step(type="Web Search Tool")
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

@function_tool
@cl.step(type="Get Info Tool")
async def get_info(Wrapper: RunContextWrapper[Info]) -> str:
    """Return the user's profile information from the run context."""
    return (
        f"The name of user is {Wrapper.context.name}, "
        f"his father name is {Wrapper.context.father_name}, "
        f"his mother name is {Wrapper.context.mother_name},"
        f"and his sister name is {Wrapper.context.sister_name}."
    )
agent = Agent(
    name="DeepSearch Agent",
    instructions=deep_research_instructions,  
    # instructions="You are DeepSearch Agent . You can answer questions, provide information and give Example(Code) if necessary . For latest information, you can search through websearch tool. Always respond in a helpful and friendly manner",
    tools=[web_search, get_info],  # <- removed trailing comma
    model_settings=ModelSettings(temperature=1.9),
    handoffs = [requirement_gathering_agent]
)
chats = []    

async def main():
    user_data = Info(
        name="Abdullah",
        father_name="Muhammad Athar",
        mother_name="Bushra",
        sister_name="Hamna"
    )


    while True:
        user_input = input("Enter Your Prompt ...")
        if user_input.lower() in ["exit","quit"]:
            break
        user_message = {"role":"user","content":f"{user_input}"}
        chats.append(user_message)
        result = await Runner.run(agent, chats, run_config=run_config,context = user_data , max_turns=30,session = session)
        ai_message = {"role":"assistant","content":result.final_output}
        chats.append(ai_message)
        print(result.final_output)    
 
        
asyncio.run(main())  