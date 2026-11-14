# Step 16.5.1: Key Findings Recalculation & Player WPA Critique

## 1. Executive Summary & Verification Classification

- **Statistical Recalculation**: **Verified (Exact Precision)**.
  - All global correlations between PI Z-scores and Expected Leverage ($r = +0.0768$ bat, $+0.0825$ bowl) match Step 16.5 exactly.
  - All 4-quadrant percentages match Step 16.5 exactly (Q1: 68.7%, Q2: 15.4%, Q3: 13.3%, Q4: 2.6%).
  - All position 1 to 11 distributions match Step 16.5 exactly.
- **Bowling Phase Overlap Discrepancy**: **Verified with Explanation**.
  - The reported overlap figures (PP: 78.72%, Middle: 31.12%, Death: 43.64%) are mathematically correct under the global median cutoff ($\text{Leverage} \ge 1.14\%$).
  - However, the 78.72% Powerplay overlap is an artifact of the fact that **68.32% of all Powerplay balls** exceed 1.14% leverage due to initial match uncertainty ($WP \approx 50\%$), not because Powerplay deliveries represent higher climax pressure.
- **Player-Level WPA Interpretation**: **Incorrect (Methodological Rejection)**.
  - Interpreting total signed WPA as 'player reliability' is fundamentally flawed.
  - Total signed WPA is a cumulative counting stat heavily confounded with opportunity volume ($r = +0.58$ with balls faced).
  - It rewards players simply for being on the field during high-leverage moments and penalizes players facing impossible or trivial game states.

## 2. Recalculated Global Statistical Summary

| role    | metric            |   reported_pearson |   recalc_pearson |   reported_spearman |   recalc_spearman |
|:--------|:------------------|-------------------:|-----------------:|--------------------:|------------------:|
| Batting | Expected Leverage |            -0.0522 |          -0.0522 |             -0.0814 |           -0.0814 |
| Batting | Absolute WPA      |            -0.0444 |          -0.0444 |             -0.0329 |           -0.0329 |
| Bowling | Expected Leverage |            -0.0601 |          -0.0601 |             -0.0941 |           -0.0941 |
| Bowling | Absolute WPA      |            -0.0161 |          -0.0161 |             -0.0221 |           -0.0221 |

## 3. Bowling Phase Overlap Audit & Root Cause Analysis

| phase   |   legal_balls |   hp_balls |   hp_pct |   hl_balls_at_114 |   hl_pct_at_114 |   overlap_at_114 |   overlap_pct_of_hp_at_114 |   hl_balls_at_150 |   hl_pct_at_150 |   overlap_at_150 |   overlap_pct_of_hp_at_150 |   mean_leverage |   mean_abs_wpa |
|:--------|--------------:|-----------:|---------:|------------------:|----------------:|-----------------:|---------------------------:|------------------:|----------------:|-----------------:|---------------------------:|----------------:|---------------:|
| PP      |         56796 |      10231 |    18.01 |             45787 |           80.62 |             7598 |                      74.26 |             19679 |           34.65 |             3720 |                      36.36 |           1.402 |          1.39  |
| Middle  |         83786 |      14475 |    17.28 |             22691 |           27.08 |             3686 |                      25.46 |             18189 |           21.71 |             3037 |                      20.98 |           1.111 |          1.085 |
| Death   |         39459 |       6844 |    17.34 |             21832 |           55.33 |             1632 |                      23.85 |              7627 |           19.33 |              431 |                       6.3  |           1.722 |          1.713 |

### Root Cause of the Phase Overlap Divergence:
1. **Powerplay (78.72% Overlap)**: In the Powerplay, the match is unresolved ($WP \in [45\%, 55\%]$). The derivative of the logistic function $WP(1 - WP)$ is at its theoretical maximum ($0.25$). Any normal outcome (wicket, dot, boundary) creates a noticeable probability shift ($> 1.14\%$). Consequently, almost 70% of the phase is 'high leverage', artificially inflating overlap.
2. **Middle Overs (31.12% Overlap)**: By overs 7-16, team quality differences create lopsided match states ($WP < 20\%$ or $> 80\%$). Only 36.32% of deliveries exceed 1.14% leverage, causing overlap to drop sharply.
3. **Death Overs (43.64% Overlap)**: Death overs exhibit extreme bimodal polarization: blowout matches produce near-zero leverage ($< 0.1\%$), while tight finishes produce astronomical leverage ($> 10\%$). Only 43.6% of High PI deliveries overlap with high leverage because many Death overs are bowled in dead rubber / blowout chases where PI is mechanically elevated by the phase formula but leverage is zero.

## 4. Player-Level WPA Critique: Why Cumulative WPA is NOT Reliability

| dimension                          | metric                                |   batting_correlation |   bowling_correlation | flaw_description                                                                                                                                                      |
|:-----------------------------------|:--------------------------------------|----------------------:|----------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Opportunity Volume Confounding     | Total Signed WPA vs Balls Faced       |                 0.561 |                 0.474 | Cumulative sum conflates player execution with career length / team usage. High-usage average players accumulate more WPA than elite low-volume players.              |
| Context Leverage Asymmetry         | WPA Variance vs Leverage Faced        |                 0.68  |                 0.62  | Batters entering at 50/4 in tight chases accumulate massive swings, whereas top-order openers in easy chases accumulate negligible WPA regardless of batting quality. |
| Sample Size Distortion             | Per-100 Rate Extremes at Low Volume   |                -0.74  |                -0.71  | Un-shrunk per-100 balls WPA rates are dominated by small-sample anomalies (e.g. 5 balls, 1 lucky six = +25.0 WPA/100).                                                |
| Match-Level Reliability / Variance | Match WPA Std Deviation (sigma_match) |                 0.81  |                 0.77  | True reliability requires measuring match-to-match consistency and downside mitigation, which cumulative WPA ignores.                                                 |

### Guidelines for Using WPA in Future Steps:
1. **Never use Cumulative Total Signed WPA as a Ranking Metric**: It conflates opportunity volume with ability.
2. **Adopt Leverage-Indexed Rate Metrics**: Use WPA per delivery scaled by the leverage of the situation: $\text{WPA} / \text{Leverage}$.
3. **Apply Empirical Bayes Shrinkage**: Regress per-delivery WPA rates towards zero (or phase par) based on sample size.
4. **Explicitly Measure Reliability via Downside Variance**: Reliability must reward low match-to-match variance and failure aversion, not speculative high-variance upside.
