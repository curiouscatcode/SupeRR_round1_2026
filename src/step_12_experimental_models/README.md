# Step 12: Experimental Ranking Model Development

This directory contains the experimental code, models, and evaluation scripts developed for **Step 12: Experimental Ranking Model Development**.

All experimental work is strictly isolated from production code and processed datasets. The official v2.0 rankings, formulas, and datasets in `data/processed/` and `src/` remain 100% untouched.

---

## 1. Directory Structure

```
src/step_12_experimental_models/
├── exp12_1_batting_formula.py             # Experiment 12.1: 3-Component Batting Formula (BRS_3)
├── exp12_2_bowling_containment.py         # Experiment 12.2: Bowling Containment & Pressure Induction (BoRS_Contain)
├── exp12_3_cohort_priors.py               # Experiment 12.3: Cohort-Specific Bayesian Priors (Chronological Validation)
├── exp12_4_confidence_qualification.py    # Experiment 12.4: Confidence Intervals & Dual-Criteria Eligibility
├── run_all_experiments.py                 # Master runner executing all 4 experiments sequentially
└── README.md                              # Module documentation (this file)
```

Outputs are saved in:
```
outputs/step_12_experimental_models/
├── exp12_1_batting_formula/
│   ├── exp12_1_batting_rankings.csv
│   ├── exp12_1_batting_comparison.csv
│   ├── 01_exp12_1_batting_formula.png
│   └── exp12_1_batting_formula_report.md
├── exp12_2_bowling_containment/
│   ├── exp12_2_bowling_rankings.csv
│   ├── exp12_2_bowling_comparison.csv
│   ├── 02_exp12_2_bowling_containment.png
│   └── exp12_2_bowling_containment_report.md
├── exp12_3_cohort_priors/
│   ├── exp12_3_cohort_priors_rankings.csv
│   ├── exp12_3_cohort_comparison.csv
│   ├── 03_exp12_3_cohort_priors.png
│   └── exp12_3_cohort_priors_report.md
├── exp12_4_confidence_qualification/
│   ├── exp12_4_qualification_rankings.csv
│   ├── exp12_4_qualification_comparison.csv
│   ├── 04_exp12_4_confidence_qualification.png
│   └── exp12_4_confidence_qualification_report.md
└── step_12_final_report.md                # Master synthesis report across all 4 experiments
```

---

## 2. Overview of the Four Experiments

| Experiment | Focus Area | Mathematical Formulation | Core Finding | Final Verdict |
| :--- | :--- | :--- | :--- | :---: |
| **12.1 Batting Formula** | Eliminates severe collinearity between Strike Rate and Boundary Execution ($r=0.963$) | $\text{BRS}_3 = 0.45(\text{SR}) + 0.35(\text{Surv}) + 0.20(\text{Diff})$ | Eliminates redundant speed variance; boosts survival share from 19.8% to 31.7%; retains 10/10 Top 10 batters. | **KEEP (Strong Candidate)** |
| **12.2 Bowling Containment** | Recognizes dot-ball pressure and boundary suppression across all bowlers | $\text{BoRS}_{\text{Contain}} = 0.40(\text{Econ}) + 0.15(\text{Wk}) + 0.30(\text{Contain}) + 0.15(\text{Diff})$ | Boundary concession ($r=-0.111$ with dots) captures true run suppression; elevates Bumrah (+10 ranks) and Theekshana (into Top 10) naturally. | **KEEP (Strong Candidate)** |
| **12.3 Cohort Priors** | Tests separate population priors for Top Order vs Middle and Pace vs Spin | $\theta^* = \lambda \hat{\theta} + (1-\lambda) \mu_{\text{Cohort}}$ with $K=50$ | Chronological out-of-sample validation proves cohort priors increase error in batting (+0.50 RMSE) and tie in bowling. | **REJECT** |
| **12.4 Qualification** | Investigates 60-ball boundary cliff and estimation uncertainty | $\text{SE} = \sigma / \sqrt{N+K}$; Dual-Criteria: $N \ge 60 \lor (N \ge 50 \land M \ge 6)$ | Precision at 59b vs 60b differs by only 0.01 pts; Dual-criteria admits proven specialists (Overton, Nasum) without arbitrary sigmoids. | **KEEP (Strong Candidate)** |

---

## 3. How to Run

To run all experiments sequentially:
```powershell
python src/step_12_experimental_models/run_all_experiments.py
```

To run individual experiments:
```powershell
python src/step_12_experimental_models/exp12_1_batting_formula.py
python src/step_12_experimental_models/exp12_2_bowling_containment.py
python src/step_12_experimental_models/exp12_3_cohort_priors.py
python src/step_12_experimental_models/exp12_4_confidence_qualification.py
```
