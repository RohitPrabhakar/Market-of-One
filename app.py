"""
Market-of-One — Living Personalization System
https://github.com/RohitPrabhakar/Market-of-One
"""
from flask import Flask, render_template, jsonify, request, session
import json, os, uuid, time
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "market-of-one-dev-key-change-in-prod")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
LIVE_MODE = bool(GEMINI_API_KEY and not GEMINI_API_KEY.startswith("your-"))
STATS_PASSWORD = os.environ.get("STATS_PASSWORD", "mot2026")

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


def get_client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()


# ── ERROR HANDLERS ────────────────────────────────────────────────────────────

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


# ── ROUTES ────────────────────────────────────────────────────────────────────

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


@app.route("/stats")
def stats():
    """Daily session counter — password protected."""
    pwd = request.args.get("key", "")
    if pwd != STATS_PASSWORD:
        return jsonify({"error": "Unauthorized — add ?key=your-password"}), 401
    from utils.guardrails import get_stats
    return jsonify(get_stats())


# ── API ───────────────────────────────────────────────────────────────────────

@app.route("/api/scrape", methods=["POST"])
def scrape():
    if not LIVE_MODE:
        return jsonify({"error": "Requires GEMINI_API_KEY in environment variables."}), 400

    data = request.get_json()
    url = data.get("url", "").strip()
    owner_context = data.get("owner_context", "").strip()
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        from agents.scraper_agent import run as scrape_run
        from agents.questions_agent import run as questions_run
        profile = scrape_run(url)
        profile["visitor_questions"] = questions_run(profile, owner_context)
        profile["owner_context"] = owner_context
        biz_id = save_business(profile)
        return jsonify({"biz_id": biz_id, "profile": profile})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    biz_id = data.get("biz_id") or session.get("biz_id")
    answers = data.get("answers", {})

    if not biz_id:
        return jsonify({"error": "No business selected"}), 400
    biz = get_business(biz_id)
    if not biz:
        return jsonify({"error": "Business not found"}), 404

    visitor_id = str(uuid.uuid4())[:8]

    # Demo mode — no key
    if not LIVE_MODE:
        return jsonify(build_mock_page(answers, biz, visitor_id))

    # Guardrails check
    from utils.guardrails import check_and_record
    ip = get_client_ip()
    allowed, reason = check_and_record(ip)

    if not allowed:
        result = build_mock_page(answers, biz, visitor_id)
        result["_notice"] = reason
        return jsonify(result)

    # Live AI generation
    try:
        return generate_live(answers, biz, visitor_id)
    except Exception as e:
        err = str(e)
        result = build_mock_page(answers, biz, visitor_id)
        result["_notice"] = f"Fell back to demo mode: {err[:120]}"
        return jsonify(result)


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
    q_vals = list(answers.values())
    need = q_vals[1] if len(q_vals) > 1 else "learn more"
    free_text = q_vals[2] if len(q_vals) > 2 else ""
    svcs = biz.get("products_services", [])
    return {
        "visitor_id": visitor_id, "mode": "mock",
        "context": {
            "name": "there", "primary_need": need,
            "moment_of_need": f"Visitor wants to {need}",
            "context_summary": f"Exploring {biz['business_name']} for: {need}. {free_text}",
            "sophistication": "intermediate", "urgency": "evaluating",
            "emotional_state": "curious", "intent_score": 65
        },
        "page": {
            "hero": {
                "greeting": "Hi there",
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
            "personalization_note": "Add GEMINI_API_KEY for real AI personalization"
        },
        "business": biz,
        "latency": {"context_ms": 0, "page_ms": 0, "total_ms": 0}
    }


if __name__ == "__main__":
    label = "LIVE MODE" if LIVE_MODE else "DEMO MODE (no API key)"
    port = int(os.environ.get("PORT", 5000))
    print(f"\n Market-of-One · {label}  →  http://localhost:{port}")
    print(f" Stats →  http://localhost:{port}/stats?key={STATS_PASSWORD}\n")
    app.run(debug=False, host="0.0.0.0", port=port)
