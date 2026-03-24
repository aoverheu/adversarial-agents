# Step 7: Cooperative Code Review — Findings

## Overview
Reviewed all 8 Python files using 6 parallel review agents (3 code reviewers + 3 simplify agents).
This establishes the **cooperative baseline** — what a quality-focused review finds.
Step 8 will review the same code with an **adversarial/security** lens for comparison.

---

## HIGH SEVERITY Issues

### 1. Unbounded `sessions` dict — memory leak
**File:** `app.py:21`
Every unique `session_id` creates a new `Agent` with its own `anthropic.Anthropic()` client and conversation history. Nothing ever evicts stale sessions. Attack scripts create a fresh UUID per request, so a campaign of 42 attacks creates 42 orphaned sessions.

### 2. Corrupt conversation history on API failure
**File:** `agent.py:85`, `app.py:53`
`perceive()` appends the user message to history before `decide()` calls the API. If the API call fails (timeout, rate limit), the user message is recorded but no assistant response follows. The history is now in a broken state — next API call may fail because messages don't alternate correctly.

### 3. No HTTP error handling in probe methods
**Files:** `step_04_adversarial_agent.py:323`, `step_05_smart_adversarial_agent.py:236`, `step_06_prompt_injection_tester.py:277`
A non-200 response or missing `"response"` key causes a cryptic `KeyError` or `JSONDecodeError`. A single network hiccup crashes the entire campaign, discarding all progress.

### 4. `run_all` annotated as `list` but is a generator
**File:** `step_04_adversarial_agent.py:333`
Return annotation says `list[AttackResult]` but body uses `yield`. Callers who trust the annotation and assign `results = agent.run_all()` without iterating get an empty `get_report()`.

### 5. `run_campaign` always uses first N categories — never cycles
**File:** `step_05_smart_adversarial_agent.py:310`
`categories = ATTACK_CATEGORIES[:attacks_per_rule]` means with default `attacks_per_rule=3`, only `direct_extraction`, `roleplay_persona_shift`, and `encoding_obfuscation` are ever tried. `context_manipulation`, `indirect_extraction`, and `multi_turn_escalation` are never reached.

### 6. `evolved["technique_name"]` KeyError when LLM returns bad JSON
**File:** `step_06_prompt_injection_tester.py:442`
The `_parse_json` fallback only guarantees `"attack_prompt"` and `"reasoning"` keys, not `"technique_name"`. Crashes the campaign when the LLM returns malformed JSON for evolved techniques.

### 7. Blocking sync LLM call in async handler
**File:** `app.py:53`
`async def chat()` calls synchronous `agent.run()` which blocks the entire asyncio event loop during the API call. No other requests can be served.

---

## MEDIUM SEVERITY Issues

### 8. User-controlled `session_id` allows session hijacking
**File:** `app.py:36`
`session_id` is accepted verbatim from the client. Any user who guesses another user's session ID can read or inject messages into their conversation.

### 9. `httpx.Client` never closed — socket leak
**Files:** `step_04:309`, `step_05:177`, `step_06:226`
No `close()`, `__del__`, or context manager support. Each creates a connection pool that's never cleaned up.

### 10. Each `Agent` creates its own `anthropic.Anthropic()` client
**File:** `agent.py:58`
Connection pool per session instead of sharing one client. Combined with unbounded sessions dict, this leaks connections at scale.

### 11. `conversation_history` grows without bound
**File:** `agent.py:55`
Every message appended forever. Long sessions hit context-window limits and cost scales quadratically.

### 12. `_reset_session` defined but never called
**File:** `step_06_prompt_injection_tester.py:279`
Dead code — session cleanup method exists but no test ever invokes it.

### 13. `conversation_log` built but never used
**File:** `step_06_prompt_injection_tester.py:338`
Dead code duplicating data already in `prompts_sent`/`responses_received`.

### 14. No input validation on CLI arguments
**Files:** `step_05_run_smart_attack.py:18`, `step_06_run_injection_test.py:18`
Non-integer input causes unhandled `ValueError` with no usage message.

### 15. Progress counter wrong when evolution returns None
**File:** `step_06_run_injection_test.py:24`
`total` assumes every evolution round produces a result, but `_run_evolved` can return `None`.

---

## CODE DUPLICATION Issues (consolidation opportunities)

### 16. `_call_llm` duplicated verbatim
`step_05:179-187` and `step_06:228-236` — identical method.

### 17. `_parse_json` duplicated with variation
`step_05:189-197` (fragile) and `step_06:238-259` (robust with fallbacks). Step 05 crashes on malformed JSON.

### 18. HTTP probe method duplicated 3 times
`step_04:311-324`, `step_05:229-236`, `step_06:271-277` — same POST logic.

### 19. `__post_init__` client setup duplicated
`step_05:175-177` and `step_06:224-226` — identical Anthropic + httpx setup.

### 20. Severity icon mapping duplicated 3 times
`step_04:39-45`, `step_05:151-153`, `step_06:203-205` — same mapping.

### 21. Report generation pattern duplicated 3 times
`step_04:348-404`, `step_05:315-374`, `step_06:487-549` — same structure.

### 22. `load_dotenv()` called in both libraries and runners
Should only be in entrypoints (runners), not library modules.

---

## STRINGLY-TYPED Issues

### 23. Severity is an enum in step 04 but raw strings in steps 05/06
Step 04 defines `Severity` enum properly. Steps 05 and 06 use bare strings with no validation. A bad LLM response like `"severity": "severe"` silently falls through all reporting branches.

### 24. Attack categories, technique types are unvalidated strings
`"direct"`, `"single"`, `"multi"` etc. used throughout with no enum or constant — typo bugs are silent.

---

## EFFICIENCY Issues

### 25. All attacks run sequentially despite being independent
Each attack uses a fresh session — fully independent. Could use `concurrent.futures.ThreadPoolExecutor` or `asyncio.gather` for significant wall-clock time reduction.

### 26. `list(Severity).index(s)` recomputed on every `max()` call
**File:** `step_04_adversarial_agent.py:264,274`
Builds full enum list and linear scans each time. Should pre-compute an order dict.

---

## Recommended Fixes (Priority Order)

| Priority | Fix | Impact |
|----------|-----|--------|
| 1 | Wrap API/HTTP calls in try/except, roll back history on failure | Prevents crashes and corrupt state |
| 2 | Create shared utility module for `_call_llm`, `_parse_json`, probe, icons, report | Eliminates ~100 lines of duplication |
| 3 | Fix `run_all` annotation and `run_campaign` category cycling | Correctness bugs |
| 4 | Add session eviction (TTL cache) and share Anthropic client | Memory/connection leaks |
| 5 | Add `.get()` fallbacks for LLM-parsed JSON keys | Prevent KeyError crashes |
| 6 | Use `Severity` enum consistently across all steps | Type safety |
| 7 | Validate CLI args, fix progress counter | UX polish |
| 8 | Add concurrency for independent attacks | Performance |
