import pandas as pd

matches = pd.read_csv('data/matches.csv')
competitions = pd.read_csv('data/competitions.csv')
bat_del = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
active_match_ids = set(bat_del['match_id'].unique())

match_meta = matches.merge(competitions, on='comp_id', how='left')
ipl_ko = match_meta[(match_meta['match_id'].isin(active_match_ids)) & (match_meta['comp_name'].str.contains('IPL', case=False, na=False)) & ((match_meta['knock_out'] == 1) | (match_meta['stage'] != 'League'))].sort_values(by=['season', 'match_date']).copy()

# Determine exact knockout stage: Qualifier 1, Eliminator, Qualifier 2, Final
def get_exact_stage(row):
    stg = row['stage']
    num = row['match_number']
    season = row['season']
    
    if stg == 'Final':
        return 'Final'
    elif stg == 'Eliminator':
        return 'Eliminator'
    elif stg == 'Qualifier':
        # Check if first qualifier or second qualifier of that season
        if season == 2025:
            # 2025: 72 is Q1, 73 is Eliminator, 74 is Q2, 75 is Final
            if num == 72:
                return 'Qualifier 1'
            elif num == 74:
                return 'Qualifier 2'
        else:
            # 2022, 2023, 2024, 2026: 71 is Q1, 72 is Eliminator, 73 is Q2, 74 is Final
            if num == 71:
                return 'Qualifier 1'
            elif num == 73:
                return 'Qualifier 2'
    return f"Unknown ({stg}, #{num})"

ipl_ko['exact_stage'] = ipl_ko.apply(get_exact_stage, axis=1)

print("=== Mapped Active IPL Knockout Matches ===")
for _, r in ipl_ko.iterrows():
    print(f"Season: {r['season']} | Match ID: {r['match_id']} | Match #: {r['match_number']} | Date: {r['match_date']} | Metadata Stage: {r['stage']:10s} -> Exact Stage: {r['exact_stage']:12s} | {r['home_team']} vs {r['away_team']} | Winner: {r['result']}")

# Check delivery counts in batting and bowling
bowl_del = pd.read_parquet('outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet')

print("\n=== Delivery and Ball Counts per Match ===")
for mid in ipl_ko['match_id']:
    b_cnt = len(bat_del[bat_del['match_id'] == mid])
    w_cnt = len(bowl_del[bowl_del['match_id'] == mid])
    leg_cnt = len(bowl_del[(bowl_del['match_id'] == mid) & (bowl_del['is_legal_ball'] == 1)])
    faced_cnt = len(bat_del[(bat_del['match_id'] == mid) & (bat_del['is_batter_ball_faced'] == 1)])
    print(f"Match {mid}: Batting rows={b_cnt}, Faced balls={faced_cnt}, Bowling rows={w_cnt}, Legal balls={leg_cnt}")
