# Market-of-One™

> *Every customer is a market. This is the open-source engine that makes it real.*

[![License](https://img.shields.io/badge/License-Apache_2.0-orange.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Framework](https://img.shields.io/badge/Framework-ARCĀ™-gold)](https://rohitprabhakar.com/arca)

---

## What This Is

**Market-of-One** is the open-source reference implementation of the [ARCĀ Framework™](https://rohitprabhakar.com/arca) — the agentic architecture that transforms AI investment into connected data, personalized customer experience, and measurable revenue.

The philosophy is simple: the age of the segment is over. Every customer deserves an experience built specifically for them — their context, their moment, their need. [Read the Market-of-One manifesto →](https://rohitprabhakar.com/market-of-one)

The problem is execution. Believing in 1:1 personalization is easy. Building the architecture that delivers it at enterprise scale is not.

**ARCĀ is that architecture. This repo is its working engine.**

---

## The ARCĀ Framework

ARCĀ — **A**ssess · **A**rchitect · **C**ommand · **Ā**mplify — is a four-stage connective architecture that embeds agentic intelligence inside the workflows where revenue decisions actually happen.

```
Assess → Architect → Command → Amplify → (repeats, self-improving)
```

This repo implements the **Architect** stage — specifically the five-layer multi-agent ecosystem at the core of every ARCĀ deployment:

| ARCĀ Agent Layer | This Repo | What It Does |
|---|---|---|
| **Signal Agents** | `scraper_agent` + `questions_agent` | Capture who the visitor is and what they need |
| **Insight Agents** | `context_agent` | Infer intent, urgency, and emotional context in real time |
| **Action Agents** | `page_agent` | Generate a personalized page — headline, insight, CTA — for that individual |
| **Orchestration Agents** | `app.py` | Command the full pipeline end-to-end |
| **Guardian Agents** | `ethics_agent` + `guardrails.py` | Govern spend caps, rate limits, and ethical rails |

**The Amplify flywheel** is implemented via `adaptation_agent` — the page adapts in real time as the visitor behaves, feeding behavioral signal back into the engine.

[Explore the full ARCĀ Framework →](https://rohitprabhakar.com/arca)

---

## What It Does

1. **Business owner** enters their URL → Signal Agents scrape the site and generate 3 custom onboarding questions
2. **Shareable link** is created for that business
3. **Visitor** answers 3 questions → Insight Agent builds a real-time context profile
4. **Action Agent** generates a personalized page from scratch — no templates, no segments
5. **Page adapts** as the visitor interacts — up to 6 injected sections per session driven by live behavioral signals

No templates. No segments. No pre-built content library.  
**Understand → Generate → Amplify.** That is the Market-of-One engine.

---

## Architecture

```
app.py                          Orchestration layer — Flask routes + pipeline command
├── agents/
│   ├── scraper_agent/          Signal Layer — URL → structured business profile
│   ├── questions_agent/        Signal Layer — Business profile → 3 custom onboarding questions
│   ├── context_agent/          Insight Layer — Visitor answers → real-time context profile
│   ├── page_agent/             Action Layer — Context → full personalized page (no templates)
│   ├── adaptation_agent/       Amplify Layer — Behavioral signals → next injected section
│   ├── ethics_agent/           Guardian Layer — [Open for contribution] Propensity-to-Annoy + ethical rails
│   └── channel_agent/          Guardian Layer — [Open for contribution] Optichannel routing
├── utils/
│   ├── llm.py                  Provider-agnostic LLM client (swap any model)
│   └── guardrails.py           Spend cap + IP rate limiting
└── templates/
    ├── index.html              Homepage
    ├── setup.html              Business owner setup
    └── visitor.html            Living adaptive page
```

---

## AI Provider

This engine is **model-agnostic by design**. ARCĀ does not prescribe a model — it prescribes an architecture. The `utils/llm.py` client is designed to be swapped for any provider:

- Google Gemini
- Anthropic Claude
- OpenAI GPT
- Azure OpenAI
- Any OpenAI-compatible endpoint

The current reference implementation uses **Gemini 2.0 Flash**. Swap in your preferred provider by updating `utils/llm.py`.

---

## Live Demo

Three demo businesses work without any API key:

| Business | Industry | Link |
|---|---|---|
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
# Add your LLM API key to .env
python app.py
```

Open `http://localhost:5000`

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LLM_API_KEY` | — | Your LLM provider API key |
| `LLM_PROVIDER` | `gemini` | Active provider: `gemini`, `anthropic`, `openai` |
| `MONTHLY_LIMIT_USD` | `5.0` | Hard spend cap — auto-falls back to demo at limit |
| `IP_DAILY_LIMIT` | `3` | Max live sessions per visitor per day |
| `STATS_PASSWORD` | `mot2026` | Password for `/stats` endpoint |
| `SECRET_KEY` | dev key | Flask session secret — change in production |

**Cost:** ~$0.001/session. $5 budget ≈ 5,000 live sessions.

---

## Two Modes

**Demo mode** (no API key) — uses visitor answers to vary headline, insight, and service matching. No AI calls. Works immediately.

**Live mode** (with API key) — Full ARCĀ pipeline: Signal → Insight → Action → Amplify, all powered by your chosen LLM provider.

---

## Contributing

This is an open project. The vision is a reference engine that any team — at any enterprise, at any scale — can deploy as the foundation of their Market-of-One strategy.

**Two agent layers are open for community contribution:**

### Guardian Layer — Ethics Agent
`agents/ethics_agent/`  
Propensity-to-Annoy scoring. Frequency capping. Consent signal handling. Ethical personalization rails.  
Issues labeled `[ethics-agent]`

### Guardian Layer — Channel Agent
`agents/channel_agent/`  
Optichannel routing — deliver the right message across email, SMS, push, in-app, and web based on real-time context.  
Issues labeled `[channel-agent]`

**What we need most:**
- LLM provider implementations (Claude, GPT-4o, Azure, Mistral)
- Guardian Agent contributions (ethics + channel)
- Assess layer — maturity diagnostic tooling (see roadmap)
- Enterprise deployment patterns (Kubernetes, multi-tenant, CDPs)

---

## Roadmap

| Stage | Status | What |
|---|---|---|
| **Architect** (Signal + Insight + Action + Amplify layers) | ✅ Live | Core engine — this repo |
| **Guardian Layer** (Ethics + Channel agents) | 🔨 Open | Community contributions welcome |
| **Assess Layer** | 📋 Planned | Maturity diagnostic — data readiness, agent architecture, org alignment |
| **Multi-tenant** | 📋 Planned | Run one engine for many businesses |
| **CDP Integration** | 📋 Planned | Native connectors to Segment, Salesforce, Adobe |
| **Multi-provider LLM** | 🔨 In Progress | Anthropic, OpenAI, Azure connectors |

---

## The Framework

**ARCĀ Framework™** — [rohitprabhakar.com/arca](https://rohitprabhakar.com/arca)  
The connective architecture that turns agentic AI into compounding revenue and CX advantage. Assess. Architect. Command. Amplify.

**Market-of-One™** — [rohitprabhakar.com/market-of-one](https://rohitprabhakar.com/market-of-one)  
The philosophy and manifesto. Every customer is a market. The age of the segment is over.

---

## License

Apache 2.0 — see [LICENSE](LICENSE).  
Copyright 2026 [Rohit Prabhakar](https://rohitprabhakar.com)

You are free to use, modify, and distribute this code. Attribution must be preserved.

**Trademark Notice:** The **ARCĀ Framework™** and **Market-of-One™** names, frameworks, and associated intellectual property are proprietary to Rohit Prabhakar and protected under trademark (Class 41 · Class 35). The Apache 2.0 license grants rights to the software only — not to the framework names, methodology branding, or associated intellectual property.
