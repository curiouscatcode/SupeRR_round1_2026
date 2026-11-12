import pandas as pd
import numpy as np

df = pd.read_csv('data/processed/delivery_pressure_index.csv')
matches = pd.read_csv('data/matches.csv')

inn2 = df[df['innings'] == 2]
sub = inn2[inn2['runs_required'] <= 0]
mids = sub['match_id'].unique()

print(f"Total affected matches: {len(mids)}")

records = []
for mid in mids:
    m_info = matches[matches['match_id'] == mid].iloc[0]
    m_df = df[df['match_id'] == mid]
    inn1_df = m_df[m_df['innings'] == 1]
    inn2_df = m_df[m_df['innings'] == 2]
    
    inn1_recon = inn1_df['team_runs_added'].sum()
    inn2_recon = inn2_df['team_runs_added'].sum()
    target_recon = inn1_recon + 1
    
    # check extras in inn1
    inn1_byes = (inn1_df['extras_type'] == 'byes').sum()
    inn1_legbyes = (inn1_df['extras_type'] == 'legbyes').sum()
    inn1_wides = (inn1_df['extras_type'] == 'wide').sum()
    inn1_noballs = (inn1_df['extras_type'].isin(['Overstep', 'other'])).sum()
    
    # deliveries where runs_required <= 0
    neg_delivs = inn2_df[inn2_df['runs_required'] <= 0]
    count_neg = len(neg_delivs)
    
    # check events in neg_delivs
    wickets_in_neg = neg_delivs['is_wicket'].sum()
    runs_in_neg = neg_delivs['runs'].sum()
    
    # result string
    res = str(m_info.get('result', ''))
    
    # Over where target first reached
    first_neg = neg_delivs.iloc[0]
    first_neg_over = f"{first_neg['overid']}.{first_neg['over_ball_num']}"
    last_inn2_over = f"{inn2_df.iloc[-1]['overid']}.{inn2_df.iloc[-1]['over_ball_num']}"
    
    records.append({
        'match_id': mid,
        'comp_id': m_info.get('comp_id'),
        'match_date': m_info.get('match_date'),
        'home_team': m_info.get('home_team'),
        'away_team': m_info.get('away_team'),
        'result': res,
        'inn1_recon': inn1_recon,
        'inn2_recon': inn2_recon,
        'target_recon': target_recon,
        'inn1_byes': inn1_byes,
        'inn1_legbyes': inn1_legbyes,
        'count_neg': count_neg,
        'wickets_in_neg': wickets_in_neg,
        'runs_in_neg': runs_in_neg,
        'first_neg_over': first_neg_over,
        'last_inn2_over': last_inn2_over,
        'inn2_total_balls': len(inn2_df)
    })

rec_df = pd.DataFrame(records)

# Let us check how many matches have meaningful events (runs > 0 or wickets > 0) or continued play after target
# versus matches where only 1 ball had runs_req <= 0 (e.g. boundary on final ball or 1 single ghost ball)
print(f"Total matches: {len(rec_df)}")
print(f"Matches with wickets falling after target reached: {(rec_df['wickets_in_neg'] > 0).sum()}")
print(f"Matches won by runs: {rec_df['result'].str.contains('run', case=False).sum()}")

# Save full summary
rec_df.to_csv('scratch/affected_matches_summary.csv', index=False)
print("Saved summary to scratch/affected_matches_summary.csv")
