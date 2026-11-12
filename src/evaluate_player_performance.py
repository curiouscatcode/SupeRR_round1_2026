"""
Player Performance Evaluation Under Pressure (Step 5)
=====================================================

This module evaluates the performance of individual batters and bowlers across:
- Overall Match Play
- Low / Moderate Pressure (PI <= 60.0)
- High / Very High Pressure (PI > 60.0)
- Phase-wise Segments (Powerplay, Middle Overs, Death Overs)

Strict Rules Followed:
1. Excludes all 233 deliveries where `runs_required <= 0`.
2. Preserves first-innings deliveries.
3. Preserves live second-innings deliveries from flagged deficit matches with `is_target_understated`.
4. Bowler wickets credited strictly to standard bowler dismissals (Caught, Bowled, LBW, Stump, Hit Wicket).
   Non-bowler dismissals (RunOut, Retire Out, Obstructing field) are excluded.
5. Batter metrics use batter runs and balls faced (not team runs or legal balls).
6. Preserves unique player IDs and names.

Outputs:
- data/processed/batter_performance.csv
- data/processed/bowler_performance.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd


# The 38 matches exhibiting first-innings target reconstruction deficits
FLAGGED_TARGET_UNDERSTATED_MATCHES = [
    14096, 14114, 14133, 15189, 16659, 16660, 16664, 19691, 20187, 24354, 
    28958, 30074, 31240, 31250, 31265, 31267, 33806, 37014, 37351, 37555, 
    40706, 40742, 40764, 41508, 45903, 46312, 47982, 48592, 50129, 50358, 
    50361, 50597, 54408, 55078, 28962, 29926, 32135, 37895
]

BOWLER_WICKET_TYPES = ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']


def safe_div(numerator, denominator, multiplier=1.0, decimals=2):
    """Safely divide numpy arrays or series, returning NaN when denominator is 0."""
    with np.errstate(divide='ignore', invalid='ignore'):
        res = (numerator / denominator) * multiplier
        if isinstance(res, (pd.Series, np.ndarray)):
            res = np.where(denominator > 0, res, np.nan)
        elif denominator == 0:
            res = np.nan
        return np.round(res, decimals)


def evaluate_batters(df: pd.DataFrame) -> pd.DataFrame:
    """Compute comprehensive batter performance metrics."""
    print("Evaluating batter performance...")

    # Delivery-level indicators
    df['is_boundary'] = (df['is_four'] | df['is_six']).astype(int)
    df['is_dot_ball_faced'] = (df['is_batter_ball_faced'] & (df['runs'] == 0)).astype(int)
    df['is_striker_out'] = (df['is_wicket'] & (df['dismissed_player_id'] == df['striker_id'])).astype(int)
    df['is_bf_int'] = df['is_batter_ball_faced'].astype(int)

    # Boolean pressure filters
    p_high = df['Batting_PI'] > 60.0
    p_low = df['Batting_PI'] <= 60.0

    # Phase filters
    is_pp = df['phase'] == 'PP'
    is_mo = df['phase'] == 'Middle'
    is_do = df['phase'] == 'Death'

    # Filtered columns for aggregation
    # Overall
    df['runs_all'] = df['runs']
    df['bf_all'] = df['is_bf_int']
    df['fours_all'] = df['is_four'].astype(int)
    df['sixes_all'] = df['is_six'].astype(int)
    df['bnd_all'] = df['is_boundary']
    df['dot_all'] = df['is_dot_ball_faced']
    df['out_all'] = df['is_striker_out']

    # Low / Moderate
    df['runs_low'] = np.where(p_low, df['runs'], 0)
    df['bf_low'] = np.where(p_low, df['is_bf_int'], 0)
    df['fours_low'] = np.where(p_low, df['is_four'], 0)
    df['sixes_low'] = np.where(p_low, df['is_six'], 0)
    df['bnd_low'] = np.where(p_low, df['is_boundary'], 0)
    df['dot_low'] = np.where(p_low, df['is_dot_ball_faced'], 0)
    df['out_low'] = np.where(p_low, df['is_striker_out'], 0)

    # High / Very High
    df['runs_high'] = np.where(p_high, df['runs'], 0)
    df['bf_high'] = np.where(p_high, df['is_bf_int'], 0)
    df['fours_high'] = np.where(p_high, df['is_four'], 0)
    df['sixes_high'] = np.where(p_high, df['is_six'], 0)
    df['bnd_high'] = np.where(p_high, df['is_boundary'], 0)
    df['dot_high'] = np.where(p_high, df['is_dot_ball_faced'], 0)
    df['out_high'] = np.where(p_high, df['is_striker_out'], 0)

    # Phase-wise splits
    for p_name, p_mask in [('pp', is_pp), ('mo', is_mo), ('do', is_do)]:
        df[f'runs_{p_name}'] = np.where(p_mask, df['runs'], 0)
        df[f'bf_{p_name}'] = np.where(p_mask, df['is_bf_int'], 0)
        df[f'bnd_{p_name}'] = np.where(p_mask, df['is_boundary'], 0)
        df[f'dot_{p_name}'] = np.where(p_mask, df['is_dot_ball_faced'], 0)
        df[f'out_{p_name}'] = np.where(p_mask, df['is_striker_out'], 0)

        df[f'runs_{p_name}_high'] = np.where(p_mask & p_high, df['runs'], 0)
        df[f'bf_{p_name}_high'] = np.where(p_mask & p_high, df['is_bf_int'], 0)
        df[f'runs_{p_name}_low'] = np.where(p_mask & p_low, df['runs'], 0)
        df[f'bf_{p_name}_low'] = np.where(p_mask & p_low, df['is_bf_int'], 0)

    # Sensitivity balls faced in flagged matches
    df['bf_target_understated'] = np.where(df['is_target_understated'], df['is_bf_int'], 0)

    # Group by striker
    agg_funcs = {
        'striker_name': 'first',
        'match_id': 'nunique',
        'innings_ball_num': 'count',
        'bf_target_understated': 'sum',
        
        # Overall
        'runs_all': 'sum', 'bf_all': 'sum', 'fours_all': 'sum', 'sixes_all': 'sum', 
        'bnd_all': 'sum', 'dot_all': 'sum', 'out_all': 'sum',
        
        # Low / Moderate
        'runs_low': 'sum', 'bf_low': 'sum', 'fours_low': 'sum', 'sixes_low': 'sum',
        'bnd_low': 'sum', 'dot_low': 'sum', 'out_low': 'sum',
        
        # High / Very High
        'runs_high': 'sum', 'bf_high': 'sum', 'fours_high': 'sum', 'sixes_high': 'sum',
        'bnd_high': 'sum', 'dot_high': 'sum', 'out_high': 'sum',

        # Phases
        'runs_pp': 'sum', 'bf_pp': 'sum', 'bnd_pp': 'sum', 'dot_pp': 'sum', 'out_pp': 'sum',
        'runs_pp_high': 'sum', 'bf_pp_high': 'sum', 'runs_pp_low': 'sum', 'bf_pp_low': 'sum',

        'runs_mo': 'sum', 'bf_mo': 'sum', 'bnd_mo': 'sum', 'dot_mo': 'sum', 'out_mo': 'sum',
        'runs_mo_high': 'sum', 'bf_mo_high': 'sum', 'runs_mo_low': 'sum', 'bf_mo_low': 'sum',

        'runs_do': 'sum', 'bf_do': 'sum', 'bnd_do': 'sum', 'dot_do': 'sum', 'out_do': 'sum',
        'runs_do_high': 'sum', 'bf_do_high': 'sum', 'runs_do_low': 'sum', 'bf_do_low': 'sum',
    }

    b_df = df.groupby('striker_id').agg(agg_funcs).reset_index()

    # Calculate match count and innings count accurately
    # Number of distinct (match_id, innings) where batter faced at least one ball
    inn_count = (
        df[df['is_bf_int'] == 1]
        .groupby('striker_id')[['match_id', 'innings']]
        .apply(lambda x: len(x.drop_duplicates()))
        .reset_index(name='innings_batted')
    )
    b_df = b_df.merge(inn_count, on='striker_id', how='left')
    b_df['innings_batted'] = b_df['innings_batted'].fillna(0).astype(int)

    # Rename identification columns
    b_df = b_df.rename(columns={
        'striker_id': 'player_id',
        'striker_name': 'player_name',
        'match_id': 'matches_played',
        'innings_ball_num': 'total_deliveries_faced'
    })

    # Rate calculations - Overall
    b_df['strike_rate'] = safe_div(b_df['runs_all'], b_df['bf_all'], 100.0)
    b_df['boundary_pct'] = safe_div(b_df['bnd_all'], b_df['bf_all'], 100.0)
    b_df['dot_pct'] = safe_div(b_df['dot_all'], b_df['bf_all'], 100.0)
    b_df['dismissal_pct'] = safe_div(b_df['out_all'], b_df['bf_all'], 100.0)
    b_df['batting_average'] = safe_div(b_df['runs_all'], b_df['out_all'])

    # Rate calculations - Low / Moderate Pressure
    b_df['low_mod_strike_rate'] = safe_div(b_df['runs_low'], b_df['bf_low'], 100.0)
    b_df['low_mod_boundary_pct'] = safe_div(b_df['bnd_low'], b_df['bf_low'], 100.0)
    b_df['low_mod_dot_pct'] = safe_div(b_df['dot_low'], b_df['bf_low'], 100.0)
    b_df['low_mod_dismissal_pct'] = safe_div(b_df['out_low'], b_df['bf_low'], 100.0)
    b_df['low_mod_batting_avg'] = safe_div(b_df['runs_low'], b_df['out_low'])

    # Rate calculations - High / Very High Pressure
    b_df['high_strike_rate'] = safe_div(b_df['runs_high'], b_df['bf_high'], 100.0)
    b_df['high_boundary_pct'] = safe_div(b_df['bnd_high'], b_df['bf_high'], 100.0)
    b_df['high_dot_pct'] = safe_div(b_df['dot_high'], b_df['bf_high'], 100.0)
    b_df['high_dismissal_pct'] = safe_div(b_df['out_high'], b_df['bf_high'], 100.0)
    b_df['high_batting_avg'] = safe_div(b_df['runs_high'], b_df['out_high'])

    # Pressure differentials
    b_df['strike_rate_delta'] = np.round(b_df['high_strike_rate'] - b_df['low_mod_strike_rate'], 2)
    b_df['boundary_pct_delta'] = np.round(b_df['high_boundary_pct'] - b_df['low_mod_boundary_pct'], 2)
    b_df['dot_pct_delta'] = np.round(b_df['high_dot_pct'] - b_df['low_mod_dot_pct'], 2)

    # Phase rate calculations
    b_df['pp_strike_rate'] = safe_div(b_df['runs_pp'], b_df['bf_pp'], 100.0)
    b_df['pp_boundary_pct'] = safe_div(b_df['bnd_pp'], b_df['bf_pp'], 100.0)
    b_df['pp_dot_pct'] = safe_div(b_df['dot_pp'], b_df['bf_pp'], 100.0)
    b_df['pp_high_strike_rate'] = safe_div(b_df['runs_pp_high'], b_df['bf_pp_high'], 100.0)
    b_df['pp_low_strike_rate'] = safe_div(b_df['runs_pp_low'], b_df['bf_pp_low'], 100.0)

    b_df['mo_strike_rate'] = safe_div(b_df['runs_mo'], b_df['bf_mo'], 100.0)
    b_df['mo_boundary_pct'] = safe_div(b_df['bnd_mo'], b_df['bf_mo'], 100.0)
    b_df['mo_dot_pct'] = safe_div(b_df['dot_mo'], b_df['bf_mo'], 100.0)
    b_df['mo_high_strike_rate'] = safe_div(b_df['runs_mo_high'], b_df['bf_mo_high'], 100.0)
    b_df['mo_low_strike_rate'] = safe_div(b_df['runs_mo_low'], b_df['bf_mo_low'], 100.0)

    b_df['do_strike_rate'] = safe_div(b_df['runs_do'], b_df['bf_do'], 100.0)
    b_df['do_boundary_pct'] = safe_div(b_df['bnd_do'], b_df['bf_do'], 100.0)
    b_df['do_dot_pct'] = safe_div(b_df['dot_do'], b_df['bf_do'], 100.0)
    b_df['do_high_strike_rate'] = safe_div(b_df['runs_do_high'], b_df['bf_do_high'], 100.0)
    b_df['do_low_strike_rate'] = safe_div(b_df['runs_do_low'], b_df['bf_do_low'], 100.0)

    # Clean rename for readability
    rename_cols = {
        'runs_all': 'total_runs', 'bf_all': 'total_balls_faced', 'fours_all': 'total_fours', 
        'sixes_all': 'total_sixes', 'bnd_all': 'total_boundaries', 'dot_all': 'total_dot_balls', 
        'out_all': 'total_dismissals',
        
        'runs_low': 'low_mod_runs', 'bf_low': 'low_mod_balls_faced', 'fours_low': 'low_mod_fours', 
        'sixes_low': 'low_mod_sixes', 'bnd_low': 'low_mod_boundaries', 'dot_low': 'low_mod_dot_balls', 
        'out_low': 'low_mod_dismissals',
        
        'runs_high': 'high_runs', 'bf_high': 'high_balls_faced', 'fours_high': 'high_fours', 
        'sixes_high': 'high_sixes', 'bnd_high': 'high_boundaries', 'dot_high': 'high_dot_balls', 
        'out_high': 'high_dismissals',

        'runs_pp': 'pp_runs', 'bf_pp': 'pp_balls_faced', 'bnd_pp': 'pp_boundaries', 'dot_pp': 'pp_dot_balls', 'out_pp': 'pp_dismissals',
        'runs_mo': 'mo_runs', 'bf_mo': 'mo_balls_faced', 'bnd_mo': 'mo_boundaries', 'dot_mo': 'mo_dot_balls', 'out_mo': 'mo_dismissals',
        'runs_do': 'do_runs', 'bf_do': 'do_balls_faced', 'bnd_do': 'do_boundaries', 'dot_do': 'do_dot_balls', 'out_do': 'do_dismissals',

        'bf_target_understated': 'target_understated_balls_faced'
    }
    b_df = b_df.rename(columns=rename_cols)

    # Sort descending by total runs
    b_df = b_df.sort_values('total_runs', ascending=False).reset_index(drop=True)
    return b_df


def evaluate_bowlers(df: pd.DataFrame) -> pd.DataFrame:
    """Compute comprehensive bowler performance metrics."""
    print("Evaluating bowler performance...")

    # Delivery-level indicators
    df['is_lb_int'] = df['is_legal_ball'].astype(int)
    df['is_bowler_wicket_int'] = (df['is_wicket'] & df['dismissal_type'].isin(BOWLER_WICKET_TYPES)).astype(int)
    df['is_bowler_dot_int'] = (df['bowler_runs_conceded'] == 0).astype(int)
    df['is_boundary_conceded'] = (df['is_four'] | df['is_six']).astype(int)

    # Pressure filters
    p_high = df['Bowling_PI'] > 60.0
    p_low = df['Bowling_PI'] <= 60.0

    # Phase filters
    is_pp = df['phase'] == 'PP'
    is_mo = df['phase'] == 'Middle'
    is_do = df['phase'] == 'Death'

    # Filtered columns for aggregation
    # Overall
    df['rc_all'] = df['bowler_runs_conceded']
    df['lb_all'] = df['is_lb_int']
    df['wk_all'] = df['is_bowler_wicket_int']
    df['dot_all'] = df['is_bowler_dot_int']
    df['bnd_all'] = df['is_boundary_conceded']
    df['fours_all'] = df['is_four'].astype(int)
    df['sixes_all'] = df['is_six'].astype(int)

    # Low / Moderate
    df['rc_low'] = np.where(p_low, df['bowler_runs_conceded'], 0)
    df['lb_low'] = np.where(p_low, df['is_lb_int'], 0)
    df['wk_low'] = np.where(p_low, df['is_bowler_wicket_int'], 0)
    df['dot_low'] = np.where(p_low, df['is_bowler_dot_int'], 0)
    df['bnd_low'] = np.where(p_low, df['is_boundary_conceded'], 0)

    # High / Very High
    df['rc_high'] = np.where(p_high, df['bowler_runs_conceded'], 0)
    df['lb_high'] = np.where(p_high, df['is_lb_int'], 0)
    df['wk_high'] = np.where(p_high, df['is_bowler_wicket_int'], 0)
    df['dot_high'] = np.where(p_high, df['is_bowler_dot_int'], 0)
    df['bnd_high'] = np.where(p_high, df['is_boundary_conceded'], 0)

    # Phase-wise splits
    for p_name, p_mask in [('pp', is_pp), ('mo', is_mo), ('do', is_do)]:
        df[f'rc_{p_name}'] = np.where(p_mask, df['bowler_runs_conceded'], 0)
        df[f'lb_{p_name}'] = np.where(p_mask, df['is_lb_int'], 0)
        df[f'wk_{p_name}'] = np.where(p_mask, df['is_bowler_wicket_int'], 0)
        df[f'dot_{p_name}'] = np.where(p_mask, df['is_bowler_dot_int'], 0)
        df[f'bnd_{p_name}'] = np.where(p_mask, df['is_boundary_conceded'], 0)

        df[f'rc_{p_name}_high'] = np.where(p_mask & p_high, df['bowler_runs_conceded'], 0)
        df[f'lb_{p_name}_high'] = np.where(p_mask & p_high, df['is_lb_int'], 0)
        df[f'wk_{p_name}_high'] = np.where(p_mask & p_high, df['is_bowler_wicket_int'], 0)

        df[f'rc_{p_name}_low'] = np.where(p_mask & p_low, df['bowler_runs_conceded'], 0)
        df[f'lb_{p_name}_low'] = np.where(p_mask & p_low, df['is_lb_int'], 0)
        df[f'wk_{p_name}_low'] = np.where(p_mask & p_low, df['is_bowler_wicket_int'], 0)

    # Sensitivity legal balls bowled in flagged matches
    df['lb_target_understated'] = np.where(df['is_target_understated'], df['is_lb_int'], 0)

    # Group by bowler
    agg_funcs = {
        'bowler_name': 'first',
        'match_id': 'nunique',
        'innings_ball_num': 'count',
        'lb_target_understated': 'sum',
        
        # Overall
        'rc_all': 'sum', 'lb_all': 'sum', 'wk_all': 'sum', 'dot_all': 'sum', 
        'bnd_all': 'sum', 'fours_all': 'sum', 'sixes_all': 'sum',
        
        # Low / Moderate
        'rc_low': 'sum', 'lb_low': 'sum', 'wk_low': 'sum', 'dot_low': 'sum', 'bnd_low': 'sum',
        
        # High / Very High
        'rc_high': 'sum', 'lb_high': 'sum', 'wk_high': 'sum', 'dot_high': 'sum', 'bnd_high': 'sum',

        # Phases
        'rc_pp': 'sum', 'lb_pp': 'sum', 'wk_pp': 'sum', 'dot_pp': 'sum', 'bnd_pp': 'sum',
        'rc_pp_high': 'sum', 'lb_pp_high': 'sum', 'wk_pp_high': 'sum',
        'rc_pp_low': 'sum', 'lb_pp_low': 'sum', 'wk_pp_low': 'sum',

        'rc_mo': 'sum', 'lb_mo': 'sum', 'wk_mo': 'sum', 'dot_mo': 'sum', 'bnd_mo': 'sum',
        'rc_mo_high': 'sum', 'lb_mo_high': 'sum', 'wk_mo_high': 'sum',
        'rc_mo_low': 'sum', 'lb_mo_low': 'sum', 'wk_mo_low': 'sum',

        'rc_do': 'sum', 'lb_do': 'sum', 'wk_do': 'sum', 'dot_do': 'sum', 'bnd_do': 'sum',
        'rc_do_high': 'sum', 'lb_do_high': 'sum', 'wk_do_high': 'sum',
        'rc_do_low': 'sum', 'lb_do_low': 'sum', 'wk_do_low': 'sum',
    }

    bw_df = df.groupby('bowler_id').agg(agg_funcs).reset_index()

    # Calculate innings count bowled
    inn_count_bowl = (
        df[df['is_lb_int'] == 1]
        .groupby('bowler_id')[['match_id', 'innings']]
        .apply(lambda x: len(x.drop_duplicates()))
        .reset_index(name='innings_bowled')
    )
    bw_df = bw_df.merge(inn_count_bowl, on='bowler_id', how='left')
    bw_df['innings_bowled'] = bw_df['innings_bowled'].fillna(0).astype(int)

    # Rename identification columns
    bw_df = bw_df.rename(columns={
        'bowler_id': 'player_id',
        'bowler_name': 'player_name',
        'match_id': 'matches_bowled',
        'innings_ball_num': 'total_deliveries_bowled'
    })

    # Rate calculations - Overall
    bw_df['total_overs'] = np.round(bw_df['lb_all'] / 6.0, 1)
    bw_df['economy_rate'] = safe_div(bw_df['rc_all'], bw_df['lb_all'], 6.0)
    bw_df['bowling_average'] = safe_div(bw_df['rc_all'], bw_df['wk_all'])
    bw_df['bowling_strike_rate'] = safe_div(bw_df['lb_all'], bw_df['wk_all'])
    bw_df['dot_pct'] = safe_div(bw_df['dot_all'], bw_df['lb_all'], 100.0)
    bw_df['boundary_pct'] = safe_div(bw_df['bnd_all'], bw_df['lb_all'], 100.0)

    # Rate calculations - Low / Moderate Pressure
    bw_df['low_mod_economy_rate'] = safe_div(bw_df['rc_low'], bw_df['lb_low'], 6.0)
    bw_df['low_mod_bowling_avg'] = safe_div(bw_df['rc_low'], bw_df['wk_low'])
    bw_df['low_mod_strike_rate'] = safe_div(bw_df['lb_low'], bw_df['wk_low'])
    bw_df['low_mod_dot_pct'] = safe_div(bw_df['dot_low'], bw_df['lb_low'], 100.0)
    bw_df['low_mod_boundary_pct'] = safe_div(bw_df['bnd_low'], bw_df['lb_low'], 100.0)

    # Rate calculations - High / Very High Pressure
    bw_df['high_economy_rate'] = safe_div(bw_df['rc_high'], bw_df['lb_high'], 6.0)
    bw_df['high_bowling_avg'] = safe_div(bw_df['rc_high'], bw_df['wk_high'])
    bw_df['high_strike_rate'] = safe_div(bw_df['lb_high'], bw_df['wk_high'])
    bw_df['high_dot_pct'] = safe_div(bw_df['dot_high'], bw_df['lb_high'], 100.0)
    bw_df['high_boundary_pct'] = safe_div(bw_df['high_boundaries_conceded' if 'high_boundaries_conceded' in bw_df else 'bnd_high'], bw_df['lb_high'], 100.0)

    # Pressure differentials
    bw_df['economy_rate_delta'] = np.round(bw_df['high_economy_rate'] - bw_df['low_mod_economy_rate'], 2)
    bw_df['dot_pct_delta'] = np.round(bw_df['high_dot_pct'] - bw_df['low_mod_dot_pct'], 2)
    bw_df['boundary_pct_delta'] = np.round(bw_df['high_boundary_pct'] - bw_df['low_mod_boundary_pct'], 2)

    # Phase rates
    bw_df['pp_economy_rate'] = safe_div(bw_df['rc_pp'], bw_df['lb_pp'], 6.0)
    bw_df['pp_dot_pct'] = safe_div(bw_df['dot_pp'], bw_df['lb_pp'], 100.0)
    bw_df['pp_boundary_pct'] = safe_div(bw_df['bnd_pp'], bw_df['lb_pp'], 100.0)
    bw_df['pp_high_economy_rate'] = safe_div(bw_df['rc_pp_high'], bw_df['lb_pp_high'], 6.0)
    bw_df['pp_low_economy_rate'] = safe_div(bw_df['rc_pp_low'], bw_df['lb_pp_low'], 6.0)

    bw_df['mo_economy_rate'] = safe_div(bw_df['rc_mo'], bw_df['lb_mo'], 6.0)
    bw_df['mo_dot_pct'] = safe_div(bw_df['dot_mo'], bw_df['lb_mo'], 100.0)
    bw_df['mo_boundary_pct'] = safe_div(bw_df['bnd_mo'], bw_df['lb_mo'], 100.0)
    bw_df['mo_high_economy_rate'] = safe_div(bw_df['rc_mo_high'], bw_df['lb_mo_high'], 6.0)
    bw_df['mo_low_economy_rate'] = safe_div(bw_df['rc_mo_low'], bw_df['lb_mo_low'], 6.0)

    bw_df['do_economy_rate'] = safe_div(bw_df['rc_do'], bw_df['lb_do'], 6.0)
    bw_df['do_dot_pct'] = safe_div(bw_df['dot_do'], bw_df['lb_do'], 100.0)
    bw_df['do_boundary_pct'] = safe_div(bw_df['bnd_do'], bw_df['lb_do'], 100.0)
    bw_df['do_high_economy_rate'] = safe_div(bw_df['rc_do_high'], bw_df['lb_do_high'], 6.0)
    bw_df['do_low_economy_rate'] = safe_div(bw_df['rc_do_low'], bw_df['lb_do_low'], 6.0)

    # Clean rename
    rename_cols = {
        'rc_all': 'total_runs_conceded', 'lb_all': 'total_legal_balls', 'wk_all': 'total_wickets',
        'dot_all': 'total_dot_balls', 'bnd_all': 'total_boundaries_conceded', 
        'fours_all': 'total_fours_conceded', 'sixes_all': 'total_sixes_conceded',

        'rc_low': 'low_mod_runs_conceded', 'lb_low': 'low_mod_legal_balls', 'wk_low': 'low_mod_wickets',
        'dot_low': 'low_mod_dot_balls', 'bnd_low': 'low_mod_boundaries_conceded',

        'rc_high': 'high_runs_conceded', 'lb_high': 'high_legal_balls', 'wk_high': 'high_wickets',
        'dot_high': 'high_dot_balls', 'bnd_high': 'high_boundaries_conceded',

        'rc_pp': 'pp_runs_conceded', 'lb_pp': 'pp_legal_balls', 'wk_pp': 'pp_wickets', 'dot_pp': 'pp_dot_balls', 'bnd_pp': 'pp_boundaries_conceded',
        'rc_mo': 'mo_runs_conceded', 'lb_mo': 'mo_legal_balls', 'wk_mo': 'mo_wickets', 'dot_mo': 'mo_dot_balls', 'bnd_mo': 'mo_boundaries_conceded',
        'rc_do': 'do_runs_conceded', 'lb_do': 'do_legal_balls', 'wk_do': 'do_wickets', 'dot_do': 'do_dot_balls', 'bnd_do': 'do_boundaries_conceded',

        'lb_target_understated': 'target_understated_legal_balls'
    }
    bw_df = bw_df.rename(columns=rename_cols)

    # Sort descending by wickets, then ascending by economy
    bw_df = bw_df.sort_values(by=['total_wickets', 'total_legal_balls'], ascending=[False, False]).reset_index(drop=True)
    return bw_df


def run_player_evaluation():
    input_path = Path('data/processed/delivery_pressure_index.csv')
    batter_out = Path('data/processed/batter_performance.csv')
    bowler_out = Path('data/processed/bowler_performance.csv')

    print(f"Loading delivery pressure index data from {input_path}...")
    df = pd.read_csv(input_path)
    total_raw_rows = len(df)
    print(f"Loaded {total_raw_rows:,} deliveries.")

    # 1. Apply data filtering: exclude all 233 deliveries where runs_required <= 0 in Innings 2
    is_target_reached_tail = (df['innings'] == 2) & (df['runs_required'] <= 0)
    num_excluded = is_target_reached_tail.sum()
    print(f"Excluding {num_excluded} second-innings target-reached deliveries (runs_required <= 0)...")
    assert num_excluded == 233, f"Expected 233 excluded deliveries, got {num_excluded}"

    clean_df = df[~is_target_reached_tail].copy()
    print(f"Clean active dataset retained: {len(clean_df):,} deliveries.")

    # 2. Add is_target_understated sensitivity flag
    clean_df['is_target_understated'] = (clean_df['innings'] == 2) & clean_df['match_id'].isin(FLAGGED_TARGET_UNDERSTATED_MATCHES)
    print(f"Deliveries flagged as target-understated: {clean_df['is_target_understated'].sum():,} / {len(clean_df):,}")

    # 3. Evaluate Batters
    batters_df = evaluate_batters(clean_df.copy())
    print(f"Evaluated {len(batters_df):,} unique batters.")

    # 4. Evaluate Bowlers
    bowlers_df = evaluate_bowlers(clean_df.copy())
    print(f"Evaluated {len(bowlers_df):,} unique bowlers.")

    # 5. Validation Assertions
    print("\nRunning rigorous verification checks against source data...")
    # Check 1: Batter runs sum
    source_batter_runs = clean_df['runs'].sum()
    eval_batter_runs = batters_df['total_runs'].sum()
    low_runs_sum = batters_df['low_mod_runs'].sum()
    high_runs_sum = batters_df['high_runs'].sum()
    assert eval_batter_runs == source_batter_runs, f"Batter runs mismatch! {eval_batter_runs} vs {source_batter_runs}"
    assert (low_runs_sum + high_runs_sum) == source_batter_runs, "Low + High batter runs do not equal total!"
    print(f"PASS: Batter runs perfectly conserved ({eval_batter_runs:,} runs: {low_runs_sum:,} low/mod + {high_runs_sum:,} high).")

    # Check 2: Batter balls faced sum
    source_balls_faced = clean_df['is_batter_ball_faced'].sum()
    eval_balls_faced = batters_df['total_balls_faced'].sum()
    low_bf_sum = batters_df['low_mod_balls_faced'].sum()
    high_bf_sum = batters_df['high_balls_faced'].sum()
    assert eval_balls_faced == source_balls_faced, f"Balls faced mismatch! {eval_balls_faced} vs {source_balls_faced}"
    assert (low_bf_sum + high_bf_sum) == source_balls_faced, "Low + High balls faced do not equal total!"
    print(f"PASS: Balls faced perfectly conserved ({eval_balls_faced:,} balls: {low_bf_sum:,} low/mod + {high_bf_sum:,} high).")

    # Check 3: Bowler runs conceded sum
    source_bowler_rc = clean_df['bowler_runs_conceded'].sum()
    eval_bowler_rc = bowlers_df['total_runs_conceded'].sum()
    low_rc_sum = bowlers_df['low_mod_runs_conceded'].sum()
    high_rc_sum = bowlers_df['high_runs_conceded'].sum()
    assert eval_bowler_rc == source_bowler_rc, f"Bowler runs conceded mismatch! {eval_bowler_rc} vs {source_bowler_rc}"
    assert (low_rc_sum + high_rc_sum) == source_bowler_rc, "Low + High bowler runs do not equal total!"
    print(f"PASS: Bowler runs conceded perfectly conserved ({eval_bowler_rc:,} runs: {low_rc_sum:,} low/mod + {high_rc_sum:,} high).")

    # Check 4: Bowler legal balls sum
    source_legal_balls = clean_df['is_legal_ball'].sum()
    eval_legal_balls = bowlers_df['total_legal_balls'].sum()
    low_lb_sum = bowlers_df['low_mod_legal_balls'].sum()
    high_lb_sum = bowlers_df['high_legal_balls'].sum()
    assert eval_legal_balls == source_legal_balls, f"Legal balls mismatch! {eval_legal_balls} vs {source_legal_balls}"
    assert (low_lb_sum + high_lb_sum) == source_legal_balls, "Low + High legal balls do not equal total!"
    print(f"PASS: Legal balls perfectly conserved ({eval_legal_balls:,} balls: {low_lb_sum:,} low/mod + {high_lb_sum:,} high).")

    # Check 5: Bowler wickets sum
    source_bowler_wickets = (clean_df['is_wicket'] & clean_df['dismissal_type'].isin(BOWLER_WICKET_TYPES)).sum()
    eval_bowler_wickets = bowlers_df['total_wickets'].sum()
    low_wk_sum = bowlers_df['low_mod_wickets'].sum()
    high_wk_sum = bowlers_df['high_wickets'].sum()
    assert eval_bowler_wickets == source_bowler_wickets, f"Bowler wickets mismatch! {eval_bowler_wickets} vs {source_bowler_wickets}"
    assert (low_wk_sum + high_wk_sum) == source_bowler_wickets, "Low + High bowler wickets do not equal total!"
    print(f"PASS: Bowler wickets perfectly conserved ({eval_bowler_wickets:,} wickets: {low_wk_sum:,} low/mod + {high_wk_sum:,} high).")

    # Check 6: No duplicate player records
    assert batters_df['player_id'].nunique() == len(batters_df), "Duplicate player IDs found in batters_df!"
    assert bowlers_df['player_id'].nunique() == len(bowlers_df), "Duplicate player IDs found in bowlers_df!"
    print("PASS: Zero duplicate player records in output datasets.")

    # 6. Save datasets
    print(f"\nSaving batter performance to {batter_out}...")
    batter_out.parent.mkdir(parents=True, exist_ok=True)
    batters_df.to_csv(batter_out, index=False)
    print(f"Saved {len(batters_df):,} batters with {len(batters_df.columns)} columns.")

    print(f"Saving bowler performance to {bowler_out}...")
    bowlers_df.to_csv(bowler_out, index=False)
    print(f"Saved {len(bowlers_df):,} bowlers with {len(bowlers_df.columns)} columns.")

    return batters_df, bowlers_df


if __name__ == '__main__':
    run_player_evaluation()
