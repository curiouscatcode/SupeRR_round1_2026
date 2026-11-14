"""
src/step_11_2_independent_audit/run_all_audits.py
Master Runner for Step 11.2: Independent Findings Audit

Executes all 8 independent audit scripts and validates that all required
markdown reports, CSV discrepancy datasets, and audit visualization charts are present and valid.
"""

import sys
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SCRIPT_DIR = BASE_DIR / "src" / "step_11_2_independent_audit"
OUTPUT_DIR = BASE_DIR / "outputs" / "step_11_2_independent_audit"

AUDIT_SCRIPTS = [
    ("audit_inv01_bumrah_reconciliation.py", "Audit Inv 1: Bumrah Wicket Rate Reconciliation", [
        "bumrah_reconciliation_table.csv",
        "01_bumrah_reconciliation_audit.png",
        "bumrah_wicket_rate_audit.md"
    ]),
    ("audit_inv02_batting_collinearity.py", "Audit Inv 2: Batting Collinearity & Variance Validation", [
        "batting_variance_decomposition.csv",
        "02_batting_collinearity_audit.png",
        "batting_collinearity_audit.md"
    ]),
    ("audit_inv03_bayesian_k_validation.py", "Audit Inv 3: Bayesian K Value & Shrinkage Validation", [
        "bayesian_k_predictive_evaluation.csv",
        "03_bayesian_k_predictive_curves.png",
        "bayesian_k_validation.md"
    ]),
    ("audit_inv04_match_consistency.py", "Audit Inv 4: Match-Level Consistency & Opportunity Validation", [
        "match_consistency_audit_metrics.csv",
        "04_match_consistency_audit.png",
        "match_consistency_audit.md"
    ]),
    ("audit_inv05_phase_exposure.py", "Audit Inv 5: Phase Exposure Confounding & Specialization", [
        "phase_exposure_reconciliation.csv",
        "05_phase_exposure_audit.png",
        "phase_exposure_audit.md"
    ]),
    ("audit_inv06_sample_threshold.py", "Audit Inv 6: Sample Threshold & Boundary Cliff Revalidation", [
        "sample_threshold_revalidation.csv",
        "06_sample_threshold_audit.png",
        "sample_threshold_audit.md"
    ]),
    ("audit_inv07_target_sensitivity.py", "Audit Inv 7: Target Sensitivity & Shoriful Islam Revalidation", [
        "target_sensitivity_revalidation.csv",
        "07_target_sensitivity_audit.png",
        "target_sensitivity_revalidation.md"
    ]),
    ("audit_inv08_cross_check_and_register.py", "Audit Inv 8: Cross-Check & Discrepancy Register", [
        "step_11_discrepancy_register.csv"
    ])
]

def main():
    print("=" * 80)
    print("STEP 11.2: MASTER INDEPENDENT AUDIT RUNNER")
    print("=" * 80)
    print(f"Working Directory: {BASE_DIR}")
    print(f"Scripts Directory: {SCRIPT_DIR}")
    print(f"Outputs Directory: {OUTPUT_DIR}")
    print("=" * 80)
    
    start_total = time.time()
    success_count = 0
    all_artifacts_ok = True
    
    for script_name, desc, expected_artifacts in AUDIT_SCRIPTS:
        script_path = SCRIPT_DIR / script_name
        print(f"\n>>> Running {desc} ({script_name})...")
        t0 = time.time()
        
        proc = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
        elapsed = time.time() - t0
        
        if proc.returncode == 0:
            print(f"    [PASS] Completed in {elapsed:.2f}s")
            success_count += 1
        else:
            print(f"    [FAIL] Return code: {proc.returncode} in {elapsed:.2f}s")
            print("    Error output:")
            print(proc.stderr[:1000])
            all_artifacts_ok = False
            continue
            
        for art in expected_artifacts:
            art_path = OUTPUT_DIR / art
            if art_path.exists() and art_path.stat().st_size > 0:
                size_kb = art_path.stat().st_size / 1024
                print(f"      - Artifact OK: {art:42s} ({size_kb:.1f} KB)")
            else:
                print(f"      - [MISSING/EMPTY] Artifact: {art}")
                all_artifacts_ok = False
                
    total_elapsed = time.time() - start_total
    print("\n" + "=" * 80)
    print(f"AUDIT SUMMARY: {success_count}/{len(AUDIT_SCRIPTS)} audit scripts passed in {total_elapsed:.2f}s")
    if all_artifacts_ok:
        print("[SUCCESS] All audit artifacts (CSVs, PNGs, MDs) verified.")
    else:
        print("[WARNING] One or more audit artifacts failed verification.")
    print("=" * 80)

if __name__ == "__main__":
    main()
