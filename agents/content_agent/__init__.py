"""
Market-of-One Content Agent
------------------
Cerebellum layer of the Living System.

Receives the Context Agent's profile and generates a
hyper-personalized message — unique to this individual,
calibrated to their emotional state, communication style,
and moment of need.

This is NOT a template. This is NOT a variant of a segment.
This is content written for a market of one.

In-Flow AI principle: Content is generated and delivered
inline, at the exact moment the signal fires — no campaign
manager, no approval cycle, no queue.
"""

import json



SYSTEM_PROMPT = """You are the Content Agent inside the Market-of-One Living System.

You receive a real-time customer context profile from the Context Agent
and generate a hyper-personalized outreach message.

Rules:
- Write for ONE person, not a segment
- Match their exact communication style and emotional state
- Address their specific moment of need, not a generic use case
- Keep the subject line under 9 words
- Keep the message under 120 words — precision over volume
- Do NOT use generic phrases like "I hope this finds you well"
- Sound like a trusted advisor, not a marketing email

Return ONLY valid JSON. No markdown fences.

Output schema:
{
  "subject_line": string,
  "message_body": string,
  "call_to_action": string (short, specific, one action only),
  "channel": string (where to send this),
  "urgency": string ("immediate" | "within_24h" | "within_week"),
  "personalization_rationale": string (why THIS message for THIS person — 1 sentence),
  "in_flow_trigger": string (what workflow event should fire this message)
}"""


def run(context_profile: dict, customer: dict) -> dict:
    client = OpenAI()
    """
    Generate a hyper-personalized message from context profile.
    
    Args:
        context_profile: Output from Context Agent
        customer: Original customer record (for preference reference)
        
    Returns:
        Personalized content package dict
    """
    user_message = f"""
Generate a hyper-personalized message based on this context profile:

Real-Time Profile:
{json.dumps(context_profile, indent=2)}

Customer Preferences:
- Communication Style: {customer['communication_style']}
- Preferred Channel: {customer['preferences']['channel']}
- Preferred Tone: {customer['preferences']['tone']}

The moment of need is: {context_profile.get('moment_of_need', 'unknown')}
The recommended action type is: {context_profile.get('recommended_action_type', 'engage')}
The customer's emotional state is: {context_profile.get('emotional_state', 'neutral')}

Write the message now. Make it feel like it was written only for {customer['name']}.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )

    raw = response.choices[0].message.content
    content = json.loads(raw)
    content["_agent"] = "content_agent"
    content["_model"] = "gpt-4o-mini"
    return content
