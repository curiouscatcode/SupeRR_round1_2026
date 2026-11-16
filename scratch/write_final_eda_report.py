import os

final_report_content = """# Step 9.2 — Finalized Exploratory Data Analysis & Visual Discovery Report

**Project:** SupeRR Selector Round 1  
**Stage:** Step 9.2 — Finalized EDA Report (Post-Reconciliation)  
**Author:** Antigravity (Google DeepMind Agentic System)  
**Date:** November 15, 2026  
**Status:** Certified, Reconciled & Frozen  
**Governing Methodology:** Step 6.3 Final Reliability Specification & Step 7.4 / 7.4.1 Certified Scoring Engine  
**Reconciliation Authority:** Step 9.1 Final Discrepancy Reconciliation (`step_9_1_discrepancy_reconciliation.md`)  

---

## Executive Summary

This report delivers the finalized and reconciled exploratory data analysis (EDA) and visual discovery documentation for the frozen player reliability scoring outputs of **SupeRR Selector Round 1**. The core objective of this competition is:

$$\\textbf{Identify the Most Reliable Players Under Pressure}$$

Following the rigorous empirical calibration and independent audits completed in Steps 6.3, 7.1–7.4, 7.4.1, 9, and 9.1, the evaluation framework applies **Pressure-Weighted Situational Value Added (PWSVA)** for batters and **Situational Bowling Value Added (SBVA)** for bowlers, incorporating:
1. Continuous pressure weighting $w(P) = (P / 50)^\\alpha$ with baseline exponent $\\alpha = 1.00$.
2. Empirical Bayes shrinkage toward situational replacement level ($0.0$) using Kish Effective Sample Size ($\\text{ESS}$) with shrinkage priors $K_{\\text{bat}} = 600$ and $K_{\\text{bowl}} = 500$.
3. 36-cell situational baseline models calibrated via match-stratified out-of-sample folds.
4. Dynamic, context-dependent wicket valuation $\\lambda_{\\text{wkt}}(u_t, W_{\\text{rem},t})$.
5. Block bootstrap resampling ($B = 1000$ match clusters) to compute empirical standard errors and 95% confidence intervals.

### Strict Scope Boundaries & Analytical Epistemology
In accordance with competition rules and the Step 9.1 reconciliation:
- **Immutable Methodology:** Scoring formulas, shrinkage parameters, baseline cells, and eligibility thresholds ($N(P \\ge 50) \\ge 50$) are strictly frozen and unaltered.
- **Epistemological Discipline:** A strict distinction is maintained between **statistically supported conclusions** (supported by inferential bootstrap intervals and out-of-sample calibration) and **descriptive observations** (sample-level distributions, phase breakdowns, and dual-format associations).
- **Missing Data Discipline:** No missing data are imputed or interpreted as zero; only validated ball-by-ball records from the 186,780 deliveries across IPL and T20 International cricket are analyzed.
- **Finalized Corrections Applied:** This document fully incorporates the verified corrections from Step 9.1, including exact alpha sensitivity rank correlations, striker-ID cross-format matching, verified phase heatmap metrics, and audited big-name player leaderboards.

---

## 1. Overall Player Rankings and Podium Dynamics

The frozen Step 7.4 scoring pipeline evaluated 297 qualified batters and 292 qualified bowlers. The Top 20 players in each discipline are visualized below, distinguishing the primary Top 10 cohort from the chasing 11–20 pack.

### 1.1 Batting Reliability Rankings (PWSVA)

![Figure 1: Top 20 Batters](../step_8_eda/figures/fig01_batting_top20_rankings.png)

```
========================================================================================================================
Rank  Player                  Team / Format              Shrunk Score  Raw Score  Raw Balls  Kish ESS  P>=50 Opps  95% CI
========================================================================================================================
1     Vaibhav Sooryavanshi    Rajasthan Royals (IPL/T20)    +0.3487     +0.7614      564       506.9       262    [+0.142, +0.523]
2     Suryakumar Yadav        India (IPL/T20I)              +0.2819     +0.3558     2638      2287.2      1087    [+0.183, +0.370]
3     Abhishek Sharma         Sunrisers Hyderabad (IPL/T20) +0.2703     +0.3547     2195      1923.3      1055    [+0.130, +0.399]
4     Tim David               Australia (IPL/T20I)          +0.2571     +0.4144     1163       980.6       535    [+0.129, +0.378]
5     Heinrich Klaasen        Sunrisers Hyderabad (IPL/T20) +0.2201     +0.3357     1409      1142.0       560    [+0.124, +0.307]
6     Phil Salt               England (IPL/T20I)            +0.1954     +0.2813     1591      1364.7       691    [+0.063, +0.303]
7     Namboori Tilak Varma    Mumbai Indians (IPL/T20I)     +0.1745     +0.2277     2338      1968.9       974    [+0.080, +0.267]
8     Travis Head             Sunrisers Hyderabad (IPL/T20) +0.1625     +0.2611     1096       988.6       546    [+0.002, +0.320]
9     Andre Russell           Kolkata Knight Riders (IPL/T) +0.1579     +0.3239      698       570.7       318    [+0.030, +0.285]
10    Reeza Hendricks         South Africa (T20I)           +0.1564     +0.2874      776       715.9       397    [+0.007, +0.287]
------------------------------------------------------------------------------------------------------------------------
11    Rajat Patidar           Royal Challengers Bengaluru   +0.1543     +0.2745      867       770.3       337    [+0.036, +0.268]
12    Josh Inglis             Australia (IPL/T20I)          +0.1449     +0.2599      855       755.9       352    [-0.001, +0.287]
13    Dinesh Karthik          Royal Challengers Bengaluru   +0.1395     +0.2912      633       552.1       390    [+0.020, +0.256]
14    Shreyas Iyer            India (IPL/T20I)              +0.1350     +0.1887     1751      1507.1       735    [+0.009, +0.237]
15    Shashank Singh          Punjab Kings (IPL)            +0.1343     +0.3081      552       463.4       222    [+0.007, +0.254]
16    Will Jacks              Royal Challengers Bengaluru   +0.1311     +0.2750      562       492.3       221    [-0.008, +0.269]
17    Jos Buttler             Rajasthan Royals (IPL/T20I)   +0.1306     +0.1642     2675      2330.2      1101    [+0.037, +0.219]
18    Marcus Stoinis          Lucknow Super Giants (IPL/T)  +0.1293     +0.1836     1812      1554.4       808    [+0.025, +0.228]
19    Mitchell Marsh          Lucknow Super Giants (IPL/T)  +0.1272     +0.1796     1656      1456.7       763    [+0.007, +0.247]
20    Sanvir Singh            Sunrisers Hyderabad (IPL)     +0.1197     +0.3995      220       196.4        89    [+0.008, +0.259]
========================================================================================================================
```

#### Analytical Observations:
- **Dominance of High-Volume Anchors and Finishers:** Suryakumar Yadav (Rank 2, score $+0.2819$) and Abhishek Sharma (Rank 3, score $+0.2703$) combine massive sample sizes ($\text{ESS} > 1900$) with exceptional raw situational run creation ($+0.355$ runs/ball above context).
- **Extreme Outlier Performance:** Vaibhav Sooryavanshi (Rank 1, score $+0.3487$) achieved an unprecedented raw score ($+0.7614$). Even under heavy shrinkage ($K_{\text{bat}} = 600$, reducing raw value by $54.2\%$), his score remains #1.
- **The Rank 10 Cutoff Boundary:** The score differential between Rank 10 (Reeza Hendricks, $+0.1564$) and Rank 11 (Rajat Patidar, $+0.1543$) is a minuscule **$0.0020$ runs per ball**. From an inferential standpoint, these players are indistinguishable, confirming that the Top 10 boundary represents a continuous performance spectrum rather than a discrete talent discontinuity.

---

### 1.2 Bowling Reliability Rankings (SBVA)

![Figure 2: Top 20 Bowlers](../step_8_eda/figures/fig02_bowling_top20_rankings.png)

```
========================================================================================================================
Rank  Player                  Team / Format              Shrunk Score  Raw Score  Raw Balls  Kish ESS  P>=50 Opps  95% CI
========================================================================================================================
1     Rashid Khan             Gujarat Titans (IPL/T20I)     +0.1756     +0.2147     2648      2245.9       901    [+0.081, +0.278]
2     Jasprit Bumrah          Mumbai Indians (IPL/T20I)     +0.1541     +0.2103     1606      1369.7       838    [+0.024, +0.278]
3     Sunil Narine            Kolkata Knight Riders (IPL)   +0.1442     +0.2020     1464      1246.3       572    [+0.056, +0.233]
4     Josh Hazlewood          Royal Challengers Bengaluru   +0.1330     +0.1904     1368      1159.5       731    [+0.002, +0.283]
5     Wanindu Hasaranga       Sri Lanka (IPL/T20I)          +0.1184     +0.1537     1932      1675.4       612    [+0.036, +0.200]
6     Bhuvneshwar Kumar       Sunrisers Hyderabad (IPL/T20) +0.1065     +0.1349     2159      1875.7      1317    [-0.009, +0.219]
7     Abrar Ahmed             Pakistan (T20I)               +0.1058     +0.1933      751       604.7       263    [-0.025, +0.228]
8     Kuldeep Yadav           Delhi Capitals (IPL/T20I)     +0.1027     +0.1346     1884      1608.6       627    [+0.008, +0.210]
9     Mahedi Hasan            Bangladesh (T20I)             +0.1025     +0.1700      860       760.3       398    [-0.044, +0.247]
10    Mujeeb Ur Rahman        Afghanistan (IPL/T20I)        +0.1024     +0.1770      772       686.6       412    [-0.012, +0.215]
------------------------------------------------------------------------------------------------------------------------
11    Mosaddek Hossain        Bangladesh (T20I)             +0.1000     +0.4468      159       144.3        50    [-0.031, +0.304]
12    Blessing Muzarabani     Zimbabwe (IPL/T20I)           +0.0996     +0.1661      817       749.3       512    [-0.009, +0.215]
13    Mohammed Shami          Gujarat Titans (IPL/T20I)     +0.0989     +0.1438     1228      1100.8       746    [-0.063, +0.262]
14    Mohsin Khan             Lucknow Super Giants (IPL)    +0.0978     +0.1791      654       601.7       376    [-0.086, +0.274]
15    Haider Ali              United Arab Emirates (T20I)   +0.0944     +0.2836      270       249.6       127    [-0.018, +0.239]
16    Trent Boult             Rajasthan Royals (IPL/T20I)   +0.0922     +0.1272     1501      1313.6       818    [-0.013, +0.215]
17    Nathan Ellis            Punjab Kings (IPL/T20I)       +0.0869     +0.1466      884       722.9       511    [-0.027, +0.198]
18    Nuwan Thushara          Mumbai Indians (IPL/T20I)     +0.0858     +0.1783      541       467.4       306    [-0.019, +0.187]
19    Akila Dananjaya         Sri Lanka (T20I)              +0.0833     +0.2662      257       230.1       107    [-0.021, +0.201]
20    Ravi Bishnoi            Lucknow Super Giants (IPL/T)  +0.0827     +0.1070     1960      1689.6       716    [-0.011, +0.174]
========================================================================================================================
```

#### Analytical Observations:
- **Spin Dominance in High-Pressure Suppression:** Spinners occupy 7 of the Top 10 bowling positions (Rashid Khan, Sunil Narine, Wanindu Hasaranga, Abrar Ahmed, Kuldeep Yadav, Mahedi Hasan, Mujeeb Ur Rahman). Their ability to suppress boundary rates and force wickets during middle and death overs under high run-rate requirements drives exceptional SBVA.
- **Pace Bowling Heavyweights:** Jasprit Bumrah (Rank 2, score $+0.1541$) and Josh Hazlewood (Rank 4, score $+0.1330$) stand out as elite pacers who consistently bowl the highest-pressure phases (death and powerplay).
- **The Cutoff Margin:** The margin between Rank 10 (Mujeeb Ur Rahman, $+0.1024$) and Rank 11 (Mosaddek Hossain, $+0.1000$) is just **$0.0024$ runs per ball**.

---

## 2. Empirical Bayes Shrinkage Mechanics and Sample Size Dynamics

Empirical Bayes shrinkage stabilizes performance estimates by regressing raw values toward the population replacement level ($0.0$). The shrinkage factor is governed by:

$$\text{Shrunk Score} = \text{Raw Score} \times \frac{\text{ESS}}{\text{ESS} + K}$$

Where $K_{\text{bat}} = 600$ and $K_{\text{bowl}} = 500$.

### 2.1 Batting Shrinkage vs. Raw Sample Size

![Figure 3: Batting Score vs Sample Size](../step_8_eda/figures/fig03_batting_score_vs_sample_size.png)

#### Shrinkage Dynamics in Batting:
1. **Small-Sample Damping:** At $\text{ESS} \approx 600$, exactly $50\%$ of a player's raw score is retained. Vaibhav Sooryavanshi ($\text{ESS} = 506.9$) faces a shrinkage factor of $506.9 / (506.9 + 600) = 0.4579$, compressing his $+0.7614$ raw score to $+0.3487$.
2. **High-Volume Retention:** Suryakumar Yadav ($\text{ESS} = 2287.2$) retains $2287.2 / (2287.2 + 600) = 79.22\%$ of his raw score, dropping only from $+0.3558$ to $+0.2819$.
3. **Prevention of Small-Sample Artifacts:** Without shrinkage, fringe players with fewer than 150 balls would dominate the leaderboard due to transient hot streaks. The hyperbolic shrinkage curve effectively shields the leaderboard from noise.

---

### 2.2 Bowling Shrinkage vs. Raw Sample Size

![Figure 4: Bowling Score vs Sample Size](../step_8_eda/figures/fig04_bowling_score_vs_sample_size.png)

#### Shrinkage Dynamics in Bowling:
1. **Filtering Volatile Spells:** Mosaddek Hossain achieved a staggering raw score of $+0.4468$ over 159 legal balls ($\text{ESS} = 144.3$). Shrinkage with $K_{\text{bowl}} = 500$ reduces his score by $77.6\%$ to $+0.1000$, correctly placing him just outside the Top 10 (Rank 11).
2. **Rewarding Sustained Excellence:** Rashid Khan ($\text{ESS} = 2245.9$) retains $2245.9 / (2245.9 + 500) = 81.79\%$ of his raw score, solidifying his status as the premier pressure bowler across world cricket.
3. **Variance Funnel Effect:** The scatter plot illustrates a classic variance funnel: dispersion collapses as sample size increases, with elite players clearly breaking away above the upper confidence envelope.

---

## 3. Uncertainty Quantification and Ranking Stability

To evaluate the statistical robustness of the rankings, 1,000 match-level block bootstrap iterations were performed. Resampling entire matches accounts for intra-match correlation and clustered delivery dependencies.

### 3.1 Confidence Intervals and Overlapping Uncertainty

![Figure 5: Batting Uncertainty](../step_8_eda/figures/fig05_batting_uncertainty_top10.png)
![Figure 6: Bowling Uncertainty](../step_8_eda/figures/fig06_bowling_uncertainty_top10.png)

#### Detailed Bootstrap Uncertainty Metrics:
```
====================================================================================================
Player                   Discipline   Shrunk Score   Bootstrap SE   95% Bootstrap CI   Overlap With
====================================================================================================
Vaibhav Sooryavanshi     Batting         +0.3487        0.0975      [+0.142, +0.523]   Ranks 2–10
Suryakumar Yadav         Batting         +0.2819        0.0483      [+0.183, +0.370]   Ranks 1, 3–6
Abhishek Sharma          Batting         +0.2703        0.0688      [+0.130, +0.399]   Ranks 1, 2, 4–8
Tim David                Batting         +0.2571        0.0638      [+0.129, +0.378]   Ranks 1–7
Heinrich Klaasen         Batting         +0.2201        0.0462      [+0.124, +0.307]   Ranks 2–9
Phil Salt                Batting         +0.1954        0.0611      [+0.063, +0.303]   Ranks 3–11
Namboori Tilak Varma     Batting         +0.1745        0.0478      [+0.080, +0.267]   Ranks 4–12
Travis Head              Batting         +0.1625        0.0799      [+0.002, +0.320]   Ranks 4–15
Andre Russell            Batting         +0.1579        0.0650      [+0.030, +0.285]   Ranks 5–15
Reeza Hendricks          Batting         +0.1564        0.0715      [+0.007, +0.287]   Ranks 5–15
----------------------------------------------------------------------------------------------------
Rashid Khan              Bowling         +0.1756        0.0505      [+0.081, +0.278]   Ranks 2–5
Jasprit Bumrah           Bowling         +0.1541        0.0634      [+0.024, +0.278]   Ranks 1, 3–8
Sunil Narine             Bowling         +0.1442        0.0460      [+0.056, +0.233]   Ranks 1, 2, 4–8
Josh Hazlewood           Bowling         +0.1330        0.0709      [+0.002, +0.283]   Ranks 1–10
Wanindu Hasaranga        Bowling         +0.1184        0.0416      [+0.036, +0.200]   Ranks 2–10
Bhuvneshwar Kumar        Bowling         +0.1065        0.0583      [-0.009, +0.219]   Ranks 4–13
Abrar Ahmed              Bowling         +0.1058        0.0645      [-0.025, +0.228]   Ranks 4–13
Kuldeep Yadav            Bowling         +0.1027        0.0514      [+0.008, +0.210]   Ranks 4–13
Mahedi Hasan             Bowling         +0.1025        0.0743      [-0.044, +0.247]   Ranks 4–15
Mujeeb Ur Rahman         Bowling         +0.1024        0.0577      [-0.012, +0.215]   Ranks 4–15
====================================================================================================
```

#### Statistical Inferences on Rank Separation:
- **Batting Tier Separation:** The point estimates of Ranks 2–4 (Suryakumar $+0.2819$, Abhishek $+0.2703$, David $+0.2571$) form a tightly clustered elite tier. While their 95% confidence intervals overlap, their mutual distance from the population mean ($+0.0041$) is statistically significant ($p < 0.001$).
- **Bowling Clustered Density:** The bowling Top 10 exhibits substantial overlap between Ranks 6 and 10 (scores spanning $+0.1065$ to $+0.1024$). Bhuvneshwar Kumar, Abrar Ahmed, Kuldeep Yadav, Mahedi Hasan, and Mujeeb Ur Rahman are separated by less than $0.004$ runs/ball. Their ranking order should be interpreted as an elite tier rather than an absolute hierarchy.

---

### 3.2 Sensitivity to Pressure Exponent ($\alpha = 1.00 \text{ vs } 1.25$)

To verify whether rankings are fragile artifacts of the linear pressure exponent ($\alpha = 1.00$), scores were re-computed under a super-linear weighting regime ($\alpha = 1.25$), which exponentially rewards climax-over performance ($P > 75$).

![Figure 7: Alpha Sensitivity](../step_8_eda/figures/fig07_alpha_sensitivity_slope.png)

#### Rank Movement Dynamics:
- **Exact Rank Correlations (Corrected):** Independent re-computation from the frozen sensitivity datasets confirms that Spearman's rank correlation between $\alpha = 1.00$ and $\alpha = 1.25$ across all qualified players is:
  $$\rho_{\text{bat}} = \mathbf{0.9978} \quad (N = 297), \qquad \rho_{\text{bowl}} = \mathbf{0.9981} \quad (N = 292)$$
  *(Note: A typographical error in early Step 8.1 draft narrative reported $0.9881$ and $0.9854$; the panel titles of Figure 7 and the Step 7.4.1 independent audit are verified as exact).*
- **Top 10 Batting Stability:** The batting Top 8 positions remain 100% invariant under $\alpha = 1.25$. Ranks 9 and 10 experience a minor swap: Reeza Hendricks climbs from #10 to #9 ($+0.1783$), while Andre Russell moves from #9 to #10 ($+0.1772$).
- **The Mohammed Shami Climax Surge:** In bowling, Mohammed Shami exhibits the most significant climb, surging from **Rank 13 to Rank 7** under $\alpha = 1.25$. This movement occurs because Shami operates heavily in extreme death-over scenarios where $P \ge 75$, directly capturing the convex reward of higher $\alpha$. Conversely, Abrar Ahmed drops from #7 to #10, and Mahedi Hasan drops from #9 to #13 due to their concentration in lower-pressure middle-over containment.

---

## 4. Pressure Exposure Profiles and Situational Leverage

The delivery-level pressure index $P \in [0, 100]$ quantifies match leverage. Across the 186,780 deliveries analyzed, pressure follows distinct empirical distributions between batting and bowling tracking datasets.

### 4.1 Population Delivery Pressure Distribution

![Figure 8: Delivery Pressure Distribution](../step_8_eda/figures/fig08_pressure_distribution_deliveries.png)

```
====================================================================================================
Pressure Regime            Pressure Range (P)     Batting Deliveries (%)    Bowling Deliveries (%)
====================================================================================================
Low Leverage               P < 30                       21.4%                     23.8%
Moderate Leverage          30 <= P < 50                 36.2%                     38.5%
High Leverage              50 <= P < 75                 36.4%                     36.8%
Climax Leverage            P >= 75                       6.0%                      0.88%
----------------------------------------------------------------------------------------------------
Total Deliveries Analyzed                               93,390                    93,390
Mean Delivery Pressure (P)                              47.35                     45.15
====================================================================================================
```

#### Analytical Observations:
- **Climax Concentration in Batting:** Batting deliveries feature a $6.04\%$ share of climax-level pressure ($P \ge 75$), whereas bowling tracking shows $0.88\%$. This divergence reflects the asymmetrical leverage in run chases, where batting pressure spikes non-linearly when the required run rate escalates beyond $12.0$ runs per over with fewer wickets in hand.

---

### 4.2 Tactical Pressure Exposure of Top 10 Players

![Figure 9: Player Pressure Exposure](../step_8_eda/figures/fig09_top_players_pressure_exposure.png)

#### Tactical Exposure Highlights:
1. **Jasprit Bumrah's Extreme Leverage:** Over **$52.18\%$ of Bumrah's career deliveries** (838 of 1,606 balls) are bowled under high pressure ($P \ge 50$). Team captains systematically deploy Bumrah as an emergency fire-fighter during powerplay crunches and death-over climaxes.
2. **Heinrich Klaasen and Tim David:** Both batters experience over $39.7\%$ of their balls in $P \ge 50$ conditions, reflecting their specialized role as middle-order rescue hitters tasked with elevating run rates against defensive bowling.
3. **Top-Order Powerplay Exploiters:** Travis Head ($49.8\%$ at $P < 50$) and Phil Salt ($43.4\%$ at $P < 50$) face substantial low-to-moderate pressure deliveries during initial powerplays, where they generate outsized value before pressure escalates.

---

## 5. Phase Specialization and Cross-Format Generalizability

T20 matches partition into three distinct operational regimes:
- **Powerplay (Overs 1–6):** Mandatory field restrictions, fresh ball, high boundary incentives.
- **Middle Overs (Overs 7–15):** Spread fields, spin consolidation, wicket preservation.
- **Death Overs (Overs 16–20):** High-risk boundary hunting, yorkers, maximum situational leverage.

### 5.1 Situational Phase Heatmaps

![Figure 10: Batting Phase Heatmap](../step_8_eda/figures/fig10_batting_phase_heatmap.png)
![Figure 11: Bowling Phase Heatmap](../step_8_eda/figures/fig11_bowling_phase_heatmap.png)

#### Crucial Metric Distinction: Unshrunk Situational Value Added per Ball
The values plotted in Figures 10 and 11 represent **unshrunk, pressure-weighted situational value added per ball** within each match phase:
$$\text{Phase Performance} = \frac{\sum_{i \in \text{phase}} w(P_i) \cdot \text{SVA}_i}{\sum_{i \in \text{phase}} w(P_i)}$$

- **Explicit Metric Separation:** These values are **NOT official Step 7.4 reliability scores**. The official Step 7.4 scores apply Empirical Bayes shrinkage across a player's full career opportunities ($K_{\text{bat}} = 600, K_{\text{bowl}} = 500$). The heatmaps display raw, within-phase run-creation or run-prevention rates above baseline to evaluate tactical phase specialization.
- **Sample Size Threshold Rule ($N \ge 20$):** In both heatmaps, any phase cell with fewer than 20 deliveries faced or bowled is suppressed as **`N/A`** to eliminate extreme small-sample noise.

#### Verified Phase Specialization Profiles (Corrected Table):

```
========================================================================================================================
Player                 Discipline   Powerplay (1–6)            Middle Overs (7–15)        Death Overs (16–20)
========================================================================================================================
Vaibhav Sooryavanshi   Batting      +0.77 (373 balls)          +0.66 (181 balls)          N/A (10 balls < 20)
Suryakumar Yadav       Batting      +0.16 (607 balls)          +0.44 (1673 balls)         +0.40 (358 balls)
Abhishek Sharma        Batting      +0.40 (1462 balls)         +0.21 (670 balls)          +0.24 (63 balls)
Tim David              Batting      +1.23 (50 balls)           +0.33 (545 balls)          +0.41 (568 balls)
Heinrich Klaasen       Batting      +0.25 (102 balls)          +0.39 (915 balls)          +0.24 (392 balls)
Phil Salt              Batting      +0.32 (950 balls)          +0.13 (546 balls)          +0.54 (95 balls)
Namboori Tilak Varma   Batting      +0.21 (341 balls)          +0.17 (1458 balls)         +0.38 (539 balls)
Travis Head            Batting      +0.32 (841 balls)          -0.02 (248 balls)          N/A (7 balls < 20)
Andre Russell          Batting      N/A (0 balls < 20)         +0.37 (363 balls)          +0.29 (335 balls)
Reeza Hendricks        Batting      +0.15 (392 balls)          +0.47 (334 balls)          +0.25 (50 balls)
------------------------------------------------------------------------------------------------------------------------
Rashid Khan            Bowling      -0.11 (240 balls)          +0.19 (1892 balls)         +0.45 (516 balls)
Jasprit Bumrah         Bowling      +0.08 (702 balls)          +0.21 (378 balls)          +0.42 (526 balls)
Sunil Narine           Bowling      -0.09 (192 balls)          +0.16 (1068 balls)         +0.71 (204 balls)
Josh Hazlewood         Bowling      +0.30 (732 balls)          -0.00 (253 balls)          +0.03 (383 balls)
Wanindu Hasaranga      Bowling      +0.06 (108 balls)          +0.14 (1554 balls)         +0.26 (270 balls)
Bhuvneshwar Kumar      Bowling      +0.23 (1302 balls)         -0.32 (168 balls)          +0.03 (689 balls)
Abrar Ahmed            Bowling      -0.02 (144 balls)          +0.23 (498 balls)          +0.40 (109 balls)
Kuldeep Yadav          Bowling      N/A (12 balls < 20)        +0.13 (1586 balls)         +0.19 (286 balls)
Mahedi Hasan           Bowling      +0.27 (378 balls)          +0.09 (414 balls)          -0.10 (68 balls)
Mujeeb Ur Rahman       Bowling      +0.06 (390 balls)          +0.38 (306 balls)          +0.23 (76 balls)
========================================================================================================================
```

#### Analytical Observations:
- **Phase Specialization in Batting:** 
  - *Powerplay Dominators:* Abhishek Sharma ($+0.40$ on 1462 balls), Phil Salt ($+0.32$ on 950 balls), and Travis Head ($+0.32$ on 841 balls) generate overwhelming situational run creation in Overs 1–6.
  - *Middle-Overs Masters:* Reeza Hendricks ($+0.47$ on 334 balls), Suryakumar Yadav ($+0.44$ on 1673 balls), and Heinrich Klaasen ($+0.39$ on 915 balls) provide peerless value against spin and non-boundary middle overs.
  - *Explosive Death Finishers:* Phil Salt ($+0.54$ on 95 balls), Tim David ($+0.41$ on 568 balls), Suryakumar Yadav ($+0.40$ on 358 balls), and Tilak Varma ($+0.38$ on 539 balls) achieve peak run acceleration under climax pressure.
- **Phase Specialization in Bowling:**
  - *Powerplay Stranglers:* Josh Hazlewood ($+0.30$ on 732 balls), Mahedi Hasan ($+0.27$ on 378 balls), and Bhuvneshwar Kumar ($+0.23$ on 1302 balls) excel with the new ball.
  - *Middle-Overs Anchors:* Mujeeb Ur Rahman ($+0.38$ on 306 balls), Abrar Ahmed ($+0.23$ on 498 balls), and Jasprit Bumrah ($+0.21$ on 378 balls) choke run flow in Overs 7–15.
  - *Lethal Death Enforcers:* Sunil Narine ($+0.71$ net runs saved/ball on 204 balls), Rashid Khan ($+0.45$ on 516 balls), Jasprit Bumrah ($+0.42$ on 526 balls), and Abrar Ahmed ($+0.40$ on 109 balls) exhibit extraordinary defensive resilience at the death.

---

### 5.2 Cross-Format Generalizability (IPL vs. T20 Internationals)

To evaluate whether high-pressure performance exhibits empirical consistency across institutional settings, players with $\ge 50$ balls faced or bowled in both the Indian Premier League (IPL) and T20 Internationals (T20I) were analyzed.

![Figure 12: Format Comparison](../step_8_eda/figures/fig12_format_comparison_dual_players.png)

```
========================================================================================================================
Discipline    Dual-Format Players (N)    Matching Basis         Pearson r    Spearman rho   Consistency Classification
========================================================================================================================
Batting               90                 Unique Striker ID        0.1149        0.1645      Low Raw Association (r ~ 0.11)
Bowling               97                 Unique Bowler ID         0.2338        0.2956      Moderate Raw Assoc. (r ~ 0.23)
========================================================================================================================
```

#### Technical Disambiguation of Dual-Format Populations:
- **The Abdul Samad String-Name Collision Resolved:** In early draft summaries, batting reported $N = 91$ because string matching combined two distinct players sharing the string name `"Abdul Samad"`:
  1. *Abdul Samad (India, `striker_id = 7446`):* Faced 424 IPL balls, 0 T20I balls.
  2. *Abdul Samad (Pakistan, `striker_id = 6922`):* Faced 0 IPL balls, 61 T20I balls.
  Neither individual player met the inclusion threshold ($N \ge 50$ balls in **both** formats). Matching strictly on unique `striker_id` removes this synthetic collision, verifying the true dual-format population at **$N = 90$ batters** with Pearson **$r = 0.1149$** and Spearman **$\rho = 0.1645$**.
- **Bowling Verification:** Bowling tracking has zero name collisions; all 97 dual-format bowlers map to unique player IDs, confirming **$N = 97$ bowlers** with Pearson **$r = 0.2338$** and Spearman **$\rho = 0.2956$**.

#### Methodological Framing of Cross-Format Metrics:
- **Descriptive Association, Not Disproof of Reliability:** The low observed correlations ($r = 0.1149$ and $r = 0.2338$) represent **unshrunk sample associations on small format slices** ($50 \le N \le 200$ balls). 
- **Errors-in-Variables Attenuation Bias:** Delivery-level outcomes in T20 cricket exhibit high intrinsic variance. Small sample sizes inherently suffer from high measurement noise, which mathematically attenuates observed sample correlations toward zero:
  $$r_{\text{obs}} = r_{\text{true}} \times \sqrt{\text{Rel}(\text{IPL}) \times \text{Rel}(\text{T20I})}$$
  These modest correlations describe raw sample volatility and demonstrate why Empirical Bayes shrinkage across full multi-competition career samples is essential. They should **not** be interpreted as proving or disproving a player's underlying cross-format latent skill.

---

## 6. Population-Level Distributions and Multidimensional Structure

### 6.1 Distributional Geometry: Skewness and Replacement Level

![Figure 13: Population Score Distributions](../step_8_eda/figures/fig13_population_score_distributions.png)

```
====================================================================================================
Metric                          Batting Population (N=297)          Bowling Population (N=292)
====================================================================================================
Mean Shrunk Score                         +0.0041                            -0.0307
Median Shrunk Score                       -0.0056                            -0.0315
Standard Deviation                         0.0718                             0.0715
Interquartile Range (IQR)             [-0.0417, +0.0372]                 [-0.0824, +0.0155]
Minimum Shrunk Score                      -0.1686                            -0.2674
Maximum Shrunk Score                      +0.3487                            +0.1756
Top 10 Cohort Mean Score                  +0.2225                            +0.1245
====================================================================================================
```

#### Distributional Insights:
- **Positive Skew in Batting:** The batting population exhibits pronounced positive skewness (right-tail elongation). While the median batter operates at $-0.0056$ (slightly below baseline), elite outliers achieve scores exceeding $+0.250$. High-pressure batting value is heavily concentrated in a small fraction of exceptional hitters.
- **Negative Centering in Bowling:** The bowling population mean is $-0.0307$, reflecting that the average qualified bowler concedes slightly more runs than the situational expectation under high-pressure conditions (where batting aggression peaks). The Top 10 bowlers ($+0.1245$) represent true positive outliers who consistently suppress run-scoring against the natural tide of late-innings acceleration.

---

### 6.2 Multidimensional Correlation Structure

![Figure 14: Multidimensional Correlations](../step_8_eda/figures/fig14_multidimensional_correlations.png)

#### Correlation Matrix Synthesis:
1. **Score vs. Kish ESS:** Weak positive correlation ($r \approx 0.18$ for batting, $r \approx 0.22$ for bowling). This confirms that Empirical Bayes shrinkage has successfully decoupled sample size from score magnitude—players do not rank highly merely because they played more matches.
2. **Score vs. Pressure Percentage:** Moderate positive correlation ($r \approx 0.24$ in bowling). Bowlers who perform well are entrusted by team captains with a higher percentage of clutch deliveries, creating a positive tactical selection feedback loop.
3. **Score vs. Bootstrap Standard Error:** Negative correlation ($r \approx -0.31$ for high-volume players). Elite players with larger sample sizes have smaller standard errors, confirming that the top ranks are supported by narrower confidence bounds.

---

## 7. Big-Name Player Analysis & Competition Implications

To evaluate where prominent international stars and IPL icons place within the frozen Step 7.4 rankings, an exhaustive audit of all requested marquee players was performed.

### 7.1 Authoritative Placement of Marquee Batters ($N = 297$)

```
========================================================================================================================
Player Name            Official Rank   Shrunk Score   Raw Score   Kish ESS   Balls Faced   95% Bootstrap Score CI
========================================================================================================================
Heinrich Klaasen       #5              +0.2201        +0.3357     1142.0     1409          [+0.1238, +0.3072]
Phil Salt              #6              +0.1954        +0.2813     1364.7     1591          [+0.0633, +0.3033]
Travis Head            #8              +0.1625        +0.2611      988.6     1096          [+0.0017, +0.3203]
Shreyas Iyer           #14             +0.1350        +0.1887     1507.1     1751          [+0.0085, +0.2366]
Jos Buttler            #17             +0.1306        +0.1642     2330.2     2675          [+0.0366, +0.2187]
Mitchell Marsh         #19             +0.1272        +0.1796     1456.7     1656          [+0.0069, +0.2471]
Harry Brook            #30             +0.0922        +0.1758      661.6      840          [-0.0671, +0.2234]
Shubman Gill           #31             +0.0921        +0.1163     2283.7     2606          [-0.0128, +0.1800]
Virat Kohli            #34             +0.0850        +0.1081     2201.2     2445          [+0.0005, +0.1547]
Babar Azam             #38             +0.0747        +0.1165     1071.6     1176          [-0.0255, +0.1589]
Mohammad Rizwan        #42             +0.0680        +0.1059     1074.1     1150          [-0.0142, +0.1401]
Sanju Samson           #44             +0.0665        +0.0873     1918.7     2207          [-0.0387, +0.1686]
KL Rahul (Lokesh)      #45             +0.0655        +0.0874     1795.7     1994          [-0.0359, +0.1486]
Pathum Nissanka        #51             +0.0561        +0.0800     1407.3     1525          [-0.0453, +0.1443]
Ravindra Jadeja        #121            +0.0065        +0.0113      802.7      938          [-0.0751, +0.0824]
Hardik Pandya          #130            +0.0018        +0.0024     1576.0     1867          [-0.0825, +0.0797]
Rishabh Pant           #154            -0.0097        -0.0153     1041.1     1226          [-0.0998, +0.0705]
Rohit Sharma           #168            -0.0164        -0.0231     1451.1     1561          [-0.1574, +0.0988]
Sam Curran             #189            -0.0228        -0.0422      702.5      784          [-0.1424, +0.0842]
Devdutt Padikkal       #284            -0.0936        -0.1574      880.2      973          [-0.2104, +0.0195]
========================================================================================================================
```

### 7.2 Authoritative Placement of Marquee Bowlers ($N = 292$)

```
========================================================================================================================
Player Name            Official Rank   Shrunk Score   Raw Score   Kish ESS   Balls Bowled  95% Bootstrap Score CI
========================================================================================================================
Rashid Khan            #1              +0.1756        +0.2147     2245.9     2648          [+0.0810, +0.2784]
Jasprit Bumrah         #2              +0.1541        +0.2103     1369.7     1606          [+0.0237, +0.2784]
Sunil Narine           #3              +0.1442        +0.2020     1246.3     1464          [+0.0555, +0.2334]
Josh Hazlewood         #4              +0.1330        +0.1904     1159.5     1368          [+0.0021, +0.2830]
Mohammed Shami         #13             +0.0989        +0.1438     1100.8     1228          [-0.0629, +0.2621]
Trent Boult            #16             +0.0922        +0.1272     1313.6     1501          [-0.0131, +0.2146]
Mitchell Santner       #37             +0.0508        +0.0684     1439.4     1677          [-0.0479, +0.1455]
Ravindra Jadeja        #45             +0.0403        +0.0572     1188.6     1337          [-0.0761, +0.1612]
Shaheen Shah Afridi    #46             +0.0402        +0.0645      828.5      934          [-0.0843, +0.1535]
Kagiso Rabada          #52             +0.0344        +0.0471     1351.2     1521          [-0.0691, +0.1506]
Mohammed Siraj         #61             +0.0215        +0.0284     1545.0     1750          [-0.1009, +0.1561]
Axar Patel             #66             +0.0195        +0.0239     2218.5     2604          [-0.0665, +0.1117]
Mitchell Starc         #203            -0.0712        -0.1264      644.7      737          [-0.2110, +0.0857]
Arshdeep Singh         #231            -0.0926        -0.1106     2578.8     3090          [-0.1730, -0.0059]
Sam Curran             #286            -0.1688        -0.2451     1105.5     1277          [-0.2668, -0.0712]
========================================================================================================================
```

### 7.3 Audited Catalog Notes Corrections
Independent verification of `unqualified_or_missing_players.csv` confirms:
1. **Ben Stokes:** Unqualified in both disciplines (Faced 34 total balls, 12 at $P \ge 50$; bowled 30 legal balls, 24 at $P \ge 50$; requires $\ge 50$).
2. **Steve Smith:** Completely absent from the 2022–2026 tracking dataset (0 deliveries faced or bowled).
3. **Shan Masood:** Batting near-miss (176 balls faced, 47 at $P \ge 50$; missed qualification threshold by 3 balls).
4. **Kieron Pollard:** Official Step 7.4 rank is **#244** (212 balls faced, 130 at $P \ge 50$, score $-0.038$), correcting an erroneous text note claiming #144 with 622 balls.
5. **Rishi Dhawan:** Completely **UNQUALIFIED in batting** (52 balls faced, 37 at $P \ge 50$), correcting an erroneous note claiming qualified at #223.
6. **Alzarri Joseph:** Official bowling rank is **#279** (1137 balls, score $-0.072$), correcting an erroneous note claiming #135.
7. **Haris Rauf:** Official bowling rank is **#51** (974 balls, score $+0.048$), correcting an erroneous note claiming #107.

---

### 7.4 Key Recommendations for SupeRR Selector Round 1
1. **Recruit for Phase Complementarity:** Selectors should avoid drafting two powerplay dominators without a dedicated death-overs finisher. Pairing an elite Powerplay aggressor (e.g., Phil Salt $+0.32$ or Abhishek Sharma $+0.40$) with an elite Death finisher (Tim David $+0.41$ or Heinrich Klaasen $+0.24$) produces optimal situational run creation.
2. **Anchor with Climax Bowling Assets:** Jasprit Bumrah (#2) and Sunil Narine (#3) represent indispensable tactical assets due to their proven ability to suppress boundary rates under extreme climax leverage ($P \ge 75$).
3. **Acknowledge Ranking Tiers:** The score differential between Rank 10 and Rank 11 in both disciplines is less than $0.0025$ runs/ball. Franchise decision-makers should view the Top 10 as an **elite interchangeable tier** rather than treating Rank 10 as fundamentally superior to Rank 11 or 12.

---

## 8. Artifact Certification & Sign-off

The visualizations, metrics, and analyses contained in this finalized report have been verified against the underlying datasets, reconciled against the authoritative Step 7.4 rankings, and certified for official submission to SupeRR Selector Round 1.

- **Finalized Report:** `outputs/step_9_2_eda_finalization/step_9_2_final_eda_report.md`
- **Correction Log:** `outputs/step_9_2_eda_finalization/step_9_2_correction_log.md`
- **Validation Report:** `outputs/step_9_2_eda_finalization/step_9_2_validation_report.md`
- **Figures Directory:** `outputs/step_8_eda/figures/` (14 high-resolution 300-DPI charts verified unchanged)
- **Big-Name Figures:** `outputs/step_8_eda/big_name_player_analysis/figures/` (8 high-resolution charts verified unchanged)
- **Methodology Version:** Step 6.3 Reconciled Specification (Frozen)
- **Audit Verification:** Step 7.4.1 Independent Audit & Step 9.1 Discrepancy Reconciliation

*Report finalized and certified.*
"""

with open('outputs/step_9_2_eda_finalization/step_9_2_final_eda_report.md', 'w', encoding='utf-8') as f:
    f.write(final_report_content)

print("Generated outputs/step_9_2_eda_finalization/step_9_2_final_eda_report.md successfully.")
