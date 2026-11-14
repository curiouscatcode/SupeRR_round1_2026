"""
Master Runner: Step 14.1 — Independent Audit of Step 14 Findings
Executes all audit scripts in sequence and verifies all generated audit deliverables.
"""

import os
import sys
import time
import subprocess

BASE_DIR = r"c:\Users\ASUS\Desktop\supeRR_selector"
SCRIPT_DIR = os.path.join(BASE_DIR, "src", "step_14_1_independent_audit")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "step_14_1_independent_audit")

AUDIT_MODULES = [
    ("Investigation 1: Workload Formula Audit", "audit_1_workload_formula.py"),
    ("Investigation 2: Batting BRS3 Audit", "audit_2_batting_brs3.py"),
    ("Investigation 3: Qualification & Neff Audit", "audit_3_qualification_neff.py"),
    ("Investigation 4: Shrinkage K Sensitivity Audit", "audit_4_shrinkage_k.py"),
    ("Investigation 5: Contradictions & Claims Audit", "audit_5_contradictions_and_claims.py"),
    ("Compilation: Master Report & Register", "compile_step_14_1_audit.py")
]

EXPECTED_OUTPUTS = [
    # Reports
    "report_1_workload_audit.md",
    "report_2_batting_brs3_audit.md",
    "report_3_qualification_neff_audit.md",
    "report_4_shrinkage_k_audit.md",
    "report_5_contradictions_and_claims_audit.md",
    "step_14_1_final_audit_report.md",
    # Datasets
    "step_14_1_discrepancy_register.csv",
    "audit_recalculated_k_sensitivity.csv",
    "step_14_1_contradictions_inventory.csv"
]

def main():
    print("=" * 80)
    print("STEP 14.1 MASTER AUDIT SUITE RUNNER")
    print("Independent Audit of Step 14 Findings")
    print("=" * 80)
    start_total = time.time()

    all_passed = True
    module_timings = []

    for name, script_name in AUDIT_MODULES:
        script_path = os.path.join(SCRIPT_DIR, script_name)
        print(f"\n>>> Running {name} ({script_name})...")
        t0 = time.time()
        res = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        dur = time.time() - t0
        module_timings.append((name, script_name, dur, res.returncode == 0))

        if res.returncode != 0:
            print(f"FAILED: {script_name} exited with code {res.returncode}")
            print("STDOUT:\n", res.stdout)
            print("STDERR:\n", res.stderr)
            all_passed = False
            break
        else:
            print(f"Completed in {dur:.2f}s (Exit code 0)")

    # Output Verification
    print("\n" + "=" * 80)
    print("VERIFYING GENERATED AUDIT DELIVERABLES")
    print("=" * 80)
    missing = []
    for fname in EXPECTED_OUTPUTS:
        fpath = os.path.join(OUTPUT_DIR, fname)
        if not os.path.exists(fpath):
            missing.append(fname)
            print(f"  [MISSING] {fname}")
        else:
            size_kb = os.path.getsize(fpath) / 1024.0
            print(f"  [VERIFIED] {fname} ({size_kb:.1f} KB)")

    total_dur = time.time() - start_total
    print("\n" + "=" * 80)
    print("STEP 14.1 AUDIT SUITE SUMMARY")
    print("=" * 80)
    for name, sname, dur, success in module_timings:
        status_str = "PASS" if success else "FAIL"
        print(f"  {name:<45} : {status_str} ({dur:.2f}s)")

    print(f"\nTotal Audit Execution Time: {total_dur:.2f}s")
    if all_passed and not missing:
        print("\nALL STEP 14.1 AUDIT CHECKS PASSED PERFECTLY!")
        print(f"Audit reports and datasets available in: {OUTPUT_DIR}")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\nSTEP 14.1 COMPLETED WITH WARNINGS OR ERRORS.")
        sys.exit(1)

if __name__ == "__main__":
    main()
