import pandas as pd

df_b = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_batting_rankings.csv')
df_bowl = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_bowling_rankings.csv')

print('=== Batting Rankings (Top 25) ===')
for idx, r in df_b.head(25).iterrows():
    print(f"{r['Rank']}: {r['Player']} | Shrunk: {r['Shrunk score']} | Raw: {r['Raw score']}")

print('\n=== Bowling Rankings (Top 25) ===')
for idx, r in df_bowl.head(25).iterrows():
    print(f"{r['Rank']}: {r['Player']} | Shrunk: {r['Shrunk score']} | Raw: {r['Raw score']}")
