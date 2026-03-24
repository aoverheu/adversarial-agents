"""
STEP 10: CI/CD Adversarial Review
===================================
Orchestrates adversarial agents in CI mode for GitHub Actions.

This script:
1. Detects which files changed in a PR
2. Runs adversarial code reviewer on changed Python files
3. Runs prompt injection tester if system prompt / agent code changed
4. Posts results as a PR comment
5. Exits 0 (pass) or 1 (fail) to control the merge gate

Environment variables (set in GitHub Actions):
  ANTHROPIC_API_KEY  — API key for Claude
  GITHUB_TOKEN       — GitHub token (auto-provided by Actions)
  GITHUB_REPOSITORY  — owner/repo (auto-provided)
  PR_NUMBER          — PR number to comment on
  CHANGED_FILES      — space-separated list of changed files
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
import httpx
from datetime import datetime

from step_08_adversarial_code_reviewer import AdversarialCodeReviewer
from step_06_prompt_injection_tester import PromptInjectionTester, TECHNIQUES


# Files that trigger prompt injection testing when changed
PROMPT_SENSITIVE_FILES = {"agent.py", "app.py"}

# Severity levels that block the PR
BLOCKING_SEVERITIES = {"critical", "high"}


def get_changed_files() -> list[str]:
    """Get list of changed files from environment or git."""
    # In CI, CHANGED_FILES is set by the workflow
    env_files = os.getenv("CHANGED_FILES", "")
    if env_files:
        return [f.strip() for f in env_files.split() if f.strip()]

    # Fallback: use git diff against main
    import subprocess
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            capture_output=True, text=True, check=True
        )
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except subprocess.CalledProcessError:
        return []


def filter_python_files(files: list[str]) -> list[str]:
    """Filter to only Python files that exist."""
    base = os.path.dirname(os.path.abspath(__file__))
    valid = []
    for f in files:
        if not f.endswith(".py"):
            continue
        path = os.path.join(base, f) if not os.path.isabs(f) else f
        if os.path.exists(path):
            valid.append(path)
    return valid


def should_run_injection_test(files: list[str]) -> bool:
    """Check if any changed files affect the system prompt / agent behavior."""
    basenames = {os.path.basename(f) for f in files}
    return bool(basenames & PROMPT_SENSITIVE_FILES)


def run_code_review(files: list[str]) -> tuple[list, bool]:
    """Run adversarial code review on changed files. Returns (findings, has_blockers)."""
    if not files:
        return [], False

    reviewer = AdversarialCodeReviewer()
    all_findings = []

    for path, findings in reviewer.review_files(files):
        name = os.path.basename(path)
        print(f"  Reviewed {name}: {len(findings)} findings")
        all_findings.extend(findings)

    blockers = [f for f in all_findings if f.severity in BLOCKING_SEVERITIES]
    return all_findings, len(blockers) > 0


def run_injection_test() -> tuple[list, bool]:
    """Run prompt injection test. Returns (results, has_blockers)."""
    with PromptInjectionTester() as tester:
        results = []
        for phase, result in tester.run_campaign(evolve_rounds=1):
            print(f"  {result}")
            results.append(result)

    breaches = [r for r in results if r.success]
    return results, len(breaches) > 0


def format_pr_comment(code_findings: list, injection_results: list,
                      code_blocked: bool, injection_blocked: bool) -> str:
    """Format results as a GitHub PR comment in markdown."""
    lines = []
    lines.append("## Adversarial Security Review")
    lines.append("")

    # Overall status
    blocked = code_blocked or injection_blocked
    if blocked:
        lines.append("**Status: BLOCKED** -- High/critical findings require attention before merge.")
    else:
        lines.append("**Status: PASSED** -- No blocking findings.")
    lines.append("")

    # Code review findings
    if code_findings:
        lines.append("### Code Review Findings")
        lines.append("")

        # Group by severity
        by_sev = {}
        for f in code_findings:
            by_sev.setdefault(f.severity, []).append(f)

        for sev in ["critical", "high", "medium", "low", "info"]:
            findings = by_sev.get(sev, [])
            if not findings:
                continue
            icon = {"critical": "X", "high": "X", "medium": "!", "low": "-", "info": "-"}.get(sev, "-")
            lines.append(f"**{sev.upper()}** ({len(findings)})")
            lines.append("")
            for f in findings:
                block_marker = " **[BLOCKING]**" if sev in BLOCKING_SEVERITIES else ""
                lines.append(f"- [{icon}] **{f.title}** ({f.file_path}:{f.line_numbers}){block_marker}")
                lines.append(f"  - {f.vulnerability}")
                if sev in BLOCKING_SEVERITIES:
                    lines.append(f"  - Remediation: {f.remediation}")
            lines.append("")
    else:
        lines.append("### Code Review")
        lines.append("No Python files changed -- code review skipped.")
        lines.append("")

    # Injection test results
    if injection_results:
        lines.append("### Prompt Injection Test")
        lines.append("")
        breaches = [r for r in injection_results if r.success]
        total = len(injection_results)
        if breaches:
            lines.append(f"**{len(breaches)}/{total} techniques breached the defense** **[BLOCKING]**")
            lines.append("")
            for r in breaches:
                lines.append(f"- **{r.technique}** ({r.severity}): {r.explanation}")
        else:
            lines.append(f"All {total} injection techniques blocked. System prompt is resilient.")
        lines.append("")
    else:
        lines.append("### Prompt Injection Test")
        lines.append("No system-prompt-related files changed -- injection test skipped.")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append(f"*Generated by Adversarial CI Review on {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)


def post_pr_comment(comment: str) -> bool:
    """Post a comment on the PR via GitHub API."""
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")

    if not all([token, repo, pr_number]):
        print("Missing GITHUB_TOKEN, GITHUB_REPOSITORY, or PR_NUMBER -- skipping PR comment.")
        print("(This is normal when running locally.)")
        return False

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    response = httpx.post(
        url,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        },
        json={"body": comment},
        timeout=15,
    )

    if response.status_code == 201:
        print(f"PR comment posted: {response.json().get('html_url', '')}")
        return True
    else:
        print(f"Failed to post PR comment: {response.status_code} {response.text[:200]}")
        return False


def main():
    print("=" * 70)
    print("ADVERSARIAL CI/CD REVIEW")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("")

    # 1. Detect changed files
    changed = get_changed_files()
    if not changed:
        print("No changed files detected. Nothing to review.")
        sys.exit(0)

    print(f"Changed files ({len(changed)}):")
    for f in changed:
        print(f"  {f}")
    print("")

    # 2. Filter to reviewable Python files
    python_files = filter_python_files(changed)
    run_injection = should_run_injection_test(changed)

    print(f"Python files to review: {len(python_files)}")
    print(f"Run injection test: {run_injection}")
    print("-" * 70)

    # 3. Run adversarial code review
    code_findings = []
    code_blocked = False
    if python_files:
        print("\nPhase 1: Adversarial Code Review")
        code_findings, code_blocked = run_code_review(python_files)
        print(f"  Total findings: {len(code_findings)}")
        print(f"  Blocking: {code_blocked}")

    # 4. Run prompt injection test
    injection_results = []
    injection_blocked = False
    if run_injection:
        print("\nPhase 2: Prompt Injection Test")
        injection_results, injection_blocked = run_injection_test()
        breaches = [r for r in injection_results if r.success]
        print(f"  Breaches: {len(breaches)}/{len(injection_results)}")
        print(f"  Blocking: {injection_blocked}")

    # 5. Format and post results
    comment = format_pr_comment(code_findings, injection_results,
                                code_blocked, injection_blocked)

    print("\n" + "=" * 70)
    print("PR COMMENT PREVIEW:")
    print("=" * 70)
    print(comment)
    print("=" * 70)

    # Post to PR if in CI
    post_pr_comment(comment)

    # 6. Exit with appropriate code
    blocked = code_blocked or injection_blocked
    if blocked:
        print("\nRESULT: BLOCKED -- high/critical findings detected.")
        sys.exit(1)
    else:
        print("\nRESULT: PASSED -- no blocking findings.")
        sys.exit(0)


if __name__ == "__main__":
    main()
