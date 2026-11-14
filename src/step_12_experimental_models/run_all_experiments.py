"""
Master Runner: Step 12 — Experimental Ranking Model Development
==============================================================
Sequentially runs all 4 independent experimental ranking models:
- 12.1 Batting formula (Strike Rate & Survival balance without Boundary collinearity)
- 12.2 Bowling containment (Boundary suppression and dot-ball pressure induction)
- 12.3 Cohort-specific priors (Chronological validation of role/style priors)
- 12.4 Confidence-based qualification (Uncertainty modeling and dual-criteria eligibility)
"""

import sys
import time
from pathlib import Path

# Configure paths
SCRIPT_DIR = Path(__file__).resolve().parent

from exp12_1_batting_formula import run_experiment_12_1
from exp12_2_bowling_containment import run_experiment_12_2
from exp12_3_cohort_priors import run_experiment_12_3
from exp12_4_confidence_qualification import run_experiment_12_4

def run_all():
    print("#" * 80)
    print("STEP 12: EXPERIMENTAL RANKING MODEL DEVELOPMENT — MASTER SUITE RUNNER")
    print("#" * 80)
    t_start = time.time()

    experiments = [
        ("Experiment 12.1 — Batting Formula", run_experiment_12_1),
        ("Experiment 12.2 — Bowling Containment", run_experiment_12_2),
        ("Experiment 12.3 — Cohort-Specific Priors", run_experiment_12_3),
        ("Experiment 12.4 — Confidence-Based Qualification", run_experiment_12_4),
    ]

    results = []

    for name, func in experiments:
        print(f"\n>>> STARTING: {name}")
        t0 = time.time()
        try:
            func()
            elapsed = time.time() - t0
            results.append((name, "SUCCESS", elapsed))
            print(f">>> COMPLETED: {name} in {elapsed:.2f}s\n")
        except Exception as e:
            elapsed = time.time() - t0
            results.append((name, f"FAILED: {e}", elapsed))
            print(f">>> ERROR in {name}: {e}\n")
            sys.exit(1)

    total_elapsed = time.time() - t_start
    print("#" * 80)
    print("STEP 12 EXPERIMENTS EXECUTION SUMMARY")
    print("#" * 80)
    for name, status, el in results:
        print(f"  {name:<48} : {status} ({el:.2f}s)")
    print(f"\nTotal Execution Time: {total_elapsed:.2f}s")
    print("#" * 80)

if __name__ == "__main__":
    run_all()
