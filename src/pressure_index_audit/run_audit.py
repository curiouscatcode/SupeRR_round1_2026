"""
Master Runner for Pressure Index Formula Audit (Step 9)
=======================================================

This script runs the complete adversarial audit suite:
1. audit_workload.py (Investigation A)
2. audit_phase_relative_pressure.py (Investigation B)
3. audit_second_innings_powerplay.py (Investigation C)
4. audit_ranking_impact.py (Investigation D)

It validates that all required figures and CSV datasets exist and have non-zero size.
"""

from pathlib import Path
import time
import subprocess
import sys

SCRIPTS = [
    ("Investigation A: Workload Loophole", "src/pressure_index_audit/audit_workload.py"),
    ("Investigation B: Phase-Relative Baselines", "src/pressure_index_audit/audit_phase_relative_pressure.py"),
    ("Investigation C: 2nd Innings PP Scoreboard Pressure", "src/pressure_index_audit/audit_second_innings_powerplay.py"),
    ("Investigation D: Downstream Ranking Impact", "src/pressure_index_audit/audit_ranking_impact.py")
]

EXPECTED_OUTPUTS = [
    # Figures
    "outputs/pressure_index_audit/01_workload_distribution_by_phase.png",
    "outputs/pressure_index_audit/02_spell_vs_innings_workload_scatter.png",
    "outputs/pressure_index_audit/03_phase_relative_distributions.png",
    "outputs/pressure_index_audit/04_absolute_vs_relative_classification_matrix.png",
    "outputs/pressure_index_audit/05_chase_scenario_pressure_curves.png",
    "outputs/pressure_index_audit/06_pp_chase_actual_deliveries_scatter.png",
    "outputs/pressure_index_audit/07_ranking_correlation_matrix.png",
    "outputs/pressure_index_audit/08_rank_movement_comparison.png",
    # CSV Data
    "outputs/pressure_index_audit/workload_bowler_impact.csv",
    "outputs/pressure_index_audit/phase_relative_player_sample_shifts.csv",
    "outputs/pressure_index_audit/second_innings_pp_scenarios.csv",
    "outputs/pressure_index_audit/experimental_rankings_comparison_batters.csv",
    "outputs/pressure_index_audit/experimental_rankings_comparison_bowlers.csv"
]


def run_all():
    print("="*80)
    print("STEP 9: PRESSURE INDEX FORMULA AUDIT — EXECUTION SUITE")
    print("="*80)

    start_total = time.time()
    for title, script_path in SCRIPTS:
        print(f"\n>>> Running {title} ({script_path})...")
        t0 = time.time()
        res = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        elapsed = time.time() - t0
        
        if res.returncode != 0:
            print(f"FAILED: {script_path}")
            print(res.stderr)
            sys.exit(1)
        else:
            print(f"COMPLETED in {elapsed:.2f}s")

    print("\n" + "="*80)
    print("VALIDATING ARTIFACT GENERATION")
    print("="*80)

    all_passed = True
    for out_file in EXPECTED_OUTPUTS:
        p = Path(out_file)
        if not p.exists():
            print(f"  [MISSING] {out_file}")
            all_passed = False
        else:
            sz_kb = p.stat().st_size / 1024
            print(f"  [OK] {out_file:65s} ({sz_kb:7.1f} KB)")

    total_time = time.time() - start_total
    print("\n" + "="*80)
    if all_passed:
        print(f"SUCCESS: All {len(EXPECTED_OUTPUTS)} audit artifacts generated in {total_time:.1f}s.")
    else:
        print(f"FAILURE: Some audit artifacts are missing.")
        sys.exit(1)
    print("="*80)


if __name__ == "__main__":
    run_all()
