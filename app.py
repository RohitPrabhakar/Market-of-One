"""
Market-of-One — Market-of-One Living System
https://github.com/rohitprabhakar/market-of-one
"""
from flask import Flask, render_template, jsonify, request, session
import json, os, uuid, time
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "market-of-one-dev-key-change-in-prod")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
LIVE_MODE = bool(OPENAI_API_KEY and not OPENAI_API_KEY.startswith("sk-your"))

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

with open("data/demo_businesses.json") as f:
    DEMO_BUSINESSES = json.load(f)

BUSINESSES_DIR = "data/businesses"
os.makedirs(BUSINESSES_DIR, exist_ok=True)


def get_business(biz_id):
    if biz_id in DEMO_BUSINESSES:
        return DEMO_BUSINESSES[biz_id]
    path = f"{BUSINESSES_DIR}/{biz_id}.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def save_business(profile):
    biz_id = str(uuid.uuid4())[:8]
    with open(f"{BUSINESSES_DIR}/{biz_id}.json", "w") as f:
        json.dump(profile, f, indent=2)
    return biz_id


# ── ROUTES ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    demos = [
        {"id": k, "name": v["business_name"], "tagline": v["tagline"], "industry": v["industry"]}
        for k, v in DEMO_BUSINESSES.items()
    ]
    return render_template("index.html", demos=demos, live_mode=LIVE_MODE)


@app.route("/setup")
def setup():
    return render_template("setup.html", live_mode=LIVE_MODE)


@app.route("/visit/<biz_id>")
def visit(biz_id):
    biz = get_business(biz_id)
    if not biz:
        return "Business not found.", 404
    session["biz_id"] = biz_id
    questions = biz.get("visitor_questions", None)
    return render_template("visitor.html", business=biz, biz_id=biz_id,
                           questions=questions, live_mode=LIVE_MODE)


# ── API ──────────────────────────────────────────────────────────────────────

@app.route("/api/scrape", methods=["POST"])
def scrape():
    """Step 1: Read URL + owner context → business profile + custom questions."""
    if not LIVE_MODE:
        return jsonify({"error": "Scraping requires an OpenAI API key. Add it to .env"}), 400

    data = request.get_json()
    url = data.get("url", "").strip()
    owner_context = data.get("owner_context", "").strip()

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        from agents.scraper_agent import run as scrape_run
        from agents.questions_agent import run as questions_run

        # Step 1: Scrape the URL
        profile = scrape_run(url)

        # Step 2: Generate business-specific questions
        visitor_questions = questions_run(profile, owner_context)
        profile["visitor_questions"] = visitor_questions
        profile["owner_context"] = owner_context

        # Save
        biz_id = save_business(profile)
        return jsonify({"biz_id": biz_id, "profile": profile})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate", methods=["POST"])
def generate():
    """Step 2: Visitor answers → context → personalized page."""
    data = request.get_json()
    biz_id = data.get("biz_id") or session.get("biz_id")
    answers = data.get("answers", {})

    if not biz_id:
        return jsonify({"error": "No business selected"}), 400

    biz = get_business(biz_id)
    if not biz:
        return jsonify({"error": "Business not found"}), 404

    visitor_id = str(uuid.uuid4())[:8]

    try:
        if not LIVE_MODE:
            return jsonify(build_mock_page(answers, biz, visitor_id))
        return generate_live(answers, biz, visitor_id)
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


def generate_live(answers, biz, visitor_id):
    from agents.context_agent import run as context_run
    from agents.page_agent import run as page_run

    t0 = time.time()
    visitor_context = context_run(answers, visitor_id)
    ctx_ms = round((time.time() - t0) * 1000)

    t1 = time.time()
    page_content = page_run(visitor_context, biz)
    page_ms = round((time.time() - t1) * 1000)

    return jsonify({
        "visitor_id": visitor_id, "mode": "live",
        "context": visitor_context,
        "page": page_content,
        "business": biz,
        "latency": {"context_ms": ctx_ms, "page_ms": page_ms, "total_ms": ctx_ms + page_ms}
    })


def build_mock_page(answers, biz, visitor_id):
    """Demo mode fallback — no API key needed."""
    q_vals = list(answers.values())
    name_guess = "there"
    need = q_vals[1] if len(q_vals) > 1 else "learn more"
    free_text = q_vals[2] if len(q_vals) > 2 else ""
    svcs = biz.get("products_services", [])
    return {
        "visitor_id": visitor_id, "mode": "mock",
        "context": {
            "name": name_guess, "primary_need": need,
            "moment_of_need": f"Visitor wants to {need}",
            "context_summary": f"Exploring {biz['business_name']} for: {need}. {free_text}",
            "sophistication": "intermediate", "urgency": "evaluating",
            "emotional_state": "curious", "intent_score": 65
        },
        "page": {
            "hero": {
                "greeting": f"Hi there",
                "headline": biz["tagline"],
                "subheadline": biz["what_they_do"],
                "primary_cta": biz["cta_primary"]
            },
            "insight": {
                "headline": "Here's what we think you need",
                "body": f"Based on what you shared, {biz['what_they_do']}"
            },
            "recommended": [
                {"name": s["name"], "match_reason": "Recommended for your situation",
                 "description": s["description"], "cta": "Learn more →"}
                for s in svcs[:2]
            ],
            "proof_points": biz.get("key_benefits", [])[:3],
            "next_step": {
                "headline": "Ready to take the next step?",
                "body": "No commitment needed. Let's start with a conversation.",
                "cta": biz["cta_primary"],
                "secondary_cta": "Learn more first"
            },
            "personalization_note": "Add OpenAI key for real AI personalization"
        },
        "business": biz,
        "latency": {"context_ms": 0, "page_ms": 0, "total_ms": 0}
    }


if __name__ == "__main__":
    label = "LIVE MODE" if LIVE_MODE else "DEMO MODE (no API key)"
    port = int(os.environ.get("PORT", 5000))
    print(f"\n Market-of-One · {label}  →  http://localhost:{port}\n")
    app.run(debug=False, host="0.0.0.0", port=port)
