"""
Market-of-One — Gemini 2.0 Flash client
Uses google-genai (new SDK, replaces google-generativeai)
"""
import os, json
from google import genai
from google.genai import types

MODEL = "gemini-2.0-flash"

def generate(system_prompt: str, user_message: str, temperature: float = 0.4) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)
    full_prompt = f"{system_prompt}\n\n{user_message}"

    response = client.models.generate_content(
        model=MODEL,
        contents=full_prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json"
        )
    )
    return json.loads(response.text)
