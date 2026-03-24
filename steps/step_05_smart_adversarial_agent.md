# Step 5: Add LLM Reasoning to the Adversarial Agent

## Core Concept
Replace hardcoded attacks and keyword analysis with LLM-powered reasoning.
The adversarial agent now uses Claude to:
1. **Generate attacks** — craft novel prompts based on the target's rules and previous failures
2. **Analyze responses** — understand whether a response is a genuine leak or a false positive refusal
3. **Adapt strategy** — learn from failed attempts and try smarter approaches

## What Changes from Step 4

| Component | Step 4 (Basic) | Step 5 (LLM-Powered) |
|-----------|---------------|----------------------|
| Attack generation | Hardcoded list of 18 prompts | Claude generates attacks dynamically |
| Analysis | Keyword matching | Claude reads the response and judges severity |
| Adaptation | None — runs the same list every time | Uses failed attempts to inform next attack |
| False positives | High — "system prompt" in refusal triggers alert | Low — Claude understands refusal vs. leak |

## The Upgraded Adversarial Loop

```
1. STRATEGIZE  — Claude reads target rules + past results, picks attack approach
2. GENERATE    — Claude crafts an attack prompt
3. PROBE       — Send the attack to HelpBot's API
4. ANALYZE     — Claude reads the response and judges: leak, refusal, or partial?
5. ADAPT       — Claude updates strategy based on what worked/failed
6. REPORT      — Log structured findings
→ Loop back to 1 with accumulated knowledge
```

## Key Design: Two LLM Roles
The adversarial agent uses Claude in two distinct roles:
- **Attacker LLM**: Generates attack prompts (creative, adversarial thinking)
- **Judge LLM**: Analyzes responses for rule violations (objective, analytical thinking)

Separating these roles prevents the attacker's bias from contaminating the analysis.

## Files Modified
- New: `smart_adversarial_agent.py` — LLM-powered adversarial agent
- New: `run_smart_attack.py` — CLI runner for the smart agent
- Unchanged: `adversarial_agent.py` — kept for comparison
