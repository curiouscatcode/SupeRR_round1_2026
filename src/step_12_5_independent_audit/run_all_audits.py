"""
Master Audit Runner: Step 12.5 — Independent Audit of Experimental Models
========================================================================
Sequentially executes all 4 independent audit modules:
- Audit 1: Batting Formula (12.1)
- Audit 2: Bowling Containment (12.2)
- Audit 3: Cohort-Specific Priors & Discrepancy Reconciliation (12.3)
- Audit 4: Confidence-Based Qualification & Clustering (12.4)
"""

import sys
import time
from pathlib import Path

# Add directory to path
SCRIPT_DIR = Path(__file__).resolve().parent

from audit_12_1_batting_formula import run_audit_1
from audit_12_2_bowling_containment import run_audit_2
from audit_12_3_cohort_priors import run_audit_3
from audit_12_4_confidence_qualification import run_audit_4

def run_all_audits():
    print("#" * 80)
    print("STEP 12.5: INDEPENDENT AUDIT OF EXPERIMENTAL MODELS — MASTER RUNNER")
    print("#" * 80)
    t_start = time.time()

    audits = [
        ("Audit 1 — Batting Formula (Exp 12.1)", run_audit_1),
        ("Audit 2 — Bowling Containment (Exp 12.2)", run_audit_2),
        ("Audit 3 — Cohort Priors & Reconciliation (Exp 12.3)", run_audit_3),
        ("Audit 4 — Confidence-Based Qualification (Exp 12.4)", run_audit_4),
    ]

    results = []

    for name, func in audits:
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
    print("STEP 12.5 AUDITS EXECUTION SUMMARY")
    print("#" * 80)
    for name, status, el in results:
        print(f"  {name:<52} : {status} ({el:.2f}s)")
    print(f"\nTotal Execution Time: {total_elapsed:.2f}s")
    print("#" * 80)

if __name__ == "__main__":
    run_all_audits()
