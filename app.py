from dataclasses import dataclass
import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.responses import PlainTextResponse
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool

# -------------------------------------------------------------------------------- #
# Load environment variables
# -------------------------------------------------------------------------------- #
load_dotenv()

# -------------------------------------------------------------------------------- #
# Initialize Google model
# -------------------------------------------------------------------------------- #
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# -------------------------------------------------------------------------------- #
# System prompt for the agent
# -------------------------------------------------------------------------------- #
SYSTEM_PROMPT = """
You are an intelligent AI agent responsible for **analyzing and shortlisting resumes** based on a given job description.

---

### 🎯 Task Overview:
Your primary task is to:
1. Execute the tool **'extract_candidate_details'** to retrieve candidate profiles
2. Analyze each candidate against the job description
3. Score and rank candidates
4. Return ONLY the top 50 candidates in a specific format

---

### ⚙️ Processing Instructions:
1. First, call the 'extract_candidate_details' tool to get all candidate data
2. Analyze each candidate's profile against the **provided job description**
3. Evaluate alignment based on:
   - **Key Skills:** 50%
   - **Total Experience:** 20%
   - **Relevant Experience:** 20%
   - **Notice Period:** 10%
4. Compute a **similarity score (0–100)** for each candidate
5. Rank ALL candidates from highest to lowest score
6. Select and return **only the Top 50 candidates**

---

### 🧾 CRITICAL OUTPUT FORMAT:
Your response must ONLY contain the formatted candidate list. Follow this EXACT format:

1.  
Name: [Full Name]  
Email: [Email Address]  
Contact: [Phone Number]  
CTC: [Current CTC as number]  
ECTC: [Expected CTC as number]  
Resume: [Resume URL]  
Experience: [Years]  
Relevant Experience: [Years]  
Skills: [Comma-separated key skills - max 5-6 most relevant]  
Score: [Numeric score between 0-100]  

2.  
Name: [Full Name]  
Email: [Email Address]  
...

---

### 🧠 CRITICAL GUIDELINES:
- DO NOT include any JSON, code blocks, or markdown tables
- DO NOT include explanations, summaries, or additional text
- DO NOT show the raw tool output
- ONLY return the formatted list of exactly 50 candidates
- Each candidate entry must be numbered (1, 2, 3...)
- Each candidate must have all fields listed above
- Skills should be a SHORT comma-separated list (not the full list)
- Score must be a decimal number (e.g., 94.5, 91.2)
- Sort by Score from highest to lowest
"""

# -------------------------------------------------------------------------------- #
# Dataclass for context
# -------------------------------------------------------------------------------- #
@dataclass
class Context:
    user_id: str

# -------------------------------------------------------------------------------- #
# Default path for resumes
# -------------------------------------------------------------------------------- #
DEFAULT_RESUME_PATH = "E://resumeagent//resume.json"

# -------------------------------------------------------------------------------- #
# Tool definition
# -------------------------------------------------------------------------------- #
@tool
def extract_candidate_details(file_path: str = DEFAULT_RESUME_PATH):
    """
    Reads a resume JSON file and extracts key candidate details.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON structure in file")

    candidates = data.get("data", {}).get("candidates", [])
    extracted_data = []

    for candidate in candidates:
        candidate_info = {
            "name": candidate.get("name", "N/A"),
            "contact": candidate.get("contactNumber", "N/A"),
            "email": candidate.get("email", "N/A"),
            "resume": candidate.get("resume", "N/A"),
            "key_skills": candidate.get("keySkills", "N/A"),
            "experience": candidate.get("experience", "N/A"),
            "relevant_experience": candidate.get("relevantExperience", "N/A"),
            "current_ctc": candidate.get("currentCtc", "N/A"),
            "expected_ctc": candidate.get("expectedCtc", "N/A"),
            "notice_period": candidate.get("noticePeriod", "N/A"),
        }
        extracted_data.append(candidate_info)
    return extracted_data

# -------------------------------------------------------------------------------- #
# Create the LangChain agent
# -------------------------------------------------------------------------------- #
agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[extract_candidate_details],
)

# -------------------------------------------------------------------------------- #
# Initialize FastAPI app
# -------------------------------------------------------------------------------- #
app = FastAPI(
    title="Resume Shortlisting Agent",
    version="1.1",
    description="AI agent that analyzes and shortlists resumes based on job descriptions.",
)

# -------------------------------------------------------------------------------- #
# API Endpoint — Returns plain text output
# -------------------------------------------------------------------------------- #
@app.post("/analyze_resumes", response_class=PlainTextResponse)
async def analyze_resumes(request: Request, job_description: str = Body(None)):
    """
    Analyze resumes based on a given job description (JSON or plain text input).
    Returns plain text output without JSON wrapper.
    Example JSON: {"job_description": "..."}
    Example Text:  (raw job description pasted)
    """

    # Try parsing JSON input first
    if not job_description:
        try:
            data = await request.json()
            job_description = data.get("job_description", "")
        except Exception:
            job_description = (await request.body()).decode("utf-8").strip()

    if not job_description:
        raise HTTPException(status_code=400, detail="No job description provided.")

    # Invoke the agent
    response = agent.invoke(
        {"messages": [{"role": "user", "content": job_description}]},
        context=Context(user_id="0"),
    )

    # Extract agent output safely
    if "messages" in response:
        last_message = response["messages"][-1]
        content = getattr(last_message, "content", None)

        if not content and isinstance(last_message, dict):
            content = last_message.get("content", "")

        # Flatten list content
        if isinstance(content, list):
            text_output = ""
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    text_output += item["text"]
                else:
                    text_output += str(item)
            content = text_output

        formatted_output = (
            str(content)
            .replace("\\n", "\n")
            .replace("\\t", "\t")
            .replace("\\", "")
            .strip()
        )

        # Return plain text directly
        return formatted_output

    raise HTTPException(status_code=500, detail="Unexpected response format from agent")


# -------------------------------------------------------------------------------- #
# Run on localhost:8001
# -------------------------------------------------------------------------------- #
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)
    
    
    