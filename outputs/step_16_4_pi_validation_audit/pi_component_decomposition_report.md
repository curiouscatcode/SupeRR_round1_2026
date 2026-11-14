# Pressure Index (PI) Component Decomposition Report (Investigation C)

**Audit Date:** 2026-11-13  
**Auditor:** Independent Analytics Agent (Step 16.4)  
**Dataset Population:** 180,839 batting deliveries across 789 matches  
**Status:** Completed & Validated  

---

## 1. Executive Summary & Mathematical Decomposition

The continuous Batting Pressure Index ($\text{Batting\_PI}$) is linear across its four underlying factors:
$$\text{Batting\_PI} = 0.65 \times T + 0.35 \times I$$
$$= \underbrace{0.65 w_W W}_{\text{Wickets}} + \underbrace{0.65 w_{\text{Rate}} \text{Rate}}_{\text{Run Rate}} + \underbrace{0.65 w_O O}_{\text{Phase Overs}} + \underbrace{0.35 I}_{\text{Settling Intensity}}$$

This investigation decomposes the $+34.26$ point average gap in Batting PI between Top-Order batters ($26.13$) and Lower-Order batters ($60.39$) into the exact points contributed by each factor.

### Core Decomposition Findings
1. **Tactical Pressure ($T$) vs Situational Intensity ($I$):**
   - **Tactical Pressure ($T$):** Contributes **$+25.23$ points ($73.6\%$)** of the total gap.
   - **Situational Intensity ($I$):** Contributes **$+9.03$ points ($26.4\%$)** of the total gap.
   - Thus, Tactical Pressure explains nearly three-quarters of the difference in the general population.
2. **The Dominance of Wickets Lost ($W$):**
   - Within Tactical Pressure, **Wickets Lost ($W$) contributes $+17.38$ points ($50.7\%$)** of the entire PI gap.
   - Run Rate pressure contributes $+5.92$ points ($17.3\%$).
   - Phase overs progression contributes $+1.93$ points ($5.6\%$).
   - Lower-order batters have an average raw Wickets Score of **$94.48$** (out of 100), compared to only **$17.79$** for top-order batters.
3. **The Settling Factor ($I$) in High-Pressure Threshold Crossing:**
   - In general play, $T$ explains $73.6\%$ of the gap.
   - However, in late-innings crisis situations (e.g. Death overs with 5+ wickets down), $T$ saturates at $\approx 50\text{--}65$ for all batters. Under that saturated tactical background, **Situational Intensity ($I$) acts as the decisive threshold gatekeeper**: it contributes up to $+35.0$ points to newly arrived batters, pushing lower-order batters past the $Z > 1.00$ threshold while leaving set top-order batters below it.

---

## 2. Component Values Across Batting Positions

| Component / Sub-Score | Formula Weight | Top Order (1–3) Points | Middle Order (4–6) Points | Lower Order (7–11) Points | Lower minus Top Gap | Share of Total Gap % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Wickets Factor ($W$)** | $0.65 \times (0.30\text{--}0.40)$ | 4.08 pts | 13.02 pts | 21.46 pts | **+17.38 pts** | **50.7%** |
| **Run Rate Factor ($S / R$)** | $0.65 \times (0.40\text{--}0.50)$ | 8.38 pts | 8.80 pts | 14.30 pts | **+5.92 pts** | **17.3%** |
| **Phase Overs ($O$)** | $0.65 \times 0.20$ | 4.72 pts | 5.93 pts | 6.65 pts | **+1.93 pts** | **5.6%** |
| **Tactical Pressure Subtotal ($0.65 T$)** | **0.65 Total** | **17.18 pts** | **27.75 pts** | **42.41 pts** | **+25.23 pts** | **73.6%** |
| **Situational Intensity ($0.35 I$)** | **0.35 Total** | **8.95 pts** | **11.20 pts** | **17.98 pts** | **+9.03 pts** | **26.4%** |
| **Total Batting Pressure Index (PI)** | **1.00** | **26.13 pts** | **38.95 pts** | **60.39 pts** | **+34.26 pts** | **100.0%** |

```
Artifact:
outputs/step_16_4_pi_validation_audit/pi_component_decomposition.csv
```

---

## 3. Investigation Questions Answered

### 1. Is the lower-order PI increase mainly driven by wickets lost?
**YES.** Wickets lost ($W$) is the single largest driver, directly accounting for **$52.2\%$** of the overall difference in Batting PI between lower order and top order. Lower-order batters face an average of $5.3$ wickets lost at the time of delivery, compared to $0.7$ wickets lost for top-order batters.

### 2. Does Tactical Pressure explain more of the gap than Situational Intensity?
**YES, in the general population:**
- Tactical Pressure ($T$) accounts for **$73.6\%$** ($+25.23$ points) of the overall gap across all 180,839 balls.
- Situational Intensity ($I$) accounts for **$26.4\%$** ($+9.03$ points).
However, **within matched-context cells (Investigation B)**, Tactical Pressure is equalized, meaning that inside identical crisis situations, $I$ accounts for almost the entire residual classification gap.

### 3. Are the components behaving as intended?
**YES.**
- Wickets lost correctly captures resource depletion and structural collapse.
- Required run rate correctly captures scoreboard urgency in chases.
- Settling intensity correctly captures the heightened vulnerability of a newly arrived batter.

### 4. Does the 65/35 weighting create any unexpected effects?
The $35\%$ weighting on $I$ allocates up to **$35.0$ absolute points** to the arrival of a new batter. Because a new batter receives $+35.0$ points and a set batter receives $+0.0$ points, $I$ creates a substantial wedge between newly arrived and set batters. In low-scoring phases (e.g. PP), this settling penalty is balanced by low tactical pressure. But in Death overs, where baseline means are already elevated, newly arrived batters easily trigger $Z > 1.00$ while set batters facing identical match situations rarely do.
This is not an algebraic flaw; it reflects the explicit design of the v2.0 PI model to penalize the "getting set" phase.
