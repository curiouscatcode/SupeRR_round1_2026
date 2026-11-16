import re

md_path = 'outputs/step_10_methodology_report/step_10_methodology_report.md'
with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Author
text = text.replace(
    '**Author:** Antigravity Autonomous Analytics & Audit Team',
    '**Author:** Amit N Suthar'
)

# 2. Add TL;DR section
tldr_md = """## Section 1 — Executive Summary

### 1.1 Executive TL;DR — Simple Plain-English Summary

- **a. Our Methodology:**
  - Evaluates 186,780 deliveries across IPL and T20Is (2022–2026) against an empirical 36-cell situational baseline (Phase × Wickets × Target × Format).
  - Isolates performance delivered under acute pressure from low-stakes accumulation.
  - Applies Empirical Bayes shrinkage ($K_{\\text{bat}} = 600, K_{\\text{bowl}} = 500$) based on Kish's Effective Sample Size ($N_{\\text{eff}}$) to eliminate small-sample noise while preserving genuine ratings for high-volume players.

- **b. Our Formula & Its Meaning:**
  - **Pressure ($P$):** $P(S_t) = \\sqrt{T(S_t) \\times L_{\\text{norm}}(S_t)} \\in [0, 100]$. Pressure is the geometric mean of Task Difficulty ($T$, physical/tactical difficulty facing the player) and Normalized Match Consequence ($L_{\\text{norm}}$, expected absolute win-probability swing across 9 discrete outcomes). True pressure exists **if and only if both difficulty and consequence are elevated**; if either is zero, pressure is zero.
  - **Batting (PWSVA):** $\\text{PWSVA}_p^{\\text{shrunk}} = \\frac{N_{\\text{eff}, p}}{N_{\\text{eff}, p} + 600} \\cdot \\bar{v}_{\\text{bat}, p}$. Measures situation-adjusted runs and capped dismissals added above state expectancy, shrunk toward replacement level.
  - **Bowling (SBVA):** $\\text{SBVA}_p^{\\text{shrunk}} = \\frac{N_{\\text{eff}, p}}{N_{\\text{eff}, p} + 500} \\cdot \\bar{v}_{\\text{bowl}, p}$. Measures net runs saved and wickets taken above expectation per legal delivery quota (penalizing extras in the numerator), shrunk toward replacement level.

- **c. Key Results:**
  - **Batting #1:** Vaibhav Sooryavanshi ranks #1 (+0.3487 shrunk, raw +0.7614, ESS = 506.9) via explosive clutch boundary hitting in high-pressure situations, retaining 45.8% under shrinkage.
  - **Batting Volume Masters:** Suryakumar Yadav (#2, +0.2819, 2,638 balls, ESS = 2,287.2) and Abhishek Sharma (#3, +0.2703, 2,195 balls, ESS = 1,923.3) maintain elite positive value added across massive sample sizes.
  - **Bowling #1 & #2:** Rashid Khan (#1, +0.1756 shrunk, 2,648 balls, ESS = 2,245.9) and Jasprit Bumrah (#2, +0.1541 shrunk, 1,606 balls, ESS = 1,369.7) dominate global bowling reliability through elite economy and breakthrough wickets in high-leverage overs.

- **d. Flaws & Limitations:**
  - **Striker Run-Out Attribution:** Striker run-outs are attributed to the striker ($W_{\\text{striker}} = 1$), while non-striker run-outs are attributed to team match state rather than individual batters.
  - **Unmodeled Environmental Variables:** Pitch deterioration across a tournament, evening dew in chase innings, venue altitude, and boundary asymmetries are not explicitly in the state vector.
  - **Discrete Phase Bins:** The 36-cell empirical baseline groups overs into coarse phases (Powerplay, Middle, Death) rather than a continuous 2D surface.

- **e. Conclusion:**
  - Situational pressure gating combined with Empirical Bayes shrinkage resolves traditional cricket metric distortions, establishing transparent, auditable rankings that prioritize high-stakes repeatability over volume padding.

### 1.2 The Challenge of Pressure Evaluation"""

text = text.replace(
    "## Section 1 — Executive Summary\n\n### 1.1 The Challenge of Pressure Evaluation",
    tldr_md
)

# Renumber 1.2 -> 1.3 and 1.3 -> 1.4
text = text.replace(
    "### 1.2 Summary of Findings",
    "### 1.3 Summary of Findings"
)
text = text.replace(
    "### 1.3 Executive Leaderboards",
    "### 1.4 Executive Leaderboards"
)

# 3. Section 9 Points on Separate Lines
sec9_old = """## Section 9 — Limitations and Future Enhancements
1. **Striker Run-Out Attribution:** Striker run-out dismissals are attributed to the striker ($W_{{\\text{{striker}}}} = 1$), while non-striker run-outs are attributed to team match state rather than individual batters.
2. **Residual Environmental Variance:** Factors such as pitch deterioration across a tournament, evening dew in the second innings, venue altitude, and asymmetrical boundary dimensions are not explicitly modeled in the ball-by-ball state space. While the match-level block bootstrap accounts for delivery clustering and match-level sampling variability, unobserved environmental factors remain residual variance.
3. **Discrete Empirical Baseline:** The 36-cell tensor groups overs into coarse phases (Powerplay, Middle, Death) and wickets into three buckets (0–3, 4–6, 7+). Future iterations (SupeRR 3.0) will incorporate continuous 2D Gaussian process surfaces over remaining deliveries and wickets."""

sec9_new = """## Section 9 — Limitations and Future Enhancements

1. **Striker Run-Out Attribution:** Striker run-out dismissals are attributed to the striker ($W_{{\\text{{striker}}}} = 1$), while non-striker run-outs are attributed to team match state rather than individual batters.

2. **Residual Environmental Variance:** Factors such as pitch deterioration across a tournament, evening dew in the second innings, venue altitude, and asymmetrical boundary dimensions are not explicitly modeled in the ball-by-ball state space. While the match-level block bootstrap accounts for delivery clustering and match-level sampling variability, unobserved environmental factors remain residual variance.

3. **Discrete Empirical Baseline:** The 36-cell tensor groups overs into coarse phases (Powerplay, Middle, Death) and wickets into three buckets (0–3, 4–6, 7+). Future iterations (SupeRR 3.0) will incorporate continuous 2D Gaussian process surfaces over remaining deliveries and wickets."""

text = text.replace(sec9_old, sec9_new)

# 4. Footer author update
text = text.replace(
    '*Official Methodology Report · SupeRR Selector 2.0 (Round 1) · Antigravity Autonomous Audit Team · November 2026*',
    '*Official Methodology Report · SupeRR Selector 2.0 (Round 1) · Amit N Suthar · November 2026*'
)

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Markdown updated successfully. New file size:", len(text))
