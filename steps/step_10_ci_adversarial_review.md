# Step 10: Adversarial Agents in CI/CD Pipeline

## Core Concept
Integrate adversarial agents into GitHub Actions so they run automatically on every PR.
No human triggers them — they're part of the infrastructure.

## What Gets Built

### 1. GitHub Actions Workflow (`.github/workflows/adversarial-review.yml`)
Triggers on PR open/update. Runs the CI script on a GitHub-hosted runner.

### 2. CI Runner Script (`step_10_ci_adversarial_review.py`)
Orchestrates adversarial agents in CI mode:
- Detects which files changed in the PR
- Runs adversarial code reviewer (Step 8) on changed Python files
- Runs prompt injection tester (Step 6) if agent.py/system prompt changed
- Formats results as a GitHub PR comment
- Exits 0 (pass) or 1 (fail) to control merge gate

### 3. PR Comment Reporter
Posts structured findings directly on the PR via GitHub API.

## Flow

```
PR opened/updated
  → GitHub Actions triggers
  → Installs Python + deps
  → Runs step_10_ci_adversarial_review.py
  → Adversarial code reviewer on changed files
  → Prompt injection tester if relevant
  → Posts PR comment with findings
  → Exit 0 (green) or 1 (red, blocks merge)
```

## Key Design Decisions
- Only reviews changed files (not entire codebase) for speed
- Prompt injection test only runs when system prompt or agent code changes
- High/critical findings block the PR; medium/low are informational
- Results posted as PR comment so the developer sees them inline
- ANTHROPIC_API_KEY stored as a GitHub Actions secret

## Files
- `.github/workflows/adversarial-review.yml` — GitHub Actions workflow
- `step_10_ci_adversarial_review.py` — CI orchestrator script
