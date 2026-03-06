"""
Market-of-One Page Agent
---------------
The heart of the Market-of-One experience.

Takes a visitor's context profile + the business's
knowledge base and generates a complete, personalized
multi-section page — rebuilt from scratch for this
specific person's needs.

In-Flow AI: The page is generated at the moment the
visitor completes onboarding. It exists for them alone.
"""

import json


SYSTEM_PROMPT = """You are the Market-of-One Page Agent — a hyper-personalization engine.

You receive:
1. A visitor's context profile (who they are, what they need right now)
2. A business's knowledge base (their products, services, benefits)

Your job: generate a complete personalized webpage — rebuilt specifically for this visitor.

Rules:
- Every headline should speak directly to THIS person's situation
- Recommend only products/services relevant to their stated need
- Use language that matches their sophistication level
- The experience should feel like the business already knew them
- Be specific — use real product names, real benefits, not generic copy

Return ONLY valid JSON:
{
  "hero": {
    "greeting": string (personal, 3-6 words, uses their name if available),
    "headline": string (their need + the solution, 8-12 words),
    "subheadline": string (1-2 sentences that speak to their specific situation),
    "primary_cta": string (specific action, 3-5 words)
  },
  "insight": {
    "headline": string ("Here's what we think you need" — personalized),
    "body": string (2-3 sentences explaining why this solution fits their situation)
  },
  "recommended": [
    {
      "name": string (real product/service name),
      "match_reason": string (why this fits THIS visitor specifically),
      "description": string (1-2 sentences),
      "cta": string (specific action)
    }
  ],
  "proof_points": [string] (3 specific reasons this business can solve their problem),
  "next_step": {
    "headline": string (action-oriented, personal),
    "body": string (1-2 sentences removing friction),
    "cta": string (primary action),
    "secondary_cta": string (lower-commitment option)
  },
  "personalization_note": string (internal — why you made these choices, 1 sentence)
}"""


def run(visitor_context: dict, business_profile: dict) -> dict:
    from openai import OpenAI
    client = OpenAI()
    """
    Generate a complete personalized page for one visitor.

    Args:
        visitor_context: Output from Context Agent (visitor profile)
        business_profile: Output from Scraper Agent (business knowledge base)

    Returns:
        Full personalized page content dict
    """
    user_message = f"""
VISITOR CONTEXT:
{json.dumps(visitor_context, indent=2)}

BUSINESS KNOWLEDGE BASE:
{json.dumps(business_profile, indent=2)}

Generate a complete personalized page for {visitor_context.get('name', 'this visitor')}.
Their primary need: {visitor_context.get('moment_of_need', 'unknown')}
Their situation: {visitor_context.get('context_summary', 'unknown')}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.6,
        response_format={"type": "json_object"}
    )

    page = json.loads(response.choices[0].message.content)
    page["_agent"] = "page_agent"
    page["_visitor_id"] = visitor_context.get("visitor_id", "unknown")
    return page
