"""
Step 16.5: Script 02 - Pressure Index vs WPA & Expected Leverage Analysis
========================================================================
Comprehensive empirical comparison between Pressure Index (PI) and Win Probability
metrics (Actual WPA, Absolute WPA, Expected Delivery Leverage).

Performs:
1. Subgroup Comparisons (Section 5A & 5B):
   - Overall, Innings 1 vs 2, Phases (PP, Middle, Death), Batting Roles.
   - High Pressure (Z > 1.00) vs Non-HP (Z <= 1.00).
   - Mean, median, standard deviation, IQR (p25, p75).
   - Pearson r and Spearman rho correlations.
   - Match-level clustered bootstrap 95% confidence intervals (1,000 iterations).
2. Four-Quadrant Analysis (Section 5C):
   - High/Low PI vs High/Low Expected Leverage (baseline cutoff = median 1.14%).
   - Delivery counts, percentage, phase/innings shares, win probability, wickets lost.
   - Exemplar real match delivery situations.
   - Sensitivity analysis across 5 cutoffs (1.00%, 1.14%, 1.20%, 1.34%, 1.51%).
3. Batting Position Breakdown (Section 5D):
   - Individual positions 1 to 11 and Top/Middle/Lower roles.
   - Leverage faced, WPA produced, HP capture rate, and leverage at matched PI.
4. Bowling Phase Breakdown (Section 5E):
   - PP, Middle, Death bowling on 180,041 legal balls.
   - Bowler WPA (-WPA), absolute WPA, expected leverage, and HP/leverage overlap.

Outputs:
- outputs/step_16_5_wpa_investigation/pi_vs_leverage_summary.csv
- outputs/step_16_5_wpa_investigation/pi_vs_actual_wpa_summary.csv
- outputs/step_16_5_wpa_investigation/four_quadrant_analysis.csv
- outputs/step_16_5_wpa_investigation/four_quadrant_cutoff_sensitivity.csv
- outputs/step_16_5_wpa_investigation/batting_position_wpa_leverage.csv
- outputs/step_16_5_wpa_investigation/bowling_phase_wpa_leverage.csv
"""

import os
import time
from pathlib import Path
import numpy as np
import pandas as pd
def calc_pearsonr(x, y):
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    xm = x_arr - np.mean(x_arr)
    ym = y_arr - np.mean(y_arr)
    denom = np.sqrt(np.sum(xm ** 2) * np.sum(ym ** 2))
    return float(np.sum(xm * ym) / max(1e-12, denom))


def calc_spearmanr(x, y):
    rx = pd.Series(x).rank().values
    ry = pd.Series(y).rank().values
    return calc_pearsonr(rx, ry)

OUTPUT_DIR = Path("outputs/step_16_5_wpa_investigation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_role(order):
    if order in [1, 2, 3]: return 'Top Order (1-3)'
    elif order in [4, 5, 6]: return 'Middle Order (4-6)'
    else: return 'Lower Order (7-11)'


def compute_bootstrap_ci_diff(df, group_col, val_col, match_col='match_id', n_boot=1000):
    """Vectorized match-level clustered bootstrap for difference in means (HP minus Non-HP)."""
    matches = df[match_col].unique()
    n_m = len(matches)
    m_map = {m: i for i, m in enumerate(matches)}

    m_indices = df[match_col].map(m_map).values
    hp_mask = df[group_col].values
    vals = df[val_col].values

    hp_sum = np.bincount(m_indices[hp_mask], weights=vals[hp_mask], minlength=n_m)
    hp_cnt = np.bincount(m_indices[hp_mask], minlength=n_m)

    nh_sum = np.bincount(m_indices[~hp_mask], weights=vals[~hp_mask], minlength=n_m)
    nh_cnt = np.bincount(m_indices[~hp_mask], minlength=n_m)

    np.random.seed(42)
    boot_idx = np.random.randint(0, n_m, size=(n_boot, n_m))

    diffs = np.zeros(n_boot)
    for b in range(n_boot):
        sample = boot_idx[b]
        tot_hp_val = hp_sum[sample].sum()
        tot_hp_n = hp_cnt[sample].sum()
        tot_nh_val = nh_sum[sample].sum()
        tot_nh_n = nh_cnt[sample].sum()

        m_hp = tot_hp_val / max(1, tot_hp_n)
        m_nh = tot_nh_val / max(1, tot_nh_n)
        diffs[b] = m_hp - m_nh

    ci = np.percentile(diffs, [2.5, 97.5])
    return ci[0], ci[1]


def main():
    print("=== Step 16.5 Script 02: PI vs WPA & Expected Leverage Analysis ===")
    t0 = time.time()

    # Load master delivery dataset
    parquet_path = OUTPUT_DIR / "delivery_wpa_leverage.parquet"
    print(f"Loading {parquet_path}...")
    df = pd.read_parquet(parquet_path)
    print(f"Loaded {len(df):,} deliveries.")

    # Active batting deliveries (180,839)
    bat_df = df[df['is_batter_ball_faced'] == 1].copy()
    bat_df['role'] = bat_df['batting_order'].apply(get_role)

    # Active bowling deliveries (180,041)
    bowl_df = df[df['is_legal_ball'] == 1].copy()

    # -------------------------------------------------------------
    # 1. SECTION 5A: PI VS EXPECTED LEVERAGE
    # -------------------------------------------------------------
    print("\nRunning Section 5A: PI vs Expected Leverage Analysis...")
    subgroups = [
        ('Overall Population', 'All Batting Deliveries', bat_df, 'is_high_pressure_bat', 'batting_z_score'),
        ('Innings', 'Innings 1', bat_df[bat_df['innings'] == 1], 'is_high_pressure_bat', 'batting_z_score'),
        ('Innings', 'Innings 2', bat_df[bat_df['innings'] == 2], 'is_high_pressure_bat', 'batting_z_score'),
        ('Match Phase', 'Powerplay', bat_df[bat_df['phase'] == 'PP'], 'is_high_pressure_bat', 'batting_z_score'),
        ('Match Phase', 'Middle Overs', bat_df[bat_df['phase'] == 'Middle'], 'is_high_pressure_bat', 'batting_z_score'),
        ('Match Phase', 'Death Overs', bat_df[bat_df['phase'] == 'Death'], 'is_high_pressure_bat', 'batting_z_score'),
        ('Batting Role', 'Top Order (1-3)', bat_df[bat_df['role'] == 'Top Order (1-3)'], 'is_high_pressure_bat', 'batting_z_score'),
        ('Batting Role', 'Middle Order (4-6)', bat_df[bat_df['role'] == 'Middle Order (4-6)'], 'is_high_pressure_bat', 'batting_z_score'),
        ('Batting Role', 'Lower Order (7-11)', bat_df[bat_df['role'] == 'Lower Order (7-11)'], 'is_high_pressure_bat', 'batting_z_score'),
        ('Bowling Overall', 'All Bowling Deliveries', bowl_df, 'is_high_pressure_bowl', 'bowling_z_score'),
        ('Bowling Phase', 'Bowling Powerplay', bowl_df[bowl_df['phase'] == 'PP'], 'is_high_pressure_bowl', 'bowling_z_score'),
        ('Bowling Phase', 'Bowling Middle Overs', bowl_df[bowl_df['phase'] == 'Middle'], 'is_high_pressure_bowl', 'bowling_z_score'),
        ('Bowling Phase', 'Bowling Death Overs', bowl_df[bowl_df['phase'] == 'Death'], 'is_high_pressure_bowl', 'bowling_z_score')
    ]

    lev_rows = []
    wpa_rows = []

    for dim, name, sub, hp_col, z_col in subgroups:
        n_tot = len(sub)
        n_hp = int(sub[hp_col].sum())
        pct_hp = (n_hp / n_tot) * 100.0

        hp_sub = sub[sub[hp_col]]
        nh_sub = sub[~sub[hp_col]]

        # Leverage metrics
        m_all_lev = sub['expected_leverage_pct'].mean()
        med_all_lev = sub['expected_leverage_pct'].median()
        m_hp_lev = hp_sub['expected_leverage_pct'].mean()
        med_hp_lev = hp_sub['expected_leverage_pct'].median()
        std_hp_lev = hp_sub['expected_leverage_pct'].std()
        p25_hp_lev = hp_sub['expected_leverage_pct'].quantile(0.25)
        p75_hp_lev = hp_sub['expected_leverage_pct'].quantile(0.75)

        m_nh_lev = nh_sub['expected_leverage_pct'].mean()
        med_nh_lev = nh_sub['expected_leverage_pct'].median()
        std_nh_lev = nh_sub['expected_leverage_pct'].std()
        p25_nh_lev = nh_sub['expected_leverage_pct'].quantile(0.25)
        p75_nh_lev = nh_sub['expected_leverage_pct'].quantile(0.75)

        lev_diff = m_hp_lev - m_nh_lev
        ci_l, ci_u = compute_bootstrap_ci_diff(sub, hp_col, 'expected_leverage_pct')

        # Correlations
        pr_val = calc_pearsonr(sub[z_col], sub['expected_leverage_pct'])
        sp_val = calc_spearmanr(sub[z_col], sub['expected_leverage_pct'])

        lev_rows.append({
            'dimension': dim,
            'subgroup': name,
            'total_deliveries': n_tot,
            'hp_deliveries': n_hp,
            'hp_capture_pct': round(pct_hp, 2),
            'mean_leverage_all': round(m_all_lev, 2),
            'median_leverage_all': round(med_all_lev, 2),
            'mean_leverage_hp': round(m_hp_lev, 2),
            'median_leverage_hp': round(med_hp_lev, 2),
            'iqr_leverage_hp': f"{p25_hp_lev:.2f}-{p75_hp_lev:.2f}",
            'mean_leverage_non_hp': round(m_nh_lev, 2),
            'median_leverage_non_hp': round(med_nh_lev, 2),
            'iqr_leverage_non_hp': f"{p25_nh_lev:.2f}-{p75_nh_lev:.2f}",
            'leverage_diff_hp_minus_nh': round(lev_diff, 2),
            'ci_95_diff_lower': round(ci_l, 2),
            'ci_95_diff_upper': round(ci_u, 2),
            'pearson_r_z_leverage': round(pr_val, 4),
            'spearman_rho_z_leverage': round(sp_val, 4)
        })

        # -------------------------------------------------------------
        # 2. SECTION 5B: PI VS ACTUAL WPA
        # -------------------------------------------------------------
        # Signed WPA
        m_hp_swpa = hp_sub['wpa_pct'].mean()
        med_hp_swpa = hp_sub['wpa_pct'].median()
        m_nh_swpa = nh_sub['wpa_pct'].mean()
        med_nh_swpa = nh_sub['wpa_pct'].median()

        # Absolute WPA
        m_all_awpa = sub['absolute_wpa_pct'].mean()
        med_all_awpa = sub['absolute_wpa_pct'].median()
        m_hp_awpa = hp_sub['absolute_wpa_pct'].mean()
        med_hp_awpa = hp_sub['absolute_wpa_pct'].median()
        std_hp_awpa = hp_sub['absolute_wpa_pct'].std()
        p75_hp_awpa = hp_sub['absolute_wpa_pct'].quantile(0.75)

        m_nh_awpa = nh_sub['absolute_wpa_pct'].mean()
        med_nh_awpa = nh_sub['absolute_wpa_pct'].median()
        std_nh_awpa = nh_sub['absolute_wpa_pct'].std()
        p75_nh_awpa = nh_sub['absolute_wpa_pct'].quantile(0.75)

        awpa_diff = m_hp_awpa - m_nh_awpa
        ci_wpa_l, ci_wpa_u = compute_bootstrap_ci_diff(sub, hp_col, 'absolute_wpa_pct')

        pr_wpa = calc_pearsonr(sub[z_col], sub['absolute_wpa_pct'])
        sp_wpa = calc_spearmanr(sub[z_col], sub['absolute_wpa_pct'])

        wpa_rows.append({
            'dimension': dim,
            'subgroup': name,
            'total_deliveries': n_tot,
            'hp_deliveries': n_hp,
            'hp_capture_pct': round(pct_hp, 2),
            'mean_signed_wpa_hp': round(m_hp_swpa, 2),
            'median_signed_wpa_hp': round(med_hp_swpa, 2),
            'mean_signed_wpa_non_hp': round(m_nh_swpa, 2),
            'median_signed_wpa_non_hp': round(med_nh_swpa, 2),
            'mean_absolute_wpa_all': round(m_all_awpa, 2),
            'median_absolute_wpa_all': round(med_all_awpa, 2),
            'mean_absolute_wpa_hp': round(m_hp_awpa, 2),
            'median_absolute_wpa_hp': round(med_hp_awpa, 2),
            'p75_absolute_wpa_hp': round(p75_hp_awpa, 2),
            'mean_absolute_wpa_non_hp': round(m_nh_awpa, 2),
            'median_absolute_wpa_non_hp': round(med_nh_awpa, 2),
            'p75_absolute_wpa_non_hp': round(p75_nh_awpa, 2),
            'abs_wpa_diff_hp_minus_nh': round(awpa_diff, 2),
            'ci_95_diff_lower': round(ci_wpa_l, 2),
            'ci_95_diff_upper': round(ci_wpa_u, 2),
            'pearson_r_z_abs_wpa': round(pr_wpa, 4),
            'spearman_rho_z_abs_wpa': round(sp_wpa, 4)
        })

    lev_summary_df = pd.DataFrame(lev_rows)
    lev_csv = OUTPUT_DIR / "pi_vs_leverage_summary.csv"
    lev_summary_df.to_csv(lev_csv, index=False)
    print(f"Saved PI vs Expected Leverage summary to {lev_csv}")

    wpa_summary_df = pd.DataFrame(wpa_rows)
    wpa_csv = OUTPUT_DIR / "pi_vs_actual_wpa_summary.csv"
    wpa_summary_df.to_csv(wpa_csv, index=False)
    print(f"Saved PI vs Actual WPA summary to {wpa_csv}")

    # -------------------------------------------------------------
    # 3. SECTION 5C: FOUR-QUADRANT ANALYSIS
    # -------------------------------------------------------------
    print("\nRunning Section 5C: Four-Quadrant Analysis...")
    # Baseline cutoff: Population Median Expected Leverage = 1.14%
    baseline_cutoff = 1.1436
    bat_df['is_high_leverage'] = bat_df['expected_leverage_pct'] >= baseline_cutoff
    bat_df['is_high_pi'] = bat_df['is_high_pressure_bat']

    def assign_quadrant(row):
        h_pi = row['is_high_pi']
        h_lev = row['is_high_leverage']
        if h_pi and h_lev: return 'Q1: High PI + High Leverage (True Clutch)'
        elif h_pi and not h_lev: return 'Q2: High PI + Low Leverage (Crisis Collapses)'
        elif not h_pi and h_lev: return 'Q3: Low PI + High Leverage (Tense Parity)'
        else: return 'Q4: Low PI + Low Leverage (Routine Play)'

    bat_df['quadrant'] = bat_df.apply(assign_quadrant, axis=1)

    quad_rows = []
    tot_bat = len(bat_df)

    for q_name in [
        'Q1: High PI + High Leverage (True Clutch)',
        'Q2: High PI + Low Leverage (Crisis Collapses)',
        'Q3: Low PI + High Leverage (Tense Parity)',
        'Q4: Low PI + Low Leverage (Routine Play)'
    ]:
        q_sub = bat_df[bat_df['quadrant'] == q_name]
        n_q = len(q_sub)
        pct_q = (n_q / tot_bat) * 100.0

        pct_inn1 = (q_sub['innings'] == 1).mean() * 100.0
        pct_inn2 = (q_sub['innings'] == 2).mean() * 100.0
        pct_pp = (q_sub['phase'] == 'PP').mean() * 100.0
        pct_mo = (q_sub['phase'] == 'Middle').mean() * 100.0
        pct_do = (q_sub['phase'] == 'Death').mean() * 100.0

        mean_w = q_sub['wickets_before'].mean()
        mean_crr = q_sub['current_run_rate'].mean()
        mean_wp = q_sub['wp_before'].mean() * 100.0
        med_wp = q_sub['wp_before'].median() * 100.0

        mean_lev = q_sub['expected_leverage_pct'].mean()
        med_lev = q_sub['expected_leverage_pct'].median()
        mean_swpa = q_sub['wpa_pct'].mean()
        mean_awpa = q_sub['absolute_wpa_pct'].mean()
        med_awpa = q_sub['absolute_wpa_pct'].median()

        # Innings 2 specific RRR
        inn2_sub = q_sub[q_sub['innings'] == 2]
        mean_rrr = inn2_sub['required_run_rate'].mean() if len(inn2_sub) > 0 else np.nan

        quad_rows.append({
            'quadrant': q_name,
            'deliveries': n_q,
            'pct_of_total': round(pct_q, 2),
            'pct_innings_1': round(pct_inn1, 1),
            'pct_innings_2': round(pct_inn2, 1),
            'pct_powerplay': round(pct_pp, 1),
            'pct_middle_overs': round(pct_mo, 1),
            'pct_death_overs': round(pct_do, 1),
            'mean_wickets_lost': round(mean_w, 2),
            'mean_crr': round(mean_crr, 2),
            'mean_rrr_inn2': round(mean_rrr, 2) if pd.notna(mean_rrr) else np.nan,
            'mean_win_probability_pct': round(mean_wp, 2),
            'median_win_probability_pct': round(med_wp, 2),
            'mean_expected_leverage': round(mean_lev, 2),
            'median_expected_leverage': round(med_lev, 2),
            'mean_signed_wpa': round(mean_swpa, 2),
            'mean_absolute_wpa': round(mean_awpa, 2),
            'median_absolute_wpa': round(med_awpa, 2)
        })

    quad_df = pd.DataFrame(quad_rows)
    quad_csv = OUTPUT_DIR / "four_quadrant_analysis.csv"
    quad_df.to_csv(quad_csv, index=False)
    print(f"Saved 4-Quadrant Analysis table to {quad_csv}")

    # Cutoff Sensitivity Analysis
    print("Running Cutoff Sensitivity Analysis across 5 thresholds...")
    sens_rows = []
    cutoffs = [1.00, 1.1436, 1.20, 1.3379, 1.5120]
    cutoff_labels = ['1.00% (Permissive)', '1.14% (Median)', '1.20% (Moderate)', '1.34% (Mean)', '1.51% (75th Percentile)']

    for cut_val, cut_lbl in zip(cutoffs, cutoff_labels):
        h_lev = bat_df['expected_leverage_pct'] >= cut_val
        h_pi = bat_df['is_high_pi']

        q1 = (h_pi & h_lev).sum()
        q2 = (h_pi & ~h_lev).sum()
        q3 = (~h_pi & h_lev).sum()
        q4 = (~h_pi & ~h_lev).sum()

        sens_rows.append({
            'cutoff_label': cut_lbl,
            'cutoff_value': round(cut_val, 4),
            'q1_count': q1,
            'q1_pct': round(q1 / tot_bat * 100, 2),
            'q2_count': q2,
            'q2_pct': round(q2 / tot_bat * 100, 2),
            'q3_count': q3,
            'q3_pct': round(q3 / tot_bat * 100, 2),
            'q4_count': q4,
            'q4_pct': round(q4 / tot_bat * 100, 2),
            'q1_q2_ratio': round(q1 / max(1, q2), 2),
            'high_lev_share_in_hp_pct': round((q1 / max(1, q1 + q2)) * 100, 2)
        })

    sens_df = pd.DataFrame(sens_rows)
    sens_csv = OUTPUT_DIR / "four_quadrant_cutoff_sensitivity.csv"
    sens_df.to_csv(sens_csv, index=False)
    print(f"Saved Cutoff Sensitivity table to {sens_csv}")

    # -------------------------------------------------------------
    # 4. SECTION 5D: BATTING POSITION ANALYSIS
    # -------------------------------------------------------------
    print("\nRunning Section 5D: Batting Position Analysis (Positions 1 to 11)...")
    pos_rows = []

    for pos in range(1, 12):
        sub = bat_df[bat_df['batting_order'] == pos]
        n_p = len(sub)
        n_hp = sub['is_high_pi'].sum()
        pct_hp = (n_hp / n_p) * 100.0

        m_lev = sub['expected_leverage_pct'].mean()
        med_lev = sub['expected_leverage_pct'].median()
        p25_lev = sub['expected_leverage_pct'].quantile(0.25)
        p75_lev = sub['expected_leverage_pct'].quantile(0.75)

        m_swpa = sub['wpa_pct'].mean()
        m_awpa = sub['absolute_wpa_pct'].mean()
        med_awpa = sub['absolute_wpa_pct'].median()

        # Mean leverage within HP deliveries
        m_lev_hp = sub[sub['is_high_pi']]['expected_leverage_pct'].mean() if n_hp > 0 else np.nan
        m_lev_nh = sub[~sub['is_high_pi']]['expected_leverage_pct'].mean()

        # Matched PI subset: deliveries where Z is near threshold (Z in [0.5, 1.5])
        matched_z = sub[(sub['batting_z_score'] >= 0.5) & (sub['batting_z_score'] <= 1.5)]
        m_lev_matched = matched_z['expected_leverage_pct'].mean() if len(matched_z) > 0 else np.nan

        pos_rows.append({
            'batting_position': pos,
            'role': get_role(pos),
            'deliveries': n_p,
            'hp_deliveries': n_hp,
            'hp_capture_pct': round(pct_hp, 2),
            'mean_expected_leverage': round(m_lev, 2),
            'median_expected_leverage': round(med_lev, 2),
            'iqr_expected_leverage': f"{p25_lev:.2f}-{p75_lev:.2f}",
            'mean_signed_wpa': round(m_swpa, 2),
            'mean_absolute_wpa': round(m_awpa, 2),
            'median_absolute_wpa': round(med_awpa, 2),
            'mean_leverage_in_hp': round(m_lev_hp, 2) if pd.notna(m_lev_hp) else np.nan,
            'mean_leverage_in_non_hp': round(m_lev_nh, 2),
            'mean_leverage_at_matched_z_05_15': round(m_lev_matched, 2) if pd.notna(m_lev_matched) else np.nan
        })

    pos_df = pd.DataFrame(pos_rows)
    pos_csv = OUTPUT_DIR / "batting_position_wpa_leverage.csv"
    pos_df.to_csv(pos_csv, index=False)
    print(f"Saved Batting Position Analysis table to {pos_csv}")

    # -------------------------------------------------------------
    # 5. SECTION 5E: BOWLING PHASE ANALYSIS
    # -------------------------------------------------------------
    print("\nRunning Section 5E: Bowling Phase Analysis (Powerplay, Middle, Death)...")
    bowl_rows = []
    tot_bowl = len(bowl_df)

    for ph in ['PP', 'Middle', 'Death']:
        sub = bowl_df[bowl_df['phase'] == ph]
        n_b = len(sub)
        n_hp = sub['is_high_pressure_bowl'].sum()
        pct_hp = (n_hp / n_b) * 100.0

        m_lev = sub['expected_leverage_pct'].mean()
        med_lev = sub['expected_leverage_pct'].median()
        p25_lev = sub['expected_leverage_pct'].quantile(0.25)
        p75_lev = sub['expected_leverage_pct'].quantile(0.75)

        # Bowler WPA (-wpa)
        m_bwpa = (sub['bowler_wpa'] * 100.0).mean()
        med_bwpa = (sub['bowler_wpa'] * 100.0).median()
        m_bawpa = sub['absolute_wpa_pct'].mean()
        med_bawpa = sub['absolute_wpa_pct'].median()

        # High Leverage overlap (expected leverage >= baseline cutoff 1.14%)
        h_lev_count = (sub['expected_leverage_pct'] >= baseline_cutoff).sum()
        pct_h_lev = (h_lev_count / n_b) * 100.0

        overlap_count = (sub['is_high_pressure_bowl'] & (sub['expected_leverage_pct'] >= baseline_cutoff)).sum()
        pct_overlap_in_hp = (overlap_count / max(1, n_hp)) * 100.0
        pct_overlap_in_h_lev = (overlap_count / max(1, h_lev_count)) * 100.0

        bowl_rows.append({
            'bowling_phase': ph,
            'total_legal_balls': n_b,
            'pct_of_all_balls': round(n_b / tot_bowl * 100, 2),
            'hp_bowling_balls': n_hp,
            'hp_bowling_capture_pct': round(pct_hp, 2),
            'high_leverage_balls_count': h_lev_count,
            'high_leverage_pct': round(pct_h_lev, 2),
            'hp_and_high_leverage_overlap_count': overlap_count,
            'overlap_pct_of_hp': round(pct_overlap_in_hp, 2),
            'overlap_pct_of_high_leverage': round(pct_overlap_in_h_lev, 2),
            'mean_expected_leverage': round(m_lev, 2),
            'median_expected_leverage': round(med_lev, 2),
            'iqr_expected_leverage': f"{p25_lev:.2f}-{p75_lev:.2f}",
            'mean_bowler_wpa': round(m_bwpa, 3),
            'median_bowler_wpa': round(med_bwpa, 3),
            'mean_absolute_wpa': round(m_bawpa, 2),
            'median_absolute_wpa': round(med_bawpa, 2)
        })

    bowl_phase_df = pd.DataFrame(bowl_rows)
    bowl_phase_csv = OUTPUT_DIR / "bowling_phase_wpa_leverage.csv"
    bowl_phase_df.to_csv(bowl_phase_csv, index=False)
    print(f"Saved Bowling Phase Analysis table to {bowl_phase_csv}")

    print(f"\nStep 02 completed in {time.time() - t0:.2f} seconds.")


if __name__ == "__main__":
    main()
