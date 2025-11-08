from google.adk.agents import SequentialAgent,ParallelAgent 
from google.adk.agents import Agent
import agentops
import os
from google.adk.agents import LlmAgent
from .subagents.rewrite import rephase_jobdescription  # rephase_question          
from .subagents.retrievers import candidate_details_agent
from .subagents.greet import greet_agent
from google.adk.models.lite_llm import LiteLlm
from .subagents.response import response_refiner_agent
from .prompt import instruction,json_instructions
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google import adk
from google.genai.types import Content, Part
import logging


# --- The Below Code Is AgentOps ---

agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"),trace_name="agentrag")


GEMINI_MODEL = "gemini-2.5-flash"
# Create the sequential agent
root_agents = SequentialAgent(
    name="resumefilteragent",
    sub_agents=[
        rephase_jobdescription,       
        candidate_details_agent,         
        # response_refiner_agent,           
    ],
        description=(
            "A sequential pipeline that processes user queries in two stages: "
            "first, it rephrases the question for clarity,"
            "then find the best 50 candidate as per job description"
        )
)


# Create the agent
greet_agent = LlmAgent(
    name="GreetAgent",
    model=GEMINI_MODEL,
    instruction="""Welcome to the Hr operations Desk! How can I assist you today? 
    Please provide your Job description to the the perfect candidate.
    """,
    description="Greets users politely and prompts them to provide their question or issue.",
    include_contents='default',
    output_key="greetings"
)

async def auto_save_session_to_memory_callback(callback_context):
    try:
        invocation_ctx = callback_context._invocation_context
        await invocation_ctx.memory_service.add_session_to_memory(invocation_ctx.session)
    except Exception as e:
        logging.error(f"Failed to save session to memory: {e}")

root_agent = Agent(
    name="manager",
    model=GEMINI_MODEL,
    description="Manager agent responsible for routing user queries and managing conversation memory.",
    instruction=json_instructions,
    sub_agents=[greet_agent, root_agents],
    tools=[adk.tools.preload_memory_tool.PreloadMemoryTool()], 
    after_agent_callback=auto_save_session_to_memory_callback,
)
