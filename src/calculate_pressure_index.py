"""
Pressure Index (PI) Calculation Engine for SupeRR Selector 2.0
==============================================================

This script implements the complete 12-formula Pressure Index (PI) framework
for all 188,330 deliveries in the validated 20-over dataset.

Core Framework:
- Every index follows: PI = (0.65 * T) + (0.35 * I)
- Match Phases: PP (Overs 1-6), Middle (Overs 7-15), Death (Overs 16-20)
- Individual Pressure (I):
    * Batter: B = max(0, min(100, ((10 - striker_balls_faced_before) / 10) * 100))
    * Bowler: B_workload = min(100, (bowler_legal_balls_in_spell_before / 12) * 100)
              S_settling = max(0, min(100, ((10 - striker_balls_faced_before) / 10) * 100))
              I_bowler = (0.50 * B_workload) + (0.50 * S_settling)

12 Specific Formulas:
1.  PI_B1_PP:   Inn 1, PP,     Batters: T = 0.40*W + 0.40*S + 0.20*O | I = B
2.  PI_B1_MO:   Inn 1, Middle, Batters: T = 0.40*W + 0.40*S + 0.20*O | I = B
3.  PI_B1_DO:   Inn 1, Death,  Batters: T = 0.40*W + 0.40*S + 0.20*O | I = B
4.  PI_BO1_PP:  Inn 1, PP,     Bowlers: T = 0.40*W + 0.40*S + 0.20*O | I = Bowler_I
5.  PI_BO1_MO:  Inn 1, Middle, Bowlers: T = 0.40*W + 0.40*S + 0.20*O | I = Bowler_I
6.  PI_BO1_DO:  Inn 1, Death,  Bowlers: T = 0.40*W + 0.40*S + 0.20*O | I = Bowler_I
7.  PI_B2_PP:   Inn 2, PP,     Batters: T = 0.50*R + 0.30*W + 0.20*O | I = B
8.  PI_B2_MO:   Inn 2, Middle, Batters: T = 0.50*R + 0.30*W + 0.20*O | I = B
9.  PI_B2_DO:   Inn 2, Death,  Batters: T = 0.50*R + 0.30*W + 0.20*O | I = B
10. PI_BO2_PP:  Inn 2, PP,     Bowlers: T = 0.40*S + 0.40*W + 0.20*O | I = Bowler_I
11. PI_BO2_MO:  Inn 2, Middle, Bowlers: T = 0.40*S + 0.40*W + 0.20*O | I = Bowler_I
12. PI_BO2_DO:  Inn 2, Death,  Bowlers: T = 0.50*S + 0.30*W + 0.20*O | I = Bowler_I

Output:
- data/processed/delivery_pressure_index.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd


def assign_pressure_level(series: pd.Series) -> pd.Series:
    """
    Categorize continuous Pressure Index (0-100) into 5 qualitative tiers:
      - 0  to 20  : Very Low
      - 21 to 40  : Low
      - 41 to 60  : Moderate
      - 61 to 80  : High
      - 81 to 100 : Very High
    """
    bins = [-np.inf, 20.0, 40.0, 60.0, 80.0, np.inf]
    labels = ['Very Low', 'Low', 'Moderate', 'High', 'Very High']
    return pd.cut(series, bins=bins, labels=labels, right=True)


def calculate_pressure_index(input_path: Path, output_path: Path) -> pd.DataFrame:
    print(f"Loading reconstructed match state data from {input_path}...")
    df = pd.read_csv(input_path)
    total_rows = len(df)
    print(f"Loaded {total_rows:,} deliveries with {len(df.columns)} columns.")

    # ---------------------------------------------------------
    # 1. Base Variables and Individual Pressure
    # ---------------------------------------------------------
    print("Calculating Individual Pressure components...")
    
    # Batter Individual Pressure (B)
    # B = max(0, min(100, ((10 - striker_balls_faced_before) / 10) * 100))
    striker_bf = df['striker_balls_faced_before'].to_numpy(dtype=float)
    b_batter = np.clip(((10.0 - striker_bf) / 10.0) * 100.0, 0.0, 100.0)
    i_batter = b_batter

    # Bowler Individual Pressure
    # B_workload = min(100, (bowler_legal_balls_in_spell_before / 12) * 100)
    # S_settling = max(0, min(100, ((10 - striker_balls_faced_before) / 10) * 100))
    # I_bowler = (0.50 * B_workload) + (0.50 * S_settling)
    bowler_spell_balls = df['bowler_legal_balls_in_spell_before'].to_numpy(dtype=float)
    b_workload = np.clip((bowler_spell_balls / 12.0) * 100.0, 0.0, 100.0)
    s_settling = b_batter
    i_bowler = (0.50 * b_workload) + (0.50 * s_settling)

    # Context arrays
    innings = df['innings'].to_numpy()
    phase = df['phase'].to_numpy()
    w_before = df['wickets_before'].to_numpy(dtype=float)
    crr = df['current_run_rate'].to_numpy(dtype=float)
    phase_overs = df['phase_overs_completed'].to_numpy(dtype=float)

    # Required Run Rate (RRR) for Innings 2
    # RRR = (runs_required / balls_remaining) * 6
    runs_req = df['runs_required'].to_numpy(dtype=float)
    balls_rem = df['balls_remaining'].to_numpy(dtype=float)
    
    # Safe RRR computation avoiding division by zero
    rrr = np.full(total_rows, np.nan, dtype=float)
    inn2_mask = (innings == 2)
    valid_inn2 = inn2_mask & (balls_rem > 0)
    rrr[valid_inn2] = (runs_req[valid_inn2] / balls_rem[valid_inn2]) * 6.0

    # ---------------------------------------------------------
    # 2. Formula masks
    # ---------------------------------------------------------
    m_b1_pp  = (innings == 1) & (phase == 'PP')
    m_b1_mo  = (innings == 1) & (phase == 'Middle')
    m_b1_do  = (innings == 1) & (phase == 'Death')

    m_b2_pp  = (innings == 2) & (phase == 'PP')
    m_b2_mo  = (innings == 2) & (phase == 'Middle')
    m_b2_do  = (innings == 2) & (phase == 'Death')

    print(f"Mask counts:\n"
          f"  Inn 1 PP: {m_b1_pp.sum():,}, MO: {m_b1_mo.sum():,}, DO: {m_b1_do.sum():,}\n"
          f"  Inn 2 PP: {m_b2_pp.sum():,}, MO: {m_b2_mo.sum():,}, DO: {m_b2_do.sum():,}")

    # Initialize all 12 formula columns with NaN
    pi_b1_pp   = np.full(total_rows, np.nan, dtype=float)
    pi_b1_mo   = np.full(total_rows, np.nan, dtype=float)
    pi_b1_do   = np.full(total_rows, np.nan, dtype=float)

    pi_bo1_pp  = np.full(total_rows, np.nan, dtype=float)
    pi_bo1_mo  = np.full(total_rows, np.nan, dtype=float)
    pi_bo1_do  = np.full(total_rows, np.nan, dtype=float)

    pi_b2_pp   = np.full(total_rows, np.nan, dtype=float)
    pi_b2_mo   = np.full(total_rows, np.nan, dtype=float)
    pi_b2_do   = np.full(total_rows, np.nan, dtype=float)

    pi_bo2_pp  = np.full(total_rows, np.nan, dtype=float)
    pi_bo2_mo  = np.full(total_rows, np.nan, dtype=float)
    pi_bo2_do  = np.full(total_rows, np.nan, dtype=float)

    # ---------------------------------------------------------
    # 3. PART B — FIRST-INNINGS BATTERS
    # ---------------------------------------------------------
    print("Computing First-Innings Batters PI...")
    # 1. PI_B1_PP
    # W = min(100, (wickets_before / 6) * 100)
    # S = max(0, min(100, ((8 - current_run_rate) / 8) * 100))
    # O = (phase_overs_completed / 6) * 100
    # T = (0.40 * W) + (0.40 * S) + (0.20 * O)
    # I = B
    # PI_B1_PP = (0.65 * T) + (0.35 * I)
    w_b1_pp = np.clip((w_before[m_b1_pp] / 6.0) * 100.0, 0.0, 100.0)
    s_b1_pp = np.clip(((8.0 - crr[m_b1_pp]) / 8.0) * 100.0, 0.0, 100.0)
    o_b1_pp = np.clip((phase_overs[m_b1_pp] / 6.0) * 100.0, 0.0, 100.0)
    t_b1_pp = (0.40 * w_b1_pp) + (0.40 * s_b1_pp) + (0.20 * o_b1_pp)
    pi_b1_pp[m_b1_pp] = (0.65 * t_b1_pp) + (0.35 * i_batter[m_b1_pp])

    # 2. PI_B1_MO
    # W = min(100, (wickets_before / 6) * 100)
    # S = max(0, min(100, ((8 - current_run_rate) / 8) * 100))
    # O = (phase_overs_completed / 9) * 100
    # T = (0.40 * W) + (0.40 * S) + (0.20 * O)
    # I = B
    # PI_B1_MO = (0.65 * T) + (0.35 * I)
    w_b1_mo = np.clip((w_before[m_b1_mo] / 6.0) * 100.0, 0.0, 100.0)
    s_b1_mo = np.clip(((8.0 - crr[m_b1_mo]) / 8.0) * 100.0, 0.0, 100.0)
    o_b1_mo = np.clip((phase_overs[m_b1_mo] / 9.0) * 100.0, 0.0, 100.0)
    t_b1_mo = (0.40 * w_b1_mo) + (0.40 * s_b1_mo) + (0.20 * o_b1_mo)
    pi_b1_mo[m_b1_mo] = (0.65 * t_b1_mo) + (0.35 * i_batter[m_b1_mo])

    # 3. PI_B1_DO
    # W = min(100, (wickets_before / 6) * 100)
    # S = max(0, min(100, ((10 - current_run_rate) / 10) * 100))
    # O = (phase_overs_completed / 5) * 100
    # T = (0.40 * W) + (0.40 * S) + (0.20 * O)
    # I = B
    # PI_B1_DO = (0.65 * T) + (0.35 * I)
    w_b1_do = np.clip((w_before[m_b1_do] / 6.0) * 100.0, 0.0, 100.0)
    s_b1_do = np.clip(((10.0 - crr[m_b1_do]) / 10.0) * 100.0, 0.0, 100.0)
    o_b1_do = np.clip((phase_overs[m_b1_do] / 5.0) * 100.0, 0.0, 100.0)
    t_b1_do = (0.40 * w_b1_do) + (0.40 * s_b1_do) + (0.20 * o_b1_do)
    pi_b1_do[m_b1_do] = (0.65 * t_b1_do) + (0.35 * i_batter[m_b1_do])

    # ---------------------------------------------------------
    # 4. PART C — FIRST-INNINGS BOWLERS
    # ---------------------------------------------------------
    print("Computing First-Innings Bowlers PI...")
    # 4. PI_BO1_PP
    # W = max(0, ((6 - wickets_before) / 6) * 100)
    # S = max(0, min(100, ((current_run_rate - 8) / (12 - 8)) * 100))
    # O = (phase_overs_completed / 6) * 100
    # T = (0.40 * W) + (0.40 * S) + (0.20 * O)
    # I = (0.50 * B_workload) + (0.50 * S_settling)
    # PI_BO1_PP = (0.65 * T) + (0.35 * I)
    w_bo1_pp = np.clip(((6.0 - w_before[m_b1_pp]) / 6.0) * 100.0, 0.0, 100.0)
    s_bo1_pp = np.clip(((crr[m_b1_pp] - 8.0) / 4.0) * 100.0, 0.0, 100.0)
    o_bo1_pp = np.clip((phase_overs[m_b1_pp] / 6.0) * 100.0, 0.0, 100.0)
    t_bo1_pp = (0.40 * w_bo1_pp) + (0.40 * s_bo1_pp) + (0.20 * o_bo1_pp)
    pi_bo1_pp[m_b1_pp] = (0.65 * t_bo1_pp) + (0.35 * i_bowler[m_b1_pp])

    # 5. PI_BO1_MO
    # W = max(0, ((6 - wickets_before) / 6) * 100)
    # S = max(0, min(100, ((current_run_rate - 7) / (11 - 7)) * 100))
    # O = (phase_overs_completed / 9) * 100
    # T = (0.40 * W) + (0.40 * S) + (0.20 * O)
    # I = (0.50 * B_workload) + (0.50 * S_settling)
    # PI_BO1_MO = (0.65 * T) + (0.35 * I)
    w_bo1_mo = np.clip(((6.0 - w_before[m_b1_mo]) / 6.0) * 100.0, 0.0, 100.0)
    s_bo1_mo = np.clip(((crr[m_b1_mo] - 7.0) / 4.0) * 100.0, 0.0, 100.0)
    o_bo1_mo = np.clip((phase_overs[m_b1_mo] / 9.0) * 100.0, 0.0, 100.0)
    t_bo1_mo = (0.40 * w_bo1_mo) + (0.40 * s_bo1_mo) + (0.20 * o_bo1_mo)
    pi_bo1_mo[m_b1_mo] = (0.65 * t_bo1_mo) + (0.35 * i_bowler[m_b1_mo])

    # 6. PI_BO1_DO
    # W = max(0, ((6 - wickets_before) / 6) * 100)
    # S = max(0, min(100, ((current_run_rate - 9) / (15 - 9)) * 100))
    # O = (phase_overs_completed / 5) * 100
    # T = (0.40 * W) + (0.40 * S) + (0.20 * O)
    # I = (0.50 * B_workload) + (0.50 * S_settling)
    # PI_BO1_DO = (0.65 * T) + (0.35 * I)
    w_bo1_do = np.clip(((6.0 - w_before[m_b1_do]) / 6.0) * 100.0, 0.0, 100.0)
    s_bo1_do = np.clip(((crr[m_b1_do] - 9.0) / 6.0) * 100.0, 0.0, 100.0)
    o_bo1_do = np.clip((phase_overs[m_b1_do] / 5.0) * 100.0, 0.0, 100.0)
    t_bo1_do = (0.40 * w_bo1_do) + (0.40 * s_bo1_do) + (0.20 * o_bo1_do)
    pi_bo1_do[m_b1_do] = (0.65 * t_bo1_do) + (0.35 * i_bowler[m_b1_do])

    # ---------------------------------------------------------
    # 5. PART D — SECOND-INNINGS BATTERS
    # ---------------------------------------------------------
    print("Computing Second-Innings Batters PI...")
    # 7. PI_B2_PP
    # R = max(0, min(100, ((RRR - 6) / (12 - 6)) * 100))
    # W = min(100, (wickets_before / 6) * 100)
    # O = (phase_overs_completed / 6) * 100
    # T = (0.50 * R) + (0.30 * W) + (0.20 * O)
    # I = B
    # PI_B2_PP = (0.65 * T) + (0.35 * I)
    r_b2_pp = np.clip(((rrr[m_b2_pp] - 6.0) / 6.0) * 100.0, 0.0, 100.0)
    w_b2_pp = np.clip((w_before[m_b2_pp] / 6.0) * 100.0, 0.0, 100.0)
    o_b2_pp = np.clip((phase_overs[m_b2_pp] / 6.0) * 100.0, 0.0, 100.0)
    t_b2_pp = (0.50 * r_b2_pp) + (0.30 * w_b2_pp) + (0.20 * o_b2_pp)
    pi_b2_pp[m_b2_pp] = (0.65 * t_b2_pp) + (0.35 * i_batter[m_b2_pp])

    # 8. PI_B2_MO
    # R = max(0, min(100, ((RRR - 7) / (13 - 7)) * 100))
    # W = min(100, (wickets_before / 6) * 100)
    # O = (phase_overs_completed / 9) * 100
    # T = (0.50 * R) + (0.30 * W) + (0.20 * O)
    # I = B
    # PI_B2_MO = (0.65 * T) + (0.35 * I)
    r_b2_mo = np.clip(((rrr[m_b2_mo] - 7.0) / 6.0) * 100.0, 0.0, 100.0)
    w_b2_mo = np.clip((w_before[m_b2_mo] / 6.0) * 100.0, 0.0, 100.0)
    o_b2_mo = np.clip((phase_overs[m_b2_mo] / 9.0) * 100.0, 0.0, 100.0)
    t_b2_mo = (0.50 * r_b2_mo) + (0.30 * w_b2_mo) + (0.20 * o_b2_mo)
    pi_b2_mo[m_b2_mo] = (0.65 * t_b2_mo) + (0.35 * i_batter[m_b2_mo])

    # 9. PI_B2_DO
    # R = max(0, min(100, ((RRR - 9) / (18 - 9)) * 100))
    # W = min(100, (wickets_before / 6) * 100)
    # O = (phase_overs_completed / 5) * 100
    # T = (0.50 * R) + (0.30 * W) + (0.20 * O)
    # I = B
    # PI_B2_DO = (0.65 * T) + (0.35 * I)
    r_b2_do = np.clip(((rrr[m_b2_do] - 9.0) / 9.0) * 100.0, 0.0, 100.0)
    w_b2_do = np.clip((w_before[m_b2_do] / 6.0) * 100.0, 0.0, 100.0)
    o_b2_do = np.clip((phase_overs[m_b2_do] / 5.0) * 100.0, 0.0, 100.0)
    t_b2_do = (0.50 * r_b2_do) + (0.30 * w_b2_do) + (0.20 * o_b2_do)
    pi_b2_do[m_b2_do] = (0.65 * t_b2_do) + (0.35 * i_batter[m_b2_do])

    # ---------------------------------------------------------
    # 6. PART E — SECOND-INNINGS BOWLERS
    # ---------------------------------------------------------
    print("Computing Second-Innings Bowlers PI...")
    # 10. PI_BO2_PP
    # S = max(0, min(100, ((current_run_rate - 6) / (12 - 6)) * 100))
    # W = max(0, ((6 - wickets_before) / 6) * 100)
    # O = (phase_overs_completed / 6) * 100
    # T = (0.40 * S) + (0.40 * W) + (0.20 * O)
    # I = (0.50 * B_workload) + (0.50 * S_settling)
    # PI_BO2_PP = (0.65 * T) + (0.35 * I)
    s_bo2_pp = np.clip(((crr[m_b2_pp] - 6.0) / 6.0) * 100.0, 0.0, 100.0)
    w_bo2_pp = np.clip(((6.0 - w_before[m_b2_pp]) / 6.0) * 100.0, 0.0, 100.0)
    o_bo2_pp = np.clip((phase_overs[m_b2_pp] / 6.0) * 100.0, 0.0, 100.0)
    t_bo2_pp = (0.40 * s_bo2_pp) + (0.40 * w_bo2_pp) + (0.20 * o_bo2_pp)
    pi_bo2_pp[m_b2_pp] = (0.65 * t_bo2_pp) + (0.35 * i_bowler[m_b2_pp])

    # 11. PI_BO2_MO
    # S = max(0, min(100, ((current_run_rate - 7) / (11 - 7)) * 100))
    # W = max(0, ((6 - wickets_before) / 6) * 100)
    # O = (phase_overs_completed / 9) * 100
    # T = (0.40 * S) + (0.40 * W) + (0.20 * O)
    # I = (0.50 * B_workload) + (0.50 * S_settling)
    # PI_BO2_MO = (0.65 * T) + (0.35 * I)
    s_bo2_mo = np.clip(((crr[m_b2_mo] - 7.0) / 4.0) * 100.0, 0.0, 100.0)
    w_bo2_mo = np.clip(((6.0 - w_before[m_b2_mo]) / 6.0) * 100.0, 0.0, 100.0)
    o_bo2_mo = np.clip((phase_overs[m_b2_mo] / 9.0) * 100.0, 0.0, 100.0)
    t_bo2_mo = (0.40 * s_bo2_mo) + (0.40 * w_bo2_mo) + (0.20 * o_bo2_mo)
    pi_bo2_mo[m_b2_mo] = (0.65 * t_bo2_mo) + (0.35 * i_bowler[m_b2_mo])

    # 12. PI_BO2_DO
    # S = max(0, min(100, ((RRR - 9) / (18 - 9)) * 100))
    # W = max(0, ((6 - wickets_before) / 6) * 100)
    # O = (phase_overs_completed / 5) * 100
    # T = (0.50 * S) + (0.30 * W) + (0.20 * O)
    # I = (0.50 * B_workload) + (0.50 * S_settling)
    # PI_BO2_DO = (0.65 * T) + (0.35 * I)
    s_bo2_do = np.clip(((rrr[m_b2_do] - 9.0) / 9.0) * 100.0, 0.0, 100.0)
    w_bo2_do = np.clip(((6.0 - w_before[m_b2_do]) / 6.0) * 100.0, 0.0, 100.0)
    o_bo2_do = np.clip((phase_overs[m_b2_do] / 5.0) * 100.0, 0.0, 100.0)
    t_bo2_do = (0.50 * s_bo2_do) + (0.30 * w_bo2_do) + (0.20 * o_bo2_do)
    pi_bo2_do[m_b2_do] = (0.65 * t_bo2_do) + (0.35 * i_bowler[m_b2_do])

    # ---------------------------------------------------------
    # 7. Populate DataFrame & Unified Columns
    # ---------------------------------------------------------
    print("Assembling output DataFrame and unified PI columns...")
    # Add rounded formula columns
    df['PI_B1_PP']  = np.round(pi_b1_pp, 2)
    df['PI_B1_MO']  = np.round(pi_b1_mo, 2)
    df['PI_B1_DO']  = np.round(pi_b1_do, 2)

    df['PI_BO1_PP'] = np.round(pi_bo1_pp, 2)
    df['PI_BO1_MO'] = np.round(pi_bo1_mo, 2)
    df['PI_BO1_DO'] = np.round(pi_bo1_do, 2)

    df['PI_B2_PP']  = np.round(pi_b2_pp, 2)
    df['PI_B2_MO']  = np.round(pi_b2_mo, 2)
    df['PI_B2_DO']  = np.round(pi_b2_do, 2)

    df['PI_BO2_PP'] = np.round(pi_bo2_pp, 2)
    df['PI_BO2_MO'] = np.round(pi_bo2_mo, 2)
    df['PI_BO2_DO'] = np.round(pi_bo2_do, 2)

    # Unified Batting_PI and Bowling_PI
    # Coalesce across the 6 mutually exclusive formula columns
    df['Batting_PI'] = (
        df['PI_B1_PP']
        .combine_first(df['PI_B1_MO'])
        .combine_first(df['PI_B1_DO'])
        .combine_first(df['PI_B2_PP'])
        .combine_first(df['PI_B2_MO'])
        .combine_first(df['PI_B2_DO'])
    )

    df['Bowling_PI'] = (
        df['PI_BO1_PP']
        .combine_first(df['PI_BO1_MO'])
        .combine_first(df['PI_BO1_DO'])
        .combine_first(df['PI_BO2_PP'])
        .combine_first(df['PI_BO2_MO'])
        .combine_first(df['PI_BO2_DO'])
    )

    # Assign Qualitative Pressure Levels
    df['Batting_Pressure_Level'] = assign_pressure_level(df['Batting_PI'])
    df['Bowling_Pressure_Level'] = assign_pressure_level(df['Bowling_PI'])

    # ---------------------------------------------------------
    # 8. Rigorous Integrity Assertions
    # ---------------------------------------------------------
    print("Running validation assertions...")
    assert len(df) == total_rows, f"Row count changed! Expected {total_rows}, got {len(df)}"

    # Check that Batting_PI and Bowling_PI have ZERO nulls
    assert df['Batting_PI'].isnull().sum() == 0, "Null values found in Batting_PI!"
    assert df['Bowling_PI'].isnull().sum() == 0, "Null values found in Bowling_PI!"
    assert df['Batting_Pressure_Level'].isnull().sum() == 0, "Null values found in Batting_Pressure_Level!"
    assert df['Bowling_Pressure_Level'].isnull().sum() == 0, "Null values found in Bowling_Pressure_Level!"

    # Bounds [0.0, 100.0]
    assert (df['Batting_PI'] >= 0.0).all() and (df['Batting_PI'] <= 100.0).all(), "Batting_PI outside [0, 100]!"
    assert (df['Bowling_PI'] >= 0.0).all() and (df['Bowling_PI'] <= 100.0).all(), "Bowling_PI outside [0, 100]!"

    # Mutually exclusive formula column checks:
    batting_formula_cols = ['PI_B1_PP', 'PI_B1_MO', 'PI_B1_DO', 'PI_B2_PP', 'PI_B2_MO', 'PI_B2_DO']
    bowling_formula_cols = ['PI_BO1_PP', 'PI_BO1_MO', 'PI_BO1_DO', 'PI_BO2_PP', 'PI_BO2_MO', 'PI_BO2_DO']

    bat_non_nulls = df[batting_formula_cols].notnull().sum(axis=1)
    bowl_non_nulls = df[bowling_formula_cols].notnull().sum(axis=1)

    assert (bat_non_nulls == 1).all(), "Every row must have exactly ONE non-null Batting formula column!"
    assert (bowl_non_nulls == 1).all(), "Every row must have exactly ONE non-null Bowling formula column!"

    print("All validation assertions passed successfully!")

    # ---------------------------------------------------------
    # 9. Save output
    # ---------------------------------------------------------
    print(f"Writing output dataset to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Successfully saved {len(df):,} deliveries to {output_path} ({len(df.columns)} columns).")

    return df


if __name__ == '__main__':
    in_file = Path('data/processed/delivery_match_state.csv')
    out_file = Path('data/processed/delivery_pressure_index.csv')
    calculate_pressure_index(in_file, out_file)
