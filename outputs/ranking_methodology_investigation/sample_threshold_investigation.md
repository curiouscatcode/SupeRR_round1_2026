# Investigation 2 — Minimum Sample Threshold and Boundary Cliff Effects

**Investigation Date**: November 2026  
**Subject**: Evaluation of the 60-Ball Primary Qualification Cutoff  
**Baseline Dataset**: 816 Batters, 589 Bowlers  
**Artifacts Generated**:
- Analytical CSV: [`sample_threshold_analysis.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/ranking_methodology_investigation/sample_threshold_analysis.csv)
- Visual Analytics Figure: [`02_sample_threshold_distributions.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/ranking_methodology_investigation/02_sample_threshold_distributions.png)

---

## 1. Executive Summary & Core Findings

In the official v2.0 ranking model, a hard boundary of **60 high-pressure balls** defines Tier 1 qualification. Players with 40 to 59 balls are segregated into "Tier 2: Specialist," while players with <40 balls are classified as "Below Threshold."

Our deep empirical investigation of the entire player population establishes that:
1. **The 60-Ball Threshold Eliminates 85.8% of Batters and 80.8% of Bowlers**: Only **116 of 816 batters (14.2%)** and **113 of 589 bowlers (19.2%)** qualify for Tier 1.
2. **The "Arbitrary Cliff" Problem**: A hard cutoff of 60 creates severe binary boundary penalties. Players who fall 1 to 5 balls short are completely erased from official rankings, regardless of how extraordinary their Bayesian-shrunk reliability is.
3. **The Jamie Overton Paradox**: Jamie Overton faced **59 high-pressure balls** (exactly 1 ball below the cutoff) with a BRS of **79.54**. In Tier 2, he is ranked #2. If the cutoff were 50 balls, Overton would rank **#6 in the entire world**, displacing Patrick Cummins (#10, BRS 74.77) and George Dockrell (#9, BRS 75.38)!
4. **The Nasum Ahmed Paradox**: Nasum Ahmed delivered **55 high-pressure legal balls** with a BoRS of **88.84**. In Tier 2, he is ranked #1. If the cutoff were 50 balls, Nasum Ahmed would rank **#2 in the entire world**, ahead of Keshav Maharaj (BoRS 79.94) and Haris Rauf (BoRS 78.84), trailing only Tim Southee (BoRS 90.69)!
5. **Double Penalty with Bayesian Shrinkage**: Because the model already applies Bayesian shrinkage ($K=50$), small samples are already penalised mathematically (at $N=59$, 45.9% of the score is shrunk toward the average population prior). Imposing a hard exclusion cliff at 60 balls constitutes a **double penalty** that discards high-confidence performers.

---

## 2. Population Qualification Across Sample Thresholds

| High-Pressure Ball Threshold | Qualifying Batters | % of Batters ($N=816$) | Qualifying Bowlers | % of Bowlers ($N=589$) |
|:---:|:---:|:---:|:---:|:---:|
| **$\ge 10$ balls** | 338 | 41.42% | 291 | 49.41% |
| **$\ge 20$ balls** | 247 | 30.27% | 224 | 38.03% |
| **$\ge 30$ balls** | 192 | 23.53% | 182 | 30.90% |
| **$\ge 40$ balls (Tier 2 Floor)** | 151 | 18.50% | 149 | 25.30% |
| **$\ge 50$ balls** | 134 | 16.42% | 129 | 21.90% |
| **$\ge 60$ balls (Official Tier 1)** | **116** | **14.22%** | **113** | **19.19%** |
| **$\ge 70$ balls** | 98 | 12.01% | 100 | 16.98% |
| **$\ge 80$ balls** | 87 | 10.66% | 88 | 14.94% |
| **$\ge 100$ balls** | 68 | 8.33% | 71 | 12.05% |
| **$\ge 150$ balls** | 32 | 3.92% | 40 | 6.79% |
| **$\ge 200$ balls** | 13 | 1.59% | 23 | 3.90% |

---

## 3. Detailed Case Studies of Boundary Casualties

### Case 1: Jamie Overton (59 Balls Faced)
- **High-Pressure Balls Faced**: 59 balls (1 ball short of 60).
- **Observed Metrics**: 109 runs, strike rate 184.75, 1 dismissal (survival rate 98.31%), 11 boundaries (18.64%), 15 dot balls (25.42%).
- **Bayesian Adjustment**: $K=50$ shrinks his observed metrics, incorporating 45.9% population prior.
- **Component Scores**: $S_{\text{sr}} = 86.82$, $S_{\text{surv}} = 92.11$, $S_{\text{exec}} = 65.41$, $S_{\text{diff}} = 65.23$.
- **Final BRS**: **79.54**.
- **Impact**: In Tier 1, a BRS of 79.54 places him **#6 in the world**, ahead of Vijay Shankar (#6, 78.02) and Jitesh Sharma (#7, 77.01). Instead, a single missing delivery locks him out into Tier 2.

### Case 2: Nasum Ahmed (55 Legal Balls Bowled)
- **High-Pressure Legal Balls**: 55 balls (5 balls short of 60).
- **Observed Metrics**: 49 runs conceded (economy 5.35 rpo), 6 wickets (strike rate 10.91%), 32 dot balls (58.18%).
- **Bayesian Adjustment**: $K=50$ shrinks economy from 5.35 to 7.11 rpo and wickets from 10.91% to 8.14%.
- **Component Scores**: $S_{\text{econ}} = 81.44$, $S_{\text{wk}} = 88.58$, $S_{\text{dot}} = 97.28$, $S_{\text{diff}} = 95.12$.
- **Final BoRS**: **88.84**.
- **Impact**: In Tier 1, BoRS 88.84 places him **#2 in the world**, behind only Tim Southee (90.69). Because of a 5-ball shortfall, he is excluded from the official rankings.

### Case 3: The Beneficiaries of the Cliff
Conversely, several bowlers who barely scraped past the 60-ball boundary gained entry and immediately dominated the official Top 10:
- **Simarjeet Singh**: Exactly **60 legal balls** $\rightarrow$ BoRS 69.40 $\rightarrow$ **Rank #9 in Tier 1**.
- **Shoriful Islam**: Exactly **61 legal balls** $\rightarrow$ BoRS 74.01 $\rightarrow$ **Rank #5 in Tier 1**.
- **Tim Southee**: Exactly **64 legal balls** $\rightarrow$ BoRS 90.69 $\rightarrow$ **Rank #1 in Tier 1**.

If Simarjeet Singh had bowled 1 fewer high-pressure delivery, he would be unranked in Tier 2. If Nasum Ahmed had bowled 5 more, he would be #2 in Tier 1.

---

## 4. Ranking Stability at Alternative Cutoffs

| Simulated Threshold | Batter Tier 1 Count | Top 10 Overlap with v2.0 | Bowler Tier 1 Count | Top 10 Overlap with v2.0 | Key Observations |
|:---:|:---:|:---:|:---:|:---:|:---|
| **Cutoff = 40 balls** | 151 (+35) | 7 / 10 | 149 (+36) | 7 / 10 | Admits Jamie Overton (#6) and Nasum Ahmed (#2). |
| **Cutoff = 50 balls** | 134 (+18) | 9 / 10 | 129 (+16) | 8 / 10 | Overton enters at #6; Nasum enters at #2. |
| **Cutoff = 60 balls (v2.0)** | **116 (Baseline)** | **10 / 10** | **113 (Baseline)** | **10 / 10** | **Official Baseline**. |
| **Cutoff = 75 balls** | 93 (-23) | 7 / 10 | 94 (-19) | 7 / 10 | Southee (#1, 64 b), Shoriful (#5, 61 b), Simarjeet (#9, 60 b), Dubey (#4, 69 b), Shankar (#6, 65 b) dropped. |
| **Cutoff = 100 balls** | 68 (-48) | 4 / 10 | 71 (-42) | 5 / 10 | 6 of the Top 10 batters and 5 of the Top 10 bowlers are disqualified! |

---

## 5. Answers to Investigation 2 Questions

### Q1: Is 60 balls a defensible threshold or an arbitrary cliff?
**Answer**: It is **partially defensible practically, but functions as an arbitrary statistical cliff**.
- **Cricketing defense**: 60 balls represents 10 complete overs in T20 cricket. Across high-pressure situations (which comprise ~19% of deliveries), facing 60 high-pressure balls requires ~15-20 matches. This filters out transient performers.
- **Statistical critique**: A hard step-function at 60 is arbitrary when combined with Bayesian shrinkage. Bayesian shrinkage with $K=50$ is continuous: a player at $N=59$ is already 45.9% shrunk toward the prior, while a player at $N=60$ is 45.5% shrunk. Treating $N=59$ as "unqualified" and $N=60$ as "fully qualified" produces severe boundary discontinuity.

### Q2: What is the impact on players just below and above 60?
**Answer**: Extreme rank distortion. Jamie Overton (59 balls, BRS 79.54) and Nasum Ahmed (55 balls, BoRS 88.84) are world-class performers locked out of Tier 1, while Simarjeet Singh (60 balls) and Shoriful Islam (61 balls) make the Top 10.

### Q3: How should this be resolved in a future v3.0 release?
**Answer**: Eliminate hard tier exclusions in favor of a **Continuous Reliability Confidence Weighting (RCW)**:
$$\text{Final Score} = \text{Score}^* \times \left(1 - e^{-N / N_0}\right)$$
or publish a unified ranking table where sample confidence intervals are reported alongside point estimates, allowing players like Overton and Nasum to be evaluated transparently.
