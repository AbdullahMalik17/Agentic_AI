from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel, RunConfig  
import os 
from dotenv import load_dotenv , find_dotenv


# load the environment variables
load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
# We create a gemini provider client 

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-pro",
    openai_client=external_client,
)

run_config = RunConfig(
    model = model ,
    model_provider = external_client,
)   

agent : Agent = Agent()
result = Runner.run(starting_agent=agent ,input = "What is your name? How can you help me ?", run_config=run_config)
