from agents import Agent, RunContextWrapper , Runner , AsyncOpenAI , OpenAIChatCompletionsModel, RunConfig ,input_guardrail, GuardrailFunctionOutput,InputGuardrailTripwireTriggered
import os 
from dotenv import load_dotenv , find_dotenv
from pydantic import BaseModel 
import asyncio

# load the environment variables
load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
class Math_Output(BaseModel):
    is_homework : bool
    reasoning : str

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
    workflow_name="Guardrials  Math Workflow"
)   
agent_quardrial = Agent(
    name = "Homework Quardrial Police",
    instructions = "If the user is asking for help with math homework by using math homework related words, you send is_homework as true, otherwise false. You always answer in the format {is_homework:bool,reasoning:str} and you never say anything else.",
    model = model,
    output_type = Math_Output
)
@input_guardrail
async def math_quardrials(ctx:RunContextWrapper,agent:Agent,input:str):
    result1 = await Runner.run(starting_agent=agent_quardrial,input=input, run_config=run_config)
    return GuardrailFunctionOutput(
       output_info="Math Output",
       tripwire_triggered=result1.final_output.is_homework,
    )
    
agent : Agent = Agent(
    name = "Guardrials Agent",
    instructions = "You are a helpful assistant that helps people find information.",
    model = model,
    input_guardrails=[math_quardrials],
)
async def main():
    try:
        result = await Runner.run(starting_agent=agent ,input = "What is the derivative of 2x+8y",run_config=run_config)
        print(result.final_output)
        
    except InputGuardrailTripwireTriggered as e:
        print(f"You should use this chatbot for non-homework related questions. {e}")
if __name__ == "__main__":
    asyncio.run(main())