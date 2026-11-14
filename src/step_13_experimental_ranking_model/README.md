# Step 13: Integrated Experimental Ranking Model Pipeline

## 1. Overview
Step 13 implements an isolated, production-grade experimental ranking model integrating the verified decisions from Step 12.6:
1. **Batting Methodology:** Refined three-component formula ($BRS_3$):
   $$\text{BRS}_3 = 0.45 \cdot \text{Score}_{\text{SR}} + 0.35 \cdot \text{Score}_{\text{Surv}} + 0.20 \cdot \text{Score}_{\text{Diff}}$$
   Boundary Execution ($\text{Score}_{\text{Exec}}$) is eliminated to resolve collinearity ($r=0.963$ with Strike Rate). Component bounds, population priors, and Bayesian shrinkage ($K=50$) are strictly preserved.
2. **Bowling Methodology:** Retains the audited official v2.0 four-component Bowler Reliability Score ($\text{BoRS}$):
   $$\text{BoRS} = 0.40 \cdot \text{Score}_{\text{Econ}} + 0.25 \cdot \text{Score}_{\text{Wk}} + 0.20 \cdot \text{Score}_{\text{Dot}} + 0.15 \cdot \text{Score}_{\text{Diff}}$$
   The experimental containment formula is omitted per Step 12.6 findings.
3. **Qualification System:** Dual-criterion Rule B applied across both disciplines:
   - **Tier 1 (Qualified):** $N \ge 60 \lor (N \ge 50 \land M \ge 6)$
   - **Tier 2 (Specialist):** $N < 60$ not meeting Tier 1, but $N \ge 40$
   - **Below Threshold (Excluded):** $N < 40$
   ($N$ = high-pressure deliveries faced/bowled; $M$ = distinct matches with high-pressure opportunities).
4. **Phase Specialists:** Phase specialist leaderboards across Powerplay (PP), Middle Overs (MO), and Death Overs (DO) are computed under the existing phase Bayesian methodology and cross-tabulated with overall qualification status.

---

## 2. Directory Structure

```
src/step_13_experimental_ranking_model/
├── rank_players_exp13.py        # Core experimental calculation engine
├── compare_exp13_vs_official.py # Full-population comparison & diagnostics
├── run_step_13.py               # Master execution runner
└── README.md                    # This architecture specification

outputs/step_13_experimental_ranking_model/
├── exp13_batter_rankings.csv              # Full population (816 batters) with BRS_3 and Rule B
├── exp13_bowler_rankings.csv              # Full population (589 bowlers) with BoRS and Rule B
├── exp13_phase_specialist_rankings.csv    # 453 phase specialist records annotated with tiers
├── exp13_batter_comparison.csv            # Player-by-player batting comparison (816 rows)
├── exp13_bowler_comparison.csv            # Player-by-player bowling comparison (589 rows)
├── exp13_tier_qualification_changes.csv   # Promoted players & boundary near-qualifiers (49 rows)
├── exp13_top10_comparison.csv             # Elite Top 10 official vs experimental comparison
├── exp13_phase_specialist_comparison.csv  # Phase specialist tier transitions (453 rows)
├── 01_score_and_rank_distributions.png    # Score deltas & rank correlations
├── 02_tier_qualification_changes.png      # Delivery volume vs match breadth clustering
├── 03_top10_movement.png                  # Bump charts for elite Top 12 batters and bowlers
├── 04_phase_specialist_analysis.png       # Phase specialist tier representation
└── step_13_final_report.md                # Comprehensive final evaluation report
```

---

## 3. How to Run

To execute the complete pipeline from scratch:
```powershell
python src/step_13_experimental_ranking_model/run_step_13.py
```
Execution takes approximately 4–5 seconds and performs 10 automated data integrity assertions.

---

## 4. Key Results Summary

| Metric | Batters | Bowlers | Notes |
| :--- | :--- | :--- | :--- |
| **Full Population Size** | 816 | 589 | 100% evaluated, 0 dropped |
| **Official Tier 1 Size** | 116 | 113 | Baseline Rule A ($N \ge 60$) |
| **Exp 13 Tier 1 Size** | 146 (+30 / +25.9%) | 130 (+17 / +15.0%) | Rule B ($N \ge 60 \lor [N \ge 50 \land M \ge 6]$) |
| **Official Tier 2 Size** | 72 | 36 | Baseline $40 \le N < 60$ |
| **Exp 13 Tier 2 Size** | 42 (-30) | 19 (-17) | Net reduction as promoted players exit |
| **Below Threshold ($N < 40$)** | 628 (Unchanged) | 440 (Unchanged) | Zero spillover into Tier 1 or 2 |
| **Correlation ($r$ / $\rho$) Full** | $r=0.9859$, $\rho=0.9818$ | $r=1.0000$, $\rho=1.0000$ | Batting shifts slightly; Bowling formula unchanged |
| **Correlation ($\rho$) Retained T1** | $\rho=0.9885$ | $\rho=1.0000$ | Relative ordering perfectly stable |
| **Top 10 Overlap** | **9 / 10 (90%)** | **8 / 10 (80%)** | Jamie Overton enters Batting #7; Nasum Ahmed (#2) & Junaid Siddique (#5) enter Bowling |
| **Top 20 Overlap** | **16 / 20 (80%)** | **17 / 20 (85%)** | High elite stability |
| **Top 50 Overlap** | **42 / 50 (84%)** | **43 / 50 (86%)** | Broad population consistency |
