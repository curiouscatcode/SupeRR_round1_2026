import pandas as pd

bat = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
bowl = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv')

print("--- Lokesh Rahul in Batting ---")
print(bat[bat['Player'] == 'Lokesh Rahul'])

print("\n--- Shaheen Afridi in Bowling ---")
print(bowl[bowl['Player'] == 'Shaheen Afridi'])

# Check requested batters in bowling
requested_batters = [
    'Shubman Gill', 'Rohit Sharma', 'Shreyas Iyer', 'Virat Kohli',
    'Devdutt Padikkal', 'Rishabh Pant', 'Mitchell Marsh', 'Babar Azam',
    'Mohammad Rizwan', 'Sanju Samson', 'Lokesh Rahul', 'Hardik Pandya',
    'Ravindra Jadeja', 'Pathum Nissanka', 'Jos Buttler', 'Harry Brook',
    'Sam Curran'
]

print("\n--- Requested Batters in Bowling Dataset ---")
for b in requested_batters:
    m = bowl[bowl['Player'].str.contains(b, case=False, na=False)]
    if len(m) > 0:
        for _, r in m.iterrows():
            print(f"Bowler: {r['Player']} | Rank: {r['Rank']} | Shrunk: {r['Shrunk score']:.4f} | ESS: {r['Kish ESS']:.1f}")

# Check requested bowlers in batting
requested_bowlers = [
    'Kagiso Rabada', 'Mitchell Starc', 'Shaheen Afridi', 'Trent Boult',
    'Mohammed Siraj', 'Mohammed Shami', 'Arshdeep Singh', 'Axar Patel',
    'Ravindra Jadeja', 'Sam Curran', 'Mitchell Santner'
]

print("\n--- Requested Bowlers in Batting Dataset ---")
for b in requested_bowlers:
    m = bat[bat['Player'].str.contains(b, case=False, na=False)]
    if len(m) > 0:
        for _, r in m.iterrows():
            print(f"Batter: {r['Player']} | Rank: {r['Rank']} | Shrunk: {r['Shrunk score']:.4f} | ESS: {r['Kish ESS']:.1f}")
