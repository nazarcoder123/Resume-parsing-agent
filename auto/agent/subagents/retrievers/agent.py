from google.adk import Agent
from .prompt import instructions
from .tools import analyze_resumes_tool # extract_candidate_details
from pydantic import BaseModel, Field
from dotenv import load_dotenv

class CandidateOutput(BaseModel):
    details: str = Field(description="Return the details of top 50 candidate.For more details refer 'json_instructions'")

# Load environment variables from .env
load_dotenv()
# --- Constants ---
GEMINI_MODEL = "gemini-2.5-flash"

# Create the text difference agent
candidate_details_agent = Agent(
    name="candidate_agent",
    model=GEMINI_MODEL,
    instruction=instructions,
    description="Execute this tool to get the detail of candidate.",
    tools=[analyze_resumes_tool],
    # output_schema=CandidateOutput,
    output_key="candidate_details",
)

