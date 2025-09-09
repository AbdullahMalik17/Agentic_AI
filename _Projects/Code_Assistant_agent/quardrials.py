import os
from agents import Agent , Runner ,input_guardrail,GuardrailFunctionOutput , AsyncOpenAI ,OpenAIChatCompletionsModel , ModelSettings , RunContextWrapper
from dataclasses import dataclass
from dotenv import load_dotenv,find_dotenv
from pydantic import BaseModel

_:bool = load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GEMINI_API_KEY","")
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
common_model = OpenAIChatCompletionsModel(
    openai_client=external_client, model="gemini-2.0-flash"
)
class Code_Output(BaseModel):
    is_non_technical : bool
    
quard_agent : Agent = Agent(
    name="Input Quardrial",
    instructions="""Check the input of user .
    If the input of user is not related to Coding or Programming , Then you return the value of 'isnt_related_code' True .
    Otherwise , You are to return the output false . If the Question is for greeting and about chatbot,you return false """,
    model = common_model,
    output_type=Code_Output,
    model_settings=ModelSettings(temperature=0.4)
) 
@input_guardrail
def related_message(ctx:RunContextWrapper,agent:Agent,input):
    result1 = Runner.run_sync(quard_agent,input)
    return GuardrailFunctionOutput(
        output_info="Check The code related to Coding or Programming .",
        tripwire_triggered=result1.final_output.is_non_technical
    )
    
    