# SupeRR Selector 2.0: Cricket Analytics Visualization Module

## Overview
This directory contains the Python scripts that generate all 16 analytical visualizations for Step 7 of the SupeRR Selector 2.0 competition.

Visualizations cover:
- **Part A:** Pressure Index Dynamics across match phases, innings, and match timelines.
- **Part B:** Batter Performance under Pressure (Strike Rate, Survival, Boundaries, Dots, and Top 10 BRS Component breakdowns).
- **Part C:** Bowler Performance under Pressure (Economy, Breakthrough Wickets, Dots, Boundaries Conceded, and Top 10 BoRS Component breakdowns).
- **Part D:** Phase Specialist Analysis across Powerplay, Middle Overs, and Death Overs.

All generated charts are saved in high resolution (300 DPI) to:
`outputs/visualizations/`

---

## Directory Structure
```
src/visualizations/
├── README.md                          # This documentation file
├── run_all.py                         # Master orchestration script to generate all 16 charts
├── plot_pressure_analysis.py          # Part A: Charts 01-05 (Pressure distributions & timelines)
├── plot_batter_analysis.py            # Part B: Charts 06-10 (Batter performance & Top 10 BRS)
├── plot_bowler_analysis.py            # Part C: Charts 11-15 (Bowler performance & Top 10 BoRS)
└── plot_phase_specialists.py          # Part D: Chart 16 (6-panel Phase Specialists Grid)
```

---

## Prerequisites
The visualization suite runs in Python 3.10+ and requires standard scientific libraries:
```bash
pip install pandas numpy matplotlib
```

---

## Data Dependencies
The scripts read strictly from the processed Step 5 and Step 6 outputs:
1. `data/processed/delivery_pressure_index.csv` (188,097 clean live deliveries)
2. `data/processed/batter_reliability_rankings.csv` (816 evaluated batters)
3. `data/processed/bowler_reliability_rankings.csv` (589 evaluated bowlers)
4. `data/processed/phase_specialist_rankings.csv` (453 phase entries)

*Note: All scripts strictly respect the exclusion of the 233 second-innings target-reached deliveries (`runs_required <= 0`).*

---

## How to Regenerate All Charts
To regenerate all 16 charts sequentially, run the master runner:
```bash
python src/visualizations/run_all.py
```

Or execute individual modules independently:
```bash
python src/visualizations/plot_pressure_analysis.py
python src/visualizations/plot_batter_analysis.py
python src/visualizations/plot_bowler_analysis.py
python src/visualizations/plot_phase_specialists.py
```

---

## Chart Catalog & Descriptions

| Chart Filename | Section | Chart Title | Core Cricketing Insight |
|---|:---:|---|---|
| `01_batting_pressure_distribution.png` | Part A | Batting Pressure Index Distribution | Shows the right-skewed distribution of batting pressure; only 12.9% of deliveries qualify as High/Very High ($\text{PI} \ge 61.0$). |
| `02_bowling_pressure_distribution.png` | Part A | Bowling Pressure Index Distribution | Shows bowling pressure centered at 41.0; 11.1% of deliveries qualify as High/Very High. |
| `03_pressure_by_phase.png` | Part A | Pressure by Match Phase | Illustrates the structural phase asymmetry: Batting pressure surges at Death (mean 42.7), while Bowling pressure peaks in Powerplay (mean 50.0) with full wickets in hand. |
| `04_pressure_by_innings.png` | Part A | Pressure by Innings | Contrasts 1st Innings setting vs 2nd Innings chasing, highlighting the heavier right-tail in second innings due to escalating RRR. |
| `05_match_pressure_timelines.png` | Part A | Match Pressure Timelines | Traces 3 distinct archetypes: (1) Last-ball thriller (CSK vs MI 2022), (2) Early top-order collapse (CSK vs MI), and (3) Comfortable one-sided chase (DC vs PBKS). |
| `06_batter_strike_rate_comparison.png`| Part B | Strike Rate: High vs Low/Mod Pressure | Demonstrates the universal -29.5 points league scoring drop under pressure; highlights Top 10 batters who defy this trend. |
| `07_batter_survival_rate_comparison.png`| Part B| Survival Rate: High vs Low/Mod Pressure | Compares wicket retention ($100 - \text{Out}\%$); illustrates how elite anchors maintain $\ge 95\%$ survival under high pressure. |
| `08_batter_boundary_dot_comparison.png` | Part B | Boundary % and Dot Ball % Comparison | Side-by-side comparison for Top 10 batters against league baselines (Boundaries drop 19.4% $\to$ 14.2%; Dots surge 35.8% $\to$ 44.8%). |
| `09_top10_batters_brs.png` | Part B | Top 10 Batters Ranked by BRS | Clean horizontal ranking chart displaying BRS scores, sample sizes, and strike rates for the primary qualified cohort. |
| `10_top10_batter_components.png` | Part B | Top 10 Batters Component Breakdown | Grouped bar chart comparing the 4 BRS sub-scores (Strike Rate, Survival, Net Execution, Clutch Differential). |
| `11_bowler_economy_comparison.png` | Part C | Economy Rate: High vs Low/Mod Pressure | Scatter plot highlighting bowlers below the parity line who tighten up ($\text{High Econ} < \text{Low Econ}$) under pressure. |
| `12_bowler_wicket_rate_comparison.png` | Part C | Breakthrough Wicket Rate Comparison | Evaluates $\frac{\text{Wickets}}{\text{Balls}} \times 100$; highlights elite breakthrough weapons under pressure. |
| `13_bowler_dot_boundary_comparison.png` | Part C | Dot % and Boundary Conceded % | Contrasts pressure creation (dots) vs containment (boundary suppression) for Top 10 bowlers. |
| `14_top10_bowlers_bors.png` | Part C | Top 10 Bowlers Ranked by BoRS | Horizontal ranking chart displaying BoRS scores, sample sizes, and economy rates for the primary qualified cohort. |
| `15_top10_bowler_components.png` | Part C | Top 10 Bowlers Component Breakdown | Grouped bar chart comparing the 4 BoRS sub-scores (Economy, Breakthrough Wicket, Dot Ball Control, Clutch Tightening). |
| `16_phase_specialists_grid.png` | Part D | Phase Specialists Grid (2x3 Multi-Panel)| 6-panel grid showcasing Top 5 qualified players across Batting (PP, MO, DO) and Bowling (PP, MO, DO) with phase-specific priors. |
