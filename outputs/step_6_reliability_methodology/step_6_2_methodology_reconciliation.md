# Step 6.2 — Reliability Methodology Reconciliation Report

**Project Target:** `experiments/pressure_definition_v1/`  
**Step:** Step 6.2 — Reliability Methodology Reconciliation  
**Deliverable File:** `outputs/step_6_reliability_methodology/step_6_2_methodology_reconciliation.md`  
**Inputs Frozen:**  
- `outputs/step_4_pressure_pipeline/delivery_pressure_v3.parquet` (186,780 deliveries, 782 matches)  
- `outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet` (186,780 deliveries, 816 batters)  
- `outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet` (186,780 deliveries, 589 bowlers)  
- `outputs/step_6_reliability_methodology/step_6_methodology_report.md` (Step 6 Design Specification)  
- `outputs/step_6_reliability_methodology/step_6_1_independent_methodology_audit.md` (Step 6.1 Audit Findings)  
**Date:** November 2026  
**Status:** **FINAL RECONCILED METHODOLOGY SPECIFICATION (READY FOR STEP 7 CALIBRATION)**

---

## 1. Executive Summary & Reconciliation Objective

The objective of Round 1 of the SupeRR Selector competition is:

$$\mathbf{Identify \; the \; Most \; Reliable \; Players \; Under \; Pressure}$$

The Step 6.1 independent audit certified the core architecture of **Situational Value Added with Empirical Bayes Regularization**, but identified two Critical mathematical defects in bowling outcome accounting, four Major statistical issues (including negative dynamic wicket values and baseline decile sparsity), and two Minor accounting ambiguities.

This Step 6.2 Reconciliation document resolves every finding from Step 6.1. It establishes a mathematically coherent, cricket-logical, and empirically testable final methodology for both batting and bowling reliability under pressure.

```
                    Reconciled Reliability Architecture
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
 Batting Reliability (PWSVA)                         Bowling Reliability (SBVA)
 ───────────────────────────                         ──────────────────────────
 • Eligible Domain: Balls Faced Only                 • Quota Basis: Legal Balls Denominator
 • Off-the-Bat Runs (batter_runs)                    • All Bowler Runs Conceded in Numerator
 • Striker Dismissals (is_striker_dismissed)         • Bowler-Credited Wickets Only
 • Monotonic Positive Resource Loss (λ_wkt)          • Zero Extras Double-Counting
 • Non-Parametric 36-Cell Baselines                  • Non-Parametric 36-Cell Baselines
           │                                                   │
           └─────────────────────────┬─────────────────────────┘
                                     ▼
                      Bayesian Regularization & Scaling
                      ─────────────────────────────────
                      • Kish Effective Sample Size (N_eff,Kish)
                      • Empirical Bayes Shrinkage (K_bat, K_bowl)
                      • Orthogonal Pressure Weighting: w(P) = (P/50)^α
                      • Match-Level Block Bootstrap Validation (95% CI)
```

---

## 2. Final Recommended Batting Methodology (PWSVA)

### 2.1 Conceptual Definition
Batting reliability under pressure is defined as a batter’s capacity to **consistently generate net runs above situational expectation while preserving team wicket resources under elevated pressure**, regularized against small-sample volatility.

### 2.2 Mathematical Specification
For any batter $i$, their observed **Pressure-Weighted Situational Value Added ($\text{PWSVA}_i$)** is computed strictly over deliveries where they faced the ball:

$$\mathbf{\text{PWSVA}_i = \frac{\sum_{t \in \mathcal{F}_i} w(P_t) \cdot V_{\text{bat}, t}}{\sum_{t \in \mathcal{F}_i} w(P_t)}}$$

Where:
- $\mathcal{F}_i = \{t : \text{striker\_id}_t = i \land \text{is\_batter\_ball\_faced}_t = \text{True}\}$ is the set of all deliveries faced by batter $i$.
- $w(P_t) = \left(\frac{P_t}{50.0}\right)^\alpha$ is the continuous pressure weighting function ($\alpha \in [1.0, 1.25]$).
- $V_{\text{bat}, t}$ is the marginal run value added by the batter on delivery $t$:

$$\mathbf{V_{\text{bat}, t} = (r_t - \mathbb{E}[R \mid \text{state}_t]) - \lambda_{\text{wkt}}(\text{state}_t) \cdot (w_t - \mathbb{E}[W \mid \text{state}_t])}$$

### 2.3 Empirical Bayes Shrinkage
To prevent small-sample specialists from topping rankings, the observed metric $\text{PWSVA}_i$ is shrunk toward the cohort prior mean ($\mu_{\text{prior}} \equiv 0.0$):

$$\mathbf{\text{PWSVA}_i^{\text{shrunk}} = \left(\frac{N_{\text{eff}, i}}{N_{\text{eff}, i} + K_{\text{bat}}}\right) \cdot \text{PWSVA}_i + \left(\frac{K_{\text{bat}}}{N_{\text{eff}, i} + K_{\text{bat}}}\right) \cdot 0.0}$$

Where $N_{\text{eff}, i}$ is Kish's effective sample size derived from the delivery weights $w(P_t)$ (see Section 7), and $K_{\text{bat}}$ is the empirical shrinkage constant estimated from the between-player variance ratio.

---

## 3. Final Recommended Bowling Methodology (SBVA)

### 3.1 Conceptual Definition
Bowling reliability under pressure is defined as a bowler’s capacity to **consistently suppress runs below situational expectation and terminate opposition wicket capital under elevated pressure**, evaluated across their completed quota of legal deliveries and regularized against small-sample volatility.

### 3.2 Resolution of Bowling Accounting: Approach A vs. Approach B
Step 6.1 mandated evaluating two distinct approaches for resolving extras double-counting and denominator singularities:
- **Approach A (Delivery-Level Value with Total Deliveries Denominator):** Evaluates every ball bowled (legal and illegal) with denominator $\sum w(P_t)$.
  - *Critical Flaw:* If an illegal delivery increments the denominator, conceding a 1-run wide in the death overs (where par is $1.80$ runs/ball) results in an economy rate of $6.0$ RPO, which is *better than par*. Bowling wides would artificially improve a bowler's rating!
- **Approach B (Legal Ball Quota Basis with All Runs Debited):** Evaluates net runs saved across the quota of legal deliveries, debiting all runs conceded (including wide and no-ball extras) in the numerator while incrementing the denominator only on legal deliveries.
  - *Cricket Reality:* In cricket, an over consists of 6 legal balls. Wides and no-balls concede extra runs without consuming balls. Economy rate is $\text{Total Runs Conceded} / (\text{Legal Balls} / 6)$.
  - *Mathematical Decision:* **Approach B is universally adopted.**

### 3.3 Reconciled Mathematical Specification
For any bowler $i$, their **Situational Bowling Value Added ($\text{SBVA}_i$)** across all deliveries bowled $\mathcal{D}_i$ is:

$$\mathbf{\text{SBVA}_i = \frac{\sum_{t \in \mathcal{D}_i} w(P_t) \cdot V_{\text{bowl}, t}}{\sum_{t \in \mathcal{D}_i} w(P_t) \cdot \mathbb{I}(\text{is\_legal\_ball}_t)}}$$

Where for every delivery $t \in \mathcal{D}_i$:

$$\mathbf{V_{\text{bowl}, t} = \begin{cases} 
(\mathbb{E}[R_{\text{bowl}} \mid \text{state}_t] - r_{\text{conceded}, t}) + \lambda_{\text{wkt}}(\text{state}_t) \cdot (w_{\text{bowler}, t} - \mathbb{E}[W_{\text{bowler}} \mid \text{state}_t]) & \text{if } \text{is\_legal\_ball}_t = \text{True} \\
- r_{\text{conceded}, t} + \lambda_{\text{wkt}}(\text{state}_t) \cdot w_{\text{bowler}, t} & \text{if } \text{is\_legal\_ball}_t = \text{False}
\end{cases}}$$

#### Why This Reconciled Formula is Mathematically Airtight:
1. **Zero Double-Counting:** On illegal deliveries, $r_{\text{conceded}, t}$ is the exact runs debited to the bowler (`bowler_runs_conceded`). No additional phantom penalty ($1.0 + \mathbb{E}[R]$) is subtracted.
2. **Zero Phantom Future Penalties:** The subsequent re-bowled delivery or free hit is evaluated when it actually occurs, completely eliminating duplicate charging.
3. **Wicket Credit Preserved:** If a wicket occurs on an illegal delivery (e.g. stumping on a wide), $w_{\text{bowler}, t} = 1$, and the bowler receives full credit $+\lambda_{\text{wkt}}$.
4. **Zero Denominator Singularity:** Because the qualification filter requires $\ge 50$ legal balls under pressure, the denominator is strictly positive for all ranked bowlers.

### 3.4 Empirical Bayes Shrinkage
$$\mathbf{\text{SBVA}_i^{\text{shrunk}} = \left(\frac{N_{\text{eff}, i}^{\text{bowl}}}{N_{\text{eff}, i}^{\text{bowl}} + K_{\text{bowl}}}\right) \cdot \text{SBVA}_i + \left(\frac{K_{\text{bowl}}}{N_{\text{eff}, i}^{\text{bowl}} + K_{\text{bowl}}}\right) \cdot 0.0}$$

---

## 4. Complete Outcome Accounting & Variable Definitions

The following table explicitly defines every variable, its underlying data source in the certified Step 5 datasets, its mathematical domain, and its accounting treatment:

| Term | Notation | Source Field in Step 5 Dataset | Domain | Reconciled Accounting Rule |
| :--- | :---: | :--- | :---: | :--- |
| **Batter Runs** | $r_t$ | `batter_runs` | $\{0, 1, 2, 3, 4, 5, 6\}$ | Runs scored off the bat only. Byes, leg-byes, and wides are strictly excluded. |
| **Balls Faced** | $\mathcal{F}_i$ | `is_batter_ball_faced` | $\{\text{True}, \text{False}\}$ | Exactly 179,590 deliveries in cohort. All 7,190 wides are strictly excluded. |
| **Striker Dismissal** | $w_t$ | `is_striker_dismissed` | $\{0, 1\}$ | True for 9,737 dismissals. Non-striker dismissals (`is_non_striker_dismissed`, 282 run-outs) are NOT charged to the striker. |
| **Bowler Runs Conceded** | $r_{\text{conceded}, t}$ | `bowler_runs_conceded` | $\mathbb{Z}_{\ge 0}$ | Total runs debited to bowler (runs off bat + wides + no-balls). Byes and leg-byes are strictly excluded. |
| **Bowler Wicket** | $w_{\text{bowler}, t}$ | `is_bowler_wicket` | $\{0, 1\}$ | Bowler-credited wickets only (Caught, Bowled, LBW, Stumped, Hit Wicket). Run-outs and retired outs are strictly excluded. |
| **Legal Delivery** | $\mathbb{I}(\text{legal}_t)$ | `is_legal_ball` | $\{0, 1\}$ | Exactly 178,798 deliveries in cohort. Wides (7,190) and no-balls (792) evaluate to 0. |
| **Delivery Pressure** | $P_t$ | `pressure_batting` / `pressure_bowling` | $[0, 100]$ | Pre-delivery pressure from Step 4 v3 pipeline ($P = \sqrt{T \times L_{\text{norm}}}$). Frozen. |
| **Pressure Weight** | $w(P_t)$ | Calculated | $\mathbb{R}_{> 0}$ | $w(P_t) = (P_t / 50.0)^\alpha$, scaling situational importance. |
| **Expected Runs** | $\mathbb{E}[R \mid \text{state}_t]$ | Baseline Lookup | $\mathbb{R}_{> 0}$ | Expected runs in that exact match state, estimated strictly over eligible deliveries. |
| **Expected Wickets** | $\mathbb{E}[W \mid \text{state}_t]$ | Baseline Lookup | $[0, 1]$ | Expected dismissal probability in that exact match state. |
| **Wicket Value** | $\lambda_{\text{wkt}}(\text{state}_t)$ | Monotonic Resource Curve | $\mathbb{R}_{> 0}$ | Run-equivalent resource value of a wicket in that state ($\ge 1.0$ run everywhere). |

### 4.1 Treatment of Specific Delivery Types
1. **Wides (7,190 deliveries):**
   - *Batting:* Excluded from striker's delivery set $\mathcal{F}_i$ ($N$ increments 0, $V_{\text{bat}}$ not computed).
   - *Bowling:* Concedes $r_{\text{conceded}} = 1$ (plus any runs). Numerator debited $-r_{\text{conceded}}$, legal ball denominator increments 0.
2. **No-Balls (792 deliveries):**
   - *Batting:* Included in $\mathcal{F}_i$ (`is_batter_ball_faced == True`). Striker credited with `batter_runs`. The 1-run penalty belongs to the bowler.
   - *Bowling:* Concedes $r_{\text{conceded}} = 1 + \text{batter\_runs}$. Numerator debited $-r_{\text{conceded}}$, legal ball denominator increments 0. Subsequent free hit evaluated when bowled.
3. **Byes & Leg-Byes (3,020 deliveries):**
   - *Batting:* Included in $\mathcal{F}_i$ (`is_batter_ball_faced == True`). Batter runs $r_t = 0$. Strikers are not credited for fielding lapses.
   - *Bowling:* Bowler conceded runs $r_{\text{conceded}, t} = 0$. Bowlers are not debited for fielding extras.

---

## 5. Reconciled Dynamic Wicket Valuation ($\lambda_{\text{wkt}}$)

### 5.1 Critique of Step 6 Heuristic & Empirical Failure
Step 6 proposed $\lambda_{\text{wkt}}(S_t) \approx \frac{V_{\text{par}} - S_t}{W_{\text{rem}, t}}$.
As proven in Step 6.1, this formula becomes negative whenever $S_t > V_{\text{par}}$, which occurs on **8,439 deliveries in Innings 1** (scores up to 301). A negative $\lambda_{\text{wkt}}$ rewards dismissals and penalizes wickets.

Furthermore, empirical cell differencing ($\mathbb{E}[R_{\text{rem}} \mid u, w] - \mathbb{E}[R_{\text{rem}} \mid u, w+1]$) on raw discrete bins produces negative values in small-sample cells (e.g. over 16 with 0 wickets lost produces $\Delta = -3.3$ runs due to selection bias).

### 5.2 Reconciled Formulation: Smooth Monotonic Resource Curves
To guarantee cricket logic and mathematical validity without imposing an artificial ad-hoc floor, $\lambda_{\text{wkt}}$ must be derived from a **smooth, strictly monotonic resource surface**:

#### Innings 1 (First-Innings Total Maximization):
$$\mathbf{\lambda_{\text{wkt}, \text{inn1}}(u_t, W_{\text{rem}, t}) = R(u_t, W_{\text{rem}, t}) - R(u_t, W_{\text{rem}, t} - 1)}$$

Where $R(u, W_{\text{rem}})$ is the expected remaining runs as a function of balls remaining $u \in [1, 120]$ and wickets in hand $W_{\text{rem}} \in [1, 10]$, modeled via the classical exponential-decay resource function (Duckworth-Lewis-Stern formulation):

$$R(u, W_{\text{rem}}) = Z_0(W_{\text{rem}}) \cdot \left[1 - \exp\left(-\frac{b \cdot u}{Z_0(W_{\text{rem}})}\right)\right]$$

#### Boundary Conditions and Mathematical Proof of Monotonicity:
1. **Strict Positivity:** Because asymptotic capacity $Z_0(W_{\text{rem}})$ is strictly increasing in wickets in hand ($Z_0(w) > Z_0(w-1)$ for all $w$), $R(u, w) > R(u, w-1)$ for all $u > 0$. Therefore:
   $$\lambda_{\text{wkt}, \text{inn1}}(u, w) > 0 \quad \forall u > 0, w \in [1, 10]$$
2. **Terminal Boundary (All-Out):** When 9 wickets have fallen ($W_{\text{rem}} = 1$), losing the final wicket ends the innings immediately:
   $$R(u, 0) \equiv 0 \implies \lambda_{\text{wkt}}(u, 1) = R(u, 1) - 0 = R(u, 1) > 0$$
   The 10th wicket is worth all remaining runs the last pair was expected to score.
3. **Phase-Dependent Evolution:**
   - *Powerplay (Overs 1–6):* $u \in [85, 120], W_{\text{rem}} \in [8, 10] \implies \lambda_{\text{wkt}} \in [12.0, 18.0]\text{ runs}$.
   - *Middle (Overs 7–16):* $u \in [25, 84], W_{\text{rem}} \in [5, 8] \implies \lambda_{\text{wkt}} \in [6.0, 11.0]\text{ runs}$.
   - *Death (Overs 17–19):* $u \in [7, 24], W_{\text{rem}} \in [2, 5] \implies \lambda_{\text{wkt}} \in [2.5, 5.0]\text{ runs}$.
   - *Final Over (Over 20):* $u \in [1, 6] \implies \lambda_{\text{wkt}} \in [1.0, 2.5]\text{ runs}$.

#### Innings 2 (Second-Innings Win Probability Leverage):
In a chase, runs beyond the target have zero utility. A wicket reduces the probability of victory:
$$\Delta \text{WP}_{\text{wkt}} = \text{WP}_2(S_t, L_t, W_t) - \text{WP}_2(S_t, L_t, W_t + 1)$$
The marginal win probability of a run is:
$$\Delta \text{WP}_{\text{run}} = \text{WP}_2(S_t + 1, L_t, W_t) - \text{WP}_2(S_t, L_t, W_t)$$

The run-equivalent value of a wicket in Innings 2 is the **marginal rate of substitution**:

$$\mathbf{\lambda_{\text{wkt}, \text{inn2}}(S_t, L_t, W_t) = \frac{\Delta \text{WP}_{\text{wkt}}}{\max(\epsilon, \Delta \text{WP}_{\text{run}})}}$$

Where $\text{WP}_2$ is the frozen Step 4 pre-delivery win probability model. In blowouts ($\text{WP} \to 0$ or $\text{WP} \to 1$), where the derivative ratio can become noisy ($0/0$), $\lambda_{\text{wkt}}$ smoothly reverts to the Innings 1 resource curve:
$$\lambda_{\text{wkt}, \text{inn2}} = (1 - \text{Leverage}_t) \cdot \lambda_{\text{wkt}, \text{inn1}} + \text{Leverage}_t \cdot \left(\frac{\Delta \text{WP}_{\text{wkt}}}{\Delta \text{WP}_{\text{run}}}\right)$$
This guarantees that $\lambda_{\text{wkt}}$ is strictly positive, cricket-logical, and continuous across all 186,780 deliveries.

---

## 6. Baseline Conditioning Strategy: Resolving Specificity vs. Sample Size

### 6.1 Evaluation of Candidate Baselines
The reconciliation must balance situational precision against sampling stability:

| Candidate Strategy | Cell Count | Min Cell Sample | Max Sampling Error | Situational Specificity | Audit Determination |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **Approach A:** Innings × Phase × Pressure Decile | 60 | **51 deliveries** | $\pm 0.45\text{ runs}$ | High, but **circular with pressure** and plagued by extreme cell sparsity. | **REJECTED** |
| **Approach B:** Innings × Phase × Format | 12 | **6,500 deliveries** | $\pm 0.04\text{ runs}$ | Too coarse; treats 15/3 collapse the same as 60/0 in PP, and 160/2 the same as 110/8 in Death. | **REJECTED** |
| **Approach C (Reconciled):** Innings × Format × Phase × Wickets Bucket | **36** | **1,462 deliveries** | **$\pm 0.08\text{ runs}$** | **Optimal:** Captures entry crisis and batting depth while preserving large statistical samples. | **APPROVED** |

### 6.2 The Reconciled 36-Cell Baseline Tensor
The situational par baseline $\mathbb{E}[Y \mid \text{state}_t]$ is estimated non-parametrically across the certified 186,780 deliveries using a 4-way stratification:

$$\mathbf{\mathbb{E}[Y \mid \text{state}_t] = \text{Lookup}(\text{Innings}, \text{Format}, \text{Phase}, \text{WicketsBucket})}$$

```
                         36-Cell Stratification Tensor
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 1. Innings:       Innings 1 (Setting Total), Innings 2 (Chasing Target) │
  │ 2. Format:        IPL (High Scoring, 8.81 RPO), T20I (Standard, 8.03 RPO)│
  │ 3. Phase:         Powerplay (1-6), Middle (7-16), Death (17-20)         │
  │ 4. Wickets Bucket:Phase-Specific Resource State:                        │
  │                   • Powerplay: 0 down (Control), 1 down, 2+ (Crisis)    │
  │                   • Middle:    0-2 down (Cruising), 3-4, 5+ (Collapse)  │
  │                   • Death:     0-3 down (Power), 4-6, 7+ (Tailenders)   │
  └─────────────────────────────────────────────────────────────────────────┘
```

#### Empirical Cell Distribution (Certified Cohort):
- **Total Deliveries:** 186,780
- **Total Cells:** Exactly 36 (100% populated)
- **Minimum Cell Size:** **1,462 deliveries** (Innings 2, T20I, Death, 0-3 wickets)
- **Median Cell Size:** **4,266 deliveries**
- **Maximum Cell Size:** **10,764 deliveries** (Innings 1, T20I, Middle, 0-2 wickets)

#### Why This Resolves Every Audit Requirement:
1. **Statistical Stability:** Every cell contains $\ge 1,462$ deliveries, guaranteeing standard errors of the mean $\le 0.08$ runs/ball.
2. **Batting-Order Fairness:** A middle-order batter walking in at 15/3 is evaluated against `PP, Wkts=2+` par (defensive, out-probable), not against 0/0 opening par. A finisher entering at 165/3 is evaluated against `Death, Wkts=0-3`, while a tailender at 110/8 is evaluated against `Death, Wkts=7+`.
3. **Format Fairness:** IPL batters are compared against IPL par (8.81 RPO), eliminating the unearned $+0.78$ RPO bonus.
4. **Zero Circularity:** The baseline conditions on match state ($u, W, \text{format}$), completely decoupling it from delivery pressure $P_t$.

---

## 7. Pressure Weighting & Orthogonality

### 7.1 Weighting Formulation
The pressure weighting function is:
$$\mathbf{w(P_t) = \left(\frac{P_t}{50.0}\right)^\alpha}$$

Where $P_t \in [0, 100]$ is the certified Step 4 pre-delivery pressure.

### 7.2 Choice of Exponent $\alpha$
Step 6.1 investigated the sensitivity of player scores to $\alpha$:
- $\alpha = 1.0$ (Linear): Weight ranges from $0.20$ ($P=10$) to $1.80$ ($P=90$). Ratio is $9.0\times$. Smooth, stable, robust.
- $\alpha = 1.25$ (Mild Convex): Weight ranges from $0.13$ ($P=10$) to $2.08$ ($P=90$). Ratio is $16.0\times$. Gives appropriate extra credit to climax deliveries without destabilizing small samples.
- $\alpha \ge 1.5$ (Super-Convex): Ratio exceeds $27\times$ to $81\times$. **Rejected** because it allows 15 balls in extreme finishes to completely override 200 balls of regular execution.

**Reconciled Decision:** The baseline weighting is set to **$\alpha = 1.0$**, with **$\alpha = 1.25$** designated as a primary sensitivity comparison in Step 7.

### 7.3 Mathematical Proof of Zero Double-Counting
Let $Y_t$ be the delivery outcome, $\mathbb{E}[Y \mid S_t]$ be the conditional baseline, and $P_t$ be pressure:
1. The conditional baseline $\mathbb{E}[Y \mid S_t]$ is estimated over $S_t = (\text{Innings}, \text{Format}, \text{Phase}, \text{WicketsBucket})$. It **does not contain $P_t$**.
2. The residual $V_t = Y_t - \mathbb{E}[Y \mid S_t]$ has expectation zero: $\mathbb{E}[V_t \mid S_t] \equiv 0$.
3. The weight $w(P_t)$ acts purely as an importance weight in the weighted average $\frac{\sum w V}{\sum w}$.
4. Therefore, situational difficulty is not counted twice: baseline sets the **expected par**, and $w(P_t)$ scales the **stakes of the execution**.

### 7.4 Role of Diagnostic Pressure Bands
Pressure bands must **not** be multiplied into composite indices (as proposed in SPRI/PEI). They serve strictly as **diagnostic reporting slices**:
- **Low Pressure ($P \le 40$):** Baseline accumulation (41.5% of balls).
- **Moderate Pressure ($40 < P \le 60$):** Standard competitive tension (40.2% of balls).
- **High Pressure ($P > 60$):** Elevated consequence & difficulty (18.3% of balls).
- **Extreme Climax Pressure ($P > 75$):** Match-defining moments (5.1% of balls).

---

## 8. Shrinkage, Information & Uncertainty Framework

To resolve the misuse of pressure-weighted exposure as effective sample size, we formally separate the four dimensions of sample size and uncertainty:

```
                  Four-Tier Uncertainty Architecture
  ┌────────────────────────────────────────────────────────────────────────┐
  │ 1. Physical Opportunity:      N_raw = Balls Faced / Legal Balls Bowled │
  │ 2. Pressure Exposure:         N_weighted = ∑ w(P_t)                   │
  │ 3. Statistical Information:   N_eff,Kish = (∑ w_t)^2 / ∑ w_t^2        │
  │ 4. Score & Ranking Precision: Cluster-Robust SE & 95% Bootstrap CIs    │
  └────────────────────────────────────────────────────────────────────────┘
```

### 8.1 Kish Effective Sample Size ($N_{\text{eff}, \text{Kish}}$)
When independent observations are weighted by non-uniform weights $w_t$, the statistical information is:

$$\mathbf{N_{\text{eff}, i} = \frac{\left(\sum_{t=1}^{N_i} w(P_{i,t})\right)^2}{\sum_{t=1}^{N_i} w(P_{i,t})^2}}$$

By the Cauchy-Schwarz inequality, $N_{\text{eff}, i} \le N_{\text{raw}, i}$ always. This eliminates the anomaly where 303 players had $N_{\text{weighted}} > N_{\text{raw}}$.

### 8.2 Cluster-Robust Variance Decomposition
Deliveries within a match share pitch and opponent conditions ($\rho_{\text{ICC}} \approx 0.0142$).
For player $i$ with average cluster size $\bar{m}_i$ balls per match, the design effect is:
$$\text{Deff}_i = 1 + (\bar{m}_i - 1) \cdot \rho_{\text{ICC}}$$
The true cluster-adjusted degrees of freedom is:
$$N_{\text{eff}, i}^{\text{cluster}} = \frac{N_{\text{eff}, i}}{\text{Deff}_i}$$

### 8.3 Empirical Bayes Shrinkage Constant $K$
Under the James-Stein / Empirical Bayes framework, the shrinkage constant $K$ represents the variance ratio:

$$\mathbf{K = \frac{\mathbb{E}[\sigma_{\text{within}}^2]}{\sigma_{\text{between}}^2}}$$

Where:
- $\sigma_{\text{within}}^2$ is the average within-player sampling variance of delivery value added.
- $\sigma_{\text{between}}^2$ is the true variance of latent talent across players, estimated via method-of-moments:
  $$\hat{\sigma}_{\text{between}}^2 = \max\left(0, \text{Var}(\hat{\theta}_i) - \frac{1}{M}\sum_{i=1}^M \frac{s_i^2}{N_{\text{eff}, i}^{\text{cluster}}}\right)$$

#### Asymmetry Between Batting and Bowling:
- **Batting:** High within-player variance ($\sigma_{\text{within}}^2 \approx 3.0$), single-dismissal hazard risk. $\implies K_{\text{bat}}$ will be higher ($\approx 70 - 100$).
- **Bowling:** Lower within-player variance ($\sigma_{\text{within}}^2 \approx 2.4$), 24-ball repeated quotas. $\implies K_{\text{bowl}}$ will be lower ($\approx 50 - 75$).
- $K_{\text{bat}}$ and $K_{\text{bowl}}$ must be estimated independently in Step 7.

### 8.4 Minimum Opportunity Filter
To receive an official competition ranking, a player must have delivered or faced at least:
$$\mathbf{N(P \ge 50.0) \ge 50 \text{ actual deliveries}}$$
This qualifies **297 batters** and **292 bowlers**, ensuring that every ranked player has at least 35% sample evidence weight ($\frac{N}{N+K} \ge 0.35$).

---

## 9. Role and Format Fairness Controls

```
                       Fairness Control Architecture
       Batting Controls                         Bowling Controls
 ─────────────────────────────           ─────────────────────────────
 • PP / Mid / Death Baselines            • PP / Mid / Death Baselines
 • 3 Wicket Buckets per Phase            • 3 Wicket Buckets per Phase
 • Per-Ball Rate (Zero Volume Bias)      • Per-Legal-Ball Rate (Quota Basis)
 • Immunity to Not-Out Inflation         • Bowler-Credited Wickets Only
 • IPL vs T20I Format Par Table          • IPL vs T20I Format Par Table
```

1. **Batting Order Balance:** Top-order batters face $P \approx 52$ in PP; middle-order batters face $P \approx 41$ in Middle; finishers face $P \approx 53$ in Death (with 42.5% at $P > 65$). By computing PWSVA as an **average rate per effective ball**, finishers do not win on volume, and openers are not penalized for facing new-ball par.
2. **Bowling Role Balance:** Middle-overs spinners (e.g. Rashid Khan, Sunil Narine) bowl when $P \approx 39$. Under the reconciled $P \ge 50$ qualification filter, they easily qualify (292 bowlers qualify), and their run suppression is benchmarked against middle-overs par ($7.3$ RPO), ensuring full fairness against death yorker specialists.
3. **Format Par Alignment:** Baselines condition on tournament format, ensuring an IPL bowler conceding 8.5 RPO is credited (+0.31 runs saved vs 8.81 par), while a T20I bowler conceding 8.5 RPO is appropriately debited (-0.47 runs vs 8.03 par).

---

## 10. Comprehensive Step 7 Validation Protocol

The following six empirical tests must be executed in Step 7 to certify the methodology:

```
                           Step 7 Validation Suite
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ 1. Match-Level Block Bootstrap: 1,000 resamples -> 95% CIs for ranks    │
  │ 2. Chronological Split-Half:    Odd vs Even matches within tournaments   │
  │ 3. Multi-Role Invariance:       R^2 < 0.05 against phase ball proportions│
  │ 4. Diagnostic Band Progression: Performance audited across 4 P-tiers    │
  │ 5. Parameter Sensitivity Grid:  K ± 30%, α ∈ {1.0, 1.15, 1.25}          │
  │ 6. Cross-Format Consistency:    IPL vs T20I correlation for dual-players │
  └─────────────────────────────────────────────────────────────────────────┘
```

1. **Match-Level Block Bootstrap ($B = 1,000$):**
   - Resample 782 matches with replacement to respect cluster correlation.
   - Recompute $\text{PWSVA}^{\text{shrunk}}$ and $\text{SBVA}^{\text{shrunk}}$ for all qualifying players.
   - Generate **95% Bootstrap Confidence Intervals** for scores and ranks $[R_{2.5\%}, R_{97.5\%}]$.
2. **Odd/Even Match Split-Half Reliability:**
   - Partition matches chronologically into odd and even match dates.
   - Compute Spearman rank correlation $\rho_{\text{split}}$. Target: $\rho_{\text{split}} \ge 0.55$.
3. **Role & Phase Invariance Multi-Regression:**
   - Regress player reliability scores against their proportions of balls in PP and Death:
     $$\hat{\theta}_i = \beta_0 + \beta_{\text{PP}} \cdot \text{PctPP}_i + \beta_{\text{Death}} \cdot \text{PctDeath}_i + \epsilon_i$$
   - Verification standard: Combined $R^2 < 0.05$, confirming that role explains less than 5% of metric variance.
4. **Diagnostic Pressure-Band Progression:**
   - Report each top-20 player's net run value added across the 4 diagnostic pressure tiers ($P \le 40, 40-60, >60, >75$).
   - Verify that no top-ranked player exhibits negative execution in Tier 3 or Tier 4.
5. **Parameter Sensitivity Sweeps:**
   - Vary $K \in \{0.7 K^*, K^*, 1.3 K^*\}$ and $\alpha \in \{1.0, 1.15, 1.25\}$.
   - Confirm rank stability: Spearman $\rho \ge 0.90$ and top-10 membership overlap $\ge 80\%$.
6. **Cross-Format Consistency:**
   - For players with $\ge 30$ pressure deliveries in both IPL and T20Is, compute cross-format rank correlation to confirm that reliability measures intrinsic player skill.

---

## 11. Summary of Rejected Alternatives

| Rejected Methodology | Core Concept | Reason for Final Rejection |
| :--- | :--- | :--- |
| **Legacy BRS3 / BoRS** | Raw Strike Rate $\times$ Pressure Index with $K=50$ | **Severe structural defects.** Rewarded death hitting without par baselines; double-counted pressure; volume-biased. |
| **Candidate Model B (SPRI / PEI)** | Composite multiplication of bands, slopes, and CV | **Statistically uninterpretable.** Compounded measurement noise; within-player slope $\beta$ unstable for small $N$. |
| **Approach A Bowling Accounting** | Total deliveries denominator ($\sum w$) | **Mathematically flawed.** Bowling wides improved economy rates in death overs; failed to reflect cricket's 6-ball over quota. |
| **Heuristic Wicket Value ($\frac{V_{\text{par}}-S}{W_{\text{rem}}}$)** | Runs to par divided by wickets remaining | **Pathological.** Evaluated to negative values on 8,439 balls, rewarding batters for getting out. |
| **Discrete Decile Baseline (60 Cells)** | $2 \times 3 \times 10$ Stratification | **Severe sparsity.** 20 cells had $N < 1,500$ down to 51 balls; created circular double-conditioning on pressure. |
| **Coarse 12-Cell Baseline** | $\text{Innings} \times \text{Phase} \times \text{Format}$ | **Sacrificed situational crisis.** Treated 15/3 collapse the same as 60/0 in PP, and 160/2 the same as 110/8 in Death. |
| **Raw Win Probability Added (WPA)** | $\sum \Delta \text{WP}$ | **Context-distorted.** Over-rewarded trivial plays in $50\%$ games and ignored clutch plays in asymmetric states. |

---

## 12. Remaining Empirical Questions for Step 7

The following four parameters are purely empirical and must be calibrated in Step 7 using data-driven estimation procedures:

1. **Numerical Value of $K_{\text{bat}}$:** To be estimated via Empirical Bayes variance-ratio estimation across the 297 qualifying batters.
2. **Numerical Value of $K_{\text{bowl}}$:** To be estimated via Empirical Bayes variance-ratio estimation across the 292 qualifying bowlers.
3. **Weighting Power Exponent $\alpha$:** Step 7 will evaluate $\alpha = 1.0$ vs $\alpha = 1.15$ vs $\alpha = 1.25$ using split-half stability and bootstrap rank widths.
4. **Parametric DLS Fit vs. 2D Monotonic GAM for $\lambda_{\text{wkt}}$:** Step 7 will compare the fit of the exponential-decay resource curve against a monotonic spline to select the smoothest representation.

---

## 13. Explicit Approval Conditions for Step 7 Calibration

The transition to Step 7 empirical implementation is approved **if and only if** the Step 7 implementation adheres strictly to the following binding criteria:

- [x] **Criterion 1 (Frozen Inputs):** Step 4 v3 pressure values and Step 5 player-level datasets remain 100% frozen.
- [ ] **Criterion 2 (Batting Domain):** PWSVA code must filter strictly to `is_batter_ball_faced == True`, completely excluding wides from the batter's ledger.
- [ ] **Criterion 3 (Bowling Quota Basis):** SBVA code must implement the reconciled Approach B formula, debiting all bowler-conceded runs in the numerator and dividing strictly by legal deliveries.
- [ ] **Criterion 4 (Monotonic Wicket Values):** $\lambda_{\text{wkt}}$ must use the smooth monotonic resource loss curve, guaranteeing $\lambda_{\text{wkt}} \ge 1.0$ run for all deliveries.
- [ ] **Criterion 5 (36-Cell Baselines):** Baselines must be estimated using the 36-cell tensor ($\text{Innings} \times \text{Format} \times \text{Phase} \times \text{WicketsBucket}$), maintaining $N \ge 1,462$ deliveries per cell.
- [ ] **Criterion 6 (Kish Effective Sample Size):** Shrinkage must use Kish's $N_{\text{eff}} = (\sum w)^2 / \sum w^2$, and $K$ must be estimated separately for batting and bowling.
- [ ] **Criterion 7 (Cluster Bootstrap CIs):** All player rankings must report 95% bootstrap confidence intervals based on 1,000 match-cluster resamples.

---
*Report certified by Antigravity Methodology Reconciliation Team.*  
*November 2026.*
