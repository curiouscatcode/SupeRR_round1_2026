import pandas as pd

df = pd.read_csv('data/processed/delivery_pressure_index.csv')
matches = pd.read_csv('data/matches.csv')

sub = df[(df['innings'] == 2) & (df['runs_required'] <= 0)]
mids = sub['match_id'].unique()

res_list = []
for mid in mids:
    m_info = matches[matches['match_id'] == mid].iloc[0]
    m_df = df[df['match_id'] == mid]
    inn1_recon = m_df[m_df['innings'] == 1]['team_runs_added'].sum()
    inn2_recon = m_df[m_df['innings'] == 2]['team_runs_added'].sum()
    target_recon = inn1_recon + 1
    
    res = m_info.get('result', '')
    res_list.append({
        'match_id': mid,
        'result': res,
        'inn1_recon': inn1_recon,
        'inn2_recon': inn2_recon,
        'target_recon': target_recon,
        'diff': inn2_recon - inn1_recon
    })

res_df = pd.DataFrame(res_list)
print("Breakdown of result string in the 90 affected matches:")
won_by_wickets = res_df['result'].str.contains('Wicket|wickets|Wkts|wkts', case=False, na=False)
won_by_runs = res_df['result'].str.contains('Run|runs', case=False, na=False)
tied = res_df['result'].str.contains('Tie|tied|Super', case=False, na=False)

print(f"Won by wickets (Chasing team won in reality): {won_by_wickets.sum()}")
print(f"Won by runs (Defending team won in reality): {won_by_runs.sum()}")
print(f"Tied / Other: {tied.sum()}")

print("\nMatches where Defending Team won in reality, but runs_required <= 0 occurred:")
print(res_df[won_by_runs][['match_id', 'result', 'inn1_recon', 'inn2_recon', 'target_recon']].to_string(index=False))
