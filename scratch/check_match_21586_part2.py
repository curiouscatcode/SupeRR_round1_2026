import pandas as pd

dms = pd.read_csv("data/processed/delivery_match_state.csv")
print("Is 21586 in delivery_match_state.csv?", 21586 in dms['match_id'].unique())

bbb = pd.read_csv("data/ball_by_ball.csv")
print("Is 21586 in ball_by_ball.csv?", 21586 in bbb['match_id'].unique())

matches = pd.read_csv("data/matches.csv")
print("Row for 21586 in matches.csv:")
print(matches[matches['match_id'] == 21586].to_dict(orient='records'))
