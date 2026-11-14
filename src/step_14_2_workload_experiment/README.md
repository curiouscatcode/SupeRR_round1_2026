# Step 14.2 — Experimental Workload Formula Implementation and Impact Analysis

## Overview
This package implements and evaluates the isolated bowler workload formula revision proposed in Step 9:
- **Baseline v2.0 Formula:** $W_{\text{spell}} = \min(100, (\text{legal\_balls\_in\_spell\_before} / 12) \times 100)$
- **Experimental Formula:** $W_{\text{innings}} = \min(100, (\text{total\_innings\_legal\_balls\_bowled\_before} / 24) \times 100)$

The evaluation runs end-to-end across:
1. All 188,330 historical deliveries (IPL and T20Is 2022–2026).
2. All 816 batters and 589 bowlers.
3. The integrated Step 13 experimental ranking model (BRS3 batting, BoRS bowling, $K=50$ shrinkage, Rule B qualification).

## Strict Guardrails
- Official v2.0 code and production datasets (`data/processed/*`) are untouched and preserved as the audited baseline.
- Steps 1 through 14.1 scripts and outputs are preserved.
- No ranking formulas, component weights, or shrinkage hyperparameters were modified.
- All code and artifacts are strictly isolated in `src/step_14_2_workload_experiment/` and `outputs/step_14_2_workload_experiment/`.

## Directory Structure
```
src/step_14_2_workload_experiment/
├── 01_recalculate_workload_and_pi.py      # Module 1: Vectorized PI engine recalculation
├── 02_compare_pressure_index.py           # Module 2: PI distribution audit & charts
├── 03_recalculate_player_performance.py   # Module 3: Batting & bowling performance
├── 04_recalculate_rankings.py             # Module 4: Step 13 ranking re-evaluation
├── 05_consolidate_and_report.py           # Module 5: Synthesis & 7-question answers
├── run_step_14_2_experiment.py            # Master pipeline runner
└── README.md                              # Technical documentation

outputs/step_14_2_workload_experiment/
├── delivery_pressure_index_exp14_2.csv    # 188,330 deliveries with experimental PI
├── exp14_2_pi_comparison_summary.csv      # Phase and innings summary statistics
├── 01_workload_and_pi_distributions.png   # 4-panel diagnostic plot (workload & PI)
├── report_pi_comparison.md                # Module 2 detailed PI comparison report
├── batter_performance_exp14_2.csv         # 816 batters evaluated under experimental PI
├── bowler_performance_exp14_2.csv         # 589 bowlers evaluated under experimental PI
├── exp14_2_batter_rankings.csv            # 816 batters ranked under BRS3 + Rule B
├── exp14_2_bowler_rankings.csv            # 589 bowlers ranked under BoRS + Rule B
├── exp14_2_ranking_comparison.csv         # Bowler ranking comparison (Step 13 vs Exp)
├── exp14_2_phase_specialist_rankings.csv  # PP, Middle, and Death specialist rankings
├── exp14_2_phase_specialist_comparison.csv# Specialist comparison across phases
├── 02_ranking_impact_and_shifts.png       # 4-panel diagnostic plot (ranking shifts)
├── report_ranking_impact.md               # Module 4 detailed ranking impact report
└── step_14_2_final_workload_impact_report.md # Consolidated authoritative final report
```

## Running the Complete Experiment
To reproduce all calculations, tables, plots, and reports from scratch:
```bash
python src/step_14_2_workload_experiment/run_step_14_2_experiment.py
```
Total runtime is approximately 10 to 15 seconds.
