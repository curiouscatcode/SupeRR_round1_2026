# SupeRR Selector 2.0: Cricket Analytics & Visualization Report

## Document Metadata
- **Project:** SupeRR Selector 2.0 — Cricket Analytics Under Pressure
- **Stage:** Step 7 — Visualizations & Comprehensive Analytical Report
- **Output Artifacts Directory:** `outputs/visualizations/`
- **Visualization Scripts:** `src/visualizations/`
- **Data Evaluated:** 188,097 clean live deliveries across 789 standard T20 matches (357 IPL, 432 T20I) from 2022 to 2026.
- **Player Populations:** 816 evaluated batters (116 Tier 1 Qualified) and 589 evaluated bowlers (113 Tier 1 Qualified).

---

## Executive Summary

This report provides the analytical evidence accompanying the SupeRR Selector 2.0 Player Reliability Ranking Engine. Through 16 high-resolution visualizations, we explore:
1. **The Anatomy of Pressure:** How match pressure fluctuates across deliveries, phases, innings, and live game states.
2. **Batting Dynamics Under Stress:** The universal degradation of scoring velocity under high pressure and how elite finishers defy this trend through strike rotation and boundary dominance.
3. **Bowling Execution Under Stress:** The containment and breakthrough characteristics of elite bowlers defending small totals or bowling to explosive set batters.
4. **Deconstruction of the Top 10 Rosters:** Why the 10 most reliable batters (BRS) and 10 most reliable bowlers (BoRS) achieved their rankings based on their 4-component score profiles.
5. **Phase Specialization:** Identifying niche mastery in the Powerplay (crisis mitigation vs new-ball swing), Middle Overs (spin control vs run acceleration), and Death Overs (finishing vs yorker execution).

All observations are strictly grounded in empirical distributions. No correlation is treated as causation, and all sample size thresholds are reported transparently.

---

# PART A — PRESSURE ANALYSIS

---

### Chart 1: Distribution of Batting Pressure Index
**File:** `outputs/visualizations/01_batting_pressure_distribution.png`

```
Distribution Overview (N = 188,097 Clean Deliveries):
- Mean Batting PI:    35.69
- Median Batting PI:  33.61
- Standard Deviation: 20.03
- High-Pressure Deliveries (PI > 60.0):  24,335 (12.9% of all deliveries)
- High-Pressure Deliveries (PI >= 61.0): 22,634 (12.0% of all deliveries)
- Very High-Pressure (PI > 80.0):        4,366 ( 2.3% of all deliveries)
- Very High-Pressure (PI >= 81.0):       3,958 ( 2.1% of all deliveries)
```

#### What the Chart Shows:
The probability density distribution of the Batting Pressure Index across all 188,097 eligible deliveries, partitioned into the 5 qualitative competition bands: Very Low ($0–20$), Low ($21–40$), Moderate ($41–60$), High ($61–80$), and Very High ($81–100$). Summary vertical markers indicate the mean ($35.69$), median ($33.61$), and the High-Pressure threshold cutoff ($\text{PI} > 60.0$).

#### Important Observations:
- The distribution is right-skewed with a prominent peak in the Low-to-Moderate zone ($25–40$).
- The vast majority of deliveries ($87.1\%$) occur in Low to Moderate pressure environments ($\text{PI} \le 60.0$).
- Only $12.9\%$ of deliveries qualify as High or Very High pressure ($\text{PI} > 60.0$, or $12.0\%$ for $\text{PI} \ge 61.0$).
- Extreme pressure ($\text{PI} > 80.0$) is a rare match condition ($2.3\%$ of deliveries, $4,366$ balls), occurring almost exclusively in the final 3 overs of steep chases or during historic top-order collapses.

#### Cricketing Interpretation:
T20 cricket is primarily played in a manageable tension band. However, tournament outcomes are disproportionately decided in the top $13\%$ high-stress deliveries. The scarcity of high-pressure deliveries explains why sample sizes are inherently constrained, necessitating Empirical Bayes shrinkage to prevent small-sample flukes from distorting player evaluations.

#### Limitations & Sample Size Concerns:
Because true high-pressure deliveries represent only ~13 out of every 100 balls in a match, an average top-order batter who plays 15 matches a year may face fewer than 30 high-pressure balls per season unless their team frequently experiences collapses or plays down-to-the-wire chases.

---

### Chart 2: Distribution of Bowling Pressure Index
**File:** `outputs/visualizations/02_bowling_pressure_distribution.png`

```
Distribution Overview (N = 188,097 Clean Deliveries):
- Mean Bowling PI:    40.97
- Median Bowling PI:  41.79
- Standard Deviation: 15.09
- High-Pressure Deliveries (PI > 60.0):  20,803 (11.1% of all deliveries)
- High-Pressure Deliveries (PI >= 61.0): 18,555 ( 9.9% of all deliveries)
- Very High-Pressure (PI > 80.0):          328 ( 0.2% of all deliveries)
- Very High-Pressure (PI >= 81.0):         230 ( 0.1% of all deliveries)
```

#### What the Chart Shows:
The probability density distribution of the Bowling Pressure Index across all 188,097 clean deliveries, indicating the mean ($40.97$), median ($41.79$), and the High-Pressure threshold ($\text{PI} > 60.0$).

#### Important Observations:
- The bowling pressure distribution is centered higher than batting pressure (mean of $41.0$ vs $35.7$, median of $41.8$ vs $33.6$), reflecting the higher baseline structural stress placed on bowlers in early overs when full wickets remain.
- However, the "Very High" pressure tail ($\text{PI} > 80.0$) is virtually non-existent for bowlers (only $328$ deliveries, $0.2\%$, and $230$ / $0.1\%$ for $\text{PI} \ge 81.0$).
- Total deliveries qualifying as High/Very High pressure are $20,803$ ($11.1\%$ for $\text{PI} > 60.0$, or $18,555$ / $9.9\%$ for $\text{PI} \ge 61.0$).

#### Cricketing Interpretation:
Bowlers experience a higher baseline level of constant pressure throughout the innings, but under the competition's mathematical formulation, Bowling PI rarely reaches the extreme 85+ zone. This occurs because Bowling PI relies on remaining batting wickets ($W = \frac{6-w}{6}$); as wickets fall late in an innings, bowling pressure paradoxically decreases unless required run rates or scoring spikes are astronomical.

#### Limitations & Sample Size Concerns:
The formula structure results in bowling pressure being heavily weighted toward situations where the batting team has many wickets in hand, which concentrates high-pressure bowling deliveries in earlier phases.

---

### Chart 3: Pressure Distribution Across Match Phases (PP, Middle, Death)
**File:** `outputs/visualizations/03_pressure_by_phase.png`

```
Phase Pressure Comparison:
Phase       | Batting Mean PI | Batting HP% (PI > 60) | Bowling Mean PI | Bowling HP% (PI > 60)
------------|:---------------:|:---------------------:|:---------------:|:---------------------:
Powerplay   | 35.0            | 8.5%                  | 50.0            | 20.5%
Middle      | 32.7            | 11.3%                 | 40.5            | 8.4%
Death       | 42.7            | 22.7%                 | 29.3            | 3.2%
```

#### What the Chart Shows:
Side-by-side boxplots comparing Batting Pressure Index and Bowling Pressure Index across the three standard T20 phases: Powerplay (Overs 1–6), Middle Overs (Overs 7–15), and Death Overs (Overs 16–20).

#### Important Observations:
- **Batting Pressure Surges in Death Overs:** Batting PI averages $35.0$ in the Powerplay, settles slightly to $32.7$ in the Middle Overs, and surges to $42.7$ at the Death. The percentage of batting deliveries classified as High Pressure escalates sharply from $8.5\%$ in PP, to $11.3\%$ in Middle, reaching $22.7\%$ in Death Overs.
- **Bowling Pressure Steeply Declines:** Bowling PI exhibits the inverse pattern: peaking in the Powerplay at a mean of $50.0$ ($20.5\%$ High Pressure), declining to $40.5$ in Middle Overs ($8.4\%$ High Pressure), and dropping to $29.3$ in Death Overs ($3.2\%$ High Pressure).

#### Cricketing Interpretation:
This chart uncovers the **structural phase asymmetry** of the competition model:
- Batters feel escalating pressure as overs run out and required run rates climb. A dot ball in the 19th over is catastrophic for a chasing batting team.
- Bowlers feel the greatest structural pressure in the Powerplay, where field restrictions are severe (only 2 fielders outside the ring) and the batting team possesses all 10 wickets in hand. Conversely, by the Death Overs, multiple wickets have usually fallen, relieving structural bowling pressure under the formula.
- **Analytical Takeaway:** Batting reliability is primarily tested in the Middle and Death phases, whereas bowling reliability is heavily tested in the Powerplay and Middle phases.

#### Limitations & Sample Size Concerns:
Because only $1,279$ high-pressure legal balls exist in Death Overs across the entire 4-year dataset, Death Overs specialist rankings for bowlers require a lower sample threshold ($N \ge 15$ legal balls) than Powerplay rankings ($N \ge 30$).

---

### Chart 4: Pressure Comparison Between First and Second Innings
**File:** `outputs/visualizations/04_pressure_by_innings.png`

```
Innings Pressure Comparison:
Regime              | 1st Innings (Setting) | 2nd Innings (Chasing)
--------------------|:---------------------:|:---------------------:
Batting Mean PI     | 31.0                  | 40.8
Batting Median PI   | 28.6                  | 39.6
Bowling Mean PI     | 38.9                  | 43.3
Bowling Median PI   | 39.5                  | 43.5
```

#### What the Chart Shows:
Comparative histograms displaying the distribution of Batting and Bowling Pressure Indexes between the First Innings (target setting) and the Second Innings (target chasing).

#### Important Observations:
- Second-innings chases exhibit significantly higher average pressure for both batters ($40.8$ vs $31.0$) and bowlers ($43.3$ vs $38.9$).
- The second-innings batting distribution exhibits a long, heavy right tail extending past $80.0$. In the first innings, Batting PI rarely exceeds $70.0$ unless a complete collapse occurs.
- Chasing introduces a non-linear pressure multiplier: Required Run Rate (RRR) compounds geometrically with every dot ball, whereas Current Run Rate (CRR) in the first innings evolves linearly.

#### Cricketing Interpretation:
Setting a target is an open-ended optimization problem; chasing a target is a fixed-resource, hard-deadline deadline problem. Chasing batters operate under acute psychological and mathematical constraints. A team that falls behind the required run rate in a chase experiences exponential pressure growth.

#### Limitations & Sample Size Concerns:
Matches where the first innings score was unusually low (e.g. all out for 100) create second-innings chases where RRR is never a factor (e.g. 5.0 RPO), pulling second-innings pressure downward for comfortable chases.

---

### Chart 5: Match-Level Pressure Timelines (Three Representative Archetypes)
**File:** `outputs/visualizations/05_match_pressure_timelines.png`

```
Representative Matches Analyzed:
1. Archetype 1 (Dramatic Finish): Match 14126 (MI vs CSK, 2022-04-21) - CSK won by 3 wickets (last ball)
2. Archetype 2 (Early Collapse):  Match 14153 (CSK vs MI, 2022-05-12) - CSK collapsed to 32/5 in 5.3 overs
3. Archetype 3 (One-Sided Chase): Match 14125 (DC vs PBKS, 2022-04-20) - DC cruised to 119/1 in 10.3 overs
```

#### What the Chart Shows:
Three distinct match timelines tracing delivery-by-delivery Batting PI (solid line), Bowling PI (dashed line), and wicket fall events (crimson markers) across 120 balls of play.

#### Important Observations:
- **Archetype 1 (Match 14126, CSK Chasing 156):**
  Batting PI hovered in the moderate range ($40–55$) until over 14. As wickets fell (including Rayudu and Jadeja), Batting PI spiked sharply into the High zone ($70–85$). In over 20, with 16 required off 4 balls, Batting PI peaked at **92.5**. When MS Dhoni struck 6, 4, 2, 4 off Jaydev Unadkat, pressure dropped precipitously as the winning boundary was struck on the final delivery.
- **Archetype 2 (Match 14153, CSK Setting Target):**
  CSK lost Ruturaj Gaikwad on ball 2, Mitchell Santner on ball 4, and Robin Uthappa in over 2. By over 5.3, CSK was 32/5. Batting PI immediately rocketed to **83.2 in the Powerplay**—a rare early crisis. Bowling PI simultaneously plummeted because MI had already secured dominant control.
- **Archetype 3 (Match 14125, DC Chasing 116):**
  DC lost only 1 wicket while scoring at over 11 RPO. Batting PI remained virtually flat in the **20–32 range** for the entire 10.3 overs. The chase was completely free of match tension.

#### Cricketing Interpretation:
These three timelines prove that the Pressure Index engine accurately tracks the live narrative of a T20 contest. It demonstrates why aggregate season statistics fail to capture reliability: a boundary hit in Archetype 3 carries near-zero pressure weight, whereas a boundary hit in the 20th over of Archetype 1 represents peak clutch execution.

---

# PART B — BATTER PERFORMANCE UNDER PRESSURE

---

### Chart 6: High-Pressure vs Low/Moderate-Pressure Strike Rate
**File:** `outputs/visualizations/06_batter_strike_rate_comparison.png`

```
Population Strike Rate Metrics (Tier 1: N >= 60 Balls Faced):
- League Low/Moderate Strike Rate: 143.52
- League High-Pressure Strike Rate: 114.05
- Net Population Drop:             -29.47 runs / 100 balls (-20.5%)
- Top 10 Batters High-Pressure SR: 153.25 average (+39.20 points above league HP prior)
```

#### What the Chart Shows:
A scatter plot comparing each qualified batter's Low/Moderate-Pressure Strike Rate (x-axis) against their High-Pressure Strike Rate (y-axis). The dashed diagonal represents the parity line ($y = x$). Points are sized by total high-pressure balls faced and colored by raw strike rate differential. Reference lines show the league baselines.

#### Important Observations:
- **The Universal Pressure Deficit:** Over $85\%$ of qualified batters fall well below the parity line. The league-wide scoring velocity drops by nearly 30 runs per 100 balls under pressure.
- **The Clutch Outliers:** Only a tiny elite cluster sits on or above the parity line. MS Dhoni ($170.62$ high vs $135.85$ low, $+34.8$ raw delta; $+22.0$ Bayesian delta) and Shubham Dubey ($169.57$ high vs $158.33$ low) stand out as rare batters whose scoring rate increases under pressure.
- Top 10 batters (Shashank Singh, Shivam Dube, Cameron Green, Jitesh Sharma) maintain strike rates between $143$ and $159$ under high pressure, outperforming the league high-pressure baseline by $30–45$ points.

#### Cricketing Interpretation:
High pressure compresses batting strike rates because field settings are optimized, bowling intensity is maximized, and the risk of gifting a wicket inhibits free scoring. Batters who maintain strike rates above $145$ under high pressure provide unmatched win equity.

#### Limitations & Sample Size Concerns:
Batters who primarily face high pressure in the Powerplay (due to early collapses) face field restrictions, whereas death-overs finishers face 5 boundary riders. This role context is normalized through phase specialist metrics.

---

### Chart 7: High-Pressure vs Low/Moderate-Pressure Survival Rate
**File:** `outputs/visualizations/07_batter_survival_rate_comparison.png`

```
Survival Rate Metrics (Surv% = 100% - Dismissal%):
- League Low/Moderate Survival Rate: 94.80% (1 dismissal per 19.2 balls)
- League High-Pressure Survival Rate: 92.91% (1 dismissal per 14.1 balls)
- Net Survival Rate Drop:             -1.89 percentage points
```

#### What the Chart Shows:
A scatter plot comparing wicket survival rates under normal conditions versus high pressure.

#### Important Observations:
- High pressure increases the hazard of dismissal by nearly $50\%$ on a per-ball basis (dismissal rate rises from $5.20\%$ to $7.09\%$).
- Elite batters demonstrate superior crease retention: Shivam Dube ($96.41\%$ Bayesian survival), Cameron Green ($96.45\%$), and Vijay Shankar ($96.92\%$) maintain survival rates well above the league low-pressure average even under extreme heat.
- Lower-order hitters who slog indiscriminately show severe survival degradation down to $88–90\%$, explaining why pure strike rate alone does not guarantee a high reliability ranking.

#### Cricketing Interpretation:
A reliable batter cannot simply score quickly; they must survive. In a tight chase, losing a wicket immediately consumes team resources and spikes pressure on incoming batters. The BRS formula's $25\%$ weight on survival rewards players who score at a high clip while protecting their wicket.

---

### Chart 8: Boundary % and Dot Ball % Comparison
**File:** `outputs/visualizations/08_batter_boundary_dot_comparison.png`

```
Execution Metrics Shift under Pressure:
Metric         | Low/Mod Pressure Baseline | High-Pressure Baseline | Net Population Shift
---------------|:-------------------------:|:----------------------:|:--------------------:
Boundary %     | 19.42%                    | 14.15%                 | -5.27% (-27.1%)
Dot Ball %     | 35.84%                    | 44.84%                 | +9.00% (+25.1%)
```

#### What the Chart Shows:
Side-by-side horizontal bar comparisons of Boundary % and Dot Ball % for the Top 10 batters, contrasting their low-pressure baseline against high-pressure execution.

#### Important Observations:
- Across the league, boundaries become $27\%$ rarer under pressure, while dot balls surge by $9.0$ percentage points (approaching $45\%$ of all pressure deliveries).
- **Boundary Retention:** Top 10 batters resist boundary suppression. MS Dhoni ($25.26\%$ boundaries), Shashank Singh ($21.48\%$), and Shivam Dube ($21.25\%$) consistently clear the rope on 1 in every 5 pressure balls.
- **Dot Ball Mitigation:** While the average batter plays dots on $45\%$ of pressure balls, elite anchors like Vijay Shankar ($38.5\%$) and Cameron Green ($37.2\%$) maintain strike rotation, preventing pressure accumulation.

#### Cricketing Interpretation:
The Net Execution factor ($\text{Bnd}^* - 0.5 \cdot \text{Dot}^*$) separates true finishers from one-dimensional boundary hitters. A batter who hits two boundaries but plays four dots in an over ($66.7\%$ dots) builds pressure; a batter who pairs boundaries with singles and doubles systematically neutralizes defensive bowling.

---

### Chart 9: Top 10 Batters Ranked by BRS
**File:** `outputs/visualizations/09_top10_batters_brs.png`

```
Official Top 10 Batters:
Rank | Player Name           | High BF | High Runs | Obs SR | Bayes SR (SR*) | BRS Score
:---:|-----------------------|:-------:|:---------:|:------:|:--------------:|:---------:
 1   | Mahendra Singh Dhoni  | 194     | 331       | 170.62 | 159.03         | 95.05
 2   | Shashank Singh        | 135     | 225       | 166.67 | 152.45         | 84.04
 3   | Shivam Dube           | 160     | 249       | 155.62 | 145.73         | 82.97
 4   | Shubham Dubey         | 69      | 117       | 169.57 | 146.24         | 80.82
 5   | Cameron Green         | 78      | 127       | 162.82 | 143.77         | 80.70
 6   | Vijay Shankar         | 65      | 97        | 149.23 | 133.93         | 78.02
 7   | Jitesh Sharma         | 97      | 157       | 161.86 | 145.59         | 77.01
 8   | Rinku Singh           | 177     | 259       | 146.33 | 139.22         | 75.49
 9   | George Dockrell       | 100     | 145       | 145.00 | 134.68         | 75.38
 10  | Patrick Cummins       | 131     | 205       | 156.49 | 144.76         | 74.77
```

#### What the Chart Shows:
A horizontal ranking bar chart displaying the final Batter Reliability Scores (BRS) for the Tier 1 qualified cohort ($N \ge 60$ balls faced), annotated with sample sizes, raw strike rates, Bayesian strike rates, and clutch differentials.

#### Important Observations:
- **MS Dhoni's Dominance:** Dhoni leads the competition with a BRS of $95.05$, outstripping second place by over $11.0$ points. His rating reflects sustained volume ($194$ balls) combined with an unmatched $159.03$ Bayesian strike rate.
- **The 80+ Elite Cohort:** Four batters achieve scores above 80: Shashank Singh ($84.04$), Shivam Dube ($82.97$), Shubham Dubey ($80.82$), and Cameron Green ($80.70$).
- **Volume Representation:** All top 10 batters possess substantial sample sizes, ranging from $65$ balls (Vijay Shankar) to $194$ balls (Dhoni), confirming that the rankings reflect sustained excellence rather than brief cameos.

---

### Chart 10: Top 10 Batters Four-Component Breakdown
**File:** `outputs/visualizations/10_top10_batter_components.png`

```
Component Weights:
- Strike Rate Score:  40% (Scoring velocity)
- Survival Score:     25% (Crease preservation)
- Net Execution:      20% (Boundary vs dot efficiency)
- Clutch Score:       15% (Elevation over personal baseline)
```

#### What the Chart Shows:
A grouped bar chart displaying the four standardized sub-scores ($S \in [0, 100]$) for each of the Top 10 batters, illustrating the specific tactical strengths that generate their composite BRS.

#### Important Observations:
- **MS Dhoni:** Maxes out Execution ($100.0$) and Clutch Elevation ($100.0$) while achieving $98.78$ in Strike Rate.
- **Shivam Dube & Cameron Green:** Dominated by Crease Survival ($91.26$ and $91.61$, respectively) paired with elite Strike Rate scores ($82.16$ and $79.71$).
- **Vijay Shankar:** Possesses the highest Survival score among the Top 10 ($95.35$), functioning as an anchor who avoids dismissals while scoring at a respectable $133.9$ Bayesian SR.
- **Pat Cummins:** High Strike Rate score ($80.96$) and strong Execution ($79.70$), offset slightly by lower Crease Survival ($68.98$).

---

# PART C — BOWLER PERFORMANCE UNDER PRESSURE

---

### Chart 11: High-Pressure vs Low/Moderate-Pressure Economy Rate
**File:** `outputs/visualizations/11_bowler_economy_comparison.png`

```
Population Economy Metrics (Tier 1: N >= 60 Legal Balls):
- League Low/Moderate Economy:  8.64 RPO
- League High-Pressure Economy:  9.06 RPO
- Net Population Increase:       +0.42 RPO (+4.9% leakage under pressure)
- Top 10 Bowlers HP Economy:     6.92 RPO average (-2.14 RPO below league HP prior)
```

#### What the Chart Shows:
A scatter plot comparing each qualified bowler's Low/Moderate-Pressure Economy Rate (x-axis) against their High-Pressure Economy Rate (y-axis). The green shaded region below the parity line represents the "Clutch Tightening Zone" where bowlers concede fewer runs per over under pressure than in normal overs.

#### Important Observations:
- Most bowlers leak additional runs under pressure ($+0.42$ RPO league increase).
- **The Elite Containment Outliers:** Bowlers positioned deep within the shaded clutch zone—Tim Southee ($5.16$ high vs $8.59$ low, $-3.43$ raw delta), Mark Adair ($5.32$ high vs $8.45$ low, $-3.13$ raw delta), and Keshav Maharaj ($6.23$ high vs $7.78$ low, $-1.55$ delta)—demonstrate remarkable run-strangling capability when defending.
- Top 10 bowlers average an observed economy of $6.92$ under pressure, outperforming the league high-pressure prior by over $2.1$ runs per over.

---

### Chart 12: High-Pressure vs Low/Moderate-Pressure Wicket Rate
**File:** `outputs/visualizations/12_bowler_wicket_rate_comparison.png`

```
Breakthrough Wicket Rate Metrics (Wickets / Legal Balls * 100):
- League Low/Moderate Wicket Rate: 5.36% (1 wicket per 18.7 balls)
- League High-Pressure Wicket Rate: 4.82% (1 wicket per 20.8 balls)
- Net Population Shift:            -0.54 percentage points
```

#### What the Chart Shows:
A scatter plot comparing breakthrough wicket rates between normal and high-pressure regimes.

#### Important Observations:
- League-wide wicket rates drop slightly under high pressure ($5.36\% \to 4.82\%$) as batters become more selective and prioritize wickets in hand.
- **Strike Bowler Dominance:** Tim Southee ($10.94\%$ raw rate, $8.25\%$ Bayesian rate), Keshav Maharaj ($8.97\%$ raw, $7.35\%$ Bayesian), and Haris Rauf ($8.49\%$ raw, $7.31\%$ Bayesian) defy this trend, taking a wicket roughly every $11–13$ legal balls under pressure.

---

### Chart 13: Bowler Dot Ball % and Boundary Conceded % Comparison
**File:** `outputs/visualizations/13_bowler_dot_boundary_comparison.png`

```
Bowling Execution Shift under Pressure:
Metric               | Low/Mod Baseline | High-Pressure Baseline | Net Population Shift
---------------------|:----------------:|:----------------------:|:--------------------:
Dot Ball %           | 36.67%           | 39.39%                 | +2.71% (+7.4%)
Boundary Conceded %  | 18.47%           | 21.64%                 | +3.16% (+17.1%)
```

#### What the Chart Shows:
Comparative horizontal bar charts showing Dot Ball % (pressure creation) and Boundary Conceded % (leakage containment) for the Top 10 bowlers.

#### Important Observations:
- Under pressure, the game polarizes: bowlers bowl more dot balls ($+2.7\%$), but also concede more boundaries ($+3.2\%$).
- **Elite Dot Generation:** Tim Southee ($57.8\%$ raw dots), Trent Boult ($52.2\%$), and Haris Rauf ($49.1\%$) produce scoreless deliveries on approximately half of all high-pressure deliveries.
- **Boundary Restriction:** Tim Southee ($9.38\%$ boundaries conceded) and Mark Adair ($14.08\%$) successfully prevent boundaries, suffocating chasing teams.

---

### Chart 14: Top 10 Bowlers Ranked by BoRS
**File:** `outputs/visualizations/14_top10_bowlers_bors.png`

```
Official Top 10 Bowlers:
Rank | Player Name        | High LB | High RC | Obs Econ | Bayes Econ (Econ*) | Bayes Wk% (Wk*) | BoRS Score
:---:|--------------------|:-------:|:-------:|:--------:|:------------------:|:---------------:|:----------:
 1   | Tim Southee        | 64      | 55      | 5.16     | 6.87               | 8.25%           | 90.69
 2   | Keshav Maharaj     | 78      | 81      | 6.23     | 7.34               | 7.35%           | 79.94
 3   | Haris Rauf         | 106     | 120     | 6.79     | 7.52               | 7.31%           | 78.84
 4   | Mark Adair         | 71      | 63      | 5.32     | 6.87               | 4.47%           | 74.70
 5   | Shoriful Islam     | 61      | 69      | 6.79     | 7.81               | 6.67%           | 74.01
 6   | Harshit Rana       | 158     | 207     | 7.86     | 8.15               | 5.97%           | 72.85
 7   | Wanindu Hasaranga  | 198     | 225     | 6.82     | 7.27               | 6.21%           | 70.04
 8   | Trent Boult        | 180     | 225     | 7.50     | 7.84               | 4.96%           | 69.72
 9   | Simarjeet Singh    | 60      | 80      | 8.00     | 8.48               | 5.83%           | 69.40
 10  | Lungi Ngidi        | 110     | 134     | 7.31     | 7.86               | 5.26%           | 68.89
```

#### What the Chart Shows:
Horizontal ranking chart displaying the final Bowler Reliability Scores (BoRS) for Tier 1 qualified bowlers ($N \ge 60$ legal balls).

#### Important Observations:
- **Tim Southee (Rank #1, BoRS: 90.69):** Outperforms the field through a rare combination of sub-5.2 raw economy, 8.25% breakthrough rate, and +1.73 RPO clutch tightening.
- **Keshav Maharaj & Haris Rauf (Ranks #2 & #3, BoRS: 79.94 & 78.84):** Demonstrate that both spin and extreme pace can dominate high pressure when paired with wicket-taking potency.
- **Volume Anchors:** Wanindu Hasaranga ($198$ balls), Trent Boult ($180$ balls), and Harshit Rana ($158$ balls) prove their reliability across immense multi-year samples.

---

### Chart 15: Top 10 Bowlers Four-Component Breakdown
**File:** `outputs/visualizations/15_top10_bowler_components.png`

```
Component Weights:
- Economy Score (Inverted): 40% (Run containment)
- Breakthrough Wicket Score: 25% (Wicket taking)
- Dot Ball Control Score:   20% (Pressure generation)
- Clutch Tightening Score:  15% (Economy improvement under pressure)
```

#### What the Chart Shows:
Grouped bar chart displaying the four standardized sub-scores for each Top 10 bowler.

#### Important Observations:
- **Tim Southee:** Scores $85+$ across three components: Dot Control ($98.93$), Clutch Tightening ($94.53$), and Wickets ($90.05$).
- **Mark Adair:** High Economy score ($85.55$) and Clutch Tightening ($96.12$), but lower Wicket score ($39.60$).
- **Trent Boult:** Highest Dot Ball Control score among elite pacers ($97.73$), reflecting his ability to bowl consecutive scoreless deliveries in the Powerplay.

---

# PART D — PHASE SPECIALIST ANALYSIS

---

### Chart 16: Phase Specialists Grid (Six-Panel Master Comparison)
**File:** `outputs/visualizations/16_phase_specialists_grid.png`

```
Phase Specialists Summary (Top 3 per Category):
Category            | Rank 1                    | Rank 2                    | Rank 3
--------------------|---------------------------|---------------------------|---------------------------
Batting Powerplay   | Cameron Green (SR* 143.5) | Nicholas Pooran (SR* 142.5)| Shreyas Iyer (SR* 136.9)
Batting Middle      | Patrick Cummins (SR* 136.6)| Shivam Dube (SR* 136.2)    | Suryakumar Yadav (SR* 135.2)
Batting Death       | Rinku Singh (SR* 186.2)   | MS Dhoni (SR* 179.6)      | Rovman Powell (SR* 166.4)
Bowling Powerplay   | Nasum Ahmed (Econ* 7.10)  | Tim Southee (Econ* 7.31)  | Mark Adair (Econ* 7.39)
Bowling Middle      | M Theekshana (Econ* 6.89) | R Ashwin (Econ* 7.06)     | W Hasaranga (Econ* 7.38)
Bowling Death       | Mohit Sharma (Econ* 6.86) | Prasidh Krishna (Econ* 7.12)| Yash Thakur (Econ* 7.36)
```

#### What the Chart Shows:
A 6-panel grid (2 rows $\times$ 3 columns) displaying the Top 5 qualified specialists in each phase against phase-specific population priors.

#### Important Observations:
1. **Batting Powerplay (Overs 1–6):**
   Cameron Green ($143.52$ Bayesian SR, $58$ balls) and Nicholas Pooran ($142.46$ SR, $56$ balls) lead. When early wickets fall, these batters counter-attack over the 30-yard circle rather than retreating into a defensive shell.
2. **Batting Middle Overs (Overs 7–15):**
   Patrick Cummins ($136.64$ SR) and Shivam Dube ($136.17$ SR, $130$ balls) dominate. Dube's ability to target spin in overs 7–15 provides game-breaking acceleration.
3. **Batting Death Overs (Overs 16–20):**
   Rinku Singh ($186.22$ Bayesian SR; $236.07$ raw SR across $61$ balls) and MS Dhoni ($179.55$ Bayesian SR; $197.37$ raw SR across $152$ balls) represent the pinnacle of modern T20 death finishing.
4. **Bowling Powerplay (Overs 1–6):**
   Nasum Ahmed ($7.10$ Bayesian Econ) and Tim Southee ($7.31$ Econ) strangle top-order scoring during fielding restrictions.
5. **Bowling Middle Overs (Overs 7–15):**
   Dominated by mystery spin and finger spin: Maheesh Theekshana ($6.89$ Econ), Ravichandran Ashwin ($7.06$ Econ), and Wanindu Hasaranga ($7.38$ Econ).
6. **Bowling Death Overs (Overs 16–20):**
   Mohit Sharma ($6.86$ Bayesian Econ across $31$ death balls) leads through back-of-the-hand slower balls and wide yorker execution.

---

## Technical Appendix: Reproduction Instructions

All charts can be regenerated using:
```bash
python src/visualizations/run_all.py
```
- Total execution time: $\sim 8.5$ seconds.
- Resolution: $300$ DPI.
- Output Directory: `outputs/visualizations/`.
