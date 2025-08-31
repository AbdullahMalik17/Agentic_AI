from agents import Agent , AsyncOpenAI, OpenAIChatCompletionsModel, function_tool , RunContextWrapper , ModelSettings
import os 
from dotenv import load_dotenv, find_dotenv
from tools import get_info 
from web_search import web_search


_:bool = load_dotenv(find_dotenv())
#here the API keys 
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("Gemini API key is not set . Please , ensure that it is defined in your env file.")

# openai_api_key = os.getenv("OPENAI_API_KEY")
# if not openai_api_key:
#     raise ValueError("OpenAI API key is not set. Please ensure OPENAI_API_KEY is defined in your .env file.")

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
# Initialize Tavily client for web search

# Here the Dynamic Instructions are as follows :
def dynamic_instructions(Wrapper: RunContextWrapper, agent: Agent) -> str:
    return f"""You are the {agent.name}, an expert researcher responsible for executing a research plan.
    
You have been given a detailed plan from the Planning Agent . You should follow the plan of planning agent. Your tasks are:
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
5. Don't ask too many question .

'You have knowledge about agent by using get info tool. Use this tool if the user ask you about his personal his informaton like name .'
IMPORTANT: Once the requirements are clear, you MUST hand off to the 'Planning Agent'. Do not attempt to answer the user's query or perform any research yourself. Your only goal is to define the research scope for the next agent."""

def planning_instructions(Wrapper: RunContextWrapper, agent: Agent) -> str:
    return f"""You are the {agent.name}, a strategic research planner. Your SOLE responsibility is to create a detailed research plan based on the provided requirements.

Your tasks are:
1. Review the requirements gathered by the previous agent.
2. Break down the research into specific, actionable subtasks.
3. For each subtask, identify the key search queries that the Lead Agent should use.
4. Structure your output as a clear, step-by-step research plan.
5. Use web search tool for better planning if needed .

Your plan should include:
1. Research Objectives
2. Key Search Areas
3. Methodology
4. Expected Deliverables

IMPORTANT: After creating the plan, you MUST hand off to the 'Lead Agent' for execution. Do NOT perform the research yourself or provide a final answer to the user. Your only deliverable is the plan itself, which will be passed to the next agent."""

def citation_instructions(Wrapper: RunContextWrapper, agent: Agent) -> str:
    return f"""You are the {agent.name}, responsible for ensuring all information provided by the Lead Agent is properly cited with markdown links. """
def reflect_instructions(Wrapper: RunContextWrapper, agent: Agent) -> str:
    return f"""You are the {agent.name}, responsible for reflecting on the information provided by the Lead Agent and ensuring it is comprehensive and accurate."""

citation_agent : Agent = Agent(
    name="Citation Agent",
    instructions=citation_instructions,
    model=model,
    tools=[web_search],
    )
 
reflect_agent: Agent = Agent(
    name = "Refelct Agent",
    instructions = "You are the Reflect Agent. Your task is to reflect on the information provided by the Lead Agent and ensure it is comprehensive and accurate.",
    model = model,
    tools = [web_search],  # Using get_info tool for citation and validation
) 
# To create a robust handoff chain and avoid NameErrors, we define the agents
# in reverse order of their execution.
lead_agent: Agent = Agent(
    name="Lead Agent",
    instructions=dynamic_instructions,
    tools=[web_search, get_info],  # Added get_info tool to the final agent
    model=model,
    model_settings=ModelSettings(
        temperature=1.9,  #  higher for creative synthesis
        tool_choice="auto",
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
    tools=[web_search,get_info],  # Allow web search for requirement validation
    handoffs=[planning_agent],  # Chained handoff
    model_settings=ModelSettings(
        temperature=0.7,  # Lower temperature for more focused responses
        tool_choice="auto"
    )
)
