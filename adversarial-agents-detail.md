# When Adversarial Agents Run in the SDLC

## Overview

Adversarial agents run at **multiple stages** of the software development lifecycle — not just after coding is done.

```
┌──────────────────────────────────────────────────────────────────────┐
│                        SOFTWARE DEVELOPMENT LIFECYCLE                │
│                                                                      │
│  PLAN → CODE → REVIEW → TEST → DEPLOY → MONITOR                    │
│           │       │        │       │         │                       │
│           ▼       ▼        ▼       ▼         ▼                       │
│         Step 7  Step 7   Step 6  Step 8    Step 10                   │
│         Code    Code     Prompt  API Red   Pipeline                  │
│         Review  Review   Inject  Team      Monitor                   │
│         Agent   Agent    Tester  Tester    Agent                     │
│                                                                      │
│  ◄──── WHILE CODING ────►◄──── AFTER CODING ────►◄── CONTINUOUS ──► │
└──────────────────────────────────────────────────────────────────────┘
```

## While Coding (Shift Left)

**Adversarial Code Reviewer (Step 7)** runs as you write code, like a linter or copilot:
- You write a function → agent immediately analyzes it for vulnerabilities
- Catches issues before they ever reach a PR
- Think of it like a security-focused pair programmer looking over your shoulder
- Could be triggered on file save or as an IDE plugin

**Why during coding?** The earlier you catch a vulnerability, the cheaper it is to fix. A SQL injection caught while typing costs 5 minutes. The same bug caught in production costs an incident.

## After Coding, Before Merge

**Prompt Injection Tester (Step 6)** and **API Red-Team Tester (Step 8)** run against the built system:
- Code is written and running (like our HelpBot)
- Adversarial agents attack it as a black box — same as a real attacker would
- Results become a "go/no-go" gate before merging

**Why after coding?** Some vulnerabilities only exist when the system is running. A prompt injection isn't visible in the source code — it's an emergent behavior of the LLM + system prompt + user input combined.

## Continuously, Post-Deploy (Step 10)

**CI/CD Pipeline Agent** and **Attacker/Defender Pairs (Step 9)** run on an ongoing basis:
- Every PR triggers adversarial tests automatically
- Monitoring agents probe the live system periodically
- New attack techniques get added as the threat landscape evolves

**Why continuously?** Threats change. A system that was safe yesterday might be vulnerable to a new attack technique discovered today.

## Summary

| When | Which Agent | What It Catches | Analogy |
|------|------------|-----------------|---------|
| **While coding** | Code Reviewer (Step 7) | Vulnerabilities in source code | Spell-check while typing |
| **Before merge** | Prompt Injection (Step 6), API Tester (Step 8) | Runtime behavior vulnerabilities | QA testing before release |
| **On every PR** | CI/CD Agent (Step 10) | Regressions, new vulnerabilities | Automated test suite |
| **Post-deploy** | Attacker/Defender (Step 9) | Evolving threats, drift | Penetration test / red team |

## Automation Progression: From Manual Scripts to Autonomous Agents

The agents we build evolve from manually-run scripts to fully autonomous Claude sub-agents.

### Phase 1: Manual + No LLM (Step 4)
- Adversarial agent is a Python script with hardcoded attacks
- You run it manually: `python run_attack.py`
- Analysis is keyword-based — no Claude involved in the adversarial agent itself
- HelpBot uses Claude, but the attacker does not

### Phase 2: Manual + LLM-Powered (Steps 5-8)
- Adversarial agent uses Claude to **generate attacks** and **analyze responses**
- Much smarter — can reason about why an attack failed and adapt
- Still manually triggered by a developer running a script
- The LLM replaces hardcoded attack lists and keyword detection

| Step | What Claude Does in the Agent |
|------|-------------------------------|
| 5 | Generates novel attacks + analyzes responses for real vs. false-positive violations |
| 6 | Generates prompt injection attempts, evolves new techniques from failures |
| 7 | Reads source code and thinks like an attacker to find vulnerabilities |
| 8 | Reasons about API surfaces and crafts unexpected payloads |

### Phase 3: Semi-Autonomous (Step 9)
- **Two Claude sub-agents running in a loop against each other**
- Attacker agent generates attacks -> Defender agent patches -> Attacker adapts
- You start it and it runs autonomously until stopped or strategies exhausted
- Human reviews the results but doesn't drive the loop

### Phase 4: Fully Automatic (Step 10)
- Adversarial agents are triggered by CI/CD events (git push, PR creation)
- No human kicks them off — they run as part of the pipeline
- Block merge if vulnerabilities are found
- Post reports automatically to the PR
- Continuous monitoring agents probe live systems on a schedule

### Summary Table

| Step | How It Runs | Uses Claude? | Automatic? |
|------|------------|:---:|:---:|
| 4 | Manual CLI script | No | No |
| 5 | Manual CLI script | Yes — generates attacks + analyzes responses | No |
| 6 | Manual CLI | Yes | No |
| 7 | Manual CLI | Yes | No |
| 8 | Manual CLI | Yes | No |
| 9 | Self-running loop | Yes — two Claude agents competing | Semi-auto |
| 10 | CI/CD trigger | Yes — runs on every PR automatically | Fully automatic |
