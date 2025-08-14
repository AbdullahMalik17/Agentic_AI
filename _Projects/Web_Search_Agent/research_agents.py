from agents import Agent , Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool , RunContextWrapper
from tavily import AsyncTavilyClient
import os 
from dotenv import load_dotenv, find_dotenv

_:bool = load_dotenv(find_dotenv())
#here the API keys 
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("Gemini API key is not set . Please , ensure that it is defined in your env file.")

# openai_api_key = os.getenv("OPENAI_API_KEY")
# if not openai_api_key:
#     raise ValueError("OpenAI API key is not set. Please ensure OPENAI_API_KEY is defined in your .env file.")

tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("Tavily API key is not set. Please ensure TAVILY_API_KEY is defined in your .env file.")

# Tavily Client 
tavily_client = AsyncTavilyClient(api_key=tavily_api_key)

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

@function_tool 
async def web_search(query: str):
    """Search the web using Tavily."""
    try:
        # Await the Tavily search response
        response = await tavily_client.search(query=query)

        # Initialize the formatted results list
        formatted_results = []

        # Iterate through the results and format them
        for result in response['results']:
            result_text = f"""### {result['title']}
{result['content']}
[Source]({result['url']})
---
"""
            formatted_results.append(result_text)

            # Join all results into a single string
        all_results = "\n".join(formatted_results)
        return all_results

    except Exception as e:
            # Handle errors gracefully
        return f"An error occurred during the web search: {str(e)}"

# Here the Dynamic Instructions are as follows :
def  dynamic_instructions(Wrapper:RunContextWrapper,agent:Agent) -> str:
    return  """You are a {agent.name} agent. 
    1. For latest information , you should use the web search tool .
    2. Your task is to lead the conversation and guide the user through the process of  Using the reflect tool to reflect on the user's input 
    3. and provide a thoughtful response and Using the citation tool to provide citations for the information provided by the reflect tool.
"""
       

# Here it is a reflect agent 
reflect_agent : Agent = Agent(
    name="Reflect Agent",
    instructions="You are a reflect agent. Your task is to reflect on the user's input and provide a thoughtful response. ",
    model=model, 
)

# Here it is a citation agent 
citation_agent = Agent(
    name="Citation Agent",
    instructions="You are a citation agent. Your task is to provide citations for the information provided by the reflect agent.",
    model=model,
)

lead_agent : Agent = Agent(
    name="Lead Agent",
    instructions=dynamic_instructions,
    tools=[web_search, reflect_agent.as_tool(tool_name="Reflect_Tools",tool_description="You are to reflect on the user's input ."),citation_agent.as_tool(tool_name="Citation_Tools",tool_description="You are to provide citations for the information provided by the reflect tool.")],
    model=model,
)

requirement_gathering_agent : Agent = Agent(
    name="Requirement Gathering Agent",
    instructions="You are a Requirement gathering agent. Your task is to gather information from the user for clarity If needed . Use the Tavily API to perform web searches and return data Relevant questions / Question from user",
    model=model,
    handoff_description="Once you have gathered the necessary information, hand off to the Planning Agent to plan the steps for operating the task according to the user requirement.",
    tools=[web_search] 
)   
 

planing_agent : Agent = Agent(
    name="Planning Agent",
    instructions="You are a planning agent. Your task is to plan the steps for operating the task according to the user requirement . Plan the data according to the user requirement by using Data Gathering Agent , then you should reply the steps . ",
    model=model,
    handoff_description="Once you have planned the steps, hand off to the Lead Agent to execute the plan and provide the final output.",
    tools=[web_search]
)
