import pandas as pd

bat = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
bowl = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv')

requested_batters = [
    'Shubman Gill', 'Rohit Sharma', 'Shreyas Iyer', 'Virat Kohli',
    'Devdutt Padikkal', 'Rishabh Pant', 'Mitchell Marsh', 'Babar Azam',
    'Mohammad Rizwan', 'Sanju Samson', 'KL Rahul', 'Hardik Pandya',
    'Ravindra Jadeja', 'Pathum Nissanka', 'Jos Buttler', 'Harry Brook',
    'Sam Curran'
]

requested_bowlers = [
    'Kagiso Rabada', 'Mitchell Starc', 'Shaheen Shah Afridi', 'Trent Boult',
    'Mohammed Siraj', 'Mohammed Shami', 'Arshdeep Singh', 'Axar Patel',
    'Ravindra Jadeja', 'Sam Curran', 'Mitchell Santner'
]

print("=== BATTING MATCHES ===")
for name in requested_batters:
    m = bat[bat['Player'].str.contains(name, case=False, na=False)]
    if len(m) > 0:
        for _, r in m.iterrows():
            print(f"MATCH: {name} -> {r['Player']} | Rank: {r['Rank']} | Shrunk: {r['Shrunk score']:.4f} | Raw: {r['Raw score']:.4f} | ESS: {r['Kish ESS']:.1f} | Balls: {r['Raw opportunities']}")
    else:
        last_name = name.split()[-1]
        m2 = bat[bat['Player'].str.contains(last_name, case=False, na=False)]
        matches = list(m2['Player'])
        print(f"NO DIRECT MATCH: {name} | Partial candidates with '{last_name}': {matches}")

print("\n=== BOWLING MATCHES ===")
for name in requested_bowlers:
    m = bowl[bowl['Player'].str.contains(name, case=False, na=False)]
    if len(m) > 0:
        for _, r in m.iterrows():
            print(f"MATCH: {name} -> {r['Player']} | Rank: {r['Rank']} | Shrunk: {r['Shrunk score']:.4f} | Raw: {r['Raw score']:.4f} | ESS: {r['Kish ESS']:.1f} | Balls: {r['Raw opportunities']}")
    else:
        last_name = name.split()[-1]
        m2 = bowl[bowl['Player'].str.contains(last_name, case=False, na=False)]
        matches = list(m2['Player'])
        print(f"NO DIRECT MATCH: {name} | Partial candidates with '{last_name}': {matches}")
