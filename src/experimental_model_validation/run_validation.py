"""
src/experimental_model_validation/run_validation.py
Master runner for Step 10: Independent Validation of Experimental Pressure Index Models.

Executes all 5 validation modules in sequential order and verifies that all
required visual and tabular artifacts are generated with non-zero size.

Usage:
    python src/experimental_model_validation/run_validation.py
"""

import sys
import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODULE_DIR = BASE_DIR / "src" / "experimental_model_validation"
OUTPUT_DIR = BASE_DIR / "outputs" / "experimental_model_validation"

SCRIPTS = [
    ("validate_workload.py", "Validation A: Bowler Workload Implementation & Distribution Audit"),
    ("validate_phase_relative.py", "Validation B: Phase-Relative Thresholds & Discrete Cutoff Mechanics"),
    ("validate_second_innings_pp.py", "Validation C: 2nd Innings Powerplay Simulation & Scenario Testing"),
    ("validate_ranking_pipeline.py", "Validation D: Authoritative Ranking Pipeline & Discrepancy Reconciliation"),
    ("validate_combined_model.py", "Validation F: Combined Model (Model 4) Reproducibility & Interaction Audit")
]

REQUIRED_ARTIFACTS = [
    # Figures (5)
    "01_workload_validation_comparison.png",
    "02_phase_relative_ties_and_cutoffs.png",
    "03_second_innings_pp_validation.png",
    "04_ranking_pipeline_discrepancy_analysis.png",
    "05_combined_model_interaction_effects.png",
    # Discrepancy Tables (5)
    "workload_validation_discrepancies.csv",
    "phase_relative_validation_discrepancies.csv",
    "second_innings_pp_validation_discrepancies.csv",
    "ranking_pipeline_validation_discrepancies.csv",
    "combined_model_validation_discrepancies.csv",
    # Authoritative Rankings (2)
    "authoritative_experimental_rankings_batters.csv",
    "authoritative_experimental_rankings_bowlers.csv",
    # Documentation & Reports (2)
    "experimental_model_validation_report.md"
]

def run_script(script_name, description):
    script_path = MODULE_DIR / script_name
    print(f"\n{'='*80}")
    print(f"RUNNING: {description}")
    print(f"Script: {script_path}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    elapsed = time.time() - start_time
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
        
    if result.returncode != 0:
        print(f"ERROR: {script_name} failed with return code {result.returncode} ({elapsed:.1f}s)")
        return False, elapsed
    else:
        print(f"SUCCESS: {script_name} completed in {elapsed:.1f}s")
        return True, elapsed

def verify_artifacts():
    print(f"\n{'='*80}")
    print("VERIFYING ARTIFACT GENERATION & INTEGRITY")
    print(f"{'='*80}\n")
    
    all_passed = True
    for artifact_name in REQUIRED_ARTIFACTS:
        if artifact_name == "experimental_model_validation_report.md":
            artifact_path = OUTPUT_DIR / artifact_name
        else:
            artifact_path = OUTPUT_DIR / artifact_name
            
        if not artifact_path.exists():
            print(f" [MISSING] {artifact_name}")
            all_passed = False
        else:
            size_kb = artifact_path.stat().st_size / 1024
            if size_kb == 0:
                print(f" [EMPTY]   {artifact_name} (0 KB)")
                all_passed = False
            else:
                print(f" [EXISTS]  {artifact_name} ({size_kb:.1f} KB)")
                
    readme_path = MODULE_DIR / "README.md"
    if not readme_path.exists():
        print(f" [MISSING] README.md in {MODULE_DIR}")
        all_passed = False
    else:
        size_kb = readme_path.stat().st_size / 1024
        print(f" [EXISTS]  README.md ({size_kb:.1f} KB)")
        
    return all_passed

def main():
    print("================================================================================")
    print("STEP 10: MASTER AUDIT RUNNER FOR EXPERIMENTAL PRESSURE INDEX MODELS")
    print("================================================================================")
    
    overall_start = time.time()
    results = []
    
    for script_name, description in SCRIPTS:
        success, elapsed = run_script(script_name, description)
        results.append((script_name, success, elapsed))
        if not success:
            print("\nAborting master runner due to script failure.")
            sys.exit(1)
            
    print(f"\n{'='*80}")
    print("EXECUTION SUMMARY")
    print(f"{'='*80}")
    for script_name, success, elapsed in results:
        status = "PASSED" if success else "FAILED"
        print(f"  {script_name:<30} : {status} ({elapsed:.1f}s)")
        
    artifacts_ok = verify_artifacts()
    total_time = time.time() - overall_start
    
    print(f"\n{'='*80}")
    if artifacts_ok:
        print(f"ALL 5 VALIDATION MODULES AND ARTIFACTS VERIFIED SUCCESSFULLY ({total_time:.1f}s)")
        print(f"{'='*80}\n")
    else:
        print(f"WARNING: Some artifacts were missing or incomplete. Please check above.")
        print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
