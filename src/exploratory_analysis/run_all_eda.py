"""
Master Orchestration Script: Run All EDA Modules
================================================
Executes:
1. eda_01_distributions.py
2. eda_02_sample_size_vs_reliability.py
3. eda_03_player_heatmaps.py
4. eda_04_phase_analysis.py
5. eda_05_ranking_model_mechanics.py
6. eda_06_clutch_regime_shifts.py
7. eda_07_outliers_and_anomalies.py

Verifies the presence and integrity of all generated charts (19 images) and anomaly CSV files (5 CSVs).
"""

import sys
import subprocess
from pathlib import Path

EDA_DIR = Path("src/exploratory_analysis")
OUT_DIR = Path("outputs/exploratory_analysis")

SCRIPTS = [
    ("eda_01_distributions.py", "Part 1: Full Population Distributions"),
    ("eda_02_sample_size_vs_reliability.py", "Part 2: Sample Size vs Reliability"),
    ("eda_03_player_heatmaps.py", "Part 3: Full Player Metric Heatmaps"),
    ("eda_04_phase_analysis.py", "Part 4: Phase-Wise Performance Analysis"),
    ("eda_05_ranking_model_mechanics.py", "Part 5: Ranking Model Mechanics & Shrinkage Dynamics"),
    ("eda_06_clutch_regime_shifts.py", "Part 6: Clutch Regime Shifts"),
    ("eda_07_outliers_and_anomalies.py", "Part 7: Outlier Investigation & Anomaly CSV Generation")
]

EXPECTED_CHARTS = [
    "01_population_distributions_overview.png",
    "02_raw_vs_bayesian_distributions.png",
    "03_tier_comparisons_boxplots.png",
    "04_batter_sample_size_vs_brs.png",
    "05_bowler_sample_size_vs_bors.png",
    "06_small_sample_score_volatility.png",
    "07_tier1_batters_heatmap.png",
    "08_tier1_bowlers_heatmap.png",
    "09_tier2_specialists_heatmap.png",
    "10_phase_performance_transitions.png",
    "11_phase_specialist_disparity.png",
    "12_cross_phase_player_profiles.png",
    "13_bayesian_shrinkage_mechanics.png",
    "14_component_influence_and_correlations.png",
    "15_shrinkage_rank_movements.png",
    "16_batter_clutch_regime_deltas.png",
    "17_bowler_clutch_regime_deltas.png",
    "18_anomaly_multidimensional_clusters.png",
    "19_methodology_vulnerabilities_showcase.png"
]

EXPECTED_CSVS = [
    "flagged_batters_anomalies.csv",
    "flagged_bowlers_anomalies.csv",
    "small_sample_high_score_players.csv",
    "conflicting_metrics_players.csv",
    "methodology_vulnerabilities_cases.csv"
]


def run_pipeline():
    print("=" * 70)
    print("STARTING FULL PLAYER EXPLORATORY DATA ANALYSIS (EDA) SUITE")
    print("=" * 70)
    
    for script_name, description in SCRIPTS:
        script_path = EDA_DIR / script_name
        print(f"\n>>> Running {description} ({script_name})...")
        cmd = [sys.executable, str(script_path)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"FAILED: {script_name}")
            print(res.stderr)
            sys.exit(1)
        else:
            print(res.stdout.strip())
            
    print("\n" + "=" * 70)
    print("VERIFYING GENERATED ARTIFACTS IN outputs/exploratory_analysis/")
    print("=" * 70)
    
    missing_charts = []
    for c in EXPECTED_CHARTS:
        p = OUT_DIR / c
        if p.exists() and p.stat().st_size > 0:
            print(f" [PASS] Chart: {c:<45} ({p.stat().st_size / 1024:.1f} KB)")
        else:
            missing_charts.append(c)
            print(f" [FAIL] MISSING: {c}")

    missing_csvs = []
    for f in EXPECTED_CSVS:
        p = OUT_DIR / f
        if p.exists() and p.stat().st_size > 0:
            print(f" [PASS] CSV  : {f:<45} ({p.stat().st_size / 1024:.1f} KB)")
        else:
            missing_csvs.append(f)
            print(f" [FAIL] MISSING: {f}")

    if not missing_charts and not missing_csvs:
        print("\n" + "=" * 70)
        print("ALL 19 CHARTS AND 5 ANOMALY CSVS VERIFIED WITH 100% INTEGRITY!")
        print("=" * 70)
    else:
        print(f"\nERROR: Missing {len(missing_charts)} charts and {len(missing_csvs)} CSVs.")
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
