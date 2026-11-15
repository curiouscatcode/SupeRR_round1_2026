import pandas as pd

dms = pd.read_csv('data/processed/delivery_match_state.csv')
matches = pd.read_csv('data/matches.csv')
comps = pd.read_csv('data/competitions.csv')
m_all = matches.merge(comps, on='comp_id', how='left')

# Group by match_id for Innings 1
inn1_stats = dms[dms['innings'] == 1].groupby('match_id').agg({
    'overid': 'max',
    'legal_balls_before': 'max',
    'is_legal_ball': 'sum',
    'wickets_before': 'max',
    'is_wicket': 'sum'
}).reset_index()

inn1_stats['total_legal'] = inn1_stats['is_legal_ball']
inn1_stats['total_wkts'] = inn1_stats['wickets_before'] + inn1_stats['is_wicket']

shortened = inn1_stats[(inn1_stats['total_legal'] < 118) & (inn1_stats['total_wkts'] < 10)]
print(f"Matches where Innings 1 had < 118 legal balls and < 10 wickets: {len(shortened)}")
shortened_merged = shortened.merge(m_all[['match_id', 'comp_name', 'match_date', 'result']], on='match_id')
print(shortened_merged[['match_id', 'comp_name', 'match_date', 'total_legal', 'overid', 'total_wkts', 'result']])
