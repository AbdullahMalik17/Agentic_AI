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
class ActionItem(BaseModel):
    task: str
    assignee: str
    due_date: Optional[str] = None
    priority: str = "medium"

class Decision(BaseModel):
    topic: str
    decision: str
    rationale: Optional[str] = None

class MeetingMinutes(BaseModel):
    meeting_title: str
    date: str
    attendees: List[str]
    agenda_items: List[str]
    key_decisions: List[Decision]
    action_items: List[ActionItem]
    next_meeting_date: Optional[str] = None
    meeting_duration_minutes: int

# Meeting minutes extractor
agent = Agent(
    name="MeetingSecretary",
    instructions="""Extract structured meeting minutes from meeting transcripts.
    Identify all key decisions, action items, and important details.""",
    output_type=MeetingMinutes,
    model = model
)

meeting_transcript =f"""
Marketing Strategy Meeting - {datetime.now().strftime('%Y-%m-%d')}
Attendees: Sarah (Marketing Manager), John (Product Manager), Lisa (Designer), Mike (Developer)
Duration: 90 minutes

Agenda:
1. Q1 Campaign Review
2. New Product Launch Strategy  
3. Budget Allocation
4. Social Media Strategy

Key Decisions:
- Approved $50K budget for Q1 digital campaigns based on strong ROI data
- Decided to launch new product in March instead of February for better market timing
- Will focus social media efforts on Instagram and TikTok for younger demographics

Action Items:
- Sarah to create campaign timeline by September 20th (high priority)
- John to finalize product features by September 25th
- Lisa to design landing page mockups by September 22nd
- Mike to review technical requirements by September 30th

Next meeting: September 29, 2025
"""

result = Runner.run_sync(agent, meeting_transcript)

print("=== Meeting Minutes ===")
print(f"Meeting Title: {result.final_output.meeting_title}")
print(f"Date: {result.final_output.date}")
print(f"Attendees: {result.final_output.attendees}")
print(f"key_decisions: {result.final_output.key_decisions}")
print(f"Decisions: {result.final_output.key_decisions[0].decision}")
print(f"Actiona Items: {result.final_output.action_items}")