import os
from dotenv import load_dotenv , find_dotenv
from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel , RunContextWrapper , function_tool
from pydantic import BaseModel 
_:bool = load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GEMINI_API_KEY","")
openai_api_key = os.getenv("OPENAI_API_KEY","")

class Info_Data(BaseModel):
    product_name: str
    cost:float
    description:str
    discount_list:(list[str]|None)= None

    
# Here We will make the provider for Agent .
external_client : AsyncOpenAI=AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/", 
) 
model : OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
      model="gemini-2.5-flash",
      openai_client=external_client,
)
@function_tool
def get_weather(city : str) -> str:
    "It is used to get the weather of a city"
    return f"The weather in {city} is sunny with a temperature of 25°C."

agent : Agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    model=model,
    output_type=Info_Data,
)
# Here we will run the agent with the input query. 
result = Runner.run_sync(agent, "Assalam o Alaikum , The mobile is Iphone 16 Pro Max . Its rate is 12000Rs . It has three cameras and 8GB RAM. It has a discount of 10% and 20% .")
print(result.final_output.product_name)
print(result.final_output.cost)
print(result.final_output.description)
print(result.final_output.discount_list)