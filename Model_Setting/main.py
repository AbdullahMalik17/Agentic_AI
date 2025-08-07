from agents import Agent, ModelSettings , Runner , AsyncOpenAI , OpenAIChatCompletionsModel, RunConfig, model_settings 
import os 
import asyncio
from dotenv import load_dotenv , find_dotenv
# load the environment variables
load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GEMINI_API_KEY")

# We create a gemini provider client 

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client,
)

run_config = RunConfig(
    model = model ,
    model_provider = external_client,
    tracing_disabled=True,
)   

async def main():
    # Create an agent with the model and function tool    
    agent = Agent(
        name = "InformationAgent",
        instructions="You are a helpful agents . Give detailed and informative answers to the user's questions. Be concise .",
        model_settings = ModelSettings(
            temperature=2,
            max_tokens=40000,
            presence_penalty=1.9
            )
    )    

    result = await Runner.run(agent , "Why do we need to learn Agentic AI ", run_config=run_config )
    print("Final output:")
    print(result.final_output)
if __name__ == "__main__":
    asyncio.run(main())