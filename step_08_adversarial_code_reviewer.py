"""
STEP 8: Adversarial Code Reviewer
===================================
Reviews code by thinking like an attacker — not just "is this code clean?"
but "how would I exploit this code?"

This is the adversarial counterpart to Step 7's cooperative review.
It uses Claude to analyze code through multiple adversarial lenses:
  - ATTACKER: "How would I exploit this code?"
  - QUALITY: "What bugs would cause security-relevant failures?"
  - ARCHITECT: "What systemic weaknesses does this design create?"

Each finding includes an exploitation scenario — not just "this is bad"
but "here's exactly how an attacker would use this."
"""

import anthropic
import os
from dataclasses import dataclass, field
from datetime import datetime

from shared import severity_icon, call_llm, parse_json, truncate, severity_summary_lines


# =============================================================================
# REVIEW PROMPTS
# =============================================================================

ATTACKER_REVIEW_PROMPT = """You are a senior penetration tester conducting a code review. Your job is to find vulnerabilities that a real attacker could exploit.

Think like an attacker. For each vulnerability you find, explain:
1. WHAT the vulnerability is
2. HOW an attacker would exploit it (step by step)
3. WHAT damage could result
4. HOW to fix it

## Focus Areas (OWASP-informed)
- Injection flaws (SQL, command, prompt injection)
- Broken authentication / session management
- Sensitive data exposure (secrets, PII, system info in errors)
- Missing input validation at trust boundaries
- Security misconfiguration (permissive defaults, debug mode)
- Cross-site scripting (if web code)
- Insecure deserialization
- Missing rate limiting / resource controls
- Information leakage in error messages or API responses

## Code to Review
File: {file_path}
```
{code}
```

Respond with ONLY a JSON array of findings. If no vulnerabilities found, return [].
Each finding:
{{
    "title": "short description",
    "severity": "critical|high|medium|low|info",
    "category": "injection|auth|data_exposure|input_validation|config|xss|resource|info_leak|other",
    "line_numbers": "e.g. 42-45 or 'N/A' if architectural",
    "vulnerability": "what the vulnerability is",
    "exploitation": "step-by-step how an attacker would exploit this",
    "impact": "what damage could result",
    "remediation": "how to fix it"
}}
"""

QUALITY_REVIEW_PROMPT = """You are a senior engineer reviewing code for bugs that could cause security-relevant failures.

Not all bugs are security bugs — focus on ones where:
- The bug could be triggered by malicious input
- The failure reveals internal state to an attacker
- The error condition creates a denial-of-service
- The logic error bypasses a security check
- The race condition breaks an authorization boundary

## Code to Review
File: {file_path}
```
{code}
```

Respond with ONLY a JSON array of findings. If no issues found, return [].
Each finding:
{{
    "title": "short description",
    "severity": "critical|high|medium|low|info",
    "category": "logic_error|error_handling|race_condition|type_confusion|state_corruption|resource_exhaustion|other",
    "line_numbers": "e.g. 42-45",
    "vulnerability": "what the bug is and why it matters for security",
    "exploitation": "how malicious input could trigger this",
    "impact": "what happens when it's triggered",
    "remediation": "how to fix it"
}}
"""

ARCHITECTURE_REVIEW_PROMPT = """You are a security architect reviewing code for systemic design weaknesses.

Focus on issues that can't be fixed by patching a single line — they require design changes:
- Trust boundaries: where is user input trusted without validation?
- Attack surface: what functionality is exposed that doesn't need to be?
- Defense in depth: if one layer fails, what catches it?
- Least privilege: does code have more access than it needs?
- Fail-safe defaults: do errors fail open (insecure) or closed (secure)?

## Code to Review
File: {file_path}
```
{code}
```

Respond with ONLY a JSON array of findings. If no issues found, return [].
Each finding:
{{
    "title": "short description",
    "severity": "critical|high|medium|low|info",
    "category": "trust_boundary|attack_surface|defense_depth|least_privilege|fail_safe|other",
    "line_numbers": "e.g. 'N/A' for architectural issues, or specific lines",
    "vulnerability": "what the design weakness is",
    "exploitation": "how an attacker would leverage this weakness",
    "impact": "what the systemic risk is",
    "remediation": "what design change would fix this"
}}
"""


@dataclass
class CodeFinding:
    """A single finding from the adversarial code review."""
    file_path: str
    review_type: str  # attacker, quality, or architecture
    title: str
    severity: str
    category: str
    line_numbers: str
    vulnerability: str
    exploitation: str
    impact: str
    remediation: str

    def __str__(self):
        return (
            f"{severity_icon(self.severity)} [{self.review_type}] {self.title} "
            f"({self.file_path}:{self.line_numbers})"
        )


@dataclass
class AdversarialCodeReviewer:
    """
    Reviews code through three adversarial lenses:
      - Attacker: penetration testing mindset
      - Quality: bugs that enable security failures
      - Architecture: systemic design weaknesses

    Each finding includes an exploitation scenario.
    """

    model: str = "claude-sonnet-4-20250514"
    findings: list = field(default_factory=list)

    def __post_init__(self):
        self._llm = anthropic.Anthropic()

    def _review_file(self, file_path: str, code: str, prompt_template: str,
                     review_type: str) -> list[CodeFinding]:
        """Run a single review lens against a file."""
        system = prompt_template.format(file_path=file_path, code=code)
        response = call_llm(self._llm, self.model, system,
                           "Analyze this code for vulnerabilities. Return JSON array.")

        raw_findings = parse_json(response, fallback=[])
        # Handle case where parse returns a dict instead of list
        if isinstance(raw_findings, dict):
            raw_findings = [raw_findings] if "title" in raw_findings else []

        results = []
        for f in raw_findings:
            if not isinstance(f, dict) or "title" not in f:
                continue
            results.append(CodeFinding(
                file_path=os.path.basename(file_path),
                review_type=review_type,
                title=f.get("title", "Unknown"),
                severity=f.get("severity", "info"),
                category=f.get("category", "other"),
                line_numbers=f.get("line_numbers", "N/A"),
                vulnerability=f.get("vulnerability", ""),
                exploitation=f.get("exploitation", ""),
                impact=f.get("impact", ""),
                remediation=f.get("remediation", ""),
            ))
        return results

    def review_file(self, file_path: str) -> list[CodeFinding]:
        """Review a single file through all three adversarial lenses."""
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        file_findings = []

        # Run all three review lenses
        for prompt, review_type in [
            (ATTACKER_REVIEW_PROMPT, "attacker"),
            (QUALITY_REVIEW_PROMPT, "quality"),
            (ARCHITECTURE_REVIEW_PROMPT, "architecture"),
        ]:
            findings = self._review_file(file_path, code, prompt, review_type)
            file_findings.extend(findings)
            self.findings.extend(findings)

        return file_findings

    def review_files(self, file_paths: list[str]):
        """Review multiple files, yielding findings per file for progress display."""
        self.findings = []
        for path in file_paths:
            file_findings = self.review_file(path)
            yield path, file_findings

    def get_report(self) -> str:
        """Generate an adversarial code review report."""
        if not self.findings:
            return "No files have been reviewed."

        # Sort by severity (critical first)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        sorted_findings = sorted(self.findings,
                                 key=lambda f: severity_order.get(f.severity, 5))

        lines = []
        lines.append("=" * 70)
        lines.append("ADVERSARIAL CODE REVIEW REPORT")
        lines.append("=" * 70)
        lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Files reviewed: {len(set(f.file_path for f in self.findings))}")
        lines.append(f"Total findings: {len(self.findings)}")
        lines.append("")

        # Severity summary
        lines.append("SEVERITY SUMMARY:")
        lines.extend(severity_summary_lines(self.findings, lambda f: f.severity))
        lines.append("")

        # By review type
        lines.append("FINDINGS BY REVIEW TYPE:")
        by_type = {}
        for f in self.findings:
            by_type.setdefault(f.review_type, []).append(f)
        for rtype, findings in by_type.items():
            lines.append(f"  {rtype}: {len(findings)} findings")
        lines.append("")

        # Detailed findings (critical and high first)
        actionable = [f for f in sorted_findings if f.severity in ("critical", "high", "medium")]
        if actionable:
            lines.append("ACTIONABLE FINDINGS (critical/high/medium):")
            lines.append("-" * 70)
            for i, f in enumerate(actionable, 1):
                lines.append(f"\n  {i}. {f}")
                lines.append(f"     Severity: {f.severity}")
                lines.append(f"     Category: {f.category}")
                lines.append(f"     Vulnerability: {f.vulnerability}")
                lines.append(f"     Exploitation: {truncate(f.exploitation, 200)}")
                lines.append(f"     Impact: {truncate(f.impact, 150)}")
                lines.append(f"     Remediation: {f.remediation}")

        # Low/info findings (summarized)
        low_info = [f for f in sorted_findings if f.severity in ("low", "info")]
        if low_info:
            lines.append("")
            lines.append(f"INFORMATIONAL ({len(low_info)} findings):")
            lines.append("-" * 70)
            for f in low_info:
                lines.append(f"  {f}")

        # Comparison callout
        lines.append("")
        lines.append("NOTE: Compare with Step 7's cooperative review.")
        lines.append("Cooperative review finds quality issues.")
        lines.append("This adversarial review finds exploitable vulnerabilities.")
        lines.append("Both are needed for delivering good, secure code.")

        lines.append("")
        lines.append("=" * 70)
        return "\n".join(lines)
