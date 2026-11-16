import pandas as pd

df_bat = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_batting_players.csv')
for p in ['Heinrich Klaasen', 'Travis Head', 'Phil Salt', 'Jos Buttler', 'Sanju Samson', 'Virat Kohli', 'Rohit Sharma']:
    m = df_bat[df_bat['Player'] == p]
    if not m.empty:
        r = m.iloc[0]
        print(p, 'Rank:', r['Rank'], 'Shrunk:', round(r['Shrunk score'], 4), 'Raw:', round(r['Raw score'], 4), 'CI:', r['95% CI'])

df_bowl = pd.read_csv('outputs/step_7_empirical_calibration/step_7_4_final_rankings/all_eligible_bowling_players.csv')
for p in ['Rashid Khan', 'Jasprit Bumrah', 'Sunil Narine', 'Josh Hazlewood', 'Axar Patel', 'Mohammed Shami', 'Trent Boult']:
    m = df_bowl[df_bowl['Player'] == p]
    if not m.empty:
        r = m.iloc[0]
        print(p, 'Rank:', r['Rank'], 'Shrunk:', round(r['Shrunk score'], 4), 'Raw:', round(r['Raw score'], 4), 'CI:', r['95% CI'])
