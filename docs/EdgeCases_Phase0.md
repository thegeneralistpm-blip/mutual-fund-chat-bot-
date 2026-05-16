# Edge Cases — Phase 0: Data Scraping & Ingestion

> **Phase:** 0 — Data Scraping & Ingestion
> **Components:** Groww Scraper, AMFI API Client, Parser, Normalizer, Chunker, Embedder, FAISS Store

---

## 1. Scraping Layer

### EC-0.1: Groww Page Structure Changes
- **Scenario:** Groww updates React components, breaking CSS selectors.
- **Impact:** Scraper extracts null/wrong fields.
- **Handling:** Validate JSON against schema. Fall back to last cached `data/raw/*.json`. Log raw HTML to `data/debug/`.

### EC-0.2: HTTP 403/429 — Rate Limiting / Bot Detection
- **Scenario:** Cloudflare or Groww blocks the scraper.
- **Handling:** Exponential backoff (5s → 15s → 45s, max 3 retries). Rotate User-Agent. Use cached data on total failure.

### EC-0.3: HTTP 5xx — Server Error
- **Scenario:** Groww returns 500/502/503 for some fund pages.
- **Handling:** Scrape each fund independently. Mark failed funds as `"stale"`. Don't abort the batch.

### EC-0.4: Fund URL Returns 404
- **Scenario:** Fund was renamed, merged, or discontinued.
- **Handling:** Log warning, skip that fund. If ≥ 3 of 6 URLs return 404, halt pipeline for manual review.

### EC-0.5: Playwright Timeout (JS Not Rendering)
- **Scenario:** React hydration takes too long; dynamic content missing.
- **Handling:** Use `wait_until="networkidle"` with 30s timeout. Retry once with 60s. Validate critical fields post-scrape.

### EC-0.6: Partial Page Load (Lazy Sections Missing)
- **Scenario:** NAV loads but "Returns" table or "Holdings" tab is lazy-loaded.
- **Handling:** Scroll/click to trigger lazy sections. Accept partial data with `"completeness_score"` field.

---

## 2. AMFI API

### EC-0.7: AMFI API Downtime
- **Scenario:** `api.mfapi.in/mf` is unreachable.
- **Handling:** Retry 3× with 5s intervals. Fall back to cached `amfi_all_funds.json`. Pipeline should not fully fail.

### EC-0.8: Stale NAV Data (Market Holidays)
- **Scenario:** API returns NAV > 3 days old.
- **Handling:** Tag as `"stale": true`. Display "NAV as of [date]" disclaimer in later phases. Don't reject the data.

### EC-0.9: Scheme Code Mismatch
- **Scenario:** Scheme code doesn't match any fund (post-merger/rebrand).
- **Handling:** Try fuzzy matching on fund name. If no match, log error and skip NAV history for that fund.

### EC-0.10: Malformed JSON Response
- **Scenario:** API returns HTML error page or invalid JSON.
- **Handling:** Wrap in `try/except json.JSONDecodeError`. Log raw response. Skip AMFI data; proceed with Groww-scraped data only.

---

## 3. Parsing & Normalization

### EC-0.11: NAV in Unexpected Format
- **Scenario:** NAV shown as `"₹123.45"`, `"123,456.78"`, `"N/A"`, or `"--"`.
- **Handling:** Strip ₹, commas, whitespace. If `"N/A"` or `"--"`, set `nav: null` and `"nav_available": false`.

### EC-0.12: Returns "N/A" for Short-Tenure Funds
- **Scenario:** New fund has no 3Y/5Y data.
- **Handling:** Set missing periods to `null` (not `0`). Schema: `"returns": { "1y": 18.5, "3y": null, "5y": null }`.

### EC-0.13: Duplicate Fund Entries
- **Scenario:** AMC listing page and individual fund pages produce overlapping records.
- **Handling:** Deduplicate by `scheme_code`. Prefer individual fund page data (richer).

### EC-0.14: Special Characters in Fund Names
- **Scenario:** Names contain `&`, en-dash, parentheses, Unicode.
- **Handling:** Normalize to UTF-8. Replace en-dashes with hyphens. Strip HTML entities.

---

## 4. Chunking & Embedding

### EC-0.15: Document Shorter Than Chunk Size
- **Scenario:** Fund text < 512 tokens.
- **Handling:** Accept single-chunk documents. This is valid.

### EC-0.16: Embedding API Rate Limit
- **Scenario:** Google `text-embedding-004` hits rate/quota limits during batch.
- **Handling:** Batch with rate limiting (100 req/min). Exponential backoff on 429. Support incremental embedding.

### EC-0.17: Specific Chunk Causes Embedding Error
- **Scenario:** A chunk is too long, has encoding issues, or violates content policy.
- **Handling:** Log chunk + error. Skip and continue. Abort if > 20% chunks fail.

### EC-0.18: FAISS Index Corruption
- **Scenario:** `index.faiss` corrupted by interrupted write or disk issue.
- **Handling:** Write to temp file then atomic rename. Keep `index.faiss.bak`. Fall back to backup on load failure.

---

## 5. Pipeline Orchestration

### EC-0.19: Pipeline Crashes Mid-Execution
- **Scenario:** Scraping OK, parsing OK, embedding crashes (OOM/API error).
- **Handling:** Track state in `data/.pipeline_state.json`. Resume from last incomplete step on re-run.

### EC-0.20: Concurrent Pipeline Runs
- **Scenario:** Two runs start simultaneously (manual + cron).
- **Handling:** File-based lock `data/.pipeline.lock`. Abort if lock < 1 hour old. Auto-clean stale locks.

### EC-0.21: Disk Space Exhausted
- **Scenario:** `data/` fills up during scraping or indexing.
- **Handling:** Pre-check: require minimum 500 MB free. Abort with clear error if insufficient.

---

## 6. Data Quality

### EC-0.22: Groww and AMFI NAV Disagree
- **Scenario:** Groww says ₹123.45, AMFI says ₹122.90 for same date.
- **Handling:** Prefer AMFI (authoritative for NAV). Log discrepancy. Use Groww for non-NAV fields (AUM, expense ratio, risk).

### EC-0.23: Fund Category Mismatch
- **Scenario:** Groww says "Multi Cap", AMFI says "Flexi Cap" (post-recategorization).
- **Handling:** Use SEBI/AMFI label as primary. Store Groww label as `"groww_category"`. Log mismatch.

### EC-0.24: All 6 Target URLs Fail
- **Scenario:** Full network outage or Groww completely down.
- **Handling:** If no cache exists → fail loudly. If cache exists → critical warning + proceed with stale data. **Never build an empty FAISS index.**

---

## Summary

| ID | Category | Severity |
|---|---|---|
| EC-0.1 | Scraping — Structure change | 🔴 High |
| EC-0.2 | Scraping — Rate limiting | 🟡 Medium |
| EC-0.3 | Scraping — Server errors | 🟡 Medium |
| EC-0.4 | Scraping — URL 404 | 🟡 Medium |
| EC-0.5 | Scraping — Playwright timeout | 🟡 Medium |
| EC-0.6 | Scraping — Partial load | 🟡 Medium |
| EC-0.7 | AMFI — Downtime | 🟡 Medium |
| EC-0.8 | AMFI — Stale NAV | 🟢 Low |
| EC-0.9 | AMFI — Code mismatch | 🟡 Medium |
| EC-0.10 | AMFI — Malformed response | 🟡 Medium |
| EC-0.11 | Parsing — NAV format | 🟡 Medium |
| EC-0.12 | Parsing — Returns N/A | 🟢 Low |
| EC-0.13 | Parsing — Duplicates | 🟢 Low |
| EC-0.14 | Parsing — Special chars | 🟢 Low |
| EC-0.15 | Chunking — Short doc | 🟢 Low |
| EC-0.16 | Embedding — Rate limit | 🟡 Medium |
| EC-0.17 | Embedding — Chunk error | 🟢 Low |
| EC-0.18 | Storage — Index corruption | 🔴 High |
| EC-0.19 | Pipeline — Partial crash | 🟡 Medium |
| EC-0.20 | Pipeline — Concurrent runs | 🟡 Medium |
| EC-0.21 | Pipeline — Disk space | 🔴 High |
| EC-0.22 | Quality — NAV disagreement | 🟡 Medium |
| EC-0.23 | Quality — Category mismatch | 🟢 Low |
| EC-0.24 | Quality — All URLs fail | 🔴 High |
