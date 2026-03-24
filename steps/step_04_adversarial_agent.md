# Step 4: Build a Basic Adversarial Agent

## Core Concept
Build an agent that systematically attacks HelpBot using hardcoded attack strategies. No LLM reasoning yet — that comes in Step 5. This step proves the adversarial loop works: **probe → analyze → report**.

## What We Build
- `adversarial_agent.py` — The adversarial agent class with attack strategies
- `run_attack.py` — CLI script to run attacks and display results
- Attack strategies organized by category (from Step 3's attack trees)

## The Adversarial Loop

```
For each attack category:
    For each attack in that category:
        1. PROBE   — Send the attack to HelpBot's API
        2. ANALYZE — Check the response for signs of rule violation
        3. REPORT  — Log the result (success/partial/fail)

Generate summary report
```

## Attack Categories (from Step 3)
1. **Direct extraction** — Bluntly ask for the system prompt or rules
2. **Roleplay/persona** — Try to make HelpBot change character
3. **Encoding tricks** — Ask for rules in a different format
4. **Context manipulation** — Pretend to be an admin or debugger
5. **Indirect extraction** — Ask about boundaries instead of rules directly
6. **Off-topic drift** — Try to get HelpBot to talk about unrelated things

## Analysis: How to Detect Rule Violations
The agent checks responses for keywords and patterns that indicate a breach:
- System prompt content leaking (mentions of "RULES", "NEVER", instruction-like text)
- Character breaking (responding as non-HelpBot identity)
- Off-topic responses (discussing non-TechNova subjects in detail)
- Rule content leaking (listing out its restrictions)

## Key Design Decisions
- Attacks are hardcoded strings (Step 5 adds LLM-generated attacks)
- Each attack targets a specific rule from HelpBot's system prompt
- Analysis is keyword-based (Step 5 adds LLM-powered analysis)
- Results are structured for reporting
- Each attack runs in a fresh session (reset between attacks) for isolation

## Files Modified
- New: `adversarial_agent.py`
- New: `run_attack.py`
