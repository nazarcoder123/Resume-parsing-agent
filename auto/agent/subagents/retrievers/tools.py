import json
from pydantic import BaseModel, Field

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