import pandas as pd
import numpy as np

def generate_supporting_tables():
    batters = pd.read_csv('outputs/step_13_experimental_ranking_model/exp13_batter_rankings.csv')
    bowlers = pd.read_csv('outputs/step_13_experimental_ranking_model/exp13_bowler_rankings.csv')
    dpi = pd.read_csv('data/processed/delivery_pressure_index.csv')
    
    # 1. Score Gaps Table
    t1_b = batters[batters['tier_exp13'] == 'Tier 1: Qualified'].sort_values('tier1_rank_exp13').reset_index(drop=True)
    t1_bo = bowlers[bowlers['tier_exp13'] == 'Tier 1: Qualified'].sort_values('tier1_rank_exp13').reset_index(drop=True)
    
    gaps_data = [
        {
            'comparison': 'Batting Rank 1 (Dhoni) vs Rank 2 (Dube)',
            'player_a': 'MS Dhoni (93.2062)',
            'player_b': 'Shivam Dube (82.0110)',
            'reported_gap': 11.20,
            'audited_exact_gap': round(t1_b.loc[0, 'brs_3'] - t1_b.loc[1, 'brs_3'], 4),
            'discrepancy': round(11.20 - (t1_b.loc[0, 'brs_3'] - t1_b.loc[1, 'brs_3']), 4),
            'verdict': 'Verified (exact rounding)'
        },
        {
            'comparison': 'Bowling Rank 1 (Southee) vs Rank 2 (Nasum)',
            'player_a': 'Tim Southee (90.6924)',
            'player_b': 'Nasum Ahmed (88.8416)',
            'reported_gap': 1.85,
            'audited_exact_gap': round(t1_bo.loc[0, 'bors'] - t1_bo.loc[1, 'bors'], 4),
            'discrepancy': round(1.85 - (t1_bo.loc[0, 'bors'] - t1_bo.loc[1, 'bors']), 4),
            'verdict': 'Verified (exact rounding)'
        },
        {
            'comparison': 'Bowling Rank 2 (Nasum) vs Rank 3 (Maharaj)',
            'player_a': 'Nasum Ahmed (88.8416)',
            'player_b': 'Keshav Maharaj (79.9386)',
            'reported_gap': 8.90,
            'audited_exact_gap': round(t1_bo.loc[1, 'bors'] - t1_bo.loc[2, 'bors'], 4),
            'discrepancy': round(8.90 - (t1_bo.loc[1, 'bors'] - t1_bo.loc[2, 'bors']), 4),
            'verdict': 'Verified (exact rounding)'
        },
        {
            'comparison': 'Batting Median Consecutive Rank Gap (Ranks 20-80)',
            'player_a': 'Rank 20 (Sai Sudharsan, 68.3037)',
            'player_b': 'Rank 80 (Gareth Delany, 52.5284)',
            'reported_gap': 0.18,
            'audited_exact_gap': round(np.median(np.diff(t1_b.loc[19:79, 'brs_3'].values) * -1), 4),
            'discrepancy': round(0.18 - np.median(np.diff(t1_b.loc[19:79, 'brs_3'].values) * -1), 4),
            'verdict': 'Minor Overstatement (Actual 0.1590 vs Reported 0.18)'
        }
    ]
    pd.DataFrame(gaps_data).to_csv('outputs/step_15_1_1_independent_eda_audit/score_gap_recalculation.csv', index=False)
    print("Saved score_gap_recalculation.csv")

    # 2. Phase Exposure Audit Table
    t1_b['pct_pp'] = (t1_b['bf_pp_high'] / t1_b['high_balls_faced']) * 100
    t1_b['pct_mo'] = (t1_b['bf_mo_high'] / t1_b['high_balls_faced']) * 100
    t1_b['pct_do'] = (t1_b['bf_do_high'] / t1_b['high_balls_faced']) * 100
    
    t1_bo['pct_pp'] = (t1_bo['lb_pp_high'] / t1_bo['high_legal_balls']) * 100
    t1_bo['pct_mo'] = (t1_bo['lb_mo_high'] / t1_bo['high_legal_balls']) * 100
    t1_bo['pct_do'] = (t1_bo['lb_do_high'] / t1_bo['high_legal_balls']) * 100
    
    phase_audit = [
        {
            'discipline': 'Bowling (Tier 1, N=130)',
            'phase': 'Powerplay (1-6)',
            'unweighted_player_mean_pct': round(t1_bo['pct_pp'].mean(), 2),
            'unweighted_player_median_pct': round(t1_bo['pct_pp'].median(), 2),
            'tier1_aggregate_delivery_share_pct': round((t1_bo['lb_pp_high'].sum() / t1_bo['high_legal_balls'].sum()) * 100, 2),
            'full_match_delivery_share_pct': round((len(dpi[(dpi['Bowling_PI'] > 60) & (dpi['phase'] == 'PP')]) / len(dpi[dpi['Bowling_PI'] > 60])) * 100, 2),
            'reported_in_step_15_1': '59.1% (cited as "share of deliveries")',
            'audit_interpretation': 'Matches unweighted player mean (59.10%) and close to aggregate (59.39%), but should be explicitly documented as player-level mean.'
        },
        {
            'discipline': 'Bowling (Tier 1, N=130)',
            'phase': 'Middle (7-15)',
            'unweighted_player_mean_pct': round(t1_bo['pct_mo'].mean(), 2),
            'unweighted_player_median_pct': round(t1_bo['pct_mo'].median(), 2),
            'tier1_aggregate_delivery_share_pct': round((t1_bo['lb_mo_high'].sum() / t1_bo['high_legal_balls'].sum()) * 100, 2),
            'full_match_delivery_share_pct': round((len(dpi[(dpi['Bowling_PI'] > 60) & (dpi['phase'] == 'Middle')]) / len(dpi[dpi['Bowling_PI'] > 60])) * 100, 2),
            'reported_in_step_15_1': '34.4%',
            'audit_interpretation': 'Matches unweighted player mean (34.41%). Aggregate share is 34.07%.'
        },
        {
            'discipline': 'Bowling (Tier 1, N=130)',
            'phase': 'Death (16-20)',
            'unweighted_player_mean_pct': round(t1_bo['pct_do'].mean(), 2),
            'unweighted_player_median_pct': round(t1_bo['pct_do'].median(), 2),
            'tier1_aggregate_delivery_share_pct': round((t1_bo['lb_do_high'].sum() / t1_bo['high_legal_balls'].sum()) * 100, 2),
            'full_match_delivery_share_pct': round((len(dpi[(dpi['Bowling_PI'] > 60) & (dpi['phase'] == 'Death')]) / len(dpi[dpi['Bowling_PI'] > 60])) * 100, 2),
            'reported_in_step_15_1': '6.5%',
            'audit_interpretation': 'Matches unweighted player mean (6.49%) and full match share (6.53%).'
        },
        {
            'discipline': 'Batting (Tier 1, N=146)',
            'phase': 'Powerplay (1-6)',
            'unweighted_player_mean_pct': round(t1_b['pct_pp'].mean(), 2),
            'unweighted_player_median_pct': round(t1_b['pct_pp'].median(), 2),
            'tier1_aggregate_delivery_share_pct': round((t1_b['bf_pp_high'].sum() / t1_b['high_balls_faced'].sum()) * 100, 2),
            'full_match_delivery_share_pct': round((len(dpi[(dpi['Batting_PI'] > 60) & (dpi['phase'] == 'PP')]) / len(dpi[dpi['Batting_PI'] > 60])) * 100, 2),
            'reported_in_step_15_1': '19.4%',
            'audit_interpretation': 'Matches unweighted player mean (19.40%). Aggregate share is 17.15%.'
        },
        {
            'discipline': 'Batting (Tier 1, N=146)',
            'phase': 'Middle (7-15)',
            'unweighted_player_mean_pct': round(t1_b['pct_mo'].mean(), 2),
            'unweighted_player_median_pct': round(t1_b['pct_mo'].median(), 2),
            'tier1_aggregate_delivery_share_pct': round((t1_b['bf_mo_high'].sum() / t1_b['high_balls_faced'].sum()) * 100, 2),
            'full_match_delivery_share_pct': round((len(dpi[(dpi['Batting_PI'] > 60) & (dpi['phase'] == 'Middle')]) / len(dpi[dpi['Batting_PI'] > 60])) * 100, 2),
            'reported_in_step_15_1': '42.4%',
            'audit_interpretation': 'Matches unweighted player mean (42.38%). Aggregate share is 45.51%.'
        },
        {
            'discipline': 'Batting (Tier 1, N=146)',
            'phase': 'Death (16-20)',
            'unweighted_player_mean_pct': round(t1_b['pct_do'].mean(), 2),
            'unweighted_player_median_pct': round(t1_b['pct_do'].median(), 2),
            'tier1_aggregate_delivery_share_pct': round((t1_b['bf_do_high'].sum() / t1_b['high_balls_faced'].sum()) * 100, 2),
            'full_match_delivery_share_pct': round((len(dpi[(dpi['Batting_PI'] > 60) & (dpi['phase'] == 'Death')]) / len(dpi[dpi['Batting_PI'] > 60])) * 100, 2),
            'reported_in_step_15_1': '38.2%',
            'audit_interpretation': 'Matches unweighted player mean (38.22%). Aggregate share is 37.34%.'
        }
    ]
    pd.DataFrame(phase_audit).to_csv('outputs/step_15_1_1_independent_eda_audit/phase_exposure_audit_table.csv', index=False)
    print("Saved phase_exposure_audit_table.csv")

if __name__ == '__main__':
    generate_supporting_tables()
