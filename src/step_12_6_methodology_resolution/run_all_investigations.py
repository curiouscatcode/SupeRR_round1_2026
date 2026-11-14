"""
Step 12.6: Master Investigation Runner
======================================
Sequentially executes all 4 methodology resolution investigations:
- Investigation 1: Batting Formula (BRS3)
- Investigation 2: Bowling Containment
- Investigation 3: Qualification & Match-Level Clustering
- Investigation 4: Ranking Consistency & Top 10 Discrepancy Resolution
"""

import sys
import time
from pathlib import Path

# Add current directory to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.append(str(SCRIPT_DIR))

from investigation_1_batting_formula import run_investigation_1
from investigation_2_bowling_containment import run_investigation_2
from investigation_3_qualification_clustering import run_investigation_3
from investigation_4_top10_reconciliation import run_investigation_4

def run_all_investigations():
    print("#" * 80)
    print("STEP 12.6: METHODOLOGY RESOLUTION — MASTER SUITE RUNNER")
    print("#" * 80)
    t_start = time.time()

    investigations = [
        ("Investigation 1 — Batting Formula (BRS3)", run_investigation_1),
        ("Investigation 2 — Bowling Containment", run_investigation_2),
        ("Investigation 3 — Qualification & Match Clustering", run_investigation_3),
        ("Investigation 4 — Ranking Consistency & Top 10 Reconciliation", run_investigation_4),
    ]

    results = []

    for name, func in investigations:
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
    print("STEP 12.6 INVESTIGATION SUITE SUMMARY")
    print("#" * 80)
    for name, status, el in results:
        print(f"  {name:<60} : {status} ({el:.2f}s)")
    print(f"\nTotal Execution Time: {total_elapsed:.2f}s")
    print("#" * 80)

if __name__ == "__main__":
    run_all_investigations()
