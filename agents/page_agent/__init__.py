"""
Market-of-One Page Agent
Generates a fully personalized page structure for a single visitor.
"""
import json
from utils.gemini import generate

SYSTEM_PROMPT = """You are the Market-of-One Page Agent.
Given a visitor context profile and a business profile, generate a complete personalized page.

Return ONLY valid JSON:
{
  "hero": {
    "greeting": string (e.g. "Hi there" or use name if known),
    "headline": string (speaks directly to their need — not generic tagline),
    "subheadline": string (addresses their specific situation),
    "primary_cta": string
  },
  "insight": {
    "headline": string ("Here's what we think you need" style),
    "body": string (2-3 sentences — explain why this business fits their situation)
  },
  "recommended": [
    {
      "name": string,
      "match_reason": string (why THIS visitor needs THIS service),
      "description": string,
      "cta": string
    }
  ],
  "proof_points": [string, string, string],
  "next_step": {
    "headline": string,
    "body": string (remove friction — speak to their urgency level),
    "cta": string,
    "secondary_cta": string
  },
  "personalization_note": string (internal — explain choices made)
}"""

def run(visitor_context: dict, business_profile: dict) -> dict:
    user_msg = f"VISITOR CONTEXT:\n{json.dumps(visitor_context, indent=2)}\n\nBUSINESS PROFILE:\n{json.dumps(business_profile, indent=2)}"
    result = generate(SYSTEM_PROMPT, user_msg, temperature=0.6)
    result["_agent"] = "page_agent"
    return result
