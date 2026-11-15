import pandas as pd
df = pd.read_parquet('outputs/step_4_pressure_pipeline/delivery_pressure_v2.parquet')

# Archetypes:
s1 = df[(df['innings'] == 1) & (df['legal_balls_before'] == 0) & (df['score_before'] == 0)].iloc[0]
s2 = df[(df['innings'] == 1) & (df['overid'] == 3) & (df['wickets_before'] == 1)].iloc[10]
s3 = df[(df['innings'] == 1) & (df['overid'] == 10) & (df['wickets_before'] >= 5)].iloc[0]
s4 = df[(df['innings'] == 1) & (df['overid'] == 19) & (df['score_before'] >= 170)].iloc[0]
s5 = df[(df['innings'] == 2) & (df['overid'] >= 14) & (df['runs_required'] <= 15) & (df['wickets_before'] <= 3)].iloc[0]
s6 = df[(df['innings'] == 2) & (df['overid'] == 16) & (df['required_run_rate'] >= 13) & (df['wickets_before'] >= 4) & (df['wickets_before'] <= 6)].iloc[0]
s7 = df[(df['innings'] == 2) & (df['overid'] == 19) & (df['runs_required'] >= 40)].iloc[0]
s8 = df[(df['innings'] == 1) & (df['overid'] == 16) & (df['score_before'] >= 160) & (df['wickets_before'] <= 2)].iloc[0]
s9 = df[(df['innings'] == 1) & (df['overid'] == 12) & (df['score_before'] <= 60) & (df['wickets_before'] >= 5)].iloc[0]
s10 = df[(df['innings'] == 2) & (df['balls_remaining'] == 1) & (df['runs_required'] <= 6) & (df['runs_required'] > 0)].iloc[0]

states = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
labels = [
    '1. Opening ball (Inn 1, 0.1)',
    '2. Powerplay (Inn 1, over 3, 1 down)',
    '3. Middle collapse (Inn 1, over 10, 5 down)',
    '4. Death situation (Inn 1, over 19, 170+)',
    '5. Comfortable chase (Inn 2, ov 15, trivial req)',
    '6. Difficult chase (Inn 2, ov 16, RRR 13+)',
    '7. Impossible chase (Inn 2, ov 19, req 40+)',
    '8. First-innings high-scoring (Inn 1, ov 16, 160/2)',
    '9. First-innings low-scoring (Inn 1, ov 12, 60/5+)',
    '10. Final ball nail-biter (Inn 2, B_rem=1, req<=6)'
]

for l, s in zip(labels, states):
    m_id = s['match_id']
    inn = s['innings']
    ov = s['overid']
    ball = s['over_ball_num']
    sc = s['score_before']
    wk = s['wickets_before']
    brem = s['balls_remaining']
    req = s['runs_required']
    print(f"{l:45s} | Match {m_id} Inn {inn} Ov {ov}.{ball} | Score={sc}/{wk}, B_rem={brem}, Req={req}")
