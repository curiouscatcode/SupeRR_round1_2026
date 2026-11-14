"""
Step 16.6.1: Script 02 - Multiplier Sensitivity Analysis (Candidate 2)
=====================================================================
Evaluates the sensitivity of Candidate 2 to the leverage multiplier parameter:
  m in [0.20, 0.35, 0.50, 0.65, 0.80]
where g_m(Z_Lev) = 1.0 + m * tanh(Z_Lev)
      S_2,m = Z_PI * g_m(Z_Lev)
      Z_2,m = Std_PxI(S_2,m)
      HP_2,m = Z_2,m > 1.00

Metrics tracked per multiplier value:
1. Batting & Bowling HP delivery counts and capture %.
2. Innings x Phase capture rates.
3. Batting order capture (Top Order 1-3, Middle 4-6, Lower 7-11, and 1-11 individually).
4. Player ranking impact (BRS3 and BoRS under K=50, Rule B):
   - Tier 1 and Tier 2 qualification counts
   - Spearman rho and Pearson r against Control
   - Top 10 overlap and composition changes
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("outputs/step_16_6_1_independent_audit")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STEP_16_5_DIR = Path("outputs/step_16_5_wpa_investigation")
PROCESSED_DIR = Path("data/processed")

MULTIPLIERS = [0.20, 0.35, 0.50, 0.65, 0.80]
K = 50.0
BOWLER_WICKET_TYPES = ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']


def standardize_series(series):
    s_std = series.std()
    if s_std == 0 or np.isnan(s_std):
        return series - series.mean()
    return (series - series.mean()) / s_std


def calculate_brs3(bat_df: pd.DataFrame, hp_col: str, model_name: str) -> pd.DataFrame:
    df = bat_df.copy()
    df['is_out'] = (df['is_wicket'] & (df['dismissed_player_id'] == df['striker_id'])).astype(int)

    df['runs_hp'] = np.where(df[hp_col], df['runs'], 0)
    df['bf_hp'] = np.where(df[hp_col], 1, 0)
    df['out_hp'] = np.where(df[hp_col], df['is_out'], 0)

    df['runs_low'] = np.where(~df[hp_col], df['runs'], 0)
    df['bf_low'] = np.where(~df[hp_col], 1, 0)

    agg = df.groupby('striker_id').agg(
        player_name=('striker_name', 'first'),
        bf_hp=('bf_hp', 'sum'),
        runs_hp=('runs_hp', 'sum'),
        out_hp=('out_hp', 'sum'),
        bf_low=('bf_low', 'sum'),
        runs_low=('runs_low', 'sum')
    ).reset_index()

    hp_matches = df[df[hp_col]].groupby('striker_id')['match_id'].nunique().to_dict()
    agg['hp_matches'] = agg['striker_id'].map(hp_matches).fillna(0).astype(int)

    tot_bf_hp = agg['bf_hp'].sum()
    tot_runs_hp = agg['runs_hp'].sum()
    tot_out_hp = agg['out_hp'].sum()
    tot_bf_low = agg['bf_low'].sum()
    tot_runs_low = agg['runs_low'].sum()

    mu_sr_hp = (tot_runs_hp / tot_bf_hp) * 100.0 if tot_bf_hp > 0 else 114.0
    mu_out_hp = (tot_out_hp / tot_bf_hp) * 100.0 if tot_bf_hp > 0 else 7.0
    mu_sr_low = (tot_runs_low / tot_bf_low) * 100.0 if tot_bf_low > 0 else 140.0

    agg['lambda_hp'] = agg['bf_hp'] / (agg['bf_hp'] + K)
    agg['lambda_low'] = agg['bf_low'] / (agg['bf_low'] + K)

    agg['sr_obs_hp'] = np.where(agg['bf_hp'] > 0, (agg['runs_hp'] / agg['bf_hp']) * 100.0, mu_sr_hp)
    agg['out_obs_hp'] = np.where(agg['bf_hp'] > 0, (agg['out_hp'] / agg['bf_hp']) * 100.0, mu_out_hp)
    agg['sr_obs_low'] = np.where(agg['bf_low'] > 0, (agg['runs_low'] / agg['bf_low']) * 100.0, mu_sr_low)

    agg['sr_star'] = agg['lambda_hp'] * agg['sr_obs_hp'] + (1.0 - agg['lambda_hp']) * mu_sr_hp
    agg['out_star'] = agg['lambda_hp'] * agg['out_obs_hp'] + (1.0 - agg['lambda_hp']) * mu_out_hp
    agg['surv_star'] = 100.0 - agg['out_star']
    agg['sr_low_star'] = agg['lambda_low'] * agg['sr_obs_low'] + (1.0 - agg['lambda_low']) * mu_sr_low
    agg['diff_sr_star'] = agg['sr_star'] - agg['sr_low_star']

    agg['score_sr'] = np.clip((agg['sr_star'] - 80.0) / 80.0 * 100.0, 0.0, 100.0)
    agg['score_surv'] = np.clip((agg['surv_star'] - 85.0) / 12.5 * 100.0, 0.0, 100.0)
    agg['score_diff'] = np.clip((agg['diff_sr_star'] + 60.0) / 80.0 * 100.0, 0.0, 100.0)

    agg['brs3'] = np.round(np.clip(0.45 * agg['score_sr'] + 0.35 * agg['score_surv'] + 0.20 * agg['score_diff'], 0.0, 100.0), 2)

    t1_mask = (agg['bf_hp'] >= 60) | ((agg['bf_hp'] >= 50) & (agg['hp_matches'] >= 6))
    t2_mask = (agg['bf_hp'] >= 40) & ~t1_mask

    agg['tier'] = 'Excluded'
    agg.loc[t2_mask, 'tier'] = 'Tier 2'
    agg.loc[t1_mask, 'tier'] = 'Tier 1'

    agg['tier1_rank'] = np.nan
    agg.loc[t1_mask, 'tier1_rank'] = agg.loc[t1_mask, 'brs3'].rank(ascending=False, method='min').astype(int)
    agg['model'] = model_name
    return agg


def calculate_bors(bowl_df: pd.DataFrame, hp_col: str, model_name: str) -> pd.DataFrame:
    df = bowl_df.copy()
    df['is_bowler_wicket'] = (df['is_wicket'] & df['dismissal_type'].isin(BOWLER_WICKET_TYPES)).astype(int)
    df['is_bowler_dot'] = (df['bowler_runs_conceded'] == 0).astype(int)

    df['rc_hp'] = np.where(df[hp_col], df['bowler_runs_conceded'], 0)
    df['lb_hp'] = np.where(df[hp_col], 1, 0)
    df['wk_hp'] = np.where(df[hp_col], df['is_bowler_wicket'], 0)
    df['dot_hp'] = np.where(df[hp_col], df['is_bowler_dot'], 0)

    df['rc_low'] = np.where(~df[hp_col], df['bowler_runs_conceded'], 0)
    df['lb_low'] = np.where(~df[hp_col], 1, 0)

    agg = df.groupby('bowler_id').agg(
        player_name=('bowler_name', 'first'),
        lb_hp=('lb_hp', 'sum'),
        rc_hp=('rc_hp', 'sum'),
        wk_hp=('wk_hp', 'sum'),
        dot_hp=('dot_hp', 'sum'),
        lb_low=('lb_low', 'sum'),
        rc_low=('rc_low', 'sum')
    ).reset_index()

    hp_matches = df[df[hp_col]].groupby('bowler_id')['match_id'].nunique().to_dict()
    agg['hp_matches'] = agg['bowler_id'].map(hp_matches).fillna(0).astype(int)

    tot_hp_balls = agg['lb_hp'].sum()
    tot_hp_rc = agg['rc_hp'].sum()
    tot_hp_wk = agg['wk_hp'].sum()
    tot_hp_dot = agg['dot_hp'].sum()
    tot_low_balls = agg['lb_low'].sum()
    tot_low_rc = agg['rc_low'].sum()

    mu_econ_hp = (tot_hp_rc / tot_hp_balls) * 6.0 if tot_hp_balls > 0 else 8.5
    mu_wk_hp = (tot_hp_wk / tot_hp_balls) * 100.0 if tot_hp_balls > 0 else 5.0
    mu_dot_hp = (tot_hp_dot / tot_hp_balls) * 100.0 if tot_hp_balls > 0 else 35.0
    mu_econ_low = (tot_low_rc / tot_low_balls) * 6.0 if tot_low_balls > 0 else 7.8

    agg['lambda_hp'] = agg['lb_hp'] / (agg['lb_hp'] + K)
    agg['lambda_low'] = agg['lb_low'] / (agg['lb_low'] + K)

    agg['econ_obs'] = np.where(agg['lb_hp'] > 0, (agg['rc_hp'] / agg['lb_hp']) * 6.0, mu_econ_hp)
    agg['wk_pct_obs'] = np.where(agg['lb_hp'] > 0, (agg['wk_hp'] / agg['lb_hp']) * 100.0, mu_wk_hp)
    agg['dot_pct_obs'] = np.where(agg['lb_hp'] > 0, (agg['dot_hp'] / agg['lb_hp']) * 100.0, mu_dot_hp)
    agg['econ_low_obs'] = np.where(agg['lb_low'] > 0, (agg['rc_low'] / agg['lb_low']) * 6.0, mu_econ_low)

    agg['econ_star'] = agg['lambda_hp'] * agg['econ_obs'] + (1.0 - agg['lambda_hp']) * mu_econ_hp
    agg['wk_star'] = agg['lambda_hp'] * agg['wk_pct_obs'] + (1.0 - agg['lambda_hp']) * mu_wk_hp
    agg['dot_star'] = agg['lambda_hp'] * agg['dot_pct_obs'] + (1.0 - agg['lambda_hp']) * mu_dot_hp
    agg['econ_low_star'] = agg['lambda_low'] * agg['econ_low_obs'] + (1.0 - agg['lambda_low']) * mu_econ_low
    agg['diff_econ_star'] = agg['econ_low_star'] - agg['econ_star']

    agg['score_econ'] = np.clip((12.0 - agg['econ_star']) / 6.0 * 100.0, 0.0, 100.0)
    agg['score_wk'] = np.clip((agg['wk_star'] - 1.5) / 7.5 * 100.0, 0.0, 100.0)
    agg['score_dot'] = np.clip((agg['dot_star'] - 25.0) / 25.0 * 100.0, 0.0, 100.0)
    agg['score_diff'] = np.clip((agg['diff_econ_star'] + 3.0) / 5.0 * 100.0, 0.0, 100.0)

    agg['bors'] = np.round(np.clip(
        0.40 * agg['score_econ'] + 0.25 * agg['score_wk'] + 0.20 * agg['score_dot'] + 0.15 * agg['score_diff'],
        0.0, 100.0), 2)

    t1_mask = (agg['lb_hp'] >= 60) | ((agg['lb_hp'] >= 50) & (agg['hp_matches'] >= 6))
    t2_mask = (agg['lb_hp'] >= 40) & ~t1_mask

    agg['tier'] = 'Excluded'
    agg.loc[t2_mask, 'tier'] = 'Tier 2'
    agg.loc[t1_mask, 'tier'] = 'Tier 1'

    agg['tier1_rank'] = np.nan
    agg.loc[t1_mask, 'tier1_rank'] = agg.loc[t1_mask, 'bors'].rank(ascending=False, method='min').astype(int)
    agg['model'] = model_name
    return agg


def main():
    print("=== Step 16.6.1 Script 02: Multiplier Sensitivity Analysis ===")
    t0 = time.time()

    # Load master dataset
    wpa_parquet = STEP_16_5_DIR / "delivery_wpa_leverage.parquet"
    print(f"Loading data from {wpa_parquet}...")
    df = pd.read_parquet(wpa_parquet)

    # Merge match state for runs, wickets, dismissal types
    dms_path = PROCESSED_DIR / "delivery_match_state.csv"
    print(f"Loading match state from {dms_path}...")
    dms_cols = ['match_id', 'innings', 'overid', 'innings_ball_num',
                'runs', 'is_wicket', 'dismissed_player_id', 'dismissal_type', 'bowler_runs_conceded']
    dms_df = pd.read_csv(dms_path, usecols=dms_cols)

    merge_keys = ['match_id', 'innings', 'overid', 'innings_ball_num']
    df = df.drop(columns=['runs', 'is_wicket', 'dismissed_player_id', 'dismissal_type', 'bowler_runs_conceded'], errors='ignore')
    df = df.merge(dms_df, on=merge_keys, how='left')

    bat_mask = df['is_batter_ball_faced'] == 1
    bowl_mask = df['is_legal_ball'] == 1

    # Standardize leverage within Phase x Innings
    bat_grouped_lev = df[bat_mask].groupby(['innings', 'phase'])['expected_leverage_pct']
    z_lev_bat = (df.loc[bat_mask, 'expected_leverage_pct'] - bat_grouped_lev.transform('mean')) / bat_grouped_lev.transform('std')
    z_pi_bat = df.loc[bat_mask, 'batting_z_score'].values

    bowl_grouped_lev = df[bowl_mask].groupby(['innings', 'phase'])['expected_leverage_pct']
    z_lev_bowl = (df.loc[bowl_mask, 'expected_leverage_pct'] - bowl_grouped_lev.transform('mean')) / bowl_grouped_lev.transform('std')
    z_pi_bowl = df.loc[bowl_mask, 'bowling_z_score'].values

    # Candidate 0 (Control)
    df.loc[bat_mask, 'hp_cand0_bat'] = z_pi_bat > 1.00
    df.loc[bowl_mask, 'hp_cand0_bowl'] = z_pi_bowl > 1.00

    # Calculate Control Rankings
    print("\nCalculating Control (Candidate 0) Rankings...")
    bat_control = calculate_brs3(df[bat_mask], 'hp_cand0_bat', 'Control')
    bowl_control = calculate_bors(df[bowl_mask], 'hp_cand0_bowl', 'Control')

    ctrl_t1_bat = bat_control[bat_control['tier'] == 'Tier 1'].set_index('striker_id')
    ctrl_t1_bowl = bowl_control[bowl_control['tier'] == 'Tier 1'].set_index('bowler_id')
    ctrl_top10_bat_ids = set(ctrl_t1_bat.nsmallest(10, 'tier1_rank').index)
    ctrl_top10_bowl_ids = set(ctrl_t1_bowl.nsmallest(10, 'tier1_rank').index)

    # Multiplier Sensitivity Loop
    sensitivity_rows = []
    position_breakdown_rows = []
    phase_breakdown_rows = []

    # Include Control as m = 0.00
    models_to_test = [(0.00, 'Control (m=0.00)')] + [(m, f"Cand 2 (m={m:.2f})") for m in MULTIPLIERS]

    for m, m_name in models_to_test:
        print(f"\nEvaluating Multiplier m = {m:.2f} ({m_name})...")
        hp_bat_col = f"hp_m_{m:.2f}_bat"
        hp_bowl_col = f"hp_m_{m:.2f}_bowl"

        if m == 0.00:
            df.loc[bat_mask, hp_bat_col] = df.loc[bat_mask, 'hp_cand0_bat']
            df.loc[bowl_mask, hp_bowl_col] = df.loc[bowl_mask, 'hp_cand0_bowl']
        else:
            # Batting Candidate 2 with multiplier m
            g_lev_b = 1.0 + m * np.tanh(z_lev_bat.values)
            raw_b = z_pi_bat * g_lev_b
            df.loc[bat_mask, f'raw_m_{m:.2f}_bat'] = raw_b
            z_cand_b = df[bat_mask].groupby(['innings', 'phase'])[f'raw_m_{m:.2f}_bat'].transform(standardize_series)
            df.loc[bat_mask, hp_bat_col] = z_cand_b > 1.00

            # Bowling Candidate 2 with multiplier m
            g_lev_bw = 1.0 + m * np.tanh(z_lev_bowl.values)
            raw_bw = z_pi_bowl * g_lev_bw
            df.loc[bowl_mask, f'raw_m_{m:.2f}_bowl'] = raw_bw
            z_cand_bw = df[bowl_mask].groupby(['innings', 'phase'])[f'raw_m_{m:.2f}_bowl'].transform(standardize_series)
            df.loc[bowl_mask, hp_bowl_col] = z_cand_bw > 1.00

        # Deliveries
        n_bat_hp = int(df.loc[bat_mask, hp_bat_col].sum())
        pct_bat_hp = (n_bat_hp / bat_mask.sum()) * 100.0
        n_bowl_hp = int(df.loc[bowl_mask, hp_bowl_col].sum())
        pct_bowl_hp = (n_bowl_hp / bowl_mask.sum()) * 100.0

        # Overlap with Control
        ov_bat_pct = ((df.loc[bat_mask, 'hp_cand0_bat'] & df.loc[bat_mask, hp_bat_col]).sum() / df.loc[bat_mask, 'hp_cand0_bat'].sum()) * 100.0
        ov_bowl_pct = ((df.loc[bowl_mask, 'hp_cand0_bowl'] & df.loc[bowl_mask, hp_bowl_col]).sum() / df.loc[bowl_mask, 'hp_cand0_bowl'].sum()) * 100.0

        # Batting Position Capture Rates
        pos_grp = df[bat_mask].groupby('batting_order')[hp_bat_col].agg(['count', 'mean'])
        pos_grp['mean'] = pos_grp['mean'] * 100.0

        top_order_mask = df[bat_mask]['batting_order'].isin([1, 2, 3])
        mid_order_mask = df[bat_mask]['batting_order'].isin([4, 5, 6])
        low_order_mask = df[bat_mask]['batting_order'].isin([7, 8, 9, 10, 11])

        top_capture = df.loc[bat_mask & top_order_mask, hp_bat_col].mean() * 100.0
        mid_capture = df.loc[bat_mask & mid_order_mask, hp_bat_col].mean() * 100.0
        low_capture = df.loc[bat_mask & low_order_mask, hp_bat_col].mean() * 100.0

        # Save position breakdown for this m
        for p in range(1, 12):
            if p in pos_grp.index:
                position_breakdown_rows.append({
                    'multiplier': m,
                    'model_name': m_name,
                    'batting_order': p,
                    'total_balls': int(pos_grp.loc[p, 'count']),
                    'hp_capture_pct': round(pos_grp.loc[p, 'mean'], 2)
                })

        # Phase Capture Rates
        phase_bat = df[bat_mask].groupby('phase')[hp_bat_col].mean() * 100.0
        inn_phase_bat = df[bat_mask].groupby(['innings', 'phase'])[hp_bat_col].mean() * 100.0

        # Run Rankings
        bat_m = calculate_brs3(df[bat_mask], hp_bat_col, m_name)
        bowl_m = calculate_bors(df[bowl_mask], hp_bowl_col, m_name)

        t1_bat = bat_m[bat_m['tier'] == 'Tier 1'].set_index('striker_id')
        t2_bat_count = (bat_m['tier'] == 'Tier 2').sum()
        t1_bowl = bowl_m[bowl_m['tier'] == 'Tier 1'].set_index('bowler_id')
        t2_bowl_count = (bowl_m['tier'] == 'Tier 2').sum()

        # Correlations vs Control on Common Tier 1
        common_bat_ids = t1_bat.index.intersection(ctrl_t1_bat.index)
        s1_bat = ctrl_t1_bat.loc[common_bat_ids, 'brs3']
        s2_bat = t1_bat.loc[common_bat_ids, 'brs3']
        bat_rho = s1_bat.rank().corr(s2_bat.rank())
        bat_r = s1_bat.corr(s2_bat)

        common_bowl_ids = t1_bowl.index.intersection(ctrl_t1_bowl.index)
        s1_bowl = ctrl_t1_bowl.loc[common_bowl_ids, 'bors']
        s2_bowl = t1_bowl.loc[common_bowl_ids, 'bors']
        bowl_rho = s1_bowl.rank().corr(s2_bowl.rank())
        bowl_r = s1_bowl.corr(s2_bowl)

        top10_bat_ids_m = set(t1_bat.nsmallest(10, 'tier1_rank').index)
        top10_bowl_ids_m = set(t1_bowl.nsmallest(10, 'tier1_rank').index)
        top10_bat_overlap = len(top10_bat_ids_m.intersection(ctrl_top10_bat_ids))
        top10_bowl_overlap = len(top10_bowl_ids_m.intersection(ctrl_top10_bowl_ids))

        sensitivity_rows.append({
            'multiplier': m,
            'model_name': m_name,
            'batting_hp_count': n_bat_hp,
            'batting_hp_pct': round(pct_bat_hp, 2),
            'batting_overlap_control_pct': round(ov_bat_pct, 2),
            'top_order_1_3_hp_pct': round(top_capture, 2),
            'middle_order_4_6_hp_pct': round(mid_capture, 2),
            'lower_order_7_11_hp_pct': round(low_capture, 2),
            'bowling_hp_count': n_bowl_hp,
            'bowling_hp_pct': round(pct_bowl_hp, 2),
            'bowling_overlap_control_pct': round(ov_bowl_pct, 2),
            'bat_pp_hp_pct': round(phase_bat.get('PP', 0), 2),
            'bat_middle_hp_pct': round(phase_bat.get('Middle', 0), 2),
            'bat_death_hp_pct': round(phase_bat.get('Death', 0), 2),
            'bat_t1_qualified': len(t1_bat),
            'bat_t2_qualified': t2_bat_count,
            'bat_spearman_rho': round(bat_rho, 4) if not np.isnan(bat_rho) else 1.0,
            'bat_pearson_r': round(bat_r, 4) if not np.isnan(bat_r) else 1.0,
            'bat_top10_overlap': top10_bat_overlap,
            'bowl_t1_qualified': len(t1_bowl),
            'bowl_t2_qualified': t2_bowl_count,
            'bowl_spearman_rho': round(bowl_rho, 4) if not np.isnan(bowl_rho) else 1.0,
            'bowl_pearson_r': round(bowl_r, 4) if not np.isnan(bowl_r) else 1.0,
            'bowl_top10_overlap': top10_bowl_overlap
        })

    # Export Results
    df_sens = pd.DataFrame(sensitivity_rows)
    sens_csv = OUTPUT_DIR / "multiplier_sensitivity_analysis.csv"
    df_sens.to_csv(sens_csv, index=False)
    print(f"\nSaved multiplier sensitivity analysis to {sens_csv}")
    print("\nSensitivity Analysis Summary:")
    print(df_sens[['multiplier', 'batting_hp_pct', 'top_order_1_3_hp_pct', 'lower_order_7_11_hp_pct',
                   'bat_t1_qualified', 'bat_spearman_rho', 'bowl_t1_qualified', 'bowl_spearman_rho']].to_string())

    df_pos = pd.DataFrame(position_breakdown_rows)
    pos_csv = OUTPUT_DIR / "multiplier_position_breakdown.csv"
    df_pos.to_csv(pos_csv, index=False)

    print(f"\nTotal time elapsed: {time.time() - t0:.2f} seconds.")


if __name__ == "__main__":
    main()
