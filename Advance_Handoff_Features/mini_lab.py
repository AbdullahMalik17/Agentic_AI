from agents import Agent, Runner, handoff, RunContextWrapper ,OpenAIChatCompletionsModel, AsyncOpenAI , function_tool 
from agents.extensions import handoff_filters
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel
import os
import asyncio

_:bool = load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GEMINI_API_KEY", "")
openai_api_key = os.getenv("OPENAI_API_KEY", "")
# 1. Which LLM Service?
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    openai_client=external_client,
    model = "gemini-2.5-flash"
)
class HandoffData(BaseModel):
    summary: str

# --- Define our specialist agents ---
billing_agent = Agent(name="Billing Agent", instructions="Handle billing questions.",model=model)
technical_agent = Agent(name="Technical Support Agent", instructions="Troubleshoot technical issues.",model=model)

# --- Define our on_handoff callback ---
def log_the_handoff(ctx: RunContextWrapper, input_data: HandoffData):
    print(f"\n[SYSTEM: Handoff initiated. Briefing: '{input_data.summary}']\n")

# --- TODO 1: Create the advanced handoffs ---

# Create a handoff to `billing_agent`.
# - Override the tool name to be "transfer_to_billing".
# - Use the `log_the_handoff` callback.
# - Require `HandoffData` as input.
to_billing_handoff = handoff(
    agent=billing_agent,
    tool_name_override="transfer_to_billing",
    tool_description_override="Transfer to the billing specialist for assistance.",
    on_handoff=log_the_handoff,
    input_type=HandoffData,
    input_filter=handoff_filters.remove_all_tools,  
    is_enabled=True,
)

# Create a handoff to `technical_agent`.
# - Use the `log_the_handoff` callback.
# - Require `HandoffData` as input.
# - Add an input filter: `handoff_filters.remove_all_tools`.
to_technical_handoff = handoff(
    agent = technical_agent,
    tool_name_override="transfer_to_technical_support",
    tool_description_override="Transfer to the technical support specialist for assistance.",
    on_handoff=log_the_handoff,
    input_type=HandoffData,
    input_filter=handoff_filters.remove_all_tools,
    is_enabled=True,
)

# --- Triage Agent uses the handoffs ---
triage_agent = Agent(
    name="Triage Agent",
    instructions="First, use the 'diagnose' tool. Then, based on the issue, handoff to the correct specialist with a summary.",
    handoffs=[to_billing_handoff, to_technical_handoff],
    model = model,
)


async def main():
    print("--- Running Scenario: Billing Issue ---")
    result = await Runner.run(triage_agent, "My payment won't go through.")
    print(f"Final Reply From: {result.last_agent.name}")
    print(f"Final Message: {result.final_output}")

asyncio.run(main())