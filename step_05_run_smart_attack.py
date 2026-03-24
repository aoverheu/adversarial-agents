"""
Run the LLM-powered adversarial agent against HelpBot.

Usage:
    python step_05_run_smart_attack.py           # 3 attacks per rule (21 total)
    python step_05_run_smart_attack.py 1         # 1 attack per rule (7 total, quick test)
    python step_05_run_smart_attack.py 6         # 6 attacks per rule (42 total, thorough)
"""

from dotenv import load_dotenv
load_dotenv()

import sys
from shared import validate_cli_arg
from step_05_smart_adversarial_agent import SmartAdversarialAgent


def main():
    attacks_per_rule = validate_cli_arg(sys.argv, default=3, name="attacks_per_rule", max_val=6)
    total = attacks_per_rule * 7  # 7 rules

    with SmartAdversarialAgent() as agent:
        print(f"Smart Adversarial Agent - LLM-Powered")
        print(f"Running {attacks_per_rule} attack(s) per rule ({total} total)")
        print(f"Each attack = 3 LLM calls (generate + probe + judge)")
        print("-" * 70)

        count = 0
        for result in agent.run_campaign(attacks_per_rule=attacks_per_rule):
            count += 1
            print(f"[{count}/{total}] {result}")

        print()
        print(agent.get_report())


if __name__ == "__main__":
    main()
