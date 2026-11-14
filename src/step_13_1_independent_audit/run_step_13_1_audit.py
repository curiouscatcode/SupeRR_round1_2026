"""
Step 13.1 Independent Audit — Master Runner Suite
=================================================
Executes the full suite of independent audit modules:
1. Module A: Calculation & Ranking Verification (816 Batters, 589 Bowlers)
2. Module B: Effective Sample Size (N_eff) & Reliability Claims Audit
3. Module C: Full-Population Comparisons & Leaderboard Verification
4. Module D: Methodological Evaluation & Discrepancy Register

Validates that all deliverables, CSV reports, and diagnostic charts are produced.
"""

from pathlib import Path
import sys
import time

# Directory setup
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = Path(__file__).resolve().parent
sys.path.append(str(SRC_DIR))

from audit_a_calculations_and_rankings import run_audit_a
from audit_b_effective_sample_size import run_audit_b
from audit_c_comparisons_and_leaderboards import run_audit_c
from audit_d_methodological_evaluation import run_audit_d


def main():
    start_time = time.time()
    print("*" * 80)
    print("STEP 13.1: MASTER INDEPENDENT AUDIT SUITE")
    print("*" * 80)

    # 1. Run Module A
    b_aud, bo_aud, calc_disc, qual_disc = run_audit_a()

    # 2. Run Module B
    neff_df = run_audit_b()

    # 3. Run Module C
    comp_df, ph_transitions = run_audit_c()

    # 4. Run Module D
    claims_df, disc_df = run_audit_d()

    elapsed = time.time() - start_time
    print("*" * 80)
    print(f"STEP 13.1 AUDIT SUITE COMPLETED IN {elapsed:.2f} SECONDS")
    print("*" * 80)

    # Verify Deliverables
    out_dir = BASE_DIR / "outputs" / "step_13_1_independent_audit"
    expected_files = [
        "audit_a_calculation_discrepancies.csv",
        "audit_a_qualification_discrepancies.csv",
        "audit_b_effective_sample_size.csv",
        "audit_c_full_population_verification.csv",
        "audit_c_top10_verification.csv",
        "audit_c_phase_specialist_verification.csv",
        "audit_d_methodological_claims.csv",
        "discrepancy_register.csv",
        "01_independent_score_and_rank_audit.png",
        "02_neff_clustering_audit.png",
        "03_phase_specialist_transitions_audit.png"
    ]

    print("\nVerifying Step 13.1 Audit Deliverables:")
    all_exist = True
    for f in expected_files:
        fp = out_dir / f
        exists = fp.exists()
        size_kb = fp.stat().st_size / 1024 if exists else 0
        status = "OK" if exists else "MISSING"
        print(f"  [{status}] {f:<45} ({size_kb:>8.1f} KB)")
        if not exists:
            all_exist = False

    assert all_exist, "One or more audit deliverable files are missing!"
    print("\nAll 11 Step 13.1 data, discrepancy, and diagnostic deliverables verified successfully.")


if __name__ == "__main__":
    main()
