# Market-of-One™

> *Every visitor gets a page built just for them.*

[![License](https://img.shields.io/badge/License-Apache_2.0-orange.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)

**Market-of-One** is an open-source proof-of-concept for hyper-personalization at the individual level. Load any business. Any visitor who arrives gets a page written specifically for them — based on who they are, what they need, and what they do while they're there.

This is the working prototype behind the [Market-of-One™ framework](https://rohitprabhakar.com/market-of-one/) by Rohit Prabhakar.

---

## What It Does

1. **Business owner** enters their URL → system scrapes the site and generates 3 custom onboarding questions
2. **Shareable link** is created for that business
3. **Visitor** answers 3 questions → AI builds a personalized page from scratch — headline, insight, recommendations, proof, CTAs — written for that specific person
4. **Page adapts in real time** as the visitor interacts — up to 6 injected sections per session based on live behavioral signals

No templates. No segments. No pre-built content library.
**Understand → Generate.** That's the Market-of-One.

---

## The Three-Layer Stack

| Layer | What It Does | Technology |
|-------|-------------|------------|
| **Know Them** | Visitor answers + behavioral signals | CDP, event streaming |
| **Understand Them** | Context Agent infers intent, urgency, emotional state | Gemini 2.0 Flash |
| **Build For Them** | Page Agent generates content on the fly — no templates | Gemini 2.0 Flash |

The third layer — generative content on the fly — is the unlock that makes Market-of-One possible. [Read the full thesis →](https://rohitprabhakar.com/the-broken-promise/)

---

## Live Demo

Three demo businesses work without any API key:

| Business | Industry | Link |
|----------|----------|------|
| PeakForm Studio | Fitness | `/visit/demo_fitness` |
| Flowdesk CRM | SaaS | `/visit/demo_saas` |
| Kindred Creative | Agency | `/visit/demo_agency` |

---

## Quick Start

```bash
git clone https://github.com/RohitPrabhakar/Market-of-One
cd Market-of-One
pip install -r requirements.txt
cp .env.example .env
# Add GEMINI_API_KEY to .env (get free at aistudio.google.com)
python app.py
```

Open `http://localhost:5000`

---

## Deploy to Railway

1. Fork this repo
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select your fork
4. Add environment variables (see below)

---

## Architecture

```
app.py                        Flask routes + demo mode fallback
├── agents/
│   ├── scraper_agent/        URL → structured business profile
│   ├── questions_agent/      Business profile → 3 custom onboarding questions
│   ├── context_agent/        Visitor answers → real-time context profile
│   ├── page_agent/           Context → full personalized page JSON
│   ├── adaptation_agent/     Behavioral signals → next injected section
│   ├── ethics_agent/         [Coming soon] Propensity-to-Annoy + guardrails
│   └── channel_agent/        [Coming soon] Optichannel routing
├── utils/
│   ├── gemini.py             Shared Gemini 2.0 Flash client
│   └── guardrails.py         Spend cap + IP rate limiting
└── templates/
    ├── index.html            Homepage
    ├── setup.html            Business owner setup
    └── visitor.html          Living adaptive page
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | From [aistudio.google.com](https://aistudio.google.com) — billing required |
| `MONTHLY_LIMIT_USD` | `5.0` | Hard spend cap — auto-falls back to demo at limit |
| `IP_DAILY_LIMIT` | `3` | Max live sessions per visitor per day |
| `STATS_PASSWORD` | `mot2026` | Password for `/stats` endpoint |
| `SECRET_KEY` | dev key | Flask session secret — change in production |

**Cost:** ~$0.001/session. $5 budget ≈ 5,000 live sessions.

---

## Two Modes

**Demo mode** (no API key) — uses visitor answers to vary headline, insight, and service matching. No AI calls. Works immediately.

**Live mode** (with `GEMINI_API_KEY`) — Full 3-agent pipeline: Context Agent → Page Agent → Adaptation Agent, all calling Gemini 2.0 Flash.

---

## Contributing

The Ethics Agent and Channel Agent are open for contributions. See the stub files for the planned interfaces.

Issues are labeled `[ethics-agent]` and `[channel-agent]`.

---

## The Framework

This repo is the working prototype of the **Market-of-One™** framework — a leadership and deployment model for building AI-driven, individually personalized customer systems across Marketing, Sales, and Service.

📖 [Read the article series →](https://rohitprabhakar.com/market-of-one/)

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
Copyright 2026 [Rohit Prabhakar](https://rohitprabhakar.com)

You are free to use, modify, and distribute this code. Attribution must be preserved. The Market-of-One™ name and framework are proprietary to Rohit Prabhakar.
