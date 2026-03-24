# Step 9: Attacker + Defender Agent Pairs

## Core Concept
Two Claude-powered agents competing in a loop:
- **Attacker**: Tries to break HelpBot via prompt injection
- **Defender**: Analyzes successful attacks and hardens the system prompt
- They iterate — attacker adapts to the hardened prompt, defender patches again

This is **adversarial self-play** — the same principle behind AlphaGo improving by playing itself.

## How It Works

```
Round 1:
  Attacker → generates attacks against current system prompt
  Attacker → sends attacks to HelpBot
  Judge     → evaluates which attacks succeeded
  Defender → analyzes successful attacks
  Defender → rewrites system prompt to defend against them

Round 2:
  HelpBot now uses the HARDENED system prompt
  Attacker → generates NEW attacks against the hardened prompt
  Attacker → sends attacks (old successful ones + new ones)
  Judge     → evaluates results
  Defender → further hardens the prompt
  ...repeat...
```

## Key Design Decisions
- Target: HelpBot's system prompt (not code)
- Defender output: improved system prompt saved to file after each round
- Attacker carries forward knowledge of what worked/failed
- The system prompt evolves over rounds — you can see the progression
- Default 3 rounds, configurable
- CLI only

## What Makes This Different from Steps 5-6
- Steps 5-6: one-sided — attacker attacks, no one defends
- Step 9: two-sided — attacker and defender compete, both improve
- The attacker must get smarter because the defender is closing holes
- The defender must anticipate novel attacks, not just patch known ones

## Output
- Per-round attack results and prompt changes
- Final hardened system prompt
- Evolution log showing how the prompt changed across rounds

## Files
- `step_09_attacker_defender.py` — The attacker/defender pair system
- `step_09_run_adversarial_selfplay.py` — CLI runner
