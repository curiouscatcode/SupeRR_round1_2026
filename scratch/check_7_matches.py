import pandas as pd

dms = pd.read_csv('data/processed/delivery_match_state.csv')
matches = pd.read_csv('data/matches.csv')

for mid in [45491, 49736, 21177, 31708, 41976, 50366, 20228]:
    m = matches[matches['match_id'] == mid].iloc[0]
    deliv = dms[dms['match_id'] == mid]
    inn1 = deliv[deliv['innings'] == 1]
    inn2 = deliv[deliv['innings'] == 2]
    res = m['result']
    ov1 = inn1['overid'].max()
    l1 = inn1['is_legal_ball'].sum()
    w1 = inn1['wickets_before'].iloc[-1] + inn1['is_wicket'].iloc[-1]
    s1 = inn1['score_before'].iloc[-1] + inn1['team_runs_added'].iloc[-1]

    ov2 = inn2['overid'].max()
    l2 = inn2['is_legal_ball'].sum()
    w2 = inn2['wickets_before'].iloc[-1] + inn2['is_wicket'].iloc[-1]
    s2 = inn2['score_before'].iloc[-1] + inn2['team_runs_added'].iloc[-1]
    
    print(f"Match {mid}: {res}")
    print(f"  Inn 1: {s1}/{w1} in {l1} legal balls (max over {ov1})")
    print(f"  Inn 2: {s2}/{w2} in {l2} legal balls (max over {ov2})")
