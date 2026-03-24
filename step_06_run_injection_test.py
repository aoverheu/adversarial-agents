"""
Run the prompt injection tester against HelpBot.

Usage:
    python step_06_run_injection_test.py        # Full campaign (11 techniques + 2 evolved)
    python step_06_run_injection_test.py 0      # Known techniques only (no evolution)
    python step_06_run_injection_test.py 5      # 5 rounds of evolution after known techniques
"""

from dotenv import load_dotenv
load_dotenv()

import sys
from shared import validate_cli_arg
from step_06_prompt_injection_tester import PromptInjectionTester, TECHNIQUES


def main():
    evolve_rounds = validate_cli_arg(sys.argv, default=2, name="evolve_rounds")

    with PromptInjectionTester() as tester:
        single = len([t for t in TECHNIQUES if t["type"] == "single"])
        multi = len([t for t in TECHNIQUES if t["type"] == "multi"])

        print("Prompt Injection Tester")
        print(f"  {single} single-turn techniques")
        print(f"  {multi} multi-turn techniques")
        print(f"  {evolve_rounds} evolution rounds")
        print("-" * 70)

        count = 0
        for phase, result in tester.run_campaign(evolve_rounds=evolve_rounds):
            count += 1
            print(f"[{count}] ({phase}) {result}")

        print()
        print(tester.get_report())


if __name__ == "__main__":
    main()
