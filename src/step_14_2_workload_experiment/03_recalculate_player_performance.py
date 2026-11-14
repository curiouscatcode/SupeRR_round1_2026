"""
Module 3: Recalculate Player Performance under Experimental Pressure Index
Part of Step 14.2: Experimental Workload Formula Implementation and Impact Analysis.

Applies the exact evaluate_player_performance logic from production:
  - Batting performance evaluated under Batting_PI (> 60.0)
  - Bowling performance evaluated under Bowling_PI_exp (> 60.0)
Outputs complete performance tables for all 816 batters and 589 bowlers.
"""

import os
import time
import numpy as np
import pandas as pd

BASE_DIR = r"c:\Users\ASUS\Desktop\supeRR_selector"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "step_14_2_workload_experiment")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BOWLER_WICKET_TYPES = ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']
FLAGGED_TARGET_UNDERSTATED_MATCHES = [
    14096, 14114, 14133, 15189, 16659, 16660, 16664, 19691, 20187, 24354, 
    28958, 30074, 31240, 31250, 31265, 31267, 33806, 37014, 37351, 37555, 
    40706, 40742, 40764, 41508, 45903, 46312, 47982, 48592, 50129, 50358, 
    50361, 50597, 54408, 55078, 28962, 29926, 32135, 37895
]

def safe_div(numerator, denominator, multiplier=1.0, decimals=2):
    with np.errstate(divide='ignore', invalid='ignore'):
        res = (numerator / denominator) * multiplier
        if isinstance(res, (pd.Series, np.ndarray)):
            res = np.where(denominator > 0, res, np.nan)
        elif denominator == 0:
            res = np.nan
        return np.round(res, decimals)

def evaluate_batters(df: pd.DataFrame) -> pd.DataFrame:
    print("Evaluating batter performance (816 batters)...")
    df = df.copy()
    df['is_boundary'] = (df['is_four'] | df['is_six']).astype(int)
    df['is_dot_ball_faced'] = (df['is_batter_ball_faced'] & (df['runs'] == 0)).astype(int)
    df['is_striker_out'] = (df['is_wicket'] & (df['dismissed_player_id'] == df['striker_id'])).astype(int)
    df['is_bf_int'] = df['is_batter_ball_faced'].astype(int)

    p_high = df['Batting_PI'] > 60.0
    p_low = df['Batting_PI'] <= 60.0

    is_pp = df['phase'] == 'PP'
    is_mo = df['phase'] == 'Middle'
    is_do = df['phase'] == 'Death'

    df['runs_all'] = df['runs']
    df['bf_all'] = df['is_bf_int']
    df['fours_all'] = df['is_four'].astype(int)
    df['sixes_all'] = df['is_six'].astype(int)
    df['bnd_all'] = df['is_boundary']
    df['dot_all'] = df['is_dot_ball_faced']
    df['out_all'] = df['is_striker_out']

    df['runs_low'] = np.where(p_low, df['runs'], 0)
    df['bf_low'] = np.where(p_low, df['is_bf_int'], 0)
    df['fours_low'] = np.where(p_low, df['is_four'].astype(int), 0)
    df['sixes_low'] = np.where(p_low, df['is_six'].astype(int), 0)
    df['bnd_low'] = np.where(p_low, df['is_boundary'], 0)
    df['dot_low'] = np.where(p_low, df['is_dot_ball_faced'], 0)
    df['out_low'] = np.where(p_low, df['is_striker_out'], 0)

    df['runs_high'] = np.where(p_high, df['runs'], 0)
    df['bf_high'] = np.where(p_high, df['is_bf_int'], 0)
    df['fours_high'] = np.where(p_high, df['is_four'].astype(int), 0)
    df['sixes_high'] = np.where(p_high, df['is_six'].astype(int), 0)
    df['bnd_high'] = np.where(p_high, df['is_boundary'], 0)
    df['dot_high'] = np.where(p_high, df['is_dot_ball_faced'], 0)
    df['out_high'] = np.where(p_high, df['is_striker_out'], 0)

    df['runs_pp'] = np.where(is_pp, df['runs'], 0)
    df['bf_pp'] = np.where(is_pp, df['is_bf_int'], 0)
    df['bnd_pp'] = np.where(is_pp, df['is_boundary'], 0)
    df['dot_pp'] = np.where(is_pp, df['is_dot_ball_faced'], 0)
    df['out_pp'] = np.where(is_pp, df['is_striker_out'], 0)

    df['runs_pp_high'] = np.where(is_pp & p_high, df['runs'], 0)
    df['bf_pp_high'] = np.where(is_pp & p_high, df['is_bf_int'], 0)
    df['runs_pp_low'] = np.where(is_pp & p_low, df['runs'], 0)
    df['bf_pp_low'] = np.where(is_pp & p_low, df['is_bf_int'], 0)

    df['runs_mo'] = np.where(is_mo, df['runs'], 0)
    df['bf_mo'] = np.where(is_mo, df['is_bf_int'], 0)
    df['bnd_mo'] = np.where(is_mo, df['is_boundary'], 0)
    df['dot_mo'] = np.where(is_mo, df['is_dot_ball_faced'], 0)
    df['out_mo'] = np.where(is_mo, df['is_striker_out'], 0)

    df['runs_mo_high'] = np.where(is_mo & p_high, df['runs'], 0)
    df['bf_mo_high'] = np.where(is_mo & p_high, df['is_bf_int'], 0)
    df['runs_mo_low'] = np.where(is_mo & p_low, df['runs'], 0)
    df['bf_mo_low'] = np.where(is_mo & p_low, df['is_bf_int'], 0)

    df['runs_do'] = np.where(is_do, df['runs'], 0)
    df['bf_do'] = np.where(is_do, df['is_bf_int'], 0)
    df['bnd_do'] = np.where(is_do, df['is_boundary'], 0)
    df['dot_do'] = np.where(is_do, df['is_dot_ball_faced'], 0)
    df['out_do'] = np.where(is_do, df['is_striker_out'], 0)

    df['runs_do_high'] = np.where(is_do & p_high, df['runs'], 0)
    df['bf_do_high'] = np.where(is_do & p_high, df['is_bf_int'], 0)
    df['runs_do_low'] = np.where(is_do & p_low, df['runs'], 0)
    df['bf_do_low'] = np.where(is_do & p_low, df['is_bf_int'], 0)

    df['bf_target_understated'] = np.where(df['match_id'].isin(FLAGGED_TARGET_UNDERSTATED_MATCHES), df['is_bf_int'], 0)

    agg_dict = {
        'player_name': ('striker_name', 'first'),
        'matches_played': ('match_id', 'nunique'),
        'total_deliveries_faced': ('is_bf_int', 'count'),
        'bf_target_understated': ('bf_target_understated', 'sum'),
        'runs_all': ('runs_all', 'sum'), 'bf_all': ('bf_all', 'sum'), 'fours_all': ('fours_all', 'sum'),
        'sixes_all': ('sixes_all', 'sum'), 'bnd_all': ('bnd_all', 'sum'), 'dot_all': ('dot_all', 'sum'), 'out_all': ('out_all', 'sum'),
        'runs_low': ('runs_low', 'sum'), 'bf_low': ('bf_low', 'sum'), 'fours_low': ('fours_low', 'sum'),
        'sixes_low': ('sixes_low', 'sum'), 'bnd_low': ('bnd_low', 'sum'), 'dot_low': ('dot_low', 'sum'), 'out_low': ('out_low', 'sum'),
        'runs_high': ('runs_high', 'sum'), 'bf_high': ('bf_high', 'sum'), 'fours_high': ('fours_high', 'sum'),
        'sixes_high': ('sixes_high', 'sum'), 'bnd_high': ('bnd_high', 'sum'), 'dot_high': ('dot_high', 'sum'), 'out_high': ('out_high', 'sum'),
        'runs_pp': ('runs_pp', 'sum'), 'bf_pp': ('bf_pp', 'sum'), 'bnd_pp': ('bnd_pp', 'sum'), 'dot_pp': ('dot_pp', 'sum'), 'out_pp': ('out_pp', 'sum'),
        'runs_pp_high': ('runs_pp_high', 'sum'), 'bf_pp_high': ('bf_pp_high', 'sum'), 'runs_pp_low': ('runs_pp_low', 'sum'), 'bf_pp_low': ('bf_pp_low', 'sum'),
        'runs_mo': ('runs_mo', 'sum'), 'bf_mo': ('bf_mo', 'sum'), 'bnd_mo': ('bnd_mo', 'sum'), 'dot_mo': ('dot_mo', 'sum'), 'out_mo': ('out_mo', 'sum'),
        'runs_mo_high': ('runs_mo_high', 'sum'), 'bf_mo_high': ('bf_mo_high', 'sum'), 'runs_mo_low': ('runs_mo_low', 'sum'), 'bf_mo_low': ('bf_mo_low', 'sum'),
        'runs_do': ('runs_do', 'sum'), 'bf_do': ('bf_do', 'sum'), 'bnd_do': ('bnd_do', 'sum'), 'dot_do': ('dot_do', 'sum'), 'out_do': ('out_do', 'sum'),
        'runs_do_high': ('runs_do_high', 'sum'), 'bf_do_high': ('bf_do_high', 'sum'), 'runs_do_low': ('runs_do_low', 'sum'), 'bf_do_low': ('bf_do_low', 'sum'),
    }

    b_df = df.groupby('striker_id').agg(**agg_dict).reset_index()
    b_df = b_df.rename(columns={'striker_id': 'player_id'})

    # Innings batted
    inn_batted = df[df['is_batter_ball_faced']].groupby('striker_id').apply(
        lambda x: x[['match_id', 'innings']].drop_duplicates().shape[0]
    ).to_dict()
    b_df['innings_batted'] = b_df['player_id'].map(inn_batted).fillna(0).astype(int)

    # Derived Rate Metrics
    b_df['strike_rate'] = safe_div(b_df['runs_all'], b_df['bf_all'], 100.0)
    b_df['boundary_pct'] = safe_div(b_df['bnd_all'], b_df['bf_all'], 100.0)
    b_df['dot_pct'] = safe_div(b_df['dot_all'], b_df['bf_all'], 100.0)
    b_df['dismissal_pct'] = safe_div(b_df['out_all'], b_df['bf_all'], 100.0)
    b_df['batting_average'] = safe_div(b_df['runs_all'], b_df['out_all'], 1.0)

    b_df['low_mod_strike_rate'] = safe_div(b_df['runs_low'], b_df['bf_low'], 100.0)
    b_df['low_mod_boundary_pct'] = safe_div(b_df['bnd_low'], b_df['bf_low'], 100.0)
    b_df['low_mod_dot_pct'] = safe_div(b_df['dot_low'], b_df['bf_low'], 100.0)
    b_df['low_mod_dismissal_pct'] = safe_div(b_df['out_low'], b_df['bf_low'], 100.0)
    b_df['low_mod_batting_avg'] = safe_div(b_df['runs_low'], b_df['out_low'], 1.0)

    b_df['high_strike_rate'] = safe_div(b_df['runs_high'], b_df['bf_high'], 100.0)
    b_df['high_boundary_pct'] = safe_div(b_df['bnd_high'], b_df['bf_high'], 100.0)
    b_df['high_dot_pct'] = safe_div(b_df['dot_high'], b_df['bf_high'], 100.0)
    b_df['high_dismissal_pct'] = safe_div(b_df['out_high'], b_df['bf_high'], 100.0)
    b_df['high_batting_avg'] = safe_div(b_df['runs_high'], b_df['out_high'], 1.0)

    b_df['strike_rate_delta'] = np.round(b_df['high_strike_rate'] - b_df['low_mod_strike_rate'], 2)
    b_df['boundary_pct_delta'] = np.round(b_df['high_boundary_pct'] - b_df['low_mod_boundary_pct'], 2)
    b_df['dot_pct_delta'] = np.round(b_df['high_dot_pct'] - b_df['low_mod_dot_pct'], 2)

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
    b_df = b_df.sort_values('total_runs', ascending=False).reset_index(drop=True)
    return b_df

def evaluate_bowlers(df: pd.DataFrame) -> pd.DataFrame:
    print("Evaluating bowler performance under experimental Bowling_PI_exp (589 bowlers)...")
    df = df.copy()
    df['is_lb_int'] = df['is_legal_ball'].astype(int)
    df['is_bowler_wicket_int'] = (df['is_wicket'] & df['dismissal_type'].isin(BOWLER_WICKET_TYPES)).astype(int)
    df['is_bowler_dot_int'] = (df['bowler_runs_conceded'] == 0).astype(int)
    df['is_boundary_conceded'] = (df['is_four'] | df['is_six']).astype(int)

    # Use Experimental Bowling PI
    p_high = df['Bowling_PI_exp'] > 60.0
    p_low = df['Bowling_PI_exp'] <= 60.0

    is_pp = df['phase'] == 'PP'
    is_mo = df['phase'] == 'Middle'
    is_do = df['phase'] == 'Death'

    df['rc_all'] = df['bowler_runs_conceded']
    df['lb_all'] = df['is_lb_int']
    df['wk_all'] = df['is_bowler_wicket_int']
    df['dot_all'] = df['is_bowler_dot_int']
    df['bnd_all'] = df['is_boundary_conceded']
    df['fours_all'] = df['is_four'].astype(int)
    df['sixes_all'] = df['is_six'].astype(int)

    df['rc_low'] = np.where(p_low, df['bowler_runs_conceded'], 0)
    df['lb_low'] = np.where(p_low, df['is_lb_int'], 0)
    df['wk_low'] = np.where(p_low, df['is_bowler_wicket_int'], 0)
    df['dot_low'] = np.where(p_low, df['is_bowler_dot_int'], 0)
    df['bnd_low'] = np.where(p_low, df['is_boundary_conceded'], 0)
    df['fours_low'] = np.where(p_low, df['is_four'].astype(int), 0)
    df['sixes_low'] = np.where(p_low, df['is_six'].astype(int), 0)

    df['rc_high'] = np.where(p_high, df['bowler_runs_conceded'], 0)
    df['lb_high'] = np.where(p_high, df['is_lb_int'], 0)
    df['wk_high'] = np.where(p_high, df['is_bowler_wicket_int'], 0)
    df['dot_high'] = np.where(p_high, df['is_bowler_dot_int'], 0)
    df['bnd_high'] = np.where(p_high, df['is_boundary_conceded'], 0)
    df['fours_high'] = np.where(p_high, df['is_four'].astype(int), 0)
    df['sixes_high'] = np.where(p_high, df['is_six'].astype(int), 0)

    df['rc_pp'] = np.where(is_pp, df['bowler_runs_conceded'], 0)
    df['lb_pp'] = np.where(is_pp, df['is_lb_int'], 0)
    df['wk_pp'] = np.where(is_pp, df['is_bowler_wicket_int'], 0)
    df['dot_pp'] = np.where(is_pp, df['is_bowler_dot_int'], 0)
    df['bnd_pp'] = np.where(is_pp, df['is_boundary_conceded'], 0)

    df['rc_pp_high'] = np.where(is_pp & p_high, df['bowler_runs_conceded'], 0)
    df['lb_pp_high'] = np.where(is_pp & p_high, df['is_lb_int'], 0)
    df['wk_pp_high'] = np.where(is_pp & p_high, df['is_bowler_wicket_int'], 0)

    df['rc_pp_low'] = np.where(is_pp & p_low, df['bowler_runs_conceded'], 0)
    df['lb_pp_low'] = np.where(is_pp & p_low, df['is_lb_int'], 0)
    df['wk_pp_low'] = np.where(is_pp & p_low, df['is_bowler_wicket_int'], 0)

    df['rc_mo'] = np.where(is_mo, df['bowler_runs_conceded'], 0)
    df['lb_mo'] = np.where(is_mo, df['is_lb_int'], 0)
    df['wk_mo'] = np.where(is_mo, df['is_bowler_wicket_int'], 0)
    df['dot_mo'] = np.where(is_mo, df['is_bowler_dot_int'], 0)
    df['bnd_mo'] = np.where(is_mo, df['is_boundary_conceded'], 0)

    df['rc_mo_high'] = np.where(is_mo & p_high, df['bowler_runs_conceded'], 0)
    df['lb_mo_high'] = np.where(is_mo & p_high, df['is_lb_int'], 0)
    df['wk_mo_high'] = np.where(is_mo & p_high, df['is_bowler_wicket_int'], 0)

    df['rc_mo_low'] = np.where(is_mo & p_low, df['bowler_runs_conceded'], 0)
    df['lb_mo_low'] = np.where(is_mo & p_low, df['is_lb_int'], 0)
    df['wk_mo_low'] = np.where(is_mo & p_low, df['is_bowler_wicket_int'], 0)

    df['rc_do'] = np.where(is_do, df['bowler_runs_conceded'], 0)
    df['lb_do'] = np.where(is_do, df['is_lb_int'], 0)
    df['wk_do'] = np.where(is_do, df['is_bowler_wicket_int'], 0)
    df['dot_do'] = np.where(is_do, df['is_bowler_dot_int'], 0)
    df['bnd_do'] = np.where(is_do, df['is_boundary_conceded'], 0)

    df['rc_do_high'] = np.where(is_do & p_high, df['bowler_runs_conceded'], 0)
    df['lb_do_high'] = np.where(is_do & p_high, df['is_lb_int'], 0)
    df['wk_do_high'] = np.where(is_do & p_high, df['is_bowler_wicket_int'], 0)

    df['rc_do_low'] = np.where(is_do & p_low, df['bowler_runs_conceded'], 0)
    df['lb_do_low'] = np.where(is_do & p_low, df['is_lb_int'], 0)
    df['wk_do_low'] = np.where(is_do & p_low, df['is_bowler_wicket_int'], 0)

    df['lb_target_understated'] = np.where(df['match_id'].isin(FLAGGED_TARGET_UNDERSTATED_MATCHES), df['is_lb_int'], 0)

    agg_dict = {
        'player_name': ('bowler_name', 'first'),
        'matches_bowled': ('match_id', 'nunique'),
        'total_deliveries_bowled': ('is_lb_int', 'count'),
        'lb_target_understated': ('lb_target_understated', 'sum'),
        'rc_all': ('rc_all', 'sum'), 'lb_all': ('lb_all', 'sum'), 'wk_all': ('wk_all', 'sum'),
        'dot_all': ('dot_all', 'sum'), 'bnd_all': ('bnd_all', 'sum'), 'fours_all': ('fours_all', 'sum'), 'sixes_all': ('sixes_all', 'sum'),
        'rc_low': ('rc_low', 'sum'), 'lb_low': ('lb_low', 'sum'), 'wk_low': ('wk_low', 'sum'),
        'dot_low': ('dot_low', 'sum'), 'bnd_low': ('bnd_low', 'sum'), 'fours_low': ('fours_low', 'sum'), 'sixes_low': ('sixes_low', 'sum'),
        'rc_high': ('rc_high', 'sum'), 'lb_high': ('lb_high', 'sum'), 'wk_high': ('wk_high', 'sum'),
        'dot_high': ('dot_high', 'sum'), 'bnd_high': ('bnd_high', 'sum'), 'fours_high': ('fours_high', 'sum'), 'sixes_high': ('sixes_high', 'sum'),
        'rc_pp': ('rc_pp', 'sum'), 'lb_pp': ('lb_pp', 'sum'), 'wk_pp': ('wk_pp', 'sum'), 'dot_pp': ('dot_pp', 'sum'), 'bnd_pp': ('bnd_pp', 'sum'),
        'rc_pp_high': ('rc_pp_high', 'sum'), 'lb_pp_high': ('lb_pp_high', 'sum'), 'wk_pp_high': ('wk_pp_high', 'sum'),
        'rc_pp_low': ('rc_pp_low', 'sum'), 'lb_pp_low': ('lb_pp_low', 'sum'), 'wk_pp_low': ('wk_pp_low', 'sum'),
        'rc_mo': ('rc_mo', 'sum'), 'lb_mo': ('lb_mo', 'sum'), 'wk_mo': ('wk_mo', 'sum'), 'dot_mo': ('dot_mo', 'sum'), 'bnd_mo': ('bnd_mo', 'sum'),
        'rc_mo_high': ('rc_mo_high', 'sum'), 'lb_mo_high': ('lb_mo_high', 'sum'), 'wk_mo_high': ('wk_mo_high', 'sum'),
        'rc_mo_low': ('rc_mo_low', 'sum'), 'lb_mo_low': ('lb_mo_low', 'sum'), 'wk_mo_low': ('wk_mo_low', 'sum'),
        'rc_do': ('rc_do', 'sum'), 'lb_do': ('lb_do', 'sum'), 'wk_do': ('wk_do', 'sum'), 'dot_do': ('dot_do', 'sum'), 'bnd_do': ('bnd_do', 'sum'),
        'rc_do_high': ('rc_do_high', 'sum'), 'lb_do_high': ('lb_do_high', 'sum'), 'wk_do_high': ('wk_do_high', 'sum'),
        'rc_do_low': ('rc_do_low', 'sum'), 'lb_do_low': ('lb_do_low', 'sum'), 'wk_do_low': ('wk_do_low', 'sum'),
    }

    w_df = df.groupby('bowler_id').agg(**agg_dict).reset_index()
    w_df = w_df.rename(columns={'bowler_id': 'player_id'})

    # Innings bowled
    inn_bowled = df[df['is_legal_ball']].groupby('bowler_id').apply(
        lambda x: x[['match_id', 'innings']].drop_duplicates().shape[0]
    ).to_dict()
    w_df['innings_bowled'] = w_df['player_id'].map(inn_bowled).fillna(0).astype(int)

    # Derived Rate Metrics
    w_df['economy_rate'] = safe_div(w_df['rc_all'], w_df['lb_all'], 6.0)
    w_df['bowling_average'] = safe_div(w_df['rc_all'], w_df['wk_all'], 1.0)
    w_df['strike_rate'] = safe_div(w_df['lb_all'], w_df['wk_all'], 1.0)
    w_df['dot_pct'] = safe_div(w_df['dot_all'], w_df['lb_all'], 100.0)
    w_df['boundary_pct'] = safe_div(w_df['bnd_all'], w_df['lb_all'], 100.0)

    w_df['low_mod_economy_rate'] = safe_div(w_df['rc_low'], w_df['lb_low'], 6.0)
    w_df['low_mod_bowling_avg'] = safe_div(w_df['rc_low'], w_df['wk_low'], 1.0)
    w_df['low_mod_strike_rate'] = safe_div(w_df['lb_low'], w_df['wk_low'], 1.0)
    w_df['low_mod_dot_pct'] = safe_div(w_df['dot_low'], w_df['lb_low'], 100.0)
    w_df['low_mod_boundary_pct'] = safe_div(w_df['bnd_low'], w_df['lb_low'], 100.0)

    w_df['high_economy_rate'] = safe_div(w_df['rc_high'], w_df['lb_high'], 6.0)
    w_df['high_bowling_avg'] = safe_div(w_df['rc_high'], w_df['wk_high'], 1.0)
    w_df['high_strike_rate'] = safe_div(w_df['lb_high'], w_df['wk_high'], 1.0)
    w_df['high_dot_pct'] = safe_div(w_df['dot_high'], w_df['lb_high'], 100.0)
    w_df['high_boundary_pct'] = safe_div(w_df['bnd_high'], w_df['lb_high'], 100.0)

    w_df['economy_delta'] = np.round(w_df['high_economy_rate'] - w_df['low_mod_economy_rate'], 2)
    w_df['dot_pct_delta'] = np.round(w_df['high_dot_pct'] - w_df['low_mod_dot_pct'], 2)
    w_df['boundary_pct_delta'] = np.round(w_df['high_boundary_pct'] - w_df['low_mod_boundary_pct'], 2)

    w_df['pp_economy_rate'] = safe_div(w_df['rc_pp'], w_df['lb_pp'], 6.0)
    w_df['pp_dot_pct'] = safe_div(w_df['dot_pp'], w_df['lb_pp'], 100.0)
    w_df['pp_boundary_pct'] = safe_div(w_df['bnd_pp'], w_df['lb_pp'], 100.0)
    w_df['pp_high_economy_rate'] = safe_div(w_df['rc_pp_high'], w_df['lb_pp_high'], 6.0)
    w_df['pp_low_economy_rate'] = safe_div(w_df['rc_pp_low'], w_df['lb_pp_low'], 6.0)

    w_df['mo_economy_rate'] = safe_div(w_df['rc_mo'], w_df['lb_mo'], 6.0)
    w_df['mo_dot_pct'] = safe_div(w_df['dot_mo'], w_df['lb_mo'], 100.0)
    w_df['mo_boundary_pct'] = safe_div(w_df['bnd_mo'], w_df['lb_mo'], 100.0)
    w_df['mo_high_economy_rate'] = safe_div(w_df['rc_mo_high'], w_df['lb_mo_high'], 6.0)
    w_df['mo_low_economy_rate'] = safe_div(w_df['rc_mo_low'], w_df['lb_mo_low'], 6.0)

    w_df['do_economy_rate'] = safe_div(w_df['rc_do'], w_df['lb_do'], 6.0)
    w_df['do_dot_pct'] = safe_div(w_df['dot_do'], w_df['lb_do'], 100.0)
    w_df['do_boundary_pct'] = safe_div(w_df['bnd_do'], w_df['lb_do'], 100.0)
    w_df['do_high_economy_rate'] = safe_div(w_df['rc_do_high'], w_df['lb_do_high'], 6.0)
    w_df['do_low_economy_rate'] = safe_div(w_df['rc_do_low'], w_df['lb_do_low'], 6.0)

    rename_cols = {
        'rc_all': 'total_runs_conceded', 'lb_all': 'total_legal_balls', 'wk_all': 'total_wickets', 
        'dot_all': 'total_dot_balls', 'bnd_all': 'total_boundaries_conceded', 'fours_all': 'total_fours_conceded', 'sixes_all': 'total_sixes_conceded',
        'rc_low': 'low_mod_runs_conceded', 'lb_low': 'low_mod_legal_balls', 'wk_low': 'low_mod_wickets', 
        'dot_low': 'low_mod_dot_balls', 'bnd_low': 'low_mod_boundaries_conceded', 'fours_low': 'low_mod_fours_conceded', 'sixes_low': 'low_mod_sixes_conceded',
        'rc_high': 'high_runs_conceded', 'lb_high': 'high_legal_balls', 'wk_high': 'high_wickets', 
        'dot_high': 'high_dot_balls', 'bnd_high': 'high_boundaries_conceded', 'fours_high': 'high_fours_conceded', 'sixes_high': 'high_sixes_conceded',
        'rc_pp': 'pp_runs_conceded', 'lb_pp': 'pp_legal_balls', 'wk_pp': 'pp_wickets', 'dot_pp': 'pp_dot_balls', 'bnd_pp': 'pp_boundaries_conceded',
        'rc_mo': 'mo_runs_conceded', 'lb_mo': 'mo_legal_balls', 'wk_mo': 'mo_wickets', 'dot_mo': 'mo_dot_balls', 'bnd_mo': 'mo_boundaries_conceded',
        'rc_do': 'do_runs_conceded', 'lb_do': 'do_legal_balls', 'wk_do': 'do_wickets', 'dot_do': 'do_dot_balls', 'bnd_do': 'do_boundaries_conceded',
        'lb_target_understated': 'target_understated_legal_balls'
    }
    w_df = w_df.rename(columns=rename_cols)
    w_df = w_df.sort_values('total_wickets', ascending=False).reset_index(drop=True)
    return w_df

def main():
    print("=" * 80)
    print("STEP 14.2 — MODULE 3: PLAYER PERFORMANCE RECALCULATION")
    print("=" * 80)

    # 1. Load Match State merged with Experimental PI
    pi_exp_path = os.path.join(OUTPUT_DIR, "delivery_pressure_index_exp14_2.csv")
    state_path = os.path.join(BASE_DIR, "data", "processed", "delivery_match_state.csv")

    t0 = time.time()
    print("Loading delivery datasets...")
    df_state = pd.read_csv(state_path)
    df_pi = pd.read_csv(pi_exp_path, usecols=['Batting_PI', 'Bowling_PI_exp', 'Bowling_PI_orig'])

    # Merge needed columns
    df_merged = df_state.copy()
    df_merged['Batting_PI'] = df_pi['Batting_PI']
    df_merged['Bowling_PI_exp'] = df_pi['Bowling_PI_exp']
    df_merged['Bowling_PI_orig'] = df_pi['Bowling_PI_orig']
    print(f"Loaded {len(df_merged)} deliveries in {time.time()-t0:.2f}s.")

    # Apply official v2.0 filter: exclude 233 deliveries where runs_required <= 0 in Innings 2
    is_target_reached_tail = (df_merged['innings'] == 2) & (df_merged['runs_required'] <= 0)
    assert is_target_reached_tail.sum() == 233, f"Expected 233 excluded deliveries, got {is_target_reached_tail.sum()}"
    df_clean = df_merged[~is_target_reached_tail].copy()
    print(f"Excluded 233 target-reached deliveries; active clean dataset: {len(df_clean):,} deliveries.")

    # 2. Recalculate Batters Performance
    t_bat = time.time()
    df_batters = evaluate_batters(df_clean)
    print(f"Evaluated {len(df_batters)} batters in {time.time()-t_bat:.2f}s.")

    # 3. Recalculate Bowlers Performance
    t_bowl = time.time()
    df_bowlers = evaluate_bowlers(df_clean)
    print(f"Evaluated {len(df_bowlers)} bowlers in {time.time()-t_bowl:.2f}s.")

    # Assertions
    assert len(df_batters) == 816, f"Expected 816 batters, got {len(df_batters)}"
    assert len(df_bowlers) == 589, f"Expected 589 bowlers, got {len(df_bowlers)}"

    # Export
    bat_csv = os.path.join(OUTPUT_DIR, "batter_performance_exp14_2.csv")
    bowl_csv = os.path.join(OUTPUT_DIR, "bowler_performance_exp14_2.csv")

    df_batters.to_csv(bat_csv, index=False)
    df_bowlers.to_csv(bowl_csv, index=False)

    print(f"\nExported batter performance to: {bat_csv}")
    print(f"Exported bowler performance to: {bowl_csv}")
    print("Module 3 Completed Successfully.")
    print("=" * 80)

if __name__ == "__main__":
    main()
