import os
from dotenv import load_dotenv , find_dotenv
from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel , RunContextWrapper , function_tool
from datetime import datetime
from typing import List, Optional
_:bool = load_dotenv(find_dotenv())
from pydantic import BaseModel
gemini_api_key = os.getenv("GEMINI_API_KEY","")
openai_api_key = os.getenv("OPENAI_API_KEY","")

# Here We will make the provider for Agent .
external_client : AsyncOpenAI=AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/", 
) 
# Here we define the model  
model : OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
      model="gemini-2.5-flash",
      openai_client=external_client,
)
# Here , we define Pydantic class
class Education(BaseModel):
    degree: str
    description : str 
    gpa : float | None 

class Experience(BaseModel):
    company : str
    start_time : str
    end_time : str
    duty : str
    
class Resume(BaseModel):
    name : str
    email : str
    phone_number : int
    education : List[Education]
    experience : Experience
    skill : list[str]
    language : list[str]
         
# Meeting minutes extractor
agent = Agent(
    name="MeetingSecretary",
    instructions="""Extract structured meeting minutes from meeting transcripts.
    Identify all key decisions, action items, and important details.""",
    output_type=Resume,
    model = model
)

# Test with sample resume
sample_resume = """
John Smith
Email: john.smith@email.com, Phone: (555) 123-4567

Professional Summary:
Experienced software developer with 5 years in web development and team leadership.

Education:
- Bachelor of Computer Science, MIT, 2018, GPA: 3.8
- Master of Software Engineering, Stanford, 2020

Experience:
- Senior Developer at Google (2020-present): Led team of 5 developers, implemented microservices architecture
- Junior Developer at Startup Inc (2018-2020): Built React applications, maintained CI/CD pipelines

Skills: Python, JavaScript, React, Docker, Kubernetes
Languages: English (native), Spanish (conversational), French (basic)
"""
result = Runner.run_sync(agent, sample_resume)
print(result.final_output)