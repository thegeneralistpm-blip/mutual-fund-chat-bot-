# Edge Cases — Phase 2: Personalized Portfolio Intelligence

> **Phase:** 2 — Personalized Intelligence
> **Components:** Auth Layer, User Profile Store, Portfolio Fetcher, Context Builder, Conversation Memory

---

## 1. Authentication & Authorization

### EC-2.1: Expired / Invalid JWT Token
- **Scenario:** User's JWT expires mid-session or is tampered with.
- **Handling:** Return HTTP 401 with message: "Session expired. Please log in again." Clear session memory.

### EC-2.2: User Not Authenticated But Asks Portfolio Question
- **Scenario:** Anonymous user asks "How is my portfolio doing?"
- **Handling:** Respond: "To view your portfolio insights, please log in first." Fall back to Phase 1 (generic Q&A) mode.

### EC-2.3: Token Stolen / Replay Attack
- **Scenario:** A valid JWT is reused from a different client/IP.
- **Handling:** Validate token + IP binding (optional). Log suspicious activity. Require re-auth on IP change.

---

## 2. Portfolio Data

### EC-2.4: User Has Empty Portfolio (No Holdings)
- **Scenario:** New user with zero mutual fund holdings asks for portfolio analysis.
- **Handling:** Respond: "It looks like you haven't invested in any mutual funds yet. Would you like me to suggest some funds based on your goals?"

### EC-2.5: Portfolio API Returns Timeout / Error
- **Scenario:** Groww internal API (or mock) for portfolio data is down.
- **Handling:** Retry once. If still failing, inform user: "I'm unable to fetch your portfolio right now. You can still ask general MF questions." Fall back to Phase 1 mode.

### EC-2.6: Portfolio Contains Funds Not in Our Knowledge Base
- **Scenario:** User holds "Axis Bluechip" or "SBI Small Cap" — we only have HDFC fund data.
- **Handling:** Acknowledge the holding but note: "I have detailed data only for HDFC funds. For your other holdings, I can provide general information." Don't fabricate data.

### EC-2.7: Very Large Portfolio (50+ Holdings)
- **Scenario:** User holds 50+ fund schemes.
- **Handling:** Summarize top 10 by value. Truncate context to fit LLM token limit. Offer: "You have 50 holdings. Here's a summary of your top 10. Ask me about any specific fund."

### EC-2.8: Portfolio Data is Stale (Cached from Last Login)
- **Scenario:** Cached portfolio snapshot is days old; user has made transactions since.
- **Handling:** Show "Portfolio data as of [date]" disclaimer. Offer to refresh: "Would you like me to fetch your latest portfolio?"

---

## 3. User Profile & Risk Assessment

### EC-2.9: User Hasn't Set Risk Profile
- **Scenario:** Risk profile is null/empty — user never completed the questionnaire.
- **Handling:** Before giving personalized recommendations, ask: "To give you better suggestions, what's your risk appetite? (Low / Medium / High)" Store the response.

### EC-2.10: User's Risk Profile Contradicts Their Portfolio
- **Scenario:** User says "Low risk" but holds 80% small-cap funds.
- **Handling:** Flag proactively: "Your portfolio is heavily tilted toward high-risk small-cap funds, which may not align with your low-risk preference. Consider diversifying."

### EC-2.11: User Changes Risk Profile Mid-Conversation
- **Scenario:** User says "Actually, I'm high risk" after previously setting "Low."
- **Handling:** Update the profile in Redis immediately. Acknowledge: "Got it — I've updated your risk profile to High. My suggestions going forward will reflect this."

---

## 4. Conversation Memory

### EC-2.12: Session Expires (Redis TTL)
- **Scenario:** User returns after 30 minutes; Redis session has expired.
- **Handling:** Start a fresh session. Don't reference previous conversation. Optionally: "It's been a while! Let me know what you'd like to discuss."

### EC-2.13: Memory Window Exceeds Token Limit
- **Scenario:** After 20+ turns, conversation memory exceeds the LLM's context window.
- **Handling:** Use sliding window (last 10 turns). Summarize older turns into a single "conversation summary" chunk.

### EC-2.14: User References Something From Earlier in Chat
- **Scenario:** "What about that fund you mentioned 5 messages ago?"
- **Handling:** If within memory window, resolve the reference. If outside window, respond: "I'm sorry, I don't recall that detail. Could you specify which fund you mean?"

### EC-2.15: Context Confusion Across Topics
- **Scenario:** User discusses HDFC Mid Cap, then switches to ELSS tax saving, then says "What's its NAV?" — ambiguous pronoun.
- **Handling:** Use the most recent fund mentioned in memory. If ambiguous, ask: "Which fund's NAV are you asking about — HDFC Mid Cap or ELSS?"

---

## 5. Personalized Responses

### EC-2.16: User Asks "Should I Sell?"
- **Scenario:** Direct buy/sell decision request.
- **Handling:** Never recommend sell/buy. Respond: "I can share performance data and analysis, but buy/sell decisions should be made with a SEBI-registered advisor." + Disclaimer.

### EC-2.17: Portfolio Has Negative Returns
- **Scenario:** User's portfolio shows -15% XIRR.
- **Handling:** Be empathetic. Don't sugarcoat: "Your portfolio has returned -15% XIRR over this period. This could be due to recent market conditions. Here's a breakdown by fund..."

### EC-2.18: User Asks to Compare Their Portfolio vs Benchmark
- **Scenario:** "Am I beating Nifty 50?"
- **Handling:** If we have benchmark data, compute and compare. If not, respond: "I currently have fund-level returns but limited benchmark data. Your HDFC Equity Fund has returned X% vs its benchmark Y%."

---

## Summary

| ID | Category | Severity |
|---|---|---|
| EC-2.1 | Auth — Expired JWT | 🟡 Medium |
| EC-2.2 | Auth — Unauthenticated query | 🟡 Medium |
| EC-2.3 | Auth — Token replay | 🟡 Medium |
| EC-2.4 | Portfolio — Empty holdings | 🟢 Low |
| EC-2.5 | Portfolio — API down | 🟡 Medium |
| EC-2.6 | Portfolio — Unknown funds | 🟡 Medium |
| EC-2.7 | Portfolio — Very large | 🟢 Low |
| EC-2.8 | Portfolio — Stale cache | 🟡 Medium |
| EC-2.9 | Profile — No risk profile | 🟡 Medium |
| EC-2.10 | Profile — Risk mismatch | 🟡 Medium |
| EC-2.11 | Profile — Mid-session change | 🟢 Low |
| EC-2.12 | Memory — Session expired | 🟢 Low |
| EC-2.13 | Memory — Token overflow | 🟡 Medium |
| EC-2.14 | Memory — Back-reference | 🟡 Medium |
| EC-2.15 | Memory — Ambiguous pronoun | 🟡 Medium |
| EC-2.16 | Response — Buy/sell advice | 🔴 High |
| EC-2.17 | Response — Negative returns | 🟡 Medium |
| EC-2.18 | Response — Benchmark compare | 🟡 Medium |
