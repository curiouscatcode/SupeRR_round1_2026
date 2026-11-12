# Step 10: Independent Validation of Experimental Pressure Index Models

## Overview & Architecture

This directory contains the independent, clean-room audit and validation suite developed during **Step 10**. The objective of this suite is to rigorously evaluate the mathematical soundness, implementation correctness, edge-case behavior, and ranking pipeline fidelity of the experimental Pressure Index (PI) models proposed in **Step 9**.

### Critical Audit Boundaries
- **Zero In-Place Mutation**: The official baseline dataset (`data/processed/`), the production ranking engine (`src/rank_players.py`), and the official Pressure Index engine (`src/calculate_pressure_index.py`) remain untouched.
- **Independent Validation Directory**: All validation scripts reside in `src/experimental_model_validation/`.
- **Dedicated Artifact Directory**: All verification figures, discrepancy CSVs, authoritative rankings, and validation reports are stored in `outputs/experimental_model_validation/`.

---

## Directory Structure

```
src/experimental_model_validation/
├── README.md                      # Architecture documentation and reproduction instructions
├── run_validation.py              # Master runner executing all 5 validation modules
├── validate_workload.py           # Validation A: Bowler Workload implementation & distribution audit
├── validate_phase_relative.py     # Validation B: Phase-Relative percentiles, discrete cutoffs & ties
├── validate_second_innings_pp.py  # Validation C: 2nd Innings PP simulation & scenario validation
├── validate_ranking_pipeline.py   # Validation D & E: Authoritative ranking pipeline & discrepancy audit
└── validate_combined_model.py     # Validation F: Combined Model (M4) reproducibility & interaction dynamics
```

---

## Validation Scripts Summary

### 1. `validate_workload.py` (Validation A)
- **Purpose**: Audits the Bowler Fatigue & Workload experimental model (Spell Workload & Innings Workload).
- **Core Checks**:
  - Excludes pre-delivery ball from spell workload: $W_{\text{spell}} = \frac{\text{legal\_balls\_in\_spell}}{6} \times 100\%$.
  - Resets spell on over transitions $\ge 2$ overs apart.
  - Excludes wide and no-ball extra deliveries from legal workload counters.
  - Verifies exact saturation cap at 100% (6 legal balls in a spell).
  - Validates delivery-level PI deltas across match phases.
- **Outputs**:
  - `outputs/experimental_model_validation/01_workload_validation_comparison.png`
  - `outputs/experimental_model_validation/workload_validation_discrepancies.csv`
- **Verdict**: `PASS`.

### 2. `validate_phase_relative.py` (Validation B)
- **Purpose**: Audits the Phase-Relative High Pressure Cutoff model (Empirical 80th Percentile per phase).
- **Core Checks**:
  - Validates empirical P80 thresholds: Batting (PP: 50.50, Middle: 50.92, Death: 62.40) and Bowling (PP: 60.27, Middle: 52.73, Death: 41.88).
  - Investigates discrete ties at boundary values (specifically 588 deliveries tied at 62.40 in Death overs batting).
  - Confirms exact player sample count shifts across all 1,405 players.
  - Verifies Tier 1 cohort expansions: Model 2 (+71 batters: 116 -> 187, with 72 new entrants and 1 dropout: Odean Smith; +54 bowlers: 113 -> 167); Model 4 (+72 batters: 116 -> 188, with 73 new entrants and 1 dropout: Odean Smith; +52 bowlers: 113 -> 165).
- **Outputs**:
  - `outputs/experimental_model_validation/02_phase_relative_ties_and_cutoffs.png`
  - `outputs/experimental_model_validation/phase_relative_validation_discrepancies.csv`
- **Verdict**: `PASS`.

### 3. `validate_second_innings_pp.py` (Validation C)
- **Purpose**: Audits the Second-Innings Powerplay recalibration and the "settled batter trap".
- **Core Checks**:
  - Simulates all 630 controlled scenarios across Required Run Rate (6.0 to 14.0), Wickets Lost (0 to 4), and Overs Completed (0 to 5).
  - Audits historical delivery population (29,597 second-innings PP deliveries).
  - Identifies steep chases (RRR $\ge$ 10.0, 9,415 balls), confirming 6,591 were under-classified as Low/Moderate in the baseline.
  - Validates Variant 1 (Target Pressure Floor: RRR / CRR / Wickets) reclassifying 1,831 balls to High Pressure while causing zero false positives in modest chases (RRR < 8.0).
  - Confirms the settled batter trap in Variant 2 where a batter at 30*(15) was penalized.
- **Outputs**:
  - `outputs/experimental_model_validation/03_second_innings_pp_validation.png`
  - `outputs/experimental_model_validation/second_innings_pp_validation_discrepancies.csv`
- **Verdict**: `PASS`.

### 4. `validate_ranking_pipeline.py` (Validation D & E)
- **Purpose**: Authoritative reconciliation of the ranking engine and full player population ranking audit.
- **Core Checks**:
  - Line-by-line parity with production `src/rank_players.py`.
  - Discovered two critical implementation discrepancies in Step 9:
    1. **Unfiltered Post-Target Deliveries**: 233 deliveries with `runs_required <= 0` were included in Step 9 but excluded in Step 5/6.2, shifting Marco Jansen by 2 HP balls and 5 rank spots.
    2. **Omission of Wide/No-Ball Extras Runs**: Step 9 pre-filtered legal balls before aggregating runs conceded, dropping 1,018 penalty runs and artificially lowering population bowling economy from 9.06 to 8.75.
  - Built authoritative rankings for all models (M0, M1, M2, M3, M4) with 100.00% exact parity to official Step 6.2 for Model 0.
- **Outputs**:
  - `outputs/experimental_model_validation/04_ranking_pipeline_discrepancy_analysis.png`
  - `outputs/experimental_model_validation/ranking_pipeline_validation_discrepancies.csv`
  - `outputs/experimental_model_validation/authoritative_experimental_rankings_batters.csv`
  - `outputs/experimental_model_validation/authoritative_experimental_rankings_bowlers.csv`
- **Verdict**: `PASS` (with documented discrepancies in Step 9).

### 5. `validate_combined_model.py` (Validation F)
- **Purpose**: Audits the Combined Model (Model 4) incorporating workload, phase-relative cutoffs, and 2nd innings PP recalibration.
- **Core Checks**:
  - Analyzes non-linear compounding and percentile threshold recalculation.
  - Confirms Death Bowling P80 rises from 41.98 to 48.37 due to innings fatigue.
  - Confirms PP Batting P80 rises from 50.50 to 52.86 due to chase recalibration.
  - Re-evaluates Tier 1 cohort transitions: Batters (+73 entrants, -1 dropout -> 188 players), Bowlers (+52 entrants, 0 dropouts -> 165 players).
  - Confirms rank correlations: Batter Spearman $\rho = 0.762$, Bowler Spearman $\rho = 0.720$.
- **Outputs**:
  - `outputs/experimental_model_validation/05_combined_model_interaction_effects.png`
  - `outputs/experimental_model_validation/combined_model_validation_discrepancies.csv`
- **Verdict**: `PASS`.

---

## How to Reproduce

To execute the entire validation suite and verify all artifacts:

```bash
python src/experimental_model_validation/run_validation.py
```

All 5 validation figures, 5 discrepancy CSVs, 2 authoritative ranking CSVs, and the comprehensive audit report will be generated and validated.
