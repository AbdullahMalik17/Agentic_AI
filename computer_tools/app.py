from agents import Agent , Runner 
import os
from dotenv import load_dotenv
os.environ["OPENAI_API_KEY"] = "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"
agent : Agent = Agent(
    name = "Assistant",
    instructions ="You are a helpful Assistant."
)
result = Runner.run_sync(agent,"What is the capital of France?")
print(result.final_output)