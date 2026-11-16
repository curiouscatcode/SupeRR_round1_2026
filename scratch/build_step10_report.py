# Script to generate step_10_methodology_report.md
import os

content = """# Identifying the Most Reliable T20 Players Under Pressure
## A Dual-Dimensional Situational Value Framework with Empirical Bayes Calibration

**Competition:** SupeRR Selector 2.0 — Round 1  
**Official Objective:** Identify the Most Reliable Players Under Pressure  
**Document:** Official Competition Methodology Report (Step 10)  
**Authors:** Antigravity (Google DeepMind Agentic System)  
**Date:** November 15, 2026  
**Status:** Certified, Fully Audited & Frozen  
**Governing Authority:** Frozen Step 6.3 Mathematical Specification & Step 7.4 Certified Scoring Engine  

---

## Table of Contents
1. [Section 1 — Executive Summary](#section-1--executive-summary)
2. [Section 2 — Dataset and Scope](#section-2--dataset-and-scope)
3. [Section 3 — Defining Pressure: The Dual-Dimensional Framework](#section-3--defining-pressure-the-dual-dimensional-framework)
4. [Section 4 — Calculating Delivery-Level Pressure](#section-4--calculating-delivery-level-pressure)
5. [Section 5 — Measuring Player Reliability: PWSVA and SBVA](#section-5--measuring-player-reliability-pwsva-and-sbva)
6. [Section 6 — Fairness, Eligibility, and Shrinkage Mechanics](#section-6--fairness-eligibility-and-shrinkage-mechanics)
7. [Section 7 — Empirical Validation and Auditing Evidence](#section-7--empirical-validation-and-auditing-evidence)
8. [Section 8 — Final Official Player Rankings](#section-8--final-official-player-rankings)
9. [Section 9 — Limitations and Future Enhancements](#section-9--limitations-and-future-enhancements)
10. [Section 10 — Conclusion](#section-10--conclusion)
11. [Technical Appendix & Authoritative Source Manifest](#technical-appendix--authoritative-source-manifest)

---

## Section 1 — Executive Summary

### 1.1 The Core Problem
Conventional cricket evaluation metrics—such as batting average, batting strike rate, bowling average, and economy rate—suffer from a foundational flaw: **they are blind to context and leverage**. In professional T20 cricket:
- A boundary hit in the 18th over of a steep chase needing 12 runs per over is treated identically to a boundary scored in a low-stakes blowout where the match is already decided.
- A dot ball bowled in the final over defending 8 runs is credited identically to a dot ball conceded when the batting team needs 60 runs from 12 balls.
- Traditional metrics ignore match phase, pitch par, wickets in hand, and leverage, penalizing middle-order rescue batters who face defensive fields and rewarding top-order anchors who accumulate runs during low-pressure powerplay overs.

To identify the **Most Reliable Players Under Pressure**, a ranking engine must isolate true performance above contextual expectation and rigorously scale that performance by the leverage of each delivery.

### 1.2 What the System Measures
This methodology introduces a principled statistical framework that measures **observed reliability under situational pressure**:
1. **Objective Delivery-Level Pressure ($P \in [0, 100]$):** Evaluated strictly before delivery release ($t^-$) by combining **Task Difficulty** (the athletic demand facing the player) and **Match Consequence** (the potential win probability swing of the ball) through a geometric mean.
2. **Context-Adjusted Situational Value Added:** Measures run creation and run prevention relative to a 36-cell empirical baseline model conditioned on innings, competition format, match phase, and wickets lost, integrated with dynamic situational wicket valuations.
3. **Continuous Pressure Weighting:** Weights each ball by $w(P) = (P / 50)^{\alpha}$ with baseline $\alpha = 1.00$, ensuring high-leverage deliveries dictate reliability scores without discarding low-pressure baseline data.
4. **Empirical Bayes Shrinkage:** Regresses raw averages toward population replacement level ($0.0$) using Kish Effective Sample Size ($\\text{ESS}$) with calibrated shrinkage constants ($K_{\\text{bat}} = 600, K_{\\text{bowl}} = 500$), eliminating small-sample noise and fluke performances.

### 1.3 Scope and Data Cohort
The analytical cohort comprises **186,780 deliveries across 782 certified 20-over matches** from the Indian Premier League (IPL) and T20 Internationals (T20I) between January 2022 and May 2026. Players must face at least 50 balls (batting) or bowl at least 50 legal balls (bowling) under above-average pressure ($P \ge 50$) to qualify. Across the certified cohort, **297 batters** and **292 bowlers** met the eligibility standard.

### 1.4 Official Podium & Top 10 Rankings
The frozen Step 7.4 scoring pipeline established the following official Top 10 players under pressure:

#### Official Top 10 Batting Reliability Rankings (PWSVA)
```
========================================================================================================================
Rank  Player                  Team / Franchise            Shrunk Score  Raw Score  Raw Balls  Kish ESS  95% Bootstrap CI
========================================================================================================================
1     Vaibhav Sooryavanshi    Rajasthan Royals (IPL/T20)    +0.3487     +0.7614       564       506.9   [+0.1422, +0.5226]
2     Suryakumar Yadav        India (IPL/T20I)              +0.2819     +0.3558      2638      2287.2   [+0.1826, +0.3700]
3     Abhishek Sharma         Sunrisers Hyderabad (IPL/T20) +0.2703     +0.3547      2195      1923.3   [+0.1295, +0.3993]
4     Tim David               Australia (IPL/T20I)          +0.2571     +0.4144      1163       980.6   [+0.1292, +0.3780]
5     Heinrich Klaasen        Sunrisers Hyderabad (IPL/T20) +0.2201     +0.3357      1409      1142.0   [+0.1238, +0.3072]
6     Phil Salt               England (IPL/T20I)            +0.1954     +0.2813      1591      1364.7   [+0.0633, +0.3033]
7     Namboori Tilak Varma    Mumbai Indians (IPL/T20I)     +0.1745     +0.2277      2338      1968.9   [+0.0802, +0.2667]
8     Travis Head             Sunrisers Hyderabad (IPL/T20) +0.1625     +0.2611      1096       988.6   [+0.0017, +0.3203]
9     Andre Russell           Kolkata Knight Riders (IPL/T) +0.1579     +0.3239       698       570.7   [+0.0300, +0.2855]
10    Reeza Hendricks         South Africa (T20I)           +0.1564     +0.2874       776       715.9   [+0.0071, +0.2869]
========================================================================================================================
```

#### Official Top 10 Bowling Reliability Rankings (SBVA)
```
========================================================================================================================
Rank  Player                  Team / Franchise            Shrunk Score  Raw Score  Raw Balls  Kish ESS  95% Bootstrap CI
========================================================================================================================
1     Rashid Khan             Gujarat Titans (IPL/T20I)     +0.1756     +0.2147      2648      2245.9   [+0.0810, +0.2784]
2     Jasprit Bumrah          Mumbai Indians (IPL/T20I)     +0.1541     +0.2103      1606      1369.7   [+0.0237, +0.2784]
3     Sunil Narine            Kolkata Knight Riders (IPL)   +0.1442     +0.2020      1464      1246.3   [+0.0555, +0.2334]
4     Josh Hazlewood          Royal Challengers Bengaluru   +0.1330     +0.1904      1368      1159.5   [+0.0021, +0.2830]
5     Wanindu Hasaranga       Sri Lanka (IPL/T20I)          +0.1184     +0.1537      1932      1675.4   [+0.0365, +0.2000]
6     Bhuvneshwar Kumar       Sunrisers Hyderabad (IPL/T20) +0.1065     +0.1349      2159      1875.7   [-0.0086, +0.2189]
7     Abrar Ahmed             Pakistan (T20I)               +0.1058     +0.1933       751       604.7   [-0.0250, +0.2277]
8     Kuldeep Yadav           Delhi Capitals (IPL/T20I)     +0.1027     +0.1346      1884      1608.6   [+0.0085, +0.2104]
9     Mahedi Hasan            Bangladesh (T20I)             +0.1025     +0.1700       860       760.3   [-0.0435, +0.2474]
10    Mujeeb Ur Rahman        Afghanistan (IPL/T20I)        +0.1024     +0.1770       772       686.6   [-0.0117, +0.2149]
========================================================================================================================
```

---

## Section 2 — Dataset and Scope

### 2.1 The Analytical Cohort
The evaluation dataset is drawn from top-tier men's T20 cricket across the 2022–2026 cycle:
- **Indian Premier League (IPL):** 2022, 2023, 2024, 2025, and early 2026 seasons.
- **T20 Internationals (T20I):** All full-member and ICC tournament fixtures involving top-tier national teams.

A total of 789 raw matches containing 188,330 reconstructed deliveries were audited. To enforce structural homogeneity, a three-step certified filtration protocol was applied:

```
====================================================================================================
CERTIFIED COHORT FILTRATION RECONCILIATION
====================================================================================================
Starting Raw Reconstructed Deliveries:                         188,330 (789 matches)
  [-] Exclusion 1: Dead-tail deliveries (runs_required <= 0):     -233 ( 90 matches affected)
  [-] Exclusion 2: Confirmed mid-match DLS matches (4 matches):   -821 (  4 matches excluded)
      * Match 20182 (IPL 2023, PBKS vs KKR, rain halted 16.0 ov):  222 deliveries
      * Match 23674 (T20I 2023, BAN vs AFG, shortened 17 ov):     211 deliveries
      * Match 24822 (T20I 2023, IND vs IRE, rain halted 6.5 ov):   170 deliveries
      * Match 28334 (T20I 2023, NZ vs BAN, rain halted 14.4 ov):   218 deliveries
  [-] Exclusion 3: Pre-match shortened matches (3 matches):       -496 (  3 matches excluded)
      * Match 15795 (T20I 2022, IND vs IRE, 12 ov/side):          138 deliveries
      * Match 31278 (IPL 2024, KKR vs MI, 16 ov/side):            201 deliveries
      * Match 48514 (T20I 2026, SL vs PAK, 12 ov/side):           157 deliveries
----------------------------------------------------------------------------------------------------
FINAL CERTIFIED 20-OVER COHORT:                               186,780 deliveries (782 matches)
  - Innings 1 Deliveries:                                       97,443 deliveries (782 matches)
  - Innings 2 Deliveries:                                       89,337 deliveries (782 matches)
====================================================================================================
```

### 2.2 Preprocessing and State Reconstruction
Each delivery is reconstructed into an exact pre-delivery state vector $S_t$:
- Ball counter $L_t \in [0, 119]$ representing legal deliveries completed in the innings.
- Legal balls remaining in the innings: $B_{\\text{rem}} = 120 - L_t$.
- Score before delivery: $S_t$.
- Wickets lost before delivery: $W_t \in [0, 9]$. Wickets remaining: $W_{\\text{rem}} = 10 - W_t$.
- Target score and runs required in Innings 2: $R_t = \text{Target} - S_t$.
- Current match phase $\phi_t \in \{\text{Powerplay (Overs 1–6)}, \text{Middle (Overs 7–15)}, \text{Death (Overs 16–20)}\}$.
- Venue historical par score $\text{Par}_{\text{venue}}$ (mean first-innings total at that specific venue).

### 2.3 Discipline Populations and Opportunity Units
Batting and bowling evaluate different athletic opportunities:
- **Batting Population ($N = 297$ qualified):** Evaluated strictly on deliveries where the batter was on strike and faced the ball (`is_batter_ball_faced == True`). Non-striker deliveries and wides are excluded from batting balls faced.
- **Bowling Population ($N = 292$ qualified):** Evaluated on all deliveries credited to the bowler. To prevent double-counting extra deliveries, bowling opportunities are normalized to the **legal ball quota** (`is_legal_ball == True`). Wides and no-balls are not counted as additional opportunities, but the extra runs and re-bowled deliveries are directly penalized in the bowler's runs conceded.

### 2.4 Missing Data Discipline
No missing deliveries, outcomes, or coordinates are imputed. If vendor ball-by-ball feeds collapsed multi-run wides into single-run records (noted in 101 historical matches), raw recorded runs were strictly preserved rather than synthetically edited.

---

## Section 3 — Defining Pressure: The Dual-Dimensional Framework

### 3.1 The Fundamental Postulate of Pressure
A robust definition of pressure cannot rely on intuition or a single arbitrary variable. In cricket:
- **Task Difficulty alone does not equal pressure:** Requiring 36 runs off the final 6 balls has maximum task difficulty (almost impossible), but if the batting team is 80/9 in a blowout, the match outcome is already decided. Slogging in garbage time carries near-zero competitive consequence.
- **Match Consequence alone does not equal pressure:** Bowling the first ball of a World Cup final has immense match consequence (the entire game hinges on the match), but the immediate athletic task is completely routine ($0/0$, 120 balls remaining, zero scoreboard stress).

True situational pressure exists only at the intersection of both dimensions:

$$\mathbf{\text{Pressure} = \sqrt{\text{Task Difficulty} \times \text{Match Consequence}}}$$

```
                           Task Difficulty (T)
                 Low [0] ──────────────────────► High [100]
              ┌────────────────────────┬────────────────────────┐
   High [100] │  MODERATE PRESSURE     │     MAXIMUM CLUTCH     │
              │  (Opening deliveries,  │  (Close death finish,  │
              │   early high stakes)   │   12 off 6 balls, 7 wk)│
Match         ├────────────────────────┼────────────────────────┤
Consequence   │  MINIMAL PRESSURE      │   SUPPRESSED PRESSURE  │
(L_norm)      │  (Comfortable chase,   │  (Impossible blowout,  │
   Low [0]    │   needs 4 off 36 balls)│   needs 45 off 6 balls)│
              └────────────────────────┴────────────────────────┘
```

### 3.2 Pre-Delivery Invariant ($t^-$)
Pressure is evaluated **strictly prior to the delivery outcome**. The pressure index $P(S_t)$ describes the situational demand facing the player as the bowler reaches the crease. It does not use the delivery result (e.g., whether a six was hit or a wicket fell) to define its own pressure. Post-delivery correlation tests confirm zero outcome leakage ($r_{\text{wicket}} = +0.0078, r_{\text{runs}} = -0.0094$).

### 3.3 Asymmetry Between Batting and Bowling
Batting and bowling are asymmetrical strategic disciplines:
- In the first innings, the batting unit aims to maximize the final total against par while managing wicket capital. The bowling unit aims to contain scoring and break partnerships.
- In the second innings, the batting chase is deterministic ($R_t$ runs from $B_{\text{rem}}$ balls). The bowling unit faces the inverse challenge: defending a fixed target where every conceded boundary reduces margin for error.

Consequently, the framework deploys **four distinct situational models**:
1. First-Innings Batting ($P_{B1}$)
2. Second-Innings Batting ($P_{B2}$)
3. First-Innings Bowling ($P_{BO1}$)
4. Second-Innings Bowling ($P_{BO2}$)

---

## Section 4 — Calculating Delivery-Level Pressure

### 4.1 Batting Task Difficulty Models ($T_{B1}, T_{B2}$)

#### Model 1: First-Innings Batting ($T_{B1}$)
In Innings 1, difficulty reflects resource scarcity and run-rate acceleration required to meet or exceed venue par ($	ext{Par}_{	ext{venue}}$):

$$Z_{B1}(S_t) = 0.45 \left(\frac{\text{RAR}_{B1}(S_t) - R_{\text{par}}}{R_{\text{par}}}\right) + 0.35 \left(\frac{W_t - \mu_W(L_t)}{\max(0.50,\, \sigma_W(L_t))}\right) + 0.20 \left(\frac{W_t}{10 - W_t + 1}\right)$$

$$T_{B1}(S_t) = \frac{100}{1 + \exp(- 1.2 \cdot Z_{B1}(S_t))}$$

Where $	ext{RAR}_{B1} = \frac{\text{Par}_{\text{venue}} - S_t}{\max(1, B_{\text{rem}})/6}$ is the required acceleration rate, and $\mu_W(L_t) \approx 10 \times (1 - (1 - L_t/120)^{0.65})$ represents the empirical wicket loss curve. On the opening ball ($L_t = 0, S_t = 0, W_t = 0$), $Z_{B1} = 0.00$, calibrating baseline difficulty to exactly **$50.00$**.

#### Model 2: Second-Innings Batting ($T_{B2}$)
In Innings 2, difficulty reflects the required run rate ($	ext{RRR}_t = \frac{R_t}{B_{\text{rem}}/6}$) compounded non-linearly by wicket scarcity:

$$Z_{B2}(S_t) = 0.55 \left(\frac{\text{RRR}_t - 8.10}{3.00}\right) + 0.30 \left(\frac{W_t - \mu_W(L_t)}{\max(0.50,\, \sigma_W(L_t))}\right) + 0.15 \left(\frac{\text{RRR}_t}{8.10} \times \frac{W_t}{10 - W_t + 1}\right)$$

$$T_{B2}(S_t) = \frac{100}{1 + \exp(- 0.95 \cdot Z_{B2}(S_t))}$$

### 4.2 Bowling Task Difficulty Models ($T_{BO1}, T_{BO2}$)

#### Model 3: First-Innings Bowling ($T_{BO1}$)
Measures containment stress when the batting side is scoring above par with wickets in hand:

$$Z_{BO1}(S_t) = 0.50 \left(\frac{\text{CRR}_t - R_{\text{par}}}{R_{\text{par}}}\right) + 0.35 \left(\frac{\mu_W(L_t) - W_t}{\max(0.50,\, \sigma_W(L_t))}\right) + 0.15 \cdot \text{FieldFactor}(\phi_t)$$

$$T_{BO1}(S_t) = \frac{100}{1 + \exp(- 1.1 \cdot Z_{BO1}(S_t))}$$

Where $\text{FieldFactor} = +0.50$ for Powerplay and Death overs, and $0.00$ for Middle overs. The term $(\mu_W(L_t) - W_t)$ assigns positive difficulty when the batting side has *more wickets in hand* than average ($W_t < \mu_W$).

#### Model 4: Second-Innings Bowling ($T_{BO2}$)
Measures defending hardship: defending is most stressful when the opponent's required run rate is low and they possess abundant wickets:

$$Z_{BO2}(S_t) = 0.60 \left(\frac{8.10 - \text{RRR}_t}{3.00}\right) + 0.40 \left(\frac{\mu_W(L_t) - W_t}{\max(0.50,\, \sigma_W(L_t))}\right)$$

$$T_{BO2}(S_t) = \frac{100}{1 + \exp(- 1.0 \cdot Z_{BO2}(S_t))}$$

### 4.3 Match Consequence ($L$) & Midpoint ECDF Normalization
Match Consequence measures the expected absolute swing in Win Probability across all possible delivery outcomes $\mathcal{O} = \{0, 1, 2, 3, 4, 6, W, \text{wide}, \text{no\_ball}\}$:

$$L(S_t) = \sum_{o \in \mathcal{O}} P(o \mid \phi_t, \text{innings}) \cdot |\text{WP}(S_{t+1}(o)) - \text{WP}(S_t)|$$

- **Penultimate Balls ($B_{\text{rem}} > 1$):** Win probability is estimated via out-of-sample logistic regression models fitted on pre-delivery state vectors.
- **Terminal Balls ($B_{\text{rem}} = 1$ in Innings 2):** Evaluated via discrete Markov terminal recurrence:
  $$\text{WP}_{\text{final}}(S_t, o) = \begin{cases} 
  1.0 & \text{if } r(o) \ge R_t \text{ and legal delivery} \\
  0.5 & \text{if } r(o) = R_t - 1 \text{ (Super Over)} \\
  0.0 & \text{if } r(o) < R_t - 1 \text{ or } o = W_{10} \\
  \text{WP}_{\text{Markov}}(R_t - 1,\, W_t) & \text{if } o \in \{\text{wide},\, \text{no\_ball}\} \text{ (re-bowled)}
  \end{cases}$$

#### Innings-Specific Midpoint ECDF Normalization
Raw consequence $L(S_t)$ naturally concentrates at lower values in Innings 1 and spikes in late Innings 2. To avoid cross-innings bias, raw values are normalized within each innings using midpoint empirical cumulative distribution percentiles:

$$L_{\text{norm}}(S_t) = \left( \frac{\sum_{j=1}^{N_i} \mathbb{I}(L_j^{(i)} < L(S_t)) + 0.5 \sum_{j=1}^{N_i} \mathbb{I}(L_j^{(i)} = L(S_t))}{N_i} \right) \times 100$$

This maps both innings to an identical median of exactly **$50.00$ index points** ($[0, 100]$ range), eliminating artificial death-over domination.

### 4.4 Final Geometric Mean Combination
The delivery pressure index combines Task Difficulty and Normalized Consequence:

$$P(S_t) = \sqrt{T(S_t) \times L_{\text{norm}}(S_t)}$$

Because the geometric mean acts as a multiplicative gate, if either dimension approaches zero, overall pressure collapses.

```
========================================================================================================================
Scenario                   Match State                  T_bat    L_norm   P_bat    Cricket Logic Verified
========================================================================================================================
1. Opening Ball (0.1)      Score 0/0, Needs 165 off 120 50.00    99.60    70.57    Opening delivery carries high base leverage
2. Top-Order Collapse      Score 10/3, Over 4.2         78.43    33.58    51.33    High crisis difficulty; bowling on top
3. Impossible Chase        Needs 10 off 1, Score 162/8  99.97     0.11     3.34    Impossible task; decided match suppressed
4. Comfortable Stroll      Needs 4 off 36, Score 166/2  14.28     3.35     6.92    Trivial chase; minimal pressure
5. Garbage-Time Blowout    Needs 52 off 12, Score 142/5 99.97     4.77    21.83    Decided game; slogging suppressed
========================================================================================================================
```

---

## Section 5 — Measuring Player Reliability: PWSVA and SBVA

Player reliability measures performance above situational expectation, weighted continuously by delivery leverage.

### 5.1 The 36-Cell Contextual Baseline
To measure true value added, performance is contrasted against expected baseline values derived from an empirical 36-cell tensor:
$$\text{Cell Structure} = 2 \text{ Innings} \times 2 \text{ Formats (IPL, T20I)} \times 3 \text{ Phases} \times 3 \text{ Wicket Buckets}$$

- **Powerplay:** 0, 1, 2+ wickets down.
- **Middle Overs:** 0–2, 3–4, 5+ wickets down.
- **Death Overs:** 0–3, 4–6, 7+ wickets down.

Each cell $c_i$ provides out-of-sample expected values:
- $\mathbb{E}[R \mid c_i]$: Expected batter runs per ball.
- $\mathbb{E}[W_{\text{bat}} \mid c_i]$: Expected striker dismissal probability.
- $\mathbb{E}[R_{\text{conc}} \mid c_i]$: Expected bowler runs conceded per legal ball.
- $\mathbb{E}[W_{\text{bowl}} \mid c_i]$: Expected bowler-credited wicket probability.

### 5.2 Dynamic Wicket Valuation ($\lambda_{\text{wkt}}$ and $\lambda_{\text{eff}}$)
A wicket is valued dynamically according to the run-expectancy surface:
$$\lambda_{\text{wkt}}(B_{\text{rem}}, W_{\text{rem}}) = \mathbb{E}[S \mid B_{\text{rem}}, W_{\text{rem}}] - \mathbb{E}[S \mid B_{\text{rem}}, W_{\text{rem}} - 1]$$

#### The Step 6.3 Second-Innings Ceiling Condition:
In the second innings, losing a wicket cannot cost more runs than the entire remaining target. Therefore, the effective wicket value is capped:
$$\lambda_{\text{eff}} = \begin{cases} 
\min(\lambda_{\text{wkt}},\, R_{\text{req}}) & \text{if Innings 2 and } W_{\text{rem}} > 1 \\
\lambda_{\text{wkt}} & \text{otherwise}
\end{cases}$$

### 5.3 Batting Performance Metric: PWSVA
On every delivery faced (`is_batter_ball_faced == True`), situational value added is:
$$v_{\text{bat}, i} = (R_i - \mathbb{E}[R \mid c_i]) - \lambda_{\text{eff}, i} \cdot (W_{\text{striker}, i} - \mathbb{E}[W_{\text{bat}} \mid c_i])$$

Weighted by continuous pressure $w_i = (P_i / 50)^{\alpha}$ with $\alpha = 1.00$:
$$\bar{v}_{\text{bat}} = \frac{\sum_{i} w_i \cdot v_{\text{bat}, i}}{\sum_{i} w_i}$$

Using Kish Effective Sample Size $N_{\text{eff}} = \frac{(\sum w_i)^2}{\sum w_i^2}$, Empirical Bayes shrinkage ($K_{\text{bat}} = 600$) produces the final score:

$$\mathbf{\text{PWSVA}_i^{\text{shrunk}} = \left( \frac{N_{\text{eff}, i}}{N_{\text{eff}, i} + 600} \right) \times \bar{v}_{\text{bat}, i}}$$

### 5.4 Bowling Performance Metric: SBVA
Evaluated on legal deliveries (`is_legal_ball == True`), with extras penalized directly:
$$v_{\text{bowl}, i} = \begin{cases}
(\mathbb{E}[R_{\text{conc}} \mid c_i] - R_{\text{conc}, i}) + \lambda_{\text{eff}, i} \cdot (W_{\text{bowl}, i} - \mathbb{E}[W_{\text{bowl}} \mid c_i]) & \text{if legal ball} \\
- R_{\text{conc}, i} + \lambda_{\text{eff}, i} \cdot W_{\text{bowl}, i} & \text{if extra (wide/no-ball)}
\end{cases}$$

Normalized by the legal ball quota to eliminate extra-ball double counting:
$$\bar{v}_{\text{bowl}} = \frac{\sum_{i} w_i \cdot v_{\text{bowl}, i}}{\sum_{i \in \text{legal}} w_i}$$

Using legal Kish ESS $N_{\text{eff}}^{\text{bowl}} = \frac{(\sum_{\text{legal}} w_i)^2}{\sum_{\text{legal}} w_i^2}$ with $K_{\text{bowl}} = 500$:

$$\mathbf{\text{SBVA}_i^{\text{shrunk}} = \left( \frac{N_{\text{eff}, i}^{\text{bowl}}}{N_{\text{eff}, i}^{\text{bowl}} + 500} \right) \times \bar{v}_{\text{bowl}, i}}$$

---

## Section 6 — Fairness, Eligibility, and Shrinkage Mechanics

### 6.1 Minimum Pressure Exposure Threshold
To qualify for official ranking, a player must achieve sustained exposure to high-pressure competition:
$$\mathbf{N(P \ge 50) \ge 50 \text{ balls faced (batting) or legal deliveries (bowling)}}$$

- **Why Minimum Exposure Matters:** T20 cricket is subject to extreme single-match variance. A specialist who plays two matches and hits 20 runs off 8 balls under high pressure would exhibit an astronomical raw average. Requiring 50 balls at $P \ge 50$ ensures every ranked player has demonstrated performance across multiple match situations.
- **Population Filtering:** Exactly 297 batters and 292 bowlers met this requirement.

### 6.2 Empirical Bayes Shrinkage Curve
Raw averages reward small samples with inflated volatility. Shrinkage acts as a regressive filter toward population replacement level ($0.0$):
$$\text{Retention Ratio} = \frac{N_{\text{eff}}}{N_{\text{eff}} + K}$$

![Figure 3: Batting Score vs Sample Size](../step_8_eda/figures/fig03_batting_score_vs_sample_size.png)
![Figure 4: Bowling Score vs Sample Size](../step_8_eda/figures/fig04_bowling_score_vs_sample_size.png)

1. **At $N_{\text{eff}} = K$:** Exactly $50.0\%$ of raw performance is retained; $50.0\%$ is shrunk toward replacement level.
2. **At High Volume ($N_{\text{eff}} > 2000$):** Players retain over $77\%$ to $82\%$ of their raw performance (e.g., Suryakumar Yadav retains $79.2\%$, Rashid Khan retains $81.8\%$).
3. **Hyperbolic Noise Protection:** Fringe players with high raw averages but modest sample sizes are regressed, ensuring the upper echelon is dominated by genuine reliability rather than statistical anomalies.

### 6.3 Uncertainty Quantification: Match-Level Block Bootstrap
To compute robust confidence bounds without parametric distribution assumptions, **1,000 match-level block bootstrap iterations** were executed:
- Entire match clusters are resampled with replacement, preserving within-match delivery dependencies and bowler-batter matchups.
- Standard errors ($\text{SE}$) and 95% confidence intervals are extracted directly from empirical percentiles.

![Figure 5: Batting Uncertainty Top 10](../step_8_eda/figures/fig05_batting_uncertainty_top10.png)
![Figure 6: Bowling Uncertainty](../step_8_eda/figures/fig06_bowling_uncertainty_top10.png)

#### Interpretation of Overlapping Confidence Bounds:
The confidence intervals of Ranks 2–5 in batting and Ranks 6–10 in bowling overlap. **Close rankings should be interpreted as elite performance tiers rather than certain ordinal separations.** The difference between Rank 10 and Rank 11 is less than $0.0025$ runs/ball in both disciplines.

---

## Section 7 — Empirical Validation and Auditing Evidence

The methodology was validated across an exhaustive series of empirical audits:

### 7.1 Baseline Out-of-Sample Calibration (Step 7.1)
- 36 baseline cells evaluated via 5-fold match-stratified cross-validation.
- Out-of-sample $R^2$ stability confirmed: zero overfitting, zero data leakage.

### 7.2 Pressure Pipeline Integrity (Step 4 & Step 4.1)
- All 12 automated pipeline validation suites passed.
- Pre-delivery invariant confirmed ($r_{\text{leakage}} < 0.01$).
- ECDF midpoint rank normalization confirmed exact $50.00$ median across both innings.

### 7.3 Mathematical Consistency Audit (Step 6.3)
- Elimination of arbitrary wicket value floors (Step 6.3 Audit 2).
- Verification of legal-ball quota normalization for bowling to eliminate extra-ball double counting (Step 6.3 Audit 4).
- Formalization of the second-innings wicket ceiling condition $\lambda_{\text{eff}} = \min(\lambda_{\text{wkt}}, R_{\text{req}})$.

### 7.4 Sensitivity to Pressure Exponent ($\alpha = 1.00 \text{ vs } 1.25$)
To test whether rankings are sensitive to the weighting exponent, scores were recomputed under super-linear weighting $\alpha = 1.25$:

![Figure 7: Alpha Sensitivity](../step_8_eda/figures/fig07_alpha_sensitivity_slope.png)

$$\rho_{\text{bat}} = \mathbf{0.9978} \quad (N = 297), \qquad \rho_{\text{bowl}} = \mathbf{0.9981} \quad (N = 292)$$

Rankings are exceptionally stable. The Top 8 batting positions are 100% invariant. In bowling, Mohammed Shami climbs from #13 to #7 under $\alpha = 1.25$ due to his heavy concentration in extreme death climaxes ($P \ge 75$).

### 7.5 Phase Performance Heatmaps
Visual heatmaps (Figures 10 and 11) plot **unshrunk, pressure-weighted situational value added per ball** within each match phase with an $N \ge 20$ sample suppression threshold:

![Figure 10: Batting Phase Heatmap](../step_8_eda/figures/fig10_batting_phase_heatmap.png)
![Figure 11: Bowling Phase Heatmap](../step_8_eda/figures/fig11_bowling_phase_heatmap.png)

- **Powerplay Specialists:** Abhishek Sharma ($+0.40$ on 1462b), Phil Salt ($+0.32$ on 950b), and Josh Hazlewood ($+0.30$ on 732b).
- **Middle-Overs Masters:** Heinrich Klaasen ($+0.39$ on 915b), Suryakumar Yadav ($+0.44$ on 1673b), and Mujeeb Ur Rahman ($+0.38$ on 306b).
- **Lethal Death Enforcers:** Sunil Narine ($+0.71$ net runs saved/ball on 204b), Rashid Khan ($+0.45$ on 516b), and Jasprit Bumrah ($+0.42$ on 526b).

### 7.6 Cross-Format Descriptive Associations
Analyzing players with $\ge 50$ balls in both IPL and T20Is:

![Figure 12: Dual-Format Comparison](../step_8_eda/figures/fig12_format_comparison_dual_players.png)

- **Batting (Striker ID Disambiguated):** $N = 90$, Pearson $r = 0.1149$, Spearman $ho = 0.1645$.
- **Bowling (Zero Name Collisions):** $N = 97$, Pearson $r = 0.2338$, Spearman $ho = 0.2956$.

These modest correlations represent **unshrunk sample associations on small format slices** ($50 \le N \le 200$ balls), attenuated toward zero by delivery-level measurement variance (errors-in-variables attenuation bias). They confirm why Empirical Bayes shrinkage across full multi-competition careers is necessary.

---

## Section 8 — Final Official Player Rankings

### 8.1 Official Batting Leaderboard (Top 10 Under Pressure)

```
========================================================================================================================
Rank  Player                  Team / Franchise            Shrunk Score  Raw Score  Balls Faced  Kish ESS    95% Score CI
========================================================================================================================
1     Vaibhav Sooryavanshi    Rajasthan Royals (IPL/T20)    +0.3487     +0.7614        564        506.9  [+0.142, +0.523]
2     Suryakumar Yadav        India (IPL/T20I)              +0.2819     +0.3558       2638       2287.2  [+0.183, +0.370]
3     Abhishek Sharma         Sunrisers Hyderabad (IPL/T20) +0.2703     +0.3547       2195       1923.3  [+0.130, +0.399]
4     Tim David               Australia (IPL/T20I)          +0.2571     +0.4144       1163        980.6  [+0.129, +0.378]
5     Heinrich Klaasen        Sunrisers Hyderabad (IPL/T20) +0.2201     +0.3357       1409       1142.0  [+0.124, +0.307]
6     Phil Salt               England (IPL/T20I)            +0.1954     +0.2813       1591       1364.7  [+0.063, +0.303]
7     Namboori Tilak Varma    Mumbai Indians (IPL/T20I)     +0.1745     +0.2277       2338       1968.9  [+0.080, +0.267]
8     Travis Head             Sunrisers Hyderabad (IPL/T20) +0.1625     +0.2611       1096        988.6  [+0.002, +0.320]
9     Andre Russell           Kolkata Knight Riders (IPL/T) +0.1579     +0.3239        698        570.7  [+0.030, +0.285]
10    Reeza Hendricks         South Africa (T20I)           +0.1564     +0.2874        776        715.9  [+0.007, +0.287]
========================================================================================================================
```

### 8.2 Official Bowling Leaderboard (Top 10 Under Pressure)

```
========================================================================================================================
Rank  Player                  Team / Franchise            Shrunk Score  Raw Score  Balls Bowled Kish ESS    95% Score CI
========================================================================================================================
1     Rashid Khan             Gujarat Titans (IPL/T20I)     +0.1756     +0.2147       2648       2245.9  [+0.081, +0.278]
2     Jasprit Bumrah          Mumbai Indians (IPL/T20I)     +0.1541     +0.2103       1606       1369.7  [+0.024, +0.278]
3     Sunil Narine            Kolkata Knight Riders (IPL)   +0.1442     +0.2020       1464       1246.3  [+0.056, +0.233]
4     Josh Hazlewood          Royal Challengers Bengaluru   +0.1330     +0.1904       1368       1159.5  [+0.002, +0.283]
5     Wanindu Hasaranga       Sri Lanka (IPL/T20I)          +0.1184     +0.1537       1932       1675.4  [+0.036, +0.200]
6     Bhuvneshwar Kumar       Sunrisers Hyderabad (IPL/T20) +0.1065     +0.1349       2159       1875.7  [-0.009, +0.219]
7     Abrar Ahmed             Pakistan (T20I)               +0.1058     +0.1933        751        604.7  [-0.025, +0.228]
8     Kuldeep Yadav           Delhi Capitals (IPL/T20I)     +0.1027     +0.1346       1884       1608.6  [+0.008, +0.210]
9     Mahedi Hasan            Bangladesh (T20I)             +0.1025     +0.1700        860        760.3  [-0.044, +0.247]
10    Mujeeb Ur Rahman        Afghanistan (IPL/T20I)        +0.1024     +0.1770        772        686.6  [-0.012, +0.215]
========================================================================================================================
```

### 8.3 Placement of Marquee International & IPL Stars
To provide full transparency, where prominent stars rank in the frozen Step 7.4 evaluation:
- **Batters:** Shreyas Iyer (#14, $+0.1350$), Jos Buttler (#17, $+0.1306$), Mitchell Marsh (#19, $+0.1272$), Harry Brook (#30, $+0.0922$), Shubman Gill (#31, $+0.0921$), Virat Kohli (#34, $+0.0850$), Babar Azam (#38, $+0.0747$), Mohammad Rizwan (#42, $+0.0680$), Sanju Samson (#44, $+0.0665$), KL Rahul (#45, $+0.0655$), Pathum Nissanka (#51, $+0.0561$), Ravindra Jadeja (#121, $+0.0065$), Hardik Pandya (#130, $+0.0018$), Rishabh Pant (#154, $-0.0097$), Rohit Sharma (#168, $-0.0164$), Sam Curran (#189, $-0.0228$), Devdutt Padikkal (#284, $-0.0936$).
- **Bowlers:** Mohammed Shami (#13, $+0.0989$), Trent Boult (#16, $+0.0922$), Mitchell Santner (#37, $+0.0508$), Ravindra Jadeja (#45, $+0.0403$), Shaheen Shah Afridi (#46, $+0.0402$), Kagiso Rabada (#52, $+0.0344$), Mohammed Siraj (#61, $+0.0215$), Axar Patel (#66, $+0.0195$), Mitchell Starc (#203, $-0.0712$), Arshdeep Singh (#231, $-0.0926$), Sam Curran (#286, $-0.1688$).

---

## Section 9 — Limitations and Future Enhancements

A rigorous methodology must acknowledge its boundaries:
1. **Observed Reliability vs. Psychological "Clutch":** This system measures **observed performance under defined situational pressure**. It does not measure or claim the existence of a permanent, unobservable psychological trait called "clutch ability." A player's score reflects tactical skill, role execution, and situational performance.
2. **Residual Match-Environment Variance:** Factors such as pitch deterioration, dew, altitude, and ground boundary dimensions operate as unmodeled residual variance captured by the bootstrap standard errors rather than explicit model parameters.
3. **Cross-Format Extrapolation Risk:** The modest cross-format correlation ($r \approx 0.11$ to $0.23$) indicates that projecting a player's IPL pressure performance onto international tournament surfaces (or vice versa) carries intrinsic estimation uncertainty. Multi-competition career aggregation is required.
4. **Second-Innings Steep Chase Bias:** While capped by $\lambda_{\text{eff}} = \min(\lambda_{\text{wkt}}, R_{\text{req}})$, wicket valuations derived from first-innings baselines may slightly overestimate middle-order preservation costs during extreme chases exceeding 14 runs per over.

---

## Section 10 — Conclusion

The SupeRR Selector Round 1 reliability engine replaces unadjusted traditional statistics with an evidence-based, mathematically audited framework:
- **Objective Pressure:** Separates athletic difficulty from match consequence, eliminating outcome bias.
- **Contextual Baseline:** Normalizes against 36 empirical game situations and dynamic wicket valuations.
- **Statistical Discipline:** Applies Empirical Bayes shrinkage and block bootstrap resampling to protect against small-sample noise.

The resulting leaderboards provide tournament selectors, franchise management, and competition judges with an uncompromised, reproducible ranking of the **Most Reliable Players Under Pressure**.

---

## Technical Appendix & Authoritative Source Manifest

All claims, equations, and results in this report trace directly to certified project artifacts:

| Domain / Claim | Authoritative Project File | Verification Status |
|---|---|:---:|
| **Formal Pressure Model Design** | `outputs/step_3_formal_pressure_methodology/step_3_formal_pressure_methodology.md` | Certified (Step 3) |
| **Pipeline Implementation & Code** | `src/step_4_pressure_pipeline/` & `outputs/step_4_pressure_pipeline/` | Certified (Step 4) |
| **Mathematical Consistency Audit** | `outputs/step_6_reliability_methodology/step_6_3_final_mathematical_consistency_audit.md` | Certified (Step 6.3) |
| **Empirical Baseline Validation** | `outputs/step_7_empirical_calibration/step_7_1_baseline_validation_report.md` | Certified (Step 7.1) |
| **Wicket Valuation Surface** | `outputs/step_7_empirical_calibration/step_7_2_wicket_valuation/step_7_2_wicket_valuation_report.md` | Certified (Step 7.2) |
| **Shrinkage Calibration ($K=600, 500$)**| `outputs/step_7_empirical_calibration/step_7_3_shrinkage_pressure_calibration/` | Certified (Step 7.3) |
| **Final Player Rankings CSVs** | `outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_batting_rankings.csv` | Frozen (Step 7.4) |
| **Final Bowling Rankings CSVs** | `outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_bowling_rankings.csv` | Frozen (Step 7.4) |
| **Independent Ranking Audit** | `outputs/step_7_empirical_calibration/step_7_4_1_independent_audit/` | Certified (Step 7.4.1) |
| **Final Discrepancy Reconciliation** | `outputs/step_9_1_discrepancy_reconciliation/step_9_1_discrepancy_reconciliation.md` | Certified (Step 9.1) |
| **Finalized EDA Report** | `outputs/step_9_2_eda_finalization/step_9_2_final_eda_report.md` | Certified (Step 9.2) |

*End of Official Methodology Report.*
"""

with open('outputs/step_10_methodology_report/step_10_methodology_report.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("Generated outputs/step_10_methodology_report/step_10_methodology_report.md successfully.")
