import os
from google.adk import Agent
import json # Needed for pretty printing dicts
from dotenv import load_dotenv
from .prompt import json_instrution,instructions # json_instrution
from pydantic import BaseModel, Field


class RephasedDescription(BaseModel):
    jobdescription: str = Field(description="Rephased Job description")
    
# --- Constants ---
GEMINI_MODEL = "gemini-2.0-flash"

# Define the agent rephase_question
rephase_jobdescription = Agent(
    name="rebuild_jobdescription",
    model=GEMINI_MODEL,
    instruction=json_instrution,
    description="An AI agent that rephrases and enhances job descriptions for clarity, conciseness, and professional tone.",
    # output_schema=RephasedDescription, # It Will Return a Json o/p
    output_key="rephased_job" # This save the output
)
