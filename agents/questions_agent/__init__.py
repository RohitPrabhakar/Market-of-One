"""
Market-of-One Questions Agent
---------------------
Takes a business profile + owner-provided context
(common customers, top services, frequent questions)
and generates 3 smart, business-specific visitor
onboarding questions with answer options.

These replace the generic questions and make the
Context Agent immediately more intelligent — because
the questions themselves are already personalized.
"""

import json


SYSTEM_PROMPT = """You are the Market-of-One Questions Agent.

A business owner has loaded their business into the Market-of-One system. 
Your job: generate exactly 3 onboarding questions to ask their website visitors.

These questions must:
- Be specific to THIS business (not generic)
- Help the Page Agent understand what the visitor needs
- Have 3-4 short answer options each (not yes/no)
- Feel natural, not like a form
- Progress from "who are you" → "what do you need" → "how urgent"

Use the business profile AND the owner's context notes to make them highly relevant.

Return ONLY valid JSON:
{
  "questions": [
    {
      "id": "q1",
      "text": string (the question — conversational, not corporate),
      "purpose": string (what this tells the Context Agent — internal note),
      "options": [string, string, string, string] (3-4 short answer options)
    },
    {
      "id": "q2", 
      "text": string,
      "purpose": string,
      "options": [string, string, string]
    },
    {
      "id": "q3",
      "text": string (this one is always open-ended, no options — let them type),
      "purpose": string,
      "options": []
    }
  ],
  "journey_framing": string (1 sentence intro shown above the questions — e.g. "Tell us a bit about yourself so we can show you exactly what you need.")
}"""


def run(business_profile: dict, owner_context: str) -> dict:
    from openai import OpenAI
    client = OpenAI()
    """
    Generate business-specific visitor questions.

    Args:
        business_profile: Output from Scraper Agent
        owner_context: Free text from business owner about their customers,
                       top services, and common questions they receive

    Returns:
        Dict with 3 custom questions and answer options
    """
    user_message = f"""
BUSINESS PROFILE:
{json.dumps(business_profile, indent=2)}

OWNER'S CONTEXT (what they shared about their customers and business):
{owner_context}

Generate 3 smart visitor questions specific to this business.
Make Q1 identify who they are (using THIS business's customer types).
Make Q2 identify what they need (using THIS business's actual services).
Make Q3 open-ended — what are they trying to solve or achieve.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.4,
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    result["_agent"] = "questions_agent"
    result["_generated_from"] = business_profile.get("business_name", "unknown")
    return result
