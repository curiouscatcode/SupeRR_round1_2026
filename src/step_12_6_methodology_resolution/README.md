# Step 12.6: Resolve Outstanding Ranking Methodology Issues

## Module Overview

This module conducts a targeted, evidence-based methodological resolution of the four critical issues emerging from Step 12.5 before proceeding to Step 13.

### Core Boundaries & Audit Integrity
1. **Production Isolation:** Zero modifications to official v2.0 code, datasets, or ranking files (`src/*`, `data/processed/*`).
2. **Step 12 Isolation:** Zero modifications to Step 12 experimental code or outputs (`src/step_12_experimental_models/*`, `outputs/step_12_experimental_models/*`).
3. **Step 12.5 Isolation:** Zero modifications to Step 12.5 audit code or outputs (`src/step_12_5_independent_audit/*`, `outputs/step_12_5_independent_audit/*`).
4. **Full-Population Scope:** Evaluates the entire eligible player population (816 batters, 589 bowlers), distinguishing the full population, eligible population, and Top 10.
5. **No Model Combination:** Evaluates each candidate independently; does not create a combined model.
6. **Step 13 Restraint:** Step 13 has **not** been started.

---

## Directory Structure

```
supeRR_selector/
├── src/
│   └── step_12_6_methodology_resolution/
│       ├── __init__.py
│       ├── investigation_1_batting_formula.py         # Inv 1: BRS3 residual, variance & sensitivity
│       ├── investigation_2_bowling_containment.py     # Inv 2: Containment overlap & phase structure
│       ├── investigation_3_qualification_clustering.py# Inv 3: Empirical ANOVA ICC & match breadth
│       ├── investigation_4_top10_reconciliation.py    # Inv 4: Discrepancy forensic resolution
│       ├── run_all_investigations.py                  # Master suite runner
│       └── README.md                                  # This documentation file
└── outputs/
    └── step_12_6_methodology_resolution/
        ├── 01_batting_formula_resolution.png          # 4-panel diagnostic chart for Inv 1
        ├── 02_bowling_containment_resolution.png      # 4-panel diagnostic chart for Inv 2
        ├── 03_qualification_clustering_resolution.png # 4-panel diagnostic chart for Inv 3
        ├── 04_top10_reconciliation_resolution.png     # 2-panel diagnostic chart for Inv 4
        ├── inv1_batting_formula_comparison.csv        # Player-level batting comparison (N=816)
        ├── inv1_batting_weight_sensitivity.csv        # 16-weight grid sensitivity results
        ├── investigation_1_batting_formula.md         # Detailed markdown report for Inv 1
        ├── inv2_bowling_containment_comparison.csv    # Player-level bowling comparison (N=589)
        ├── investigation_2_bowling_containment.md     # Detailed markdown report for Inv 2
        ├── inv3_qualification_comparison.csv          # Player match breadth & cluster metrics
        ├── inv3_qualification_sensitivity_grid.csv    # Grid comparison across 7 qualification rules
        ├── investigation_3_qualification_clustering.md# Detailed markdown report for Inv 3
        ├── inv4_top10_reconciliation_table.csv        # Authoritative Top 10 reconciliation table
        ├── inv4_authoritative_top10_comparison.csv    # Authoritative Top 10 player comparison
        ├── investigation_4_top10_reconciliation.md    # Detailed markdown report for Inv 4
        ├── step_12_6_discrepancy_register.csv         # Complete 19-issue tracking register
        └── step_12_6_final_report.md                  # Master synthesis report
```

---

## Summary of Investigation Findings & Decisions

### 1. Investigation 1: Batting Formula BRS3
- **Classification:** `RESOLVED WITH QUALIFICATIONS`
- **Recommendation:** `ADVANCE AS A CANDIDATE`
- **Core Findings:**
  - Boundary Execution shares $92.70\%$ variance with Strike Rate ($r = 0.9628$ in Tier 1; $r = 0.9638$ across all 816 batters).
  - Regression residual analysis reveals the $7.30\%$ non-shared variance correlates strongly with high dots ($r = -0.4964$) and negatively with strike rotation ($r = +0.4998$). Removing Boundary Execution stops giving a compounding double reward to non-rotating boundary sluggers.
  - $BRS_3$ realigns effective covariance shares to $51.01\%$ SR, $31.67\%$ Survival, and $17.31\%$ Clutch Diff, matching nominal intentions ($45/35/20$).
  - Weight sensitivity grid ($16$ combinations) demonstrates extreme rank stability ($\rho \ge 0.9863$, Top 10 overlap 9-10/10).
  - Rank changes are phase-neutral ($|r| < 0.15$ with PP, MO, DO).

### 2. Investigation 2: Bowling Containment
- **Classification:** `RESOLVED WITH QUALIFICATIONS`
- **Recommendation:** `RETAIN OFFICIAL V2.0 PROVISIONALLY`
- **Core Findings:**
  - Economy Rate is $92.89\%$ linearly explained by Boundary Concession Rate ($r = +0.8938$) and Dot Ball Rate ($r = -0.4576$). Joint $R^2$ exceeds $93\%$ across all phases (Powerplay $95.4\%$, Middle $94.1\%$, Death $93.5\%$).
  - Adding Containment at $30\%$ alongside Economy ($40\%$) creates $79.24\%$ collinear overlap ($r = 0.8902$), artificially inflating total run restriction to $74.52\%$ effective variance and compressing Wickets from $32.35\%$ down to $10.12\%$.
  - Expensive strike bowlers drop an average of $-11.8$ ranks (Mukesh Choudhary $-30$).
  - Because no objective loss function justifies a specific containment weighting, official v2.0 is provisionally retained pending multi-objective win-probability modeling.

### 3. Investigation 3: Qualification & Match-Level Clustering
- **Classification:** `RESOLVED`
- **Recommendation:** `ADVANCE AS A CANDIDATE (RULE B: DUAL-CRITERIA)`
- **Core Findings:**
  - Empirical delivery-level ANOVA Intraclass Correlation Coefficient ($\text{ICC}$) is **$0.0231$ (2.3%) for batting** and **$0.0183$ (1.8%) for bowling**, disproving the arbitrary $\text{ICC} = 0.15$ assumed in Step 12.4. Design effects are modest ($\text{Deff} \approx 1.09$).
  - Several bowlers qualified under $N \ge 60$ despite very low match breadth (Kartik Tyagi 8 matches, Harsh Dubey 8 matches, Simarjeet Singh 9 matches).
  - In contrast, near-qualifiers with 50–59 balls boast immense match breadth (Quinton de Kock 34 matches, Sai Sudharsan 26 matches, Will Jacks 18 matches, Jamie Overton 14 matches).
  - Dual-Criteria ($N \ge 60 \lor (N \ge 50 \land M \ge 6)$) admits $+30$ batters and $+17$ bowlers, removes 0 players, eliminates the 0.01 pt knife-edge cliff, and preserves 100% Top 10 overlap in both disciplines.

### 4. Investigation 4: Ranking Consistency & Top 10 Discrepancy
- **Classification:** `RESOLVED (PREVIOUS NARRATIVE CLAIM INCORRECT)`
- **Core Findings:**
  - The Step 12.5 narrative table listing Klaasen, Suryakumar, Pooran (Batting) and Mohsin Khan, Narine, Pathirana (Bowling) was a **manual synthesis markdown transcription error**. The underlying Python code in `exp12_1_batting_formula.py` and `audit_12_1_batting_formula.py` evaluated the correct official Step 6.2 dataset.
  - The true official Tier 1 Top 3 begins: **1. MS Dhoni, 2. Shashank Singh, 3. Shivam Dube** (Batting), and **1. Tim Southee, 2. Keshav Maharaj, 3. Haris Rauf** (Bowling).
  - Under verified Tier 1 rules, Top 10 overlap is exactly **10 / 10 (100.0%) for Batting** and **9 / 10 (90.0%) for Bowling**.
  - Full-population rank stability is mathematically certified: Batting $\rho = 0.9818$, Bowling $\rho = 0.9634$.

---

## Execution Instructions

To execute all four investigations and generate all outputs:
```bash
python src/step_12_6_methodology_resolution/run_all_investigations.py
```
