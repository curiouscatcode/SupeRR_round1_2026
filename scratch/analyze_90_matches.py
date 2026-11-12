import pandas as pd
import numpy as np

df = pd.read_csv('data/processed/delivery_pressure_index.csv')
matches = pd.read_csv('data/matches.csv')

inn2 = df[df['innings'] == 2]
neg_delivs = inn2[inn2['runs_required'] <= 0]
match_ids = neg_delivs['match_id'].unique()

print(f"Total Innings 2 deliveries: {len(inn2):,}")
print(f"Total deliveries where runs_required <= 0: {len(neg_delivs)} ({len(neg_delivs)/len(inn2)*100:.3f}%)")
print(f"Total matches affected: {len(match_ids)} out of 789 ({len(match_ids)/789*100:.2f}%)")

# Let's inspect each match:
# 1. Did the match end at this delivery, or were there deliveries after?
# 2. How many deliveries occurred after target reached?
# 3. Was it at the very end of the innings (the last over/balls)?
match_summary = []
for mid in match_ids:
    m_info = matches[matches['match_id'] == mid].iloc[0]
    m_all = df[df['match_id'] == mid]
    m_inn1 = m_all[m_all['innings'] == 1]
    m_inn2 = m_all[m_all['innings'] == 2]
    
    inn1_recon_score = m_inn1['team_runs_added'].sum()
    inn2_recon_score = m_inn2['team_runs_added'].sum()
    
    sub = m_inn2[m_inn2['runs_required'] <= 0]
    first_idx = sub.index[0]
    first_row = sub.iloc[0]
    last_row = sub.iloc[-1]
    
    num_delivs_after_reached = len(sub)
    first_over = first_row['overid']
    first_ball = first_row['over_ball_num']
    total_inn2_balls = len(m_inn2)
    last_ball_is_final = (sub.index[-1] == m_inn2.index[-1])
    
    match_summary.append({
        'match_id': mid,
        'result': m_info.get('result'),
        'inn1_recon': inn1_recon_score,
        'inn2_recon': inn2_recon_score,
        'target': inn1_recon_score + 1,
        'first_reached_over': f"{first_over}.{first_ball}",
        'count_reached_rows': num_delivs_after_reached,
        'inn2_total_balls': total_inn2_balls,
        'ends_at_innings_end': last_ball_is_final,
        'min_runs_req': sub['runs_required'].min(),
        'max_runs_req': sub['runs_required'].max()
    })

sum_df = pd.DataFrame(match_summary)
print("\n--- Summary of Affected Matches ---")
print(sum_df.head(20).to_string(index=False))

print(f"\nBreakdown of 'ends_at_innings_end':")
print(sum_df['ends_at_innings_end'].value_counts())

print(f"\nDistribution of count of reached rows per match:")
print(sum_df['count_reached_rows'].value_counts().sort_index())
