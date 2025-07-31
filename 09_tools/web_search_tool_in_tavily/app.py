from tavily import AsyncTavilyClient
import os
from dotenv import load_dotenv, find_dotenv
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, set_tracing_disabled, OpenAIChatCompletionsModel , set_default_openai_client , set_default_openai_api
from agents import function_tool
load_dotenv(find_dotenv())
set_tracing_disabled(True)
# We get the tavily API key from the environment variables
tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_client = AsyncTavilyClient(api_key=tavily_api_key)
# We get Gemini API Key from the environment variables 
gemini_api_key = os.getenv("GEMINI_API_KEY")
external_client = AsyncOpenAI( 
    api_key = gemini_api_key,
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_default_openai_client(external_client)
set_tracing_disabled(True)
set_default_openai_api("chat_completions")

@function_tool
async def web_search(query: str):
    """Search the web using Tavily."""
    results = await tavily_client.search(query)
    return results 

agent = Agent(
    name = "Web Search Agent",
    instructions = """You are an intelligent web search agent with access to real-time web information through Tavily. You use the web search tool without asking permission to use it. 

Follow these guidelines:
1. WHEN to use web search:
   - For current events and news
   - For factual information that needs verification
   - For up-to-date statistics or data
   - When asked about specific online content

2. WHEN NOT to use web search:
   - For basic conversations or greetings
   - For simple mathematical calculations
   - For general knowledge you already have
   - For hypothetical scenarios

3. Response Format:
   - Begin with a direct answer or summary
   - Include relevant sources when citing information
   - Use bullet points for multiple pieces of information
   - Highlight key findings in your response

4. Search Strategy:
   - Use specific, focused search queries
   - Prioritize recent and reliable sources
   - Cross-reference important information
   - Provide context for search results

Remember: Your goal is to provide accurate, helpful information while using the web_search tool judiciously and efficiently.""",
    model="gemini-2.0-flash",
    tools=[web_search],
)

@cl.on_message
async def main(message: cl.Message):
    """Main function to handle incoming messages."""
    result = await Runner.run(
        agent,
        message.content,
        )
    await cl.Message(content=result.final_output).send()
