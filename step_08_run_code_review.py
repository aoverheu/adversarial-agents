"""
Run the adversarial code reviewer against project files.

Usage:
    python step_08_run_code_review.py                    # Review all project Python files
    python step_08_run_code_review.py agent.py app.py    # Review specific files
"""

from dotenv import load_dotenv
load_dotenv()

import sys
import os
from step_08_adversarial_code_reviewer import AdversarialCodeReviewer


DEFAULT_FILES = [
    "agent.py",
    "app.py",
    "step_04_adversarial_agent.py",
    "step_05_smart_adversarial_agent.py",
    "step_06_prompt_injection_tester.py",
]


def main():
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = DEFAULT_FILES

    # Resolve paths
    base = os.path.dirname(os.path.abspath(__file__))
    resolved = []
    for f in files:
        path = os.path.join(base, f) if not os.path.isabs(f) else f
        if not os.path.exists(path):
            print(f"Warning: File not found: {f}")
            continue
        resolved.append(path)

    if not resolved:
        print("No valid files to review.")
        sys.exit(1)

    reviewer = AdversarialCodeReviewer()

    print("Adversarial Code Reviewer")
    print(f"Reviewing {len(resolved)} files through 3 lenses (attacker, quality, architecture)")
    print(f"  = {len(resolved) * 3} LLM calls")
    print("-" * 70)

    for path, findings in reviewer.review_files(resolved):
        name = os.path.basename(path)
        if findings:
            print(f"\n{name}: {len(findings)} findings")
            for f in findings:
                print(f"  {f}")
        else:
            print(f"\n{name}: no findings")

    print()
    print(reviewer.get_report())


if __name__ == "__main__":
    main()
