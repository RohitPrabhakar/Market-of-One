"""
Market-of-One Scraper Agent
Reads any website URL and extracts a structured business profile.
"""
import requests, json
from bs4 import BeautifulSoup
from utils.gemini import generate

SYSTEM_PROMPT = """You are the Market-of-One Scraper Agent.
Extract a structured business profile from this website content.

Return ONLY valid JSON:
{
  "business_name": string,
  "tagline": string,
  "what_they_do": string (2-3 sentences),
  "industry": string,
  "target_customers": [string],
  "products_services": [
    {"name": string, "description": string, "best_for": string}
  ],
  "key_benefits": [string],
  "tone": string (e.g. "professional", "warm", "bold"),
  "cta_primary": string,
  "contact_or_url": string
}"""

def run(url: str) -> dict:
    resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)[:4000]
    result = generate(SYSTEM_PROMPT, f"Website URL: {url}\n\nContent:\n{text}")
    result["source_url"] = url
    result["_agent"] = "scraper_agent"
    return result
