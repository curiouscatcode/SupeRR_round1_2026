import pandas as pd
import numpy as np

df = pd.read_csv('data/processed/delivery_pressure_index.csv')
matches = pd.read_csv('data/matches.csv')

inn2 = df[df['innings'] == 2]
sub = inn2[inn2['runs_required'] <= 0]
mids = sub['match_id'].unique()

print(f"Total affected matches: {len(mids)}")

rows = []
for mid in mids:
    m_info = matches[matches['match_id'] == mid].iloc[0]
    m_delivs = df[df['match_id'] == mid]
    inn1 = m_delivs[m_delivs['innings'] == 1]
    inn2 = m_delivs[m_delivs['innings'] == 2]
    
    inn1_recon = inn1['team_runs_added'].sum()
    inn2_recon = inn2['team_runs_added'].sum()
    target_recon = inn1_recon + 1
    
    # Deliveries where runs_required <= 0
    neg_delivs = inn2[inn2['runs_required'] <= 0]
    count_neg = len(neg_delivs)
    
    # Events during these negative deliveries
    runs_in_neg = neg_delivs['runs'].sum()
    wickets_in_neg = neg_delivs['is_wicket'].sum()
    extras_in_neg = neg_delivs['extras_type'].notnull().sum()
    
    # Delivery info
    first_neg_ball = neg_delivs.iloc[0]
    first_neg_str = f"Over {first_neg_ball['overid']}.{first_neg_ball['over_ball_num']}"
    last_ball = inn2.iloc[-1]
    last_ball_str = f"Over {last_ball['overid']}.{last_ball['over_ball_num']}"
    
    # Check byes/legbyes count in inn1
    inn1_lb = (inn1['extras_type'] == 'legbyes').sum()
    inn1_b = (inn1['extras_type'] == 'byes').sum()
    inn1_w = (inn1['extras_type'] == 'wide').sum()
    inn1_nb = (inn1['extras_type'].isin(['Overstep', 'other'])).sum()
    
    rows.append({
        'match_id': mid,
        'comp_id': m_info['comp_id'],
        'match_date': m_info['match_date'],
        'home_team': m_info['home_team'],
        'away_team': m_info['away_team'],
        'result': m_info['result'],
        'inn1_recon': inn1_recon,
        'inn2_recon': inn2_recon,
        'target_recon': target_recon,
        'count_neg': count_neg,
        'first_neg_over': first_neg_str,
        'last_ball_over': last_ball_str,
        'runs_in_neg': runs_in_neg,
        'wickets_in_neg': wickets_in_neg,
        'inn1_lb': inn1_lb,
        'inn1_b': inn1_b,
        'inn1_w': inn1_w,
        'inn1_nb': inn1_nb
    })

res_df = pd.DataFrame(rows)
res_df.to_csv('scratch/detailed_90_matches.csv', index=False)
print("Saved 90 matches to scratch/detailed_90_matches.csv")
print(res_df[['match_id', 'match_date', 'home_team', 'away_team', 'result', 'inn1_recon', 'inn2_recon', 'count_neg', 'runs_in_neg', 'wickets_in_neg']].head(20).to_string())
