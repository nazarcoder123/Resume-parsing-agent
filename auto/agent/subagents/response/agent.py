from google.adk.agents import LlmAgent
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import json_instruction, instructions

GEMINI_MODEL = "gemini-2.0-flash" 

response_refiner_agent = Agent(
    name="build_response_refiner",
    model=GEMINI_MODEL,
    instruction=json_instruction,
    description="You are a output refiner agent.",
    output_key="extracted_text",
)