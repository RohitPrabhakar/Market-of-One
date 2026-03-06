"""
Market-of-One Context Agent — Visitor Edition
--------------------------------------
Synthesizes a visitor's onboarding answers into a
real-time context profile that drives page generation.
"""

import json, uuid


SYSTEM_PROMPT = """You are the Market-of-One Context Agent. A visitor just answered 3 onboarding questions.
Build their real-time context profile so the Page Agent can generate a personalized experience.

Return ONLY valid JSON:
{
  "visitor_id": string (use the one provided),
  "name": string (if they gave one, otherwise "there"),
  "intent_score": integer (0-100, how ready to act are they),
  "primary_need": string (the core thing they came here for),
  "moment_of_need": string (what does this person need RIGHT NOW, be specific),
  "situation": string (their context — individual, small business, enterprise, etc.),
  "sophistication": string ("beginner" | "intermediate" | "expert"),
  "urgency": string ("exploring" | "evaluating" | "ready_to_act"),
  "emotional_state": string (e.g. "curious", "frustrated", "overwhelmed", "excited"),
  "context_summary": string (2 sentences max — brief for the Page Agent),
  "recommended_journey": string ("quick_win" | "deep_dive" | "comparison" | "getting_started")
}"""


def run(answers: dict, visitor_id: str = None) -> dict:
    from openai import OpenAI
    client = OpenAI()
    if not visitor_id:
        visitor_id = str(uuid.uuid4())[:8]

    answers_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in answers.items()])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Visitor ID: {visitor_id}\n\nOnboarding answers:\n{answers_text}"}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    profile = json.loads(response.choices[0].message.content)
    profile["visitor_id"] = visitor_id
    profile["_agent"] = "context_agent"
    return profile
