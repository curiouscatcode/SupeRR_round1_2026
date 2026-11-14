"""
Master Runner: Step 14 — Independent Historical Methodology Validation
Executes all validation scripts in sequence and verifies all generated artifacts.
"""

import os
import sys
import time
import subprocess

BASE_DIR = r"c:\Users\ASUS\Desktop\supeRR_selector"
SCRIPT_DIR = os.path.join(BASE_DIR, "src", "step_14_historical_methodology_validation")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "step_14_historical_methodology_validation")

MODULES = [
    ("Investigation A: Pressure Index Validity", "inv_a_pressure_index_validity.py"),
    ("Investigation B: Batting Reliability (BRS_3)", "inv_b_batting_reliability.py"),
    ("Investigation C: Bowling Reliability (BoRS)", "inv_c_bowling_reliability.py"),
    ("Investigation D: Qualification & Sample Reliability", "inv_d_qualification_reliability.py"),
    ("Investigation E: Ranking Robustness & Sensitivity", "inv_e_ranking_robustness.py"),
    ("Investigation F: Final Assessment & Synthesis", "inv_f_methodological_assessment.py")
]

EXPECTED_OUTPUTS = [
    # Visualizations
    "01_pressure_index_phase_innings_validation.png",
    "02_batting_component_tradeoffs_brs3.png",
    "03_bowling_component_orthogonality_bors.png",
    "04_qualification_rule_b_boundary_clustering.png",
    "05_ranking_sensitivity_full_population.png",
    # Datasets
    "exp14_pressure_index_distributions.csv",
    "exp14_batter_full_population_evaluation.csv",
    "exp14_bowler_full_population_evaluation.csv",
    "exp14_qualification_boundary_analysis.csv",
    "exp14_sensitivity_experiments.csv",
    "discrepancy_register.csv",
    # Reports
    "report_a_pressure_index_validity.md",
    "report_b_batting_reliability.md",
    "report_c_bowling_reliability.md",
    "report_d_qualification_reliability.md",
    "report_e_ranking_robustness.md",
    "step_14_final_methodological_validation_report.md"
]

def main():
    print("=" * 80)
    print("STEP 14 MASTER VALIDATION RUNNER")
    print("Independent Historical Methodology Validation")
    print("=" * 80)
    start_total = time.time()

    all_passed = True
    module_timings = []

    for name, script_name in MODULES:
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
    print("VERIFYING GENERATED DELIVERABLES")
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
    print("STEP 14 VALIDATION SUITE SUMMARY")
    print("=" * 80)
    for name, sname, dur, success in module_timings:
        status_str = "PASS" if success else "FAIL"
        print(f"  {name:<45} : {status_str} ({dur:.2f}s)")

    print(f"\nTotal Suite Execution Time: {total_dur:.2f}s")
    if all_passed and not missing:
        print("\nALL STEP 14 VALIDATION CHECKS PASSED PERFECTLY!")
        print(f"Reports and artifacts available in: {OUTPUT_DIR}")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\nSTEP 14 COMPLETED WITH WARNINGS OR ERRORS.")
        sys.exit(1)

if __name__ == "__main__":
    main()
