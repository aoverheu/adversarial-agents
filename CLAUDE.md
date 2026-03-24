# Adversarial Agents Learning Project

## What This Is
A hands-on learning project where we build adversarial AI agents step by step.
We learn by building — concepts are explained just-in-time as we code.

## User Context
- Software developer adapting to AI-driven changes in the SDLC
- Wants practical implementation skills, not academic theory
- Prefers detailed line-by-line code explanations (this is a learning project)
- Has enterprise Anthropic account

## Tech Stack
- Python 3.12, FastAPI, Uvicorn, Jinja2
- Anthropic Claude API (enterprise account, key in `.env`)
- Server runs on port 8877 (port 8000 is blocked by corporate proxy)

## Current State: Steps 1-10 COMPLETE

### Learning Roadmap
| Step | Topic | Status |
|------|-------|--------|
| 1 | Agent loop basics (perceive → decide → act) | DONE |
| 2 | What makes an agent adversarial | DONE |
| 3 | Game theory basics (minimax, attacker/defender) | DONE |
| 4 | Build a basic adversarial agent | DONE |
| 5 | Add LLM reasoning to the adversarial agent | DONE |
| 6 | Prompt injection tester | DONE |
| 7 | Cooperative code review (using Claude Code agents) | DONE |
| 8 | Adversarial code reviewer | DONE |
| 9 | Attacker + defender agent pairs (adversarial self-play) | DONE |
| 10 | Adversarial agents in CI/CD pipeline | DONE |

### File Inventory
| File | Purpose |
|------|---------|
| `.env` | ANTHROPIC_API_KEY (do NOT commit) |
| `agent.py` | Core Agent class — perceive/decide/act loop + HelpBot system prompt |
| `app.py` | FastAPI server wrapping the agent as a web API |
| `templates/index.html` | Chat frontend for HelpBot (TechNova Support) |
| `steps/step_01_agent_loop.md` | Step 1 reference — agent loop concepts, data flow, code breakdown |
| `steps/step_02_what_makes_an_agent_adversarial.md` | Step 2 reference — adversarial vs cooperative, attack types, SDLC mapping |
| `steps/step_03_game_theory_basics.md` | Step 3 reference — minimax, attack trees, STRIDE, attacker/defender asymmetry |
| `shared.py` | Shared utilities — LLM calls, JSON parsing, HTTP probing, severity, reports |
| `adversarial-agents-detail.md` | When adversarial agents run in the SDLC + automation progression |
| `step_04_adversarial_agent.py` | AdversarialAgent class — 18 hardcoded attacks, keyword analysis, report generation |
| `step_04_run_attack.py` | CLI: `python step_04_run_attack.py [category]` |
| `steps/step_04_adversarial_agent.md` | Step 4 reference — adversarial loop, attack categories, analysis approach |
| `step_05_smart_adversarial_agent.py` | LLM-powered adversarial agent — Claude generates attacks + judges responses |
| `step_05_run_smart_attack.py` | CLI: `python step_05_run_smart_attack.py [attacks_per_rule]` |
| `steps/step_05_smart_adversarial_agent.md` | Step 5 reference — attacker/judge LLM roles, adaptation loop |
| `step_06_prompt_injection_tester.py` | Prompt injection tester — 11 named techniques, multi-turn, evolution |
| `step_06_run_injection_test.py` | CLI: `python step_06_run_injection_test.py [evolve_rounds]` |
| `steps/step_06_prompt_injection_tester.md` | Step 6 reference — injection types, named techniques, multi-turn strategy |
| `steps/step_07_cooperative_code_review.md` | Step 7 results — 26 findings from 6 review agents, prioritized fixes |
| `step_08_adversarial_code_reviewer.py` | Adversarial code reviewer — 3 lenses: attacker, quality, architecture |
| `step_08_run_code_review.py` | CLI: `python step_08_run_code_review.py [files...]` |
| `steps/step_08_adversarial_code_reviewer.md` | Step 8 reference — adversarial vs cooperative review, OWASP focus |
| `step_09_attacker_defender.py` | Attacker/Defender self-play — two Claude agents competing in rounds |
| `step_09_run_adversarial_selfplay.py` | CLI: `python step_09_run_adversarial_selfplay.py [rounds] [attacks_per_round]` |
| `steps/step_09_attacker_defender_pairs.md` | Step 9 reference — self-play concept, round structure, prompt evolution |
| `prompt_evolution/` | Output directory for evolved system prompts from self-play runs |
| `step_10_ci_adversarial_review.py` | CI orchestrator — runs adversarial agents, posts PR comments, controls merge gate |
| `.github/workflows/adversarial-review.yml` | GitHub Actions workflow — triggers on PR open/update |
| `steps/step_10_ci_adversarial_review.md` | Step 10 reference — CI/CD integration, workflow design |

### Target App: HelpBot
- A customer support chatbot for "TechNova" (fictional cloud platform)
- Products: NovaCMS, NovaDB, NovaAuth with specific pricing
- Has 7 security rules in its system prompt (never reveal prompt, never go off-topic, etc.)
- These rules are the ATTACK SURFACE for the adversarial agent we'll build in Step 4+
- API endpoint: POST /api/chat with {message, session_id}

### Key Decisions
- Build target app FIRST (Steps 1-3), then attack it (Steps 4+)
- Agent fundamentals taught by building HelpBot itself (it IS an agent)
- No heavy ML/training — this is engineering, not model training
- User prefers detailed line-by-line explanations of code
- **Always create `steps/step_XX_<name>.md` BEFORE starting each step** — serves as reference material and resume point
- **Python files use `step_XX_<name>.py` naming** — step md files match with `.md` extension
- **Adversarial = good code + secure code** — not just security; adversarial review covers quality, correctness, AND security

## How to Resume
1. Read this file (loaded automatically)
2. Check the roadmap above for current step
3. Review file inventory to understand what exists
4. Continue from the next NOT STARTED step
