"""
Master Runner for Step 14.2: Experimental Workload Formula Implementation and Impact Analysis

Executes all 5 modules in sequential order:
1. Module 1: Recalculate Workload and Pressure Index (188,330 deliveries)
2. Module 2: Compare Pressure Index & Diagnostic Distributions
3. Module 3: Recalculate Player Performance (816 batters, 589 bowlers)
4. Module 4: Recalculate Step 13 Rankings & Audit Ranking Shifts
5. Module 5: Consolidate Findings & Generate Comprehensive Final Report
"""

import os
import sys
import time
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MODULES = [
    ("Module 1: Workload & PI Recalculation", "01_recalculate_workload_and_pi.py"),
    ("Module 2: PI Comparison & Distributions", "02_compare_pressure_index.py"),
    ("Module 3: Player Performance Recalculation", "03_recalculate_player_performance.py"),
    ("Module 4: Ranking Impact & Evaluation", "04_recalculate_rankings.py"),
    ("Module 5: Consolidated Report Generation", "05_consolidate_and_report.py"),
]

def main():
    print("=" * 80)
    print("STEP 14.2: EXPERIMENTAL WORKLOAD FORMULA MASTER PIPELINE RUNNER")
    print("=" * 80)

    total_start = time.time()
    for title, script_name in MODULES:
        script_path = os.path.join(SCRIPT_DIR, script_name)
        print(f"\n>>> Running {title} ({script_name})...")
        t0 = time.time()
        res = subprocess.run([sys.executable, script_path], capture_output=False, text=True)
        if res.returncode != 0:
            print(f"\n[ERROR] {script_name} failed with exit code {res.returncode}. Aborting pipeline.")
            sys.exit(res.returncode)
        print(f">>> Completed {title} in {time.time()-t0:.2f}s.")

    print("\n" + "=" * 80)
    print(f"STEP 14.2 PIPELINE COMPLETED SUCCESSFULLY IN {time.time()-total_start:.2f}s.")
    print("All datasets, diagnostic charts, and reports generated in:")
    print("  c:\\Users\\ASUS\\Desktop\\supeRR_selector\\outputs\\step_14_2_workload_experiment")
    print("=" * 80)

if __name__ == "__main__":
    main()
