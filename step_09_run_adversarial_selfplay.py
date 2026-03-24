"""
Run attacker vs defender adversarial self-play.

Usage:
    python step_09_run_adversarial_selfplay.py         # 3 rounds, 5 attacks each
    python step_09_run_adversarial_selfplay.py 5       # 5 rounds
    python step_09_run_adversarial_selfplay.py 3 8     # 3 rounds, 8 attacks each
"""

from dotenv import load_dotenv
load_dotenv()

import sys
from shared import validate_cli_arg
from step_09_attacker_defender import AttackerDefenderSystem


def main():
    num_rounds = validate_cli_arg(sys.argv, default=3, name="num_rounds", max_val=10)

    attacks_per_round = 5
    if len(sys.argv) > 2:
        try:
            attacks_per_round = int(sys.argv[2])
            if attacks_per_round < 1:
                raise ValueError
        except ValueError:
            print("attacks_per_round must be a positive integer")
            sys.exit(1)

    total_attacks = num_rounds * attacks_per_round
    # Each attack = probe + judge = 2 LLM calls
    # Each round also has attacker generation + possibly defender = 2 more
    estimated_calls = total_attacks * 2 + num_rounds * 2

    with AttackerDefenderSystem(attacks_per_round=attacks_per_round) as system:
        print("Adversarial Self-Play: Attacker vs Defender")
        print(f"  {num_rounds} rounds, {attacks_per_round} attacks per round")
        print(f"  ~{estimated_calls} LLM calls estimated")
        print("=" * 70)

        for result in system.run_selfplay(num_rounds=num_rounds):
            breaches = len(result.breaches)
            total = len(result.attacks)
            print(f"\nRound {result.round_num}: {breaches}/{total} breached ({result.breach_rate:.0%})")

            for a in result.attacks:
                print(f"  {a}")

            if result.changes_made:
                print(f"\n  Defender hardened prompt:")
                for c in result.changes_made[:3]:
                    print(f"    - {c}")

        # Save prompt evolution
        output_dir = "prompt_evolution"
        final_path = system.save_prompt_evolution(output_dir)
        print(f"\nPrompt evolution saved to: {output_dir}/")
        print(f"Final hardened prompt: {final_path}")

        print()
        print(system.get_report())


if __name__ == "__main__":
    main()
