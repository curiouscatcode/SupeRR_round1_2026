# SupeRR Selector: T20 Player Performance & Reliability Under Pressure

## Overview

**SupeRR Selector** is a sports analytics project designed to evaluate how professional T20 cricket players (batters and bowlers) perform under pressure and to rank the most reliable clutch performers.

The engine models ball-by-ball match context (Required Run Rate, wickets remaining, phase of the match, bowler spells, target deficits) into a granular **Pressure Index (PI)** bounded in $[0, 100]$. Using this index, player performances are evaluated across High Pressure ($PI \ge 61$) and Low/Moderate Pressure ($PI \le 60$) regimes, applying Bayesian shrinkage ($K=50$) to normalize metrics and compute authoritative **Batter Reliability Scores (BRS)** and **Bowler Reliability Scores (BoRS)**.

---

## Repository Structure

```
supeRR_selector/
├── README.md                      # Project overview, architecture, and reproduction instructions
├── .gitignore                     # Git ignore rules protecting virtualenvs, secrets, and large datasets
│
├── data/                          # Match metadata and processed rankings
│   ├── competitions.csv           # Competition metadata
│   ├── teams.csv                  # Team metadata
│   ├── matches.csv                # Match headers (dates, venues, toss, result)
│   ├── playing_eleven.csv         # Match lineups and player IDs
│   ├── competition_team_player_mapping.csv
│   │
│   └── processed/                 # Official v2.0 Production Rankings & Aggregations
│       ├── batter_performance.csv              # Aggregated batter statistics across pressure regimes
│       ├── bowler_performance.csv              # Aggregated bowler statistics across pressure regimes
│       ├── batter_reliability_rankings.csv     # Official v2.0 Batter Rankings (116 Tier 1 Qualified)
│       ├── bowler_reliability_rankings.csv     # Official v2.0 Bowler Rankings (113 Tier 1 Qualified)
│       └── phase_specialist_rankings.csv       # Powerplay, Middle, and Death Phase Specialists
│
├── src/                           # Core Engine Implementation & Audits
│   ├── inspect_data.py            # Data inspection & integrity checks
│   ├── prepare_match_data.py      # Match state reconstruction & target tracking
│   ├── calculate_pressure_index.py# Official v2.0 Pressure Index calculation engine
│   ├── evaluate_player_performance.py # Player metric aggregation by pressure regime
│   ├── rank_players.py            # Official v2.0 Bayesian ranking engine
│   │
│   ├── visualizations/            # Step 7: Cricket Analysis & Visualization Suite
│   ├── exploratory_analysis/      # Step 8: Full Population Exploratory Data Analysis (EDA)
│   ├── pressure_index_audit/      # Step 9: Adversarial Audit of Experimental Models (M1-M4)
│   └── experimental_model_validation/ # Step 10: Independent Clean-Room Validation Suite
│
├── outputs/                       # Reports, Figures, and Verification Datasets
│   ├── visualizations/            # 16 figures & cricket_analysis_report.md
│   ├── exploratory_analysis/      # 19 figures & exploratory_analysis_report.md
│   ├── pressure_index_audit/      # 8 figures, experimental CSVs & pressure_index_audit_report.md
│   └── experimental_model_validation/ # 5 verification figures, 5 discrepancy CSVs,
│                                      # authoritative experimental rankings (M0-M4),
│                                      # and experimental_model_validation_report.md
│
├── problem_statement_pdf/         # Original problem statement specification
└── scratch/                       # Internal development scripts and exploratory scratchpads
```

---

## Datasets & Reproduction Guide

### Large Datasets Excluded from Version Control
In accordance with repository size best practices, large datasets (>40 MB) are excluded via `.gitignore`:
1. `data/ball_by_ball.csv` (41.3 MB, 188,330 deliveries): Raw ball-by-ball tracking dataset. Expected to be placed into `data/`.
2. `data/processed/delivery_match_state.csv` (48.5 MB): Reconstructed match-state dataset.
3. `data/processed/delivery_pressure_index.csv` (57.3 MB): Calculated delivery-level Pressure Index dataset.

### Pipeline Reproduction Steps
To regenerate the processed datasets and official rankings from raw data:
```bash
# 1. Prepare delivery-level match state
python src/prepare_match_data.py

# 2. Compute official delivery-level Pressure Index
python src/calculate_pressure_index.py

# 3. Evaluate player performance by pressure regime
python src/evaluate_player_performance.py

# 4. Generate official v2.0 reliability rankings
python src/rank_players.py
```

### Running the Step 10 Independent Validation Suite
To execute the complete independent verification suite and regenerate all Step 10 discrepancy tables, verification charts, and authoritative experimental rankings:
```bash
python src/experimental_model_validation/run_validation.py
```

---

## Key Methodological Governance & Audit Status

- **Official Model Status (v2.0)**: The official Pressure Index engine (`calculate_pressure_index.py`) and official rankings (`data/processed/batter_reliability_rankings.csv` and `bowler_reliability_rankings.csv`) represent the approved baseline.
- **Experimental Models Status (M1–M4)**: Models evaluated during Step 9 and Step 10 (Bowler Workload, Phase-Relative Cutoffs, 2nd Innings Powerplay Floor, and Combined System) are **experimental prototypes**. They are computationally verified but **NOT APPROVED** as new production models.
- **Settled Batter Trap (Variant 2)**: Permanently rejected due to simulation evidence showing it penalizes set batters keeping chases alive.
"# SupeRR_round1_2026" 
