"""
Market-of-One Guardrails
- Hard monthly spend cap ($5 default)
- IP rate limiting (3 sessions/IP/day)
- Daily session counter
All state stored in data/usage.json — resets monthly/daily automatically.
"""
import json, os
from datetime import datetime, date

USAGE_FILE = "data/usage.json"
MONTHLY_LIMIT_USD = float(os.environ.get("MONTHLY_LIMIT_USD", "5.0"))
IP_DAILY_LIMIT = int(os.environ.get("IP_DAILY_LIMIT", "3"))

# Gemini 2.0 Flash pricing (per 1M tokens, ~$0.10 input + $0.40 output)
# Rough estimate per session: ~2000 tokens total → $0.0006 per session
COST_PER_SESSION_USD = 0.001  # conservative estimate


def _load() -> dict:
    if not os.path.exists(USAGE_FILE):
        return _empty()
    try:
        with open(USAGE_FILE) as f:
            return json.load(f)
    except:
        return _empty()


def _empty() -> dict:
    now = datetime.utcnow()
    return {
        "month": now.strftime("%Y-%m"),
        "today": str(date.today()),
        "monthly_sessions": 0,
        "monthly_cost_usd": 0.0,
        "daily_sessions": 0,
        "ip_counts": {}  # ip -> {date: str, count: int}
    }


def _save(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _reset_if_needed(data: dict) -> dict:
    now = datetime.utcnow()
    current_month = now.strftime("%Y-%m")
    current_day = str(date.today())

    if data.get("month") != current_month:
        data["month"] = current_month
        data["monthly_sessions"] = 0
        data["monthly_cost_usd"] = 0.0

    if data.get("today") != current_day:
        data["today"] = current_day
        data["daily_sessions"] = 0
        data["ip_counts"] = {}

    return data


def check_and_record(ip: str) -> tuple[bool, str]:
    """
    Returns (allowed: bool, reason: str).
    If allowed, also records the session.
    """
    data = _load()
    data = _reset_if_needed(data)

    # 1. Monthly spend cap
    if data["monthly_cost_usd"] >= MONTHLY_LIMIT_USD:
        return False, f"Monthly limit of ${MONTHLY_LIMIT_USD} reached — running in demo mode."

    # 2. IP rate limit
    ip_record = data["ip_counts"].get(ip, {"date": "", "count": 0})
    if ip_record.get("date") == str(date.today()):
        if ip_record["count"] >= IP_DAILY_LIMIT:
            return False, f"Daily limit of {IP_DAILY_LIMIT} live sessions per visitor reached — running in demo mode."
    else:
        ip_record = {"date": str(date.today()), "count": 0}

    # Record session
    ip_record["count"] += 1
    data["ip_counts"][ip] = ip_record
    data["monthly_sessions"] += 1
    data["daily_sessions"] += 1
    data["monthly_cost_usd"] = round(data["monthly_cost_usd"] + COST_PER_SESSION_USD, 4)

    _save(data)
    return True, "ok"


def get_stats() -> dict:
    data = _load()
    data = _reset_if_needed(data)
    return {
        "month": data["month"],
        "today": data["today"],
        "monthly_sessions": data["monthly_sessions"],
        "daily_sessions": data["daily_sessions"],
        "monthly_cost_usd": round(data["monthly_cost_usd"], 4),
        "monthly_limit_usd": MONTHLY_LIMIT_USD,
        "budget_remaining_usd": round(max(0, MONTHLY_LIMIT_USD - data["monthly_cost_usd"]), 4),
        "budget_pct_used": round((data["monthly_cost_usd"] / MONTHLY_LIMIT_USD) * 100, 1)
    }
