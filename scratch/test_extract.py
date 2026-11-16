import pandas as pd

bat_df = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_batting_rankings.csv')
bowl_df = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/final_bowling_rankings.csv')

print("Batting top 3:")
for _, r in bat_df.head(3).iterrows():
    print(f"#{int(r['Rank'])} {r['Player']} | Shrunk: {r['Shrunk score']:+.4f} | Raw: {r['Raw score']:+.4f} | Balls: {int(r['Raw opportunities'])} | ESS: {r['Kish ESS']:.1f} | CI: {r['95% CI']}")

print("Bowling top 3:")
for _, r in bowl_df.head(3).iterrows():
    print(f"#{int(r['Rank'])} {r['Player']} | Shrunk: {r['Shrunk score']:+.4f} | Raw: {r['Raw score']:+.4f} | Balls: {int(r['Raw opportunities'])} | ESS: {r['Kish ESS']:.1f} | CI: {r['95% CI']}")
