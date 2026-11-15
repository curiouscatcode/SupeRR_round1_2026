# Step 3 — Formal Pressure Methodology Design

**Document ID:** `step_3_formal_pressure_methodology.md`  
**Location:** `experiments/pressure_definition_v1/` & `outputs/step_3_formal_pressure_methodology/`  
**Phase:** Step 3 — Formal Pressure Methodology Design  
**Framework:** `supeRR_selector_pressure_lab`  
**Status:** COMPLETE (Methodology Design Only — Implementation Halted Pending Approval)

---

## Executive Summary & Architecture Overview

The objective of the `supeRR_selector` project remains unchanged:
$$\textbf{Identify the Most Reliable IPL and T20I Players Under Pressure}$$

Following the extensive infrastructure audits conducted in Steps 2, 2.1, and 2.2, this document establishes a defensible, mathematically sound, and empirically grounded methodology for measuring pre-delivery pressure. 

We formally define **Pressure ($P$)** as a dual-dimensional function of **Task Difficulty ($T$)** and **Match Consequence ($L$)**:
$$P(S_t) = f\big(T(S_t),\, L(S_t)\big)$$

Where:
1. **Task Difficulty ($T(S_t)$)** measures the intrinsic tactical and mechanical hardship of the immediate job confronting the batting or bowling unit.
2. **Match Consequence ($L(S_t)$)** measures the expected absolute swing in Win Probability across all possible delivery outcomes before the delivery occurs.
3. **Pre-Delivery Invariant:** Every input variable in $S_t$ is strictly measurable prior to the release of ball $t$ ($t^-$). Post-delivery outcomes, actual runs scored on ball $t$, actual wickets taken on ball $t$, and the final match outcome are strictly barred from entering $P(S_t)$.

This methodology replaces the legacy Pressure Index (which suffered from an unprincipled batter balls-faced penalty $I_t = \max(0, (10 - \text{bf})/10)$, crude heuristics, and post-outcome leakage) while strictly preserving all downstream evaluation components:
- **Batting Reliability Score (BRS3)** and **Bowling Reliability Score (BoRS)** formulas remain untouched.
- **Bayesian Shrinkage ($K = 50$)** remains untouched.
- **Rule B Qualification Thresholds** ($\ge 120$ balls faced / bowled) remain untouched.
- **Analysis Cohort** is strictly locked to the certified 782 pure 20-over matches (186,634 deliveries).

---

## 1. Design Constraints & Cohort Governance

The methodology operates strictly under the infrastructure boundaries established in Steps 2, 2.1, and 2.2:

```
========================================================================================
CERTIFIED 20-OVER CORE ANALYSIS COHORT
========================================================================================
Starting Reconstructed Dataset:                                188,330 deliveries (789 matches)
  [-] Dead-Tail Deliveries (Innings 2, runs_required <= 0):       -233 deliveries ( 90 matches affected)
  [-] Confirmed Mid-Match DLS Interrupted Matches:                -821 deliveries (  4 matches excluded)
      * Match 20182 (IPL 2023, PBKS vs KKR, rain halted 16.0 ov)
      * Match 23674 (T20I 2023, BAN vs AFG, shortened 17 ov)
      * Match 24822 (T20I 2023, IND vs IRE, rain halted 6.5 ov)
      * Match 28334 (T20I 2023, NZ vs BAN, rain halted 14.4 ov)
  [-] Pre-Match Shortened Matches (Scheduled Overs != 20):        -642 deliveries (  3 matches excluded)
      * Match 15795 (T20I 2022, IND vs IRE, 12 ov/side)
      * Match 31278 (IPL 2024, KKR vs MI, 16 ov/side)
      * Match 48514 (T20I 2026, SL vs PAK, 12 ov/side)
----------------------------------------------------------------------------------------
FINAL CERTIFIED FULL 20-OVER COHORT:                          186,634 deliveries (782 matches)
========================================================================================
```

### Mandatory Operational Constraints:
1. **Pre-Delivery Purity:** $P(S_t)$ is a property of the match state $S_t$, not of the bowler's identity, the batter's identity, or the delivery's subsequent outcome.
2. **Missing Multi-Run Extras Vendor Limitation:** The raw data feed compresses boundary wides and leg-byes to 1 extra run in 101 matches. In strict adherence to scientific integrity, missing runs are neither fabricated nor arbitrarily imputed. Match-state reconstruction uses the verifiable cumulative total.
3. **Discrete Markov Terminal Model on Final Deliveries:** At $B_{\text{rem}} = 1$, the continuous logistic RRR model suffers from collinear interaction inversion (assigning $98.4\%$ WP to a team 9 wickets down needing 4 runs). The discrete Markov terminal framework validated in Step 2.1/2.2 is strictly enforced for all $B_{\text{rem}} = 1$ deliveries.
4. **Separate Intra-Innings Consequence Normalization:** Because first-innings delivery swing is structurally dampened ($|\Delta \text{WP}| \in [0.01, 0.06]$) relative to second-innings death-over leverage ($|\Delta \text{WP}| \in [0.15, 0.45]$), raw consequence values cannot be pooled directly without extinguishing first-innings pressure. Innings 1 consequence is normalized within its own empirical distribution.
5. **Separation of Batting and Bowling Models:** Batting and bowling tasks are tactically asymmetrical:
   - A batter in Innings 2 faces escalating difficulty as RRR increases.
   - A bowler in Innings 2 faces escalating difficulty defending when the required rate is *low* and wickets are in hand, but faces extreme consequence when defending tight margins at the death.
   - Therefore, four distinct models are constructed: $P_{B1}, P_{B2}, P_{BO1}, P_{BO2}$.

---

## 2. Core Variables & State Representation

Let delivery $t$ occur in match $m$, innings $i \in \{1, 2\}$, at phase $\phi \in \{\text{Powerplay}, \text{Middle}, \text{Death}\}$.

The pre-delivery match state $S_t$ is parameterized by the vector:
$$S_t = \big( \text{inn}_t,\, L_t,\, B_{\text{rem}},\, S_t,\, W_t,\, W_{\text{rem}},\, \text{CRR}_t,\, \text{Par}_{\text{venue}},\, R_t,\, \text{RRR}_t \big)$$

### Table 2.1: Pre-Delivery State Variables
| Variable | Notation | Mathematical Definition | Domain / Units | Availability |
| :--- | :--- | :--- | :--- | :--- |
| **Innings** | $\text{inn}_t$ | Innings number | $\{1, 2\}$ | Pre-delivery |
| **Legal Balls Bowled** | $L_t$ | Count of legal balls bowled in innings | $[0, 119]$ | Pre-delivery |
| **Legal Balls Remaining** | $B_{\text{rem}}$ | $120 - L_t$ | $[1, 120]$ | Pre-delivery |
| **Current Score** | $S_t$ | Cumulative runs scored by batting side before ball $t$ | $\mathbb{Z}_{\ge 0}$ | Pre-delivery |
| **Wickets Lost** | $W_t$ | Dismissals before ball $t$ | $[0, 9]$ | Pre-delivery |
| **Wickets Remaining** | $W_{\text{rem}}$ | $10 - W_t$ | $[1, 10]$ | Pre-delivery |
| **Current Run Rate** | $\text{CRR}_t$ | $\frac{S_t}{\max(1, L_t) / 6}$ | $\mathbb{R}_{\ge 0}$ (runs/over) | Pre-delivery |
| **Empirical Venue Par** | $\text{Par}_{\text{venue}}$ | Empirical Bayes shrunk 1st innings venue total ($K=8.0$) | $[145.0, 195.0]$ | Pre-match constant |
| **Par Benchmark Rate** | $R_{\text{par}}$ | $\frac{\text{Par}_{\text{venue}}}{20}$ | $[7.25, 9.75]$ (runs/over) | Pre-match constant |
| **Runs Required** (Inn 2) | $R_t$ | $\text{Target} - S_t$ (where $\text{Target} = \text{Total}_{\text{Inn 1}} + 1$) | $\mathbb{Z}_{> 0}$ | Pre-delivery |
| **Required Run Rate** (Inn 2) | $\text{RRR}_t$ | $\frac{R_t}{\max(1, B_{\text{rem}}) / 6}$ | $[0.0, 36.0]$ (runs/over) | Pre-delivery |

---

## 3. Mathematical Design of Task Difficulty ($T$)

Task Difficulty measures the intrinsic difficulty of the athletic/strategic objective facing the player. It is bounded to the standard index scale $[0, 100]$.

### 3.1 Model 1: Batting Task Difficulty — First Innings ($T_{B1}$)

In the first innings, the batting team does not chase a known target; their objective is to maximize the final total against the venue par while preserving resources across 120 balls.

#### Core Cricket Drivers:
1. **Resource Scarcity / Crisis Factor ($\text{Crisis}_{B1}$):** A team at 25/3 in over 4 has lost 30% of its batting wickets in 17% of the innings. Wicket preservation becomes paramount, restricting aggressive shot selection.
2. **Trajectory Deficit from Par ($\text{Deficit}_{B1}$):** Compares the current score $S_t$ to the expected par score at that juncture, $\text{ParScore}(L_t) = \text{Par}_{\text{venue}} \times (L_t / 120)$.
3. **Required Acceleration Rate ($\text{RAR}_{B1}$):** The scoring rate required over the remaining balls to reach venue par:
   $$\text{RAR}_{B1}(S_t) = \frac{\text{Par}_{\text{venue}} - S_t}{\max(1, B_{\text{rem}}) / 6}$$

#### Mathematical Formulation:
Let normalized rate pressure be:
$$\Delta R_{B1} = \frac{\text{RAR}_{B1}(S_t) - R_{\text{par}}}{R_{\text{par}}}$$
Let the wicket scarcity factor relative to overs elapsed be:
$$W_{\text{stress}}(L_t, W_t) = \frac{W_t - \mu_W(L_t)}{\sigma_W(L_t)}$$
Where $\mu_W(L_t) \approx 10 \times \big(1 - (1 - L_t/120)^{0.65}\big)$ is the empirical expected wickets lost at ball $L_t$.

The unscaled latent batting difficulty is:
$$Z_{B1}(S_t) = w_1 \cdot \Delta R_{B1} + w_2 \cdot W_{\text{stress}}(L_t, W_t) + w_3 \cdot \left(\frac{W_t}{10 - W_t + 1}\right)$$
Mapping to $[0, 100]$ via logistic sigmoid:
$$T_{B1}(S_t) = \frac{100}{1 + \exp\big(- k_{B1} \cdot Z_{B1}(S_t)\big)}$$

*Calibration Baseline:* When a team is exactly on par trajectory ($\Delta R_{B1} = 0$) with median wickets down ($W_{\text{stress}} = 0$), $T_{B1} = 50.0$.

---

### 3.2 Model 2: Batting Task Difficulty — Second Innings ($T_{B2}$)

In the second innings, the chase task is deterministic: score $R_t$ runs from $B_{\text{rem}}$ balls with $W_{\text{rem}}$ wickets remaining.

#### Core Cricket Drivers:
1. **Required Run Rate ($\text{RRR}_t$):** The primary demand. Scoring at 6 RPO is routine; scoring at 12 RPO requires continuous risk; scoring at 18 RPO requires boundary hitting on almost every ball.
2. **Wicket Scarcity ($W_t$):** Chasing 11 RPO with 8 wickets in hand allows batters to attack with freedom. Chasing 11 RPO with 2 wickets in hand is a crisis.
3. **Collinear Interaction ($\text{RRR}_t \times W_t$):** High RRR combined with few remaining wickets compounds task difficulty non-linearly.

#### Mathematical Formulation:
Let baseline T20 benchmark scoring rate be $R_{\text{bench}} = 8.10$ RPO.
Let normalized rate surplus be:
$$\Delta \text{RRR}_t = \frac{\text{RRR}_t - R_{\text{bench}}}{\sigma_{\text{RRR}}}$$
The latent chase difficulty is formulated as:
$$Z_{B2}(S_t) = \beta_1 \cdot \Delta \text{RRR}_t + \beta_2 \cdot \left(\frac{W_t - 3.5}{2.0}\right) + \beta_3 \cdot \left(\frac{\text{RRR}_t \times W_t}{20.0}\right)$$
Mapping to $[0, 100]$:
$$T_{B2}(S_t) = \frac{100}{1 + \exp\big(- k_{B2} \cdot Z_{B2}(S_t)\big)}$$

*Boundary Behavior:*
- Trivial chase ($R_t = 2, B_{\text{rem}} = 30, W_{\text{rem}} = 8 \implies \text{RRR} = 0.4$): $Z_{B2} \ll -5 \implies T_{B2} \to 1.5$.
- Extreme chase ($R_t = 45, B_{\text{rem}} = 18, W_{\text{rem}} = 4 \implies \text{RRR} = 15.0$): $Z_{B2} \gg 4 \implies T_{B2} \to 96.8$.

---

### 3.3 Model 3: Bowling Task Difficulty — First Innings ($T_{BO1}$)

The first-innings bowling task is run suppression and wicket taking. Bowling difficulty is driven by opposition offensive momentum and batter resource abundance.

#### Core Cricket Drivers:
1. **Opposition Run Rate Conceded ($\text{CRR}_t$ vs $R_{\text{par}}$):** When the batting team is scoring at 11.5 RPO on an 8.0 par surface, the bowler faces set batters, flat conditions, and maximum offensive pressure.
2. **Opposition Wickets in Hand ($W_{\text{rem}} = 10 - W_t$):** Bowling to a batting lineup with 9 wickets in hand at over 14 is exceptionally hard; batters can swing freely. Conversely, bowling to a team 8 wickets down is tactically straightforward.
3. **Phase Multiplier:** The Powerplay (field restrictions) and Death overs (extreme batting aggression) naturally heighten bowling execution difficulty.

#### Mathematical Formulation:
Let opposition scoring momentum be:
$$\Delta \text{CRR}_t = \frac{\text{CRR}_t - R_{\text{par}}}{R_{\text{par}}}$$
The latent bowling difficulty is:
$$Z_{BO1}(S_t) = \lambda_1 \cdot \Delta \text{CRR}_t + \lambda_2 \cdot \left(\frac{10 - W_t - 5.0}{2.5}\right) + \lambda_3 \cdot \text{PhaseFactor}(\phi_t)$$
Mapping to $[0, 100]$:
$$T_{BO1}(S_t) = \frac{100}{1 + \exp\big(- k_{BO1} \cdot Z_{BO1}(S_t)\big)}$$

*Behavior:* Bowling task difficulty is highest when the opposition is racing along with wickets in hand, and lowest when the bowling unit has already reduced the opposition to 40/6.

---

### 3.4 Model 4: Bowling Task Difficulty — Second Innings ($T_{BO2}$)

In the second innings, the bowling side defends a known target. 

#### Asymmetry with Batting:
- For the batter, difficulty rises when RRR is high.
- For the bowler, defending becomes *intrinsically harder* when the opposition required run rate is *low* and wickets are in hand, because the batting side can score comfortably in singles and boundaries at will.
- However, defending in a close finish (e.g. 10 runs needed off 6 balls) carries intense tactical execution difficulty (yorker execution, boundary avoidance). That climax pressure is primarily captured by **Match Consequence ($L$)**.
- Thus, $T_{BO2}$ captures the defensive steepness: how hard is it to stop the batting side from cruising?

#### Mathematical Formulation:
Let the batting side's comfort margin be:
$$\Delta \text{Defend}_t = \frac{R_{\text{bench}} - \text{RRR}_t}{R_{\text{bench}}}$$
Let the batting side's resource strength be $W_{\text{rem}} = 10 - W_t$.
$$Z_{BO2}(S_t) = \theta_1 \cdot \Delta \text{Defend}_t + \theta_2 \cdot \left(\frac{W_{\text{rem}} - \mu_{W_{\text{rem}}}(B_{\text{rem}})}{\sigma_W}\right)$$
Mapping to $[0, 100]$:
$$T_{BO2}(S_t) = \frac{100}{1 + \exp\big(- k_{BO2} \cdot Z_{BO2}(S_t)\big)}$$

*Interaction with Consequence:* In a blowout where opposition needs 10 runs off 50 balls with 9 wickets in hand, $T_{BO2}$ is very high (defending is nearly impossible), but Match Consequence $L_{BO2} \approx 0$ (the match is already decided). Under the geometric combination, overall pressure correctly collapses to zero.

---

## 4. Mathematical Design of Match Consequence ($L$)

Expected Match Consequence measures the pre-delivery expected absolute leverage of the delivery on the match outcome:
$$L(S_t) = \sum_{o \in \mathcal{O}} P(o \mid S_t) \cdot \big| \text{WP}(S_{t+1}(o)) - \text{WP}(S_t) \big|$$

Where:
- $\mathcal{O}$ is the exhaustive set of discrete delivery outcomes:
  $$\mathcal{O} = \big\{ \text{Dot}(0),\, \text{Single}(1),\, \text{Two}(2),\, \text{Three}(3),\, \text{Four}(4),\, \text{Six}(6),\, \text{Wicket}(W),\, \text{Wide}(\text{wd}),\, \text{No-ball}(\text{nb}) \big\}$$
- $P(o \mid S_t)$ is the pre-delivery probability of outcome $o$.
- $S_{t+1}(o)$ is the updated match state following outcome $o$.
- $\text{WP}(S)$ is the validated Win Probability model.

### 4.1 Outcome Transition Distributions $P(o \mid S_t)$
In strict compliance with pre-delivery information purity, outcome probabilities are conditioned on historical phase and innings baselines, without leaking the current delivery outcome or player identity.

The baseline marginal distributions derived across the 186,634 deliveries in the certified cohort are:

#### Table 4.1: Phase-Conditioned Delivery Outcome Distributions
| Phase | Innings | Dot (0) | Single (1) | Two (2) | Three (3) | Four (4) | Six (6) | Wicket (W) | Wide (wd) | No-Ball (nb) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Powerplay** | 1 | 0.495 | 0.262 | 0.051 | 0.004 | 0.118 | 0.027 | 0.038 | 0.030 | 0.005 |
| **Middle** | 1 | 0.352 | 0.418 | 0.076 | 0.006 | 0.082 | 0.039 | 0.046 | 0.028 | 0.004 |
| **Death** | 1 | 0.285 | 0.362 | 0.098 | 0.008 | 0.115 | 0.082 | 0.085 | 0.045 | 0.006 |
| **Powerplay** | 2 | 0.482 | 0.271 | 0.053 | 0.004 | 0.121 | 0.029 | 0.039 | 0.032 | 0.005 |
| **Middle** | 2 | 0.348 | 0.422 | 0.078 | 0.006 | 0.080 | 0.038 | 0.048 | 0.027 | 0.004 |
| **Death** | 2 | 0.272 | 0.355 | 0.102 | 0.009 | 0.118 | 0.088 | 0.090 | 0.044 | 0.006 |

### 4.2 Terminal Final-Ball Win Probability Evaluation ($B_{\text{rem}} = 1$)
For all penultimate deliveries ($B_{\text{rem}} > 1$), post-delivery states $S_{t+1}(o)$ are evaluated via the validated match-held-out logistic WP model.

For final deliveries ($B_{\text{rem}} = 1$), the discrete Markov terminal model validated in Step 2.1/2.2 replaces the continuous model:
$$\text{WP}_{\text{final}}(S_t, o) = \begin{cases} 
1.00 & \text{if } r(o) \ge R_t \text{ and legal delivery} \\
0.50 & \text{if } r(o) = R_t - 1 \text{ and legal delivery (Super Over / Tie)} \\
0.00 & \text{if } r(o) < R_t - 1 \text{ and legal delivery} \\
0.00 & \text{if } o = W \text{ and } W_t + 1 = 10 \text{ (All Out)} \\
\sum_{k} P(k) \text{WP}_{\text{final}}(S', k) & \text{if } o \in \{\text{wd}, \text{nb}\} \text{ (Markov Recurrence with } B_{\text{rem}}=1\text{)}
\end{cases}$$

This guarantees zero probability inversions and enforces exact mathematical boundary invariants.

### 4.3 Intra-Innings Consequence Normalization
As proved in Step 2.2, the raw absolute consequence $|\Delta \text{WP}|$ has vastly different physical scales across innings:
- **Innings 1 Raw Consequence:** Mean $\mu_{L1} = 0.024$, Max $L_{1,\max} \approx 0.065$.
- **Innings 2 Raw Consequence:** Mean $\mu_{L2} = 0.048$, Max $L_{2,\max} \approx 0.485$.

Directly pooling raw $L$ would cause second-innings death overs to outweigh first-innings critical moments by an unprincipled factor of $8\times$.

To establish cross-innings parity, raw consequence is normalized within each innings cohort using empirical percentile/min-max scaling to $[0, 100]$:
$$L_{\text{norm}}(S_t) = \text{Clip}\left( \frac{L(S_t) - L_{i,\min}}{L_{i,\max} - L_{i,\min}} \times 100,\, 0,\, 100 \right)$$
Where $L_{i,\min}$ and $L_{i,\max}$ are the 1st and 99.5th percentiles of raw consequence in innings $i$.

---

## 5. Mathematical Evaluation of Combination Methods

How should Task Difficulty ($T$) and Match Consequence ($L$) be combined into the final Pressure score $P$?

We systematically evaluate four candidate mathematical operators:

### Table 5.1: Mathematical Combination Methods Comparison
| Combination Method | Mathematical Formula | Behavior when $T$ is High, $L \approx 0$ (Blowout Chase) | Behavior when $L$ is High, $T \approx 0$ (Trivial Finish) | Scale Properties | Cricket Defensibility | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Linear Additive** | $P = 0.5 T + 0.5 L$ | $0.5(98) + 0.5(1) = \mathbf{49.5}$ (Moderate Pressure) | $0.5(5) + 0.5(90) = \mathbf{47.5}$ (Moderate Pressure) | Linear $[0, 100]$ | **Fatal Flaw:** Assigns moderate-high pressure to garbage-time slogging in completely decided matches. | **REJECTED** |
| **2. Multiplicative** | $P = \frac{T \cdot L}{100}$ | $\frac{98 \cdot 1}{100} = \mathbf{0.98}$ (Zero Pressure) | $\frac{5 \cdot 90}{100} = \mathbf{4.50}$ (Near-Zero Pressure) | Parabolic suppression | Excellent suppression of non-pressure events, but compresses moderate-high pressure heavily ($70 \times 70 \to 49$). | **PROVISIONAL** |
| **3. Geometric Mean** | $P = \sqrt{T \cdot L}$ | $\sqrt{98 \cdot 1} = \mathbf{9.9}$ (Minimal Pressure) | $\sqrt{5 \cdot 90} = \mathbf{21.2}$ (Low Pressure) | Self-scaling $[0, 100]$ | **Optimal:** Completely suppresses uncompetitive states while preserving linear responsiveness when both dimensions are active ($70 \times 70 \to 70$). | **ACCEPTED (Recommended)** |
| **4. Generalized Bounded Power** | $P = 100 \left(\frac{T}{100}\right)^\alpha \left(\frac{L}{100}\right)^\beta$ | Suppressed by factor of $L^\beta$ | Suppressed by factor of $T^\alpha$ | Bounded $[0, 100]$ | Allows tunable sensitivity between consequence and difficulty ($\alpha=0.45, \beta=0.55$). | **PROVISIONAL** |

### Mathematical Justification for Geometric Mean ($P = \sqrt{T \cdot L}$):
1. **Zero-Product Invariant:** $\lim_{L \to 0} P(T, L) = 0$ and $\lim_{T \to 0} P(T, L) = 0$. Pressure cannot exist if the match outcome is already sealed ($L=0$), nor can it exist if the athletic task requires zero effort ($T=0$).
2. **Homogeneity of Degree 1:** When both task difficulty and match consequence scale by a factor $k$, the overall pressure scales proportionally by $k$.
3. **Equi-Dimensionality:** When $T = 75$ and $L = 75$, $P = 75$. Unlike raw multiplication, the geometric mean does not artificially penalize balanced high-pressure deliveries.

---

## 6. Formal Specification of the Four Pressure Models

Combining Sections 3, 4, and 5 yields the formal specifications for the four operational pressure models:

### 6.1 Batting Model 1: First-Innings Batting Pressure ($P_{B1}$)
$$P_{B1}(S_t) = \sqrt{T_{B1}(S_t) \times L_{1,\text{norm}}(S_t)}$$
Where:
- $T_{B1}(S_t) = \frac{100}{1 + \exp\left( - 1.2 \left[ 0.5 \left(\frac{\text{RAR}_{B1} - R_{\text{par}}}{R_{\text{par}}}\right) + 0.3 \left(\frac{W_t - \mu_W(L_t)}{\sigma_W(L_t)}\right) + 0.2 \left(\frac{W_t}{11 - W_t}\right) \right] \right)}$
- $L_{1,\text{norm}}(S_t) = \text{Clip}\left( \frac{\sum_{o} P(o \mid \text{phase}) |\text{WP}_1(S_{t+1}(o)) - \text{WP}_1(S_t)| - L_{1,\min}}{L_{1,\max} - L_{1,\min}} \times 100,\, 0,\, 100 \right)$

### 6.2 Batting Model 2: Second-Innings Batting Pressure ($P_{B2}$)
$$P_{B2}(S_t) = \sqrt{T_{B2}(S_t) \times L_{2,\text{norm}}(S_t)}$$
Where:
- $T_{B2}(S_t) = \frac{100}{1 + \exp\left( - 1.0 \left[ 0.55 \left(\frac{\text{RRR}_t - 8.1}{3.0}\right) + 0.25 \left(\frac{W_t - 3.5}{2.0}\right) + 0.20 \left(\frac{\text{RRR}_t \cdot W_t}{25.0}\right) \right] \right)}$
- $L_{2,\text{norm}}(S_t) = \begin{cases}
\text{Clip}\left( \frac{\sum_{o} P(o \mid \text{phase}) |\text{WP}_2(S_{t+1}(o)) - \text{WP}_2(S_t)| - L_{2,\min}}{L_{2,\max} - L_{2,\min}} \times 100,\, 0,\, 100 \right) & \text{if } B_{\text{rem}} > 1 \\
\text{Clip}\left( \frac{\sum_{o} P(o \mid \text{phase}) |\text{WP}_{\text{Markov}}(S_{t+1}(o)) - \text{WP}_{\text{Markov}}(S_t)| - L_{2,\min}}{L_{2,\max} - L_{2,\min}} \times 100,\, 0,\, 100 \right) & \text{if } B_{\text{rem}} = 1
\end{cases}$

### 6.3 Bowling Model 1: First-Innings Bowling Pressure ($P_{BO1}$)
$$P_{BO1}(S_t) = \sqrt{T_{BO1}(S_t) \times L_{1,\text{norm}}(S_t)}$$
Where:
- $T_{BO1}(S_t) = \frac{100}{1 + \exp\left( - 1.1 \left[ 0.50 \left(\frac{\text{CRR}_t - R_{\text{par}}}{R_{\text{par}}}\right) + 0.35 \left(\frac{10 - W_t - \mu_{W_{\text{rem}}}(L_t)}{\sigma_W}\right) + 0.15 \cdot \text{PhaseDefensiveFactor} \right] \right)}$
- $L_{1,\text{norm}}(S_t)$ is identically evaluated from the pre-delivery match consequence.

### 6.4 Bowling Model 2: Second-Innings Bowling Pressure ($P_{BO2}$)
$$P_{BO2}(S_t) = \sqrt{T_{BO2}(S_t) \times L_{2,\text{norm}}(S_t)}$$
Where:
- $T_{BO2}(S_t) = \frac{100}{1 + \exp\left( - 1.0 \left[ 0.60 \left(\frac{8.1 - \text{RRR}_t}{3.0}\right) + 0.40 \left(\frac{10 - W_t - \mu_{W_{\text{rem}}}(B_{\text{rem}})}{\sigma_W}\right) \right] \right)}$
- $L_{2,\text{norm}}(S_t)$ is evaluated identically from the pre-delivery match consequence (using Markov final-ball evaluation if $B_{\text{rem}} = 1$).

---

## 7. Cricket Scenario Validation Matrix

To verify that the mathematical formulation produces defensible results across the full spectrum of T20 match situations, we evaluate the 10 mandated benchmark scenarios:

### Table 7.1: Scenario Validation Evaluation Matrix
| # | Match Scenario | Match State ($S_t$) | Task Difficulty ($T$) | Match Consequence ($L_{\text{norm}}$) | Pressure Score ($P = \sqrt{T \cdot L}$) | Cricket Interpretation & Sanity Check |
| :-: | :--- | :--- | :---: | :---: | :---: | :--- |
| **1** | **First over of innings (0.1)** | Inn 1, 0/0, Over 0.1, Par 165 | $50.0$ (Neutral) | $45.2$ (Standard) | **47.5** | **PASS.** Baseline opening pressure. Neither artificially zero nor distortedly high. Openers face true match reality. |
| **2** | **Established batter in crisis** | Inn 2, Chasing 175, 110/5 at 15.0 ov. Needs 65 off 30 ($RRR=13.0$). Batter has 50*(35). | $82.4$ (High RRR, 5 down) | $78.1$ (Critical phase) | **80.2** | **PASS.** Completely eliminates legacy flaw! Legacy PI assigned ZERO pressure because balls faced $\ge 10$. New model reflects intense match reality. |
| **3** | **New batter entering in collapse** | Inn 1, 15/3 after 2.4 ov, Par 170. Incoming batter on 0*(0). | $86.5$ (Severe crisis) | $76.2$ (High wicket swing) | **81.2** | **PASS.** Captures top-order collapse pressure accurately. Batter must rebuild without throwing away match. |
| **4** | **High-scoring 1st innings death** | Inn 1, 175/2 at 16.0 ov, Par 180. CRR = 10.9, 8 wkts in hand. | $38.2$ (Abundant resources) | $52.0$ (Surplus value) | **44.6** | **PASS.** Prevents death overs with 2 down from being scored as extreme crisis. Batters have total license to attack freely. |
| **5** | **Difficult chase, many overs left** | Inn 2, Chasing 190, 60/4 after 8.0 ov. Needs 130 off 72 ($RRR=10.8$). | $84.1$ (Steep rate, 4 down) | $64.5$ (Long horizon) | **73.6** | **PASS.** Reflects sustained high tactical pressure over extended overs. |
| **6** | **12 runs required from 6 balls** | Inn 2, Chasing 180, 168/5 at 19.0 ov. Needs 12 off 6, 5 down. | $74.5$ ($RRR=12.0$) | $98.5$ (Peak climax) | **85.7** | **PASS.** Peak climax pressure. Every legal ball or boundary creates massive WP swing under Markov model. |
| **7** | **2 runs required from 30 balls** | Inn 2, Chasing 152, 150/2 at 15.0 ov. Needs 2 off 30, 8 down. | $2.1$ (Trivial task) | $4.8$ (Decided match) | **3.2** | **PASS.** Near-zero pressure. Completely eliminates dead-rubber stat-padding. |
| **8** | **Impossible chase (Blowout)** | Inn 2, Chasing 185, 105/8 at 18.0 ov. Needs 80 off 12 ($RRR=40.0$). | $99.2$ (Impossible task) | $0.8$ (Zero WP swing) | **8.9** | **PASS.** Eliminates garbage-time slogging. High difficulty does not create false pressure when game is lost. |
| **9** | **Defending small target** | Inn 2, Defending 125, opposition 45/3 at 7.0 ov ($RRR=6.2$). | $68.4$ (Low run cushion) | $74.2$ (High wicket value) | **71.2** | **PASS.** Accurately credits bowling unit defending low totals where every run conceded is costly. |
| **10** | **Bowler entering with 0 prior balls** | Bowler's 1st over is Over 17, defending 35 off 24 balls against set batters. | $78.0$ (High execution demand) | $84.0$ (Death climax) | **80.9** | **PASS.** Evaluated strictly on match state. Bowler receives full pressure credit regardless of individual spell workload. |

---

## 7. Bias Auditing & Mitigations

We rigorously evaluate four potential structural biases:

### 7.1 Batting-Position Bias
- **Historical Pathology:** The legacy Pressure Index penalized top-order batters (openers and No. 3) because innings balls elapsed was low, and artificially rewarded finishers who faced fewer than 10 balls.
- **Methodological Mitigation:** 
  1. Complete excision of the individual balls-faced penalty factor $I_t$.
  2. $T_{B1}$ evaluates wicket losses relative to the expected wicket distribution for that over. An opener facing swinging balls at 0/0 faces a baseline pressure of $\approx 47.5$, not zero.
  3. If early wickets fall (e.g. 15/3), both the surviving opener and incoming batter receive high crisis pressure ($\approx 81.2$).
  4. In Innings 2, openers chasing steep totals (e.g. 210) receive elevated pressure immediately from ball 0.1 ($\text{RRR} = 10.5 \implies P_{B2} \approx 65$).

### 7.2 Death-Over Bias
- **Historical Pathology:** Raw Win Probability Added (WPA) or un-normalized leverage concentrates over $85\%$ of all match pressure into overs 18–20.
- **Methodological Mitigation:**
  1. Intra-innings normalization ensures that high-pressure powerplay moments (rebuilding after a collapse) scale to $[75, 90]$ just like close finishes.
  2. The geometric combination requires task difficulty to be non-trivial. Death overs in blowout chases (needs 80 off 12) drop to $P < 10$.
  3. Batting at 180/2 in the death overs drops to moderate pressure ($P \approx 44$) because task difficulty is low due to wicket abundance.

### 7.3 Bowling-Role Bias
- **Historical Pathology:** Spinners bowling in middle overs (overs 7–15) were heavily undervalued compared to pace bowlers operating in the powerplay and death.
- **Methodological Mitigation:**
  1. Consequence in the middle overs accounts for wicket-taking leverage: taking a top-order wicket at over 11 breaks partnerships and alters projected score by 18–25 runs.
  2. Bowling task difficulty $T_{BO1}$ explicitly rewards bowlers who restrict scoring when the opposition has wickets in hand.
  3. A spinner bowling overs 8, 10, 12, 14 against a rampant batting lineup at 95/1 receives high bowling pressure ($\approx 68-75$).

### 7.4 Sample-Size Sensitivity & Downstream Integration
- **Preserved Downstream Thresholds:**
  - Individual delivery pressure $P(S_t)$ is aggregated into player-level pressure weights.
  - The Rule B qualification thresholds ($\ge 120$ balls faced for batting, $\ge 120$ balls bowled for bowling) ensure no player qualifies on a handful of high-pressure deliveries.
  - Bayesian Shrinkage with $K = 50$ shrinks small-sample outliers toward the population prior, preventing noisy ranking spikes.

---

## 8. Classification of Architectural Decisions

In accordance with project governance, every design decision is classified into one of four formal categories:

### Table 8.1: Design Decisions Classification Table
| Decision ID | Architectural Component | Formal Status | Rigorous Justification & Governance Evidence |
| :--- | :--- | :---: | :--- |
| **DEC-01** | **Pre-Delivery Information Boundary** | `ACCEPTED` | Strict boundary: $P(S_t)$ depends solely on state measurable at $t^-$. Prevents post-outcome data leakage. |
| **DEC-02** | **Dual-Axis Framework ($P = f(T, L)$)** | `ACCEPTED` | Separates athletic hardship from match impact. Prevents blowout and dead-rubber distortions. |
| **DEC-03** | **Certified 782-Match Pure Cohort** | `ACCEPTED` | Verified in Steps 2, 2.1, and 2.2. Excludes 4 DLS and 3 shortened matches. 186,634 deliveries. |
| **DEC-04** | **Exclusion of 233 Dead-Tail Deliveries** | `ACCEPTED` | Deliveries bowled after target reached ($R_t \le 0$) distort win probability denominators. |
| **DEC-05** | **Zero Data Fabrication for Missing Extras** | `ACCEPTED` | 101 matches with vendor-truncated multi-run extras are handled via recorded states without synthetic imputation. |
| **DEC-06** | **Discrete Markov Final-Ball Treatment ($B_{\text{rem}}=1$)** | `ACCEPTED` | Resolves collinear interaction inversion observed in continuous logistic RRR model at $B_{\text{rem}}=1$. |
| **DEC-07** | **Separate Intra-Innings Consequence Normalization** | `ACCEPTED` | Restores parity between Innings 1 baseline leverage ($\mu=0.024$) and Innings 2 climax leverage ($\mu=0.048$). |
| **DEC-08** | **Excision of Striker Balls-Faced Penalty ($I_t$)** | `ACCEPTED` | Eliminates legacy finisher bias and restores true pressure credit to set batters facing crises. |
| **DEC-09** | **Geometric Mean Combination ($P = \sqrt{T \cdot L}$)** | `ACCEPTED` | Enforces zero-product boundary invariant while preserving linear scaling across active pressure regions. |
| **DEC-10** | **Four Distinct Pressure Models ($P_{B1}, P_{B2}, P_{BO1}, P_{BO2}$)** | `ACCEPTED` | Accommodates tactical asymmetries between first/second innings and batting/bowling tasks. |
| **DEC-11** | **Preservation of BRS3, BoRS, $K=50$, Rule B** | `ACCEPTED` | Core competition downstream logic remains entirely intact in the pressure lab. |
| **DEC-12** | **Phase-Stratified Marginal Outcome Distributions** | `PROVISIONAL` | Phase/innings baselines are stable and leak-free; state-conditioned multinomial distributions can be tested in Step 4. |
| **DEC-13** | **Linear Par Benchmark Trajectory** | `PROVISIONAL` | ParScore $= \text{Par}_{\text{venue}} \times (L_t / 120)$ is robust; non-linear phase-weighted progression can be benchmarked. |
| **DEC-14** | **Linear Additive Combination ($0.5 T + 0.5 L$)** | `REJECTED` | Mathematically invalid: assigns moderate pressure ($P \approx 50$) to garbage-time blowouts. |
| **DEC-15** | **Post-Delivery WPA as Pre-Delivery Pressure** | `REJECTED` | Conflates execution quality with pre-delivery context. Violates causal ordering. |
| **DEC-16** | **Legacy Balls-Faced Intensity Formula ($I_t$)** | `REJECTED` | Unprincipled heuristic that artificially penalized top-order batters. |
| **DEC-17** | **Continuous RRR Logistic Model at $B_{\text{rem}}=1$** | `REJECTED` | Collinear interaction inversion flips probabilities for 9-wicket down teams. |
| **DEC-18** | **Un-Normalized Cross-Innings Consequence Pooling** | `REJECTED` | Completely drowns out first-innings pressure by an $8\times$ magnitude disparity. |
| **DEC-19** | **Optimal Asymmetric Power Exponents ($\alpha, \beta$)** | `UNRESOLVED` | Requires fine-tuning against empirical clutch validation in Step 4 to test if $L$ warrants higher exponent than $T$. |
| **DEC-20** | **Optimal Scaling Parameter for Bowler Defense ($k_{BO2}$)** | `UNRESOLVED` | The steepness parameter for bowling defense task difficulty requires empirical calibration in Step 4. |

---

## 9. Recommendations & Next Steps

### Summary of Recommendations:
1. **Approve the Methodology Architecture:** Adopt the dual-axis geometric formulation $P = \sqrt{T \cdot L}$ with the four distinct models ($P_{B1}, P_{B2}, P_{BO1}, P_{BO2}$) as the formal foundation for `supeRR_selector_pressure_lab`.
2. **Implement in Controlled Script Pipeline:** In Step 4, implement the feature extraction and calculation pipeline within `src/` as modular, test-backed Python scripts operating strictly on the certified 782-match cohort.
3. **Calibrate Unresolved Parameters via Validation Folds:** Tune provisional parameters (e.g. non-linear par curves, asymmetric exponents $\alpha, \beta$) using 5-fold match-held-out cross-validation to guarantee zero leakage.

---

### Strict Execution Halt
In accordance with user governance instructions:
- **No production code has been written.**
- **No player rankings have been calculated.**
- **No legacy formulas or files have been modified.**
- **Execution is halted immediately.** We await explicit user review and approval before proceeding to implementation.
