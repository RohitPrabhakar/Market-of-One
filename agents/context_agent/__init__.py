"""
Market-of-One Context Agent
Synthesizes visitor onboarding answers into a real-time context profile.
"""
import json, uuid
from utils.gemini import generate

SYSTEM_PROMPT = """You are the Market-of-One Context Agent. A visitor answered 3 onboarding questions.
Build their real-time context profile to drive personalized page generation.

Return ONLY valid JSON:
{
  "visitor_id": string,
  "name": string (if given, else "there"),
  "intent_score": integer (0-100),
  "primary_need": string,
  "moment_of_need": string (specific — what do they need RIGHT NOW),
  "situation": string (individual / small business / enterprise / exploring),
  "sophistication": string ("beginner" | "intermediate" | "expert"),
  "urgency": string ("exploring" | "evaluating" | "ready_to_act"),
  "emotional_state": string ("curious" | "frustrated" | "overwhelmed" | "excited"),
  "context_summary": string (2 sentences max),
  "recommended_journey": string ("quick_win" | "deep_dive" | "comparison" | "getting_started")
}"""

def run(answers: dict, visitor_id: str = None) -> dict:
    if not visitor_id:
        visitor_id = str(uuid.uuid4())[:8]
    answers_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in answers.items()])
    result = generate(SYSTEM_PROMPT, f"Visitor ID: {visitor_id}\n\nAnswers:\n{answers_text}", temperature=0.3)
    result["visitor_id"] = visitor_id
    result["_agent"] = "context_agent"
    return result
