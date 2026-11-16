import pandas as pd

df_bat = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
df_bowl = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv')

bat_players = [
    'Heinrich Klaasen', 'Phil Salt', 'Travis Head', 'Shreyas Iyer', 'Jos Buttler',
    'Mitchell Marsh', 'Virat Kohli', 'Rohit Sharma', 'Shubman Gill', 'Devdutt Padikkal',
    'Rishabh Pant', 'Babar Azam', 'Mohammad Rizwan', 'Sanju Samson', 'KL Rahul',
    'Lokesh Rahul', 'Hardik Pandya', 'Ravindra Jadeja', 'Pathum Nissanka', 'Harry Brook', 'Sam Curran'
]

bowl_players = [
    'Rashid Khan', 'Jasprit Bumrah', 'Sunil Narine', 'Josh Hazlewood', 'Mohammed Shami',
    'Trent Boult', 'Kagiso Rabada', 'Mitchell Starc', 'Shaheen Shah Afridi', 'Mohammed Siraj',
    'Arshdeep Singh', 'Axar Patel', 'Ravindra Jadeja', 'Sam Curran', 'Mitchell Santner'
]

print("=== BATTING RANKS IN AUTHORITATIVE STEP 7.4 ===")
for p in bat_players:
    m = df_bat[df_bat['Player'].str.contains(p, case=False, na=False)]
    if not m.empty:
        for _, r in m.iterrows():
            print(f"{r['Player']}: Rank #{r['Rank']} | Shrunk: {r['Shrunk score']} | Raw: {r['Raw score']}")
    else:
        print(f"NOT FOUND: {p}")

print("\n=== BOWLING RANKS IN AUTHORITATIVE STEP 7.4 ===")
for p in bowl_players:
    m = df_bowl[df_bowl['Player'].str.contains(p, case=False, na=False)]
    if not m.empty:
        for _, r in m.iterrows():
            print(f"{r['Player']}: Rank #{r['Rank']} | Shrunk: {r['Shrunk score']} | Raw: {r['Raw score']}")
    else:
        print(f"NOT FOUND: {p}")
