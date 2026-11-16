# Step 10.4 — Pressure Methodology Formula Traceability Matrix

**Project:** SupeRR Selector 2.0 — Round 1  
**Deliverable:** Formula Traceability Matrix  
**Date:** November 16, 2026  
**Status:** FULLY TRACED & VERIFIED

---

## 1. Overview & Purpose

This document provides a line-by-line mathematical traceability mapping between:
1. **The Frozen Step 4 Python Codebase** (`src/step_4_pressure_pipeline/`)
2. **The Approved Step 3.2 Methodology** (`outputs/step_3_formal_pressure_methodology/step_3_formal_pressure_methodology.md`)
3. **The Final Step 10 Methodology Report** (`outputs/step_10_methodology_report/step_10_methodology_report.md` and `.pdf`, Sections 3–4, Pages 5–6)

---

## 2. Master Pressure Formula

### 2.1 Mathematical Formulation
$$P(S_t) = \sqrt{T(S_t) \times L_{\text{norm}}(S_t)} \in [0, 100]$$

Where:
- $T(S_t) \in [0, 100]$: Pre-delivery Task Difficulty evaluating the acute physical, tactical, and scoring/defending difficulty facing the player.
- $L_{\text{norm}}(S_t) \in [0, 100]$: Innings-stratified empirical percentile of expected absolute win probability swing across all 9 discrete legal/illegal ball outcomes.

### 2.2 Traceability Mapping
| System Component | Code Implementation | Script & Line Numbers | Report Location |
| :--- | :--- | :--- | :--- |
| **Batting Pressure** | `p_bat = np.sqrt(np.maximum(0.0, t_bat * l_norm))` | `src/step_4_pressure_pipeline/06_generate_pressure_dataset.py`<br>Line 28 | Section 3.2 (p. 5) |
| **Bowling Pressure** | `p_bowl = np.sqrt(np.maximum(0.0, t_bowl * l_norm))` | `src/step_4_pressure_pipeline/06_generate_pressure_dataset.py`<br>Line 29 | Section 3.2 (p. 5) |
| **Range Bounding** | `np.clip(p_bat, 0.0, 100.0)`<br>`np.clip(p_bowl, 0.0, 100.0)` | `src/step_4_pressure_pipeline/06_generate_pressure_dataset.py`<br>Lines 32–33 | Section 3.2 (p. 5) |

---

## 3. Task Difficulty Models ($T$)

### 3.1 Batting Innings 1 Task Difficulty ($T_{B1}$)
In Innings 1, batters maximize total score against baseline venue par ($V_{\text{par}}$, global default $176.68$).

#### Formulas
1. **Required Acceleration Rate (RAR):**
   $$\text{RAR} = \max\left(0, \frac{V_{\text{par}} - \text{Score}_t}{(120 - B_{\text{elapsed}})/6}\right)$$
2. **Rate Stress:**
   $$\Delta R_{B1} = \frac{\text{RAR} - R_{\text{par}}}{R_{\text{par}}}, \quad \text{where } R_{\text{par}} = \frac{V_{\text{par}}}{20}$$
3. **Empirical Wicket Curve Stress:**
   $$W_{\text{stress}} = \begin{cases} 0.0 & \text{if } B_{\text{elapsed}} = 0 \\ \frac{W_t - \mu_W(L_t)}{\sigma_W(L_t)} & \text{if } B_{\text{elapsed}} > 0 \end{cases}$$
4. **Standardized Composite & Logistic Scaling:**
   $$Z_{B1} = 0.60 \cdot \Delta R_{B1} + 0.40 \cdot W_{\text{stress}}$$
   $$T_{B1} = \frac{100}{1 + \exp(-1.2 \cdot Z_{B1})} \in [0, 100]$$

#### Code Traceability
- **Script:** `src/step_4_pressure_pipeline/05_task_difficulty_models.py`
- **Lines 53–72:**
  - `brem1 = np.maximum(1.0, 120.0 - lballs1)`
  - `rar1 = np.maximum(0.0, (vpar1 - score1) / (brem1 / 6.0))`
  - `rate_stress1 = (rar1 - rpar1) / rpar1`
  - `w_stress1 = np.where(lballs1 == 0, 0.0, (wt1 - mu1) / sig1)`
  - `z_b1 = 0.60 * rate_stress1 + 0.40 * w_stress1`
  - `t_b1 = 100.0 / (1.0 + np.exp(-1.2 * np.clip(z_b1, -20.0, 20.0)))`
- **Report Location:** Section 4.1.1 (p. 5)

---

### 3.2 Batting Innings 2 Task Difficulty ($T_{B2}$)
In Innings 2, task difficulty is governed by required run rate, remaining wickets, and their interaction.

#### Formulas
1. **Required Run Rate (RRR):**
   $$\text{RRR} = \text{clip}\left(\frac{R_{\text{req}}}{B_{\text{rem}}} \times 6, 0.0, 36.0\right)$$
2. **Standardized Predictors:**
   $$Z_{\text{RRR}} = \frac{\text{RRR} - 8.10}{3.00}, \quad Z_W = \frac{W_t - 3.50}{2.00}$$
3. **Centered Non-Linear Interaction:**
   $$Z_{\text{inter}} = \frac{\text{RRR} \cdot W_t - 28.0}{25.0}$$
4. **Standardized Composite & Logistic Scaling:**
   $$Z_{B2} = 0.55 \cdot Z_{\text{RRR}} + 0.25 \cdot Z_W + 0.20 \cdot Z_{\text{inter}}$$
   $$T_{B2} = \frac{100}{1 + \exp(-1.0 \cdot Z_{B2})} \in [0, 100]$$

#### Code Traceability
- **Script:** `src/step_4_pressure_pipeline/05_task_difficulty_models.py`
- **Lines 75–88:**
  - `rrr2 = np.clip((req2 / brem2) * 6.0, 0.0, 36.0)`
  - `z_rrr2 = (rrr2 - 8.10) / 3.00`
  - `z_w2 = (wt2 - 3.50) / 2.00`
  - `z_inter2 = (rrr2 * wt2 - 28.0) / 25.0`
  - `z_b2 = 0.55 * z_rrr2 + 0.25 * z_w2 + 0.20 * z_inter2`
  - `t_b2 = 100.0 / (1.0 + np.exp(-1.0 * np.clip(z_b2, -20.0, 20.0)))`
- **Report Location:** Section 4.1.2 (p. 5)

---

### 3.3 Bowling Innings 1 Task Difficulty ($T_{BO1}$)
In Innings 1, bowling difficulty reflects run suppression against venue par, opponent batting capital, and fielding restrictions.

#### Formulas
1. **Conceded Current Run Rate (CRR):**
   $$\text{CRR} = \begin{cases} R_{\text{par}} & \text{if } B_{\text{elapsed}} = 0 \\ \frac{\text{Score}_t}{\max(1, B_{\text{elapsed}})} \times 6 & \text{if } B_{\text{elapsed}} > 0 \end{cases}$$
2. **CRR Stress:**
   $$\Delta \text{CRR} = \frac{\text{CRR} - R_{\text{par}}}{R_{\text{par}}}$$
3. **Opponent Wicket Abundance:**
   $$W_{\text{opp}} = \begin{cases} 0.0 & \text{if } B_{\text{elapsed}} = 0 \\ \frac{\mu_W(L_t) - W_t}{\sigma_W(L_t)} & \text{if } B_{\text{elapsed}} > 0 \end{cases}$$
4. **Phase Field Restriction Factor:**
   $$\text{FieldFactor} = \begin{cases} 0.50 & \text{if Phase} \in \{\text{Powerplay, Death}\} \\ 0.00 & \text{if Phase} \in \{\text{Middle}\} \end{cases}$$
5. **Standardized Composite & Logistic Scaling:**
   $$Z_{BO1} = 0.50 \cdot \Delta \text{CRR} + 0.35 \cdot W_{\text{opp}} + 0.15 \cdot \text{FieldFactor}$$
   $$T_{BO1} = \frac{100}{1 + \exp(-1.1 \cdot Z_{BO1})} \in [0, 100]$$

#### Code Traceability
- **Script:** `src/step_4_pressure_pipeline/05_task_difficulty_models.py`
- **Lines 91–105:**
  - `crr1 = np.where(lballs1 == 0, rpar1, (score1 / np.maximum(1.0, lballs1)) * 6.0)`
  - `crr_stress1 = (crr1 - rpar1) / rpar1`
  - `w_opp_stress1 = np.where(lballs1 == 0, 0.0, (mu1 - wt1) / sig1)`
  - `field_factor1 = np.where(np.isin(phase1, ['PP', 'Death']), 0.50, 0.00)`
  - `z_bo1 = 0.50 * crr_stress1 + 0.35 * w_opp_stress1 + 0.15 * field_factor1`
  - `t_bo1 = 100.0 / (1.0 + np.exp(-1.1 * np.clip(z_bo1, -20.0, 20.0)))`
- **Report Location:** Section 4.1.3 (p. 6)

---

### 3.4 Bowling Innings 2 Task Difficulty ($T_{BO2}$)
In Innings 2, bowling difficulty reflects defending a target when the opponent is comfortable.

#### Formulas
1. **Chase Comfort Defense Stress:**
   $$\text{RRR}_{\text{stress}} = \frac{8.10 - \text{RRR}}{3.00}$$
2. **Opponent Wicket Abundance:**
   $$W_{\text{opp}} = \frac{\mu_W(L_t) - W_t}{\sigma_W(L_t)}$$
3. **Standardized Composite & Logistic Scaling:**
   $$Z_{BO2} = 0.60 \cdot \text{RRR}_{\text{stress}} + 0.40 \cdot W_{\text{opp}}$$
   $$T_{BO2} = \frac{100}{1 + \exp(-1.0 \cdot Z_{BO2})} \in [0, 100]$$

#### Code Traceability
- **Script:** `src/step_4_pressure_pipeline/05_task_difficulty_models.py`
- **Lines 108–117:**
  - `rrr_stress2 = (8.10 - rrr2) / 3.00`
  - `w_opp_stress2 = (mu2 - wt2) / sig2`
  - `z_bo2 = 0.60 * rrr_stress2 + 0.40 * w_opp_stress2`
  - `t_bo2 = 100.0 / (1.0 + np.exp(-1.0 * np.clip(z_bo2, -20.0, 20.0)))`
- **Report Location:** Section 4.1.4 (p. 6)

---

## 4. Match Consequence ($L$) & ECDF Normalization

### 4.1 Expected Match Consequence Formula
Pre-delivery expected consequence $L(S_t)$ evaluates the expected absolute swing in Win Probability across 9 mutually exclusive delivery outcomes:
$$L(S_t) = \sum_{o \in \mathcal{O}} P(o \mid S_t) \cdot \big| \text{WP}(S_{t+1}(o)) - \text{WP}(S_t) \big|$$

Where:
- $\mathcal{O} = \{\text{dot, 1, 2, 3, 4, 6, wicket, wide, no-ball}\}$ (9 outcomes).
- $P(o \mid S_t)$ are empirical transition probabilities stratified by phase $\times$ innings.
- $\text{WP}(S)$ is the pre-delivery win probability predicted by the validated logistic models with Markov terminal engine.

#### Code Traceability
- **Script:** `src/step_4_pressure_pipeline/04_consequence_and_ecdf.py`
- **Lines 20–28:** Outcome configuration:
  ```python
  OUTCOMES_CONFIG = [
      ('dot',     0, 0, 1),
      ('one',     1, 0, 1),
      ('two',     2, 0, 1),
      ('three',   3, 0, 1),
      ('four',    4, 0, 1),
      ('six',     6, 0, 1),
      ('wicket',  0, 1, 1),
      ('wide',    1, 0, 0),
      ('no_ball', 1, 0, 0)
  ]
  ```
- **Lines 105–185:** Vectorized outcome loops and `cum_swing += p_o * np.abs(wp_next - curr_wp)`.
- **Report Location:** Section 4.2.1 (p. 6)

---

### 4.2 Innings-Stratified ECDF Normalization
Because second-innings deliveries experience larger absolute win probability swings (due to definite finish lines and known targets), pooling both innings compresses first-innings pressure percentiles. To preserve orthogonal symmetry, ECDF normalization is stratified by innings:

$$L_{\text{norm}}(S_t) = \frac{\text{Rank}_{\text{left}} + \text{Rank}_{\text{right}}}{2 \cdot N_i} \times 100 \in [0, 100]$$

Where:
- Innings 1 calibration sample: $N_1 = 96,165$ deliveries.
- Innings 2 calibration sample: $N_2 = 90,615$ deliveries.
- Total cohort: $N = 186,780$ deliveries.

#### Code Traceability
- **Script:** `src/step_4_pressure_pipeline/04_consequence_and_ecdf.py`
- **Lines 190–215:**
  - `l1_sorted = np.sort(l1_vals); n1 = len(l1_sorted)`
  - `r_left1 = np.searchsorted(l1_sorted, l1_vals, side='left')`
  - `r_right1 = np.searchsorted(l1_sorted, l1_vals, side='right')`
  - `l_norm_arr[inn1_mask] = ((r_left1 + r_right1) / (2.0 * n1)) * 100.0`
  - Equivalent mid-rank sorting on `inn2_mask`.
- **Report Location:** Section 4.2.2 (p. 6)

---

## 5. Summary Traceability Matrix

| Math Term in Report | Report Section & Page | Code Variable | Code File & Line Range | Audit Verification |
| :--- | :--- | :--- | :--- | :--- |
| $P(S_t) = \sqrt{T \times L_{\text{norm}}}$ | Section 3.2, p. 5 | `p_bat`, `p_bowl` | `06_generate_pressure_dataset.py`: 28–29 | **EXACT MATCH** |
| $Z_{B1} = 0.60 \Delta R_{B1} + 0.40 W_{\text{stress}}$ | Section 4.1.1, p. 5 | `z_b1` | `05_task_difficulty_models.py`: 70 | **EXACT MATCH** |
| $T_{B1} = 100 / (1 + e^{-1.2 Z_{B1}})$ | Section 4.1.1, p. 5 | `t_b1` | `05_task_difficulty_models.py`: 71 | **EXACT MATCH** |
| $Z_{B2} = 0.55 Z_{\text{RRR}} + 0.25 Z_W + 0.20 Z_{\text{inter}}$ | Section 4.1.2, p. 5 | `z_b2` | `05_task_difficulty_models.py`: 86 | **EXACT MATCH** |
| $T_{B2} = 100 / (1 + e^{-1.0 Z_{B2}})$ | Section 4.1.2, p. 5 | `t_b2` | `05_task_difficulty_models.py`: 87 | **EXACT MATCH** |
| $Z_{BO1} = 0.50 \Delta \text{CRR} + 0.35 W_{\text{opp}} + 0.15 \text{FF}$ | Section 4.1.3, p. 6 | `z_bo1` | `05_task_difficulty_models.py`: 103 | **EXACT MATCH** |
| $T_{BO1} = 100 / (1 + e^{-1.1 Z_{BO1}})$ | Section 4.1.3, p. 6 | `t_bo1` | `05_task_difficulty_models.py`: 104 | **EXACT MATCH** |
| $Z_{BO2} = 0.60 \text{RRR}_{\text{stress}} + 0.40 W_{\text{opp}}$ | Section 4.1.4, p. 6 | `z_bo2` | `05_task_difficulty_models.py`: 115 | **EXACT MATCH** |
| $T_{BO2} = 100 / (1 + e^{-1.0 Z_{BO2}})$ | Section 4.1.4, p. 6 | `t_bo2` | `05_task_difficulty_models.py`: 116 | **EXACT MATCH** |
| $L(S_t) = \sum P(o) \|\Delta \text{WP}\|$ | Section 4.2.1, p. 6 | `raw_L` | `04_consequence_and_ecdf.py`: 93–185 | **EXACT MATCH** |
| $L_{\text{norm}}$ ($N_1 = 96,165, N_2 = 90,615$) | Section 4.2.2, p. 6 | `l_norm_arr` | `04_consequence_and_ecdf.py`: 190–215 | **EXACT MATCH** |
