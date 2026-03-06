"""
Market-of-One Questions Agent
Generates 3 business-specific visitor onboarding questions.
"""
import json
from utils.gemini import generate

SYSTEM_PROMPT = """You are the Market-of-One Questions Agent.
Generate exactly 3 onboarding questions for visitors to this specific business.

Rules:
- Q1: Who are they (use THIS business's customer types as options)
- Q2: What do they need (use THIS business's actual services as options)  
- Q3: Always open-ended — let them type freely

Return ONLY valid JSON:
{
  "journey_framing": string (1 sentence intro shown above questions),
  "questions": [
    {
      "id": "q1",
      "text": string,
      "purpose": string (internal note for Context Agent),
      "options": [string, string, string, string]
    },
    {
      "id": "q2",
      "text": string,
      "purpose": string,
      "options": [string, string, string]
    },
    {
      "id": "q3",
      "text": string (open-ended),
      "purpose": string,
      "options": []
    }
  ]
}"""

def run(business_profile: dict, owner_context: str) -> dict:
    user_msg = f"BUSINESS PROFILE:\n{json.dumps(business_profile, indent=2)}\n\nOWNER CONTEXT:\n{owner_context}"
    result = generate(SYSTEM_PROMPT, user_msg, temperature=0.4)
    result["_agent"] = "questions_agent"
    result["_generated_from"] = business_profile.get("business_name", "unknown")
    return result
