# Step 8: Adversarial Code Reviewer

## Core Concept
An agent that reviews code by **thinking like an attacker** — not just "is this code clean?"
but "how would I exploit this code?" Combined with quality review for complete coverage.

## How It Differs from Step 7 (Cooperative Review)

| Cooperative Review (Step 7) | Adversarial Review (Step 8) |
|---|---|
| "Is this code correct?" | "How would I exploit this code?" |
| "Does this follow conventions?" | "What attack vectors does this expose?" |
| "Is there a bug here?" | "Can I trigger this bug maliciously?" |
| "Should this be refactored?" | "Does this design create security gaps?" |
| Finds quality issues | Finds exploitable vulnerabilities |

## What the Adversarial Code Reviewer Checks

### Security (Attacker Mindset)
- OWASP Top 10 vulnerabilities (injection, broken auth, XSS, etc.)
- Input validation gaps an attacker could exploit
- Authentication/authorization weaknesses
- Information leakage patterns (error messages, logs, API responses)
- Hardcoded secrets or credentials
- Insecure dependencies

### Quality (Delivering Good Code)
- Logic errors that could be triggered by edge-case inputs
- Race conditions and concurrency issues
- Error handling gaps that reveal internal state
- Unvalidated assumptions about data

### Architecture (Systemic Weaknesses)
- Trust boundaries violated (user input trusted without validation)
- Missing rate limiting or resource controls
- Overly permissive defaults
- Attack surface unnecessarily large

## Design
- Takes a file or directory path as input
- Uses Claude to analyze code with an adversarial lens
- Produces a vulnerability report with:
  - Severity rating (critical/high/medium/low/info)
  - Exploitation scenario (how an attacker would use it)
  - Remediation advice
  - Code quality issues that enable the vulnerability

## Files
- `step_08_adversarial_code_reviewer.py` — The adversarial code reviewer agent
- `step_08_run_code_review.py` — CLI runner
