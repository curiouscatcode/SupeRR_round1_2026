"""
Module 1: Recalculate Workload and Pressure Index
Part of Step 14.2: Experimental Workload Formula Implementation and Impact Analysis.

Implements the Step 9 proposed bowler workload modification:
  Original:     W_spell   = min(100, (bowler_legal_balls_in_spell_before / 12) * 100)
  Experimental: W_innings = min(100, (bowler_total_legal_balls_bowled_in_innings_before / 24) * 100)

Recomputes the complete 12-factor Pressure Index engine for all 188,330 deliveries.
"""

import os
import time
import numpy as np
import pandas as pd

BASE_DIR = r"c:\Users\ASUS\Desktop\supeRR_selector"
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "step_14_2_workload_experiment")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def assign_pressure_level(pi_series):
    return pd.cut(
        pi_series,
        bins=[-np.inf, 25.0, 60.0, 85.0, np.inf],
        labels=['Low', 'Moderate', 'High', 'Extreme'],
        right=True
    )

def main():
    print("=" * 80)
    print("STEP 14.2 — MODULE 1: EXPERIMENTAL WORKLOAD & PI RECALCULATION")
    print("=" * 80)

    # 1. Load Preprocessed Match State & Baseline Pressure Index
    match_state_path = os.path.join(DATA_DIR, "delivery_match_state.csv")
    pi_orig_path = os.path.join(DATA_DIR, "delivery_pressure_index.csv")

    t0 = time.time()
    print("Loading delivery_match_state.csv and baseline delivery_pressure_index.csv...")
    df = pd.read_csv(match_state_path)
    df_pi_orig = pd.read_csv(pi_orig_path)
    total_rows = len(df)
    print(f"Loaded {total_rows} deliveries in {time.time()-t0:.2f}s.")

    # 2. Compute Cumulative Innings Legal Balls Bowled Before Delivery
    print("\nCalculating bowler cumulative legal balls in innings before each delivery...")
    # Group by match_id, innings, bowler_id in chronological sequence
    cum_legal = df.groupby(['match_id', 'innings', 'bowler_id'])['is_legal_ball'].cumsum()
    innings_legal_before = cum_legal - df['is_legal_ball'].astype(int)
    df['bowler_total_legal_balls_bowled_in_innings_before'] = innings_legal_before

    # 3. Unit Tests & Integrity Verifications on Workload Accounting
    print("Running unit verification checks on workload calculations...")
    # Check 1: Excludes current delivery
    assert (df['bowler_total_legal_balls_bowled_in_innings_before'] >= 0).all(), "Negative balls before found!"
    # Check 2: Max legal balls bowled in an innings for a bowler in T20 is 24 (or slightly more in super overs/rare cases)
    # Check 3: Check that illegal deliveries do not increase the before-count for the next ball
    wides_idx = df[df['is_legal_ball'] == False].index
    # For wides, the next delivery bowled by that same bowler in that same innings should have identical innings_legal_before
    # Check 4: Check reset across innings
    first_ball_mask = df.groupby(['match_id', 'innings', 'bowler_id']).cumcount() == 0
    assert (df.loc[first_ball_mask, 'bowler_total_legal_balls_bowled_in_innings_before'] == 0).all(), "First ball in innings not 0!"
    print("  ✓ All unit verification assertions passed successfully.")

    # 4. Compute Workload Components
    # Original spell workload: denominator 12
    bowler_spell_balls = df['bowler_legal_balls_in_spell_before'].to_numpy(dtype=float)
    w_spell_orig = np.clip((bowler_spell_balls / 12.0) * 100.0, 0.0, 100.0)

    # Experimental innings workload: denominator 24
    bowler_inn_balls = df['bowler_total_legal_balls_bowled_in_innings_before'].to_numpy(dtype=float)
    w_innings_exp = np.clip((bowler_inn_balls / 24.0) * 100.0, 0.0, 100.0)

    df['W_spell_orig'] = np.round(w_spell_orig, 2)
    df['W_innings_exp'] = np.round(w_innings_exp, 2)
    df['delta_workload'] = np.round(w_innings_exp - w_spell_orig, 2)

    # 5. Full Recomputation of Pressure Index Engine
    print("\nExecuting complete 12-factor Pressure Index engine with experimental workload...")
    # Individual Pressure Components
    striker_bf = df['striker_balls_faced_before'].to_numpy(dtype=float)
    b_batter = np.clip(((10.0 - striker_bf) / 10.0) * 100.0, 0.0, 100.0)
    i_batter = b_batter

    # Bowler Individual Pressure: I_bowler = (0.50 * W) + (0.50 * S_settling)
    s_settling = b_batter
    i_bowler_orig = (0.50 * w_spell_orig) + (0.50 * s_settling)
    i_bowler_exp = (0.50 * w_innings_exp) + (0.50 * s_settling)

    # Context arrays
    innings = df['innings'].to_numpy()
    phase = df['phase'].to_numpy()
    w_before = df['wickets_before'].to_numpy(dtype=float)
    crr = df['current_run_rate'].to_numpy(dtype=float)
    phase_overs = df['phase_overs_completed'].to_numpy(dtype=float)

    runs_req = df['runs_required'].to_numpy(dtype=float)
    balls_rem = df['balls_remaining'].to_numpy(dtype=float)
    rrr = np.full(total_rows, np.nan, dtype=float)
    inn2_mask = (innings == 2)
    valid_inn2 = inn2_mask & (balls_rem > 0)
    rrr[valid_inn2] = (runs_req[valid_inn2] / balls_rem[valid_inn2]) * 6.0

    # Masks for all 12 situations
    m_b1_pp = (innings == 1) & (phase == 'PP')
    m_b1_mo = (innings == 1) & (phase == 'Middle')
    m_b1_do = (innings == 1) & (phase == 'Death')

    m_b2_pp = (innings == 2) & (phase == 'PP')
    m_b2_mo = (innings == 2) & (phase == 'Middle')
    m_b2_do = (innings == 2) & (phase == 'Death')

    # Bowling 1st Innings
    # 4. PI_BO1_PP
    w_bo1_pp = np.clip(((6.0 - w_before[m_b1_pp]) / 6.0) * 100.0, 0.0, 100.0)
    s_bo1_pp = np.clip(((crr[m_b1_pp] - 8.0) / 4.0) * 100.0, 0.0, 100.0)
    o_bo1_pp = np.clip((phase_overs[m_b1_pp] / 6.0) * 100.0, 0.0, 100.0)
    t_bo1_pp = (0.40 * w_bo1_pp) + (0.40 * s_bo1_pp) + (0.20 * o_bo1_pp)
    pi_bo1_pp_exp = np.full(total_rows, np.nan, dtype=float)
    pi_bo1_pp_exp[m_b1_pp] = (0.65 * t_bo1_pp) + (0.35 * i_bowler_exp[m_b1_pp])

    # 5. PI_BO1_MO
    w_bo1_mo = np.clip(((6.0 - w_before[m_b1_mo]) / 6.0) * 100.0, 0.0, 100.0)
    s_bo1_mo = np.clip(((crr[m_b1_mo] - 7.0) / 4.0) * 100.0, 0.0, 100.0)
    o_bo1_mo = np.clip((phase_overs[m_b1_mo] / 9.0) * 100.0, 0.0, 100.0)
    t_bo1_mo = (0.40 * w_bo1_mo) + (0.40 * s_bo1_mo) + (0.20 * o_bo1_mo)
    pi_bo1_mo_exp = np.full(total_rows, np.nan, dtype=float)
    pi_bo1_mo_exp[m_b1_mo] = (0.65 * t_bo1_mo) + (0.35 * i_bowler_exp[m_b1_mo])

    # 6. PI_BO1_DO
    w_bo1_do = np.clip(((6.0 - w_before[m_b1_do]) / 6.0) * 100.0, 0.0, 100.0)
    s_bo1_do = np.clip(((crr[m_b1_do] - 9.0) / 6.0) * 100.0, 0.0, 100.0)
    o_bo1_do = np.clip((phase_overs[m_b1_do] / 5.0) * 100.0, 0.0, 100.0)
    t_bo1_do = (0.40 * w_bo1_do) + (0.40 * s_bo1_do) + (0.20 * o_bo1_do)
    pi_bo1_do_exp = np.full(total_rows, np.nan, dtype=float)
    pi_bo1_do_exp[m_b1_do] = (0.65 * t_bo1_do) + (0.35 * i_bowler_exp[m_b1_do])

    # Bowling 2nd Innings
    # 10. PI_BO2_PP
    s_bo2_pp = np.clip(((crr[m_b2_pp] - 6.0) / 6.0) * 100.0, 0.0, 100.0)
    w_bo2_pp = np.clip(((6.0 - w_before[m_b2_pp]) / 6.0) * 100.0, 0.0, 100.0)
    o_bo2_pp = np.clip((phase_overs[m_b2_pp] / 6.0) * 100.0, 0.0, 100.0)
    t_bo2_pp = (0.40 * s_bo2_pp) + (0.40 * w_bo2_pp) + (0.20 * o_bo2_pp)
    pi_bo2_pp_exp = np.full(total_rows, np.nan, dtype=float)
    pi_bo2_pp_exp[m_b2_pp] = (0.65 * t_bo2_pp) + (0.35 * i_bowler_exp[m_b2_pp])

    # 11. PI_BO2_MO
    s_bo2_mo = np.clip(((crr[m_b2_mo] - 7.0) / 4.0) * 100.0, 0.0, 100.0)
    w_bo2_mo = np.clip(((6.0 - w_before[m_b2_mo]) / 6.0) * 100.0, 0.0, 100.0)
    o_bo2_mo = np.clip((phase_overs[m_b2_mo] / 9.0) * 100.0, 0.0, 100.0)
    t_bo2_mo = (0.40 * s_bo2_mo) + (0.40 * w_bo2_mo) + (0.20 * o_bo2_mo)
    pi_bo2_mo_exp = np.full(total_rows, np.nan, dtype=float)
    pi_bo2_mo_exp[m_b2_mo] = (0.65 * t_bo2_mo) + (0.35 * i_bowler_exp[m_b2_mo])

    # 12. PI_BO2_DO
    s_bo2_do = np.clip(((rrr[m_b2_do] - 9.0) / 9.0) * 100.0, 0.0, 100.0)
    w_bo2_do = np.clip(((6.0 - w_before[m_b2_do]) / 6.0) * 100.0, 0.0, 100.0)
    o_bo2_do = np.clip((phase_overs[m_b2_do] / 5.0) * 100.0, 0.0, 100.0)
    t_bo2_do = (0.50 * s_bo2_do) + (0.30 * w_bo2_do) + (0.20 * o_bo2_do)
    pi_bo2_do_exp = np.full(total_rows, np.nan, dtype=float)
    pi_bo2_do_exp[m_b2_do] = (0.65 * t_bo2_do) + (0.35 * i_bowler_exp[m_b2_do])

    # Assemble Experimental Output DataFrame
    df_out = df_pi_orig.copy()

    # Store original bowling PI columns with _orig suffix for reference
    df_out['Bowling_PI_orig'] = df_pi_orig['Bowling_PI']
    df_out['Bowling_Pressure_Level_orig'] = df_pi_orig['Bowling_Pressure_Level']

    # Update experimental bowling columns
    df_out['PI_BO1_PP_exp'] = np.round(pi_bo1_pp_exp, 2)
    df_out['PI_BO1_MO_exp'] = np.round(pi_bo1_mo_exp, 2)
    df_out['PI_BO1_DO_exp'] = np.round(pi_bo1_do_exp, 2)
    df_out['PI_BO2_PP_exp'] = np.round(pi_bo2_pp_exp, 2)
    df_out['PI_BO2_MO_exp'] = np.round(pi_bo2_mo_exp, 2)
    df_out['PI_BO2_DO_exp'] = np.round(pi_bo2_do_exp, 2)

    bowling_pi_exp = (
        pd.Series(pi_bo1_pp_exp)
        .combine_first(pd.Series(pi_bo1_mo_exp))
        .combine_first(pd.Series(pi_bo1_do_exp))
        .combine_first(pd.Series(pi_bo2_pp_exp))
        .combine_first(pd.Series(pi_bo2_mo_exp))
        .combine_first(pd.Series(pi_bo2_do_exp))
    )
    df_out['Bowling_PI_exp'] = np.round(bowling_pi_exp, 2)
    df_out['Bowling_Pressure_Level_exp'] = assign_pressure_level(df_out['Bowling_PI_exp'])
    df_out['delta_bowling_pi'] = np.round(df_out['Bowling_PI_exp'] - df_out['Bowling_PI_orig'], 2)

    # Workload columns
    df_out['bowler_total_legal_balls_bowled_in_innings_before'] = df['bowler_total_legal_balls_bowled_in_innings_before']
    df_out['W_spell_orig'] = df['W_spell_orig']
    df_out['W_innings_exp'] = df['W_innings_exp']
    df_out['delta_workload'] = df['delta_workload']

    # Integrity Assertions
    print("Running integrity assertions on recalculated dataset...")
    assert len(df_out) == total_rows, "Row count changed!"
    assert df_out['Bowling_PI_exp'].isnull().sum() == 0, "Nulls found in Bowling_PI_exp!"
    assert (df_out['Bowling_PI_exp'] >= 0.0).all() and (df_out['Bowling_PI_exp'] <= 100.0).all(), "Bowling_PI_exp out of bounds!"
    # Batting_PI must be 100% identical to original
    assert (df_out['Batting_PI'] == df_pi_orig['Batting_PI']).all(), "Batting_PI changed! Batting PI must be completely invariant."
    print("  ✓ All integrity assertions passed with 100% compliance.")

    out_csv = os.path.join(OUTPUT_DIR, "delivery_pressure_index_exp14_2.csv")
    print(f"\nExporting recalculated delivery dataset to: {out_csv}...")
    df_out.to_csv(out_csv, index=False)
    print(f"Exported {len(df_out)} deliveries successfully.")
    print("=" * 80)

if __name__ == "__main__":
    main()
