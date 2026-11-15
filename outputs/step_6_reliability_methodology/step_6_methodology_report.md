# Step 6 — Player Reliability Methodology Design Report

**Project Target:** `experiments/pressure_definition_v1/`  
**Step:** Step 6 — Player Reliability Methodology Design  
**Deliverable File:** `outputs/step_6_reliability_methodology/step_6_methodology_report.md`  
**Input Datasets:**  
- `outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet` (186,780 deliveries, 816 batters)  
- `outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet` (186,780 deliveries, 589 bowlers)  
**Date:** November 2026  
**Status:** **METHODOLOGY DESIGN SPECIFICATION (DESIGN-ONLY PHASE)**

---

## 1. Executive Summary & Objective Alignment

The overarching objective of Round 1 of the SupeRR Selector competition is:

$$\mathbf{Identify \; the \; Most \; Reliable \; Players \; Under \; Pressure}$$

Having established, audited, and certified the objective pre-delivery pressure pipeline (`delivery_pressure_v3.parquet`, where $P = \sqrt{T \times L_{\text{norm}}} \in [0, 100]$) and reconciled the player-level delivery datasets (`Step 5`), the task of Step 6 is to design a mathematically sound, statistically defensible, and interpretable methodology to evaluate how reliably individual batters and bowlers perform when confronted with pressure.

### Core Methodological Principles

1. **Independent Batting and Bowling Architectures:**
   Batting and bowling are structurally asymmetric disciplines. A batter faces non-linear ruin risk (a single dismissal ends their innings permanently), whereas a bowler delivers discrete spells across multiple overs where containment and wicket-taking interact. Batting and bowling reliability cannot be forced into a single symmetric formula.
2. **Efficiency Above Situational Par (Not Volume):**
   Reliability does not mean accumulating the most raw runs or bowling the most overs. A player who faces 400 balls in comfortable situations at a mediocre strike rate is not reliable under pressure. Reliability measures the capacity to **consistently deliver positive performance relative to situational expectations under elevated pressure**.
3. **Situational Baseline Conditioning:**
   Performance must be benchmarked against an empirical situational par $\mathbb{E}[Y \mid \text{state}]$. A single taken against an unhittable yorker at $P=85$ in the death overs is a positive play; a dot ball in the same situation is a failure.
4. **Bayesian Regularization Over Ad-Hoc Penalties:**
   Small-sample distortion (e.g. a batter facing 15 balls and hitting 3 sixes) is resolved using formal **Empirical Bayes Shrinkage** toward cohort role-priors, rather than arbitrary division factors ($outs + 1$) or arbitrary hard thresholds.
5. **Transparency and Interpretability:**
   Complex black-box machine learning models are rejected in favor of auditable, transparent statistical formulations with clear physical and cricketing interpretations.

---

## 2. Conceptual Foundation: Defining Reliability Under Pressure

In classical statistical reliability theory, reliability is defined as the consistency of measurement or performance under stress. In Twenty20 cricket, a player's reliability under pressure comprises two complementary, quantifiable dimensions:

$$\text{Reliability} = \text{Execution Efficiency Under Stress} \times \text{Consistency (Low Failure Rate)}$$

```
                            Player Reliability Architecture
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
      Execution Efficiency                            Consistency & Resilience
  (Performance Above Situational Par)             (Stability Across Pressure Tiers)
                 │                                               │
  • Net Run Value Added (RVA)                     • Low Performance Drop-off (Slope)
  • Boundary Generation / Prevention              • Downside Failure Rate Minimization
  • Wicket Value / Strike Efficiency              • Inter-Match Variance Regularization
```

### 2.1 The Two Fundamental Measurement Pitfalls

1. **The Volume Fallacy:** Rewarding players simply for having more opportunities. Openers face $\approx 35\%$ of all match deliveries; death bowlers bowl $\approx 20\%$ of match overs. An unadjusted cumulative sum rewards role opportunity rather than execution quality.
2. **The Small-Sample Outlier Trap:** Evaluating players purely on unweighted rates (e.g. strike rate or economy rate) without shrinkage rewards small-sample volatility. A tail-ender who hits 16 runs off 4 balls in one high-pressure finish has an infinite high-pressure strike rate (400.0) but zero proven reliability.

---

## 3. Proposed Batting Reliability Framework

### 3.1 Defining Batting Success and Failure Under Pressure

On any given delivery $t$, a batter facing pressure $P_t$ produces an outcome characterized by runs scored $r_t \in \{0, 1, 2, 3, 4, 6\}$ and dismissal status $w_t \in \{0, 1\}$. 

Success and failure cannot be judged by runs alone:
- **Failure:** A dot ball when the required rate is high; a dismissal that collapses team batting capital; consuming balls without rotating strike.
- **Success:** Hitting boundaries to relieve required rate pressure; rotating strike off difficult deliveries; preserving wicket capital during early collapses.

### 3.2 Candidate Batting Models

We propose and evaluate two primary candidate models:

---

#### Candidate Batting Model A: Pressure-Weighted Situational Value Added (PWSVA)

Model A evaluates each delivery relative to the empirical situational run expectation $\mathbb{E}[R \mid \text{state}_t]$ and situational dismissal risk $\mathbb{E}[W \mid \text{state}_t]$, weighted by continuous delivery pressure $P_t$:

$$V_{\text{bat}, t} = (r_t - \mathbb{E}[R \mid \text{state}_t]) - \lambda_{\text{wkt}}(\text{state}_t) \cdot (w_t - \mathbb{E}[W \mid \text{state}_t])$$

Where:
- $r_t$: Runs scored off the bat by the striker on delivery $t$.
- $\mathbb{E}[R \mid \text{state}_t]$: Expected runs scored on delivery $t$ by an average batter in that exact phase, innings, and pressure decile.
- $w_t \in \{0, 1\}$: Striker dismissal indicator (`is_striker_dismissed`).
- $\mathbb{E}[W \mid \text{state}_t]$: Expected probability of a striker dismissal in that exact state.
- $\lambda_{\text{wkt}}(\text{state}_t)$: The situational run-equivalent value of a wicket, derived from the resource loss curve:
  $$\lambda_{\text{wkt}}(\text{state}_t) = \frac{\partial \text{Total Runs}}{\partial W} \approx \frac{V_{\text{par}} - \text{score}_t}{W_{\text{rem}, t}}$$
  In the Powerplay with 8 wickets in hand, a wicket is worth $\approx 18.0$ runs of team capital. In the 20th over with 2 balls remaining, a wicket is worth $\approx 1.5$ runs.

The player's raw pressure-weighted performance across $N$ deliveries is:

$$\text{PWSVA}_i = \frac{\sum_{t=1}^{N_i} w(P_t) \cdot V_{\text{bat}, t}}{\sum_{t=1}^{N_i} w(P_t)}$$

Where $w(P_t) = \left(\frac{P_t}{50.0}\right)^\alpha$ is the pressure weighting function ($\alpha \ge 1.0$).

---

#### Candidate Batting Model B: Stratified Pressure Resilience Index (SPRI)

Model B partitions deliveries into three standardized diagnostic pressure bands:
- **Low / Par Pressure:** $P_t \le 45.0$ (Baseline accumulation)
- **Moderate Pressure:** $45.0 < P_t \le 65.0$ (Standard competitive tension)
- **High / Climax Pressure:** $P_t > 65.0$ (High consequence and severe task difficulty)

The model computes:
1. **High-Pressure Execution Index ($HPE_i$):** Net run-rate efficiency and survival rate within the high-pressure band ($P > 65$).
2. **Pressure Resilience Slope ($\beta_{\text{resilience}, i}$):** The regression slope of delivery efficiency against pressure:
   $$V_{\text{bat}, t} = \alpha_i + \beta_{\text{resilience}, i} \cdot P_t + \epsilon_t$$
   - $\beta > 0$: Batter's performance **elevates** as pressure rises (clutch performer).
   - $\beta \approx 0$: Batter's performance is **invariant** to pressure (unshakable anchor).
   - $\beta < 0$: Batter's performance **deteriorates** as pressure rises (choke tendency).
3. **Consistency Factor ($C_i$):** $1 - \text{CV}(V_{\text{bat}})$, penalizing erratic boom-or-bust variance across matches.

The composite Stratified Pressure Resilience Index is:

$$\text{SPRI}_i = \left( HPE_i \times (1 + \tanh(\beta_{\text{resilience}, i})) \times C_i \right)_{\text{shrunk}}$$

---

### 3.3 Worked Hypothetical Batting Example

Consider three batters facing high-pressure death overs ($P_t = 75.0$, baseline par $\mathbb{E}[R] = 1.35$ runs/ball, $\mathbb{E}[W] = 0.08$ outs/ball, $\lambda_{\text{wkt}} = 3.5$ runs):

| Delivery Sequence | Batter A (Elite Finisher) | Batter B (Volatile Hitter) | Batter C (Sub-Par Accumulator) |
| :---: | :---: | :---: | :---: |
| **Ball 1** | 2 runs ($+0.65$) | 0 runs ($-1.35$) | 1 run ($-0.35$) |
| **Ball 2** | 4 runs ($+2.65$) | 6 runs ($+4.65$) | 1 run ($-0.35$) |
| **Ball 3** | 1 run ($-0.35$) | 0 runs ($-1.35$) | 0 runs ($-1.35$) |
| **Ball 4** | 6 runs ($+4.65$) | 6 runs ($+4.65$) | 1 run ($-0.35$) |
| **Ball 5** | 2 runs ($+0.65$) | Out ($-1.35 - 3.22 = -4.57$) | 2 runs ($+0.65$) |
| **Ball 6** | 4 runs ($+2.65$) | 0 runs ($-1.35$) | Out ($-1.35 - 3.22 = -4.57$) |
| **Total Runs / Outs** | **19 runs (0 outs)** | **12 runs (1 out)** | **5 runs (1 out)** |
| **Strike Rate** | **316.7** | **200.0** | **83.3** |
| **Net Value Added ($\sum V$)** | **$+10.90\text{ runs}$** | **$-0.68\text{ runs}$** | **$-7.32\text{ runs}$** |
| **Reliability Verdict** | **Exceptional (+1.82 runs/ball)** | **Negative (-0.11 runs/ball)** | **Severely Unreliable (-1.22)** |

**Insight:** Batter B hit two sixes (SR 200), but through three dot balls and a dismissal, consumed scarce balls and produced net-negative value relative to situational death par. The value-added formulation correctly identifies Batter A as reliable and rejects Batter B.

---

## 4. Proposed Bowling Reliability Framework

### 4.1 Defining Bowling Success and Failure Under Pressure

A bowler facing high pressure $P_t$ seeks to:
1. **Suppress Scoring:** Prevent runs from reaching the batting side.
2. **Generate Dots:** Deny scoring shots ($66,047$ dots in cohort).
3. **Take Wickets:** Permanently terminate opposition batting capital.
4. **Prevent Boundaries:** Deny high-leverage 4s and 6s.
5. **Maintain Discipline:** Avoid unforced extras (wides and no-balls) that grant free runs and free deliveries.

### 4.2 Candidate Bowling Models

---

#### Candidate Bowling Model A: Situational Bowling Value Added (SBVA)

Model A evaluates the net runs saved and wickets gained on delivery $t$ relative to situational expectation:

$$V_{\text{bowl}, t} = (\mathbb{E}[R_{\text{bowl}} \mid \text{state}_t] - r_{\text{conceded}, t}) + \lambda_{\text{wkt}}(\text{state}_t) \cdot (w_{\text{bowler}, t} - \mathbb{E}[W_{\text{bowler}} \mid \text{state}_t]) - \text{Penalty}_{\text{extra}, t}$$

Where:
- $r_{\text{conceded}, t}$: Runs debited to the bowler (`bowler_runs_conceded`).
- $\mathbb{E}[R_{\text{bowl}} \mid \text{state}_t]$: Expected runs conceded in that phase, innings, and pressure decile.
- $w_{\text{bowler}, t} \in \{0, 1\}$: Standard bowler-credited wicket indicator (`is_bowler_wicket`: Caught, Bowled, LBW, Stump, Hit Wicket). Run-outs are **not** credited here.
- $\text{Penalty}_{\text{extra}, t}$: An unforced extras penalty applied to wides ($1.0 + \mathbb{E}[R_{\text{re-bowl}}]$) and no-balls ($1.0 + \mathbb{E}[R_{\text{free-hit}}]$).

The player's pressure-weighted bowling value across $M_i$ legal deliveries is:

$$\text{SBVA}_i = \frac{\sum_{t=1}^{D_i} w(P_t) \cdot V_{\text{bowl}, t}}{\sum_{t=1}^{D_i} w(P_t) \cdot \mathbb{I}(\text{legal}_t)}$$

---

#### Candidate Bowling Model B: Pressure Execution Index (PEI)

Model B constructs a multi-component execution rating across high-pressure deliveries ($P_t > 65.0$):

$$\text{PEI}_i = \theta_1 \cdot \text{DotRateRelPar}_i + \theta_2 \cdot \text{BoundarySuppressionRelPar}_i + \theta_3 \cdot \text{StrikeRateRelPar}_i - \theta_4 \cdot \text{ExtrasRate}_i$$

Where each component is standardized relative to the phase expectation:
- $\text{DotRateRelPar} = \frac{\text{Observed Dot \%}}{\mathbb{E}[\text{Dot \%} \mid \text{Phase}]}$
- $\text{BoundarySuppressionRelPar} = \frac{\mathbb{E}[\text{Boundary \%} \mid \text{Phase}]}{\max(0.01, \text{Observed Boundary \%})}$
- $\text{StrikeRateRelPar} = \frac{\text{Wickets Taken} / \text{Balls}}{\mathbb{E}[\text{Wickets} / \text{Ball} \mid \text{Phase}]}$
- $\text{ExtrasRate} = \frac{\text{Wides} + \text{No-Balls}}{\text{Total Deliveries}}$

---

### 4.3 Worked Hypothetical Bowling Example

Consider two bowlers delivering Over 19 defending 16 runs ($P_t = 82.0$, baseline death par: $\mathbb{E}[R_{\text{bowl}}] = 1.80$ runs/ball, $\mathbb{E}[W_{\text{bowl}}] = 0.12$ wkts/ball, $\lambda_{\text{wkt}} = 3.5$ runs):

| Delivery Sequence | Bowler A (Execution Specialist) | Bowler B (Volatile Strike Bowler) |
| :---: | :---: | :---: |
| **Ball 1** | Dot ($1.80 - 0 = +1.80$) | 6 conceded ($1.80 - 6 = -4.20$) |
| **Ball 2** | 1 run ($1.80 - 1 = +0.80$) | Wide ($1.80 - 2.50 = -0.70$) |
| **Ball 3** | Dot ($1.80 - 0 = +1.80$) | Dot ($1.80 - 0 = +1.80$) |
| **Ball 4** | 2 runs ($1.80 - 2 = -0.20$) | Wicket ($1.80 - 0 + 3.08 = +4.88$) |
| **Ball 5** | 1 run ($1.80 - 1 = +0.80$) | 4 conceded ($1.80 - 4 = -2.20$) |
| **Ball 6** | Wicket ($1.80 - 0 + 3.08 = +4.88$) | 1 run ($1.80 - 1 = +0.80$) |
| **Ball 7 (re-bowled)**| N/A | 4 conceded ($1.80 - 4 = -2.20$) |
| **Figures** | **1.0 over, 4 runs, 1 wicket** | **1.0 over, 17 runs, 1 wicket (1 wide)** |
| **Match Result** | **Won match (defended 16)** | **Lost match (conceded 17)** |
| **Net Value Added ($\sum V$)** | **$+9.88\text{ runs}$** | **$-1.82\text{ runs}$** |
| **Reliability Verdict** | **Elite (+9.88 runs saved)** | **Unreliable (-1.82 runs conceded)** |

**Insight:** Bowler B took a wicket, but conceded two boundaries and a wide, losing the match. Bowler A executed with discipline, suffocating the chase. Model A cleanly separates the two.

---

## 5. Baseline Selection Methodology

To avoid phase and match-state bias, every delivery must be compared against a **conditional expectation baseline**.

### 5.1 Stratified Empirical Par Surfaces
The baseline expectation is estimated non-parametrically across the certified 186,780-delivery cohort using multi-way stratification:

$$\mathbb{E}[Y \mid \text{state}_t] = \text{Lookup}(\text{Innings}, \text{Phase}, \text{PressureDecile})$$

Where $Y \in \{r_{\text{batter}}, r_{\text{bowler}}, w_{\text{striker}}, w_{\text{bowler}}, \text{is\_boundary}, \text{is\_dot}\}$:

```
                          Baseline Stratification Tensor
    ┌────────────────────────────────────────────────────────────────────────┐
    │  Innings:      { Innings 1 (Defending), Innings 2 (Chasing) }          │
    │  Phase:        { Powerplay (1-6), Middle (7-16), Death (17-20) }        │
    │  Pressure:     { Deciles D1 through D10 based on P_bat / P_bowl }      │
    │  Cell Samples: Minimum N >= 1,500 deliveries per cell                  │
    └────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Why Continuous Regression Surfaces are Rejected
We considered fitting a multi-variable Poisson or Negative Binomial regression for $\mathbb{E}[R \mid S_t, L_t, W_t, P_t]$. However:
1. Parametric assumptions (e.g. log-linear rate scaling) distort extreme death-over boundary clusters.
2. Stratified empirical binning guarantees that $\sum_{t=1}^N (Y_t - \mathbb{E}[Y \mid \text{state}_t]) \equiv 0$ across every stratum, eliminating structural bias between phases.

---

## 6. Sample-Size, Uncertainty & Bayesian Shrinkage Treatment

### 6.1 The Sample-Size Spectrum in the Cohort
The Step 5 audit demonstrated significant variance in exposure across players:
- **Batters:** Total balls faced ranges from $1$ to $2,674$. Under high pressure ($P > 60$), balls faced ranges from $1$ to $480$.
  - Batters with $\ge 100$ high-pressure balls: $144$ players.
  - Batters with $\ge 50$ high-pressure balls: $233$ players.
- **Bowlers:** Legal deliveries bowled ranges from $1$ to $2,683$. Under high pressure ($P > 60$), legal balls ranges from $1$ to $420$.
  - Bowlers with $\ge 100$ high-pressure legal balls: $139$ players.
  - Bowlers with $\ge 50$ high-pressure legal balls: $222$ players.

### 6.2 Empirical Bayes Shrinkage Formulation
To prevent small-sample specialists from dominating rankings without discarding valuable sample information, all player estimates must undergo **Empirical Bayes Shrinkage**:

$$\theta_i^{\text{shrunk}} = \frac{N_{\text{eff}, i}}{N_{\text{eff}, i} + K} \cdot \hat{\theta}_i + \frac{K}{N_{\text{eff}, i} + K} \cdot \mu_{\text{prior}}$$

Where:
- $\hat{\theta}_i$: The observed sample efficiency metric (e.g. $\text{PWSVA}_i$ or $\text{SBVA}_i$).
- $N_{\text{eff}, i} = \sum_{t=1}^{N_i} \left(\frac{P_{i,t}}{50.0}\right)$: The effective pressure-weighted sample size.
- $\mu_{\text{prior}}$: The cohort prior mean ($\mu \equiv 0.0$ for value-added metrics).
- $K$: The empirical shrinkage constant, representing the number of pseudo-deliveries required to pull a player halfway between the prior and their sample mean.

### 6.3 Derivation of Shrinkage Constant $K$
Under the James-Stein / Empirical Bayes framework, $K$ is estimated directly from the ratio of expected within-player sampling variance ($\sigma_{\text{within}}^2$) to true between-player variance ($\sigma_{\text{between}}^2$):

$$K = \frac{\mathbb{E}[\sigma_{\text{within}}^2]}{\sigma_{\text{between}}^2}$$

**Provisional Design Thresholds for Testing in Step 7:**
- **Batting Shrinkage Prior:** $K_{\text{bat}} \in [60, 100]$ effective deliveries.
- **Bowling Shrinkage Prior:** $K_{\text{bowl}} \in [60, 100]$ effective legal deliveries.
- **Minimum Qualification Filter:** Players must have faced or bowled at least **$50$ actual deliveries under pressure ($P > 50$)** to receive an official competition ranking, ensuring that reported ratings have at least $35\%$ sample evidence weight.

---

## 7. Fairness, Role Adjustments & Bias Controls

### 7.1 Batting Order Bias
- **The Issue:** Openers face the new ball in Powerplays against fresh fast bowlers with fielding restrictions; middle-order batters face spin during consolidation; finishers face defensive yorkers and boundary fields at the death.
- **Control:** By subtracting situational par $\mathbb{E}[R \mid \text{phase}, \text{innings}, P]$ at the delivery level, each player is evaluated against peers in that exact match segment. A finisher who scores at $11.0$ RPO when par is $10.5$ RPO gains $+0.5$ RPO. An opener who scores at $8.5$ RPO when par is $7.5$ RPO gains $+1.0$ RPO. Neither role has an unfair structural advantage.

### 7.2 Bowling Phase Bias
- **The Issue:** Death bowlers have higher raw economy rates ($10.5+$ RPO) than middle-overs spinners ($7.5$ RPO). Raw economy heavily biases against death bowlers.
- **Control:** Expected runs conceded $\mathbb{E}[R_{\text{bowl}}]$ is phase-specific. A death bowler conceding $9.0$ RPO gains $+1.5$ runs saved per over. A middle-overs bowler conceding $8.5$ RPO loses $-1.0$ run per over.

### 7.3 Innings Asymmetry (Defending vs. Chasing)
- **The Issue:** In Innings 2, pressure is dictated by required run rate and balls remaining; in Innings 1, pressure is dictated by par trajectory.
- **Control:** Stratification separates Innings 1 and Innings 2 baselines, preserving tournament balance.

### 7.4 Unequal Opportunities & Selection Bias
- **The Issue:** Elite players are trusted by captains to bowl the 19th over or bat in collapses. Average players are protected.
- **Control:** Effective sample weighting $N_{\text{eff}} = \sum (P/50)$ ensures that a player who faces 100 balls at $P=80$ accumulates $160$ effective deliveries, appropriately reflecting their heavy situational responsibility.

---

## 8. Comprehensive Validation Strategy (For Step 7)

To ensure that the recommended methodology is not overfitted, Step 7 must execute the following validation suite:

1. **Split-Half Reliability ($r_{\text{odd/even}}$):**
   Partition each player's deliveries into odd and even match dates. Compute the correlation $r_{\text{split}}$ of the resulting reliability metrics. A reliable metric must demonstrate $r_{\text{split}} \ge 0.65$.
2. **Phase-Invariance Test:**
   Regress player reliability scores against the proportion of balls bowled/faced in the death overs. The correlation must be negligible ($|r| < 0.15$), confirming that role bias has been eradicated.
3. **Sensitivity Analysis on Shrinkage Prior $K$:**
   Vary $K \in \{40, 60, 80, 100, 120\}$. Confirm that player rankings remain rank-stable (Spearman $\rho \ge 0.95$).
4. **Predictive Validity:**
   Train reliability parameters on the first $60\%$ of chronological matches and test whether top-decile reliable players outperform bottom-decile players in the remaining $40\%$ under high pressure.

---

## 9. Alternative Approaches Considered and Rejected

| Methodology Considered | Core Mathematical Concept | Reason for Rejection |
| :--- | :--- | :--- |
| **Legacy BRS3 / BoRS** | Raw Strike Rate $\times$ Pressure Index with $K=50$ shrinkage | **Mathematically flawed.** Compounded volume and phase bias; rewarded death hitters regardless of situational par; double-counted pressure. |
| **Raw Win Probability Added (WPA)** | $\sum (\text{WP}_{t+1} - \text{WP}_t)$ | **State-dependent distortion.** Over-rewards trivial boundary hits when $\text{WP}$ is balanced ($50\%$) and under-rewards clutch play in blowouts. High match-context noise. |
| **Raw Strike Rate / Economy at $P > 60$** | $\frac{\text{Runs}}{\text{Balls}} \times 100$ | **Severe sample-size distortion.** Rewards small-sample outliers (e.g. 15 balls, SR 220) and ignores dismissals and baseline phase difficulty. |
| **Complex Black-Box ML (XGBoost/NN)** | Gradient boosting on player IDs | **Uninterpretable and overfitted.** Cannot explain why a player ranks 4th vs 12th; creates tournament gaming and opacity. |

---

## 10. Remaining Methodological Decisions & Step 7 Roadmap

The following design parameters are designated as **provisional** and must be empirically calibrated in Step 7:

1. **Calibration of $\lambda_{\text{wkt}}$:** Test whether situational resource loss ($\frac{V_{\text{par}} - S_t}{W_{\text{rem}}}$) or empirical cohort run-loss per wicket produces higher split-half reliability.
2. **Empirical Determination of $K_{\text{bat}}$ and $K_{\text{bowl}}$:** Fit $K$ directly from between-player variance using maximum likelihood across the 782-match cohort.
3. **Pressure Weighting Power $\alpha$:** Test $\alpha = 1.0$ (linear) vs. $\alpha = 1.5$ (super-linear emphasis on climax pressure).
4. **Minimum Delivery Eligibility:** Evaluate thresholds of $N \ge 40$, $N \ge 50$, and $N \ge 60$ high-pressure balls to maximize player coverage while preserving metric stability.

---

## 11. Final Methodological Determination

The recommended methodology for Round 1 of the SupeRR Selector competition is:

$$\mathbf{Pressure\text{-}Weighted \; Situational \; Value \; Added \; (PWSVA) \; with \; Empirical \; Bayes \; Shrinkage}$$

It directly solves the competition objective:
- It eliminates role and phase bias through empirical situational baselines.
- It separates execution efficiency from mere opportunity.
- It protects against small-sample noise through formal Bayesian regularization.
- It is transparent, interpretable, and reproducible.

$$\mathbf{STEP \; 6 \; DESIGN: \quad COMPLETE \; \& \; READY \; FOR \; STEP \; 7 \; TESTING}$$

---
*Report certified by Antigravity Autonomous Scientific Methodology Team.*
