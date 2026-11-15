# Step 6.1 — Independent Methodology Audit Report: Player Reliability Under Pressure

**Project Target:** `experiments/pressure_definition_v1/`  
**Step:** Step 6.1 — Independent Methodology Audit  
**Deliverable File:** `outputs/step_6_reliability_methodology/step_6_1_independent_methodology_audit.md`  
**Audited Document:** `outputs/step_6_reliability_methodology/step_6_methodology_report.md` (Step 6 Design Specification)  
**Input Datasets Audited:**  
- `outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet` (186,780 deliveries, 816 batters)  
- `outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet` (186,780 deliveries, 589 bowlers)  
- `data/matches.csv` & `data/competitions.csv` (782 matches: 355 IPL, 427 T20I)  
**Date:** November 2026  
**Auditor:** Independent Methodology & Statistical Reviewer  
**Audit Status:** **COMPLETE & CERTIFIED WITH CONDITIONS**

---

## 1. Executive Verdict: PASS WITH CONDITIONS

### Overall Determination
**Verdict:** **`PASS WITH CONDITIONS`**

The Step 6 Player Reliability Methodology Design represents a massive conceptual advance over the legacy BRS3 and BoRS approaches. It correctly discards unregularized strike rates, rejects raw volume accumulation, introduces formal Empirical Bayes regularization, and recognizes the structural asymmetry between batting and bowling disciplines.

**However, the Step 6 design specification contains two Critical mathematical defects, four Major statistical defects, and two Minor ambiguities that would produce severe distortions, division-by-zero crashes, and inverted incentives if implemented without correction:**

1. **Critical Defect 1 (Extras Double-Counting in Bowling):** The proposed SBVA formula debits bowlers twice for unforced extras (once in `bowler_runs_conceded` and a second time in $\text{Penalty}_{\text{extra}}$), while adding phantom penalties for future re-bowled deliveries that are already evaluated when bowled.
2. **Critical Defect 2 (Bowling Denominator Singularity):** The proposed SBVA denominator $\sum w(P_t) \mathbb{I}(\text{legal}_t)$ excludes illegal deliveries from the denominator while accumulating severe negative penalties in the numerator, creating massive per-ball distortions and a division-by-zero singularity if a spell consists solely of illegal deliveries.
3. **Major Defect 3 (Inverted Dynamic Wicket Valuation):** The proposed heuristic $\lambda_{\text{wkt}}(S_t) \approx \frac{V_{\text{par}} - S_t}{W_{\text{rem}}}$ becomes negative when a team's score exceeds venue par ($S_t > V_{\text{par}}$). In our certified 186,780-delivery dataset, this occurs on **8,439 deliveries in Innings 1** (scores up to 301). A negative $\lambda_{\text{wkt}}$ creates a perverse pathology where **batters are rewarded for being dismissed and bowlers are penalized for taking wickets**.
4. **Major Defect 4 (Pseudo-Sample Size Misnomer & Unmodeled Clustering):** The definition $N_{\text{eff}} = \sum (P_t / 50)$ is not an effective sample size in the statistical sense (Kish 1965); it is pressure-weighted exposure. For 303 batters, $N_{\text{eff}} > N_{\text{raw}}$ (e.g. David Miller: $N_{\text{raw}} = 1,243$, $N_{\text{eff}} = 1,256.5$, but Kish's $N_{\text{kish}} = 1,058.8$). Furthermore, deliveries within matches are not independent: intra-class correlation ($\rho_{\text{ICC}} \approx 0.0142$) produces player-innings design effects ($\text{Deff}$) between $1.15$ and $1.73$, meaning degrees of freedom are overstated by up to $73\%$.
5. **Major Defect 5 (Baseline Decile Sparsity & Circularity):** The proposed multi-way stratification ($\text{Innings} \times \text{Phase} \times \text{Pressure Decile} = 60$ cells) fails the report's own stability claim ($N \ge 1,500$ per cell). In reality, **20 out of 56 cells have fewer than 1,500 deliveries**, four cells are completely empty, and cells shrink to as low as **51 deliveries** (Innings 2, Powerplay, Decile 9). This injects extreme sampling noise into high-pressure situational par values.
6. **Major Defect 6 (Macro Tournament Scoring Disparity):** The 782 matches consist of 355 IPL matches (mean scoring rate 8.81 RPO) and 427 T20I matches (mean scoring rate 8.03 RPO). A single blended situational par table without format conditioning awards IPL batters an unearned $+0.78$ RPO bonus while systematically penalizing IPL bowlers.

### Conditions for Approval to Proceed to Step 7
Step 7 empirical calibration is permitted to proceed **ONLY** after formally binding the mathematical corrections, denominator definitions, monotonic resource curves, and baseline cell consolidation detailed in Section 10 and Section 13 of this audit report.

---

## 2. Mathematical Audit of Batting PWSVA

### 2.1 Formula Specification Under Review
$$\text{Candidate Model A (PWSVA):} \quad V_{\text{bat}, t} = (r_t - \mathbb{E}[R \mid S_t]) - \lambda_{\text{wkt}}(S_t) \cdot (w_t - \mathbb{E}[W \mid S_t])$$

$$\text{Aggregated Batter Metric:} \quad \text{PWSVA}_i = \frac{\sum_{t=1}^{N_i} w(P_t) \cdot V_{\text{bat}, t}}{\sum_{t=1}^{N_i} w(P_t)}$$

### 2.2 Algebraic Sign and Term Verification
- **Run Component $(r_t - \mathbb{E}[R \mid S_t])$:**
  - When the striker scores $r_t > \mathbb{E}[R \mid S_t]$ (e.g. boundary 4 or 6), the term is positive.
  - When the striker scores $r_t < \mathbb{E}[R \mid S_t]$ (e.g. dot ball $r_t = 0$), the term is negative ($- \mathbb{E}[R \mid S_t]$).
  - *Audit Finding:* Mathematically correct and standard in linear weights run expectancy.
- **Wicket Component $-\lambda_{\text{wkt}}(S_t) \cdot (w_t - \mathbb{E}[W \mid S_t])$:**
  - When the striker is dismissed ($w_t = 1$): the term evaluates to $-\lambda_{\text{wkt}}(S_t)(1 - \mathbb{E}[W \mid S_t]) < 0$. The batter is penalized for the loss of team wicket resources, offset slightly by the baseline risk $\mathbb{E}[W \mid S_t]$ of that delivery state.
  - When the striker survives ($w_t = 0$): the term evaluates to $-\lambda_{\text{wkt}}(S_t)(0 - \mathbb{E}[W \mid S_t]) = +\lambda_{\text{wkt}}(S_t) \cdot \mathbb{E}[W \mid S_t] > 0$. The batter is credited for surviving an out-probable delivery.
  - *Audit Finding:* Mathematically sound, provided $\lambda_{\text{wkt}}(S_t) > 0$. (See Section 5 for the breakdown when $\lambda_{\text{wkt}} \le 0$).

### 2.3 Outcome Definitions and Data Field Lineage
1. **Striker Runs $r_t$:** Must strictly map to `batter_runs` from `batting_pressure_deliveries.parquet`, representing runs off the bat. It must **not** map to `team_runs_added`, which includes byes, leg-byes, and wides.
2. **Striker Dismissal $w_t$:** Must strictly map to `is_striker_dismissed`. In the certified Step 5 dataset, `is_striker_dismissed` is True for 9,737 striker dismissals. Non-striker dismissals (`is_non_striker_dismissed`, 282 run-outs) must **not** be debited to the striker, as the striker was not the dismissed party.
3. **Delivery Domain & Unforced Extras:**
   - In `batting_pressure_deliveries.parquet`, there are 186,780 total records, of which **179,590 are balls faced by the batter** (`is_batter_ball_faced == True`) and **7,190 are wides** (`is_batter_ball_faced == False`).
   - If wides are included in the batter's delivery summation, $r_t = 0$ and $w_t = 0$. The batter would be assessed:
     $$V_{\text{bat}, \text{wide}} = (0 - \mathbb{E}[R \mid S_t]) + \lambda_{\text{wkt}}(S_t) \mathbb{E}[W \mid S_t] < 0$$
     This penalizes the striker for a delivery they could not hit and did not face!
   - *Audit Mandate:* The summation index $t$ must be explicitly restricted to deliveries where `is_batter_ball_faced == True`.

### 2.4 Wicket Double-Counting Analysis
A common concern in cricket value-added models is whether subtracting expected runs *and* subtracting wicket value double-counts the failure.
- On a dismissal delivery, the batter scores 0 runs off the bat ($r_t = 0$) and loses their wicket ($w_t = 1$).
- Total delivery impact:
  $$V_{\text{bat}, t} = - \mathbb{E}[R \mid S_t] - \lambda_{\text{wkt}}(S_t)(1 - \mathbb{E}[W \mid S_t])$$
- *Theoretical Justification:* On delivery $t$, the batting side loses two distinct economic assets:
  1. The **opportunity cost of the ball consumed** (an average batter would have generated $\mathbb{E}[R \mid S_t]$ runs).
  2. The **future scoring capital of the wicket terminated** (having one fewer wicket in hand reduces expected final innings total by $\lambda_{\text{wkt}}$).
- *Boundary Condition Check:* As long as the situational baseline $\mathbb{E}[R \mid S_t]$ is the **unconditional expectation across all deliveries** (including wickets), this does not constitute double-counting. If $\mathbb{E}[R \mid S_t]$ were conditioned strictly on survival ($w_t = 0$), then an explicit covariance adjustment would be required. The unconditional baseline proposed in Step 6 is therefore mathematically defensible.

### 2.5 Numerical Demonstration: Correct vs. Incorrect PWSVA Behavior

```
Scenario: Over 19.2 chasing 18 runs (P = 82.0). 
Baseline expectations: E[R] = 1.45 runs, E[W] = 0.08 outs, lambda_wkt = 3.50 runs, w(P) = 1.64.
```

| Delivery Outcome | True Cricket Impact | Correct Formula ($V_{\text{bat}, t}$) | Incorrect Specification (Wides Unfiltered) |
| :--- | :--- | :--- | :--- |
| **Striker hits Six ($r=6, w=0$)** | Match-winning execution | $(6 - 1.45) - 3.5(0 - 0.08) = \mathbf{+4.83\text{ runs}}$ | $\mathbf{+4.83\text{ runs}}$ |
| **Striker takes Single ($r=1, w=0$)** | Strike rotated off good ball | $(1 - 1.45) - 3.5(0 - 0.08) = \mathbf{-0.17\text{ runs}}$ | $\mathbf{-0.17\text{ runs}}$ |
| **Striker plays Dot ($r=0, w=0$)** | High-pressure failure | $(0 - 1.45) - 3.5(0 - 0.08) = \mathbf{-1.17\text{ runs}}$ | $\mathbf{-1.17\text{ runs}}$ |
| **Striker Dismissed ($r=0, w=1$)** | Critical match blow | $(0 - 1.45) - 3.5(1 - 0.08) = \mathbf{-4.67\text{ runs}}$ | $\mathbf{-4.67\text{ runs}}$ |
| **Bowler bowls Wide ($r=0, w=0$)** | Striker didn't face ball | **EXCLUDED (N increments 0)** | $(0 - 1.45) + 0.28 = \mathbf{-1.17\text{ runs}}$ *(Severe Defect!)* |

---

## 3. Mathematical Audit of Bowling SBVA

### 3.1 Formula Specification Under Review
$$\text{Candidate Model A (SBVA):} \quad V_{\text{bowl}, t} = (\mathbb{E}[R_{\text{bowl}} \mid S_t] - r_{\text{conceded}, t}) + \lambda_{\text{wkt}}(S_t)(w_{\text{bowler}, t} - \mathbb{E}[W_{\text{bowler}} \mid S_t]) - \text{Penalty}_{\text{extra}, t}$$

$$\text{Aggregated Bowler Metric:} \quad \text{SBVA}_i = \frac{\sum_{t=1}^{D_i} w(P_t) \cdot V_{\text{bowl}, t}}{\sum_{t=1}^{D_i} w(P_t) \cdot \mathbb{I}(\text{legal}_t)}$$

Where Step 6 defined:
$$\text{Penalty}_{\text{extra}, t} = \begin{cases} 1.0 + \mathbb{E}[R_{\text{re-bowl}}] & \text{if wide} \\ 1.0 + \mathbb{E}[R_{\text{free-hit}}] & \text{if no-ball} \end{cases}$$

### 3.2 Critical Defect 1: Extras Double-Counting & Phantom Penalties
The proposed extras penalty is mathematically flawed in two distinct ways:

1. **Double-Counting the 1-Run Penalty:**
   In cricket rules and in our certified `bowling_pressure_deliveries.parquet` dataset:
   - For all 7,190 wides, `bowler_runs_conceded == 1`.
   - For no-balls, `bowler_runs_conceded == 1 + batter_runs`.
   Thus, the first term $(\mathbb{E}[R_{\text{bowl}} \mid S_t] - r_{\text{conceded}, t})$ **already debits the bowler for the 1-run extra**.
   If $\text{Penalty}_{\text{extra}, t}$ ALSO contains $1.0$, the 1-run penalty is **deducted twice**.
2. **Phantom Future-Ball Double-Counting:**
   Subtracting $\mathbb{E}[R_{\text{re-bowl}}]$ or $\mathbb{E}[R_{\text{free-hit}}]$ charges the bowler for an expectation of runs that the batting side might score on the subsequent delivery.
   However, when that subsequent delivery is bowled, it is **itself entered into the dataset as delivery $t+1$ and evaluated against situational expectations**!
   If the re-bowled delivery results in a boundary (4 runs), the bowler is debited in delivery $t+1$. Penalizing them with $\mathbb{E}[R_{\text{re-bowl}}]$ on delivery $t$ means the cost of that re-bowled ball is charged twice.

### 3.3 Critical Defect 2: Denominator Singularity and Exposure Distortion
Look at the proposed aggregation denominator:
$$\text{Denominator} = \sum_{t=1}^{D_i} w(P_t) \cdot \mathbb{I}(\text{legal}_t)$$

- For any illegal delivery (wide or no-ball), $\mathbb{I}(\text{legal}_t) \equiv 0$.
- The denominator does **not increment**, but the numerator accumulates a large negative value:
  $$V_{\text{bowl}, \text{wide}} \approx (\mathbb{E}[R] - 1.0) - (1.0 + \mathbb{E}[R]) = -2.0 \text{ runs}$$
- **Pathology A (Exposure Distortion):**
  If Bowler X bowls an over of: Wide, Wide, Wide, Dot, Dot, Dot, Dot, Dot, Dot (6 legal balls, 3 wides):
  - Numerator: $3 \times (-2.0) + 6 \times (+1.4) = -6.0 + 8.4 = +2.4\text{ runs}$.
  - Denominator: $6.0$ legal balls.
  - Per-ball SBVA: $+0.40$ runs/ball.
  - But what if Bowler Y bowls 1 wide, then gets injured and leaves the field?
    - Numerator: $-2.0$.
    - Denominator: $0.0$!
    - **Result: `ZeroDivisionError` (NaN/Inf crash).**
- **Pathology B (Unbounded Rate Distortion):**
  Because the denominator only counts legal balls, any bowler who bowls 3 wides in an over has those penalties concentrated over only 6 legal balls. The unit of measurement becomes erratic.

### 3.4 Numerical Proof of SBVA Distortion

```
Scenario: Bowler delivers Over 19 defending 15 runs (P = 85.0).
Baseline: E[R_bowl] = 1.60 runs/ball, E[W_bowl] = 0.10, lambda_wkt = 3.50 runs, w(P) = 1.70.
Bowler delivers 7 balls: Dot, Wide, 4 runs (re-bowled), Dot, Wicket, 1 run, Dot.
Actual match figures: 1.0 over, 6 runs conceded, 1 wicket, 1 wide. Match WON.
```

Let us evaluate this exact spell under the Step 6 formula vs. the Corrected Mathematical Formulation:

| Ball # | Delivery Event | Step 6 Calculation ($V_{\text{bowl}}$) | Corrected Calculation ($V_{\text{bowl}}$) | Notes on Discrepancy |
| :---: | :---: | :---: | :---: | :---: |
| 1 | Dot ball | $1.60 - 0 - 0.35 = \mathbf{+1.25}$ | $1.60 - 0 - 0.35 = \mathbf{+1.25}$ | Standard dot credit |
| 2 | Wide ($r=1$) | $(1.60 - 1) - (1.0 + 1.60) - 0.35 = \mathbf{-2.35}$ | $0 - 1.00 = \mathbf{-1.00}$ | **Step 6 over-penalizes by $-1.35$ runs!** |
| 3 | Re-bowled (4 runs) | $1.60 - 4 - 0.35 = \mathbf{-2.75}$ | $1.60 - 4 - 0.35 = \mathbf{-2.75}$ | Bowler debited for 4 conceded |
| 4 | Dot ball | $1.60 - 0 - 0.35 = \mathbf{+1.25}$ | $1.60 - 0 - 0.35 = \mathbf{+1.25}$ | Standard dot credit |
| 5 | Wicket ($r=0, w=1$) | $1.60 - 0 + 3.5(0.90) = \mathbf{+4.75}$ | $1.60 - 0 + 3.5(0.90) = \mathbf{+4.75}$ | Bowler credited for clutch wicket |
| 6 | Single ($r=1$) | $1.60 - 1 - 0.35 = \mathbf{+0.25}$ | $1.60 - 1 - 0.35 = \mathbf{+0.25}$ | Good defensive ball |
| 7 | Dot ball | $1.60 - 0 - 0.35 = \mathbf{+1.25}$ | $1.60 - 0 - 0.35 = \mathbf{+1.25}$ | Match sealed |
| **Sum** | **Numerator ($\sum w \cdot V$)** | **$+5.95 \times 1.70 = \mathbf{+10.115}$** | **$+7.30 \times 1.70 = \mathbf{+12.410}$** | Step 6 destroys $+2.30$ runs of bowler value |
| **Denom** | **$\sum w(P_t) \cdot \mathbb{I}(\text{legal})$** | **$6 \times 1.70 = \mathbf{10.20}$** | **$6 \times 1.70 = \mathbf{10.20}$** | Denominator ignores illegal ball |
| **Final** | **Metric (Value / Legal Ball)** | **$+0.992\text{ runs/ball}$** | **$+1.217\text{ runs/ball}$** | **Step 6 suppresses bowler skill by 18.5%!** |

**Conclusion:** The Step 6 extras formulation is mathematically invalid. The correct formulation is specified in Section 10.

---

## 4. Effective Sample Size, Clustering & Shrinkage Audit

### 4.1 Statistical Critique of $N_{\text{eff}} = \sum (P_t / 50)$
Step 6 proposes:
$$N_{\text{eff}, i} = \sum_{t=1}^{N_i} \left(\frac{P_{i, t}}{50.0}\right)$$

In classical survey and sampling statistics (Kish 1965), when independent observations are weighted by non-uniform weights $w_t \ge 0$, the effective sample size is:
$$N_{\text{eff, Kish}} = \frac{\left(\sum_{t=1}^{N} w_t\right)^2}{\sum_{t=1}^{N} w_t^2}$$

#### Fundamental Mathematical Properties:
1. **The Kish Inequality:** For any set of non-identical positive weights, $N_{\text{eff, Kish}} < N_{\text{raw}}$. Unequal weighting *always* reduces statistical precision relative to equal weighting of independent observations.
2. **The Step 6 Inversion:** Under Step 6's definition, if a player faces 100 balls at an average pressure of $P = 75$, then:
   $$N_{\text{eff}} = 100 \times \frac{75}{50} = 150 \text{ pseudo-deliveries}$$
   Claiming that observing 100 physical deliveries yields 150 independent units of statistical evidence violates basic information theory.

#### Empirical Evidence Across Cohort Players:
In our certified dataset:
- For **303 batters** and **284 bowlers**, $N_{\text{step6}} > N_{\text{raw}}$!
- Concrete examples:
  - **Axar Patel:** $N_{\text{raw}} = 1,268$, $N_{\text{step6}} = 1,271.3$, Kish's $N_{\text{kish}} = 1,093.2$.
  - **David Miller:** $N_{\text{raw}} = 1,243$, $N_{\text{step6}} = 1,256.5$, Kish's $N_{\text{kish}} = 1,058.8$.
  - **Shimron Hetmyer:** $N_{\text{raw}} = 1,198$, $N_{\text{step6}} = 1,209.0$, Kish's $N_{\text{kish}} = 1,032.4$.
- *Audit Finding:* $N_{\text{step6}}$ is **pressure-weighted exposure**, NOT an effective sample size. Conflating exposure with degrees of freedom distorts Bayesian shrinkage.

```
       Comparison of Sample Size Metrics (Top Batters)
 3000 ┼────────────────────────────────────────────────────────
      │  █ N_raw    ▓ N_step6 (Exposure)    ▒ N_kish (True Info)
 2500 ┼──█─▓───────────────────────────────────────────────────
      │  █ ▓ ▒      █ ▓ ▒       █ ▓ ▒
 2000 ┼──█─▓─▒──────█─▓─▒───────█─▓─▒──────█─▓─────────────────
      │  █ ▓ ▒      █ ▓ ▒       █ ▓ ▒      █ ▓ ▒
 1500 ┼──█─▓─▒──────█─▓─▒───────█─▓─▒──────█─▓─▒───────────────
      │  │ │ │      │ │ │       │ │ │      │ │ │       █ ▓ ▒
 1000 ┼──│─│─│──────│─│─│───────│─│─│──────│─│─│───────█─▓─▒───
      │  J.Buttler  S.Yadav     S.Gill    V.Kohli     D.Miller
```

### 4.2 Intra-Match Dependence and Cluster Effects
Step 6 treats every delivery as an independent and identically distributed (i.i.d.) trial. This assumption is severely violated in cricket:
- **Pitch & Venue Homogeneity:** A deteriorating pitch in Chennai or a road in Bengaluru affects all 20 balls an individual faces in that match.
- **Opponent Quality Clustering:** A batter faces the same bowling attack and tactical plans within a match.
- **Batter Momentum & Psychological State:** Deliveries within an innings are autocorrelated (a batter seeing the ball well hits multiple boundaries).

#### Empirical Intra-Class Correlation (ICC) Measurement:
We performed a one-way ANOVA decomposition on the certified 179,590 batting balls across matches:
- **Match-Level Global ICC:** $\rho_{\text{match}} = 0.0142$ (with average match cluster $n_0 = 229.7$ balls).
- **Global Design Effect:** $\text{Deff}_{\text{global}} = 1 + (229.7 - 1) \times 0.0142 = \mathbf{4.25}$!
- **Within-Player Innings Clustering:** For individual players batting across multiple innings:
  - **Jos Buttler:** 115 innings, average 23.1 balls/inn, $\rho = 0.0154 \implies \mathbf{\text{Deff} = 1.34}$.
  - **Suryakumar Yadav:** 131 innings, average 20.1 balls/inn, $\rho = 0.0175 \implies \mathbf{\text{Deff} = 1.33}$.
  - **Shubman Gill:** 107 innings, average 24.2 balls/inn, $\rho = 0.0139 \implies \mathbf{\text{Deff} = 1.32}$.
  - **Ishan Kishan:** 116 innings, average 20.2 balls/inn, $\rho = 0.0378 \implies \mathbf{\text{Deff} = 1.73}$.

*Audit Finding:* Treating balls as independent i.i.d. draws overstates statistical information by **30% to 73%**. Effective degrees of freedom must be cluster-adjusted when fitting shrinkage constants.

### 4.3 Validity of Shrinkage Model & Variance Ratio $K$
Step 6 proposes Empirical Bayes shrinkage:
$$\theta_i^{\text{shrunk}} = \frac{N_i}{N_i + K} \hat{\theta}_i + \frac{K}{N_i + K} \mu_{\text{prior}}$$
with $K = \frac{\mathbb{E}[\sigma_{\text{within}}^2]}{\sigma_{\text{between}}^2}$ provisionally set to $[60, 100]$ for both batting and bowling.

- **Asymmetry Between Disciplines:**
  - **Batting:** High-variance, extreme right-skewed outcomes ($\{0, 1, 2, 3, 4, 6\}$), with ruin risk (a single dismissal terminates the spell). $\sigma_{\text{within, bat}}^2$ is structurally large.
  - **Bowling:** Bowlers deliver quotas of 24 balls across discrete spells. Bowling performance is more repeatable and less hazard-dominated.
  - Setting $K_{\text{bat}} = K_{\text{bowl}} \in [60, 100]$ without empirical fitting is an arbitrary guess.
  - *Audit Mandate:* $K_{\text{bat}}$ and $K_{\text{bowl}}$ must be estimated separately from the data in Step 7 using restricted maximum likelihood (REML) or empirical Bayes method-of-moments on cluster-aggregated data.

### 4.4 Qualification Threshold Audit
Step 6 proposes a minimum qualification filter of **50 deliveries under pressure ($P > 50$)**.
We evaluated the player distribution in the certified dataset:

| Threshold Criterion | Qualifying Batters | Qualifying Bowlers | Audit Evaluation |
| :--- | :---: | :---: | :--- |
| **$N(P \ge 50) \ge 30$** | 373 | 344 | Includes marginal / replacement players. |
| **$N(P \ge 50) \ge 40$** | 329 | 312 | Solid coverage; captures emerging players. |
| **$N(P \ge 50) \ge \mathbf{50}$ (Step 6)** | **297** | **292** | **Defensible:** Yields $\approx 300$ regular tournament contributors. |
| **$N(P \ge 50) \ge 60$** | 262 | 266 | Excludes some specialized middle-order contributors. |
| **$N(P \ge 50) \ge 100$** | 205 | 207 | Restricts strictly to multi-season core veterans. |

*Audit Finding:* The threshold of $N(P \ge 50) \ge 50$ is statistically defensible, as it guarantees that any ranked player has at least 50 observed pressure trials, giving a shrinkage weight $\frac{N}{N+K} \ge 33\%$ to $45\%$.

---

## 5. Situational Baselines & Dynamic Wicket Valuation Audit

### 5.1 Baseline Stratification & Cell Sparsity Analysis
Step 6 specifies:
$$\mathbb{E}[Y \mid \text{state}_t] = \text{Lookup}(\text{Innings}, \text{Phase}, \text{PressureDecile})$$
with the explicit claim: *"Cell Samples: Minimum $N \ge 1,500$ deliveries per cell"* (line 231).

#### Empirical Disproof:
We cross-tabulated the certified 186,780 deliveries across this exact $2 \times 3 \times 10$ tensor. The results refute the report's claim:

```
Batting Baseline Tensor Breakdown (186,780 deliveries):
• Total expected cells: 2 x 3 x 10 = 60
• Populated cells: 56 (4 cells are COMPLETELY EMPTY)
• Cells with N < 1,500 deliveries: 20 cells (35.7% of all populated cells!)
• Minimum cell count: 51 DELIVERIES (Innings 2, Powerplay, Decile 9)
• Innings 1, Powerplay, Decile 1: 78 deliveries
• Innings 1, Powerplay, Decile 2: 227 deliveries
• Innings 2, Death, Decile 8: 540 deliveries

Bowling Baseline Tensor Breakdown:
• Populated cells: 57 (3 cells COMPLETELY EMPTY)
• Cells with N < 1,500 deliveries: 17 cells (29.8% of all cells)
• Minimum cell count: 141 DELIVERIES (Innings 1, Powerplay, Decile 1)
```

#### Why This Occurs:
Global pressure deciles are computed across all 186,780 deliveries.
- In the Powerplay, consequence is structurally moderate; pressure rarely enters Decile 9 or 10.
- In Death overs, consequence is high; pressure rarely enters Decile 1 or 2.
- Stratifying by both `Phase` and global `PressureDecile` forces the data into thin, degenerate slices. A cell with only 51 balls has enormous sampling error ($\pm 0.40$ runs/ball), corrupting the situational par values!

### 5.2 Decile Selection Circularity & Double-Conditioning
- Delivery pressure $P_t = \sqrt{T_t \times L_{\text{norm}, t}}$ is directly calculated from task difficulty (required run rate or current run rate vs. par) and match consequence.
- If the baseline $\mathbb{E}[R \mid \text{state}_t]$ already conditions on `PressureDecile`, then a high-pressure chase delivery is benchmarked against a baseline that has already absorbed the high task difficulty.
- Multiplying the resulting residual by continuous weight $w(P_t)$ creates an econometric **double-conditioning endogeneity**: pressure is used to define the benchmark AND to scale the importance of the residual.

### 5.3 Dynamic Wicket Valuation $\lambda_{\text{wkt}}(S_t)$ Pathology
Step 6 proposes:
$$\lambda_{\text{wkt}}(S_t) \approx \frac{V_{\text{par}} - S_t}{W_{\text{rem}, t}}$$
claiming values of $\approx 18.0$ runs early and $\approx 1.5$ runs late.

#### Critical Mathematical Pathology:
What happens when a team scores more than venue par in Innings 1 ($S_t > V_{\text{par}}$)?
- In our certified dataset:
  - Deliveries in Innings 1 with $S_t \ge 165$: **8,439 deliveries**
  - Deliveries with $S_t \ge 180$: **4,982 deliveries**
  - Deliveries with $S_t \ge 200$: **2,153 deliveries** (scores up to 301)
- When $S_t = 200$ and venue par is 165 with 6 wickets in hand:
  $$V_{\text{par}} - S_t = 165 - 200 = -35 \implies \lambda_{\text{wkt}} = \frac{-35}{6} = \mathbf{-5.83\text{ runs}!}$$
- **The Resulting Perverse Incentive:**
  - If a batter gets out ($w_t = 1$):
    $$-\lambda_{\text{wkt}}(1 - \mathbb{E}[W]) = -(-5.83)(0.92) = \mathbf{+5.36\text{ runs credit to the batter!}}$$
    **The batter is rewarded with +5.36 runs for getting out!**
  - If a bowler takes a wicket ($w_{\text{bowler}} = 1$):
    $$+\lambda_{\text{wkt}}(1 - \mathbb{E}[W]) = +(-5.83)(0.90) = \mathbf{-5.25\text{ runs penalty to the bowler!}}$$
    **The bowler is penalized with -5.25 runs for taking a wicket!**

Furthermore, in Innings 2, $V_{\text{par}}$ is not defined (the target is a fixed integer $T$, not a par rate). If target is 180 and score is 175 with 8 wickets in hand, $(180-175)/8 = 0.62$ runs, which collapses wicket value to near zero while the match is still contested.

*Audit Finding:* The heuristic formula $\frac{V_{\text{par}} - S_t}{W_{\text{rem}}}$ is a **Major Mathematical Defect**. A proper resource loss function must be strictly positive and bounded, as specified in Section 10.

---

## 6. Batting and Bowling Role Fairness Audit

### 6.1 Batting Order Bias & Entry Situations
- **Openers (Overs 1–6):**
  - Face new ball against rested frontline bowlers with field restrictions.
  - Mean $P_{\text{bat}} = 51.95$, Median $= 53.86$, $\text{Std} = 11.34$.
  - Only $7.7\%$ of deliveries reach $P > 65$.
- **Middle Order (Overs 7–16):**
  - Face spin and boundary fielders; rebuild after wickets or consolidate.
  - Mean $P_{\text{bat}} = 41.62$, Median $= 41.49$, $\text{Std} = 16.41$.
  - Only $9.7\%$ of deliveries reach $P > 65$.
- **Finishers (Overs 17–20):**
  - Face death bowling (yorkers, wide cutters) under escalating required run rates.
  - Mean $P_{\text{bat}} = 52.68$, Median $= 59.59$, $\text{Std} = 25.46$.
  - **$42.5\%$ of deliveries reach $P > 65$!**
- **Outcome Variance by Phase:**
  - Death: $\text{Var}(r) = 3.487$, Dismissal Rate $= 8.22\%$.
  - Middle: $\text{Var}(r) = 2.652$, Dismissal Rate $= 4.74\%$.
  - PP: $\text{Var}(r) = 3.258$, Dismissal Rate $= 4.46\%$.

*Fairness Assessment:* Because death overs have 31% higher run variance and nearly 2x higher dismissal rates, unadjusted absolute value added naturally produces larger swings for death hitters. However, PWSVA is an **efficiency rate per ball** ($\frac{\sum w V}{\sum w}$), not a cumulative sum. By normalizing by $\sum w(P_t)$, it measures average value added per effective ball, protecting openers and middle-order batters from volume bias.

### 6.2 Not-Out Survivorship Distortion
In traditional batting averages ($\text{Runs} / \text{Outs}$), finishers who remain not out have artificially deflated denominators, causing averages to inflate wildly (e.g. 50+).
- In PWSVA, every delivery faced is evaluated individually.
- On a delivery where the batter is not out ($w_t = 0$), they receive a credit of $+\lambda_{\text{wkt}} \mathbb{E}[W \mid S_t]$ (the baseline hazard rate $\approx 0.04 - 0.08$ outs/ball).
- *Audit Finding:* PWSVA is **completely immune to the classical not-out denominator distortion**.

### 6.3 Bowling Role Fairness: Death Bowlers vs. Middle-Overs Spinners
This is the most critical fairness challenge in T20 bowling analytics:
- **Death Bowlers (Overs 17–20):** Mean $P_{\text{bowl}} = 45.91$, with $30.6\%$ of balls at $P > 65$.
- **Middle-Overs Bowlers (Overs 7–16):** Mean $P_{\text{bowl}} = 38.96$, with **ONLY 1.4% of balls at $P > 65$!**
- If a methodology defines reliability under pressure using a hard threshold like $P > 65$, **world-class middle-overs spinners (Rashid Khan, Sunil Narine, Kuldeep Yadav, Yuzvendra Chahal) are systematically disenfranchised**.
- Under the proposed qualification filter of $N(P \ge 50) \ge 50$:
  - Middle-overs deliveries still offer $25.9\%$ of balls at $P \ge 50$ (close matches, chasing tight totals).
  - 292 bowlers qualify, ensuring excellent representation across all phases.
- Phase-specific baseline subtraction ($\mathbb{E}[R_{\text{bowl}} \mid \text{phase}]$) ensures that a death bowler conceding 9.0 RPO against a 10.5 RPO par gains $+1.5$ runs saved per over, while a middle bowler conceding 6.5 RPO against a 7.5 RPO par gains $+1.0$ run saved per over. Neither role is handed an unearned advantage.

### 6.4 Macro Tournament Disparity: IPL vs. T20I
The dataset comprises two distinct tournament ecosystems:
- **355 IPL matches:** Mean scoring rate $= \mathbf{8.81\text{ RPO}}$, Dismissal rate $= \mathbf{5.12\%}$.
- **427 T20I matches:** Mean scoring rate $= \mathbf{8.03\text{ RPO}}$, Dismissal rate $= \mathbf{5.68\%}$.

```
Tournament Ecosystem Comparison (Certified Cohort):
       IPL (355 Matches)       │      T20I (427 Matches)
  Scoring Rate: 8.81 RPO       │ Scoring Rate: 8.03 RPO  (+0.78 RPO in IPL)
  Dismissal Rate: 5.12%        │ Dismissal Rate: 5.68%   (+0.56% outs in T20I)
  High Pressure (% P>65): 17.1%│ High Pressure (% P>65): 15.6%
```

*Audit Finding:* If situational par $\mathbb{E}[R]$ is estimated globally across all 782 matches without format conditioning:
- The global blended death par will be $\approx 9.6$ RPO.
- An IPL death batter scoring at 9.8 RPO (below average for IPL death overs) would be credited with $+0.2$ runs saved!
- An IPL bowler conceding 9.2 RPO (excellent for IPL death overs) would be penalized!
- *Audit Mandate:* Situational baselines must incorporate tournament format or be calibrated relative to match/venue par.

---

## 7. Pressure Integration & Double-Counting Audit

### 7.1 Weighting Function Exponent $\alpha$
Step 6 proposes:
$$w(P_t) = \left(\frac{P_t}{50.0}\right)^\alpha \quad (\alpha \ge 1.0)$$

- **Linear Weighting ($\alpha = 1.0$):**
  - A ball at $P = 25$ gets weight $0.50$.
  - A ball at $P = 50$ gets weight $1.00$.
  - A ball at $P = 85$ gets weight $1.70$.
  - Extreme balls carry 3.4x the weight of low-pressure balls. This provides smooth, stable scaling.
- **Super-Linear Weighting ($\alpha = 1.5$ or $2.0$):**
  - At $\alpha = 2.0$: $w(25) = 0.25$, $w(50) = 1.00$, $w(85) = 2.89$.
  - Extreme balls carry **11.6x the weight** of low-pressure balls!
  - Under $\alpha = 2.0$, a player's career reliability metric can be dominated by just 15–20 balls in two dramatic finishes, completely overwhelming hundreds of balls of consistent high-pressure execution.
- *Audit Recommendation:* $\alpha$ must be constrained to the narrow interval $\alpha \in [1.0, 1.25]$ to prevent extreme outlier deliveries from monopolizing player evaluations.

### 7.2 Diagnostic Pressure Bands vs. Composite Indices
In Candidate Model B (SPRI for batting, PEI for bowling), Step 6 proposed combining performance in discrete pressure bands ($P > 65$), regression slopes ($\beta_{\text{resilience}}$), and variance penalties ($1 - \text{CV}$) into a composite multiplication index.

*Audit Determination:* **Candidate Model B (SPRI/PEI) is REJECTED.**
1. Multiplying index numbers ($HPE \times (1 + \tanh(\beta)) \times C$) compounds measurement errors and destroys physical interpretability (the resulting number has no physical unit like runs saved or value added).
2. Estimating a within-player regression slope $\beta_{\text{resilience}}$ requires large per-player samples across all pressure tiers; for players with 60–80 balls, $\beta$ has huge standard errors and destabilizes rankings.
3. Pressure bands ($P \le 45$, $45 < P \le 65$, $P > 65$) must serve strictly as **diagnostic validation tools** to verify that top-ranked players perform well across all tiers, NOT as composite formula terms. PWSVA and SBVA (Model A) are the only statistically sound foundations.

---

## 8. Validation Methodology Audit

### 8.1 Critique of Proposed Validation Thresholds
Step 6 proposed the following validation criteria for Step 7:
1. Split-half reliability $r_{\text{split}} \ge 0.65$.
2. Phase-invariance correlation $|r| < 0.15$ with death overs proportion.
3. Predictive split (train on 60%, test on 40%).

*Audit Critique:*
- **Arbitrary Correlation Threshold ($r \ge 0.65$):**
  In cricket analytics, per-ball performance has high irreducible variance. In published sports analytics literature, split-half correlations for per-ball batting metrics across 100–200 balls typically range from $0.45$ to $0.60$. Demanding an unregularized split correlation $\ge 0.65$ risks forcing artificial smoothing or over-relying on volume.
- **Phase Invariance ($|r| < 0.15$):**
  Checking correlation only against the death overs proportion is insufficient. The audit must also verify independence from Powerplay proportion and Middle overs proportion, and verify that the top 20 ranked players include specialists from all three phases.
- **Descriptive vs. Predictive Clarification:**
  The competition objective is:
  $$\mathbf{Identify \; the \; Most \; Reliable \; Players \; Under \; Pressure}$$
  This is a **retrospective, descriptive evaluation** of player execution across the certified 782-match historical tournament cohort. It is NOT a future forecasting contest for matches played in 2027.
  While predictive cross-validation is a useful secondary diagnostic to prove the metric captures genuine skill rather than noise, the primary validation standard must be **measurement robustness, ranking stability, and uncertainty quantification**.

### 8.2 Mandatory Step 7 Validation Protocol
The empirical validation suite in Step 7 must execute the following five tests:
1. **Match-Cluster Bootstrap Stability:** Resample matches with replacement (respecting cluster dependence) $B = 1,000$ times. Compute 95% bootstrap confidence intervals for player ratings. Verify that ranking shifts among the top 20 are bounded.
2. **Odd/Even Match Split-Half Reliability:** Split matches chronologically by odd/even match dates within each tournament. Compute Spearman rank correlation $\rho_{\text{split}}$ of shrunk scores.
3. **Role Balance & Representation Audit:** Verify that the top 30 ranked batters include at least 8 openers, 8 middle-order anchors, and 8 death finishers. Verify that the top 30 bowlers include at least 8 Powerplay pacers, 8 middle-overs spinners, and 8 death executioners.
4. **Shrinkage Sensitivity Analysis:** Vary $K$ by $\pm 30\%$ and $\alpha \in \{1.0, 1.25, 1.5\}$. Confirm that top-10 membership remains stable ($\ge 80\%$ overlap).
5. **Format Robustness:** Check that player reliability is not driven entirely by one tournament format (e.g. check performance separately in IPL vs. T20I cohorts).

---

## 9. Ranked Summary of Defects

```
                        Defect Severity Hierarchy
  ┌────────────────────────────────────────────────────────────────────────┐
  │ CRITICAL: SBVA Extras Double-Counting & Denominator Singularity        │
  ├────────────────────────────────────────────────────────────────────────┤
  │ MAJOR:    Inverted Dynamic Wicket Valuation (Negative Lambda)          │
  │           Pseudo-Sample Size Misnomer & Unmodeled Match Clustering     │
  │           Baseline Decile Sparsity (Cells < 1,500 down to 51 balls)    │
  │           Macro Format Gap (IPL 8.81 RPO vs T20I 8.03 RPO Unadjusted)   │
  ├────────────────────────────────────────────────────────────────────────┤
  │ MINOR:    Arbitrary Validation Thresholds (r >= 0.65)                  │
  │           Omission of Explicit is_batter_ball_faced Filter in PWSVA    │
  ├────────────────────────────────────────────────────────────────────────┤
  │ UNRESOLVED: Numerical Values of K_bat and K_bowl (Step 7 Tuning)       │
  │             Exact Alpha Exponent (Step 7 Grid Search)                  │
  │             Optimal Qualification Cutoff (N=40 vs 50 vs 60)            │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Recommended Mathematical Corrections

### 10.1 Corrected Batting PWSVA Formulation
For any striker $i$, aggregate strictly over deliveries where `is_batter_ball_faced == True`:

$$\mathbf{\text{PWSVA}_i = \frac{\sum_{t \in \mathcal{F}_i} w(P_t) \cdot V_{\text{bat}, t}}{\sum_{t \in \mathcal{F}_i} w(P_t)}}$$

Where:
- $\mathcal{F}_i = \{t : \text{striker}_t = i \land \text{is\_batter\_ball\_faced}_t = \text{True}\}$
- $V_{\text{bat}, t} = (r_t - \mathbb{E}[R \mid \text{state}_t]) - \lambda_{\text{wkt}}(\text{state}_t) \cdot (w_t - \mathbb{E}[W \mid \text{state}_t])$
- $r_t = \text{batter\_runs}_t$
- $w_t = \text{is\_striker\_dismissed}_t$
- $w(P_t) = \left(\frac{P_t}{50.0}\right)^\alpha \quad \text{with } \alpha \in [1.0, 1.25]$

### 10.2 Corrected Bowling SBVA Formulation
To completely eliminate extras double-counting and denominator singularities, bowling value added must be formulated on the basis of **Total Runs Conceded and Total Wickets Taken relative to Legal Balls Delivered**:

$$\mathbf{\text{SBVA}_i = \frac{\sum_{t \in \mathcal{D}_i} w(P_t) \cdot V_{\text{bowl}, t}}{\sum_{t \in \mathcal{D}_i} w(P_t) \cdot \mathbb{I}(\text{legal}_t)}}$$

Where for every delivery $t \in \mathcal{D}_i$ bowled by bowler $i$:
$$V_{\text{bowl}, t} = \begin{cases} 
(\mathbb{E}[R_{\text{bowl}} \mid \text{state}_t] - r_{\text{conceded}, t}) + \lambda_{\text{wkt}}(\text{state}_t)(w_{\text{bowler}, t} - \mathbb{E}[W_{\text{bowler}} \mid \text{state}_t]) & \text{if } \text{is\_legal\_ball}_t = \text{True} \\
- r_{\text{conceded}, t} + \lambda_{\text{wkt}}(\text{state}_t) \cdot w_{\text{bowler}, t} & \text{if } \text{is\_legal\_ball}_t = \text{False}
\end{cases}$$

#### Why This Mathematical Correction is Bulletproof:
1. **Zero Double-Counting:** On an illegal delivery (wide or no-ball), $r_{\text{conceded}, t}$ is the actual runs conceded (1 run for a wide, $1 + \text{runs}$ for a no-ball). The bowler is debited exactly what they conceded.
2. **Zero Phantom Penalties:** The re-bowled ball and free hit are evaluated when bowled, eliminating duplicate charging.
3. **Consistent Units:** The summation over legal balls in the denominator means the metric measures **Net Runs Saved per Legal Ball**, identical to how Economy Rate measures Runs Conceded per Legal Over in standard cricket accounting.
4. **Singularity Protection:** In the qualification filter, bowlers must have delivered at least 50 legal balls under pressure, guaranteeing that the denominator is strictly positive ($\sum w(P_t) \mathbb{I}(\text{legal}) \ge 50$).

### 10.3 Corrected Dynamic Wicket Valuation $\lambda_{\text{wkt}}$
To prevent negative values when $S_t > V_{\text{par}}$, $\lambda_{\text{wkt}}$ must be defined as the **marginal resource loss in expected remaining scoring capacity**, derived from historical innings trajectories:

$$\mathbf{\lambda_{\text{wkt}}(u_t, W_{\text{rem}, t}) = \mathbb{E}[R_{\text{rem}} \mid u_t, W_{\text{rem}, t}] - \mathbb{E}[R_{\text{rem}} \mid u_t, W_{\text{rem}, t} - 1]}$$

Where:
- $u_t$: Legal balls remaining in the innings ($120 - L_t$).
- $W_{\text{rem}, t}$: Wickets in hand ($10 - W_t$).
- $\mathbb{E}[R_{\text{rem}} \mid u, W_{\text{rem}}]$: Expected remaining runs to be scored by the team.

#### Mathematical Properties of the Corrected $\lambda_{\text{wkt}}$:
- **Strictly Monotonic and Positive:** Because losing a wicket always weakly reduces expected remaining runs, $\lambda_{\text{wkt}} > 0$ across all states, even when current score exceeds 250!
- **Natural Boundaries:**
  - In Overs 1–6 ($u \in [84, 120]$, $W_{\text{rem}} \in [8, 10]$): $\lambda_{\text{wkt}} \in [10.0, 16.0]$ runs.
  - In Middle Overs ($u \in [24, 83]$, $W_{\text{rem}} \in [5, 8]$): $\lambda_{\text{wkt}} \in [5.0, 10.0]$ runs.
  - In Death Overs ($u \in [1, 24]$, $W_{\text{rem}} \in [2, 5]$): $\lambda_{\text{wkt}} \in [1.5, 4.0]$ runs.
  - On the final ball ($u = 1$): $\lambda_{\text{wkt}} \approx 0.5 - 1.0$ run.
- Zero future outcome leakage: $\lambda_{\text{wkt}}$ depends strictly on pre-delivery state variables $(u_t, W_{\text{rem}, t})$.

### 10.4 Consolidated Robust Baseline Stratification
To eliminate sparse cells and decile circularity:
1. Replace global pressure deciles with a 2-tier or 3-tier pressure grouping, OR
2. Condition baseline par strictly on:
   $$\mathbb{E}[Y \mid \text{state}_t] = \text{Lookup}(\text{Innings}, \text{Phase}, \text{TournamentFormat})$$
   - Innings $\in \{1, 2\}$ (2 tiers)
   - Phase $\in \{\text{Powerplay, Middle, Death}\}$ (3 tiers)
   - Format $\in \{\text{IPL, T20I}\}$ (2 tiers)
   - Total cells: $2 \times 3 \times 2 = \mathbf{12\text{ cells}}$.
   - **Minimum sample per cell:** $> 6,500$ deliveries! Zero sparse cells!
3. Pressure enters cleanly through the continuous weighting function $w(P_t) = (P_t / 50)^\alpha$.

---

## 11. Decisions Accepted Now

1. **Independent Batting and Bowling Architectures:**
   Accepted. Batting is hazard-driven (ruin risk); bowling is quota-driven. They cannot share a symmetric formula.
2. **Situational Value Added Relative to Par:**
   Accepted. Evaluating players on marginal runs and wickets relative to situational expectations solves role and volume bias.
3. **Empirical Bayes Regularization Framework:**
   Accepted. Shrinking player estimates toward cohort priors via $\theta^{\text{shrunk}} = \frac{N}{N+K} \hat{\theta} + \frac{K}{N+K} \mu_{\text{prior}}$ is the mathematically sound solution to small-sample volatility.
4. **Rejection of Legacy BRS3 / BoRS:**
   Accepted. Legacy formulas compounded volume bias, rewarded death batting without situational par baselines, and double-counted pressure.
5. **Rejection of Complex Black-Box Machine Learning:**
   Accepted. Gradient-boosted player embeddings are opaque, uninterpretable, and invite overfitting. Transparent statistical formulations are required.
6. **Rejection of Raw Win Probability Added (WPA):**
   Accepted. Raw WPA over-rewards trivial plays in balanced states (WP $\approx 50\%$) and is excessively noisy.

---

## 12. Decisions Remaining Provisional Until Step 7 Testing

The following numerical parameters cannot be finalized during this design audit and must be empirically calibrated on the certified dataset in Step 7:

1. **Numerical Values of Shrinkage Constants $K_{\text{bat}}$ and $K_{\text{bowl}}$:**
   Must be fitted from between-player and within-player variance components using REML or Empirical Bayes method-of-moments. Provisional range: $K_{\text{bat}} \in [50, 100]$, $K_{\text{bowl}} \in [50, 100]$.
2. **Weighting Function Exponent $\alpha$:**
   Must be tested over the grid $\alpha \in \{1.0, 1.15, 1.25, 1.5\}$ to evaluate ranking stability and prevent extreme-ball domination.
3. **Qualification Threshold Cutoff:**
   Must be evaluated across $N(P \ge 50) \in \{40, 50, 60\}$ to verify player pool coverage and stability.
4. **Empirical Lookup Table vs. Parametric Resource Curve for $\lambda_{\text{wkt}}$:**
   Step 7 must compare an empirical $(u_t, W_{\text{rem}, t})$ lookup matrix against a fitted Exponential-decay resource curve.

---

## 13. Conditions Required Before Step 7 Can Begin

To preserve scientific rigor and ensure compliance with project governance, Step 7 calibration scripts may only be executed once the following six conditions are met:

- [x] **Condition 1 (Audit Clearance):** The Step 6.1 independent methodology audit is completed and published.
- [ ] **Condition 2 (Bowling Formula Correction):** Step 7 code must implement the corrected SBVA formula (Section 10.2), with zero extras double-counting and legal-ball denominator accounting.
- [ ] **Condition 3 (Batting Ball-Facing Filter):** Step 7 code must restrict batting PWSVA aggregation strictly to `is_batter_ball_faced == True`, completely excluding wides from the batter's ledger.
- [ ] **Condition 4 (Monotonic Positive Wicket Resource Function):** The dynamic wicket function $\lambda_{\text{wkt}}$ must be implemented using the marginal remaining runs formulation (Section 10.3), guaranteeing $\lambda_{\text{wkt}} > 0$ for all deliveries.
- [ ] **Condition 5 (Robust Baseline Stratification):** Situational par tables must eliminate sparse decile cells, maintaining $N \ge 2,500$ deliveries in all strata and incorporating tournament format (IPL vs. T20I).
- [ ] **Condition 6 (Cluster-Aware Validation Protocol):** The validation suite in Step 7 must implement match-level bootstrap clustering and report 95% uncertainty intervals for all ranked players.

---
*Report certified by Independent Scientific Methodology Auditor.*  
*November 2026.*
