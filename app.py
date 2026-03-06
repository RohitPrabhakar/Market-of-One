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


@app.route("/api/adapt", methods=["POST"])
def adapt():
    """Live page adaptation — receive a signal, return next content section."""
    data = request.get_json()
    biz_id = data.get("biz_id") or session.get("biz_id")
    visitor_context = data.get("visitor_context", {})
    signals = data.get("signals", [])
    injection_count = data.get("injection_count", 0)

    if not biz_id:
        return jsonify({"error": "No business selected"}), 400
    biz = get_business(biz_id)
    if not biz:
        return jsonify({"error": "Business not found"}), 404

    if injection_count >= 6:
        return jsonify({"done": True, "message": "Session complete"})

    if not LIVE_MODE:
        return jsonify(build_mock_adaptation(signals, biz, injection_count))

    from utils.guardrails import check_and_record
    ip = get_client_ip()
    allowed, _ = check_and_record(ip)
    if not allowed:
        return jsonify(build_mock_adaptation(signals, biz, injection_count))

    try:
        from agents.adaptation_agent import run as adapt_run
        section = adapt_run(visitor_context, signals, biz, injection_count)
        return jsonify({"section": section, "injection_count": injection_count + 1})
    except Exception as e:
        return jsonify(build_mock_adaptation(signals, biz, injection_count))


def build_mock_adaptation(signals, biz, injection_count):
    last_signal = signals[-1] if signals else {}
    signal_type = last_signal.get("type", "tell_more")
    section_type = "deep_dive"
    if signal_type == "not_relevant":
        section_type = "inline_question"
    elif signal_type == "free_text":
        section_type = "objection_handler"
    elif injection_count > 2:
        section_type = "quick_win"

    svcs = biz.get("products_services", [])
    svc = svcs[injection_count % len(svcs)] if svcs else {}

    sections = {
        "deep_dive": {
            "headline": f"More on {svc.get('name', 'our approach')}",
            "body": svc.get("description", biz.get("what_they_do", "")),
            "inline_element": {"type": "multiple_choice",
                               "question": "What matters most to you?",
                               "options": ["Speed of results", "Price", "Ease of getting started", "Proven track record"]},
            "cta": biz.get("cta_primary")
        },
        "inline_question": {
            "headline": "Let us recalibrate",
            "body": "We want to show you what's actually relevant. One quick question:",
            "inline_element": {"type": "multiple_choice",
                               "question": "What's closest to what you're looking for?",
                               "options": [s["name"] for s in svcs[:4]] if svcs else ["Option A", "Option B"]},
            "cta": None
        },
        "objection_handler": {
            "headline": "Here's what people usually wonder about",
            "body": f"The most common question we get: {biz.get('what_they_do', '')}",
            "inline_element": {"type": "free_text", "question": "What's holding you back?", "options": []},
            "cta": None
        },
        "quick_win": {
            "headline": "The easiest way to start",
            "body": f"No commitment needed. {biz.get('key_benefits', [''])[0] if biz.get('key_benefits') else ''}",
            "inline_element": {"type": "none", "question": "", "options": []},
            "cta": biz.get("cta_primary")
        }
    }

    content = sections.get(section_type, sections["deep_dive"])
    return {
        "section": {
            "section_type": section_type,
            **content,
            "rationale": "mock adaptation",
            "_agent": "mock"
        },
        "injection_count": injection_count + 1
    }


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
    """Demo mode — uses visitor answers to actually personalize content."""
    q_vals = list(answers.values())
    q1 = q_vals[0] if len(q_vals) > 0 else ""
    q2 = q_vals[1] if len(q_vals) > 1 else ""
    free_text = q_vals[2] if len(q_vals) > 2 else ""
    svcs = biz.get("products_services", [])

    # Match Q2 to best service
    matched_svc = svcs[0] if svcs else {}
    for s in svcs:
        keywords = (s.get("best_for", "") + " " + s.get("name", "")).lower()
        if any(w in keywords for w in q2.lower().split()):
            matched_svc = s
            break
    second_svc = next((s for s in svcs if s != matched_svc), svcs[1] if len(svcs) > 1 else matched_svc)

    # Personalize headline + insight from Q1/Q2
    q_combined = (q1 + " " + q2).lower()
    if any(w in q1.lower() for w in ["beginner", "haven't", "while", "years", "quit"]):
        headline = "You don't need to have it figured out. That's what we're here for."
        insight_body = ("Most people who come to us say exactly what you said. "
                        "Starting from scratch is actually easier than fixing bad habits. "
                        + matched_svc.get("best_for", ""))
    elif any(w in q_combined for w in ["stuck", "plateau", "inconsistent", "results"]):
        headline = "Inconsistency isn't a willpower problem. It's a system problem."
        insight_body = ("You're doing the work — the results just aren't matching the effort. "
                        "That gap almost always comes down to one missing piece. "
                        + matched_svc.get("best_for", ""))
    elif any(w in q_combined for w in ["injury", "recover", "pain", "return"]):
        headline = "Coming back after injury takes a different approach. We know how."
        insight_body = ("Returning from injury means your body needs a progression plan, not a generic program. "
                        + matched_svc.get("best_for", ""))
    elif any(w in q_combined for w in ["nutrition", "eat", "food", "diet"]):
        headline = "The exercise is working. The missing piece is what happens in the kitchen."
        insight_body = ("You already have the discipline to train. "
                        "Nutrition coaching is about building the same system around food. "
                        + matched_svc.get("best_for", ""))
    elif any(w in q_combined for w in ["weight", "lose", "fat"]):
        headline = "Sustainable results don't come from doing more — they come from doing the right things."
        insight_body = ("Weight loss that lasts is 30% training and 70% everything else. "
                        + matched_svc.get("best_for", ""))
    else:
        headline = biz.get("tagline", "")
        insight_body = matched_svc.get("best_for", biz.get("what_they_do", ""))

    def match_reason(svc):
        if free_text and len(free_text) > 5:
            return 'You mentioned "' + free_text[:55] + '..." — this fits'
        return svc.get("best_for", "")[:80] or "Matched to your situation"

    what_they_do = biz.get("what_they_do", "")[:200]
    benefits = biz.get("key_benefits", [])
    cta = biz.get("cta_primary", "Get started")
    benefit_line = benefits[1] if len(benefits) > 1 else ""

    return {
        "visitor_id": visitor_id,
        "mode": "mock",
        "context": {
            "name": "there",
            "primary_need": q2 or "learn more",
            "moment_of_need": q1 + " — looking for: " + q2,
            "context_summary": q1 + ". Needs: " + q2 + ". " + free_text,
            "sophistication": "beginner" if any(w in q1.lower() for w in ["beginner", "haven't", "while"]) else "intermediate",
            "urgency": "ready_to_act" if len(free_text) > 10 else "evaluating",
            "emotional_state": "frustrated" if any(w in q_combined for w in ["stuck", "failed", "tried"]) else "curious",
            "intent_score": 75 if free_text else 55
        },
        "page": {
            "hero": {
                "greeting": "Hi there",
                "headline": headline,
                "subheadline": what_they_do,
                "primary_cta": cta
            },
            "insight": {
                "headline": "Here's what we think is going on",
                "body": insight_body
            },
            "recommended": [
                {
                    "name": matched_svc.get("name", ""),
                    "match_reason": match_reason(matched_svc),
                    "description": matched_svc.get("description", ""),
                    "cta": "Learn more →"
                },
                {
                    "name": second_svc.get("name", ""),
                    "match_reason": second_svc.get("best_for", "")[:80],
                    "description": second_svc.get("description", ""),
                    "cta": "Learn more →"
                }
            ],
            "proof_points": benefits[:4],
            "next_step": {
                "headline": "The next step is simpler than you think",
                "body": cta + " — no commitment, no pressure. " + benefit_line,
                "cta": cta,
                "secondary_cta": "Visit website"
            }
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
