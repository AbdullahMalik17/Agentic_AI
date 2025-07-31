from agents import Agent , Runner 
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
agent : Agent = Agent(
    name = "Assistant",
    instructions ="You are a helpful Assistant."
)
result = Runner.run_sync(agent,"What is the capital of France?")
print(result.final_output)