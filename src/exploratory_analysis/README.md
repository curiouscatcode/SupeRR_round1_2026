# SupeRR Selector 2.0: Full Player Exploratory Data Analysis (EDA)

## Directory Overview
- **Location:** `src/exploratory_analysis/`
- **Output Artifacts:** `outputs/exploratory_analysis/`
- **Stage:** Step 8 — Full Player Population Exploratory Data Analysis & Anomaly Investigation
- **Data Evaluated:**
  - 816 Batters (`data/processed/batter_reliability_rankings.csv` & `batter_performance.csv`)
  - 589 Bowlers (`data/processed/bowler_reliability_rankings.csv` & `bowler_performance.csv`)
  - 453 Phase Specialist Entries (`data/processed/phase_specialist_rankings.csv`)
  - 188,097 Clean Deliveries (`data/processed/delivery_pressure_index.csv`)

---

## Execution Guide

### Run Master Orchestration Pipeline
To generate all 19 high-resolution figures (300 DPI) and 5 anomaly CSV datasets in a single execution:
```bash
python src/exploratory_analysis/run_all_eda.py
```

### Run Individual Analysis Modules
Each script is completely self-contained and can be executed independently:
```bash
# Part 1: Full Population Distributions (BRS, BoRS, Raw vs Bayesian, Tier Boxplots)
python src/exploratory_analysis/eda_01_distributions.py

# Part 2: Sample Size vs Reliability (Scatter plots, Tier Separation, Volatility Bins)
python src/exploratory_analysis/eda_02_sample_size_vs_reliability.py

# Part 3: Full Player Metric Heatmaps (116 Tier 1 Batters, 113 Tier 1 Bowlers, Tier 2 Specialists)
python src/exploratory_analysis/eda_03_player_heatmaps.py

# Part 4: Phase-Wise Performance Analysis (Cross-Phase Transitions, Disparities, Archetypes)
python src/exploratory_analysis/eda_04_phase_analysis.py

# Part 5: Ranking Model Mechanics & Shrinkage Dynamics (Regressions, Component Influence, Rank Shifts)
python src/exploratory_analysis/eda_05_ranking_model_mechanics.py

# Part 6: Clutch Regime Shifts (Low/Mod vs High Pressure Deltas & Quadrants)
python src/exploratory_analysis/eda_06_clutch_regime_shifts.py

# Part 7: Outlier Investigation & Anomaly CSV Generation (Anomaly Clusters & Vulnerability Case Studies)
python src/exploratory_analysis/eda_07_outliers_and_anomalies.py
```

---

## Chart Catalog & Descriptions (19 Figures)

| Figure Filename | Part | Focus & Visual Design | Core Analytical Discovery |
|---|:---:|---|---|
| `01_population_distributions_overview.png` | 1 | 4-panel KDE, histograms, and ECDFs for BRS and BoRS by Tier. | Tier 1 scores follow a bell curve centered at ~54; Below-Threshold players exhibit massive variance with extreme tails. |
| `02_raw_vs_bayesian_distributions.png` | 1 | 4-panel comparison of raw vs posterior metrics ($SR^*$, $Surv^*$, $Econ^*$, $Wk^*$). | Illustrates variance compression towards priors (114.05 SR, 9.06 Econ), eliminating 0% and 100% small-sample flukes. |
| `03_tier_comparisons_boxplots.png` | 1 | 6-panel boxplots comparing components across Tier 1, Tier 2, and Below Threshold. | Demonstrates that Tier 1 maintains tighter variance; Below-Threshold includes volatile 0 and 100 extremes. |
| `04_batter_sample_size_vs_brs.png` | 2 | Scatter plot of High-P Balls Faced vs BRS for all 816 batters with Tier boundaries. | Highlights small-sample high-score outliers (e.g. Vipraj Nigam BRS 93.6, Jamie Overton 79.5) and Tier 1 qualifiers. |
| `05_bowler_sample_size_vs_bors.png` | 2 | Scatter plot of High-P Legal Balls vs BoRS for all 589 bowlers with Tier boundaries. | Highlights small-sample tightening bowlers (Nasum Ahmed 88.8, Mark Wood 79.1, Schalkwyk 74.5) against Tier 1 masters. |
| `06_small_sample_score_volatility.png` | 2 | 2-panel boxplot of BRS and BoRS dispersion across sample size deciles. | Standard deviation drops monotonically from $\sigma = 16.4$ in $1–10$ balls down to $\sigma = 6.2$ at $N \ge 100$ balls. |
| `07_tier1_batters_heatmap.png` | 3 | 2-column side-by-side heatmap displaying **ALL 116 Tier 1 Qualified Batters**. | 100% visible coverage of all qualified batters across $SR^*$, $Surv^*$, $Bnd^*$, $Dot^*$, Clutch $\Delta^*$, and BRS. |
| `08_tier1_bowlers_heatmap.png` | 3 | 2-column side-by-side heatmap displaying **ALL 113 Tier 1 Qualified Bowlers**. | 100% visible coverage of all qualified bowlers across $Econ^*$, $Wk^*$, $Dot^*$, Boundary Conceded%, Clutch $\Delta^*$, and BoRS. |
| `09_tier2_specialists_heatmap.png` | 3 | Heatmap of Tier 2 Specialists (Top 45 of 72 Batters, and all 36 Bowlers). | Unveils high-ceiling specialists (e.g. Overton, Sudharsan, Nasum Ahmed, Mark Wood) protected from Tier 1 dilution. |
| `10_phase_performance_transitions.png` | 4 | 4-panel scatter plots comparing High-P SR and Economy across PP, MO, and DO. | Shows universal strike rate escalation towards Death Overs and severe bowling economy leakage at the Death. |
| `11_phase_specialist_disparity.png` | 4 | Dumbbell charts of players with largest phase rank inversions. | Contrasts pure death finishers (Dhoni #2 Death vs #86 Middle; Rinku #1 vs #66) with middle-overs anchors (Axar, Cummins). |
| `12_cross_phase_player_profiles.png` | 4 | Parallel trajectory profiles across match phases for iconic player archetypes. | Illustrates role-specific execution (e.g. Bumrah multi-phase control, Dhoni death surge, Head PP dominance). |
| `13_bayesian_shrinkage_mechanics.png` | 5 | Scatter of raw vs posterior metrics colored by sample size $N$ with prior anchors. | Visualizes the horizontal shrinkage vectors pulling small-$N$ points toward league priors ($K=50$). |
| `14_component_influence_and_correlations.png` | 5 | Correlation matrices and standardized regression coefficients ($\beta$). | Proves that Net Execution ($\beta = 0.428$) and Economy ($\beta = 0.461$) are the primary empirical drivers of final rank. |
| `15_shrinkage_rank_movements.png` | 5 | Dumbbell charts of top 8 climbers and top 8 fallers between raw rank and final rank. | Explains why Narine (-52 ranks) and Salt (-32 ranks) plunge, while Tilak Varma (+18) and Pollard (+19) ascend. |
| `16_batter_clutch_regime_deltas.png` | 6 | 4-panel analysis of batter shifts ($\Delta SR$, $\Delta Bnd\%$, $\Delta Dot\%$, Risk/Reward quadrants). | 71.4% of batters suffer scoring drops; maps players into Clutch Masters, Anchors, Explosive Sacrifices, and Degraders. |
| `17_bowler_clutch_regime_deltas.png` | 6 | 4-panel analysis of bowler shifts ($\Delta Econ$, $\Delta Wk\%$, Containment quadrants). | Separates Gold Standard bowlers (+wickets, tighter econ) from Restrictive Shields, Expensive Strike, and Bleeders. |
| `18_anomaly_multidimensional_clusters.png` | 7 | 2D anomaly maps identifying All-or-Nothing batters and Expensive Strike bowlers. | Isolates players with conflicting sub-metrics (e.g. high boundary% + high dots; high wickets + high economy). |
| `19_methodology_vulnerabilities_showcase.png` | 7 | 4-panel visual case study of 4 systemic methodology vulnerabilities. | Deep-dive into the Bumrah Paradox, the 60-Ball Threshold Cliff, Narine Multi-Component Tension, and Dhoni Phase Inversion. |

---

## Anomaly Datasets Catalog (5 CSV Files)

1. [`flagged_batters_anomalies.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/exploratory_analysis/flagged_batters_anomalies.csv) (81 rows):
   - Outliers across 4 categories: Small-Sample Extreme SR ($SR \ge 220, N < 30$), Zero Dismissal Outliers ($N \ge 30, \text{Dismissals} = 0$), All-or-Nothing Boundary-Dependent Batters ($Bnd\% \ge 20\%, Dot\% \ge 45\%$), and Severe Clutch Scoring Collapses ($\Delta SR \le -40$).
2. [`flagged_bowlers_anomalies.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/exploratory_analysis/flagged_bowlers_anomalies.csv) (26 rows):
   - Outliers across 4 categories: Expensive Strike Bowlers ($Econ \ge 10.5, Wk \ge 5$), Restrictive Shields ($Econ \le 7.5, Wk \le 2$), High Dot Rate with Boundary Bleed ($Dot\% \ge 45\%, Econ \ge 9.5$), and Severe Economy Bleeders ($\Delta Econ \le -2.5$ RPO).
3. [`small_sample_high_score_players.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/exploratory_analysis/small_sample_high_score_players.csv) (42 rows):
   - Players with $N < 60$ deliveries whose BRS or BoRS exceeds $65.0$. Details why they were safely quarantined into Tier 2 or Below Threshold.
4. [`conflicting_metrics_players.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/exploratory_analysis/conflicting_metrics_players.csv) (20 rows):
   - Players with statistically dissonant performance dimensions (e.g. elite containment but zero wickets, or high boundary rate masked by 50%+ dot balls).
5. [`methodology_vulnerabilities_cases.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/exploratory_analysis/methodology_vulnerabilities_cases.csv) (5 rows):
   - Formal case studies documenting methodological edge cases: The Bumrah Paradox, The 60-Ball Cliff, Narine Strike Rate Collapse, Dhoni Phase Inversion, and Target Under-Reconstruction.
