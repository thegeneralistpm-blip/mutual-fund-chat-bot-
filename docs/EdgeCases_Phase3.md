# Edge Cases — Phase 3: Agentic Capabilities

> **Phase:** 3 — Agentic Tool-Use
> **Components:** Agent Orchestrator, Tool Registry, ReAct LLM, Live NAV Fetcher, SIP Calculator, Fund Comparator, Tax Estimator

---

## 1. Tool Selection & Routing

### EC-3.1: Agent Selects Wrong Tool
- **Scenario:** User asks "What is NAV?" (educational) but agent routes to `get_live_nav` tool instead of RAG search.
- **Handling:** Add intent classification before tool routing. Educational queries → RAG. Data queries → tools.

### EC-3.2: Query Requires Multiple Tools
- **Scenario:** "Compare HDFC Mid Cap and Small Cap, and also calculate SIP for the winner."
- **Handling:** Agent should chain tools: `compare_funds` → `calculate_sip_returns`. Ensure sequential execution and context passing between tool calls.

### EC-3.3: Agent Enters Infinite Tool-Calling Loop
- **Scenario:** ReAct loop: Thought → Action → Observation → Thought → Action... never reaching Final Answer.
- **Handling:** Set max iterations (e.g., 5). If exceeded, force a final answer: "I wasn't able to fully process your request. Here's what I found so far..."

### EC-3.4: No Tool Matches the Query
- **Scenario:** User asks something none of the registered tools can handle (e.g., "What is Bitcoin price?").
- **Handling:** Fall back to RAG search. If RAG also has low confidence, respond: "This is outside my current capabilities. I specialize in HDFC mutual funds."

---

## 2. Live NAV Fetcher

### EC-3.5: AMFI API Returns Stale NAV (Weekend/Holiday)
- **Scenario:** User asks for "current NAV" on Sunday — API returns Friday's NAV.
- **Handling:** Display with date: "HDFC Mid Cap NAV: ₹123.45 (as of Fri, May 9). Markets are closed on weekends."

### EC-3.6: Fund Scheme Code Not Found in API
- **Scenario:** Scheme code was changed or deprecated.
- **Handling:** Try fuzzy search on fund name. If not found, respond: "I couldn't fetch live NAV for this fund. Here's the last known NAV from our database."

### EC-3.7: API Returns NAV = 0 or Negative
- **Scenario:** Malformed API data.
- **Handling:** Reject any NAV ≤ 0. Log the anomaly. Return cached NAV with "unable to fetch latest" disclaimer.

---

## 3. Fund Comparison Tool

### EC-3.8: Comparing Funds of Different Categories
- **Scenario:** "Compare HDFC Gold ETF FoF vs HDFC Small Cap" — apples to oranges.
- **Handling:** Proceed with comparison but add context: "Note: These are different fund categories (Gold vs Equity Small Cap). A direct comparison may not be meaningful."

### EC-3.9: One of the Compared Funds Not in Knowledge Base
- **Scenario:** "Compare HDFC Mid Cap vs Axis Bluechip."
- **Handling:** Respond: "I have detailed data for HDFC Mid Cap but not Axis Bluechip. Here's HDFC Mid Cap's performance. For a full comparison, check Groww's compare feature."

### EC-3.10: Comparison With Insufficient Data
- **Scenario:** One fund has 5Y returns but the other was launched 2 years ago.
- **Handling:** Compare only overlapping periods. Note: "HDFC Multi Cap has only 2 years of history, so I'm comparing 1Y and 2Y returns only."

---

## 4. SIP Calculator

### EC-3.11: Unrealistic SIP Parameters
- **Scenario:** User inputs SIP of ₹10 lakh/month for 100 years at 50% return.
- **Handling:** Validate inputs. Max SIP: ₹10,00,000. Max duration: 40 years. Max expected return: 30%. Flag unrealistic combos with a warning.

### EC-3.12: Expected Return Rate Not Specified
- **Scenario:** "Calculate SIP of ₹5,000 for 10 years."
- **Handling:** Ask: "What annual return rate should I assume? Typical equity fund returns range 10–15%." Or use fund's historical return as default.

### EC-3.13: SIP Amount Below Fund Minimum
- **Scenario:** User says "SIP of ₹50/month in HDFC Small Cap" — min SIP is ₹100.
- **Handling:** Inform: "HDFC Small Cap requires a minimum SIP of ₹100. Would you like to recalculate with ₹100?"

---

## 5. Tax Estimator (ELSS / 80C)

### EC-3.14: Investment Amount Exceeds 80C Limit
- **Scenario:** User says "I want to save tax by investing ₹5 lakh in ELSS."
- **Handling:** Inform: "Section 80C deduction is capped at ₹1.5 lakh/year. Tax savings on ₹1.5 lakh at 30% slab = ₹46,800. The remaining ₹3.5 lakh won't provide additional tax benefit."

### EC-3.15: User Asks About New vs Old Tax Regime
- **Scenario:** "Will ELSS help me save tax?"
- **Handling:** Clarify: "ELSS deductions under Section 80C are available only in the Old Tax Regime. Under the New Regime, these deductions are not applicable."

### EC-3.16: Non-ELSS Fund for Tax Saving
- **Scenario:** "Can I save tax with HDFC Mid Cap?"
- **Handling:** Respond: "HDFC Mid Cap is not an ELSS fund and does not qualify for Section 80C deduction. Only ELSS funds (Tax Saver category) qualify." Suggest ELSS alternatives if available.

---

## 6. Agent Orchestration

### EC-3.17: Tool Returns Error / Exception
- **Scenario:** A tool crashes (API error, parsing error, division by zero in calculator).
- **Handling:** Catch exception. Agent should treat it as an observation: "Tool error: unable to fetch data." Then produce a graceful final answer using available context.

### EC-3.18: Tool Returns Partial Data
- **Scenario:** `compare_funds` succeeds for Fund A but fails for Fund B.
- **Handling:** Present available data: "Here's HDFC Mid Cap's performance. I couldn't retrieve data for the other fund."

### EC-3.19: LLM Misformats Tool Call Arguments
- **Scenario:** Agent outputs `compare_funds("HDFC", "small cap")` instead of proper fund names.
- **Handling:** Validate tool arguments before execution. If invalid, retry with prompt: "Please specify the full fund names for comparison."

### EC-3.20: User Asks Agent to Perform Destructive Action
- **Scenario:** "Start a SIP of ₹10,000 in HDFC Mid Cap" or "Redeem my portfolio."
- **Handling:** Never execute write operations. Respond: "I can't start or modify SIPs directly. You can do this on the Groww app. Here's the link to HDFC Mid Cap: [URL]." Human-in-the-loop guardrail.

---

## Summary

| ID | Category | Severity |
|---|---|---|
| EC-3.1 | Routing — Wrong tool | 🟡 Medium |
| EC-3.2 | Routing — Multi-tool chain | 🟡 Medium |
| EC-3.3 | Routing — Infinite loop | 🔴 High |
| EC-3.4 | Routing — No matching tool | 🟢 Low |
| EC-3.5 | NAV — Stale (holiday) | 🟢 Low |
| EC-3.6 | NAV — Code not found | 🟡 Medium |
| EC-3.7 | NAV — Zero/negative value | 🟡 Medium |
| EC-3.8 | Compare — Different categories | 🟢 Low |
| EC-3.9 | Compare — Unknown fund | 🟡 Medium |
| EC-3.10 | Compare — Missing data period | 🟡 Medium |
| EC-3.11 | SIP — Unrealistic params | 🟡 Medium |
| EC-3.12 | SIP — Missing return rate | 🟢 Low |
| EC-3.13 | SIP — Below minimum | 🟢 Low |
| EC-3.14 | Tax — Exceeds 80C limit | 🟡 Medium |
| EC-3.15 | Tax — Old vs new regime | 🟡 Medium |
| EC-3.16 | Tax — Non-ELSS fund | 🟡 Medium |
| EC-3.17 | Agent — Tool error | 🟡 Medium |
| EC-3.18 | Agent — Partial data | 🟡 Medium |
| EC-3.19 | Agent — Bad tool args | 🟡 Medium |
| EC-3.20 | Agent — Destructive action | 🔴 High |
