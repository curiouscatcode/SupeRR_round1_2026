"""
Step 16.3: Investigation Script 02
Bowling Role & Phase Exposure & Bias Investigation (Experiment 3)
==================================================================
Investigates whether the bowling pressure classification (Z > 1.00)
or ranking methodology (BoRS) systematically favours particular bowling
phases or roles (Powerplay, Middle Overs, Death Overs, Multi-Phase).

Evaluates:
1. Bowling Role Definitions:
   - Powerplay Specialist: PP share >= 45% and Death share < 25%
   - Middle Overs Specialist: Middle share >= 50% and Death share < 25%
   - Death Overs Specialist: Death share >= 30% and PP share < 30%
   - Multi-Phase Bowler: All others (multi-phase pace spearheads / all-rounders)
2. Bowling Pressure Exposure:
   - Delivery-level capture rates and representation indices by role
   - Phase breakdown within each bowling role
3. Bowling Ranking Outcomes:
   - Rule B Tier 1 and Tier 2 qualification across roles
   - Top 10 and Top 25 representation
   - Component score distributions (Economy 40%, Wickets 25%, Dots 20%, Diff 15%)
4. Structural Diagnosis:
   - Evaluates whether role disparities stem from pressure classification,
     BoRS formula weights, or genuine skill differences.

Exports:
- outputs/step_16_3_role_threshold_investigation/bowling_role_phase_exposure.csv
- outputs/step_16_3_role_threshold_investigation/bowling_player_diagnostics_and_rankings.csv
- outputs/step_16_3_role_threshold_investigation/bowling_role_bias_summary.csv
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/step_16_3_role_threshold_investigation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BOWLER_WICKET_TYPES = ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']
K = 50.0


def classify_bowler_role(pp_pct, mo_pct, do_pct):
    if do_pct >= 30.0 and pp_pct < 30.0:
        return 'Death Overs Specialist'
    elif pp_pct >= 45.0 and do_pct < 25.0:
        return 'Powerplay Specialist'
    elif mo_pct >= 50.0 and do_pct < 25.0:
        return 'Middle Overs Specialist'
    else:
        return 'Multi-Phase Bowler'


def main():
    print("=== Step 16.3 Script 02: Bowling Role & Phase Bias Investigation ===")

    # 1. Load active cleaned dataset
    raw_df = pd.read_csv(PROCESSED_DIR / "delivery_pressure_index.csv")
    tail_mask = (raw_df['innings'] == 2) & (raw_df['runs_required'] <= 0)
    df = raw_df[~tail_mask].copy()

    bowl_df = df[df['is_legal_ball'] == 1].copy()
    total_legal_balls = len(bowl_df)
    print(f"Total Bowling Legal Balls: {total_legal_balls:,}")

    # 2. Compute Approach B Bowling Z-score (Phase x Innings)
    grouped = bowl_df.groupby(['innings', 'phase'])['Bowling_PI']
    means = grouped.transform('mean')
    stds = grouped.transform('std')
    bowl_df['z_score'] = (bowl_df['Bowling_PI'] - means) / stds
    bowl_df['hp'] = bowl_df['z_score'] > 1.00
    total_hp_balls = bowl_df['hp'].sum()
    print(f"Total High-Pressure Bowling Balls (Z > 1.00): {total_hp_balls:,} ({total_hp_balls/total_legal_balls*100:.2f}%)")

    # 3. Classify Bowlers by Phase Allocation
    bp = bowl_df.groupby(['bowler_id', 'phase']).size().unstack(fill_value=0)
    for ph in ['PP', 'Middle', 'Death']:
        if ph not in bp.columns:
            bp[ph] = 0
    bp['total'] = bp.sum(axis=1)
    bp['pp_pct'] = (bp['PP'] / bp['total']) * 100.0
    bp['middle_pct'] = (bp['Middle'] / bp['total']) * 100.0
    bp['death_pct'] = (bp['Death'] / bp['total']) * 100.0

    bp['role'] = [
        classify_bowler_role(p, m, d) 
        for p, m, d in zip(bp['pp_pct'], bp['middle_pct'], bp['death_pct'])
    ]

    bowler_role_map = bp['role'].to_dict()
    bowl_df['bowler_role'] = bowl_df['bowler_id'].map(bowler_role_map)

    # 4. Bowling Role & Phase Exposure Analysis
    roles = ['Powerplay Specialist', 'Middle Overs Specialist', 'Death Overs Specialist', 'Multi-Phase Bowler']
    role_exposure_rows = []

    for r in roles:
        sub = bowl_df[bowl_df['bowler_role'] == r]
        r_tot = len(sub)
        r_hp = sub['hp'].sum()
        r_nat_pct = round((r_tot / total_legal_balls) * 100.0, 2)
        r_cap_pct = round((r_hp / r_tot) * 100.0, 2)
        r_hp_share = round((r_hp / total_hp_balls) * 100.0, 2)
        r_rep_idx = round(r_hp_share / r_nat_pct, 3)

        # Phase breakdown within role
        pp_tot = (sub['phase'] == 'PP').sum()
        pp_hp = (sub['phase'] == 'PP') & sub['hp']
        mo_tot = (sub['phase'] == 'Middle').sum()
        mo_hp = (sub['phase'] == 'Middle') & sub['hp']
        do_tot = (sub['phase'] == 'Death').sum()
        do_hp = (sub['phase'] == 'Death') & sub['hp']

        role_exposure_rows.append({
            'role': r,
            'total_balls': r_tot,
            'natural_share_pct': r_nat_pct,
            'hp_balls': r_hp,
            'within_role_capture_pct': r_cap_pct,
            'hp_share_pct': r_hp_share,
            'representation_index': r_rep_idx,
            'pp_balls_total': pp_tot,
            'pp_hp_balls': pp_hp.sum(),
            'pp_capture_pct': round((pp_hp.sum() / pp_tot * 100.0), 2) if pp_tot > 0 else 0.0,
            'middle_balls_total': mo_tot,
            'middle_hp_balls': mo_hp.sum(),
            'middle_capture_pct': round((mo_hp.sum() / mo_tot * 100.0), 2) if mo_tot > 0 else 0.0,
            'death_balls_total': do_tot,
            'death_hp_balls': do_hp.sum(),
            'death_capture_pct': round((do_hp.sum() / do_tot * 100.0), 2) if do_tot > 0 else 0.0
        })

    role_exposure_df = pd.DataFrame(role_exposure_rows)
    out_exp_path = OUTPUT_DIR / "bowling_role_phase_exposure.csv"
    role_exposure_df.to_csv(out_exp_path, index=False)
    print(f"Saved bowling role exposure to {out_exp_path}")

    # 5. Bowler Diagnostics & BoRS Calculation
    bowl_df['is_bowler_wicket'] = (bowl_df['is_wicket'] & bowl_df['dismissal_type'].isin(BOWLER_WICKET_TYPES)).astype(int)
    bowl_df['is_bowler_dot'] = (bowl_df['bowler_runs_conceded'] == 0).astype(int)

    bowl_df['rc_hp'] = np.where(bowl_df['hp'], bowl_df['bowler_runs_conceded'], 0)
    bowl_df['lb_hp'] = np.where(bowl_df['hp'], 1, 0)
    bowl_df['wk_hp'] = np.where(bowl_df['hp'], bowl_df['is_bowler_wicket'], 0)
    bowl_df['dot_hp'] = np.where(bowl_df['hp'], bowl_df['is_bowler_dot'], 0)

    bowl_df['rc_low'] = np.where(~bowl_df['hp'], bowl_df['bowler_runs_conceded'], 0)
    bowl_df['lb_low'] = np.where(~bowl_df['hp'], 1, 0)

    b_agg = bowl_df.groupby('bowler_id').agg(
        player_name=('bowler_name', 'first'),
        lb_hp=('lb_hp', 'sum'),
        rc_hp=('rc_hp', 'sum'),
        wk_hp=('wk_hp', 'sum'),
        dot_hp=('dot_hp', 'sum'),
        lb_low=('lb_low', 'sum'),
        rc_low=('rc_low', 'sum')
    ).reset_index()

    hp_matches = bowl_df[bowl_df['hp']].groupby('bowler_id')['match_id'].nunique().to_dict()
    b_agg['hp_matches'] = b_agg['bowler_id'].map(hp_matches).fillna(0).astype(int)

    # Attach phase balls
    b_agg['role'] = b_agg['bowler_id'].map(bowler_role_map)
    b_agg['total_balls'] = b_agg['bowler_id'].map(bp['total']).astype(int)
    b_agg['pp_balls'] = b_agg['bowler_id'].map(bp['PP']).astype(int)
    b_agg['mo_balls'] = b_agg['bowler_id'].map(bp['Middle']).astype(int)
    b_agg['do_balls'] = b_agg['bowler_id'].map(bp['Death']).astype(int)
    b_agg['pp_pct'] = b_agg['bowler_id'].map(bp['pp_pct']).round(1)
    b_agg['middle_pct'] = b_agg['bowler_id'].map(bp['middle_pct']).round(1)
    b_agg['death_pct'] = b_agg['bowler_id'].map(bp['death_pct']).round(1)

    # Priors under Step 16 Bowling Control
    tot_hp_balls = b_agg['lb_hp'].sum()
    tot_hp_rc = b_agg['rc_hp'].sum()
    tot_hp_wk = b_agg['wk_hp'].sum()
    tot_hp_dot = b_agg['dot_hp'].sum()
    tot_low_balls = b_agg['lb_low'].sum()
    tot_low_rc = b_agg['rc_low'].sum()

    mu_econ_hp = (tot_hp_rc / tot_hp_balls) * 6.0
    mu_wk_hp = (tot_hp_wk / tot_hp_balls) * 100.0
    mu_dot_hp = (tot_hp_dot / tot_hp_balls) * 100.0
    mu_econ_low = (tot_low_rc / tot_low_balls) * 6.0

    print(f"Priors under Step 16 Control: HP Econ={mu_econ_hp:.4f}, HP Wk%={mu_wk_hp:.4f}, HP Dot%={mu_dot_hp:.4f}, Low Econ={mu_econ_low:.4f}")

    b_agg['lambda_hp'] = b_agg['lb_hp'] / (b_agg['lb_hp'] + K)
    b_agg['lambda_low'] = b_agg['lb_low'] / (b_agg['lb_low'] + K)

    b_agg['econ_obs'] = np.where(b_agg['lb_hp'] > 0, (b_agg['rc_hp'] / b_agg['lb_hp']) * 6.0, mu_econ_hp)
    b_agg['wk_pct_obs'] = np.where(b_agg['lb_hp'] > 0, (b_agg['wk_hp'] / b_agg['lb_hp']) * 100.0, mu_wk_hp)
    b_agg['dot_pct_obs'] = np.where(b_agg['lb_hp'] > 0, (b_agg['dot_hp'] / b_agg['lb_hp']) * 100.0, mu_dot_hp)
    b_agg['econ_low_obs'] = np.where(b_agg['lb_low'] > 0, (b_agg['rc_low'] / b_agg['lb_low']) * 6.0, mu_econ_low)

    b_agg['econ_star'] = b_agg['lambda_hp'] * b_agg['econ_obs'] + (1.0 - b_agg['lambda_hp']) * mu_econ_hp
    b_agg['wk_star'] = b_agg['lambda_hp'] * b_agg['wk_pct_obs'] + (1.0 - b_agg['lambda_hp']) * mu_wk_hp
    b_agg['dot_star'] = b_agg['lambda_hp'] * b_agg['dot_pct_obs'] + (1.0 - b_agg['lambda_hp']) * mu_dot_hp
    b_agg['econ_low_star'] = b_agg['lambda_low'] * b_agg['econ_low_obs'] + (1.0 - b_agg['lambda_low']) * mu_econ_low
    b_agg['diff_econ_star'] = b_agg['econ_low_star'] - b_agg['econ_star']

    b_agg['score_econ'] = np.clip((12.0 - b_agg['econ_star']) / 6.0 * 100.0, 0.0, 100.0)
    b_agg['score_wk'] = np.clip((b_agg['wk_star'] - 1.5) / 7.5 * 100.0, 0.0, 100.0)
    b_agg['score_dot'] = np.clip((b_agg['dot_star'] - 25.0) / 25.0 * 100.0, 0.0, 100.0)
    b_agg['score_diff'] = np.clip((b_agg['diff_econ_star'] + 3.0) / 5.0 * 100.0, 0.0, 100.0)

    b_agg['bors'] = np.round(np.clip(
        0.40 * b_agg['score_econ'] + 
        0.25 * b_agg['score_wk'] + 
        0.20 * b_agg['score_dot'] + 
        0.15 * b_agg['score_diff'], 0.0, 100.0), 2)

    # Rule B Qualification
    p1 = b_agg['lb_hp'] >= 60
    p2 = (b_agg['lb_hp'] >= 50) & (b_agg['hp_matches'] >= 6)
    t1 = p1 | p2
    t2 = (b_agg['lb_hp'] >= 40) & ~t1

    b_agg['tier'] = 'Excluded'
    b_agg.loc[t2, 'tier'] = 'Tier 2'
    b_agg.loc[t1, 'tier'] = 'Tier 1'

    b_agg['tier1_rank'] = np.nan
    b_agg.loc[t1, 'tier1_rank'] = b_agg.loc[t1, 'bors'].rank(ascending=False, method='min').astype(int)

    # Reorder columns cleanly
    diag_cols = [
        'bowler_id', 'player_name', 'role', 'total_balls', 'pp_balls', 'mo_balls', 'do_balls',
        'pp_pct', 'middle_pct', 'death_pct', 'lb_hp', 'hp_matches', 'tier', 'tier1_rank',
        'econ_obs', 'wk_pct_obs', 'dot_pct_obs', 'econ_low_obs',
        'econ_star', 'wk_star', 'dot_star', 'econ_low_star', 'diff_econ_star',
        'score_econ', 'score_wk', 'score_dot', 'score_diff', 'bors'
    ]
    diag_df = b_agg.sort_values(by=['tier', 'tier1_rank', 'lb_hp'], ascending=[True, True, False])[diag_cols]
    out_diag_path = OUTPUT_DIR / "bowling_player_diagnostics_and_rankings.csv"
    diag_df.to_csv(out_diag_path, index=False)
    print(f"Saved bowling player diagnostics to {out_diag_path}")

    # 6. Bowling Role Bias Summary Table
    t1_df = b_agg[b_agg['tier'] == 'Tier 1'].copy()
    tot_t1 = len(t1_df)

    bias_rows = []
    for r in roles:
        r_all = b_agg[b_agg['role'] == r]
        r_t1 = t1_df[t1_df['role'] == r]

        n_all = len(r_all)
        n_t1 = len(r_t1)
        t1_qual_rate = round((n_t1 / n_all * 100.0), 2) if n_all > 0 else 0.0
        t1_share = round((n_t1 / tot_t1 * 100.0), 2) if tot_t1 > 0 else 0.0

        n_top10 = (r_t1['tier1_rank'] <= 10).sum()
        n_top25 = (r_t1['tier1_rank'] <= 25).sum()

        r_exposure_row = role_exposure_df[role_exposure_df['role'] == r].iloc[0]

        bias_rows.append({
            'role': r,
            'total_bowlers': n_all,
            'tier1_bowlers': n_t1,
            'tier1_qual_rate_pct': t1_qual_rate,
            'tier1_share_pct': t1_share,
            'top10_bowlers': n_top10,
            'top25_bowlers': n_top25,
            'mean_bors': round(r_t1['bors'].mean(), 2) if n_t1 > 0 else 0.0,
            'median_bors': round(r_t1['bors'].median(), 2) if n_t1 > 0 else 0.0,
            'mean_score_econ': round(r_t1['score_econ'].mean(), 2) if n_t1 > 0 else 0.0,
            'mean_score_wk': round(r_t1['score_wk'].mean(), 2) if n_t1 > 0 else 0.0,
            'mean_score_dot': round(r_t1['score_dot'].mean(), 2) if n_t1 > 0 else 0.0,
            'mean_score_diff': round(r_t1['score_diff'].mean(), 2) if n_t1 > 0 else 0.0,
            'mean_econ_star': round(r_t1['econ_star'].mean(), 2) if n_t1 > 0 else 0.0,
            'mean_wk_star': round(r_t1['wk_star'].mean(), 2) if n_t1 > 0 else 0.0,
            'mean_dot_star': round(r_t1['dot_star'].mean(), 2) if n_t1 > 0 else 0.0,
            'within_role_hp_capture_pct': r_exposure_row['within_role_capture_pct'],
            'representation_index': r_exposure_row['representation_index']
        })

    bias_df = pd.DataFrame(bias_rows)
    out_bias_path = OUTPUT_DIR / "bowling_role_bias_summary.csv"
    bias_df.to_csv(out_bias_path, index=False)
    print(f"Saved bowling role bias summary to {out_bias_path}")

    print("\nBowling Role Bias Summary:")
    print(bias_df[['role', 'total_bowlers', 'tier1_bowlers', 'tier1_share_pct', 'top10_bowlers', 'top25_bowlers', 'mean_bors', 'within_role_hp_capture_pct']].to_string(index=False))


if __name__ == "__main__":
    main()
