"""
Step 10.4 Methodology Report Restoration & PDF Compilation Pipeline
Corrects Sections 3 and 4 to accurately reflect the frozen Step 3 and Step 4 Python codebase:
- Master Geometric Mean: P = sqrt(T * L_norm) in [0, 100]
- All 4 Task Difficulty Models (T_B1, T_B2, T_BO1, T_BO2) with exact standardization, coefficients, and logistic functions
- Expected Absolute Match Consequence over 9 discrete outcomes: L(S_t) = sum P(o) |Delta WP|
- Separate Innings-Stratified ECDF Normalization (ECDF_1 and ECDF_2)
- Exact 12-page PDF compilation with publication typography
"""

import os
import sys
import gc
import pandas as pd
import pymupdf

def build_step10_4_report():
    print("=" * 80)
    print("STEP 10.4 METHODOLOGY REPORT GENERATION & COMPILATION")
    print("=" * 80)

    # 1. Load Authoritative Step 7.4 CSVs
    bat_csv_path = 'outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_batting_rankings.csv'
    bowl_csv_path = 'outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_bowling_rankings.csv'

    df_bat = pd.read_csv(bat_csv_path).head(10)
    df_bowl = pd.read_csv(bowl_csv_path).head(10)
    print(f"Loaded {len(df_bat)} batting rows and {len(df_bowl)} bowling rows.")

    # 2. Build Markdown Top 10 Tables
    md_bat_table = """```
========================================================================================================================
Rank  Player                  Team / Franchise            Shrunk Score  Raw Score  Raw Balls  Kish ESS  95% Bootstrap CI
========================================================================================================================
"""
    for idx, row in df_bat.iterrows():
        rank = f"#{int(row['Rank'])}"
        player = row['Player']
        team = row['Team/format']
        shrunk = f"{float(row['Shrunk score']):+.4f}"
        raw = f"{float(row['Raw score']):+.4f}"
        balls = str(int(row['Raw opportunities']))
        ess = f"{float(row['Kish ESS']):.1f}"
        ci = str(row['95% CI']).strip()
        md_bat_table += f"{rank:<5} {player:<23} {team:<27} {shrunk:>12} {raw:>10} {balls:>10} {ess:>9}  {ci}\n"
    md_bat_table += "========================================================================================================================\n```"

    md_bowl_table = """```
========================================================================================================================
Rank  Player                  Team / Franchise            Shrunk Score  Raw Score  Legal Balls Kish ESS 95% Bootstrap CI
========================================================================================================================
"""
    for idx, row in df_bowl.iterrows():
        rank = f"#{int(row['Rank'])}"
        player = row['Player']
        team = row['Team/format']
        shrunk = f"{float(row['Shrunk score']):+.4f}"
        raw = f"{float(row['Raw score']):+.4f}"
        balls = str(int(row['Raw opportunities']))
        ess = f"{float(row['Kish ESS']):.1f}"
        ci = str(row['95% CI']).strip()
        md_bowl_table += f"{rank:<5} {player:<23} {team:<27} {shrunk:>12} {raw:>10} {balls:>10} {ess:>9}  {ci}\n"
    md_bowl_table += "========================================================================================================================\n```"

    # 3. Build HTML Top 10 Tables (Booktabs Border Styling)
    html_bat_table = """<table class="report-table">
<thead>
<tr>
    <th style="width: 7%;">Rank</th>
    <th style="width: 23%;">Player Name</th>
    <th style="width: 24%;">Team / Franchise</th>
    <th style="width: 11%;">Shrunk Score</th>
    <th style="width: 10%;">Raw Score</th>
    <th style="width: 7%;">Balls</th>
    <th style="width: 8%;">Kish ESS</th>
    <th style="width: 10%;">95% Bootstrap CI</th>
</tr>
</thead>
<tbody>
"""
    for idx, row in df_bat.iterrows():
        rank = f"#{int(row['Rank'])}"
        player = row['Player']
        team = row['Team/format']
        shrunk = f"{float(row['Shrunk score']):+.4f}"
        raw = f"{float(row['Raw score']):+.4f}"
        balls = str(int(row['Raw opportunities']))
        ess = f"{float(row['Kish ESS']):.1f}"
        ci = str(row['95% CI']).strip()
        html_bat_table += f"""<tr>
    <td class="bold">{rank}</td>
    <td class="bold">{player}</td>
    <td>{team}</td>
    <td class="bold primary">{shrunk}</td>
    <td>{raw}</td>
    <td>{balls}</td>
    <td>{ess}</td>
    <td>{ci}</td>
</tr>
"""
    html_bat_table += "</tbody>\n</table>"

    html_bowl_table = """<table class="report-table">
<thead>
<tr>
    <th style="width: 7%;">Rank</th>
    <th style="width: 23%;">Player Name</th>
    <th style="width: 24%;">Team / Franchise</th>
    <th style="width: 11%;">Shrunk Score</th>
    <th style="width: 10%;">Raw Score</th>
    <th style="width: 7%;">Balls</th>
    <th style="width: 8%;">Kish ESS</th>
    <th style="width: 10%;">95% Bootstrap CI</th>
</tr>
</thead>
<tbody>
"""
    for idx, row in df_bowl.iterrows():
        rank = f"#{int(row['Rank'])}"
        player = row['Player']
        team = row['Team/format']
        shrunk = f"{float(row['Shrunk score']):+.4f}"
        raw = f"{float(row['Raw score']):+.4f}"
        balls = str(int(row['Raw opportunities']))
        ess = f"{float(row['Kish ESS']):.1f}"
        ci = str(row['95% CI']).strip()
        html_bowl_table += f"""<tr>
    <td class="bold">{rank}</td>
    <td class="bold">{player}</td>
    <td>{team}</td>
    <td class="bold primary">{shrunk}</td>
    <td>{raw}</td>
    <td>{balls}</td>
    <td>{ess}</td>
    <td>{ci}</td>
</tr>
"""
    html_bowl_table += "</tbody>\n</table>"

    # 4. Define Full Restored Markdown Text
    full_markdown_text = f"""# SupeRR Selector 2.0: Identifying the Most Reliable T20 Players Under Pressure
## A Dual-Dimensional Situational Value Framework with Empirical Bayes Shrinkage

**Author:** Antigravity Autonomous Analytics & Audit Team  
**Competition:** SupeRR Selector Season 2 — Round 1  
**Dataset Scope:** Ball-by-ball records from Men's T20 Competitions (IPL & T20I, 2022–2026, $N = 186,780$ deliveries)  
**Authoritative Source Baseline:** Frozen Step 7.4 Outputs (`outputs/step_7_empirical_calibration/step_7_4_final_rankings/`)  
**Publication Date:** November 2026  

---

## Section 1 — Executive Summary

### 1.1 The Challenge of Pressure Evaluation
In elite Twenty20 cricket, traditional evaluation metrics—such as raw batting strike rate, batting average, and bowling economy rate—fail to distinguish between low-stakes accumulation and performance delivered under acute match pressure. A boundary hit when requiring 6 runs off 2 balls carries vastly greater athletic and tactical value than a boundary hit in a decided blowout. Conversely, conceding a single boundary in a high-leverage death over does not reflect poor execution if the baseline expectancy in that situation is substantially worse.

To identify the **most reliable players under pressure**, we design and implement an end-to-end mathematical framework:
1. **Objective, Independent Pressure Quantification ($P_t \in [0, 100]$):** Pressure is decoupled from player identity and outcome, defined strictly pre-delivery ($t^-$) as the geometric mean of **Task Difficulty ($T_t$)** and **Normalized Match Consequence ($L_{\\text{{norm}}}(S_t)$)**.
2. **Situational Value Added (SVA):** Every delivery is evaluated against a discrete 36-cell empirical baseline tensor calibrated on 186,780 deliveries, computing runs and dismissals added relative to exact match state expectancy.
3. **Endgame Wicket Capping:** To eliminate mathematical distortion in late-inning run chases where required runs are low, effective wicket valuations are capped by remaining runs ($\lambda_{{\\text{{eff}}}} = \\min(\\lambda_{{\\text{{wkt}}}}, R_{{\\text{{req}}}})$).
4. **Quota-Based Bowling Normalization:** Conceded extras (wides and no-balls) are penalized in the numerator, while bowling opportunity rates are normalized strictly over legal deliveries.
5. **Empirical Bayes Shrinkage toward Zero Replacement Level:** Raw situational averages are regressed based on Kish's Effective Sample Size ($N_{{\\text{{eff}}}}$), preventing small-sample noise from dominating official leaderboards ($K_{{\\text{{bat}}}} = 600, K_{{\\text{{bowl}}}} = 500$).

### 1.2 Summary of Findings
Across 186,780 deliveries spanning 2022–2026:
- Exactly **297 batters** and **292 bowlers** met the sustained pressure eligibility threshold ($N(P \\ge 50) \\ge 50$).
- **Top Batting Performer:** **Vaibhav Sooryavanshi** ranks #1 (+0.3487 shrunk PWSVA), exhibiting extraordinary boundary hitting in high-pressure opportunities (raw +0.7614, Kish ESS = 506.9, retaining 45.8% of raw performance under rigorous shrinkage).
- **Consistently Elite Batting Volume:** **Suryakumar Yadav** ranks #2 (+0.2819 shrunk PWSVA, raw +0.3558, 2,638 balls, Kish ESS = 2,287.2) and **Abhishek Sharma** ranks #3 (+0.2703 shrunk PWSVA, raw +0.3547, 2,195 balls, Kish ESS = 1,923.3), maintaining elite positive value added across massive sample sizes.
- **Top Bowling Performer:** **Rashid Khan** ranks #1 (+0.1756 shrunk SBVA, raw +0.2147, 2,648 balls, Kish ESS = 2,245.9), followed closely by **Jasprit Bumrah** at #2 (+0.1541 shrunk SBVA, raw +0.2103, 1,606 balls, Kish ESS = 1,369.7) and **Sunil Narine** at #3 (+0.1442 shrunk SBVA, raw +0.2020, 1,464 balls, Kish ESS = 1,246.3).

### 1.3 Executive Leaderboards

#### Official Top 10 Batting Reliability Rankings (PWSVA)
{md_bat_table}

#### Official Top 10 Bowling Reliability Rankings (SBVA)
{md_bowl_table}

---

## Section 2 — Dataset and Scope

### 2.1 Scope of Data
The evaluation dataset is drawn from top-tier men's T20 cricket spanning January 1, 2022 through May 31, 2026:
- **Indian Premier League (IPL):** 365 matches (seasons 2022, 2023, 2024, 2025, and 2026).
- **Men's T20 Internationals (T20I):** All official ICC encounters among full-member nations and major ICC tournament fixtures.
- **Delivery Cohort:** 186,780 valid ball-by-ball deliveries across 742 unique matches.

### 2.2 Pre-Delivery Data Hygiene & State Representation
Every delivery is represented as a pre-delivery state vector $S_t = (I_t, B_{{\\text{{elapsed}}}}, B_{{\\text{{rem}}}}, R_{{\\text{{curr}}}}, R_{{\\text{{target}}}}, R_{{\\text{{req}}}}, W_t, W_{{\\text{{rem}}}}, \\text{{Phase}}_t, \\text{{Format}}_t, V_{{\\text{{venue}}}})$. Strict data hygiene ensures:
1. **Pre-Delivery Boundary ($t^-$):** All state variables are measured prior to ball release. Outcome variables (runs scored, wickets taken, extras) are strictly segregated from state inputs.
2. **Legal Delivery Synchronization:** Incomplete or interrupted matches are parsed through valid ball-by-ball logs. Super Overs are excluded from regular baseline calibration.
3. **Player Disambiguation:** Player identities are resolved via unique registry IDs, disambiguating identical names across franchise and international rosters.

### 2.3 Qualification Gate: $N(P \\ge 50) \\ge 50$
To eliminate volatile micro-samples while retaining genuine specialists, players qualify if and only if they faced or bowled at least **50 deliveries under elevated pressure ($P_i \\ge 50$)**. Exactly 297 batters and 292 bowlers satisfied this threshold.

---

## Section 3 — Defining Pressure: The Dual-Dimensional Framework

### 3.1 Foundational Philosophy
Traditional models conflate difficulty with consequence:
- A batter facing Jasprit Bumrah in the 19th over needing 24 runs faces extreme athletic difficulty *and* extreme consequence.
- A tailender batting in the 19th over needing 85 runs faces extreme difficulty, but near-zero consequence (the match is already lost).
- An opener playing a maiden over in the 1st innings faces moderate difficulty and moderate consequence.

True pressure exists **if and only if both difficulty and consequence are elevated**. If consequence is zero, difficult execution is merely garbage time. If difficulty is zero (e.g. needing 2 runs off 30 balls), elevated consequence is routine execution.

### 3.2 The Master Multiplicative Gating Principle
To enforce this orthogonal symmetry, delivery-level pressure ($P$) is defined as the geometric mean of Task Difficulty ($T$) and Normalized Match Consequence ($L_{{\\text{{norm}}}}$):
$$P(S_t) = \\sqrt{{T(S_t) \\times L_{{\\text{{norm}}}}(S_t)}} \\in [0, 100]$$

Where:
- $T(S_t) \\in [0, 100]$ evaluates the pre-delivery physical and tactical difficulty facing the player.
- $L_{{\\text{{norm}}}}(S_t) \\in [0, 100]$ evaluates the normalized win probability swing across all plausible delivery outcomes.
- Both components are computed strictly at $t^-$ (prior to ball release), completely eliminating outcome bias.
- **Scale Interpretation:**
  - $P < 25$: Low pressure / blowout / early innings baseline.
  - $25 \\le P < 50$: Moderate pressure / standard league baseline.
  - $50 \\le P < 75$: High pressure / match qualification territory ($N(P \\ge 50) \\ge 50$).
  - $P \\ge 75$: Climax pressure / death overs, crisis recovery, and tight finishes.

---

## Section 4 — Calculating Delivery-Level Pressure (Frozen Step 4 Engine)

### 4.1 Task Difficulty Formulation ($T$)
Task difficulty models tactical demand based on innings, match phase, wickets lost, and scoring rates relative to historical baselines (`05_task_difficulty_models.py`).

#### Batting Task Difficulty — Innings 1 ($T_{{\\text{{bat}}, 1}}$)
In Innings 1, batters maximize total score against baseline venue par ($V_{{\\text{{par}}}}$, default $176.68$ runs, baseline par rate $R_{{\\text{{par}}}} = V_{{\\text{{par}}}} / 20$):
1. **Required Acceleration Rate (RAR):** $\\text{{RAR}} = \\max\\left(0, \\frac{{V_{{\\text{{par}}}} - \\text{{Score}}}}{{B_{{\\text{{rem}}}} / 6}}\\right)$.
2. **Rate Stress:** $\\Delta R_{{B1}} = \\frac{{\\text{{RAR}} - R_{{\\text{{par}}}}}}{{R_{{\\text{{par}}}}}}$.
3. **Empirical Wicket Curve Stress:** $W_{{\\text{{stress}}}} = \\frac{{W_t - \\mu_W(L_t)}}{{\\sigma_W(L_t)}}$ (with $W_{{\\text{{stress}}}} = 0$ at ball 0), where $\\mu_W$ and $\\sigma_W$ are the empirical mean and standard deviation of wickets fallen at delivery $L_t$.
4. **Latent Index & Logistic Transformation:**
   $$Z_{{B1}} = 0.60 \\cdot \\Delta R_{{B1}} + 0.40 \\cdot W_{{\\text{{stress}}}}$$
   $$T_{{\\text{{bat}}, 1}} = \\frac{{100}}{{1 + \\exp(-1.2 \\cdot Z_{{B1}})}} \\in [0, 100]$$

#### Batting Task Difficulty — Innings 2 ($T_{{\\text{{bat}}, 2}}$)
In Innings 2, demand is dictated by Required Run Rate relative to remaining resources:
1. **Standardized RRR:** $\\text{{RRR}} = \\text{{clip}}\\left(\\frac{{R_{{\\text{{req}}}}}}{{B_{{\\text{{rem}}}}}} \\cdot 6, 0, 36\\right), \\quad Z_{{\\text{{RRR}}}} = \\frac{{\\text{{RRR}} - 8.10}}{{3.00}}$.
2. **Standardized Wickets Fallen:** $Z_W = \\frac{{W_t - 3.50}}{{2.00}}$.
3. **Centered Non-Linear Interaction:** $Z_{{\\text{{inter}}}} = \\frac{{\\text{{RRR}} \\cdot W_t - 28.0}}{{25.0}}$.
4. **Latent Index & Logistic Transformation:**
   $$Z_{{B2}} = 0.55 \\cdot Z_{{\\text{{RRR}}}} + 0.25 \\cdot Z_W + 0.20 \\cdot Z_{{\\text{{inter}}}}$$
   $$T_{{\\text{{bat}}, 2}} = \\frac{{100}}{{1 + \\exp(-1.0 \\cdot Z_{{B2}})}} \\in [0, 100]$$

#### Bowling Task Difficulty — Innings 1 ($T_{{\\text{{bowl}}, 1}}$)
Bowlers seek containment and wickets against opposition batting momentum:
1. **Conceded Current Run Rate:** $\\text{{CRR}} = \\frac{{\\text{{Score}}}}{{\\max(1, B_{{\\text{{elapsed}}}})}} \\cdot 6$ (or $R_{{\\text{{par}}}}$ at ball 0), $\\Delta \\text{{CRR}} = \\frac{{\\text{{CRR}} - R_{{\\text{{par}}}}}}{{R_{{\\text{{par}}}}}}$.
2. **Opponent Wicket Abundance:** $W_{{\\text{{opp}}}} = \\frac{{\\mu_W(L_t) - W_t}}{{\\sigma_W(L_t)}}$ (with $W_{{\\text{{opp}}}} = 0$ at ball 0).
3. **Phase Field Restriction Factor:** $\\text{{FieldFactor}} = 0.50$ (Powerplay and Death), $0.00$ (Middle).
4. **Latent Index & Logistic Transformation:**
   $$Z_{{BO1}} = 0.50 \\cdot \\Delta \\text{{CRR}} + 0.35 \\cdot W_{{\\text{{opp}}}} + 0.15 \\cdot \\text{{FieldFactor}}$$
   $$T_{{\\text{{bowl}}, 1}} = \\frac{{100}}{{1 + \\exp(-1.1 \\cdot Z_{{BO1}})}} \\in [0, 100]$$

#### Bowling Task Difficulty — Innings 2 ($T_{{\\text{{bowl}}, 2}}$)
Bowlers defend targets under chase pressure:
1. **Chase Comfort Defense Stress:** $\\text{{RRR}}_{{\\text{{stress}}}} = \\frac{{8.10 - \\text{{RRR}}}}{{3.00}}$ (capturing the extreme difficulty of halting an opponent cruising comfortably below par).
2. **Opponent Wicket Abundance:** $W_{{\\text{{opp}}}} = \\frac{{\\mu_W(L_t) - W_t}}{{\\sigma_W(L_t)}}$.
3. **Latent Index & Logistic Transformation:**
   $$Z_{{BO2}} = 0.60 \\cdot \\text{{RRR}}_{{\\text{{stress}}}} + 0.40 \\cdot W_{{\\text{{opp}}}}$$
   $$T_{{\\text{{bowl}}, 2}} = \\frac{{100}}{{1 + \\exp(-1.0 \\cdot Z_{{BO2}})}} \\in [0, 100]$$

---

### 4.2 Match Consequence Formulation ($L$) (`04_consequence_and_ecdf.py`)

#### Pre-Delivery Expected Match Consequence $L(S_t)$
Raw leverage is defined as the expected absolute swing in Win Probability across discrete delivery outcomes:
$$L(S_t) = \\sum_{{o \\in \\mathcal{{O}}}} P(o \\mid S_t) \\cdot \\big| \\text{{WP}}(S_{{t+1}}(o)) - \\text{{WP}}(S_t) \\big|$$
Where discrete outcome space $\\mathcal{{O}}$ consists of 9 mutually exclusive delivery events:
$$\\mathcal{{O}} = \\big\\{{ \\text{{Dot (0)}}, \\text{{Single (1)}}, \\text{{Two (2)}}, \\text{{Three (3)}}, \\text{{Four (4)}}, \\text{{Six (6)}}, \\text{{Wicket Dismissal (W)}}, \\text{{Wide (wd)}}, \\text{{No-ball (nb)}} \\big\\}}$$
- $P(o \\mid S_t)$ are pre-delivery empirical transition probabilities conditioned strictly on phase and innings baselines (zero player or outcome leakage).
- $\\text{{WP}}(S)$ are validated logistic regression state models with Markov terminal resolution for final-over states ($B_{{\\text{{rem}}}} \\le 1$).

#### Innings-Stratified ECDF Normalization $L_{{\\text{{norm}}}}(S_t)$
Raw consequence exhibits an order-of-magnitude scale divergence between innings (Innings 1 max $L_1 \\approx 0.065$, Innings 2 max $L_2 \\approx 0.485$). Direct pooling would destroy first-innings high-leverage representation. To establish cross-innings parity, consequence is normalized **separately within each innings** using Empirical Cumulative Distribution Functions:
$$L_{{\\text{{norm}}}}(S_t) = \\frac{{\\text{{Rank}}_{{\\text{{left}}}} + \\text{{Rank}}_{{\\text{{right}}}}}}{{2 \\cdot N_{{\\text{{innings}}}}}} \\times 100 \\in [0, 100]$$
Where $\\text{{ECDF}}_1$ is calibrated on $N_1 = 96,165$ deliveries, and $\\text{{ECDF}}_2$ is calibrated on $N_2 = 90,615$ deliveries.

### 4.3 Validation of Scenario Behaviors
To demonstrate that $P(S_t)$ operates with complete physical validity, four canonical boundary scenarios were evaluated:
1. **Scenario A (Final Over, 6 runs required, 3 wickets in hand):** $T = 82.5, L_{{\\text{{norm}}}} = 98.4 \\implies P = \\sqrt{{82.5 \\times 98.4}} = \\mathbf{{90.1}}$ (Extreme Pressure).
2. **Scenario B (Over 18, 75 runs required, 2 wickets in hand):** $T = 98.0, L_{{\\text{{norm}}}} = 4.2 \\implies P = \\sqrt{{98.0 \\times 4.2}} = \\mathbf{{20.3}}$ (Garbage Time: Task is impossible, but match consequence is negligible).
3. **Scenario C (Over 2, Innings 1, score 12/0):** $T = 38.0, L_{{\\text{{norm}}}} = 42.0 \\implies P = \\mathbf{{39.9}}$ (Routine Powerplay baseline).
4. **Scenario D (Over 19, defending 4 runs, 7 wickets down):** $T = 88.0, L_{{\\text{{norm}}}} = 96.0 \\implies P = \\mathbf{{91.9}}$ (Maximum Bowling Climax Defense).

---

## Section 5 — Measuring Player Reliability: PWSVA and SBVA

### 5.1 The 36-Cell Situational Baseline
Rather than comparing players to static historical averages, every delivery $i$ is contrasted against expected performance in a discrete 36-cell empirical baseline tensor $c_i$:
- **Innings:** $\{1, 2\}$ (2 levels).
- **Competition Format:** $\{\\text{{IPL}}, \\text{{T20I}}\}$ (2 levels).
- **Match Phase:** $\{\\text{{Powerplay (Overs 1–6)}}, \\text{{Middle (Overs 7–15)}}, \\text{{Death (Overs 16–20)}}\}$ (3 levels).
- **Wickets Lost Bucket:** $\{0–3, 4–6, 7+\}$ (3 levels).
- **Total Cells:** $2 \\times 2 \\times 3 \\times 3 = 36 \\text{{ cells}}$.

Each cell establishes expected runs ($\\mathbb{{E}}[R \\mid c_i]$), expected batter dismissals ($\\mathbb{{E}}[W_{{\\text{{bat}}}} \\mid c_i]$), and expected bowling wickets ($\\mathbb{{E}}[W_{{\\text{{bowl}}}} \\mid c_i]$).

### 5.2 Dynamic and Capped Wicket Valuation
Dismissals are valued in run equivalents ($\\lambda_{{\\text{{wkt}}}}$) based on empirical resource loss across match phase and innings. To prevent mathematical distortion in endgame run-chases, the effective wicket value ($\\lambda_{{\\text{{eff}}}}$) is capped strictly by remaining required runs (Step 6.3 Audit 2):
$$\\lambda_{{\\text{{eff}}}} = \\min\\left(\\lambda_{{\\text{{wkt}}}}, R_{{\\text{{req}}}}\\right) \\quad [\\text{{if Innings 2 and }} W_{{\\text{{rem}}}} > 1]$$
*Rationale:* If a chasing team requires 4 runs to win with 6 wickets in hand, losing a wicket cannot rationally cost 12 runs of resource value. Capping $\\lambda_{{\\text{{eff}}}}$ at $R_{{\\text{{req}}}}$ preserves monotonic sanity.

### 5.3 Batting Performance Metric: PWSVA
Batting Situational Value Added ($v_{{\\text{{bat}}, i}}$) on delivery $i$:
$$v_{{\\text{{bat}}, i}} = \\left(R_i - \\mathbb{{E}}[R \\mid c_i]\\right) - \\lambda_{{\\text{{eff}}, i}} \\cdot \\left(W_{{\\text{{striker}}, i}} - \\mathbb{{E}}[W_{{\\text{{bat}}}} \\mid c_i]\\right)$$

Weighted by continuous pressure $w_i = (P_i / 50)^\\alpha$ with baseline $\\alpha = 1.00$:
$$\\bar{{v}}_{{\\text{{bat}}, p}} = \\frac{{\\sum_{{i=1}}^{{n_p}} w_i \\cdot v_{{\\text{{bat}}, i}}}}{{\\sum_{{i=1}}^{{n_p}} w_i}}$$

Using Kish's Effective Sample Size $N_{{\\text{{eff}}, p}}^{{\\text{{bat}}}} = \\frac{{\\left(\\sum_{{i=1}}^{{n_p}} w_i\\right)^2}}{{\\sum_{{i=1}}^{{n_p}} w_i^2}}$ with calibrated shrinkage constant $K_{{\\text{{bat}}}} = 600$:
$$\\mathbf{{\\text{{PWSVA}}_p^{{\\text{{shrunk}}}} = \\left( \\frac{{N_{{\\text{{eff}}, p}}^{{\\text{{bat}}}}}}{{N_{{\\text{{eff}}, p}}^{{\\text{{bat}}}} + 600}} \\right) \\cdot \\bar{{v}}_{{\\text{{bat}}, p}}}}$$

### 5.4 Bowling Performance Metric: SBVA
Bowling Situational Value Added ($v_{{\\text{{bowl}}, i}}$) is evaluated on all bowler-attributed deliveries:
$$v_{{\\text{{bowl}}, i}} = \\begin{{cases}}
\\left(\\mathbb{{E}}[R_{{\\text{{conc}}}} \\mid c_i] - R_{{\\text{{conc}}, i}}\\right) + \\lambda_{{\\text{{eff}}, i}} \\cdot \\left(W_{{\\text{{bowl}}, i}} - \\mathbb{{E}}[W_{{\\text{{bowl}}}} \\mid c_i]\\right) & \\text{{if legal ball}} \\\\
- R_{{\\text{{conc}}, i}} + \\lambda_{{\\text{{eff}}, i}} \\cdot W_{{\\text{{bowl}}, i}} & \\text{{if illegal ball (wide/no-ball)}}
\\end{{cases}}$$

#### The Legal-Ball Quota Denominator (Step 6.3 Audit 4)
In T20 cricket, a bowler's capacity is constrained by a quota of legal deliveries (maximum 24 legal balls per match). To avoid double-counting penalties and prevent artificial sample size inflation:
1. **Conceded Extras Penalized in Numerator:** Every conceded run from wides and no-balls is fully debited against the bowler in $v_{{\\text{{bowl}}, i}}$. Any wickets taken on illegal deliveries (e.g., stumping off a wide) are credited in the numerator.
2. **Quota Denominator:** The rate average $\\bar{{v}}_{{\\text{{bowl}}}}$ and Kish ESS are normalized strictly over **legal deliveries**:
$$\\bar{{v}}_{{\\text{{bowl}}, p}} = \\frac{{\\sum_{{i=1}}^{{m_p}} w_i \\cdot v_{{\\text{{bowl}}, i}}}}{{\\sum_{{i \\in \\text{{legal}}}} w_i}}$$
$$N_{{\\text{{eff}}, p}}^{{\\text{{bowl}}}} = \\frac{{\\left(\\sum_{{i \\in \\text{{legal}}}} w_i\\right)^2}}{{\\sum_{{i \\in \\text{{legal}}}} w_i^2}}$$

Applying empirical Bayes shrinkage with calibrated shrinkage constant $K_{{\\text{{bowl}}}} = 500$:
$$\\mathbf{{\\text{{SBVA}}_p^{{\\text{{shrunk}}}} = \\left( \\frac{{N_{{\\text{{eff}}, p}}^{{\\text{{bowl}}}}}}{{N_{{\\text{{eff}}, p}}^{{\\text{{bowl}}}} + 500}} \\right) \\cdot \\bar{{v}}_{{\\text{{bowl}}, p}}}}$$

---

## Section 6 — Fairness, Eligibility, and Shrinkage Mechanics

### 6.1 Minimum Pressure Exposure Threshold
To qualify for official ranking, a player must achieve sustained exposure to high-pressure competition:
$$\\mathbf{{N(P \\ge 50) \\ge 50 \\text{{ balls faced (batting) or legal deliveries (bowling)}}}}$$

- **Why Minimum Exposure Matters:** T20 cricket is subject to extreme single-match variance. A specialist who plays two matches and hits 20 runs off 8 balls under high pressure would exhibit an astronomical raw average. Requiring 50 balls at $P \\ge 50$ ensures every ranked player has demonstrated performance across multiple match situations.
- **Population Filtering:** Exactly **297 batters** and **292 bowlers** met this requirement.

### 6.2 Empirical Bayes Shrinkage Curve
Raw averages reward small samples with inflated volatility. Shrinkage acts as a regressive filter toward population replacement level ($0.0$):
$$\\text{{Retention Ratio }} w_i = \\frac{{N_{{\\text{{eff}}, i}}}}{{N_{{\\text{{eff}}, i}} + K}}$$

```
                Empirical Bayes Shrinkage Retention Curve
  100% ┌────────────────────────────────────────────────────────────┐
       │                                     Suryakumar / Buttler   │
   80% │                                    • (ESS ~2300, Ret 79%)  │
       │                          • Abhishek Sharma                 │
   60% │                  •       (ESS 1923, Ret 76.2%)             │
       │           Heinrich Klaasen                                 │
   50% │----• (ESS 1142, Ret 65.6%)                                 │
       │   At ESS = K (50% Ret)                                     │
   40% │ • Vaibhav Sooryavanshi                                     │
       │   (ESS 507, Ret 45.8%)                                     │
   20% │                                                            │
    0% └──────┬───────────┬──────────────┬─────────────┬────────────┘
             K=600       1000           1500          2000        2500
                            Kish Effective Sample Size (ESS)
```

1. **At $N_{{\\text{{eff}}}} = K$:** Exactly $50.0\%$ of raw performance is retained; $50.0\%$ is regressed toward replacement level.
2. **Batting Retention Dynamics ($K_{{\\text{{bat}}}} = 600$):**
   - At $\\text{{ESS}} = 600$: Retention is exactly $50.0\%$.
   - **Vaibhav Sooryavanshi** ($\\text{{ESS}} = 506.9$): Retains $506.9 / (506.9 + 600) = \\mathbf{{45.79\\%}}$ (appropriately regressed because $\\text{{ESS}} < 600$; raw $+0.7614$ regressed to shrunk $+0.3487$).
   - **Tim David** ($\\text{{ESS}} = 980.6$): Retains $980.6 / (980.6 + 600) = \\mathbf{{62.04\\%}}$.
   - **Heinrich Klaasen** ($\\text{{ESS}} = 1142.0$): Retains $1142.0 / (1142.0 + 600) = \\mathbf{{65.56\\%}}$.
   - **Phil Salt** ($\\text{{ESS}} = 1364.7$): Retains $1364.7 / (1364.7 + 600) = \\mathbf{{69.46\\%}}$.
   - **Abhishek Sharma** ($\\text{{ESS}} = 1923.3$): Retains $1923.3 / (1923.3 + 600) = \\mathbf{{76.22\\%}}$.
   - **Namboori Tilak Varma** ($\\text{{ESS}} = 1968.9$): Retains $1968.9 / (1968.9 + 600) = \\mathbf{{76.64\\%}}$.
   - **Suryakumar Yadav** ($\\text{{ESS}} = 2287.2$): Retains $2287.2 / (2287.2 + 600) = \\mathbf{{79.22\\%}}$.
   - **Jos Buttler** ($\\text{{ESS}} = 2330.2$): Retains $2330.2 / (2330.2 + 600) = \\mathbf{{79.52\\%}}$.
   - At $\\text{{ESS}} \\ge 2400$: Retention reaches $80.0\\%$ and above.
3. **Bowling Retention Dynamics ($K_{{\\text{{bowl}}}} = 500$):**
   - At $\\text{{ESS}} = 500$: Retention is exactly $50.0\\%$.
   - **Abrar Ahmed** ($\\text{{ESS}} = 604.7$): Retains $604.7 / (604.7 + 500) = \\mathbf{{54.74\\%}}$.
   - **Josh Hazlewood** ($\\text{{ESS}} = 1159.5$): Retains $1159.5 / (1159.5 + 500) = \\mathbf{{69.87\\%}}$.
   - **Sunil Narine** ($\\text{{ESS}} = 1246.3$): Retains $1246.3 / (1246.3 + 500) = \\mathbf{{71.37\\%}}$.
   - **Jasprit Bumrah** ($\\text{{ESS}} = 1369.7$): Retains $1369.7 / (1369.7 + 500) = \\mathbf{{73.26\\%}}$.
   - **Wanindu Hasaranga** ($\\text{{ESS}} = 1675.4$): Retains $1675.4 / (1675.4 + 500) = \\mathbf{{77.02\\%}}$.
   - **Bhuvneshwar Kumar** ($\\text{{ESS}} = 1875.7$): Retains $1875.7 / (1875.7 + 500) = \\mathbf{{78.95\\%}}$.
   - **Rashid Khan** ($\\text{{ESS}} = 2245.9$): Retains $2245.9 / (2245.9 + 500) = \\mathbf{{81.79\\%}}$.
   - At $\\text{{ESS}} \\ge 2000$: Retention reaches $80.0\\%$ and above.

### 6.3 Uncertainty Quantification: Match-Level Block Bootstrap
To compute robust confidence bounds without parametric distribution assumptions, **1,000 match-level block bootstrap iterations** were executed:
- Entire match clusters are resampled with replacement, preserving within-match delivery dependencies and bowler-batter matchups.
- Standard errors ($\\text{{SE}}$) and 95% confidence intervals are extracted directly from empirical percentiles.

#### Interpretation of Overlapping Confidence Bounds:
The confidence intervals of Ranks 2–5 in batting and Ranks 6–10 in bowling overlap. **Close rankings should be interpreted as elite performance tiers rather than certain ordinal separations.** The difference between Rank 10 and Rank 11 is less than $0.0025$ runs/ball in both disciplines.

---

## Section 7 — Empirical Validation and Auditing Evidence

### 7.1 Baseline Out-of-Sample Calibration (Step 7.1)
The 36-cell empirical baseline was evaluated via 5-fold cross-validation across 186,780 deliveries:
- **Batting Out-of-Sample RMSE:** 1.71 to 1.76 runs per delivery across all 5 validation folds.
- **Prediction Bias:** $< 0.004$ runs per delivery (near-zero mean calibration error).
- **Zero Data Leakage:** Wicket frequencies and expected runs were computed strictly on training folds.

### 7.2 Sensitivity to Pressure Exponent ($\\alpha = 1.00$ vs. $1.25$)
To verify that rankings are robust to super-linear weighting, scores were recalculated with $\\alpha = 1.25$:
- **Batting Spearman Correlation:** $\\rho = 0.9978$ across all 297 qualified batters. Top 8 positions are 100% invariant.
- **Bowling Spearman Correlation:** $\\rho = 0.9981$ across all 292 qualified bowlers. Top 5 positions are 100% invariant. Mohammed Shami climbs from #13 to #7 due to extreme concentration in death climaxes ($P \\ge 75$).

### 7.3 Phase Specialization Dynamics
Evaluating unshrunk pressure-weighted situational value added per ball within each match phase (Figures 7 and 8) reveals distinct tactical masteries:
- **Powerplay Specialists:** Abhishek Sharma (+0.40 on 1462b), Phil Salt (+0.32 on 950b), and Josh Hazlewood (+0.30 on 732b).
- **Middle-Overs Masters:** Heinrich Klaasen (+0.39 on 915b), Suryakumar Yadav (+0.44 on 1673b), and Mujeeb Ur Rahman (+0.38 on 306b).
- **Lethal Death Enforcers:** Sunil Narine (+0.71 net runs saved/ball on 204b), Rashid Khan (+0.45 on 516b), and Jasprit Bumrah (+0.42 on 526b).

### 7.4 Cross-Format Descriptive Associations
Evaluating players with $\\ge 50$ deliveries in both IPL and T20Is:
- **Batting (Unique Striker ID Disambiguated):** $N = 90$, Pearson $r = 0.1149$, Spearman $\\rho = 0.1645$ ($p = 0.1215$).
- **Bowling (Zero Name Collisions):** $N = 97$, Pearson $r = 0.2338$, Spearman $\\rho = 0.2956$ ($p = 0.0033$).

These descriptive correlations show that batting pressure performance exhibits higher environment sensitivity ($\\rho = 0.1645$), reflecting differing team roles, while bowling execution exhibits greater stability ($\\rho = 0.2956$). This justifies empirical Bayes shrinkage across differing format sample sizes.

---

## Section 8 — Placement of Prominent International & Franchise Stars

| Player Name | Discipline | Official Rank | Shrunk Score | Raw Score | Balls Faced / Bowled | Kish ESS | 95% Score CI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Heinrich Klaasen** | Batting | **#5** | +0.2201 | +0.3357 | 1,409 | 1,142.0 | `[+0.1238, +0.3072]` |
| **Phil Salt** | Batting | **#6** | +0.1954 | +0.2813 | 1,591 | 1,364.7 | `[+0.0633, +0.3033]` |
| **Travis Head** | Batting | **#8** | +0.1625 | +0.2611 | 1,096 | 988.6 | `[+0.0017, +0.3203]` |
| **Shreyas Iyer** | Batting | **#14** | +0.1350 | +0.1887 | 1,751 | 1,507.1 | `[+0.0085, +0.2366]` |
| **Jos Buttler** | Batting | **#17** | +0.1306 | +0.1642 | 2,675 | 2,330.2 | `[+0.0366, +0.2187]` |
| **Mitchell Marsh** | Batting | **#19** | +0.1272 | +0.1796 | 1,656 | 1,456.7 | `[+0.0069, +0.2471]` |
| **Virat Kohli** | Batting | **#34** | +0.0850 | +0.1081 | 2,445 | 2,201.2 | `[+0.0005, +0.1547]` |
| **Rohit Sharma** | Batting | **#168** | -0.0164 | -0.0231 | 1,561 | 1,451.1 | `[-0.1574, +0.0988]` |
| **Rashid Khan** | Bowling | **#1** | +0.1756 | +0.2147 | 2,648 | 2,245.9 | `[+0.0810, +0.2784]` |
| **Jasprit Bumrah** | Bowling | **#2** | +0.1541 | +0.2103 | 1,606 | 1,369.7 | `[+0.0237, +0.2784]` |
| **Sunil Narine** | Bowling | **#3** | +0.1442 | +0.2020 | 1,464 | 1,246.3 | `[+0.0555, +0.2334]` |
| **Josh Hazlewood** | Bowling | **#4** | +0.1330 | +0.1904 | 1,368 | 1,159.5 | `[+0.0021, +0.2830]` |
| **Mohammed Shami** | Bowling | **#13** | +0.0989 | +0.1438 | 1,228 | 1,100.8 | `[-0.0629, +0.2621]` |
| **Trent Boult** | Bowling | **#16** | +0.0922 | +0.1272 | 1,501 | 1,313.6 | `[-0.0131, +0.2146]` |
| **Axar Patel** | Bowling | **#66** | +0.0195 | +0.0239 | 2,604 | 2,218.5 | `[-0.0665, +0.1117]` |

---

## Section 9 — Limitations and Future Enhancements
1. **Striker Run-Out Attribution:** Striker run-out dismissals are attributed to the striker ($W_{{\\text{{striker}}}} = 1$), while non-striker run-outs are attributed to team match state rather than individual batters.
2. **Residual Environmental Variance:** Factors such as pitch deterioration across a tournament, evening dew in the second innings, venue altitude, and asymmetrical boundary dimensions are not explicitly modeled in the ball-by-ball state space. While the match-level block bootstrap accounts for delivery clustering and match-level sampling variability, unobserved environmental factors remain residual variance.
3. **Discrete Empirical Baseline:** The 36-cell tensor groups overs into coarse phases (Powerplay, Middle, Death) and wickets into three buckets (0–3, 4–6, 7+). Future iterations (SupeRR 3.0) will incorporate continuous 2D Gaussian process surfaces over remaining deliveries and wickets.

---

## Section 10 — Conclusion
The SupeRR Selector Round 1 reliability system establishes an uncompromised, reproducible standard for T20 evaluation. By decomposing pressure into Task Difficulty and Match Consequence, contrasting performance against a 36-cell empirical baseline, and applying Empirical Bayes shrinkage, the engine delivers transparent, evidence-based rankings that stand up to rigorous statistical audit.

---
*Official Methodology Report · SupeRR Selector 2.0 (Round 1) · Antigravity Autonomous Audit Team · November 2026*
"""

    md_out_path = 'outputs/step_10_methodology_report/step_10_methodology_report.md'
    with open(md_out_path, 'w', encoding='utf-8') as f:
        f.write(full_markdown_text)
    print(f"Successfully wrote corrected Markdown to {md_out_path} ({len(full_markdown_text)} bytes).")

    # 5. Define HTML Template with Exact Step 4 Formulas for Pages 5 & 6
    raw_html_template = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {
    size: letter;
    margin: 34pt 40pt 34pt 40pt;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 8.5pt;
    line-height: 1.35;
    color: #2d3748;
}
.report-title {
    font-size: 16pt;
    font-weight: 800;
    color: #1a365d;
    line-height: 1.15;
    margin-bottom: 3pt;
}
.report-subtitle {
    font-size: 10pt;
    font-weight: 600;
    color: #2b6cb0;
    margin-bottom: 8pt;
}
.meta-box {
    background-color: #f7fafc;
    border-left: 3pt solid #3182ce;
    padding: 5pt 8pt;
    font-size: 7.5pt;
    color: #4a5568;
    margin-bottom: 10pt;
    line-height: 1.3;
}
.section-header {
    font-size: 11pt;
    font-weight: 700;
    color: #1a365d;
    border-bottom: 1.2pt solid #e2e8f0;
    padding-bottom: 2pt;
    margin-top: 10pt;
    margin-bottom: 4pt;
}
.subsection-header {
    font-size: 9.2pt;
    font-weight: 700;
    color: #2c5282;
    margin-top: 5pt;
    margin-bottom: 2pt;
}
p {
    margin-top: 0;
    margin-bottom: 5pt;
    text-align: justify;
}
ul, ol {
    margin-top: 0;
    margin-bottom: 5pt;
    padding-left: 14pt;
}
li {
    margin-bottom: 2pt;
}
.formula-card {
    border: 0.8pt solid #cbd5e0;
    border-left: 3pt solid #2b6cb0;
    padding: 3.5pt 6pt;
    margin-top: 2.5pt;
    margin-bottom: 4pt;
    font-size: 8.0pt;
    line-height: 1.22;
}
.formula-title {
    font-weight: bold;
    color: #1a365d;
    font-size: 8.2pt;
    margin-bottom: 1.5pt;
}
.formula-eq {
    font-family: "Courier New", Courier, monospace;
    font-size: 8.0pt;
    font-weight: bold;
    color: #1a202c;
    background-color: #f7fafc;
    padding: 2pt 4pt;
    margin: 1.5pt 0;
    border: 0.5pt solid #e2e8f0;
}
table.report-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 3pt;
    margin-bottom: 6pt;
    font-size: 7.2pt;
    line-height: 1.15;
}
table.report-table th {
    border-top: 1.2pt solid #1a365d;
    border-bottom: 1.2pt solid #1a365d;
    color: #1a365d;
    padding: 3pt 3pt;
    font-weight: bold;
    text-align: left;
    background-color: transparent;
}
table.report-table td {
    padding: 2.2pt 3pt;
    border-bottom: 0.5pt solid #e2e8f0;
    text-align: left;
}
table.report-table tr:last-child td {
    border-bottom: 1.2pt solid #1a365d;
}
.bold { font-weight: bold; }
.primary { color: #2b6cb0; }
.figure-container {
    text-align: center;
    margin-top: 4pt;
    margin-bottom: 6pt;
}
.figure-container img {
    max-width: 98%;
    height: auto;
    border: 0.5pt solid #cbd5e0;
}
.figure-caption {
    font-size: 7.2pt;
    font-style: italic;
    color: #718096;
    margin-top: 2pt;
}
.page-break {
    page-break-before: always;
}
</style>
</head>
<body>

<!-- PAGE 1: TITLE & EXECUTIVE SUMMARY -->
<div class="report-title">Identifying the Most Reliable T20 Players Under Pressure</div>
<div class="report-subtitle">A Dual-Dimensional Situational Value Framework with Empirical Bayes Shrinkage</div>

<div class="meta-box">
    <strong>Author:</strong> Antigravity Autonomous Analytics &amp; Audit Team &nbsp;|&nbsp; <strong>Competition:</strong> SupeRR Selector Season 2 &mdash; Round 1<br>
    <strong>Dataset Scope:</strong> Ball-by-ball records from Men's T20 Competitions (IPL &amp; T20I, 2022&ndash;2026, <i>N</i> = 186,780 deliveries)<br>
    <strong>Authoritative Source Baseline:</strong> Frozen Step 7.4 Outputs (<code>outputs/step_7_empirical_calibration/step_7_4_final_rankings/</code>)
</div>

<h2 class="section-header">Section 1 &mdash; Executive Summary</h2>
<h3 class="subsection-header">1.1 The Challenge of Pressure Evaluation</h3>
<p>
In elite Twenty20 cricket, traditional evaluation metrics&mdash;such as raw batting strike rate, batting average, and bowling economy rate&mdash;fail to distinguish between low-stakes accumulation and performance delivered under acute match pressure. A boundary hit when requiring 6 runs off 2 balls carries vastly greater athletic and tactical value than a boundary hit in a decided blowout. Conversely, conceding a single boundary in a high-leverage death over does not reflect poor execution if the baseline expectancy in that situation is substantially worse.
</p>
<p>
To identify the <strong>most reliable players under pressure</strong>, we design and implement an end-to-end mathematical framework:
</p>
<ul>
    <li><strong>Objective, Independent Pressure Quantification (<i>P<sub>t</sub></i> &isin; [0, 100]):</strong> Pressure is decoupled from player identity and outcome, defined strictly pre-delivery (<i>t</i><sup>&minus;</sup>) as the geometric mean of <strong>Task Difficulty (<i>T<sub>t</sub></i>)</strong> and <strong>Normalized Match Consequence (<i>L</i><sub>norm</sub>(<i>S<sub>t</sub></i>))</strong>.</li>
    <li><strong>Situational Value Added (SVA):</strong> Every delivery is evaluated against a discrete 36-cell empirical baseline tensor calibrated on 186,780 deliveries, computing runs and dismissals added relative to exact match state expectancy.</li>
    <li><strong>Endgame Wicket Capping:</strong> To eliminate mathematical distortion in late-inning run chases where required runs are low, effective wicket valuations are capped by remaining runs (&lambda;<sub>eff</sub> = min(&lambda;<sub>wkt</sub>, <i>R</i><sub>req</sub>)).</li>
    <li><strong>Quota-Based Bowling Normalization:</strong> Conceded extras (wides and no-balls) are penalized in the numerator, while bowling opportunity rates are normalized strictly over legal deliveries.</li>
    <li><strong>Empirical Bayes Shrinkage toward Zero Replacement Level:</strong> Raw situational averages are regressed based on Kish's Effective Sample Size (<i>N</i><sub>eff</sub>), preventing small-sample noise from dominating official leaderboards (<i>K</i><sub>bat</sub> = 600, <i>K</i><sub>bowl</sub> = 500).</li>
</ul>

<h3 class="subsection-header">1.2 Summary of Findings</h3>
<p>
Across 186,780 deliveries spanning 2022&ndash;2026:
</p>
<ul>
    <li>Exactly <strong>297 batters</strong> and <strong>292 bowlers</strong> met the sustained pressure eligibility threshold (<i>N</i>(<i>P</i> &ge; 50) &ge; 50).</li>
    <li><strong>Top Batting Performer:</strong> <strong>Vaibhav Sooryavanshi</strong> ranks #1 (+0.3487 shrunk PWSVA), exhibiting extraordinary boundary hitting in high-pressure opportunities (raw +0.7614, Kish ESS = 506.9, retaining 45.8% of raw performance under rigorous shrinkage).</li>
    <li><strong>Consistently Elite Batting Volume:</strong> <strong>Suryakumar Yadav</strong> ranks #2 (+0.2819 shrunk PWSVA, raw +0.3558, 2,638 balls, Kish ESS = 2,287.2) and <strong>Abhishek Sharma</strong> ranks #3 (+0.2703 shrunk PWSVA, raw +0.3547, 2,195 balls, Kish ESS = 1,923.3), maintaining elite positive value added across massive sample sizes.</li>
    <li><strong>Top Bowling Performer:</strong> <strong>Rashid Khan</strong> ranks #1 (+0.1756 shrunk SBVA, raw +0.2147, 2,648 balls, Kish ESS = 2,245.9), followed closely by <strong>Jasprit Bumrah</strong> at #2 (+0.1541 shrunk SBVA, raw +0.2103, 1,606 balls, Kish ESS = 1,369.7) and <strong>Sunil Narine</strong> at #3 (+0.1442 shrunk SBVA, raw +0.2020, 1,464 balls, Kish ESS = 1,246.3).</li>
</ul>

<div class="page-break"></div>

<!-- PAGE 2: EXECUTIVE LEADERBOARDS -->
<h2 class="section-header">Section 1.3 &mdash; Executive Leaderboards</h2>

<h3 class="subsection-header">Official Top 10 Batting Reliability Rankings (PWSVA)</h3>
__HTML_BAT_TABLE__

<h3 class="subsection-header">Official Top 10 Bowling Reliability Rankings (SBVA)</h3>
__HTML_BOWL_TABLE__

<div class="page-break"></div>

<!-- PAGE 3: DATASET & SCOPE -->
<h2 class="section-header">Section 2 &mdash; Dataset and Scope</h2>

<h3 class="subsection-header">2.1 Scope of Data</h3>
<p>
The evaluation dataset is drawn from top-tier men's T20 cricket spanning January 1, 2022 through May 31, 2026:
</p>
<ul>
    <li><strong>Indian Premier League (IPL):</strong> 365 matches (seasons 2022, 2023, 2024, 2025, and 2026).</li>
    <li><strong>Men's T20 Internationals (T20I):</strong> All official ICC encounters among full-member nations and major ICC tournament fixtures.</li>
    <li><strong>Delivery Cohort:</strong> 186,780 valid ball-by-ball deliveries across 742 unique matches.</li>
</ul>

<h3 class="subsection-header">2.2 Pre-Delivery Data Hygiene &amp; State Representation</h3>
<p>
Every delivery is represented as a pre-delivery state vector <i>S<sub>t</sub></i> = (<i>I<sub>t</sub></i>, <i>B</i><sub>elapsed</sub>, <i>B</i><sub>rem</sub>, <i>R</i><sub>curr</sub>, <i>R</i><sub>target</sub>, <i>R</i><sub>req</sub>, <i>W<sub>t</sub></i>, <i>W</i><sub>rem</sub>, Phase<sub><i>t</i></sub>, Format<sub><i>t</i></sub>, <i>V</i><sub>venue</sub>). Strict data hygiene ensures:
</p>
<ol>
    <li><strong>Pre-Delivery Boundary (<i>t</i><sup>&minus;</sup>):</strong> All state variables are measured prior to ball release. Outcome variables (runs scored, wickets taken, extras) are strictly segregated from state inputs.</li>
    <li><strong>Legal Delivery Synchronization:</strong> Incomplete or interrupted matches are parsed through valid ball-by-ball logs. Super Overs are excluded from regular baseline calibration.</li>
    <li><strong>Player Disambiguation:</strong> Player identities are resolved via unique registry IDs, disambiguating identical names across franchise and international rosters.</li>
</ol>

<h3 class="subsection-header">2.3 Qualification Gate: <i>N</i>(<i>P</i> &ge; 50) &ge; 50</h3>
<p>
To eliminate volatile micro-samples while retaining genuine specialists, players qualify if and only if they faced or bowled at least <strong>50 deliveries under elevated pressure (<i>P<sub>i</sub></i> &ge; 50)</strong>. Exactly 297 batters and 292 bowlers satisfied this threshold.
</p>

<div class="page-break"></div>

<!-- PAGE 4: VISUAL REFERENCE - TOP 20 RANKINGS -->
<h2 class="section-header">Visual Reference: Official Top 20 Rankings</h2>

<div class="figure-container">
    <img src="outputs/step_7_empirical_calibration/step_7_4_final_rankings/top10_batting_reliability.png" alt="Top 20 Batters" style="max-height: 290pt;">
    <div class="figure-caption">Figure 1: Top 20 Batters Ranked by Pressure-Weighted Situational Value Added (PWSVA Shrunk) with 95% Bootstrap Intervals.</div>
</div>

<div class="figure-container">
    <img src="outputs/step_7_empirical_calibration/step_7_4_final_rankings/top10_bowling_reliability.png" alt="Top 20 Bowlers" style="max-height: 290pt;">
    <div class="figure-caption">Figure 2: Top 20 Bowlers Ranked by Situational Bowling Value Added (SBVA Shrunk) with 95% Bootstrap Intervals.</div>
</div>

<div class="page-break"></div>

<!-- PAGE 5: DEFINING PRESSURE & BATTING TASK DIFFICULTY -->
<h2 class="section-header">Section 3 &mdash; Defining Pressure: The Dual-Dimensional Framework</h2>

<h3 class="subsection-header">3.1 Foundational Philosophy</h3>
<p>
Traditional models conflate difficulty with consequence. A batter facing Jasprit Bumrah in the 19th over needing 24 runs faces extreme athletic difficulty <i>and</i> extreme consequence. Conversely, a tailender batting in the 19th over needing 85 runs faces extreme difficulty, but near-zero consequence (the match is already decided). True pressure exists <strong>if and only if both difficulty and consequence are elevated</strong>.
</p>

<h3 class="subsection-header">3.2 The Master Multiplicative Gating Principle</h3>
<p>
Delivery-level pressure (<i>P</i>) is defined strictly pre-delivery (<i>t</i><sup>&minus;</sup>) as the geometric mean of Task Difficulty (<i>T</i>) and Normalized Match Consequence (<i>L</i><sub>norm</sub>) (Step 3.2 Decision COMP-01, <code>06_generate_pressure_dataset.py</code>):
</p>
<div class="formula-card">
    <div class="formula-title">Combined Geometric-Mean Pressure Equation:</div>
    <div class="formula-eq">P(S_t) = sqrt( T(S_t) * L_norm(S_t) ) in [0, 100]</div>
    <div>Pre-delivery evaluation at <i>t</i><sup>&minus;</sup> completely eliminates outcome bias and player identity leakage. Scale: <i>P</i> &lt; 25 (Low / Baseline), 25&ndash;50 (Moderate), 50&ndash;75 (High / Qualification), &ge; 75 (Climax / Extreme).</div>
</div>

<h2 class="section-header">Section 4 &mdash; Calculating Delivery-Level Pressure (Frozen Step 4 Engine)</h2>

<h3 class="subsection-header">Task Difficulty Formulation: Batting (<code>05_task_difficulty_models.py</code>)</h3>
<div class="formula-card">
    <div class="formula-title">Batting Task Difficulty &mdash; Innings 1 (T_bat, 1):</div>
    <div class="formula-eq">RAR = max( 0, (V_par - Score) / (B_rem / 6) ),   delta_R = (RAR - R_par) / R_par</div>
    <div class="formula-eq">W_stress = (W_t - mu_W(L_t)) / sigma_W(L_t)   [W_stress = 0 at ball 0]</div>
    <div class="formula-eq">Z_B1 = 0.60 * delta_R + 0.40 * W_stress</div>
    <div class="formula-eq">T_bat, 1 = 100 / ( 1 + exp( -1.2 * Z_B1 ) ) in [0, 100]</div>
    <div>Evaluates Required Acceleration Rate (RAR) against venue par (default 176.68 runs, <i>R</i><sub>par</sub> = 8.83 RPO) and empirical wicket curve stress (<i>&mu;<sub>W</sub></i>, <i>&sigma;<sub>W</sub></i>) mapped via logistic sigmoid.</div>
</div>

<div class="formula-card">
    <div class="formula-title">Batting Task Difficulty &mdash; Innings 2 (T_bat, 2):</div>
    <div class="formula-eq">RRR = clip( (R_req / B_rem) * 6, 0, 36 ),   Z_RRR = (RRR - 8.10) / 3.00</div>
    <div class="formula-eq">Z_W = (W_t - 3.50) / 2.00,   Z_inter = (RRR * W_t - 28.0) / 25.0</div>
    <div class="formula-eq">Z_B2 = 0.55 * Z_RRR + 0.25 * Z_W + 0.20 * Z_inter</div>
    <div class="formula-eq">T_bat, 2 = 100 / ( 1 + exp( -1.0 * Z_B2 ) ) in [0, 100]</div>
    <div>Models chase difficulty using standardized Required Run Rate (RRR), standardized wickets fallen, and their centered non-linear interaction term (<i>Z</i><sub>inter</sub>) mapped via logistic sigmoid.</div>
</div>

<div class="page-break"></div>

<!-- PAGE 6: BOWLING TASK DIFFICULTY & MATCH CONSEQUENCE -->
<h3 class="subsection-header">Task Difficulty Formulation: Bowling (<code>05_task_difficulty_models.py</code>)</h3>

<div class="formula-card">
    <div class="formula-title">Bowling Task Difficulty &mdash; Innings 1 (T_bowl, 1):</div>
    <div class="formula-eq">CRR = (Score / max(1, B_elapsed)) * 6,   delta_CRR = (CRR - R_par) / R_par</div>
    <div class="formula-eq">W_opp = (mu_W(L_t) - W_t) / sigma_W(L_t)   [W_opp = 0 at ball 0]</div>
    <div class="formula-eq">Z_BO1 = 0.50 * delta_CRR + 0.35 * W_opp + 0.15 * FieldFactor</div>
    <div class="formula-eq">T_bowl, 1 = 100 / ( 1 + exp( -1.1 * Z_BO1 ) ) in [0, 100]</div>
    <div>Evaluates conceded run-rate momentum, opponent wicket abundance, and phase field restriction penalties (FieldFactor = +0.50 in Powerplay and Death; 0.00 in Middle overs).</div>
</div>

<div class="formula-card">
    <div class="formula-title">Bowling Task Difficulty &mdash; Innings 2 (T_bowl, 2):</div>
    <div class="formula-eq">RRR_stress = (8.10 - RRR) / 3.00,   W_opp = (mu_W(L_t) - W_t) / sigma_W(L_t)</div>
    <div class="formula-eq">Z_BO2 = 0.60 * RRR_stress + 0.40 * W_opp</div>
    <div class="formula-eq">T_bowl, 2 = 100 / ( 1 + exp( -1.0 * Z_BO2 ) ) in [0, 100]</div>
    <div>Evaluates defense hardship when the batting side is cruising comfortably below required rate (low RRR), coupled with opponent wickets in hand. Inverting batting difficulty was explicitly rejected.</div>
</div>

<h3 class="subsection-header">Match Consequence Formulation ($L$) (<code>04_consequence_and_ecdf.py</code>)</h3>
<div class="formula-card">
    <div class="formula-title">Pre-Delivery Expected Match Consequence (L):</div>
    <div class="formula-eq">L(S_t) = sum_{o in O} P(o | S_t) * | WP( S_{t+1}(o) ) - WP( S_t ) |</div>
    <div>Expected absolute Win Probability swing over 9 discrete delivery outcomes &Oscr; = {Dot(0), 1, 2, 3, 4, 6, Wicket, Wide, No-ball} weighted by phase-conditioned empirical transition probabilities <i>P</i>(<i>o</i> | <i>S<sub>t</sub></i>).</div>
</div>

<div class="formula-card">
    <div class="formula-title">Innings-Stratified ECDF Normalization (L_norm):</div>
    <div class="formula-eq">L_norm(S_t) = [ ( Rank_left + Rank_right ) / ( 2 * N_innings ) ] * 100 in [0, 100]</div>
    <div>Computed <strong>separately within each innings</strong> (ECDF_1 on <i>N</i><sub>1</sub> = 96,165; ECDF_2 on <i>N</i><sub>2</sub> = 90,615), overcoming the 8&times; raw scale divergence (<i>L</i><sub>1,max</sub> &approx; 0.065 vs. <i>L</i><sub>2,max</sub> &approx; 0.485).</div>
</div>

<h3 class="subsection-header">Validation of Scenario Behaviors</h3>
<ul>
    <li><strong>Scenario A (Final Over, 6 runs required, 3 wickets in hand):</strong> <i>T</i> = 82.5, <i>L</i><sub>norm</sub> = 98.4 &rArr; <i>P</i> = <strong>90.1</strong> (Extreme Pressure).</li>
    <li><strong>Scenario B (Over 18, 75 runs required, 2 wickets in hand):</strong> <i>T</i> = 98.0, <i>L</i><sub>norm</sub> = 4.2 &rArr; <i>P</i> = <strong>20.3</strong> (Garbage Time: Task is impossible, but match consequence is negligible).</li>
    <li><strong>Scenario C (Over 2, Innings 1, score 12/0):</strong> <i>T</i> = 38.0, <i>L</i><sub>norm</sub> = 42.0 &rArr; <i>P</i> = <strong>39.9</strong> (Routine Powerplay baseline).</li>
    <li><strong>Scenario D (Over 19, defending 4 runs, 7 wickets down):</strong> <i>T</i> = 88.0, <i>L</i><sub>norm</sub> = 96.0 &rArr; <i>P</i> = <strong>91.9</strong> (Maximum Bowling Climax Defense).</li>
</ul>

<div class="page-break"></div>

<!-- PAGE 7: MEASURING RELIABILITY & RETENTION DYNAMICS -->
<h2 class="section-header">Section 5 &mdash; Measuring Player Reliability: PWSVA and SBVA</h2>

<h3 class="subsection-header">The 36-Cell Situational Baseline and Capped Wicket Valuation</h3>
<p>
Every ball is evaluated relative to a 36-cell empirical baseline <i>c<sub>i</sub></i> = (Innings &times; Format &times; Phase &times; Wicket Bucket) calibrated from 186,780 deliveries. To prevent distortion in endgame chases where few runs remain, effective wicket values are capped: &lambda;<sub>eff</sub> = min(&lambda;<sub>wkt</sub>, <i>R</i><sub>req</sub>) if Innings 2 and <i>W</i><sub>rem</sub> &gt; 1.
</p>

<div class="formula-card">
    <div class="formula-title">Batting Reliability Metric (PWSVA Shrunk):</div>
    <div class="formula-eq">v_bat, i = ( R_i - E[R | c_i] ) - lambda_eff, i * ( W_striker, i - E[W_bat | c_i] )</div>
    <div class="formula-eq">PWSVA_p^shrunk = [ N_eff, p^bat / ( N_eff, p^bat + 600 ) ] * [ sum( w_i * v_bat, i ) / sum( w_i ) ]</div>
</div>

<div class="formula-card">
    <div class="formula-title">Bowling Reliability Metric (SBVA Shrunk):</div>
    <div class="formula-eq">v_bowl, i = ( E[R_conc | c_i] - R_conc, i ) + lambda_eff, i * ( W_bowl, i - E[W_bowl | c_i] )</div>
    <div class="formula-eq">SBVA_p^shrunk = [ N_eff, p^bowl / ( N_eff, p^bowl + 500 ) ] * [ sum( w_i * v_bowl, i ) / sum_legal( w_i ) ]</div>
</div>

<h2 class="section-header">Section 6 &mdash; Fairness, Eligibility, and Shrinkage Mechanics</h2>
<p>
<strong>Qualification Threshold:</strong> <i>N</i>(<i>P</i> &ge; 50) &ge; 50 balls faced (batting) or legal deliveries (bowling). Exactly 297 batters and 292 bowlers met this requirement.
</p>
<p>
<strong>Exact Shrinkage Retention Dynamics (Retention = <i>N</i><sub>eff</sub> / (<i>N</i><sub>eff</sub> + <i>K</i>)):</strong>
</p>
<ul>
    <li><strong>At <i>N</i><sub>eff</sub> = <i>K</i>:</strong> Retention is exactly 50.0%; 50.0% is regressed toward replacement level.</li>
    <li><strong>Batting Retention (<i>K</i><sub>bat</sub> = 600):</strong> Vaibhav Sooryavanshi (ESS 506.9) retains 45.79%; Tim David (ESS 980.6) retains 62.04%; Heinrich Klaasen (ESS 1142.0) retains 65.56%; Phil Salt (ESS 1364.7) retains 69.46%; Abhishek Sharma (ESS 1923.3) retains 76.22%; Suryakumar Yadav (ESS 2287.2) retains 79.22%; Jos Buttler (ESS 2330.2) retains 79.52%. Retention reaches 80.0% at ESS = 2400.</li>
    <li><strong>Bowling Retention (<i>K</i><sub>bowl</sub> = 500):</strong> Abrar Ahmed (ESS 604.7) retains 54.74%; Josh Hazlewood (ESS 1159.5) retains 69.87%; Sunil Narine (ESS 1246.3) retains 71.37%; Jasprit Bumrah (ESS 1369.7) retains 73.26%; Wanindu Hasaranga (ESS 1675.4) retains 77.02%; Bhuvneshwar Kumar (ESS 1875.7) retains 78.95%; Rashid Khan (ESS 2245.9) retains 81.79%. Retention reaches 80.0% at ESS = 2000.</li>
</ul>

<div class="page-break"></div>

<!-- PAGE 8: VISUAL REFERENCE - SHRINKAGE FUNNELS -->
<h2 class="section-header">Visual Reference: Empirical Bayes Shrinkage Funnels</h2>

<div class="figure-container">
    <img src="outputs/step_7_empirical_calibration/step_7_3_shrinkage_pressure_calibration/batting_shrinkage_funnel.png" alt="Batting Shrinkage Funnel" style="max-height: 290pt;">
    <div class="figure-caption">Figure 3: Batting Empirical Bayes Shrinkage Funnel showing convergence of raw PWSVA toward population baseline (K = 600).</div>
</div>

<div class="figure-container">
    <img src="outputs/step_7_empirical_calibration/step_7_3_shrinkage_pressure_calibration/bowling_shrinkage_funnel.png" alt="Bowling Shrinkage Funnel" style="max-height: 290pt;">
    <div class="figure-caption">Figure 4: Bowling Empirical Bayes Shrinkage Funnel showing convergence of raw SBVA toward population baseline (K = 500).</div>
</div>

<div class="page-break"></div>

<!-- PAGE 9: UNCERTAINTY QUANTIFICATION -->
<h2 class="section-header">Section 6.3 &mdash; Uncertainty Quantification: Match-Level Block Bootstrap</h2>
<p>
To evaluate estimation stability without parametric assumptions, we execute 1,000 match-level block bootstrap iterations. By resampling entire match clusters rather than isolated deliveries, within-match tactical correlation, bowler-batter matchup dependencies, and pitch variance are strictly preserved.
</p>

<div class="figure-container">
    <img src="outputs/step_7_empirical_calibration/step_7_4_final_rankings/score_distributions.png" alt="Bootstrap Uncertainty" style="max-height: 310pt;">
    <div class="figure-caption">Figure 5: Bootstrap Score Distributions and 95% Confidence Intervals for Top 10 Batting and Bowling Reliability Leaderboards.</div>
</div>

<h3 class="subsection-header">Interpretation of Overlapping Confidence Intervals</h3>
<p>
Bootstrap confidence bounds for adjacent ranks overlap (e.g., Ranks 2&ndash;5 in batting and Ranks 6&ndash;10 in bowling). In sports analytics, point estimates reflect the expected mean, but overlapping intervals signify performance tiers. Small rank differences (&lt; 0.003 runs/ball) represent comparable elite execution under pressure rather than definitive superiority.
</p>

<div class="page-break"></div>

<!-- PAGE 10: EMPIRICAL VALIDATION & PHASE SPECIALIZATION -->
<h2 class="section-header">Section 7 &mdash; Empirical Validation and Auditing Evidence</h2>

<h3 class="subsection-header">7.1 Baseline Out-of-Sample Calibration (Step 7.1)</h3>
<p>
The 36-cell empirical baseline was evaluated via 5-fold cross-validation across 186,780 deliveries:
</p>
<ul>
    <li><strong>Batting Out-of-Sample RMSE:</strong> 1.71 to 1.76 runs per delivery across all 5 validation folds.</li>
    <li><strong>Prediction Bias:</strong> &lt; 0.004 runs per delivery (near-zero mean calibration error).</li>
    <li><strong>Zero Data Leakage:</strong> Wicket frequencies and expected runs were computed strictly on training folds.</li>
</ul>

<h3 class="subsection-header">7.2 Sensitivity to Pressure Exponent (&alpha; = 1.00 vs. 1.25)</h3>
<p>
To verify that rankings are robust to super-linear weighting, scores were recalculated with &alpha; = 1.25:
</p>
<ul>
    <li><strong>Batting Spearman Correlation:</strong> &rho; = 0.9978 across all 297 qualified batters. Top 8 positions are 100% invariant.</li>
    <li><strong>Bowling Spearman Correlation:</strong> &rho; = 0.9981 across all 292 qualified bowlers. Top 5 positions are 100% invariant. Mohammed Shami climbs from #13 to #7 due to extreme concentration in death climaxes (<i>P</i> &ge; 75).</li>
</ul>

<h3 class="subsection-header">7.3 Phase Specialization Dynamics</h3>
<p>
Evaluating unshrunk pressure-weighted situational value added per ball within each match phase (Figures 7 and 8) reveals distinct tactical masteries:
</p>
<ul>
    <li><strong>Powerplay Specialists:</strong> Abhishek Sharma (+0.40 on 1462b), Phil Salt (+0.32 on 950b), and Josh Hazlewood (+0.30 on 732b).</li>
    <li><strong>Middle-Overs Masters:</strong> Heinrich Klaasen (+0.39 on 915b), Suryakumar Yadav (+0.44 on 1673b), and Mujeeb Ur Rahman (+0.38 on 306b).</li>
    <li><strong>Lethal Death Enforcers:</strong> Sunil Narine (+0.71 net runs saved/ball on 204b), Rashid Khan (+0.45 on 516b), and Jasprit Bumrah (+0.42 on 526b).</li>
</ul>

<div class="page-break"></div>

<!-- PAGE 11: VISUAL REFERENCE - PHASE HEATMAPS -->
<h2 class="section-header">Visual Reference: Phase Performance Heatmaps</h2>

<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig_7_batting_phase_heatmap.png" alt="Batting Phase Heatmap" style="max-height: 290pt;">
    <div class="figure-caption">Figure 7: Batting Phase Performance Heatmap (Powerplay vs. Middle vs. Death Value Added per Ball).</div>
</div>

<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig_8_bowling_phase_heatmap.png" alt="Bowling Phase Heatmap" style="max-height: 290pt;">
    <div class="figure-caption">Figure 8: Bowling Phase Performance Heatmap (Powerplay vs. Middle vs. Death Net Runs Saved per Ball).</div>
</div>

<div class="page-break"></div>

<!-- PAGE 12: MARQUEE STARS & CONCLUSION -->
<h3 class="subsection-header">7.4 Cross-Format Descriptive Associations</h3>
<p>
Evaluating players with &ge; 50 deliveries in both IPL and T20Is:
</p>
<ul>
    <li><strong>Batting (Unique Striker ID Disambiguated):</strong> <i>N</i> = 90, Pearson <i>r</i> = 0.1149, Spearman &rho; = 0.1645 (<i>p</i> = 0.1215).</li>
    <li><strong>Bowling (Zero Name Collisions):</strong> <i>N</i> = 97, Pearson <i>r</i> = 0.2338, Spearman &rho; = 0.2956 (<i>p</i> = 0.0033).</li>
</ul>
<p>
These descriptive correlations show that batting pressure performance exhibits higher environment sensitivity (&rho; = 0.1645), reflecting differing team roles, while bowling execution exhibits greater stability (&rho; = 0.2956). This justifies empirical Bayes shrinkage across differing format sample sizes.
</p>

<h2 class="section-header">Section 8 &mdash; Placement of Prominent International &amp; Franchise Stars</h2>
<table class="report-table">
<thead>
<tr>
    <th>Player Name</th>
    <th>Discipline</th>
    <th>Official Rank</th>
    <th>Shrunk Score</th>
    <th>Raw Score</th>
    <th>Balls</th>
    <th>Kish ESS</th>
    <th>95% Score CI</th>
</tr>
</thead>
<tbody>
<tr><td class="bold">Heinrich Klaasen</td><td>Batting</td><td class="bold">#5</td><td class="bold primary">+0.2201</td><td>+0.3357</td><td>1409</td><td>1142.0</td><td>[+0.1238, +0.3072]</td></tr>
<tr><td class="bold">Phil Salt</td><td>Batting</td><td class="bold">#6</td><td class="bold primary">+0.1954</td><td>+0.2813</td><td>1591</td><td>1364.7</td><td>[+0.0633, +0.3033]</td></tr>
<tr><td class="bold">Travis Head</td><td>Batting</td><td class="bold">#8</td><td class="bold primary">+0.1625</td><td>+0.2611</td><td>1096</td><td>988.6</td><td>[+0.0017, +0.3203]</td></tr>
<tr><td class="bold">Shreyas Iyer</td><td>Batting</td><td class="bold">#14</td><td class="bold primary">+0.1350</td><td>+0.1887</td><td>1751</td><td>1507.1</td><td>[+0.0085, +0.2366]</td></tr>
<tr><td class="bold">Jos Buttler</td><td>Batting</td><td class="bold">#17</td><td class="bold primary">+0.1306</td><td>+0.1642</td><td>2675</td><td>2330.2</td><td>[+0.0366, +0.2187]</td></tr>
<tr><td class="bold">Mitchell Marsh</td><td>Batting</td><td class="bold">#19</td><td class="bold primary">+0.1272</td><td>+0.1796</td><td>1656</td><td>1456.7</td><td>[+0.0069, +0.2471]</td></tr>
<tr><td class="bold">Virat Kohli</td><td>Batting</td><td class="bold">#34</td><td class="bold primary">+0.0850</td><td>+0.1081</td><td>2445</td><td>2201.2</td><td>[+0.0005, +0.1547]</td></tr>
<tr><td class="bold">Rohit Sharma</td><td>Batting</td><td class="bold">#168</td><td class="bold primary">-0.0164</td><td>-0.0231</td><td>1561</td><td>1451.1</td><td>[-0.1574, +0.0988]</td></tr>
<tr><td class="bold">Rashid Khan</td><td>Bowling</td><td class="bold">#1</td><td class="bold primary">+0.1756</td><td>+0.2147</td><td>2648</td><td>2245.9</td><td>[+0.0810, +0.2784]</td></tr>
<tr><td class="bold">Jasprit Bumrah</td><td>Bowling</td><td class="bold">#2</td><td class="bold primary">+0.1541</td><td>+0.2103</td><td>1606</td><td>1369.7</td><td>[+0.0237, +0.2784]</td></tr>
<tr><td class="bold">Sunil Narine</td><td>Bowling</td><td class="bold">#3</td><td class="bold primary">+0.1442</td><td>+0.2020</td><td>1464</td><td>1246.3</td><td>[+0.0555, +0.2334]</td></tr>
<tr><td class="bold">Josh Hazlewood</td><td>Bowling</td><td class="bold">#4</td><td class="bold primary">+0.1330</td><td>+0.1904</td><td>1368</td><td>1159.5</td><td>[+0.0021, +0.2830]</td></tr>
<tr><td class="bold">Mohammed Shami</td><td>Bowling</td><td class="bold">#13</td><td class="bold primary">+0.0989</td><td>+0.1438</td><td>1228</td><td>1100.8</td><td>[-0.0629, +0.2621]</td></tr>
<tr><td class="bold">Trent Boult</td><td>Bowling</td><td class="bold">#16</td><td class="bold primary">+0.0922</td><td>+0.1272</td><td>1501</td><td>1313.6</td><td>[-0.0131, +0.2146]</td></tr>
<tr><td class="bold">Axar Patel</td><td>Bowling</td><td class="bold">#66</td><td class="bold primary">+0.0195</td><td>+0.0239</td><td>2604</td><td>2218.5</td><td>[-0.0665, +0.1117]</td></tr>
</tbody>
</table>

<h2 class="section-header">Section 9 &mdash; Limitations and Future Enhancements</h2>
<p>
1. <strong>Striker Run-Out Attribution:</strong> Striker run-out dismissals are attributed to the striker (<i>W</i><sub>striker</sub> = 1), while non-striker run-outs are attributed to team match state rather than individual batters. 2. <strong>Residual Environmental Variance:</strong> Factors such as pitch deterioration across a tournament, evening dew in the second innings, venue altitude, and asymmetrical boundary dimensions are not explicitly modeled in the ball-by-ball state space. While the match-level block bootstrap accounts for delivery clustering and match-level sampling variability, unobserved environmental factors remain residual variance. 3. <strong>Discrete Empirical Baseline:</strong> The 36-cell tensor groups overs into coarse phases (Powerplay, Middle, Death) and wickets into three buckets (0-3, 4-6, 7+). Future iterations (SupeRR 3.0) will incorporate continuous 2D Gaussian process surfaces over remaining deliveries and wickets.
</p>

<h2 class="section-header">Section 10 &mdash; Conclusion</h2>
<p>
The SupeRR Selector Round 1 reliability system establishes an uncompromised, reproducible standard for T20 evaluation. By decomposing pressure into Task Difficulty and Match Consequence, contrasting performance against a 36-cell empirical baseline, and applying Empirical Bayes shrinkage, the engine delivers transparent, evidence-based rankings that stand up to rigorous statistical audit.
</p>

<div style="margin-top: 8pt; font-size: 7.2pt; color: #718096; text-align: center; border-top: 0.5pt solid #e2e8f0; padding-top: 3pt;">
    Official Methodology Report &middot; SupeRR Selector 2.0 (Round 1) &middot; Antigravity Autonomous Audit Team &middot; November 2026
</div>

</body>
</html>
"""

    pdf_html = raw_html_template.replace("__HTML_BAT_TABLE__", html_bat_table).replace("__HTML_BOWL_TABLE__", html_bowl_table)

    # 6. Render PDF via PyMuPDF Story
    pdf_path = 'outputs/step_10_methodology_report/step_10_methodology_report.pdf'
    raw_pdf_path = 'scratch/raw_step10_4_methodology_report.pdf'

    archive = pymupdf.Archive('.')
    writer = pymupdf.DocumentWriter(raw_pdf_path)
    story = pymupdf.Story(html=pdf_html, archive=archive)

    def rectfn(rect_num, filled):
        mediabox = pymupdf.paper_rect('letter')
        rect = pymupdf.Rect(40, 34, mediabox.width - 40, mediabox.height - 34)
        return mediabox, rect, pymupdf.Identity

    story.write(writer, rectfn)
    writer.close()

    # 7. Add Running Headers and Footers to Every Page
    doc = pymupdf.open(raw_pdf_path)
    total_pages = len(doc)
    print(f"Generated raw PDF with {total_pages} pages.")
    assert total_pages == 12, f"Target page count is 12, got {total_pages}"

    for pno in range(total_pages):
        page = doc[pno]
        if pno > 0:
            page.insert_text(
                (40, 24),
                "SupeRR Selector 2.0 — Official Methodology Report",
                fontsize=7.5,
                color=(0.35, 0.4, 0.45)
            )
        page.insert_text(
            (40, page.rect.height - 20),
            "Confidential — Prepared for SupeRR Selector Round 1 Competition Judges",
            fontsize=7.5,
            color=(0.5, 0.5, 0.5)
        )
        page_str = f"Page {pno + 1} of {total_pages}"
        tw = pymupdf.get_text_length(page_str, fontname="helv", fontsize=7.5)
        page.insert_text(
            (page.rect.width - 40 - tw, page.rect.height - 20),
            page_str,
            fontsize=7.5,
            color=(0.3, 0.3, 0.3)
        )

    doc.save(pdf_path, deflate=True, garbage=4)
    doc.close()
    del doc
    del writer
    gc.collect()

    try:
        if os.path.exists(raw_pdf_path):
            os.remove(raw_pdf_path)
    except Exception as e:
        print(f"Notice: Could not remove temporary raw PDF: {e}")

    print(f"Successfully generated restored PDF at {pdf_path} (Pages: {total_pages}, Size: {os.path.getsize(pdf_path)} bytes).")
    return True

if __name__ == '__main__':
    build_step10_4_report()
