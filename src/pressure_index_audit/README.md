# Pressure Index Formula Audit Module (Step 9)

This directory contains the independent, adversarial audit suite investigating three structural hypotheses in the SupeRR Selector Pressure Index (PI) engine.

## Audit Hypotheses

1. **Investigation A — Bowler Workload Loophole (`audit_workload.py`):**
   - Investigates whether `B_workload = min(100, (bowler_legal_balls_in_spell_before / 12) * 100)` prematurely saturates at 100% after only 2 continuous overs (12 balls), disproportionately inflating early-spell deliveries and penalizing broken-spell death specialists.
   - Evaluates alternative: `B_workload_innings = min(100, (innings_legal_balls_before / 24) * 100)`.

2. **Investigation B — Phase-Relative Baselines (`audit_phase_relative_pressure.py`):**
   - Investigates whether applying a uniform absolute threshold (`PI > 60.0`) creates structural cross-phase bias due to divergent phase baseline centers (PP Batting PI mean = 35.04 vs. Death = 42.66; PP Bowling PI mean = 50.01 vs. Death = 29.29).
   - Evaluates alternative: Phase-relative top 20% (80th percentile) classification per phase.

3. **Investigation C — Second-Innings Powerplay Scoreboard Pressure (`audit_second_innings_powerplay.py`):**
   - Investigates whether `PI_B2_PP` understates scoreboard pressure on openers chasing 200+ at 0/0 and traps settled batters (`striker_bf >= 10`, `I = 0`) below 60.0 even at $RRR \ge 12.0$.
   - Evaluates alternative weightings and target dominance formulations.

4. **Investigation D — Player Ranking Sensitivity (`audit_ranking_impact.py`):**
   - Re-evaluates player performance and Bayesian reliability scores (BRS and BoRS) across 5 comparative models (Baseline, Innings Workload, Phase-Relative, Alt PP, and Combined Model).
   - Measures Spearman rank correlation ($\rho$), Top 10 overlap, rank movements, and Tier 1 turnover.

5. **Master Suite (`run_audit.py`):**
   - Executes all four audit modules and validates artifact generation.

## Execution

To reproduce the complete audit:
```bash
python src/pressure_index_audit/run_audit.py
```

All outputs are saved to `outputs/pressure_index_audit/`.
