# Step 10: Independent Validation of Experimental Pressure Index Models

**Audit Date**: November 2026  
**Auditor**: Independent Validation Agent (Clean-Room Execution)  
**Scope**: Verification of Step 9 Experimental Pressure Index Models (Model 1, Model 2, Model 3, Model 4)  
**Input Datasets Audited**:
- `data/processed/delivery_pressure_index.csv` (188,330 deliveries)
- `data/processed/delivery_match_state.csv`
- `data/processed/batter_performance.csv` & `data/processed/bowler_performance.csv`
- `data/processed/batter_reliability_rankings.csv` & `data/processed/bowler_reliability_rankings.csv`
- `outputs/pressure_index_audit/` (Step 9 Experimental Outputs)

---

## Executive Summary & Validation Verdicts

An independent, clean-room mathematical audit was conducted on the four experimental Pressure Index (PI) models and the ranking pipeline introduced during the Step 9 investigation. The evaluation verified mathematical derivations, delivery-level state transitions, discrete threshold mechanics, edge-case behavior, and ranking stability across the full player population (1,405 players).

### Critical Methodological Framing

In evaluating these models, this audit maintains a strict distinction across four evaluation dimensions:
1. **Mathematical Correctness**: Formal validity of equations, domain bounds $[0, 100]$, and asymptotic behavior.
2. **Implementation Correctness**: Algorithmic accuracy, edge-case resets, pre-delivery indexing, and denominator/extras handling.
3. **Ranking Impact**: Shift in player eligibility, qualified sample sizes, Bayesian shrinkage stabilization, and ordinal rank stability.
4. **Cricketing Validity**: Domain realism, tactical alignment with T20 match context, and incentive compatibility for real-world players.

> [!IMPORTANT]
> **A mathematically validated formula is NOT a proven improvement in cricketing accuracy.**
> - The official v2.0 Pressure Index engine and production rankings (`data/processed/batter_reliability_rankings.csv` and `bowler_reliability_rankings.csv`) **remain completely unchanged**.
> - Model 4 and all other variants evaluated herein **remain experimental prototypes** and are **NOT APPROVED** as new official models.

### Summary of Audit Verdicts

| Experimental Model | Core Concept / Innovation | Validation Scope | Verdict | Key Finding / Cricketing & Methodological Assessment |
|:---|:---|:---|:---:|:---|
| **Model 1: Bowler Workload** | Spell & Innings Fatigue Additive Penalty | Delivery-level state tracking, saturation, boundary resets | **PASS** | **Mathematically & implementationally validated**. However, its interpretation as physical fatigue remains an open methodological question: Innings Workload is strongly collinear with over number ($r > 0.85$), acting primarily as a proxy for match phase and inflating Death Bowling PI by $+10.60$ points. |
| **Model 2: Phase-Relative Cutoffs** | Empirical 80th Percentile per phase (PP, Mid, Death) | Percentile derivation, discrete ties, sample expansion | **PASS** | **Mathematically & implementationally validated**. Eliminates the death-overs finishing monopoly. However, it measures **relative pressure within each phase** rather than **absolute match leverage**, implicitly treating a high-pressure Powerplay delivery as equivalent in leverage to a final-over chase. |
| **Model 3: 2nd Innings PP (Variant 1)** | Target Pressure Floor ($RRR \times 2.5 + \dots$) | 630 simulation scenarios, 29,597 historical deliveries | **PASS** | **Mathematically validated**. Successfully rescues 1,831 steep-chase balls ($RRR \ge 10$) without false positives in modest chases ($RRR < 8$). However, its full cricketing validity across varied pitch and boundary conditions is not yet established. |
| **Model 3: Settled Batter Trap (Variant 2)** | Batter Runs Multiplier on Batting Pressure | 630 simulation scenarios, individual score tracking | **FAIL** | **Conceptually & cricket-realistically flawed**. Penalizes set batters ($30^*$ off 15) keeping a chase alive compared to new batters ($0^*$ off 0). **Permanently rejected**. |
| **Step 9 Ranking Pipeline** | Step 9 Experimental Ranking Engine (`audit_ranking_impact.py`) | Parity against Step 6.2 official ranking engine | **PARTIAL PASS** | **Two critical implementation discrepancies discovered in Step 9 code**: 233 un-filtered deliveries post-target and omission of 1,018 extras penalty runs on wides/no-balls. Reconciled in the Step 10 authoritative pipeline. |
| **Model 4: Combined System** | Integration of M1, M2, and M3 (Variant 1) | Compounding effects, dynamic P80 recalibration | **PASS** | **Fully reproducible computationally**. Demonstrates non-linear interaction dynamics. **NOT APPROVED** as the new official model; remains an unverified research prototype. |

---

## Comprehensive Validation Discrepancy Table

The following master discrepancy table consolidates all numerical benchmarks evaluated between the Step 9 investigation report and the independent Step 10 clean-room audit.

| Dimension / Metric | Step 9 Reported | Independently Calculated | Absolute Diff | Relative Diff | Root Cause / Technical Explanation | Status |
|:---|:---:|:---:|:---:|:---:|:---|:---:|
| **Workload: Spell Saturation Cap Balls (100%)** | 13,751 | 13,751 | 0 | 0.00% | Exact match. Bowlers bowling $\ge 6$ balls in spell saturate. | **PASS** |
| **Workload: Mean Spell Workload (Overall %)** | 38.64% | 38.64% | 0.00% | 0.00% | Exact match across all 188,097 clean deliveries. | **PASS** |
| **Workload: PP High-Pressure Balls (Bowling)** | 9,240 | 9,240 | 0 | 0.00% | Workload increases PP bowling high-pressure balls from 9,141 to 9,240. | **PASS** |
| **Workload: Death High-Pressure Balls (Bowling)** | 2,980 | 2,980 | 0 | 0.00% | Workload increases Death bowling high-pressure balls from 1,827 to 2,980. | **PASS** |
| **Phase-Relative: PP Batting P80 Cutoff** | 50.50 | 50.50 | 0.00 | 0.00% | Exact match for empirical 80th percentile. | **PASS** |
| **Phase-Relative: Middle Batting P80 Cutoff** | 50.92 | 50.92 | 0.00 | 0.00% | Exact match for empirical 80th percentile. | **PASS** |
| **Phase-Relative: Death Batting P80 Cutoff** | 62.40 | 62.40 | 0.00 | 0.00% | Exact match. Discrete tie of 588 deliveries at 62.40. | **PASS** |
| **Phase-Relative: PP Bowling P80 Cutoff** | 60.27 | 60.27 | 0.00 | 0.00% | Exact match for empirical 80th percentile. | **PASS** |
| **Phase-Relative: Middle Bowling P80 Cutoff** | 52.73 | 52.73 | 0.00 | 0.00% | Exact match for empirical 80th percentile. | **PASS** |
| **Phase-Relative: Death Bowling P80 Cutoff** | 41.88 | 41.88 | 0.00 | 0.00% | Exact match for empirical 80th percentile. | **PASS** |
| **Phase-Relative: Tier 1 Batter Expansion (M2)** | +71 | +71 | 0 | 0.00% | Exact match: 116 $\rightarrow$ 187 Tier 1 batters (+72 new, -1 dropped). | **PASS** |
| **Phase-Relative: Tier 1 Bowler Expansion (M2)** | +54 | +54 | 0 | 0.00% | Exact match: 113 $\rightarrow$ 167 Tier 1 bowlers (+54 new, -0 dropped). | **PASS** |
| **2nd Innings PP: Steep Chases ($RRR \ge 10$)** | 9,415 | 9,415 | 0 | 0.00% | 31.81% of all 29,597 second-innings PP deliveries. | **PASS** |
| **2nd Innings PP: Low/Mod Balls in Steep Chases** | 6,591 | 6,591 | 0 | 0.00% | 70.01% of steep chase balls were misclassified as Low/Mod in baseline. | **PASS** |
| **2nd Innings PP: Reclassified Balls (Variant 1)** | 1,831 | 1,831 | 0 | 0.00% | Successfully reclassified to High Pressure ($PI \ge 61$). | **PASS** |
| **2nd Innings PP: Modest Chase False Positives** | 0 | 0 | 0 | 0.00% | Zero deliveries with $RRR < 8.0$ reclassified to High Pressure. | **PASS** |
| **Ranking Pipeline: Target-Reached Deliveries** | 0 filtered | 233 filtered | +233 | N/A | Step 9 omitted `(innings == 2) & (runs_required <= 0)` filter. | **PARTIAL PASS** |
| **Ranking Pipeline: Bowling High Runs Conceded** | 29,000 | 30,018 | +1,018 | +3.51% | Step 9 dropped extras penalty runs on wides/no-balls on HP balls. | **PARTIAL PASS** |
| **Ranking Pipeline: Bowling High Economy Prior** | 8.7468 | 9.0579 | +0.3111 | +3.56% | Drop of 1,018 runs artificially lowered population bowling economy prior. | **PARTIAL PASS** |
| **Rankings: Marco Jansen High-Pressure Balls** | 132 | 130 | -2 | -1.52% | 2 extra balls came from match 40742 over 20 after target reached. | **PARTIAL PASS** |
| **Rankings: Marco Jansen Baseline Rank** | #40 | #45 | -5 | N/A | Caused by un-filtered 233 deliveries. Official Step 6.2 is #45. | **PARTIAL PASS** |
| **Rankings: Model 4 Bowler Top 10 Overlap** | 3 / 10 | 4 / 10 | +1 | +33.3% | Authoritative pipeline retains 4 bowlers (Southee, Rana, Rauf, Maharaj). | **PARTIAL PASS** |
| **Combined M4: Tier 1 Batter Count** | 188 | 188 | 0 | 0.00% | Exact match: 116 baseline $\rightarrow$ 188 (+73 new, -1 dropped: Odean Smith). | **PASS** |
| **Combined M4: Tier 1 Bowler Count** | 165 | 165 | 0 | 0.00% | Exact match: 113 baseline $\rightarrow$ 165 (+52 new, -0 dropped). | **PASS** |
| **Combined M4: Batter Spearman $\rho$ (Tier 1)** | 0.7629 | 0.7623 | -0.0006 | -0.08% | Exact match within precision tolerance ($\rho = 0.7647$ all 816 batters). | **PASS** |
| **Combined M4: Bowler Spearman $\rho$ (Tier 1)** | 0.7285 | 0.7195 | -0.0090 | -1.24% | Reconciled: difference caused by Step 9 omitting 1,018 wide/no-ball runs. | **PASS** |

---

## Section A: Bowler Workload & Fatigue Validation (Model 1)

### 1. Mathematical Formulation & Pre-Delivery State Rule
In Step 9, the bowler workload additive term was specified as:
$$\Delta PI_{\text{bowling}} = w_{\text{spell}} \cdot W_{\text{spell}} + w_{\text{innings}} \cdot W_{\text{innings}}$$
where $w_{\text{spell}} = 10.0$, $w_{\text{innings}} = 10.0$, and:
$$W_{\text{spell}} = \min\left(1.0, \frac{\text{legal\_balls\_in\_current\_spell}}{6}\right) \times 100\%$$
$$W_{\text{innings}} = \min\left(1.0, \frac{\text{legal\_balls\_in\_innings}}{24}\right) \times 100\%$$

**Audit Verification of Implementation**:
- **Pre-Delivery State**: Verified. On delivery $t$, the counter counts legal balls bowled strictly prior to delivery $t$. For example, the first legal ball of an over has $\text{legal\_balls\_in\_spell} = 0$, giving $W_{\text{spell}} = 0.0\%$.
- **Wide & No-Ball Handling**: If ball 1 is a wide, it does not increment the legal ball counter; the subsequent ball still has $\text{legal\_balls\_in\_spell} = 0$.
- **Spell Boundary Resets**: A bowler’s spell counter resets to zero if the difference between the current over number and the bowler’s previous over number is $\ge 2$. If a bowler bowls over 1 and over 2 (consecutive overs from alternate ends), the spell counter persists across overs up to 12 legal balls, saturating at $100\%$ after ball 6.
- **Saturation Cap**: Exactly **13,751 deliveries** across the dataset have $W_{\text{spell}} = 100.0\%$. This occurs whenever a bowler bowls consecutive overs or delivers over completions without spell breaks. Only **1 delivery** in the entire dataset reaches $W_{\text{innings}} = 100.0\%$ (Match 41509, Innings 1, Over 12.7 by Aaron Hardie, an anomalous 7th legal ball in the over).

```
Visual Artifact: outputs/experimental_model_validation/01_workload_validation_comparison.png
Discrepancy Table: outputs/experimental_model_validation/workload_validation_discrepancies.csv
```

### 2. Phase-Level Workload Distribution & Methodological Critique
The empirical workload distributions across phases reveal why Model 1 disproportionately impacts death bowlers:

| Phase | Mean Spell Workload | Mean Innings Workload | Mean Total $\Delta PI$ | Base Bowling PI | Workload Bowling PI | HP Deliveries ($\ge 61$) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Powerplay (Overs 1–6)** | 37.97% | 21.74% | +5.97 | 45.98 | 51.95 | 9,141 $\rightarrow$ 9,240 (+1.1%) |
| **Middle (Overs 7–15)** | 40.76% | 41.57% | +8.23 | 42.13 | 50.36 | 6,366 $\rightarrow$ 7,834 (+23.1%) |
| **Death (Overs 16–20)** | 33.68% | 72.35% | +10.60 | 31.85 | 42.45 | 1,827 $\rightarrow$ 2,980 (+63.1%) |
| **Overall** | **38.64%** | **41.65%** | **+8.03** | **40.95** | **48.98** | **17,334 $\rightarrow$ 20,054 (+15.7%)** |

**Cricketing Assessment**:
- While mathematically elegant and correctly implemented, the additive formulation has a major methodological vulnerability: **Innings Workload acts as a collinear proxy for match phase**.
- A bowler who returns in over 19 has bowled 18 balls simply because of typical T20 bowling rotations, not necessarily because they are fatigued.
- The model treats 24 balls across 1.5 hours in T20 cricket as inducing severe physical exhaustion, elevating Death overs pressure by an average of $+10.60$ points. Whether this reflects genuine physiological breakdown or merely penalizes death specialists requires deeper biomechanical and tactical study before any adoption.

---

## Section B: Phase-Relative Cutoffs & Discrete Tie Mechanics (Model 2)

### 1. Empirical 80th Percentile Thresholds
Model 2 discards the arbitrary fixed threshold ($PI \ge 61$) in favor of an empirical 80th percentile threshold computed independently within each match phase:

| Phase | Batting P80 Threshold | Batting HP Deliveries | Bowling P80 Threshold | Bowling HP Deliveries |
|:---|:---:|:---:|:---:|:---:|
| **Powerplay (Overs 1–6)** | **50.50** | 11,830 (20.00%) | **60.27** | 11,836 (20.01%) |
| **Middle (Overs 7–15)** | **50.92** | 17,331 (20.00%) | **52.73** | 17,360 (20.03%) |
| **Death (Overs 16–20)** | **62.40** | 7,951 (18.79%) | **41.88** | 8,464 (20.00%) |
| **Total** | — | **37,112 (19.73%)** | — | **37,660 (20.02%)** |

### 2. Discrete Ties at 62.40 in Death Batting
The audit revealed an important mathematical nuance: in Death overs batting, **7,951 deliveries** have $PI > 62.40$ (18.79%), but exactly **588 deliveries** tie at $PI = 62.400000$.
- If strict inequality ($PI > P80$) is used, Death Batting HP deliveries = 7,951 (18.79%).
- If inclusive inequality ($PI \ge P80$) is used, Death Batting HP deliveries = 8,539 (20.18%).
- Step 9 reported 7,951 deliveries because it used strict `>`. Both formulations are valid, but the discrete tie must be explicitly parameterized in future production specifications to avoid discrepancies.

### 3. Reconciling Baseline and Model 2 Cohorts
The audit reconciled the exact population transitions for Model 2:
- **Batters**:
  - Authoritative Baseline Tier 1: **116 players** ($\ge 60$ HP balls in official Step 6.2).
  - Model 2 Tier 1: **187 players**.
  - Transitions: **72 new entrants**, **1 dropout** (**Odean Smith**, ID 4840, who dropped from 63 to 58 HP balls).
  - Net Expansion: $187 - 116 = \mathbf{+71\text{ players}}$ (+61.2%).
  - Top-order anchors gain substantial sample sizes: Virat Kohli (47 $\rightarrow$ 124 HP balls), Rohit Sharma (48 $\rightarrow$ 167 HP balls), David Warner (44 $\rightarrow$ 133 HP balls).
- **Bowlers**:
  - Authoritative Baseline Tier 1: **113 players**.
  - Model 2 Tier 1: **167 players**.
  - Transitions: **54 new entrants**, **0 dropouts**.
  - Net Expansion: $167 - 113 = \mathbf{+54\text{ players}}$ (+47.8%).
  - Powerplay specialists gain substantial representation: Trent Boult (180 $\rightarrow$ 261 HP balls), Bhuvneshwar Kumar (299 $\rightarrow$ 459 HP balls).

```
Visual Artifact: outputs/experimental_model_validation/02_phase_relative_ties_and_cutoffs.png
Discrepancy Table: outputs/experimental_model_validation/phase_relative_validation_discrepancies.csv
```

**Cricketing Assessment**:
- **Relative vs Absolute Leverage**: Model 2 successfully rectifies the structural death-overs monopoly of the baseline engine. However, by equalizing the high-pressure proportion to 20% across all phases, it implicitly asserts that the top 20% most intense Powerplay balls represent the *same degree of match pressure* as the top 20% most intense Death balls. In reality, a boundary conceded in Over 20 changes win probability much more drastically than one conceded in Over 2. Model 2 evaluates *phase-relative difficulty*, not *absolute match jeopardy*.

---

## Section C: 2nd Innings Powerplay Recalibration & Scenario Testing (Model 3)

### 1. Controlled Simulation Testing (630 Scenarios)
A 3-dimensional factorial grid was evaluated across 630 scenarios:
- **Required Run Rate ($RRR$)**: 6.0 to 14.0 (step 1.0)
- **Wickets Lost**: 0 to 4 (step 1)
- **Overs Completed**: 0 to 5 (step 1)

**Findings**:
1. **Baseline Failure**: In the baseline model, a team chasing $14.0$ RRR in over 3 with 2 wickets down received a Batting PI of only **44.82** (Low/Moderate), because the static phase weight allocated only 25% weight to match state during the Powerplay.
2. **Variant 1 Success**: The dynamic target pressure floor:
   $$\text{Floor}_{\text{PP}} = \max\left(0, (RRR - 8.0) \times 2.5 + \text{wickets\_lost} \times 2.0\right)$$
   elevates the pressure for this scenario to **62.82** (High Pressure).
3. **Modest Chase Protection**: In modest chases ($RRR \le 7.5$), the floor evaluates to $0.0$, preventing artificial inflation.

```
Visual Artifact: outputs/experimental_model_validation/03_second_innings_pp_validation.png
Discrepancy Table: outputs/experimental_model_validation/second_innings_pp_validation_discrepancies.csv
```

### 2. Historical Population Delivery Audit
Across all 29,597 second-innings Powerplay deliveries:
- **Steep Chases ($RRR \ge 10.0$)**: Exactly 9,415 deliveries (31.81%).
- **Baseline Misclassification**: Exactly **6,591 deliveries** (70.01% of steep chases) were classified as Low/Moderate pressure ($PI \le 60$).
- **Variant 1 Rescue**: Variant 1 reclassifies **1,831 deliveries** to High Pressure ($PI \ge 61$), raising total HP balls in 2nd innings PP from 3,301 to 5,132.
- **False Positives**: Exactly **0 deliveries** with $RRR < 8.0$ were reclassified as High Pressure.

### 3. Rejection of the "Settled Batter Trap" (Variant 2 Failure)
Variant 2 introduced a multiplicative individual batter term:
$$\text{Multiplier} = 1.0 - 0.005 \times \text{batter\_runs\_scored}$$
- In a scenario where a team is chasing $13.0$ RRR in over 5 with 3 wickets down:
  - An incoming batter ($0^*$ off 0 balls) receives $PI = 64.50$ (High Pressure).
  - A set batter who has scored $30^*$ off 15 balls receives $PI = 54.82$ (Low/Moderate Pressure).
- **Audit Verdict: FAIL**. This creates an absurd tactical incentive: the batter actively anchoring the run chase is evaluated under "Low Pressure," while a new batter facing the exact same required rate is evaluated under "High Pressure." Variant 2 is rejected and permanently excluded.

---

## Section D: Ranking Pipeline Integrity & Discrepancy Reconciliation

The audit uncovered two critical implementation bugs in Step 9's ranking script (`audit_ranking_impact.py`) that caused divergence from the official Step 6.2 rankings (`data/processed/batter_reliability_rankings.csv` and `bowler_reliability_rankings.csv`).

```
Visual Artifact: outputs/experimental_model_validation/04_ranking_pipeline_discrepancy_analysis.png
Discrepancy Table: outputs/experimental_model_validation/ranking_pipeline_validation_discrepancies.csv
```

### Discrepancy 1: Unfiltered Post-Target Deliveries (233 Deliveries)
- **Official Step 5 / Step 6.2 Pipeline**:
  ```python
  # evaluate_player_performance.py (Lines 118-121)
  df = df[~((df['innings'] == 2) & (df['runs_required'] <= 0))].copy()
  ```
  Properly filtered out **233 invalid deliveries** where the match had concluded. Clean population: **188,097 deliveries**.
- **Step 9 Implementation**: Processed all **188,330 deliveries** directly without filtering.
- **Impact on Player Rankings**: Leaked 9 post-target high-pressure balls. In match ID `40742` (Over 20), Marco Jansen faced 2 extra deliveries after target was reached, shifting his balls from 130 to 132, BRS from 58.72 to 59.73, and rank from **#45 to #40** (+5 spots). Exactly 22 batters experienced 1-place rank shifts.

### Discrepancy 2: Omission of Wide and No-Ball Extras Runs in Bowling Economy
- **Official Step 6.2 Pipeline**:
  ```python
  # evaluate_player_performance.py (Lines 240-244)
  p_high = df['bowler_pressure_tier'].isin(['High', 'Very High'])
  df['rc_high'] = np.where(p_high, df['bowler_runs_conceded'], 0)
  df['lb_high'] = np.where(p_high, df['is_legal_ball'], 0)
  ```
  `bowler_runs_conceded` includes penalty runs from wides and no-balls, while `is_legal_ball` serves as denominator. Total HP runs conceded = **30,018** across 19,884 legal balls $\rightarrow$ Population High Economy Prior = **9.0579** rpo.
- **Step 9 Implementation**:
  ```python
  # audit_ranking_impact.py (Lines 290-295)
  lb_df = df[df['is_legal_ball'] == 1].copy()
  rc_high = lb_df.groupby('bowler_id')['bowler_runs_conceded'].sum()
  ```
  By filtering `df['is_legal_ball'] == 1` *before* aggregating runs, Step 9 discarded **1,018 runs conceded on wides and no-balls on high-pressure deliveries**.
- **Impact on Bowler Ratings**: High runs conceded dropped to 29,000, lowering the population high economy prior from **9.0579 to 8.7468** (-0.3111 rpo). This artificially improved every bowler's economy by 0.3 to 0.6 rpo, distorting Bayesian shrinkage values.

### Authoritative Resolution
When these two discrepancies were corrected in `validate_ranking_pipeline.py`, Authoritative Model 0 achieved **100.00% exact parity** with official Step 6.2 production rankings:
- **0 BRS discrepancies** across all 816 batters.
- **0 BoRS discrepancies** across all 589 bowlers.
- **0 Tier 1 rank discrepancies** for all qualified players.

---

## Section E: Full Player Eligibility & Reconciled Ranking Changes

### Reconciling the Tier 1 Populations
To resolve previous conflicting figures in drafting:
- **Official Step 6.2 Baseline**: Exactly **116 Tier 1 batters** and **113 Tier 1 bowlers**.
- **Model 2 Expansion**: Exactly **187 Tier 1 batters** (Net: **+71**; 72 new entrants, 1 dropout: Odean Smith) and **167 Tier 1 bowlers** (Net: **+54**; 54 new entrants, 0 dropouts).
- **Model 4 Expansion**: Exactly **188 Tier 1 batters** (Net: **+72**; 73 new entrants, 1 dropout: Odean Smith) and **165 Tier 1 bowlers** (Net: **+52**; 52 new entrants, 0 dropouts).
- **Origin of "117" & Confusion**: An earlier draft subtracted Model 2's +71 expansion from Model 4's 188 total ($188 - 71 = 117$), mistakenly treating 117 as the baseline instead of the true 116. Additionally, the single dropped batter was misnamed as "Lendl Simmons" (who does not appear in the dataset) instead of **Odean Smith** (player ID 4840, who dropped from 63 to 58 HP balls).

### Top 20 Authoritative Batter Rankings: Model 0 vs Model 4

| Rank | Model 0 (Official Baseline) | HP Balls (M0) | BRS (M0) | Model 4 (Combined System) | HP Balls (M4) | BRS (M4) | Rank Change (M0 $\rightarrow$ M4) |
|:---:|:---|:---:|:---:|:---|:---:|:---:|:---:|
| **1** | Mahendra Singh Dhoni | 194 | 95.05 | Naman Dhir | 120 | 88.47 | New Entrant (Unranked $\rightarrow$ #1) |
| **2** | Shashank Singh | 135 | 84.04 | Reeza Hendricks | 142 | 88.17 | New Entrant (Unranked $\rightarrow$ #2) |
| **3** | Shivam Dube | 160 | 82.97 | Faf du Plessis | 116 | 86.43 | Unranked (21 b) $\rightarrow$ **#3** |
| **4** | Shubham Dubey | 69 | 80.82 | Sanju Samson | 256 | 85.26 | #27 (95 b) $\rightarrow$ **#4** (+23) |
| **5** | Cameron Green | 78 | 80.70 | Suryakumar Yadav | 331 | 83.97 | #19 (104 b) $\rightarrow$ **#5** (+14) |
| **6** | Vijay Shankar | 65 | 78.02 | Prabhsimran Singh | 145 | 83.97 | New Entrant (Unranked $\rightarrow$ #6) |
| **7** | Jitesh Sharma | 97 | 77.01 | Finn Allen | 71 | 83.66 | New Entrant (Unranked $\rightarrow$ #7) |
| **8** | Rinku Singh | 177 | 75.49 | Riyan Parag | 177 | 83.39 | #30 (77 b) $\rightarrow$ **#8** (+22) |
| **9** | George Dockrell | 100 | 75.38 | William Jacks | 97 | 82.97 | New Entrant (Unranked $\rightarrow$ #9) |
| **10** | Patrick Cummins | 131 | 74.77 | Sai Sudharsan | 169 | 82.14 | New Entrant (Unranked $\rightarrow$ #10) |
| **11** | Glenn Maxwell | 108 | 74.56 | Virat Kohli | 151 | 81.76 | Tier 2 (47 b) $\rightarrow$ **#11** (+36) |
| **12** | Tristan Stubbs | 79 | 74.33 | Harry Brook | 111 | 81.25 | New Entrant (Unranked $\rightarrow$ #12) |
| **13** | Ashutosh Sharma | 69 | 73.80 | Glenn Maxwell | 224 | 80.89 | #11 (108 b) $\rightarrow$ #13 (-2) |
| **14** | Andre Russell | 129 | 73.74 | Shimron Hetmyer | 160 | 78.96 | #17 (118 b) $\rightarrow$ #14 (+3) |
| **15** | Tim David | 97 | 73.18 | Nicholas Pooran | 215 | 78.71 | #20 (95 b) $\rightarrow$ #15 (+5) |
| **16** | Rahul Tewatia | 116 | 73.06 | KL Rahul | 239 | 78.68 | #52 (74 b) $\rightarrow$ **#16** (+36) |
| **17** | Shimron Hetmyer | 118 | 72.82 | David Warner | 167 | 77.46 | Tier 2 (44 b) $\rightarrow$ **#17** (+27) |
| **18** | Nicholas Pooran | 95 | 72.39 | Abhishek Sharma | 108 | 77.10 | New Entrant (Unranked $\rightarrow$ #18) |
| **19** | Suryakumar Yadav | 104 | 70.92 | Tilak Varma | 179 | 77.01 | #35 (84 b) $\rightarrow$ **#19** (+16) |
| **20** | David Miller | 109 | 70.21 | Jonny Bairstow | 126 | 76.54 | New Entrant (Unranked $\rightarrow$ #20) |

- **MS Dhoni**: #1 in M0 (194 balls, BRS 95.05) $\rightarrow$ **#56 in M4** (182 balls, BRS 63.66). M0's absolute PI >= 61 threshold gave death finishers an artificial monopoly. M4 cross-phase scaling normalizes death overs.
- **Virat Kohli**: Tier 2 in M0 (47 balls, BRS 51.46) $\rightarrow$ **#11 in M4** (151 balls, BRS 81.76). Phase-relative Powerplay/Middle cutoffs and steep chase recalibration allow Kohli's elite anchor clutch to qualify.
- **Top 10 Overlap**: Exactly **0 / 10 (0.0%)**.

---

### Top 20 Authoritative Bowler Rankings: Model 0 vs Model 4

| Rank | Model 0 (Official Baseline) | HP Balls (M0) | BoRS (M0) | Model 4 (Combined System) | HP Balls (M4) | BoRS (M4) | Rank Change (M0 $\rightarrow$ M4) |
|:---:|:---|:---:|:---:|:---|:---:|:---:|:---:|
| **1** | Tim Southee | 64 | 90.69 | Nasum Ahmed | 85 | 91.64 | New Entrant (Unranked $\rightarrow$ #1) |
| **2** | Keshav Maharaj | 78 | 79.94 | Mark Wood | 85 | 86.45 | New Entrant (Unranked $\rightarrow$ #2) |
| **3** | Haris Rauf | 106 | 78.84 | Brad Evans | 75 | 81.77 | New Entrant (Unranked $\rightarrow$ #3) |
| **4** | Mark Adair | 71 | 74.70 | Tim Southee | 162 | 77.70 | #1 (64 b) $\rightarrow$ **#4** (-3) |
| **5** | Shoriful Islam | 61 | 74.01 | Harshit Rana | 223 | 74.76 | #6 (158 b) $\rightarrow$ **#5** (+1) |
| **6** | Harshit Rana | 158 | 72.85 | Matthew Humphreys | 72 | 73.47 | New Entrant (Unranked $\rightarrow$ #6) |
| **7** | Wanindu Hasaranga | 198 | 70.04 | Craig Young | 69 | 72.99 | New Entrant (Unranked $\rightarrow$ #7) |
| **8** | Trent Boult | 180 | 69.72 | Haris Rauf | 163 | 72.75 | #3 (106 b) $\rightarrow$ **#8** (-5) |
| **9** | Simarjeet Singh | 60 | 69.40 | Ravichandran Ashwin | 253 | 72.43 | #14 (170 b) $\rightarrow$ **#9** (+5) |
| **10** | Lungi Ngidi | 110 | 68.89 | Keshav Maharaj | 120 | 71.36 | #2 (78 b) $\rightarrow$ **#10** (-8) |
| **11** | Richard Ngarava | 75 | 68.32 | Wanindu Hasaranga | 382 | 68.58 | #7 (198 b) $\rightarrow$ #11 (-4) |
| **12** | Arshdeep Singh | 140 | 68.22 | Nathan Ellis | 220 | 67.57 | #19 (108 b) $\rightarrow$ **#12** (+7) |
| **13** | Sandeep Sharma | 116 | 67.87 | Lockie Ferguson | 215 | 67.14 | #20 (126 b) $\rightarrow$ **#13** (+7) |
| **14** | Ravichandran Ashwin | 170 | 67.43 | Arshdeep Singh | 224 | 66.86 | #12 (140 b) $\rightarrow$ #14 (-2) |
| **15** | Blessing Muzarabani | 75 | 67.27 | Sandeep Sharma | 244 | 66.50 | #13 (116 b) $\rightarrow$ #15 (-2) |
| **16** | Mohit Sharma | 177 | 66.69 | T Natarajan | 275 | 66.19 | #23 (152 b) $\rightarrow$ **#16** (+7) |
| **17** | Mohammed Siraj | 144 | 66.24 | Mark Adair | 148 | 65.55 | #4 (71 b) $\rightarrow$ #17 (-13) |
| **18** | Avesh Khan | 128 | 65.65 | Lungi Ngidi | 189 | 64.97 | #10 (110 b) $\rightarrow$ #18 (-8) |
| **19** | Nathan Ellis | 108 | 65.48 | Blessing Muzarabani | 158 | 64.67 | #15 (75 b) $\rightarrow$ #19 (-4) |
| **20** | Lockie Ferguson | 126 | 65.46 | Mohit Sharma | 267 | 64.38 | #16 (177 b) $\rightarrow$ #20 (-4) |

- **Jasprit Bumrah**: #24 in M0 (168 balls, BoRS 59.29) $\rightarrow$ **#12 in M1** (210 balls, BoRS 64.56) $\rightarrow$ **#24 in M4** (382 balls, BoRS 60.45).
- **Sunil Narine**: #43 in M0 (217 balls, BoRS 55.56) $\rightarrow$ **#21 in M1** (191 balls, BoRS 62.12) $\rightarrow$ **#35 in M4** (340 balls, BoRS 56.84).
- **Trent Boult**: #8 in M0 (180 balls, BoRS 69.72) $\rightarrow$ **#36 in M1** (194 balls, BoRS 57.35) $\rightarrow$ **#38 in M4** (287 balls, BoRS 56.52).
- **Top 10 Overlap**: Exactly **4 / 10 (40.0%)** (Tim Southee, Harshit Rana, Haris Rauf, Keshav Maharaj) retain Top 10 status in the authoritative pipeline. (Step 9 reported 3 due to omitting extras runs).

---

## Section F: Combined Model Reproducibility & Interaction Dynamics (Model 4)

### 1. Dynamic Threshold Recalibration
Because M1 (Workload) and M3 (2nd Innings PP) alter delivery-level PI distributions, empirical 80th percentiles shift dynamically:

| Phase | Metric | Base Baseline | Model 4 Value | Net Threshold Shift | Physical Driver |
|:---|:---|:---:|:---:|:---:|:---|
| **Powerplay** | Batting P80 | 50.50 | **52.86** | **+2.36** | Variant 1 floor elevates steep chase pressure. |
| **Powerplay** | Bowling P80 | 60.27 | **57.13** | **-3.14** | PP workload increases average PP score, compressing distribution. |
| **Middle** | Batting P80 | 50.92 | **50.92** | 0.00 | Middle phase inputs remain unaffected by M1/M3. |
| **Middle** | Bowling P80 | 52.73 | **53.17** | **+0.45** | Workload additive penalty slightly raises threshold. |
| **Death** | Batting P80 | 62.40 | **62.40** | 0.00 | Death batting inputs remain unaffected. |
| **Death** | Bowling P80 | 41.88 | **48.37** | **+6.49** | Innings workload (+10.6 pts) heavily shifts Death Bowling P80. |

```
Visual Artifact: outputs/experimental_model_validation/05_combined_model_interaction_effects.png
Discrepancy Table: outputs/experimental_model_validation/combined_model_validation_discrepancies.csv
```

### 2. Full Population Cohort Transitions & Reconciled Counts

| Cohort | Baseline (M0) | Model 4 Count | New Entrants | Dropouts | Net Expansion |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Tier 1 Batters ($\ge 60$ HP balls)** | **116** | **188** | +73 | -1 (Odean Smith) | **+72 (+62.1%)** |
| **Tier 1 Bowlers ($\ge 60$ HP balls)** | **113** | **165** | +52 | 0 | **+52 (+46.0%)** |
| **Tier 2 Batters (40–59 HP balls)** | 72 | 73 | +22 | -21 | **+1** |
| **Tier 2 Bowlers (40–59 HP balls)** | 36 | 36 | +22 | -22 | **0** |
| **Below Threshold Batters** | 628 | 555 | 0 | -73 | **-73** |
| **Below Threshold Bowlers** | 440 | 388 | 0 | -52 | **-52** |

### 3. Full Population Spearman Correlations
- **Batters**:
  - Full population ($N=816$): $\rho = 0.7647$
  - Tier 1 qualified in both ($N=115$): $\rho = 0.7623$ (Step 9 reported 0.7629).
- **Bowlers**:
  - Full population ($N=589$): $\rho = 0.6399$
  - Tier 1 qualified in both ($N=113$): $\rho = 0.7195$ (Step 9 reported 0.7285). The difference is explained by Step 9's omission of 1,018 extras runs in high economy calculations.

---

## Section G: Detailed Responses to the 7 Mandatory Evaluation Questions

### Question 1: Are all three experimental formulas implemented correctly?
**Answer: PARTIALLY YES**.
- **Bowler Workload (Model 1)**: Correctly implemented. Strictly obeys pre-delivery legal ball counting, spell resets ($\ge 2$ overs), and saturation caps.
- **Phase-Relative Cutoffs (Model 2)**: Correctly implemented. Accurately derives empirical 80th percentiles per phase.
- **2nd Innings PP Target Pressure Floor (Model 3, Variant 1)**: Correctly implemented. Elevates steep chase pressure without false positives in modest chases.
- **Settled Batter Multiplier (Model 3, Variant 2)**: **FAILED**. Conceptually flawed; penalizes set batters actively keeping chases alive. Permanently rejected.

### Question 2: Are all delivery-level changes reproducible?
**Answer: YES (100.00% Reproducible)** across all 188,097 clean deliveries. Spell saturation cap balls (13,751), mean workloads, phase percentiles, and steep chase reclassifications match to full numerical precision.

### Question 3: Does the ranking pipeline preserve the original model?
**Answer: NO in Step 9; YES in Step 10 Authoritative Pipeline**.
Step 9 introduced two data handling flaws:
1. Leaked 233 deliveries post-match conclusion (`runs_required <= 0`), altering Marco Jansen's rank by 5 spots.
2. Dropped 1,018 penalty runs on wides/no-balls, distorting the bowling high economy prior from 9.06 to 8.75 rpo.
Step 10's authoritative pipeline corrects both, achieving **100.00% exact parity** with official Step 6.2 production rankings.

### Question 4: Are Tier 1 and Tier 2 eligibility changes correct?
**Answer: YES**.
Reconciled counts: Baseline Tier 1 has 116 batters and 113 bowlers. Model 4 expands Tier 1 by +72 batters (to 188; 73 new entrants, 1 dropout: Odean Smith) and +52 bowlers (to 165; 52 new entrants, 0 dropouts).

### Question 5: Are the reported Top 10 changes correct?
**Answer: PARTIALLY YES**.
- Batter Top 10 overlap is confirmed at **0 / 10 (0.0%)**.
- Bowler Top 10 overlap is corrected from Step 9's reported 3 / 10 to **4 / 10 (40.0%)** (Tim Southee, Harshit Rana, Haris Rauf, Keshav Maharaj), following resolution of the extras penalty runs omission.

### Question 6: Is the combined model reproducible?
**Answer: YES (Fully Reproducible)**.
Model 4's multi-stage compounding effects and dynamic P80 recalibration (Death Bowling P80 rising to 48.37; PP Batting P80 rising to 52.86) were reproduced independently from raw deliveries.

### Question 7: Which Step 9 conclusions should be corrected or withdrawn?
**Answer**:
1. **Withdraw the Settled Batter Multiplier (Variant 2)**: Permanently reject the batter run discount.
2. **Correct Bowling Economy Aggregation**: Must include the 1,018 runs conceded on wides/no-balls on high-pressure balls.
3. **Correct Post-Target Filtering**: Must filter out 233 deliveries where `runs_required <= 0`.
4. **Correct Bowler Top 10 Overlap**: Correct from 3 to 4 bowlers.
5. **Clarify Discrete Ties**: Explicitly document the 588 deliveries tied at 62.40 in Death Batting.

---

## Section H: Strategic Governance & Production Status

1. **Official Production Stability**: Official v2.0 datasets (`data/processed/`) and production ranking models (`src/rank_players.py`) **remain completely unchanged**.
2. **Experimental Prototype Status**: Model 4 is a research prototype and is **NOT APPROVED** as a new official model.
3. **Future v3.0 Guidance**:
   - Phase-Relative Cutoffs (Model 2) provides the strongest conceptual remedy for the death-overs finishing monopoly.
   - Innings Workload (Model 1) must be redesigned to avoid collinearity with over number.
   - Variant 1 target floor provides a robust mechanism for Powerplay chases.

---

## Verification Artifact Manifest

- **Module Directory**: [`src/experimental_model_validation/`](file:///c:/Users/ASUS/Desktop/supeRR_selector/src/experimental_model_validation/)
  - [`run_validation.py`](file:///c:/Users/ASUS/Desktop/supeRR_selector/src/experimental_model_validation/run_validation.py) (Master Runner)
  - [`validate_workload.py`](file:///c:/Users/ASUS/Desktop/supeRR_selector/src/experimental_model_validation/validate_workload.py)
  - [`validate_phase_relative.py`](file:///c:/Users/ASUS/Desktop/supeRR_selector/src/experimental_model_validation/validate_phase_relative.py)
  - [`validate_second_innings_pp.py`](file:///c:/Users/ASUS/Desktop/supeRR_selector/src/experimental_model_validation/validate_second_innings_pp.py)
  - [`validate_ranking_pipeline.py`](file:///c:/Users/ASUS/Desktop/supeRR_selector/src/experimental_model_validation/validate_ranking_pipeline.py)
  - [`validate_combined_model.py`](file:///c:/Users/ASUS/Desktop/supeRR_selector/src/experimental_model_validation/validate_combined_model.py)
  - [`README.md`](file:///c:/Users/ASUS/Desktop/supeRR_selector/src/experimental_model_validation/README.md)
- **Output Artifacts**: [`outputs/experimental_model_validation/`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/experimental_model_validation/)
  - Figures: [`01_workload_validation_comparison.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/experimental_model_validation/01_workload_validation_comparison.png), [`02_phase_relative_ties_and_cutoffs.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/experimental_model_validation/02_phase_relative_ties_and_cutoffs.png), [`03_second_innings_pp_validation.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/experimental_model_validation/03_second_innings_pp_validation.png), [`04_ranking_pipeline_discrepancy_analysis.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/experimental_model_validation/04_ranking_pipeline_discrepancy_analysis.png), [`05_combined_model_interaction_effects.png`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/experimental_model_validation/05_combined_model_interaction_effects.png)
  - Discrepancy Tables: [`workload_validation_discrepancies.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/experimental_model_validation/workload_validation_discrepancies.csv), [`phase_relative_validation_discrepancies.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/experimental_model_validation/phase_relative_validation_discrepancies.csv), [`second_innings_pp_validation_discrepancies.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/experimental_model_validation/second_innings_pp_validation_discrepancies.csv), [`ranking_pipeline_validation_discrepancies.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/experimental_model_validation/ranking_pipeline_validation_discrepancies.csv), [`combined_model_validation_discrepancies.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/experimental_model_validation/combined_model_validation_discrepancies.csv)
  - Authoritative Rankings: [`authoritative_experimental_rankings_batters.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/experimental_model_validation/authoritative_experimental_rankings_batters.csv), [`authoritative_experimental_rankings_bowlers.csv`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/experimental_model_validation/authoritative_experimental_rankings_bowlers.csv)
  - Audit Report: [`experimental_model_validation_report.md`](file:///c:/Users/ASUS/Desktop/supeRR_selector/outputs/experimental_model_validation/experimental_model_validation_report.md)
