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
    {"name": string, "description": string, "best_for": string, "outcome": string, "price": string}
  ],
  "key_benefits": [string],
  "testimonials": [{"name": string, "result": string}],
  "tone": string,
  "cta_primary": string,
  "cta_url": string,
  "contact_or_url": string
}"""


def run(url: str) -> dict:
    # Ensure URL has scheme
    if not url.startswith("http"):
        url = "https://" + url

    try:
        resp = requests.get(
            url, timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (compatible; Market-of-One/1.0)"},
            allow_redirects=True
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "iframe"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)[:5000]
    except requests.exceptions.Timeout:
        raise ValueError(f"Could not reach {url} — site timed out after 15s")
    except requests.exceptions.ConnectionError:
        raise ValueError(f"Could not connect to {url} — check the URL and try again")
    except Exception as e:
        raise ValueError(f"Failed to fetch {url}: {str(e)}")

    result = generate(SYSTEM_PROMPT, f"Website URL: {url}\n\nContent:\n{text}")
    result["source_url"] = url
    result["contact_or_url"] = result.get("contact_or_url") or url
    result["cta_url"] = result.get("cta_url") or url
    result["_agent"] = "scraper_agent"
    return result
