import pandas as pd

m_df = pd.read_csv('data/matches.csv')
p_df = pd.read_csv('data/processed/delivery_pressure_index.csv')

# Exclude 233 tail deliveries
clean_df = p_df[~((p_df['innings'] == 2) & (p_df['runs_required'] <= 0))].copy()

# Look for:
# Archetype 1: Dramatic Chase (IPL match, Inn 2, goes to over 20, max PI > 85, won by < 5 runs/wkts)
m_inn2 = clean_df[clean_df['innings'] == 2]
m_stats = m_inn2.groupby('match_id').agg({
    'Batting_PI': ['max', 'mean'],
    'overid': 'max',
    'wickets_before': 'max',
    'runs_required': 'min'
})
m_stats.columns = ['max_pi', 'mean_pi', 'max_over', 'max_w', 'min_rr']

thriller_ids = m_stats[(m_stats['max_over'] == 20) & (m_stats['max_pi'] > 90) & (m_stats['min_rr'] >= 1) & (m_stats['min_rr'] <= 6)].index
print("Archetype 1 Candidates (High-Pressure Escalating Finish):")
for mid in thriller_ids[:5]:
    m = m_df[m_df['match_id'] == mid].iloc[0]
    print(f"  Match {mid}: {m['match_date']} | {m['home_team']} vs {m['away_team']} | {m['result']}")

# Archetype 2: First-Innings Collapse (early wickets in PP, Batting PI spikes early)
p_inn1_pp = clean_df[(clean_df['innings'] == 1) & (clean_df['phase'] == 'PP')]
pp_w = p_inn1_pp.groupby('match_id').agg({'wickets_before': 'max', 'Batting_PI': 'max'})
collapse_ids = pp_w[(pp_w['wickets_before'] >= 3) & (pp_w['Batting_PI'] > 75)].index
print("\nArchetype 2 Candidates (First-Innings Early Collapse):")
for mid in collapse_ids[:5]:
    m = m_df[m_df['match_id'] == mid].iloc[0]
    print(f"  Match {mid}: {m['match_date']} | {m['home_team']} vs {m['away_team']} | {m['result']}")

# Archetype 3: Comfortable One-Sided Chase (low Batting PI throughout Inn 2, max PI < 45)
easy_ids = m_stats[(m_stats['max_pi'] < 45) & (m_stats['max_w'] <= 2)].index
print("\nArchetype 3 Candidates (Low-Pressure Comfortable Chase):")
for mid in easy_ids[:5]:
    m = m_df[m_df['match_id'] == mid].iloc[0]
    print(f"  Match {mid}: {m['match_date']} | {m['home_team']} vs {m['away_team']} | {m['result']}")
