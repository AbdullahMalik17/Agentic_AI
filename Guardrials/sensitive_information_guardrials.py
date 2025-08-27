from agents import Agent, RunContextWrapper , Runner , AsyncOpenAI , OpenAIChatCompletionsModel, RunConfig , GuardrailFunctionOutput,InputGuardrailTripwireTriggered, output_guardrail
import os 
from agents.exceptions import OutputGuardrailTripwireTriggered
from dotenv import load_dotenv , find_dotenv
from pydantic import BaseModel 
import asyncio

# load the environment variables
load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
class Sensitive_Information(BaseModel):
    is_sensitive_info:bool
    reasoning:str

# We create a gemini provider client 
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client,
)
run_config = RunConfig(
    model = model ,
    model_provider = external_client,
    workflow_name="Guardrials Sensitive Information Workflow"
)   
agent_quardrial = Agent(
    name = "Sensitive Quardrial Police",
    instructions = """
    If the user is asking for help with the following  things , you can send is_sensitive_info as true:-
    - Personal Information
    - Account Details.
    - Financial Information.
    - Company information.
    - Any other sensitive information.
    """,
    model = model,
    output_type = Sensitive_Information
)
@output_guardrail
async def sensitive_info_quardrials(ctx:RunContextWrapper,agent:Agent,input:str):
    result1 = await Runner.run(starting_agent=agent_quardrial,input=input, run_config=run_config)
    return GuardrailFunctionOutput(
       output_info="Math Output",
       tripwire_triggered=result1.final_output.is_sensitive_info,
)
    
agent : Agent = Agent(
    name = "Guardrials Agent",
    instructions = "You are a helpful assistant that helps people find information.",
    model = model,
    output_guardrails=[sensitive_info_quardrials],
)
async def main():
    try:
        result = await Runner.run(starting_agent=agent ,input = "What is the account information of john@gmal.com",run_config=run_config)
        print(result.final_output)
        
    except OutputGuardrailTripwireTriggered as e:
        print(f"Your query consists of sensitive information. ")
        print("I can't give you this data without permission from the data owner")
if __name__ == "__main__":
    asyncio.run(main())