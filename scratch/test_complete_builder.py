import os
import sys
import re
import gc
import pandas as pd
import numpy as np
import pymupdf

def build_and_verify():
    print("=" * 80)
    print("TEST COMPLETE BUILDER: STEP 10 REPORT (WITH KNOCKOUT EXPERIMENT)")
    print("=" * 80)

    # 1. Load Authoritative Step 7.4 CSVs
    bat_csv_path = 'outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_batting_rankings.csv'
    bowl_csv_path = 'outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_bowling_rankings.csv'
    df_bat = pd.read_csv(bat_csv_path).head(10)
    df_bowl = pd.read_csv(bowl_csv_path).head(10)

    print(f"Loaded {len(df_bat)} batting rows and {len(df_bowl)} bowling rows.")

    # 2. Build Markdown Top 10 Tables (ASCII Codeblocks)
    md_bat_table = """```
========================================================================================================================
Rank  Player                  Team / Franchise            Shrunk Score  Raw Score  Balls Faced Kish ESS 95% Bootstrap CI
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
        md_bat_table += f"{rank:<5} {player:<23} {team:<27} {shrunk:>12} {raw:>10} {balls:>11} {ess:>9}  {ci}\n"
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

    # 3. Build HTML Top 10 Tables (Booktabs Border Styling matching build_step10_2)
    def make_html_table(df, discipline):
        rows = []
        for _, r in df.iterrows():
            rank = f"#{int(r['Rank'])}"
            player = r['Player']
            team = r['Team/format'].replace('(IPL & T20I)', '(IPL/T20I)')
            shrunk = f"<strong>{r['Shrunk score']:+.4f}</strong>"
            raw = f"{r['Raw score']:+.4f}"
            balls = f"{int(r['Raw opportunities'])}"
            ess = f"{r['Kish ESS']:.1f}"
            ci = r['95% CI'].replace('[', '[+').replace(', ', ', +').replace('+-', '-')
            
            row_html = f"<tr><td>{rank}</td><td>{player}</td><td>{team}</td><td>{shrunk}</td><td>{raw}</td><td>{balls}</td><td>{ess}</td><td>{ci}</td></tr>"
            rows.append(row_html)
            
        table_html = "<table>\n<tr>\n    <th>Rank</th><th>Player Name</th><th>Team / Franchise</th><th>Shrunk Score</th><th>Raw Score</th><th>Balls</th><th>Kish ESS</th><th>95% Bootstrap CI</th>\n</tr>\n" + "\n".join(rows) + "\n</table>"
        return table_html

    html_bat_table = make_html_table(df_bat, "Batting")
    html_bowl_table = make_html_table(df_bowl, "Bowling")

    # 4. Define Full Markdown Text
    full_markdown_text = """# SupeRR Selector 2.0: Official Technical Methodology and Reliability Calibration Report
## A Dual-Dimensional Situational Pressure Framework with Empirical Bayes Shrinkage

**Author:** Amit N Suthar  
**Competition:** SupeRR Selector Season 2026 (Round 1 Submission)  
**Dataset Coverage:** 742 Elite Men's T20 Matches (IPL & T20I, 2022–2026, $N = 186,780$ deliveries)  
**Authoritative Source Baseline:** Frozen Step 7.4 Outputs (`outputs/step_7_empirical_calibration/step_7_4_final_rankings/`)  
**Status:** Certified Authoritative Baseline (Fully Audited & Restored)

---

## Section 1 — Executive Summary

### 1.1 Core Mandate & Architectural Overview
Conventional T20 metrics systematically reward stat-padding in low-leverage phases while failing to isolate true execution under match pressure. A boundary hit when needing 85 off 12 deliveries is treated identically to a boundary struck when needing 14 off 6. Similarly, dot balls delivered during low-risk middle overs are conflated with ice-cold execution in death-over climaxes.

The **SupeRR Selector 2.0 Reliability Engine** resolves these fundamental distortions through a rigorous four-stage pipeline:
1. **Dual-Dimensional Delivery Pressure ($P \in [0, 100]$):** Evaluates every pre-delivery match state $S_t$ strictly at release ($t^-$) through two orthogonal axes: physical/tactical **Task Difficulty** ($T$) and win-probability **Match Consequence** ($L$).
2. **Phase-Conditioned Situational Value Added (SVA):** Benchmarks every delivery outcome against a 36-cell empirical baseline $E[R \mid \text{Phase}, W_t, I_t]$ calibrated across 186,780 historical balls.
3. **Kish Effective Sample Size ($\text{ESS}$):** Replaces raw ball counts with variance-adjusted weighting to reflect true informational depth.
4. **Empirical Bayes Shrinkage:** Shrinks volatile, small-sample raw estimates toward cohort priors to ensure that leaderboard ranks represent true underlying skill.

### 1.2 Executive TL;DR: Summary of Methodology, Mathematics, and Key Findings
- **Our Methodology in Brief:** We model every delivery prior to release ($t^-$), measuring the athletic and tactical difficulty of the situation alongside the win-probability swing at stake. Player outcomes are then compared against historical empirical expectations across 36 phase-and-wicket match states, isolating pure individual value added above baseline.
- **Our Mathematical Formula & Meaning:** Combined pressure is defined as $P(S_t) = \sqrt{T(S_t) \times L_{\\text{norm}}(S_t)} \in [0, 100]$. This multiplicative geometric mean enforces strict orthogonal gating: if match consequence is zero (garbage time), pressure is zero; if athletic difficulty is zero (trivial target), pressure is zero. True pressure exists only when high consequence intersects difficult execution.
- **Official Results & Elite Performers:**
  - *Batting Leaderboard:* Led by Vaibhav Sooryavanshi (+0.3487 shrunk, raw +0.7614, ESS 506.9), Suryakumar Yadav (+0.2819 shrunk, ESS 2287.2), Abhishek Sharma (+0.2703 shrunk, ESS 1923.3), Tim David (+0.2571 shrunk), and Heinrich Klaasen (+0.2201 shrunk).
  - *Bowling Leaderboard:* Led by Rashid Khan (+0.1756 shrunk, ESS 2245.9), Jasprit Bumrah (+0.1541 shrunk, ESS 1369.7), Sunil Narine (+0.1442 shrunk, ESS 1246.3), Josh Hazlewood (+0.1330 shrunk, ESS 1159.5), and Wanindu Hasaranga (+0.1184 shrunk, ESS 1675.4).
- **Flaws, Limitations & Future Enhancements:** Current modeling attributes striker run-outs to the striker ($W_{\\text{striker}} = 1$) while non-striker run-outs are treated as team variance; pitch wear, dew, and ground dimensions remain unmodeled residual environmental variance; and the 36-cell baseline relies on discrete phase/wicket buckets rather than continuous 2D Gaussian process surfaces.
- **Auditing Conclusion:** The framework successfully addresses several limitations of conventional cricket metrics, reduces small-sample instability through shrinkage, and demonstrates robust rank stability under sensitivity testing ($\rho > 0.997$ under super-linear pressure weighting).

### 1.3 Executive Leaderboards

#### Official Top 10 Batting Reliability Rankings (PWSVA)
""" + md_bat_table + """

#### Official Top 10 Bowling Reliability Rankings (SBVA)
""" + md_bowl_table + """

---

## Section 2 — Dataset and Scope

### 2.1 Scope of Data
The evaluation dataset is drawn from top-tier men's T20 cricket spanning January 1, 2022 through May 31, 2026:
- **Indian Premier League (IPL):** 365 matches (seasons 2022, 2023, 2024, 2025, and 2026).
- **Men's T20 Internationals (T20I):** All official ICC encounters among full-member nations and major ICC tournament fixtures.
- **Delivery Cohort:** 186,780 valid ball-by-ball deliveries across 742 unique matches.

### 2.2 Pre-Delivery Data Hygiene & State Representation
Every delivery is represented as a pre-delivery state vector $S_t = (I_t, B_{\\text{elapsed}}, B_{\\text{rem}}, R_{\\text{curr}}, R_{\\text{target}}, R_{\\text{req}}, W_t, W_{\\text{rem}}, \\text{Phase}_t, \\text{Format}_t, V_{\\text{venue}})$. Strict data hygiene ensures:
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
To enforce this orthogonal symmetry, delivery-level pressure ($P$) is defined as the geometric mean of Task Difficulty ($T$) and Normalized Match Consequence ($L_{\\text{norm}}$):
$$P(S_t) = \\sqrt{T(S_t) \\times L_{\\text{norm}}(S_t)} \\in [0, 100]$$

Where:
- $T(S_t) \\in [0, 100]$ evaluates the pre-delivery physical and tactical difficulty facing the player.
- $L_{\\text{norm}}(S_t) \\in [0, 100]$ evaluates the normalized win probability swing across all plausible delivery outcomes.
- Both components are computed strictly at $t^-$ (prior to ball release), completely eliminating outcome bias.
- **Scale Interpretation:**
  - $P < 25$: Low pressure / blowout / early innings baseline.
  - $25 \\le P < 50$: Moderate pressure / standard league baseline.
  - $50 \\le P < 75$: High pressure / late-innings or close-chase leverage.
  - $P \\ge 75$: Extreme pressure / death-over climaxes and sudden-death swings.

---

## Section 4 — Calculating Delivery-Level Pressure (Frozen Step 4 Engine)

### 4.1 Task Difficulty Architecture: The Four Separate Sub-Models
Task Difficulty is evaluated through four distinct, specialized logistic sub-models reflecting the differing tactical objectives across innings and disciplines:

#### 1. Batting Innings 1 Task Difficulty ($T_{B1}$)
In the first innings, batters face the dual burden of accelerating scoring while conserving wickets:
$$Z_{B1} = 0.60 \\times \\text{RAR} + 0.40 \\times W_{\\text{stress}}$$
$$T_{B1} = \\frac{100}{1 + \\exp\\left(-1.20 \\times \\text{clip}(Z_{B1}, -20, 20)\\right)}$$
- $\\text{RAR} = \\frac{\\text{CRR} - 8.10}{2.50}$: Required Acceleration Rate relative to T20 par scoring (8.10 runs/over, $\\sigma = 2.50$).
- $W_{\\text{stress}} = \\frac{W_t - 3.50}{2.00}$: Wickets lost stress relative to average wicket loss ($3.50, \\sigma = 2.00$).

#### 2. Batting Innings 2 Task Difficulty ($T_{B2}$)
In the chase, the required run rate and remaining wickets interact multiplicatively:
$$Z_{B2} = 0.55 \\times Z_{\\text{RRR}} + 0.25 \\times Z_{W2} + 0.20 \\times Z_{\\text{inter}}$$
$$T_{B2} = \\frac{100}{1 + \\exp\\left(-1.00 \\times \\text{clip}(Z_{B2}, -20, 20)\\right)}$$
- $Z_{\\text{RRR}} = \\frac{\\text{RRR} - 8.10}{3.00}$: Required run rate stress.
- $Z_{W2} = \\frac{W_t - 3.50}{2.00}$: Wickets lost stress.
- $Z_{\\text{inter}} = \\frac{\\text{RRR} \\times W_t - 28.0}{25.0}$: Non-linear crisis interaction term capturing simultaneous high rate and depleted resources.

#### 3. Bowling Innings 1 Task Difficulty ($T_{BO1}$)
In the first innings, bowlers defend against batting momentum and fielding constraints:
$$Z_{BO1} = 0.50 \\times \\text{CRR}_{\\text{stress}} + 0.35 \\times W_{\\text{opp}} + 0.15 \\times \\text{FieldFactor}$$
$$T_{BO1} = \\frac{100}{1 + \\exp\\left(-1.10 \\times \\text{clip}(Z_{BO1}, -20, 20)\\right)}$$
- $\\text{CRR}_{\\text{stress}} = \\frac{\\text{CRR} - 8.10}{2.50}$: Opponent scoring velocity.
- $W_{\\text{opp}} = \\frac{(10 - W_t) - 6.50}{2.00}$: Opponent batting depth remaining.
- $\\text{FieldFactor} = 0.50$ during Powerplay and Death overs (0.00 during Middle overs).

#### 4. Bowling Innings 2 Task Difficulty ($T_{BO2}$)
In the chase, bowlers face extreme pressure when defending low remaining targets:
$$Z_{BO2} = 0.60 \\times \\text{RRR}_{\\text{def}} + 0.40 \\times W_{\\text{opp2}}$$
$$T_{BO2} = \\frac{100}{1 + \\exp\\left(-1.00 \\times \\text{clip}(Z_{BO2}, -20, 20)\\right)}$$
- $\\text{RRR}_{\\text{def}} = \\frac{8.10 - \\text{RRR}}{3.00}$: Defending low required run rates.
- $W_{\\text{opp2}} = \\frac{(10 - W_t) - 6.50}{2.00}$: Batting wickets remaining for the chasing team.

### 4.2 Expected Match Consequence $L(S_t)$ Across Discrete Outcomes
Pre-delivery consequence evaluates the potential win-probability volatility of the upcoming delivery. Rather than relying on actual ball outcomes, $L(S_t)$ computes the expected win-probability swing across all **nine discrete potential outcomes**:
$$L(S_t) = \\sum_{o \\in \\mathcal{O}} P(o) \\cdot \\left| \\text{WP}(S_{t+1}^{(o)}) - \\text{WP}(S_t) \\right|$$

Where:
- $\\mathcal{O} = \\{0, 1, 2, 3, 4, 6, \\text{Wicket}, \\text{Wide}, \\text{NoBall}\\}$ represents the nine canonical delivery outcomes.
- $P(o)$ is the empirical outcome probability conditioned on phase and wickets.
- $\\text{WP}(S_t)$ is the pre-delivery win probability from the validated win-probability engine.

### 4.3 Innings-Stratified ECDF Normalization ($L_{\\text{norm}}$)
Because first-innings win-probability swings have lower absolute variance than second-innings chase climaxes, raw $L(S_t)$ values are normalized via **separate empirical cumulative distribution functions (ECDF)**:
$$L_{\\text{norm}}(S_t) = 100 \\times \\text{ECDF}_{I_t}\\left(L(S_t)\\right)$$
- **First Innings ($N_1 = 96,165$):** Evaluated strictly against the historical first-innings consequence distribution.
- **Second Innings ($N_2 = 90,615$):** Evaluated strictly against the historical second-innings consequence distribution.
- This guarantees uniform $[0, 100]$ calibration across both innings, preventing second-innings bias.

---

## Section 5 — Measuring Player Reliability: PWSVA and SBVA

### 5.1 The 36-Cell Empirical Situational Baseline
Every delivery outcome is compared against the empirical expectation of that exact match state, structured as a 36-cell tensor:
$$\\text{Cell}(S_t) = \\text{Phase}(3) \\times \\text{Wicket Bucket}(3) \\times \\text{Innings}(2) \\times \\text{Format}(2) = 36 \\text{ discrete states}$$

For every cell, two baseline expectations are pre-calculated:
- $E[R \\mid \\text{Cell}]$: Expected runs conceded per delivery.
- $E[W \\mid \\text{Cell}]$: Expected probability of a wicket per delivery.

### 5.2 Batting: Pressure-Weighted Situational Value Added (PWSVA)
For a batter facing delivery $i$, raw value added contrasts runs scored and wicket preservation against baseline:
$$\\text{SVA}_{\\text{bat}, i} = (R_i - E[R \\mid \\text{Cell}_i]) - V_W \\times (W_i - E[W \\mid \\text{Cell}_i])$$

Where $V_W = 4.50$ runs represents the empirically calibrated value of wicket preservation. The delivery is weighted by normalized pressure:
$$w_i = \\left(\\frac{P_i}{100}\\right)^{\\alpha}, \\quad \\alpha = 1.00$$
$$\\text{PWSVA}_j = \\frac{\\sum_{i \\in \\mathcal{D}_j} w_i \\times \\text{SVA}_{\\text{bat}, i}}{\\sum_{i \\in \\mathcal{D}_j} w_i}$$

### 5.3 Bowling: Situational Bowling Value Added (SBVA)
Bowlers are evaluated on run suppression and breakthrough generation:
$$\\text{SVA}_{\\text{bowl}, i} = (E[R \\mid \\text{Cell}_i] - R_{\\text{conceded}, i}) + V_W \\times (W_i - E[W \\mid \\text{Cell}_i])$$
$$\\text{SBVA}_j = \\frac{\\sum_{i \\in \\mathcal{D}_j} w_i \\times \\text{SVA}_{\\text{bowl}, i}}{\\sum_{i \\in \\mathcal{D}_j} w_i}$$

#### Treatment of Extras and Non-Legal Deliveries
- **Wides and No-Balls:** Conceded runs (including penalty extras) enter $R_{\\text{conceded}, i}$. The delivery is included in the numerator but receives zero credit in legal ball counts ($B_{\\text{legal}}$), ensuring bowlers are appropriately penalized for indiscipline without inflating opportunity denominators.
- **Run-Out Attribution:** Striker run-outs are attributed to the striker ($W_{\\text{striker}} = 1$) for batting SVA. Non-striker run-outs are treated as team variance. Bowlers do not receive credit for run-outs unless executing direct-hit fielding.

### 5.4 Explicit Contrast Against Normal Situations: Individual Pressure Lift ($\\Delta$)
The core mandate of Round 1 requires identifying top performers under pressure *compared to normal match situations*. The SupeRR Selector framework provides a two-level baseline architecture to satisfy this:
1. **Level 1 (Situational Match Expectation):** Every delivery outcome is evaluated relative to the 36-cell empirical baseline $E[R \\mid \\text{Cell}]$ and $E[W \\mid \\text{Cell}]$, isolating execution quality from favorable match contexts.
2. **Level 2 (Individual Pressure Lift $\\Delta$):** We explicitly contrast a player's execution in high-pressure match states ($P \\ge 50$) against their own baseline in routine, low-pressure states ($P < 50$):
   $$\\Delta_j = \\text{SVA}_j(P \\ge 50) - \\text{SVA}_j(P < 50)$$

#### Empirical Findings Across Qualified Cohorts:
- **Macro Cohort Degradation:** At the overall population level, batting execution degrades as pressure rises (population mean SVA drops from $+0.032$ runs/ball at $P < 50$ to $+0.004$ at $P \\ge 50$), while bowling run concession tightens.
- **Batting Pressure Elevation:** Top-ranked batters actively elevate their production when stakes peak:
  - **Vaibhav Sooryavanshi (#1):** $\\text{SVA}_{P \\ge 50} = +0.836$ vs. $\\text{SVA}_{P < 50} = +0.629$ ($\\Delta = +0.207$ runs/ball, $+32.9\\%$ elevation).
  - **Phil Salt (#6):** $\\text{SVA}_{P \\ge 50} = +0.378$ vs. $\\text{SVA}_{P < 50} = +0.263$ ($\\Delta = +0.115$ runs/ball, $+43.7\\%$ elevation).
  - **Heinrich Klaasen (#5):** $\\text{SVA}_{P \\ge 50} = +0.395$ vs. $\\text{SVA}_{P < 50} = +0.318$ ($\\Delta = +0.077$ runs/ball, $+24.2\\%$ elevation).
  - **Suryakumar Yadav (#2):** $\\text{SVA}_{P \\ge 50} = +0.379$ vs. $\\text{SVA}_{P < 50} = +0.343$ ($\\Delta = +0.037$ runs/ball).
  - **Tim David (#4):** $\\text{SVA}_{P \\ge 50} = +0.417$ vs. $\\text{SVA}_{P < 50} = +0.407$ ($\\Delta = +0.010$ runs/ball).
- **Bowling Pressure Surge:** Elite bowlers demonstrate extraordinary surges under high leverage ($P \\ge 50$):
  - **Rashid Khan (#1):** Surges from $+0.109$ runs saved/ball in routine play to $+0.267$ under pressure ($\\Delta = +0.159$, a $+145.9\\%$ efficiency surge).
  - **Josh Hazlewood (#4):** Surges from $+0.038$ runs saved/ball to $+0.198$ under pressure ($\\Delta = +0.161$, a $+421.1\\%$ efficiency surge).
  - **Mujeeb Ur Rahman (#10):** Surges from $+0.058$ runs saved/ball to $+0.212$ under pressure ($\\Delta = +0.153$, a $+265.5\\%$ efficiency surge).
  - **Wanindu Hasaranga (#5):** Surges from $+0.135$ to $+0.216$ runs saved/ball ($\\Delta = +0.081$, a $+60.0\\%$ efficiency surge).
  - **Bhuvneshwar Kumar (#6):** Surges from $+0.080$ to $+0.141$ runs saved/ball ($\\Delta = +0.061$, a $+76.3\\%$ efficiency surge).

---

## Section 6 — Fairness, Eligibility, and Shrinkage Mechanics

### 6.1 Kish Effective Sample Size (ESS)
Because pressure weighting introduces variance heterogeneity, unweighted ball counts distort statistical reliability. We compute the Kish Effective Sample Size (ESS):
$$\\text{ESS}_j = \\frac{\\left(\\sum_{i=1}^{N_j} w_i\\right)^2}{\\sum_{i=1}^{N_j} w_i^2}$$
- When weights are uniform, $\\text{ESS} = N_j$.
- Under concentrated high-pressure deliveries, $\\text{ESS} < N_j$, penalizing players whose opportunities were clustered in low-information garbage time.

### 6.2 Empirical Bayes Shrinkage
To prevent small-sample specialists from dominating leaderboards, raw performance is shrunk toward the qualified cohort prior:
$$\\theta_j^{\\text{shrunk}} = \\lambda_j \\cdot \\text{PWSVA}_j + (1 - \\lambda_j) \\cdot \\mu_{\\text{prior}}$$

Where the shrinkage weight $\\lambda_j$ is governed by Kish ESS and the calibrated shrinkage constant $K$:
$$\\lambda_j = \\frac{\\text{ESS}_j}{\\text{ESS}_j + K}$$
- **Batting:** $\\mu_{\\text{prior}} = 0.0000$ runs/ball, $K_{\\text{bat}} = 600.0$.
- **Bowling:** $\\mu_{\\text{prior}} = 0.0000$ runs/ball, $K_{\\text{bowl}} = 500.0$.
- **Mathematical Meaning:** A player with $\\text{ESS} = K$ receives exactly 50% shrinkage toward zero. High-volume stalwarts ($\text{ESS} > 1500$) retain $> 75\%$ of their raw execution value.

### 6.3 Uncertainty Quantification: Match-Level Block Bootstrap
Confidence intervals are generated via **1,000 match-level block bootstrap iterations**. By resampling entire matches rather than isolated deliveries, the bootstrap preserves within-match delivery correlation, partnership dependencies, and tactical game flow. Leaderboard tables display 95% bootstrap intervals.

---

## Section 7 — Empirical Validation and Auditing Evidence

### 7.1 Baseline Out-of-Sample Calibration (Step 7.1)
The 36-cell empirical baseline was evaluated via 5-fold cross-validation across 186,780 deliveries:
- **Batting Out-of-Sample RMSE:** 1.71 to 1.76 runs per delivery across all 5 validation folds.
- **Prediction Bias:** $< 0.004$ runs per delivery (near-zero mean calibration error).
- **Zero Data Leakage:** Wicket frequencies and expected runs were computed strictly on training folds.

### 7.2 Sensitivity to Pressure Exponent ($\alpha = 1.00$ vs. $1.25$)
To verify that rankings are robust to super-linear weighting, scores were recalculated with $\alpha = 1.25$ (Figure 6):
- **Batting Spearman Correlation:** $\rho = 0.9978$ across all 297 qualified batters. Top 8 positions are 100% invariant.
- **Bowling Spearman Correlation:** $\rho = 0.9981$ across all 292 qualified bowlers. Top 5 positions are 100% invariant. Mohammed Shami climbs from #13 to #7 due to extreme concentration in death climaxes ($P \ge 75$).

### 7.3 Phase Specialization Dynamics
Evaluating unshrunk pressure-weighted situational value added per ball within each match phase (Figures 7 and 8) reveals distinct tactical masteries:
- **Powerplay Specialists:** Abhishek Sharma (+0.40 on 1462b), Phil Salt (+0.32 on 950b), and Josh Hazlewood (+0.30 on 732b).
- **Middle-Overs Masters:** Heinrich Klaasen (+0.39 on 915b), Suryakumar Yadav (+0.44 on 1673b), and Mujeeb Ur Rahman (+0.38 on 306b).
- **Lethal Death Enforcers:** Sunil Narine (+0.71 net runs saved/ball on 204b), Rashid Khan (+0.45 on 516b), and Jasprit Bumrah (+0.42 on 526b).

### 7.4 Cross-Format Descriptive Associations
Evaluating players with $\ge 50$ deliveries in both IPL and T20Is:
- **Batting (Unique Striker ID Disambiguated):** $N = 90$, Pearson $r = 0.1149$, Spearman $\rho = 0.1645$ ($p = 0.1215$).
- **Bowling (Zero Name Collisions):** $N = 97$, Pearson $r = 0.2338$, Spearman $\rho = 0.2956$ ($p = 0.0033$).

These descriptive correlations show that batting pressure performance exhibits higher environment sensitivity ($\rho = 0.1645$), reflecting differing team roles, while bowling execution exhibits greater stability ($\rho = 0.2956$). This justifies empirical Bayes shrinkage across differing format sample sizes.

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

1. **Striker Run-Out Attribution:** Striker run-out dismissals are attributed to the striker ($W_{\\text{striker}} = 1$), while non-striker run-outs are attributed to team match state rather than individual batters.

2. **Residual Environmental Variance:** Factors such as pitch deterioration across a tournament, evening dew in the second innings, venue altitude, and asymmetrical boundary dimensions are not explicitly modeled in the ball-by-ball state space. While the match-level block bootstrap accounts for delivery clustering and match-level sampling variability, unobserved environmental factors remain residual variance.

3. **Discrete Empirical Baseline:** The 36-cell tensor groups overs into coarse phases (Powerplay, Middle, Death) and wickets into three buckets (0–3, 4–6, 7+). Future iterations (SupeRR 3.0) will incorporate continuous 2D Gaussian process surfaces over remaining deliveries and wickets.

---

## Section 10 — Experimental Sensitivity: Tournament Knockout Leverage

To evaluate whether high-stakes tournament stages warrant super-weighting beyond ball-by-ball situational pressure, an experimental evaluation tested multiplier bonuses ($1.10\\times$ to $1.25\\times$) on delivery pressure weights ($P$) across 19 full IPL playoff matches (4,445 deliveries), recalculating dynamic Kish Effective Sample Size ($\text{ESS}$) and Empirical Bayes shrinkage for all qualified players.

### 10.1 Key Results of the Knockout Leverage Experiment
- **Bowling Top 10 Invariance (100% Retention):** The top 4 positions remained strictly invariant (Rashid Khan #1, Jasprit Bumrah #2, Sunil Narine #3, Josh Hazlewood #4). Under playoff leverage weighting, Varun Chakravarthy surged from official #17 into #5 (displacing baseline #5 Wanindu Hasaranga to #6), while all 10 baseline bowlers retained their elite tier classification with zero dropout.
- **Batting Top 10 Dynamics (90% Retention):** The official Top 7 remained completely invariant (Vaibhav Sooryavanshi #1, Suryakumar Yadav #2, Abhishek Sharma #3, Nicholas Pooran #4, Heinrich Klaasen #5, Phil Salt #6, Cameron Green #7). Rajat Patidar entered at #8 (+3 rank gain based on 186 playoff balls), displacing Reeza Hendricks (#10 \to #11), while Travis Head slipped (#8 \to #10) due to high-leverage playoff dismissals.

### 10.2 Experimental Conclusion and Decision Rationale
The tournament knockout bonus was **rejected** from the official production methodology and frozen Step 7.4 baseline based on three core architectural principles:
1. **Severe Small-Sample Volatility:** Concentrating high leverage onto 40–180 playoff deliveries introduced excessive rank instability (e.g., Mitchell Starc surged +17 ranks on just 42 playoff balls, while Ayush Badoni dropped 9 ranks on 7 deliveries).
2. **Structural Participation Bias:** Over 69.4% of qualified batters and 72.3% of qualified bowlers had zero playoff deliveries due to franchise non-qualification, systematically penalizing elite individuals for broader team shortcomings.
3. **Intrinsic Leverage Sufficiency:** The core SupeRR Selector framework already prices match leverage directly through pre-delivery win-probability swing $L(S_t)$ and task difficulty $T(S_t)$. Imposing an external stage multiplier created redundant double-counting of high-pressure deliveries.

---

## Section 11 — Conclusion
The SupeRR Selector Round 1 reliability system establishes an uncompromised, reproducible standard for T20 evaluation. By decomposing pressure into Task Difficulty and Match Consequence, contrasting performance against a 36-cell empirical baseline, and applying Empirical Bayes shrinkage, the engine delivers transparent, evidence-based rankings that stand up to rigorous statistical audit.

---
*Official Methodology Report · SupeRR Selector 2.0 (Round 1) · Amit N Suthar · November 2026*
"""

    md_out_path = 'outputs/step_10_methodology_report/step_10_methodology_report.md'
    with open(md_out_path, 'w', encoding='utf-8') as f:
        f.write(full_markdown_text)
    print(f"Successfully wrote corrected Markdown to {md_out_path} ({len(full_markdown_text)} bytes).")

    # 5. Define HTML Template with Exact Step 4 Formulas and Pages
    raw_html_template = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {
    size: letter;
    margin: 34pt 40pt;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 8.8pt;
    line-height: 1.32;
    color: #2d3748;
}
h1.title {
    font-size: 18pt;
    font-weight: bold;
    color: #1a365d;
    margin-bottom: 2pt;
    text-align: center;
}
h2.subtitle {
    font-size: 11pt;
    font-weight: 600;
    color: #2b6cb0;
    margin-top: 0pt;
    margin-bottom: 8pt;
    text-align: center;
}
.meta-box {
    border: 1pt solid #cbd5e0;
    border-left: 3.5pt solid #3182ce;
    padding: 5pt 8pt;
    margin-bottom: 8pt;
    font-size: 7.8pt;
    line-height: 1.25;
}
.meta-box p {
    margin: 1.5pt 0;
}
h2.section-header {
    font-size: 11.5pt;
    font-weight: bold;
    color: #1a365d;
    border-bottom: 1.2pt solid #cbd5e0;
    padding-bottom: 2pt;
    margin-top: 8pt;
    margin-bottom: 5pt;
}
h3.subsection-header {
    font-size: 9.8pt;
    font-weight: bold;
    color: #2b6cb0;
    margin-top: 6pt;
    margin-bottom: 3pt;
}
p {
    margin-top: 0pt;
    margin-bottom: 5pt;
    text-align: justify;
}
ul, ol {
    margin-top: 0pt;
    margin-bottom: 5pt;
    padding-left: 14pt;
}
li {
    margin-bottom: 2pt;
}
.formula-card {
    background-color: #f7fafc;
    border: 1pt solid #e2e8f0;
    border-left: 3pt solid #3182ce;
    padding: 4.5pt 8pt;
    margin: 4pt 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 8.3pt;
    line-height: 1.38;
    color: #1a202c;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4pt;
    margin-bottom: 6pt;
    font-size: 7.8pt;
    page-break-inside: avoid;
}
th {
    border-top: 1.2pt solid #1a365d;
    border-bottom: 1.2pt solid #1a365d;
    background-color: transparent;
    color: #1a365d;
    text-align: left;
    padding: 3.5pt 4pt;
    font-weight: bold;
}
td {
    border-bottom: 0.5pt solid #cbd5e1;
    padding: 3pt 4pt;
    color: #2d3748;
}
.figure-container {
    text-align: center;
    margin: 6pt 0;
    page-break-inside: avoid;
}
.figure-caption {
    font-size: 7.5pt;
    font-weight: bold;
    color: #4a5568;
    margin-top: 3pt;
    margin-bottom: 4pt;
}
.page-break {
    page-break-before: always;
}
</style>
</head>
<body>

<!-- PAGE 1: TITLE & EXECUTIVE SUMMARY -->
<h1 class="title">SupeRR Selector 2.0: Official Technical Methodology and Reliability Calibration Report</h1>
<h2 class="subtitle">A Dual-Dimensional Situational Pressure Framework with Empirical Bayes Shrinkage</h2>

<div class="meta-box">
    <strong>Author:</strong> Amit N Suthar &nbsp;|&nbsp; <strong>Competition:</strong> SupeRR Selector Season 2026 (Round 1 Submission)<br>
    <strong>Evaluation Dataset:</strong> 742 Elite Men's T20 Matches (IPL &amp; T20I, 2022&ndash;2026, <i>N</i> = 186,780 deliveries)<br>
    <strong>Authoritative Source Baseline:</strong> Frozen Step 7.4 Outputs (<code>outputs/step_7_empirical_calibration/step_7_4_final_rankings/</code>)<br>
    <strong>Status:</strong> Certified Authoritative Baseline (Fully Audited &amp; Restored)
</div>

<h2 class="section-header">Section 1 &mdash; Executive Summary</h2>

<h3 class="subsection-header">1.1 Core Mandate &amp; Architectural Overview</h3>
<p>
Conventional T20 cricket analytics systematically over-reward accumulation in low-leverage contexts while obscuring failure under critical match strain. Striking a boundary when 85 runs are required from 12 deliveries contributes identically in traditional strike rates to striking a boundary when 14 runs are needed from 6. Similarly, dot balls delivered during non-threatening middle overs are counted equally to ice-cold death-over breakthroughs.
</p>
<p>
The <strong>SupeRR Selector 2.0 Reliability Engine</strong> addresses several limitations of conventional cricket metrics through an audited four-stage quantitative pipeline:
</p>
<ul>
    <li><strong>Dual-Dimensional Delivery Pressure (<i>P</i> &isin; [0, 100]):</strong> Evaluates every pre-delivery match state strictly at ball release (<i>t</i><sup>&minus;</sup>) by synthesizing orthogonal athletic <strong>Task Difficulty</strong> (<b>T</b>) and win-probability <strong>Match Consequence</strong> (<b>L</b>).</li>
    <li><strong>Phase-Conditioned Situational Value Added (SVA):</strong> Evaluates individual performance against an empirical 36-cell tensor baseline calibrated on 186,780 deliveries.</li>
    <li><strong>Kish Effective Sample Size (ESS):</strong> Replaces naive ball counts with variance-adjusted weighting to reflect true informational depth.</li>
    <li><strong>Empirical Bayes Shrinkage:</strong> Mitigates small-sample instability by shrinking noisy estimates toward cohort priors.</li>
</ul>

<div style="background-color: #ebf8ff; border: 1pt solid #bee3f8; border-left: 3.5pt solid #3182ce; padding: 5pt 7pt; margin: 4pt 0 2pt 0; font-size: 7.7pt; line-height: 1.25;">
    <strong style="color: #2b6cb0; font-size: 8.2pt;">Executive TL;DR &mdash; Summary of Methodology, Mathematics &amp; Results:</strong>
    <ul style="margin: 2pt 0 0 0; padding-left: 12pt;">
        <li><strong>Methodology:</strong> Every delivery is modeled prior to release (<i>t</i><sup>&minus;</sup>), evaluating situational difficulty and win-probability leverage before contrasting player performance against an empirical 36-cell expectation baseline.</li>
        <li><strong>Formula &amp; Meaning:</strong> Combined pressure is <b>P</b>(<i>S<sub>t</sub></i>) = [ <b>T</b>(<i>S<sub>t</sub></i>) &times; <b>L</b><sub>norm</sub>(<i>S<sub>t</sub></i>) ]<sup>1/2</sup>. The multiplicative geometric mean enforces strict orthogonal gating: zero consequence yields zero pressure (garbage time), and trivial difficulty yields zero pressure (routine play).</li>
        <li><strong>Official Results:</strong> Batting is led by Vaibhav Sooryavanshi (+0.3487), Suryakumar Yadav (+0.2819), and Abhishek Sharma (+0.2703). Bowling is led by Rashid Khan (+0.1756), Jasprit Bumrah (+0.1541), and Sunil Narine (+0.1442).</li>
        <li><strong>Pressure Lift vs. Normal (&Delta;):</strong> Top performers actively elevate execution under high pressure (<i>P</i> &ge; 50) relative to normal states (<i>P</i> &lt; 50). Standout positive lift &Delta; = SVA<sub>P&ge;50</sub> &minus; SVA<sub>P&lt;50</sub> includes Vaibhav (+0.207 runs/ball), Klaasen (+0.077), Rashid (+0.159 runs saved/ball, +146%), Hazlewood (+0.161, +421%), and Mujeeb (+0.153, +265%).</li>
        <li><strong>Flaws &amp; Limitations:</strong> Striker run-outs are attributed to strikers while non-striker run-outs remain team variance; environmental factors (pitch wear, dew) remain unobserved residual variance; 36-cell baseline uses discrete buckets rather than continuous 2D Gaussian surfaces.</li>
        <li><strong>Conclusion:</strong> The framework addresses several limitations of conventional cricket metrics, reduces small-sample instability through shrinkage, and demonstrates robust rank stability (&rho; &gt; 0.997 under super-linear weighting).</li>
    </ul>
</div>

<div class="page-break"></div>

<!-- PAGE 2: EXECUTIVE LEADERBOARDS -->
<h2 class="section-header">Section 1.3 &mdash; Executive Leaderboards</h2>
<p style="margin-bottom: 4pt;">
The official Top 10 rankings represent shrunk reliability performance across all qualified players facing &ge; 50 elevated pressure deliveries (<i>P</i> &ge; 50).
</p>

<h3 class="subsection-header" style="margin-top: 3pt; margin-bottom: 2pt;">Official Top 10 Batting Reliability Rankings (PWSVA)</h3>
__HTML_BAT_TABLE__

<h3 class="subsection-header" style="margin-top: 6pt; margin-bottom: 2pt;">Official Top 10 Bowling Reliability Rankings (SBVA)</h3>
__HTML_BOWL_TABLE__

<div class="page-break"></div>

<!-- PAGE 3: DATASET & DUAL-DIMENSIONAL FRAMEWORK -->
<h2 class="section-header">Section 2 &mdash; Dataset and Scope</h2>

<h3 class="subsection-header">2.1 Scope of Data</h3>
<p>
The evaluation dataset encompasses top-tier men's T20 cricket from January 1, 2022 through May 31, 2026:
</p>
<ul>
    <li><strong>Indian Premier League (IPL):</strong> 365 matches (seasons 2022, 2023, 2024, 2025, and 2026).</li>
    <li><strong>Men's T20 Internationals (T20I):</strong> All official ICC encounters among full-member nations and ICC Men's T20 World Cup fixtures.</li>
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

<h2 class="section-header">Section 3 &mdash; Defining Pressure: The Dual-Dimensional Framework</h2>

<h3 class="subsection-header">3.1 Foundational Philosophy</h3>
<p>
Traditional models conflate difficulty with consequence:
</p>
<ul>
    <li>A batter facing Jasprit Bumrah in the 19th over needing 24 runs faces extreme athletic difficulty <em>and</em> extreme consequence.</li>
    <li>A tailender batting in the 19th over needing 85 runs faces extreme difficulty, but near-zero consequence (the match is already lost).</li>
    <li>An opener playing a maiden over in the 1st innings faces moderate difficulty and moderate consequence.</li>
</ul>
<p>
True pressure exists <strong>if and only if both difficulty and consequence are elevated</strong>. If consequence is zero, difficult execution is merely garbage time. If difficulty is zero (e.g. needing 2 runs off 30 balls), elevated consequence is routine execution.
</p>

<h3 class="subsection-header">3.2 The Master Multiplicative Gating Principle</h3>
<p>
To enforce this orthogonal symmetry, delivery-level pressure (<i>P</i>) is defined as the geometric mean of Task Difficulty (<b>T</b>) and Normalized Match Consequence (<b>L</b><sub>norm</sub>):
</p>
<div class="formula-card">
    <b>P(S<sub>t</sub>)</b> = [ <b>T(S<sub>t</sub>)</b> &times; <b>L<sub>norm</sub>(S<sub>t</sub>)</b> ]<sup>1/2</sup> &isin; [0, 100]
</div>
<p>
Both components are evaluated strictly at <i>t</i><sup>&minus;</sup> (prior to ball release), completely eliminating outcome bias.
</p>

<div class="page-break"></div>

<!-- PAGE 4: VISUAL REFERENCE - TOP 20 RANKINGS -->
<h2 class="section-header">Visual Reference: Top 20 Reliability Rankings</h2>

<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig01_batting_top20_rankings.png" alt="Top 20 Batting Rankings" style="height: 228pt; width: auto;">
    <div class="figure-caption">Figure 1: Official Top 20 Batting Reliability Rankings (PWSVA per Ball with 95% Bootstrap Confidence Intervals).</div>
</div>

<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig02_bowling_top20_rankings.png" alt="Top 20 Bowling Rankings" style="height: 228pt; width: auto;">
    <div class="figure-caption">Figure 2: Official Top 20 Bowling Reliability Rankings (SBVA per Ball with 95% Bootstrap Confidence Intervals).</div>
</div>

<div class="page-break"></div>

<!-- PAGE 5: STEP 4 ENGINE - TASK DIFFICULTY DETAILS -->
<h2 class="section-header">Section 4 &mdash; Calculating Delivery-Level Pressure (Frozen Step 4 Engine)</h2>

<h3 class="subsection-header">4.1 Master Combined Pressure Formula</h3>
<p>
Delivery-level pressure combines Task Difficulty <b>T</b>(<i>S<sub>t</sub></i>) and Normalized Match Consequence <b>L</b><sub>norm</sub>(<i>S<sub>t</sub></i>) via the Geometric Mean:
</p>
<div class="formula-card">
    <b>P(S_t)</b> = [ max(0.0, <b>T(S_t)</b> &times; <b>L_norm(S_t)</b>) ]<sup>1/2</sup><br>
    p_bat = [ max(0.0, t_bat &times; l_norm) ]<sup>1/2</sup><br>
    p_bowl = [ max(0.0, t_bowl &times; l_norm) ]<sup>1/2</sup>
</div>
<p>
Both <b>T</b> and <b>L</b><sub>norm</sub> operate on a standardized [0, 100] scale, ensuring pressure <b>P(S_t)</b> &isin; [0, 100].
</p>

<h3 class="subsection-header">4.2 Task Difficulty Model 1: Batting Innings 1 (T_B1)</h3>
<p>
In the first innings, batting difficulty evaluates Required Acceleration Rate (RAR) and wickets lost stress:
</p>
<div class="formula-card">
    rate_stress1 = (crr1 - 8.10) / 2.50<br>
    W_stress1 = (w_lost1 - 3.50) / 2.00<br>
    z_b1 = 0.60 &times; rate_stress1 + 0.40 &times; W_stress1<br>
    t_b1 = 100.0 / ( 1.0 + exp( -1.2 &times; clip(z_b1, -20.0, 20.0) ) )
</div>
<p>
Parameters: par scoring rate = 8.10 runs/over (&sigma; = 2.50); par wicket loss = 3.50 (&sigma; = 2.00); logistic scaling factor = 1.20.
</p>

<h3 class="subsection-header">4.3 Task Difficulty Model 2: Batting Innings 2 (T_B2)</h3>
<p>
In the second innings chase, batting difficulty integrates Required Run Rate (RRR), wickets down, and their non-linear crisis interaction:
</p>
<div class="formula-card">
    z_rrr2 = (rrr2 - 8.10) / 3.00<br>
    z_w2 = (wt2 - 3.50) / 2.00<br>
    z_inter2 = (rrr2 &times; wt2 - 28.0) / 25.0<br>
    z_b2 = 0.55 &times; z_rrr2 + 0.25 &times; z_w2 + 0.20 &times; z_inter2<br>
    t_b2 = 100.0 / ( 1.0 + exp( -1.0 &times; clip(z_b2, -20.0, 20.0) ) )
</div>
<p>
Parameters: par chase RRR = 8.10 (&sigma; = 3.00); par wickets down = 3.50 (&sigma; = 2.00); interaction center = 28.0 (&sigma; = 25.0); weights = [0.55, 0.25, 0.20]; logistic scaling factor = 1.00.
</p>

<div class="page-break"></div>

<!-- PAGE 6: STEP 4 ENGINE - BOWLING TD & ECDF -->
<h3 class="subsection-header">4.4 Task Difficulty Model 3: Bowling Innings 1 (T_BO1)</h3>
<p>
In the first innings, bowling difficulty evaluates opponent scoring rate, wickets in hand, and fielding restrictions:
</p>
<div class="formula-card">
    crr_stress1 = (crr1 - 8.10) / 2.50<br>
    w_opp_stress1 = ((10.0 - w_lost1) - 6.50) / 2.00<br>
    field_factor1 = 0.50 if phase &isin; ['PP', 'Death'] else 0.00<br>
    z_bo1 = 0.50 &times; crr_stress1 + 0.35 &times; w_opp_stress1 + 0.15 &times; field_factor1<br>
    t_bo1 = 100.0 / ( 1.0 + exp( -1.1 &times; clip(z_bo1, -20.0, 20.0) ) )
</div>
<p>
Parameters: weights = [0.50, 0.35, 0.15]; logistic scaling factor = 1.10. Field restriction factor = 0.50 during Powerplay and Death.
</p>

<h3 class="subsection-header">4.5 Task Difficulty Model 4: Bowling Innings 2 (T_BO2)</h3>
<p>
In the second innings chase, bowling difficulty evaluates defending low required rates against opponent wickets in hand:
</p>
<div class="formula-card">
    rrr_stress2 = (8.10 - rrr2) / 3.00<br>
    w_opp_stress2 = ((10.0 - wt2) - 6.50) / 2.00<br>
    z_bo2 = 0.60 &times; rrr_stress2 + 0.40 &times; w_opp_stress2<br>
    t_bo2 = 100.0 / ( 1.0 + exp( -1.0 &times; clip(z_bo2, -20.0, 20.0) ) )
</div>
<p>
Parameters: weights = [0.60, 0.40]; logistic scaling factor = 1.00.
</p>

<h3 class="subsection-header">4.6 Pre-Delivery Expected Consequence Across Nine Discrete Outcomes</h3>
<p>
Rather than evaluating actual ball outcomes, <i>L</i>(<i>S<sub>t</sub></i>) evaluates the expected absolute win probability swing across all nine discrete possibilities:
</p>
<div class="formula-card">
    L(S<sub>t</sub>) = &sum;<sub>o &isin; &Omega;</sub> P(o) &times; | WP(S<sub>t+1</sub><sup>(o)</sup>) - curr_wp |<br>
    &Omega; = {dot (0), 1 run, 2 runs, 3 runs, 4 runs, 6 runs, wicket, wide, no-ball}
</div>
<p>
Transition states update balls remaining, runs, and wickets before querying the Win Probability model.
</p>

<h3 class="subsection-header">4.7 Innings-Stratified ECDF Normalization (L_norm)</h3>
<p>
To prevent second-innings chase climaxes from dominating first-innings deliveries, raw consequence values are mapped to percentiles via separate empirical cumulative distribution functions:
</p>
<div class="formula-card">
    l_norm = 100.0 &times; ( searchsorted(innings_sorted_L, L) / N_innings )<br>
    N<sub>1</sub> = 96,165 deliveries (Innings 1) &nbsp;|&nbsp; N<sub>2</sub> = 90,615 deliveries (Innings 2)
</div>

<div class="page-break"></div>

<!-- PAGE 7: SITUATIONAL VALUE ADDED & SHRINKAGE -->
<h2 class="section-header">Section 5 &mdash; Measuring Player Reliability: PWSVA and SBVA</h2>

<h3 class="subsection-header">5.1 The 36-Cell Empirical Situational Baseline</h3>
<p>
Every delivery outcome is compared against the empirical expectation of that exact match state, structured as a 36-cell tensor:
</p>
<div class="formula-card">
    Cell(S<sub>t</sub>) = Phase(3) &times; Wicket Bucket(3) &times; Innings(2) &times; Format(2) = 36 discrete states
</div>
<p>
For every cell, baseline runs <i>E</i>[<i>R</i> &mid; Cell] and baseline wicket probability <i>E</i>[<i>W</i> &mid; Cell] are pre-calculated across 186,780 deliveries.
</p>

<h3 class="subsection-header">5.2 Batting: Pressure-Weighted Situational Value Added (PWSVA)</h3>
<p>
For a batter facing delivery <i>i</i>, raw value added contrasts runs scored and wicket preservation against baseline:
</p>
<div class="formula-card">
    SVA<sub>bat, i</sub> = ( R<sub>i</sub> - E[R &mid; Cell<sub>i</sub>] ) - V<sub>W</sub> &times; ( W<sub>i</sub> - E[W &mid; Cell<sub>i</sub>] )<br>
    PWSVA<sub>j</sub> = &sum; ( w<sub>i</sub> &times; SVA<sub>bat, i</sub> ) / &sum; w<sub>i</sub>, &nbsp; where w<sub>i</sub> = ( P<sub>i</sub> / 100 )<sup>1.00</sup>
</div>
<p>
Wicket valuation constant <i>V<sub>W</sub></i> = 4.50 runs represents the empirical value of preserving a wicket.
</p>

<h3 class="subsection-header">5.3 Bowling: Situational Bowling Value Added (SBVA)</h3>
<p>
Bowlers are evaluated on run suppression and breakthrough generation:
</p>
<div class="formula-card">
    SVA<sub>bowl, i</sub> = ( E[R &mid; Cell<sub>i</sub>] - R<sub>conceded, i</sub> ) + V<sub>W</sub> &times; ( W<sub>i</sub> - E[W &mid; Cell<sub>i</sub>] )<br>
    SBVA<sub>j</sub> = &sum; ( w<sub>i</sub> &times; SVA<sub>bowl, i</sub> ) / &sum; w<sub>i</sub>
</div>
<p>
Wides and no-balls are counted in conceded runs and the numerator, but receive zero credit in legal ball counts, penalizing extras without inflating denominators.
</p>

<h3 class="subsection-header">5.4 Individual Pressure Lift (&Delta;): Performance Contrast vs. Normal Situations</h3>
<p>
To satisfy the mandate of comparing high-pressure execution against normal situations, we compute individual <strong>Pressure Lift</strong>:
</p>
<div class="formula-card">
    &Delta;<sub>j</sub> = SVA<sub>j</sub>(P &ge; 50) &minus; SVA<sub>j</sub>(P &lt; 50)
</div>
<p>
While population batting degrades under high pressure (cohort average drops from +0.032 to +0.004 runs/ball), top-ranked players actively elevate execution above their own baseline: Vaibhav Sooryavanshi achieves &Delta; = +0.207 runs/ball (+33%), Phil Salt +0.115 (+44%), and Heinrich Klaasen +0.077 (+24%). Among bowlers, elite performers show dramatic surges in run suppression under strain: Rashid Khan surges +146% (&Delta; = +0.159 runs saved/ball, rising from +0.109 to +0.267), Josh Hazlewood surges +421% (&Delta; = +0.161, rising from +0.038 to +0.198), and Mujeeb Ur Rahman surges +265% (&Delta; = +0.153, rising from +0.058 to +0.212).
</p>

<h2 class="section-header">Section 6 &mdash; Fairness, Eligibility, and Shrinkage Mechanics</h2>

<h3 class="subsection-header">6.1 Kish Effective Sample Size (ESS)</h3>
<p>
To account for variance heterogeneity under non-uniform pressure weights, sample sizes are adjusted via Kish ESS:
</p>
<div class="formula-card">
    ESS<sub>j</sub> = ( &sum; w<sub>i</sub> )<sup>2</sup> / &sum; ( w<sub>i</sub><sup>2</sup> )
</div>

<h3 class="subsection-header">6.2 Empirical Bayes Shrinkage</h3>
<p>
To eliminate small-sample noise, raw scores are shrunk toward cohort priors:
</p>
<div class="formula-card">
    &theta;<sub>j</sub><sup>shrunk</sup> = &lambda;<sub>j</sub> &times; Score<sub>j</sub> + ( 1 - &lambda;<sub>j</sub> ) &times; &mu;<sub>prior</sub><br>
    &lambda;<sub>j</sub> = ESS<sub>j</sub> / ( ESS<sub>j</sub> + K )
</div>
<p>
Shrinkage constants: <i>K</i><sub>bat</sub> = 600.0, <i>K</i><sub>bowl</sub> = 500.0, &mu;<sub>prior</sub> = 0.0000. When ESS = <i>K</i>, retention is exactly 50%.
</p>

<div class="page-break"></div>

<!-- PAGE 8: VISUAL REFERENCE - SCORE VS SAMPLE SIZE -->
<h2 class="section-header">Visual Reference: Score vs. Sample Size Calibration</h2>

<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig03_batting_score_vs_sample_size.png" alt="Batting Score vs Sample Size" style="height: 228pt; width: auto;">
    <div class="figure-caption">Figure 3: Batting Reliability Score vs. Sample Size (Illustrating Empirical Bayes Shrinkage Dynamics).</div>
</div>

<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig04_bowling_score_vs_sample_size.png" alt="Bowling Score vs Sample Size" style="height: 228pt; width: auto;">
    <div class="figure-caption">Figure 4: Bowling Reliability Score vs. Sample Size (Illustrating Empirical Bayes Shrinkage Dynamics).</div>
</div>

<div class="page-break"></div>

<!-- PAGE 9: UNCERTAINTY QUANTIFICATION & SCORE DISTRIBUTIONS -->
<h2 class="section-header">Section 6.3 &mdash; Uncertainty Quantification: Match-Level Block Bootstrap</h2>
<p>
Delivery-level observations within a cricket match are fundamentally non-independent due to persistent pitch wear, weather dynamics, ground dimensions, and bowler spell momentum. Resampling individual deliveries independently would severely underestimate parameter standard errors.
</p>
<p>
To generate statistically valid confidence bounds, we implement a <strong>match-level block bootstrap</strong> with <i>B</i> = 1,000 iterations:
</p>
<ol>
    <li>Let <i>M</i> = 742 denote the unique match identifiers in the evaluation corpus.</li>
    <li>For bootstrap replicate <i>b</i> &isin; {1, &hellip;, 1000}, sample <i>M</i> match clusters with replacement: <i>M</i><sup>(<i>b</i>)</sup> = {<i>m</i><sub>1</sub><sup>*</sup>, &hellip;, <i>m<sub>M</sub></i><sup>*</sup>}.</li>
    <li>Assemble the bootstrap delivery cohort by retrieving all ball events belonging to the sampled matches.</li>
    <li>Recompute weighted situational metrics, Kish ESS, and Empirical Bayes shrinkage for all qualified players.</li>
    <li>Extract the empirical 2.5th and 97.5th percentiles to construct non-parametric 95% confidence intervals.</li>
</ol>

<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig13_population_score_distributions.png" alt="Population Score Distributions" style="height: 200pt; width: auto;">
    <div class="figure-caption">Figure 5: Empirical Bayes Shrunk vs. Raw Score Distributions Across All Qualified Players (N = 297 Batters, N = 292 Bowlers).</div>
</div>

<h3 class="subsection-header">Interpretation of Overlapping Confidence Intervals</h3>
<p>
Bootstrap confidence bounds for adjacent ranks overlap (e.g., Ranks 2&ndash;5 in batting and Ranks 6&ndash;10 in bowling). In sports analytics, point estimates reflect the expected mean, but overlapping intervals signify performance tiers. Small rank differences (&lt; 0.003 runs/ball) represent comparable elite execution under pressure rather than definitive superiority.
</p>

<div class="page-break"></div>

<!-- PAGE 10: EMPIRICAL VALIDATION & CROSS-FORMAT ASSOCIATIONS -->
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
To verify that rankings are robust to super-linear weighting, scores were recalculated with &alpha; = 1.25 (Figure 6):
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

<div class="figure-container" style="margin-top: 4pt; margin-bottom: 2pt;">
    <img src="outputs/step_8_eda/figures/fig07_alpha_sensitivity_slope.png" alt="Alpha Sensitivity Slopegraph" style="height: 190pt; width: auto;">
    <div class="figure-caption">Figure 6: Sensitivity of Player Rankings to Super-Linear Pressure Weighting (&alpha; = 1.00 vs. 1.25 Across Qualified Cohorts).</div>
</div>

<div class="page-break"></div>

<!-- PAGE 11: VISUAL REFERENCE - PHASE HEATMAPS -->
<h2 class="section-header">Visual Reference: Phase Performance Heatmaps</h2>

<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig10_batting_phase_heatmap.png" alt="Batting Phase Heatmap" style="height: 228pt; width: auto;">
    <div class="figure-caption">Figure 7: Batting Phase Performance Heatmap (Powerplay vs. Middle vs. Death Value Added per Ball).</div>
</div>

<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig11_bowling_phase_heatmap.png" alt="Bowling Phase Heatmap" style="height: 228pt; width: auto;">
    <div class="figure-caption">Figure 8: Bowling Phase Performance Heatmap (Powerplay vs. Middle vs. Death Net Runs Saved per Ball).</div>
</div>

<div class="page-break"></div>

<!-- PAGE 12: MARQUEE STARS, LIMITATIONS, KNOCKOUT EXPERIMENT, CONCLUSION -->
<h2 class="section-header">Section 8 &mdash; Placement of Prominent International &amp; Franchise Stars</h2>
<table>
<tr>
    <th>Player Name</th><th>Discipline</th><th>Official Rank</th><th>Shrunk Score</th><th>Raw Score</th><th>Balls</th><th>Kish ESS</th><th>95% Score CI</th>
</tr>
<tr><td>Heinrich Klaasen</td><td>Batting</td><td>#5</td><td><strong>+0.2201</strong></td><td>+0.3357</td><td>1409</td><td>1142.0</td><td>[+0.1238, +0.3072]</td></tr>
<tr><td>Phil Salt</td><td>Batting</td><td>#6</td><td><strong>+0.1954</strong></td><td>+0.2813</td><td>1591</td><td>1364.7</td><td>[+0.0633, +0.3033]</td></tr>
<tr><td>Travis Head</td><td>Batting</td><td>#8</td><td><strong>+0.1625</strong></td><td>+0.2611</td><td>1096</td><td>988.6</td><td>[+0.0017, +0.3203]</td></tr>
<tr><td>Shreyas Iyer</td><td>Batting</td><td>#14</td><td><strong>+0.1350</strong></td><td>+0.1887</td><td>1751</td><td>1507.1</td><td>[+0.0085, +0.2366]</td></tr>
<tr><td>Jos Buttler</td><td>Batting</td><td>#17</td><td><strong>+0.1306</strong></td><td>+0.1642</td><td>2675</td><td>2330.2</td><td>[+0.0366, +0.2187]</td></tr>
<tr><td>Mitchell Marsh</td><td>Batting</td><td>#19</td><td><strong>+0.1272</strong></td><td>+0.1796</td><td>1656</td><td>1456.7</td><td>[+0.0069, +0.2471]</td></tr>
<tr><td>Virat Kohli</td><td>Batting</td><td>#34</td><td><strong>+0.0850</strong></td><td>+0.1081</td><td>2445</td><td>2201.2</td><td>[+0.0005, +0.1547]</td></tr>
<tr><td>Rohit Sharma</td><td>Batting</td><td>#168</td><td><strong>-0.0164</strong></td><td>-0.0231</td><td>1561</td><td>1451.1</td><td>[-0.1574, +0.0988]</td></tr>
<tr><td>Rashid Khan</td><td>Bowling</td><td>#1</td><td><strong>+0.1756</strong></td><td>+0.2147</td><td>2648</td><td>2245.9</td><td>[+0.0810, +0.2784]</td></tr>
<tr><td>Jasprit Bumrah</td><td>Bowling</td><td>#2</td><td><strong>+0.1541</strong></td><td>+0.2103</td><td>1606</td><td>1369.7</td><td>[+0.0237, +0.2784]</td></tr>
<tr><td>Sunil Narine</td><td>Bowling</td><td>#3</td><td><strong>+0.1442</strong></td><td>+0.2020</td><td>1464</td><td>1246.3</td><td>[+0.0555, +0.2334]</td></tr>
<tr><td>Josh Hazlewood</td><td>Bowling</td><td>#4</td><td><strong>+0.1330</strong></td><td>+0.1904</td><td>1368</td><td>1159.5</td><td>[+0.0021, +0.2830]</td></tr>
<tr><td>Mohammed Shami</td><td>Bowling</td><td>#13</td><td><strong>+0.0989</strong></td><td>+0.1438</td><td>1228</td><td>1100.8</td><td>[-0.0629, +0.2621]</td></tr>
<tr><td>Trent Boult</td><td>Bowling</td><td>#16</td><td><strong>+0.0922</strong></td><td>+0.1272</td><td>1501</td><td>1313.6</td><td>[-0.0131, +0.2146]</td></tr>
<tr><td>Axar Patel</td><td>Bowling</td><td>#66</td><td><strong>+0.0195</strong></td><td>+0.0239</td><td>2604</td><td>2218.5</td><td>[-0.0665, +0.1117]</td></tr>
</table>

<h2 class="section-header">Section 9 &mdash; Limitations and Future Enhancements</h2>
<div style="margin-top: 1pt; margin-bottom: 2pt;">
    <p style="margin-bottom: 1.5pt;"><strong>1. Striker Run-Out Attribution:</strong> Striker run-outs are attributed to the striker (<i>W</i><sub>striker</sub> = 1); non-striker run-outs are attributed to team match state.</p>
    <p style="margin-bottom: 1.5pt;"><strong>2. Residual Environmental Variance:</strong> Pitch wear, dew, and ground dimensions are unobserved residual factors; delivery clustering is captured via match-level block bootstrap.</p>
    <p style="margin-bottom: 1.5pt;"><strong>3. Discrete Empirical Baseline:</strong> The 36-cell tensor groups overs and wickets discretely; future iterations will adopt continuous 2D Gaussian processes.</p>
</div>

<h2 class="section-header">Section 10 &mdash; Experimental Sensitivity: Tournament Knockout Leverage</h2>
<p style="margin-bottom: 1.5pt;">
To test whether tournament stakes warrant super-weighting, an experiment applied multipliers (1.10&times; to 1.25&times;) to delivery pressure (<i>P</i>) across 19 IPL playoff matches (4,445 deliveries) with dynamic Kish ESS and Empirical Bayes re-shrinkage.
</p>
<ul style="margin-top: 1pt; margin-bottom: 2pt;">
    <li><strong>Key Results:</strong> Bowlers in the top tier showed 100% retention (Top 4 invariant: Rashid #1, Bumrah #2, Narine #3, Hazlewood #4; Varun surged from official #17 into #5 under playoff leverage, moving Hasaranga to #6). Batters showed 90% retention (Top 7 invariant; Rajat Patidar rose from rank 11 to 8 on 186 playoff balls; Travis Head slipped from rank 8 to 10).</li>
    <li><strong>Conclusion:</strong> The knockout bonus was <strong>rejected</strong> from official rankings due to small-sample volatility (e.g., Mitchell Starc +17 ranks on 42 balls), structural bias against players on non-qualifying teams (71% with zero playoff balls), and redundant double-counting since win-probability swing already prices late-game leverage.</li>
</ul>

<h2 class="section-header">Section 11 &mdash; Conclusion</h2>
<p style="margin-bottom: 2pt;">
The SupeRR Selector framework establishes an uncompromised, reproducible standard for T20 evaluation. By decomposing pressure into Task Difficulty and Win-Probability Consequence, contrasting against an empirical baseline, and applying Empirical Bayes shrinkage, the engine delivers transparent, mathematically robust rankings.
</p>

<div style="margin-top: 4pt; font-size: 7.2pt; color: #718096; text-align: center; border-top: 0.5pt solid #e2e8f0; padding-top: 2pt;">
    Official Methodology Report &middot; SupeRR Selector 2.0 (Round 1) &middot; Amit N Suthar &middot; November 2026
</div>

</body>
</html>
"""

    pdf_html = raw_html_template.replace("__HTML_BAT_TABLE__", html_bat_table).replace("__HTML_BOWL_TABLE__", html_bowl_table)

    # 6. Render PDF via PyMuPDF Story
    pdf_path = 'outputs/step_10_methodology_report/step_10_methodology_report.pdf'
    raw_pdf_path = 'scratch/raw_test_complete_report.pdf'

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
            "Confidential — Prepared for SupeRR Selector Round 1 · Author: Amit N Suthar",
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
    build_and_verify()
