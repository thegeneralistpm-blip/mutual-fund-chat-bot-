# Problem Statement: Groww Mutual Fund (MF) Chatbot

## Overview

Retail investors in India are increasingly turning to digital platforms like Groww to manage their mutual fund investments. However, despite a feature-rich app, a significant portion of users—especially first-time investors—struggle with:

- Understanding which mutual fund to invest in based on their risk appetite and goals.
- Interpreting NAV movements, expense ratios, and fund performance metrics.
- Getting quick answers to SIP-related queries (start, pause, increase SIP amount).
- Navigating ELSS funds for tax-saving purposes under Section 80C.
- Portfolio rebalancing decisions and understanding fund category differences.

Currently, Groww's in-app support relies on a rule-based chatbot and human agents, which leads to:
- High resolution time for investment-related queries.
- Poor personalization — generic answers not tied to a user's actual portfolio or goals.
- Inability to handle complex, conversational, multi-turn financial queries.

---

## Problem Statement

> **Build an AI-powered, conversational Mutual Fund Chatbot for the Groww platform that enables retail investors to get personalized, accurate, and actionable guidance on mutual fund discovery, portfolio health, SIP management, and tax-saving investments — using natural language.**

---

## Target Users

| User Segment | Description |
|---|---|
| **First-time investors** | New to MFs, need educational guidance and fund discovery |
| **SIP investors** | Regular SIP users who want performance tracking and optimization tips |
| **Tax-saving investors** | Users looking for ELSS recommendations under Section 80C |
| **Active portfolio holders** | Experienced investors needing portfolio health checks and rebalancing advice |

---

## Key Use Cases

### 1. Fund Discovery & Recommendation
- "Suggest a good large-cap mutual fund for a 5-year horizon."
- "Which is better — Mirae Asset or Axis Bluechip for long-term?"
- "I want to invest ₹5,000/month with moderate risk. What should I pick?"

### 2. SIP Management Queries
- "How do I start a SIP on Groww?"
- "Can I pause my SIP temporarily?"
- "What happens if my SIP payment fails?"

### 3. Portfolio Intelligence
- "How is my portfolio performing compared to the benchmark?"
- "Am I overexposed to mid-cap funds?"
- "Suggest rebalancing based on my current holdings."

### 4. Tax & Compliance Queries
- "Which ELSS fund gives the best returns for tax saving?"
- "What is the lock-in period for ELSS?"
- "How much can I save in tax by investing in ELSS?"

### 5. Educational Queries
- "What is the difference between direct and regular mutual funds?"
- "What does exit load mean?"
- "Explain NAV in simple terms."

### 6. Market & Fund Insights
- "What is the current NAV of Mirae Asset Emerging Bluechip?"
- "How has the Nifty 50 index fund performed in the last 1 year?"
- "Are debt funds safe in the current interest rate environment?"

---

## Success Metrics

| Metric | Target |
|---|---|
| Query resolution rate (no human handoff) | ≥ 80% |
| Average response latency | < 3 seconds |
| User satisfaction (CSAT) | ≥ 4.2 / 5 |
| First-contact resolution | ≥ 75% |
| Fund recommendation accuracy (user feedback) | ≥ 85% |

---

## Constraints & Guardrails

- The chatbot must **not act as a SEBI-registered investment advisor (RIA)**. All recommendations should carry appropriate disclaimers.
- Must comply with **SEBI regulations** on AI-generated financial advice.
- User portfolio data must be handled with **strict privacy and data security** standards.
- The system must gracefully **escalate to a human agent** for complex complaints or account-related issues.
- Responses must be **factually grounded** — hallucination on financial data is unacceptable.

---

## Technology Landscape

| Component | Options |
|---|---|
| LLM | Google Gemini / OpenAI GPT-4o / Claude |
| Embedding & Retrieval | FAISS / Pinecone / Weaviate |
| Backend | Python (FastAPI / Flask) |
| Data Sources | AMFI API, Groww internal APIs, MF knowledge base |
| Conversation Memory | Redis / LangChain Memory |
| Deployment | Docker + GCP / AWS |

---

## Scope of This Project

This project focuses on building a **Phase-wise MVP → Production-grade** Groww MF Chatbot covering:

0. **Phase 0** — Data scraping & ingestion (Groww fund pages + AMFI API → vector store)
1. **Phase 1** — Core RAG-based Q&A bot (educational + fund data queries)
2. **Phase 2** — Personalized portfolio intelligence (user context integration)
3. **Phase 3** — Agentic capabilities (SIP management, fund comparison, real-time data)
4. **Phase 4** — Production hardening (safety, compliance, scalability, monitoring)

### Phase 0 Target URLs (Zerodha Mutual Funds)

| Fund | Groww URL |
|---|---|
| Zerodha Nifty Large Midcap 250 | https://groww.in/mutual-funds/zerodha-nifty-large-midcap-250-index-fund-direct-growth |
| Zerodha Silver ETF FoF | https://groww.in/mutual-funds/zerodha-silver-etf-fof-direct-growth |
| Zerodha Gold ETF FoF | https://groww.in/mutual-funds/zerodha-gold-etf-fof-direct-growth |
| Zerodha ELSS Tax Saver | https://groww.in/mutual-funds/zerodha-elss-tax-saver-nifty-large-midcap-250-index-fund-direct-growth |
| Zerodha Overnight Fund | https://groww.in/mutual-funds/zerodha-overnight-fund-direct-growth |
