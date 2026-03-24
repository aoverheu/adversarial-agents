"""
Run the adversarial agent against HelpBot.

Usage:
    python step_04_run_attack.py              # Run all attacks
    python step_04_run_attack.py direct       # Run only 'direct' category
    python step_04_run_attack.py roleplay     # Run only 'roleplay' category
    python step_04_run_attack.py encoding     # Run only 'encoding' category
    python step_04_run_attack.py context      # Run only 'context' category
    python step_04_run_attack.py indirect     # Run only 'indirect' category
    python step_04_run_attack.py offtopic     # Run only 'offtopic' category
"""

from dotenv import load_dotenv
load_dotenv()

import sys
from step_04_adversarial_agent import AdversarialAgent, ATTACKS

VALID_CATEGORIES = {"direct", "roleplay", "encoding", "context", "indirect", "offtopic"}


def main():
    category = sys.argv[1] if len(sys.argv) > 1 else None

    if category and category not in VALID_CATEGORIES:
        print(f"Unknown category: {category}")
        print(f"Available: {', '.join(sorted(VALID_CATEGORIES))}")
        sys.exit(1)

    with AdversarialAgent() as agent:
        if category:
            attacks = [a for a in ATTACKS if a["category"] == category]
            print(f"Running {len(attacks)} attacks in category: {category}")
        else:
            attacks = ATTACKS
            print(f"Running all {len(attacks)} attacks")

        print("-" * 70)

        for result in agent.run_all(attacks):
            print(result)

        print()
        print(agent.get_report())


if __name__ == "__main__":
    main()
