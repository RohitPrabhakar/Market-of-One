"""
Market-of-One Scraper Agent
------------------
Reads a business URL and extracts a structured profile:
name, what they do, products/services, value props, tone.

This becomes the "knowledge base" that the Page Agent
uses to build personalized experiences.
"""

import requests
from bs4 import BeautifulSoup
import json, re


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

SYSTEM_PROMPT = """You are a business intelligence agent. Given raw text scraped from a business website, 
extract a clean structured profile. Be specific — pull real product names, real services, real value props.

Return ONLY valid JSON:
{
  "business_name": string,
  "tagline": string (their core value prop in one line),
  "what_they_do": string (2-3 sentences, plain English),
  "industry": string,
  "target_customers": [string] (who they serve — be specific),
  "products_services": [
    {
      "name": string,
      "description": string (1-2 sentences),
      "best_for": string (who this is for)
    }
  ],
  "key_benefits": [string] (3-5 specific benefits, not generic fluff),
  "tone": string (e.g. "professional", "casual", "technical", "warm"),
  "cta_primary": string (their main call to action),
  "contact_or_url": string
}"""


def scrape_url(url: str) -> str:
    """Fetch and clean text content from a URL."""
    if not url.startswith("http"):
        url = "https://" + url

    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove noise
    for tag in soup(["script", "style", "nav", "footer", "iframe", "noscript"]):
        tag.decompose()

    # Get meaningful text
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r'\s+', ' ', text)

    # Limit to ~3000 chars — enough for OpenAI to understand the business
    return text[:3000]


def run(url: str) -> dict:
    from openai import OpenAI
    client = OpenAI()
    """
    Scrape a URL and return a structured business profile.

    Args:
        url: Business website URL

    Returns:
        Structured business profile dict
    """
    raw_text = scrape_url(url)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Website URL: {url}\n\nScraped content:\n{raw_text}"}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    profile = json.loads(response.choices[0].message.content)
    profile["source_url"] = url
    profile["_agent"] = "scraper_agent"
    return profile
