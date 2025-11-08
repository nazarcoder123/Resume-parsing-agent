import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Load environment variables from .env
load_dotenv()

GEMINI_MODEL = "gemini-2.0-flash"

# Set OpenRouter API settings (can also be set manually if needed)
os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
os.environ["OPENROUTER_API_BASE"] = os.getenv("OPENROUTER_API_BASE")

# # Get the OpenRouter API key from environment variables
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

# Set up the model using LiteLLM with OpenRouter and qwen3
model = LiteLlm(
    model="openrouter/qwen/qwen3-235b-a22b-07-25:free",
    api_key=openrouter_api_key
)

# Create the agent
greet_agent = LlmAgent(
    name="GreetAgent",
    model=GEMINI_MODEL,
    instruction="""
        Welcome to the Hr operations Desk! How can I assist you today?
        Please provide your Job description to the the perfect candidate.
    """,
    description="Greets users politely and prompts them to provide their question or issue.",
    output_key="greetings"
)


