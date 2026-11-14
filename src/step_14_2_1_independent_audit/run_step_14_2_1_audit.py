"""
Master Runner for Step 14.2.1: Independent Audit of Experimental Workload Formula

Executes all 5 audit modules in sequence:
1. Module 1: Audit Workload Formula Calculations & Spell-Reset Mechanism
2. Module 2: Audit Pressure Classification & Delivery Transitions
3. Module 3: Audit Performance Accounting & Population Consistency
4. Module 4: Audit Eligibility Changes & Ranking Reconciliation
5. Module 5: Discrepancy Register & Final Audit Report Generation
"""

import os
import sys
import time
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MODULES = [
    ("Module 1: Workload & Spell-Reset Audit", "01_audit_workload_and_spell_reset.py"),
    ("Module 2: Pressure Classification & Transitions", "02_audit_pressure_classification_and_transitions.py"),
    ("Module 3: Accounting & Population Consistency", "03_audit_performance_and_accounting_consistency.py"),
    ("Module 4: Eligibility & Ranking Reconciliation", "04_audit_eligibility_and_rankings.py"),
    ("Module 5: Discrepancy Register & Report", "05_generate_audit_report_and_register.py"),
]

def main():
    print("=" * 80)
    print("STEP 14.2.1: INDEPENDENT AUDIT MASTER PIPELINE RUNNER")
    print("=" * 80)

    total_start = time.time()
    for title, script_name in MODULES:
        script_path = os.path.join(SCRIPT_DIR, script_name)
        print(f"\n>>> Running {title} ({script_name})...")
        t0 = time.time()
        res = subprocess.run([sys.executable, script_path], capture_output=False, text=True)
        if res.returncode != 0:
            print(f"\n[ERROR] {script_name} failed with exit code {res.returncode}. Aborting audit.")
            sys.exit(res.returncode)
        print(f">>> Completed {title} in {time.time()-t0:.2f}s.")

    print("\n" + "=" * 80)
    print(f"STEP 14.2.1 AUDIT COMPLETED SUCCESSFULLY IN {time.time()-total_start:.2f}s.")
    print("All audit datasets, discrepancy registers, plots, and reports generated in:")
    print("  c:\\Users\\ASUS\\Desktop\\supeRR_selector\\outputs\\step_14_2_1_independent_audit")
    print("=" * 80)

if __name__ == "__main__":
    main()
