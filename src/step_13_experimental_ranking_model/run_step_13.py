"""
Step 13: Integrated Experimental Ranking Model Master Runner
============================================================
Executes the full Step 13 experimental workflow:
1. rank_players_exp13.py: Computes BRS_3, retains BoRS, applies Rule B qualification.
2. compare_exp13_vs_official.py: Evaluates full population deltas, tier shifts, elite overlaps, phase integrity.
3. Validates that all deliverables and figures exist.
"""

from pathlib import Path
import sys
import time

# Directory setup
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = Path(__file__).resolve().parent
sys.path.append(str(SRC_DIR))

from rank_players_exp13 import run_exp13_pipeline
from compare_exp13_vs_official import run_comparative_analysis

def main():
    start_time = time.time()
    print("*" * 80)
    print("STEP 13: MASTER RUNNER — INTEGRATED EXPERIMENTAL RANKING MODEL")
    print("*" * 80)
    
    # Run Step 1: Integrated Ranking Pipeline
    exp13_bat, exp13_bowl, exp13_phase = run_exp13_pipeline()
    
    # Run Step 2: Comparative Analysis Pipeline
    b_merged, bo_merged, tier_changes, top10_df, phase_comp = run_comparative_analysis()
    
    elapsed = time.time() - start_time
    print("*" * 80)
    print(f"STEP 13 COMPLETED SUCCESSFULLY IN {elapsed:.2f} SECONDS")
    print("*" * 80)
    
    # Deliverables verification
    out_dir = BASE_DIR / "outputs" / "step_13_experimental_ranking_model"
    expected_files = [
        "exp13_batter_rankings.csv",
        "exp13_bowler_rankings.csv",
        "exp13_phase_specialist_rankings.csv",
        "exp13_batter_comparison.csv",
        "exp13_bowler_comparison.csv",
        "exp13_tier_qualification_changes.csv",
        "exp13_top10_comparison.csv",
        "exp13_phase_specialist_comparison.csv",
        "01_score_and_rank_distributions.png",
        "02_tier_qualification_changes.png",
        "03_top10_movement.png",
        "04_phase_specialist_analysis.png"
    ]
    
    print("\nVerifying Step 13 Deliverables:")
    all_exist = True
    for f in expected_files:
        fp = out_dir / f
        exists = fp.exists()
        size_kb = fp.stat().st_size / 1024 if exists else 0
        status = "OK" if exists else "MISSING"
        print(f"  [{status}] {f:<40} ({size_kb:>8.1f} KB)")
        if not exists:
            all_exist = False
            
    assert all_exist, "One or more expected deliverable files are missing!"
    print("\nAll 12 Step 13 data and visualization deliverables successfully verified.")

if __name__ == "__main__":
    main()
