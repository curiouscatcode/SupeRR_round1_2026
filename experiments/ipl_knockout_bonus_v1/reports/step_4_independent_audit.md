# Step 4 — Independent Audit Report: IPL Knockout Bonus Experiment (v1)

**Audit Subject:** IPL Knockout Bonus Experiment (v1) (`experiments/ipl_knockout_bonus_v1/`)  
**Auditor:** Independent Quality & Verification Agent (Google DeepMind Antigravity)  
**Date:** November 15, 2026  
**Status:** Complete — Audited & Certified  
**Governing Standard:** Read-Only Audit Protocol; No Modifications to Official Rankings or Experiment Calculations  

---

## Executive Summary

This independent audit evaluated the completed **IPL Knockout Bonus Experiment (v1)** located in `experiments/ipl_knockout_bonus_v1/`. The audit independently reproduced all calculations, verified the exactness of mathematical formulas and Empirical Bayes shrinkage, evaluated zero-knockout invariance, investigated specific player ranks and reporting anomalies, decomposed score movements for representative players into analytical components, and critically appraised the methodological conclusions drawn in the experiment report.

### Audit Findings At A Glance

| Audit Dimension | Finding / Metric | Audit Verdict |
| :--- | :--- | :---: |
| **1. Numerical Reproduction** | All 297 batters and 292 bowlers across 1.00×, 1.10×, 1.20×, 1.25× reproduced with $\Delta = 0.00\times 10^0$ error | **Verified** |
| **2. Zero-Knockout Invariance** | All 206 zero-KO batters and 210 zero-KO bowlers have exact machine-zero score/ESS shifts ($\Delta = 0.00\times 10^0$) | **Verified** |
| **3. Mathematical Score Decomposition** | Re-weighting effect ($\beta_0 \Delta R$) accounts for $>95\%$ of $\Delta S$; ESS shrinkage effect reconciles to $< 10^{-17}$ | **Verified** |
| **4. Reporting & Display Consistency** | CSV rankings are 100% correct; 3 narrative/display discrepancies identified in `experiment_report.md` | **Verified with qualification** |
| **5. Methodological Interpretations** | Low-sample volatility and tournament bias confirmed; shrinkage and correlation claims qualified | **Verified with qualification** |

---

## 1. Independent Reproduction of Results

The audit independently processed the raw delivery-level parquet datasets (`batting_pressure_deliveries.parquet` and `bowling_pressure_deliveries.parquet`), the 36-cell contextual expectation tensors, the dynamic situation-dependent wicket valuation lookup table, and the 19 audited knockout match IDs across all four weighting regimes:
1. **$1.00\times$ Baseline**
2. **$1.10\times$ Multiplier**
3. **$1.20\times$ Multiplier**
4. **$1.25\times$ Multiplier**

### Reproduction Audit Summary

```
========================================================================================================================
Multiplier Regime    Discipline    Population    Max Shrunk Error    Max Raw Error    Max ESS Error    Max Rank Error
========================================================================================================================
1.00x (Baseline)     Batting       297 players      0.00e+00            0.00e+00         0.00e+00             0
1.00x (Baseline)     Bowling       292 players      0.00e+00            0.00e+00         0.00e+00             0
------------------------------------------------------------------------------------------------------------------------
1.10x Multiplier     Batting       297 players      0.00e+00            0.00e+00         0.00e+00             0
1.10x Multiplier     Bowling       292 players      0.00e+00            0.00e+00         0.00e+00             0
------------------------------------------------------------------------------------------------------------------------
1.20x Multiplier     Batting       297 players      0.00e+00            0.00e+00         0.00e+00             0
1.20x Multiplier     Bowling       292 players      0.00e+00            0.00e+00         0.00e+00             0
------------------------------------------------------------------------------------------------------------------------
1.25x Multiplier     Batting       297 players      0.00e+00            0.00e+00         0.00e+00             0
1.25x Multiplier     Bowling       292 players      0.00e+00            0.00e+00         0.00e+00             0
========================================================================================================================
```

### Verification of Core Calculations:
1. **Adjusted Delivery Weights:** For deliveries in the 19 audited knockout matches, $w_i^{\text{adj}} = (P_i / 50.0) \times M$; for all other deliveries, $w_i^{\text{adj}} = (P_i / 50.0) \times 1.00$. Verified across all 152,789 total deliveries.
2. **Weighted Contributions:**
   - Batting: $V_i = (\text{runs\_off\_bat}_i - \text{exp\_runs}_i) - \lambda_i^{\text{eff}} (\text{dismissed}_i - \text{exp\_dismissal}_i)$.
   - Bowling: $V_i = (\text{exp\_runs}_i - \text{runs\_conceded}_i) + \lambda_i^{\text{eff}} (\text{wicket}_i - \text{exp\_wicket}_i)$ with extras (wides/noballs) charged to the bowler.
3. **Kish ESS Recalculation:** $\text{ESS}_{\text{adj}} = (\sum w_i^{\text{adj}})^2 / \sum (w_i^{\text{adj}})^2$ correctly recomputed for each player under each multiplier.
4. **Empirical Bayes Shrinkage:**
   - Batting: $S_{\text{bat}} = \frac{\text{ESS}}{\text{ESS} + 600.0} \times R_{\text{bat}}$.
   - Bowling: $S_{\text{bowl}} = \frac{\text{ESS}}{\text{ESS} + 500.0} \times R_{\text{bowl}}$.
5. **Zero-Knockout Invariance:**
   - **Batting:** All 206 batters with 0 knockout deliveries experienced **$\Delta S = 0.00\times 10^0$** and **$\Delta \text{ESS} = 0.00\times 10^0$**.
   - **Bowling:** All 210 bowlers with 0 knockout deliveries experienced **$\Delta S = 0.00\times 10^0$** and **$\Delta \text{ESS} = 0.00\times 10^0$**.
   - **Verdict: Verified.**

---

## 2. Investigation of Reporting Inconsistencies

The audit performed a line-by-line reconciliation between the generated CSV ranking files and the narrative claims in `experiment_report.md`.

### 2.1 Focus Player Rank Matrix

```
========================================================================================================================
Player Name         Discipline    Base Rank    1.10x Rank    1.20x Rank    1.25x Rank    Base Score    1.20x Score    1.25x Score
========================================================================================================================
Rajat Patidar       Batting          11            10             8             8         +0.154308     +0.159205      +0.160237
Andre Russell       Batting           9             9             9             9         +0.157881     +0.157881      +0.157881
Travis Head         Batting           8             8            10            11         +0.162485     +0.156806      +0.155373
Reeza Hendricks     Batting          10            11            11            10         +0.156353     +0.156353      +0.156353
========================================================================================================================
```

### 2.2 Detailed Investigation Findings

#### Finding 1: Travis Head vs. Reeza Hendricks Top 10 Displacement at 1.25×
- **Audit Discovery:** In `experiment_report.md` (Executive Summary, Section 2, and Section 7), the narrative stated:
  > *"The batting Top 10 exhibits 90% retention, with only a single borderline change: Rajat Patidar climbs from #11 to #8, displacing Reeza Hendricks (#10 to #11)."*
- **Reconciliation with CSVs:**
  - At **$1.10\times$**: Patidar rises to #10 ($+0.156916$), pushing Hendricks to #11 ($+0.156353$). Head remains at #8 ($+0.159656$). Displaced: Hendricks.
  - At **$1.20\times$**: Patidar rises to #8 ($+0.159205$). Head drops to #10 ($+0.156806$). Hendricks is #11 ($+0.156353$). Displaced: Hendricks.
  - At **$1.25\times$**: Patidar is #8 ($+0.160237$). Russell is #9 ($+0.157881$). **Reeza Hendricks is #10 ($+0.156353$)**, and **Travis Head drops to #11 ($+0.155373$)**!
- **Discrepancy Identification:** At $1.25\times$, the player excluded from the Top 10 is **Travis Head**, NOT Reeza Hendricks. Hendricks is actually *restored* to the Top 10 because Head's playoff penalty at $1.25\times$ reduces Head's score below Hendricks' invariant baseline score.
- **Classification:** **Incorrect Narrative Generalization** in `experiment_report.md` (the table in Section 2 accurately had Head at 11 and Hendricks at 10, but the prose erroneously asserted Hendricks was permanently displaced across all multipliers).

#### Finding 2: The Claim That "Rajat Patidar Overtakes Andre Russell"
- **Audit Discovery:** The previous summary stated:
  > *"Patidar accumulates +0.00490 runs/ball, overtaking Travis Head, Andre Russell, and Reeza Hendricks."*
- **Reconciliation with CSVs:**
  - At Baseline: Patidar was Rank 11 ($+0.154308$); Russell was Rank 9 ($+0.157881$).
  - At $1.20\times$: Patidar is Rank 8 ($+0.159205$); Russell is Rank 9 ($+0.157881$).
  - Pairwise score comparison confirms: **Patidar's score surpassed Russell's score by $+0.001324$ runs/ball**. Patidar is ranked ahead of Russell.
  - **Why did Russell's rank not change?**
    While Patidar jumped ahead of Russell ($11 \to 8$), Travis Head simultaneously plummeted behind Russell ($8 \to 10$). Russell was leapfrogged from below by Patidar ($-1$ relative position) but simultaneously gained a position from Head's drop ($+1$ relative position). The net rank change for Russell was exactly **$0$** ($\text{Rank } 9 \to 9$).
- **Classification:** **Verified with qualification.** The statement that Patidar overtook Russell is pairwise and mathematically true; however, readers could be confused if they observe Russell remaining at Rank 9 without understanding the compensatory effect of Head's demotion.

#### Finding 3: Top 10 Retention Percentages
```
========================================================================================================================
Multiplier    Discipline    Retention %    Top 10 Overlap    Players Exiting Top 10    Players Entering Top 10
========================================================================================================================
1.10x         Batting          90.0%           9 / 10        Reeza Hendricks (#11)     Rajat Patidar (#10)
1.20x         Batting          90.0%           9 / 10        Reeza Hendricks (#11)     Rajat Patidar (#8)
1.25x         Batting          90.0%           9 / 10        Travis Head (#11)         Rajat Patidar (#8)
------------------------------------------------------------------------------------------------------------------------
1.10x         Bowling         100.0%          10 / 10        None                      None
1.20x         Bowling         100.0%          10 / 10        None                      None
1.25x         Bowling         100.0%          10 / 10        None                      None
========================================================================================================================
```
- **Classification:** **Verified.** The numerical percentage ($90\%$ batting, $100\%$ bowling) is mathematically correct across all multipliers, though the composition of the displaced cohort differs at $1.25\times$.

#### Finding 4: Table Display Omission in Bowling Top 12 (Mohsin Khan)
- **Audit Discovery:** In Section 3.1 of `experiment_report.md`, Table 3 displayed the Top 12 bowlers fixed by their Baseline rank order. Rows 11 and 12 were assigned to Mosaddek Hossain and Blessing Muzarabani, showing their $1.20\times$ ranks as 12 and 13. This resulted in an apparent missing rank (#11) in the $1.20\times$ column.
- **Reconciliation with CSVs:**
  - Mohsin Khan rose from Baseline Rank 14 ($+0.097827$) to **Rank 11 ($+0.100679$)** at $1.20\times$ and **Rank 11 ($+0.101339$)** at $1.25\times$.
  - Because Table 3 fixed rows strictly to baseline ranks 1–12, Mohsin Khan was excluded from the display, creating a formatting defect.
- **Classification:** **Formatting / Display Inconsistency.** The underlying CSV `bowling_rankings_1_20.csv` is completely correct.

---

## 3. Mathematical Score Change Decomposition

To explain why player scores change under the $1.20\times$ multiplier, the audit decomposed the net score difference $\Delta S = S_1 - S_0$ into its constituent econometric drivers.

### 3.1 Analytical Framework

The Empirical Bayes shrunk score is defined as:
$$S = \beta \cdot R \quad \text{where} \quad \beta = \frac{\text{ESS}}{\text{ESS} + K}$$

When knockout weights are scaled by $M = 1.20$:
1. The raw score changes from $R_0$ to $R_1$ ($\Delta R = R_1 - R_0$) due to increased knockout delivery weighting.
2. The Kish effective sample size changes from $\text{ESS}_0$ to $\text{ESS}_1$ ($\Delta \text{ESS} = \text{ESS}_1 - \text{ESS}_0$).
3. The shrinkage retention factor changes from $\beta_0$ to $\beta_1$ ($\Delta \beta = \beta_1 - \beta_0$).

The exact algebraic relationship between $\Delta \beta$ and $\Delta \text{ESS}$ is:
$$\Delta \beta = \frac{\text{ESS}_1}{\text{ESS}_1 + K} - \frac{\text{ESS}_0}{\text{ESS}_0 + K} = \frac{K \cdot \Delta \text{ESS}}{(\text{ESS}_1 + K)(\text{ESS}_0 + K)}$$

The total score change reconciles identically via baseline-referenced decomposition:
$$\Delta S = \underbrace{\beta_0 \cdot \Delta R}_{\text{Re-weighting Effect}} + \underbrace{\Delta \beta \cdot R_0}_{\text{Kish ESS / Shrinkage Effect}} + \underbrace{\Delta \beta \cdot \Delta R}_{\text{Interaction Term}}$$

and via path-independent Shapley / Midpoint decomposition:
$$\Delta S = \bar{\beta} \cdot \Delta R + \bar{R} \cdot \Delta \beta \quad \text{where} \quad \bar{\beta} = \frac{\beta_0 + \beta_1}{2}, \quad \bar{R} = \frac{R_0 + R_1}{2}$$

### 3.2 Exact Decomposition Matrix ($1.20\times$)

```
========================================================================================================================
Player Name       Disc.      K    Delta R       Delta ESS     Delta Beta    Reweight Effect  Shrink/ESS Effect  Interaction   Reconciled Sum  Residual
========================================================================================================================
Rajat Patidar     Bat      600   +0.009277      -3.4983       -1.121e-03      +0.005215         -0.000308       -1.040e-05      +0.004897     < 1e-17
Travis Head       Bat      600   -0.008928      -2.0629       -4.911e-04      -0.005556         -0.000128       +4.384e-06      -0.005680     < 1e-17
Ayush Badoni      Bat      600   -0.004749      -0.4734       -1.693e-04      -0.002549         +0.000007       +8.042e-07      -0.002541       0.00
Mitchell Starc    Bowl     500   +0.019295      +0.8811       +3.359e-04      +0.010867         -0.000042       +6.482e-06      +0.010831     < 1e-17
Akash Madhwal     Bowl     500   +0.022506      -0.3286       -2.568e-04      +0.008440         +0.000015       -5.781e-06      +0.008449       0.00
Josh Hazlewood    Bowl     500   +0.004369      +2.3472       +4.256e-04      +0.003052         +0.000081       +1.859e-06      +0.003135     < 1e-17
========================================================================================================================
```

### 3.3 Critical Mathematical Insights From the Decomposition

1. **Re-weighting Dominates Score Shifts ($>95\%$ to $>99\%$):**
   - For all six audited players, the change in raw performance caused by up-weighting knockout deliveries accounts for virtually the entire score shift.
   - For Mitchell Starc, the raw re-weighting effect is $+0.010867$ runs/ball, representing **$100.3\%$** of his net $+0.010831$ score gain.
   - For Rajat Patidar, the raw re-weighting effect is $+0.005215$ runs/ball, representing **$106.5\%$** of his $+0.004897$ gain.
2. **Kish ESS Can Decrease Under Knockout Multipliers:**
   - A counter-intuitive mathematical discovery: for Rajat Patidar, Travis Head, Ayush Badoni, and Akash Madhwal, **Kish ESS actually decreased** ($\Delta \text{ESS} < 0$).
   - *Why?* Kish's effective sample size $\text{ESS} = (\sum w_i)^2 / \sum w_i^2$ is inversely proportional to weight variance ($1 + \text{CV}(w)^2$). Because knockout deliveries already had high baseline pressure $P_i$, applying an additional $1.20\times$ multiplier increased the internal dispersion of the delivery weights, slightly reducing sampling efficiency.
   - This decreased $\beta$ by $\sim 10^{-4}$ to $10^{-3}$, slightly increasing the shrinkage penalty towards zero.
3. **Exact Numerical Reconciliation:**
   - The residual reconciliation error between the sum of the components and the actual $\Delta S$ is strictly $\le 5.2 \times 10^{-18}$, confirming exact mathematical closure.

---

## 4. Methodological Interpretation Audit

The audit evaluated whether the four primary conceptual arguments against the knockout multiplier presented in `experiment_report.md` are justified, separating mathematical findings from subjective domain interpretations.

### 4.1 Claim 1: "The bonus undermines shrinkage."
- **Mathematical Finding:** The Empirical Bayes shrinkage equation $S = \beta \cdot R$ is preserved and strictly applied. The shrinkage parameter $K$ ($600$ for batting, $500$ for bowling) remains constant, and small samples are still mathematically compressed towards zero.
- **Statistical / Econometric Evaluation:**
  Shrinkage exists to prevent noisy, small-sample variance from dominating rankings. When a $1.20\times$ multiplier is applied to a tiny sample (e.g., Starc's 42 balls, Madhwal's 45 balls, Badoni's 7 balls), it gives disproportionate leverage to a narrow window of play. This effectively re-injects sample-size volatility into the leaderboard, subverting the *regularizing intent* of shrinkage.
- **Audit Verdict:** **Verified with qualification.** Mathematically, shrinkage is not undermined or removed; however, methodologically, its stabilizing purpose is degraded by introducing artificial leverage on low-volume data slices.

### 4.2 Claim 2: "The bonus creates structural tournament-selection bias."
- **Mathematical Finding:** Exactly **$69.4\%$ of qualified batters (206/297)** and **$71.9\%$ of qualified bowlers (210/292)** have zero knockout deliveries. For all these players, $\Delta S \equiv 0.00\times 10^0$.
- **Statistical / Econometric Evaluation:**
  Playoff qualification is a collective franchise outcome (10 franchises compete, only 4 qualify). Furthermore, international-only cricketers (e.g., Babar Azam, Mohammad Rizwan, Reeza Hendricks, Mosaddek Hossain) cannot participate in IPL knockouts by definition. Because delivery pressure $P_i \in [0, 100]$ already captures situational difficulty (run chases, wickets in hand, death overs) regardless of tournament stage, adding an arbitrary stage multiplier creates structural privilege for players on winning IPL franchises.
- **Audit Verdict:** **Verified.** This conclusion is mathematically sound, empirically verifiable, and structurally valid.

### 4.3 Claim 3: "High Spearman correlation means the bonus provides little additional value."
- **Mathematical Finding:** Global Spearman rank correlation against baseline is $\rho > 0.9996$ across all 297 batters and 292 bowlers.
- **Audit Nuance (Subgroup Analysis):**
  The audit conducted an independent correlation analysis restricted solely to the knockout-exposed cohort:
  - Batting ($N=91$ with knockout balls): $\rho_{1.10} = 0.999758$, $\rho_{1.20} = 0.999385$, $\rho_{1.25} = 0.999077$.
  - Bowling ($N=82$ with knockout balls): $\rho_{1.10} = 0.999764$, $\rho_{1.20} = 0.999131$, $\rho_{1.25} = 0.998552$.
  Even among players who actually played knockouts, the correlation remains $> 0.9985$.
- **Subjective vs. Mathematical Distinction:**
  Mathematically, the ordering is almost identical. However, in sports analytics, proponents of stage weighting would argue that the feature's purpose is not to rearrange the entire leaderboard, but rather to tune specific boundary selections (e.g., deciding whether Rajat Patidar breaks into the Top 10).
- **Audit Verdict:** **Verified with qualification.** The high correlation proves global macro stability, but dismissing feature value solely based on $\rho$ overlooks targeted boundary adjustments.

### 4.4 Claim 4: "Small knockout samples create disproportionate ranking movements."
- **Mathematical Finding:**
  - Mitchell Starc bowled just 42 balls across 2 playoff matches (5.7% of his 737 career deliveries) and surged **+17 ranking spots** ($203 \to 186$).
  - Akash Madhwal bowled 45 balls across 2 playoff matches and surged **+14 ranking spots** ($131 \to 117$).
  - Ayush Badoni faced just 7 balls in 1 playoff match and plunged **-9 ranking spots** ($182 \to 191$).
  - In contrast, high-exposure players (e.g., Rashid Khan, 174 balls across 8 matches) experienced $\Delta \text{Rank} = 0$.
- **Audit Verdict:** **Verified.** The empirical evidence conclusively proves that players with tiny playoff samples experience the largest rank volatility, which is undesirable in a robust reliability framework.

---

## 5. Formal Discrepancy Register

```
========================================================================================================================
ID        Discrepancy Description                                   Severity     Location                   Classification
========================================================================================================================
DISC-01   Narrative stated Reeza Hendricks is displaced in all      Low          experiment_report.md       Incorrect
          multipliers; at 1.25x, Travis Head is displaced to #11                 (Sec. 2 & Exec Summary)
          and Hendricks is restored to #10.

DISC-02   Claim that Rajat Patidar overtook Andre Russell while     Low          Summary Narrative & Chat   Verified with
          Russell remained at Rank 9 needs explicit explanation                  Transcript                 qualification
          of Travis Head's simultaneous demotion.

DISC-03   Table 3 (Top 12 Bowling) omitted Mohsin Khan (who rose    Medium       experiment_report.md       Incorrect
          to Rank 11 at 1.20x/1.25x) because rows were fixed                     (Section 3.1)
          strictly to baseline ranks 1-12.
========================================================================================================================
```

---

## 6. Final Audit Verdict

| Audit Item | Scope | Status | Notes |
| :--- | :--- | :---: | :--- |
| **Recalculation Reproducibility** | All 4 regimes, 589 players | **Verified** | Machine-precision exact match ($0.00\times 10^0$) |
| **Zero-Knockout Invariance** | 416 zero-KO players | **Verified** | Exactly $0.00\times 10^0$ delta in raw, ESS, and shrunk scores |
| **Score Decomposition** | Starc, Madhwal, Badoni, Patidar, Head, Hazlewood | **Verified** | Exact closed-form reconciliation ($< 10^{-17}$ residual) |
| **Top 10 Retention Figures** | Batting (90%), Bowling (100%) | **Verified** | Retention percentages verified across all regimes |
| **Discrepancy Reporting** | 3 specific documentation issues | **Verified with qualification** | Documented in Section 5 discrepancy register |
| **Methodological Recommendation** | Do not adopt 1.20× into official rankings | **Verified** | Statistically and methodologically sound |

### Audit Recommendation
The experiment's central evaluative recommendation — **DO NOT adopt the $1.20\times$ knockout bonus into official rankings and preserve the frozen Step 7.4 baseline** — is fully endorsed by this independent audit. The official rankings remain certified, frozen, and unmodified.
