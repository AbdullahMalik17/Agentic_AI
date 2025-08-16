from agents import Agent , AsyncOpenAI, OpenAIChatCompletionsModel, function_tool , RunContextWrapper , ModelSettings
from tavily import AsyncTavilyClient
import os 
from dotenv import load_dotenv, find_dotenv
from tools import get_info

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
def dynamic_instructions(Wrapper: RunContextWrapper, agent: Agent) -> str:
    return f"""You are the {agent.name}, an expert researcher responsible for executing a research plan.
    
You have been given a detailed plan from the Planning Agent. Your tasks are:
1. Execute the research plan step-by-step, using the 'web_search' tool with the specified queries.
2. Gather all necessary information from the web.
3. Analyze and synthesize the collected information thoroughly.
4. Structure your final response with clear sections as requested, such as:
   - Summary of findings
   - Detailed analysis
   - Supporting evidence
   - Recommendations (if applicable)
5. ALWAYS cite your sources properly using markdown links.

You are the final agent in the chain. Your response will be sent directly to the user. Ensure it is comprehensive, accurate, and well-structured."""

def gather_requirements_instructions(Wrapper: RunContextWrapper, agent: Agent) -> str:
    return f"""You are the {agent.name}, responsible for understanding and clarifying the user's research requirements.

Your tasks are:
1. Interact with the user if their request is unclear to gather all necessary details.
2. Identify the key objectives, areas to explore, and any constraints.
3. Synthesize this into a clear set of requirements.
4. Minimise the Questioning to ensure the user feels understood and engaged.

IMPORTANT: Once the requirements are clear, you MUST hand off to the 'Planning Agent'. Do not attempt to answer the user's query or perform any research yourself. Your only goal is to define the research scope for the next agent."""

def planning_instructions(Wrapper: RunContextWrapper, agent: Agent) -> str:
    return f"""You are the {agent.name}, a strategic research planner. Your SOLE responsibility is to create a detailed research plan based on the provided requirements.

Your tasks are:
1. Review the requirements gathered by the previous agent.
2. Break down the research into specific, actionable subtasks.
3. For each subtask, identify the key search queries that the Lead Agent should use.
4. Structure your output as a clear, step-by-step research plan.

Your plan should include:
1. Research Objectives
2. Key Search Areas
3. Methodology
4. Expected Deliverables

IMPORTANT: After creating the plan, you MUST hand off to the 'Lead Agent' for execution. Do NOT perform the research yourself or provide a final answer to the user. Your only deliverable is the plan itself, which will be passed to the next agent."""

# To create a robust handoff chain and avoid NameErrors, we define the agents
# in reverse order of their execution.
lead_agent: Agent = Agent(
    name="Lead Agent",
    instructions=dynamic_instructions,
    tools=[web_search, get_info],  # Added get_info tool to the final agent
    model=model,
    model_settings=ModelSettings(
        temperature=1.9,  #  higher for creative synthesis
        tool_choice="auto"
    )
)

planning_agent: Agent = Agent(
    name="Planning Agent",
    instructions=planning_instructions,
    model=model,
    tools=[web_search],  # For plan validation and initial research
    handoffs=[lead_agent],  # Chained handoff
    model_settings=ModelSettings(
        temperature=0.8,
        tool_choice="auto"
    )
)

requirement_gathering_agent: Agent = Agent(
    name="Requirement Gathering Agent",
    instructions=gather_requirements_instructions,
    model=model,
    tools=[web_search],  # Allow web search for requirement validation
    handoffs=[planning_agent],  # Chained handoff
    model_settings=ModelSettings(
        temperature=0.7,  # Lower temperature for more focused responses
        tool_choice="auto"
    )
)
