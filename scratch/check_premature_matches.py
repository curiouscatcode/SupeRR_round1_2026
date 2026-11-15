import pandas as pd

matches = pd.read_csv('data/matches.csv')
comps = pd.read_csv('data/competitions.csv')
m_all = matches.merge(comps, on='comp_id', how='left')
dms = pd.read_csv('data/processed/delivery_match_state.csv')

for mid in [31278, 48514, 15795, 14130, 14164]:
    m = m_all[m_all['match_id'] == mid].iloc[0]
    deliv = dms[dms['match_id'] == mid]
    inn1 = deliv[deliv['innings'] == 1]
    inn2 = deliv[deliv['innings'] == 2]
    print(f"Match {mid}: {m['comp_name']} ({m['match_date']})")
    print(f"  Result: {m['result']}")
    print(f"  Inn 1: {inn1['is_legal_ball'].sum()} legal balls, max overid = {inn1['overid'].max()}")
    print(f"  Inn 2: {inn2['is_legal_ball'].sum()} legal balls, max overid = {inn2['overid'].max()}")
    print(f"  Revised cols: {m['first_inn_revised_overs']}, {m['second_inn_revised_overs']}, {m['revised_target']}")
