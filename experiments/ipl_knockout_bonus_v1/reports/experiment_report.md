# Comprehensive Experiment Report: IPL Knockout Bonus (v1)

**Experiment:** IPL Knockout Bonus (v1)  
**Author:** Antigravity (Google DeepMind Agentic System)  
**Date:** November 15, 2026  
**Status:** Complete & Certified for Independent Review  
**Governing Standard:** Frozen Step 7.4 Baseline Architecture; Isolated Execution  

---

## Executive Summary

This experiment evaluates whether scaling delivery-level pressure weights by a **knockout bonus multiplier** ($M \in \{1.10\times, 1.20\times, 1.25\times\}$) for performances in IPL playoff matches (**Qualifier 1**, **Eliminator**, **Qualifier 2**, and the **Final**) meaningfully and defensibly improves player reliability rankings.

### Core Evaluative Verdict
$$\textbf{Recommendation: DO NOT adopt the 1.20× Knockout Bonus into Official Rankings.}$$

While the concept of rewarding knockout heroics has strong narrative appeal, rigorous empirical and statistical testing demonstrates that:
1. **The Core Ranking Hierarchy is Already Highly Stable:** Macro rank correlation against the frozen baseline is **$\rho > 0.9996$** across all 297 batters and 292 bowlers. Knockout weighting does not discover hidden talent; it primarily perturbs a few boundary ranks.
2. **Top 10 Retention is Nearly Absolute:** The bowling Top 10 exhibits **$100\%$ retention** (zero players enter or leave across all multipliers). The batting Top 10 exhibits **$90\%$ retention**, with only a single borderline change: Rajat Patidar climbs from #11 to #8, displacing Reeza Hendricks (#10 to #11).
3. **Severe Small-Sample Volatility:** A tiny sample of playoff deliveries exerts disproportionate leverage. For example, **Mitchell Starc climbs 17 ranking spots** based on just **42 legal balls across 2 matches**, while **Akash Madhwal climbs 14 spots** based on **45 balls**. This directly contradicts the foundational goal of Empirical Bayes regularization, which is designed to prevent small-sample volatility from distorting rankings.
4. **Structural Tournament-Selection Bias:** Over **$69.4\%$ of qualified batters (206 of 297)** and **$71.9\%$ of qualified bowlers (210 of 292)** have zero knockout appearances (predominantly international-only cricketers like Babar Azam, Mohammad Rizwan, Reeza Hendricks, or players whose franchises missed the playoffs). Because delivery-level pressure $P \in [0, 100]$ already quantifies situational difficulty objectively, adding an institutional tournament-stage multiplier introduces arbitrary structural bias against international and non-playoff players.

---

## 1. Experimental Design & Audit Standards

The experiment tested four distinct weighting regimes:

| Version | Knockout Multiplier ($M$) | Non-Knockout Multiplier | Target Purpose |
| :--- | :---: | :---: | :--- |
| **Baseline** | **$1.00\times$** | $1.00\times$ | Certified Step 7.4 Frozen Baseline |
| **Experiment A** | **$1.10\times$** | $1.00\times$ | Mild Playoff Leverage (+10%) |
| **Experiment B** | **$1.20\times$** | $1.00\times$ | Target Proposed Bonus (+20%) |
| **Experiment C** | **$1.25\times$** | $1.00\times$ | High Playoff Leverage (+25%) |

### Mathematical Safeguards Enforced:
- **Delivery Weight Adjustment:** $w_i^{\text{adj}} = (P_i / 50.0) \times M$ for deliveries in the 19 audited knockout matches; $w_i^{\text{adj}} = (P_i / 50.0) \times 1.00$ for all other deliveries.
- **Dynamic Kish ESS Recalculation:** $\text{ESS}_{\text{adj}} = \left(\sum w_i^{\text{adj}}\right)^2 / \sum (w_i^{\text{adj}})^2$.
- **Consistent Empirical Bayes Shrinkage:** $K_{\text{bat}} = 600$, $K_{\text{bowl}} = 500$ applied to re-weighted raw scores.
- **Strict Zero-Knockout Invariance:** Confirmed mathematically and numerically: all 206 batters and 210 bowlers with zero knockout deliveries experience **exactly $0.00\times 10^0$ change** in raw score, Kish ESS, and shrunk score.
- **Population Preservation:** Exactly 297 batters and 292 bowlers; zero qualification rule alterations.

---

## 2. Batting Leaderboard Impact

### 2.1 Top 12 Batting Comparison Across Multipliers

```
========================================================================================================================
Base  1.10x  1.20x  1.25x  Player Name             KO Matches  KO Balls  Base Shrunk  1.20x Shrunk  Delta Score  Delta Rank
========================================================================================================================
1     1      1      1      Vaibhav Sooryavanshi        2          76       +0.3487      +0.3551       +0.00643       0
2     2      2      2      Suryakumar Yadav            4         104       +0.2819      +0.2825       +0.00063       0
3     3      3      3      Abhishek Sharma             4          16       +0.2703      +0.2654       -0.00495       0
4     4      4      4      Tim David                   4          38       +0.2571      +0.2545       -0.00254       0
5     5      5      5      Heinrich Klaasen            4          82       +0.2201      +0.2195       -0.00065       0
6     6      6      6      Phil Salt                   2          35       +0.1954      +0.1951       -0.00026       0
7     7      7      7      Namboori Tilak Varma        4          76       +0.1745      +0.1749       +0.00037       0
8     8      10     11     Travis Head                 4          39       +0.1625      +0.1568       -0.00568      -2
9     9      9      9      Andre Russell               0           0       +0.1579      +0.1579        0.00000       0
10    11     11     10     Reeza Hendricks             0           0       +0.1564      +0.1564        0.00000      -1
------------------------------------------------------------------------------------------------------------------------
11    10     8      8      Rajat Patidar               7         186       +0.1543      +0.1592       +0.00490      +3
12    12     12     12     Josh Inglis                 3          51       +0.1449      +0.1407       -0.00425       0
========================================================================================================================
```

![Figure 1: Batting Rank Changes](outputs/comparisons/figures/fig01_batting_rank_changes_1_20.png)

### 2.2 Key Batting Dynamics:
1. **The Rajat Patidar Entry (#11 $\to$ #8):**
   - Rajat Patidar is the sole player to penetrate the Top 10 under the knockout bonus. Over 7 playoff appearances, Patidar faced 186 balls and delivered outstanding situational value added (highlighted by his 112* off 54 in the 2022 Eliminator).
   - At $1.20\times$, his shrunk score rises by $+0.00490$ runs/ball (from $+0.1543$ to $+0.1592$). Because the baseline gap between Rank 10 (Hendricks, $+0.1564$) and Rank 11 (Patidar, $+0.1543$) was only $0.0020$ runs/ball, this bonus easily vaults Patidar into Rank 8.
2. **The Reeza Hendricks Exit (#10 $\to$ #11):**
   - Reeza Hendricks has zero IPL playoff appearances (international-only dataset). His score remains frozen at $+0.156353$. Patidar's upward surge passively pushes Hendricks out of the Top 10 by a razor-thin margin of $0.00045$ runs/ball.
3. **Travis Head's Playoff Penalty (#8 $\to$ #10):**
   - Travis Head faced 39 balls across 4 playoff matches in 2024, suffering early dismissals in Qualifier 1 (0 off 2) and the Final (0 off 1). Weighting these failures by $1.20\times$ reduces his score from $+0.1625$ to $+0.1568$, dropping him 2 spots.
4. **Top 7 Batters are Completely Invariant:**
   - Positions 1 through 7 (Sooryavanshi, Suryakumar, Abhishek, David, Klaasen, Salt, Tilak Varma) remain completely unchanged.

---

## 3. Bowling Leaderboard Impact

### 3.1 Top 12 Bowling Comparison Across Multipliers

```
========================================================================================================================
Base  1.10x  1.20x  1.25x  Player Name             KO Matches  KO Balls  Base Shrunk  1.20x Shrunk  Delta Score  Delta Rank
========================================================================================================================
1     1      1      1      Rashid Khan                 8         174       +0.1756      +0.1737       -0.00191       0
2     2      2      2      Jasprit Bumrah              2          48       +0.1541      +0.1526       -0.00152       0
3     3      3      3      Sunil Narine                2          48       +0.1442      +0.1433       -0.00092       0
4     4      4      4      Josh Hazlewood              6         139       +0.1330      +0.1362       +0.00314       0
5     5      5      5      Wanindu Hasaranga           2          48       +0.1184      +0.1173       -0.00107       0
6     7      7      7      Bhuvneshwar Kumar           7         132       +0.1065      +0.1040       -0.00254      -1
7     6      6      6      Abrar Ahmed                 0           0       +0.1058      +0.1058        0.00000      +1
8     8      8      8      Kuldeep Yadav               0           0       +0.1027      +0.1027        0.00000       0
9     9      9      9      Mahedi Hasan                0           0       +0.1025      +0.1025        0.00000       0
10    10     10     10     Mujeeb Ur Rahman            0           0       +0.1024      +0.1024        0.00000       0
------------------------------------------------------------------------------------------------------------------------
11    11     12     12     Mosaddek Hossain            0           0       +0.1000      +0.1000        0.00000      -1
12    12     13     13     Blessing Muzarabani         0           0       +0.0996      +0.0996        0.00000      -1
========================================================================================================================
```

![Figure 2: Bowling Rank Changes](outputs/comparisons/figures/fig02_bowling_rank_changes_1_20.png)

### 3.2 Key Bowling Dynamics:
1. **100% Top 10 Retention:**
   - Exactly the same 10 bowlers occupy the Top 10 across all multiplier regimes. Not a single bowler outside the Top 10 breaks in.
2. **The Bhuvneshwar / Abrar Internal Swap (#6 vs. #7):**
   - Bhuvneshwar Kumar bowled 132 balls across 7 playoff matches with slightly negative net situational value added in death overs. At $1.20\times$, his score drops by $-0.00254$ runs/ball (from $+0.1065$ to $+0.1040$).
   - Abrar Ahmed (0 knockout balls) stays at $+0.1058$, overtaking Bhuvneshwar for Rank 6.
3. **Josh Hazlewood's Gain:**
   - Hazlewood bowled 139 legal balls in playoffs with stellar economy, gaining $+0.00314$ runs saved/ball, consolidating his #4 spot and closing the gap on Sunil Narine (#3).

---

## 4. Largest Movers and Small-Sample Vulnerability Analysis

```
========================================================================================================================
Discipline  Player Name           Base Rank  1.20x Rank  Rank Change  KO Matches  KO Balls Faced/Bowled  Score Change
========================================================================================================================
Bowling     Mitchell Starc           203        186         +17            2                42             +0.01083
Bowling     Akash Madhwal            131        117         +14            2                45             +0.00845
Batting     Rahul Tripathi           239        228         +11            3                63             +0.00503
Bowling     Mohammed Siraj            61         72         -11            7               150             -0.00590
Bowling     Rasikh Salam             215        205         +10            2                42             +0.00604
Batting     Deepak Hooda             199        190          +9            2                39             +0.00409
Batting     Ayush Badoni             182        191          -9            1                 7             -0.00254
Batting     Venkatesh Iyer           133        125          +8            4                77             +0.00501
Batting     Faf du Plessis           114        122          -8            3                42             -0.00409
========================================================================================================================
```

![Figure 4: Exposure vs Rank Delta](outputs/comparisons/figures/fig04_knockout_exposure_vs_rank_delta.png)

### Critical Analytical Insights on Rank Volatility:
- **The Mitchell Starc Surge (+17 Ranks on 42 Balls):**
  Mitchell Starc's career dataset consists of 737 legal balls. In the 2024 playoffs, he bowled just 42 balls across Qualifier 1 and the Final, capturing two match-winning spells. Multiplying these 42 balls by $1.20\times$ causes Starc to leap **17 positions** (Rank 203 to 186).
- **The Ayush Badoni Drop (-9 Ranks on 7 Balls):**
  Ayush Badoni faced just 7 balls in a single playoff match, getting dismissed cheaply. Under $1.20\times$, this tiny 7-ball sample drops him **9 full ranks** across 297 batters.
- **Methodological Vulnerability:**
  This demonstrates that the knockout multiplier creates **high-leverage noise in small samples**. Regularization is intended to protect leaderboards from low-volume hot and cold streaks; adding a tournament-stage multiplier actively re-introduces small-sample distortion.

---

## 5. Sensitivity & Robustness Evaluation

```
========================================================================================================================
Multiplier Regime    Batting Spearman rho    Batting Top 10 Ret.    Bowling Spearman rho    Bowling Top 10 Ret.
========================================================================================================================
1.10x                     0.99990                   90.0%                0.99990                  100.0%
1.20x                     0.99975                   90.0%                0.99965                  100.0%
1.25x                     0.99963                   90.0%                0.99943                  100.0%
========================================================================================================================
```

![Figure 3: Sensitivity & Robustness](outputs/comparisons/figures/fig03_spearman_and_top10_retention.png)

1. **Near-Perfect Monotonic Stability:** Across all three versions, Spearman rank correlation remains above $0.9994$, confirming that the macro architecture is robust.
2. **Diminishing Returns:** Escalating the multiplier from $1.10\times$ to $1.25\times$ does not reveal new structural insights; it merely exaggerates the rank swings of players with small playoff samples (e.g., Starc climbs +10 at 1.10x, +17 at 1.20x, +19 at 1.25x).

---

## 6. Disentangling Exposure from Performance

A common pitfall in cricket analytics is confusing **team knockout qualification (exposure)** with **individual clutch capability (performance)**.

- **High Knockout Exposure Does NOT Guarantee Rank Gains:**
  - Mohammed Siraj played 7 playoff matches (150 balls), but because he conceded expensive boundaries in several high-pressure spells, the $1.20\times$ multiplier magnified his negative value, dropping him 11 ranks (61 $\to$ 72).
  - Travis Head played 4 playoff matches (39 balls), but two early dismissals reduced his score and pushed him from #8 to #10.
- **Genuine Performance vs. Exposure Multipliers:**
  Under the frozen baseline methodology, delivery pressure $P_i$ already evaluates the exact match situation (required run rate, wickets in hand, overs remaining). A final over requiring 15 runs has high pressure regardless of whether it occurs in an IPL league match, a T20 World Cup group match, or an IPL playoff. Adding an arbitrary multiplier on top of $P_i$ penalizes players whose teams were eliminated early, regardless of their individual clutch performance.

---

## 7. Final Recommendation & Conclusion

### Summary of Findings:
1. **The 1.20× Knockout Bonus does not improve the reliability methodology.** It creates isolated, volatile rank perturbations based on sample sizes as small as 7 to 45 deliveries.
2. **It introduces structural unfairness** against the 206 batters and 210 bowlers who did not play IPL knockouts, despite their excellence under pressure in league and international matches.
3. **The frozen Step 7.4 baseline rankings remain the most statistically defensible, objective, and unbiased evaluation of player reliability under pressure.**

**Action:** All experimental outputs remain strictly archived in `experiments/ipl_knockout_bonus_v1/`. The official frozen Step 7.4 rankings remain unmodified.

---

### Artifact Index

All experimental data, reports, and charts are saved and accessible:
- [experiment_report.md](file:///c:/Users/ASUS/Desktop/supeRR_selector - Copy/experiments/ipl_knockout_bonus_v1/reports/experiment_report.md)
- [methodology_notes.md](file:///c:/Users/ASUS/Desktop/supeRR_selector - Copy/experiments/ipl_knockout_bonus_v1/reports/methodology_notes.md)
- [validation_report.md](file:///c:/Users/ASUS/Desktop/supeRR_selector - Copy/experiments/ipl_knockout_bonus_v1/reports/validation_report.md)
- [batting_multipliers_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector - Copy/experiments/ipl_knockout_bonus_v1/outputs/comparisons/batting_multipliers_comparison.csv)
- [bowling_multipliers_comparison.csv](file:///c:/Users/ASUS/Desktop/supeRR_selector - Copy/experiments/ipl_knockout_bonus_v1/outputs/comparisons/bowling_multipliers_comparison.csv)
- [sensitivity_metrics.json](file:///c:/Users/ASUS/Desktop/supeRR_selector - Copy/experiments/ipl_knockout_bonus_v1/outputs/comparisons/sensitivity_metrics.json)
- [figures/](file:///c:/Users/ASUS/Desktop/supeRR_selector - Copy/experiments/ipl_knockout_bonus_v1/outputs/comparisons/figures/)
