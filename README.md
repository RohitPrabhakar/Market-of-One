# ARCĀ OS — The Market-of-One Living System

> *Intelligence delivered at the moment of need, inside the workflow. Zero context-switching.*

A multi-agent hyper-personalization engine that shows what enterprise architecture looks like when it mimics a living organism. Built and open-sourced by **[Rohit Prabhakar](https://rohitprabhakar.com)**.

**No engineers needed to run it. No API key needed to see it work.**

---

## Run It in 60 Seconds (No Install)

**The easiest way — one click:**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/rohitprabhakar/arca-os)

Click the button → click Deploy → open the URL. Done.  
*(Leave the API key blank — Demo Mode works out of the box.)*

---

## Run It on Your Laptop

### Option A — You have Python installed

```bash
# Step 1: Download the code
git clone https://github.com/rohitprabhakar/arca-os.git
cd arca-os

# Step 2: Install (one time only)
pip install -r requirements.txt

# Step 3: Run
python app.py

# Step 4: Open your browser
# Go to: http://localhost:5000
```

That's it. **No API key needed** — Demo Mode runs automatically.

---

### Option B — You have Docker installed

```bash
git clone https://github.com/rohitprabhakar/arca-os.git
cd arca-os
docker compose up
# Open http://localhost:5000
```

---

## Unlock Live AI Mode (Optional)

Want real AI-generated responses instead of demos?

1. Get a free API key at [platform.openai.com](https://platform.openai.com)
2. Copy `.env.example` to `.env`
3. Replace `sk-your-key-here` with your actual key
4. Re-run `python app.py`

Cost: approximately **$0.01 per full pipeline run** using `gpt-4o-mini`.

---

## What It Does

Select a customer → click **RUN PIPELINE** → watch the Living System fire.

| Agent | What It Does | Status |
|---|---|---|
| **Context Agent** | Reads signals, builds a real-time profile: intent score, risk score, emotional state, moment of need | ✅ Live |
| **Content Agent** | Writes a unique message for this one person — not a template, not a segment | ✅ Live |
| **Ethics Agent** | Propensity-to-Annoy score + consent guardrails | 🔓 Open to contribute |
| **Channel Agent** | Routes to the right channel at the millisecond of intent | 🔓 Open to contribute |

---

## The In-Flow AI Principle

Traditional personalization: analyst reads signals → briefs writer → builds campaign → schedules send. That's days.

ARCĀ OS: signal fires → agents run → personalized message ready. That's milliseconds. No human in the loop. No workflow interruption.

That's **In-Flow AI** — intelligence delivered at the moment of need, inside the workflow.

---

## Architecture

```
INCOMING SIGNALS  →  Context Agent  →  Content Agent  →  [Ethics Agent]  →  [Channel Agent]
                      (Who is this        (Write for          (Is it safe         (Right channel,
                       person now?)        one person)         to send?)           right moment)
                            ↑_________________Recursive Memory Loop__________________↑
```

Maps to AWS: Kinesis · Bedrock · Amazon Personalize · Guardrails · Pinpoint · SageMaker

---

## Contribute

Two agents are open. Build one, put your name on it.

**🔴 Ethics Agent** — `[ethics-agent]`  
Calculate Propensity-to-Annoy, enforce GDPR/CCPA consent, validate guardrails before any message fires.

**🟣 Channel Agent** — `[channel-agent]`  
Optichannel routing: email vs in-app vs SMS vs push, selected by AI at the millisecond of intent.

[Open an issue →](https://github.com/rohitprabhakar/arca-os/issues)

---

## The ARCĀ Framework

This repo is the working implementation of **ARCĀ** — Agentic Revenue & Customer Architecture.  
A leadership framework for Fortune 500 executives building enterprise Living Systems.

Learn more: [rohitprabhakar.com](https://rohitprabhakar.com)

---

MIT License · Built with the conviction that the enterprise that most closely mimics a living system wins.
