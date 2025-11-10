import json
from pydantic import BaseModel, Field
import requests

# Predefined path
DEFAULT_RESUME_PATH = "E://resumeagent//resume.json"

def extract_candidate_details(file_path: str = DEFAULT_RESUME_PATH):
    """
    Reads a resume JSON file and extracts key candidate details.

    Args:
        file_path (str): Path to the JSON file (defaults to predefined path).

    Returns:
        list[dict]: A list of candidate information dictionaries.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

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


def analyze_resumes_tool(job_description: str) -> str:
    """
    Calls the resume shortlisting FastAPI agent to analyze resumes based on a given job description.
    Accepts either JSON input ({"job_description": "..."}) or plain text (raw description).
    Returns plain text output directly from the API (no JSON wrapper).
    """
    try:
        url = "http://127.0.0.1:8001/analyze_resumes"
        
        # --- Detect if input is JSON or plain text ---
        try:
            # Try parsing as JSON first
            parsed = json.loads(job_description)
            # If it has job_description key, use JSON body
            if isinstance(parsed, dict) and "job_description" in parsed:
                payload = parsed
                headers = {"Content-Type": "application/json"}
            else:
                # JSON-like but not the right structure
                payload = job_description
                headers = {"Content-Type": "text/plain"}
        except json.JSONDecodeError:
            # Raw text (not JSON)
            payload = job_description
            headers = {"Content-Type": "text/plain"}

        # --- Make the request ---
        response = requests.post(url, data=payload if isinstance(payload, str) else None,
                                 json=payload if isinstance(payload, dict) else None,
                                 headers=headers, timeout=1800)
        response.raise_for_status()

        # --- Return plain text output ---
        return response.text.strip()

    except requests.exceptions.RequestException as e:
        return f"❌ Error calling resume agent: {str(e)}"