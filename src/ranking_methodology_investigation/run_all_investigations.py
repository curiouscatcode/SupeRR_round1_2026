"""
src/ranking_methodology_investigation/run_all_investigations.py
Master Runner for Step 11: Deep Ranking Methodology Investigation

Sequentially executes all 9 investigation scripts and validates that all
required CSV datasets, publication charts, and markdown reports exist and are populated.
"""

import sys
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SCRIPT_DIR = BASE_DIR / "src" / "ranking_methodology_investigation"
OUTPUT_DIR = BASE_DIR / "outputs" / "ranking_methodology_investigation"

INVESTIGATIONS = [
    ("inv01_bumrah_balance.py", "Inv 1: Bumrah & Bowling Balance", [
        "bumrah_component_comparison.csv",
        "01_bumrah_vs_top10_components.png",
        "bumrah_bowling_investigation.md"
    ]),
    ("inv02_sample_threshold.py", "Inv 2: Minimum Sample Threshold", [
        "sample_threshold_analysis.csv",
        "02_sample_threshold_distributions.png",
        "sample_threshold_investigation.md"
    ]),
    ("inv03_bayesian_shrinkage.py", "Inv 3: Bayesian Shrinkage & K=50", [
        "bayesian_shrinkage_variations.csv",
        "03_bayesian_shrinkage_k_curves.png",
        "bayesian_shrinkage_investigation.md"
    ]),
    ("inv04_batting_metrics.py", "Inv 4: Batting Metric Balance", [
        "batting_metric_distributions.csv",
        "04_batting_metric_correlations.png",
        "batting_metric_investigation.md"
    ]),
    ("inv05_bowling_metrics.py", "Inv 5: Bowling Metric Balance", [
        "bowling_metric_distributions.csv",
        "05_bowling_metric_tradeoffs.png",
        "bowling_metric_investigation.md"
    ]),
    ("inv06_phase_specialization.py", "Inv 6: Phase Specialization & Dhoni", [
        "phase_specialization_analysis.csv",
        "06_phase_specialist_vs_overall.png",
        "phase_specialization_investigation.md"
    ]),
    ("inv07_match_consistency.py", "Inv 7: Match-to-Match Consistency", [
        "match_consistency_metrics.csv",
        "07_match_to_match_consistency.png",
        "match_consistency_investigation.md"
    ]),
    ("inv08_target_sensitivity.py", "Inv 8: Target Reconstruction Sensitivity", [
        "target_sensitivity_impact.csv",
        "08_target_sensitivity_distribution.png",
        "target_sensitivity_investigation.md"
    ]),
    ("inv09_ranking_robustness.py", "Inv 9: Overall Ranking Robustness", [
        "ranking_robustness_experiments.csv",
        "09_ranking_robustness_sensitivity.png",
        "ranking_robustness_investigation.md"
    ])
]

def main():
    print("=" * 80)
    print("STEP 11: MASTER INVESTIGATION RUNNER")
    print("=" * 80)
    print(f"Working Directory: {BASE_DIR}")
    print(f"Scripts Directory: {SCRIPT_DIR}")
    print(f"Outputs Directory: {OUTPUT_DIR}")
    print("=" * 80)
    
    start_total = time.time()
    success_count = 0
    all_artifacts_ok = True
    
    for script_name, desc, expected_artifacts in INVESTIGATIONS:
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
            
        # Verify artifacts
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
    print(f"SUMMARY: {success_count}/{len(INVESTIGATIONS)} investigations passed in {total_elapsed:.2f}s")
    if all_artifacts_ok:
        print("[SUCCESS] All 27 required artifacts (9 CSVs, 9 PNGs, 9 MDs) verified.")
    else:
        print("[WARNING] One or more artifacts failed verification.")
    print("=" * 80)

if __name__ == "__main__":
    main()
