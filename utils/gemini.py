"""
Shared Gemini 2.0 Flash client — one place to swap models.
All agents import generate() from here.
"""
import os, json
import google.generativeai as genai

MODEL = "gemini-2.0-flash"

def generate(system_prompt: str, user_message: str, temperature: float = 0.4) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=MODEL,
        generation_config={
            "response_mime_type": "application/json",
            "temperature": temperature
        }
    )
    response = model.generate_content(f"{system_prompt}\n\n{user_message}")
    return json.loads(response.text)
