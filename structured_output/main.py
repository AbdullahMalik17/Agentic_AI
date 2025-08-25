import os
from dotenv import load_dotenv , find_dotenv
from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel , RunContextWrapper , function_tool
from pydantic import BaseModel 
_:bool = load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GEMINI_API_KEY","")
openai_api_key = os.getenv("OPENAI_API_KEY","")

class Data(BaseModel):
    city: str
    temperature: float
    air_speed: float 
    summary : str 
    
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
    output_type=Data,
)
# Here we will run the agent with the input query. 
result = Runner.run_sync(agent, "Assalam o Alaikum , What is the weather in Bahawalpur ?")
print(result.final_output)
print(result.final_output.city)
print(result.final_output.temperature)
print(result.final_output.summary)
print(result.final_output.air_speed)