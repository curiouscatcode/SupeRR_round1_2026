import pandas as pd

bat_del = pd.read_parquet('outputs/step_5_player_level_dataset/batting_pressure_deliveries.parquet')
bowl_del = pd.read_parquet('outputs/step_5_player_level_dataset/bowling_pressure_deliveries.parquet')

famous_check = [
    'MS Dhoni', 'Dhoni', 'David Warner', 'Warner', 'Ben Stokes', 'Stokes',
    'Steve Smith', 'Kane Williamson', 'Williamson', 'Pat Cummins', 'Cummins',
    'Faf du Plessis', 'du Plessis', 'Glenn Maxwell', 'Maxwell', 'Andre Russell',
    'Sunil Narine', 'Dinesh Karthik', 'Shikhar Dhawan', 'Dhawan', 'Jonny Bairstow',
    'Bairstow', 'Moeen Ali', 'Marcus Stoinis', 'Stoinis', 'Quinton de Kock', 'de Kock',
    'David Miller', 'Miller', 'Nicholas Pooran', 'Pooran', 'Shimron Hetmyer', 'Hetmyer',
    'Rinku Singh', 'Shivam Dube', 'Dube', 'Yuzvendra Chahal', 'Chahal', 'Kuldeep Yadav',
    'Varun Chakravarthy', 'Harshal Patel', 'Anrich Nortje', 'Nortje', 'Lockie Ferguson',
    'Ferguson', 'Adam Zampa', 'Zampa', 'Tabraiz Shamsi', 'Shamsi', 'Ishant Sharma',
    'Bhuvneshwar Kumar', 'Deepak Chahar', 'Shardul Thakur', 'Thakur', 'Washington Sundar'
]

bat_names = set(bat_del['striker_name'].unique())
bowl_names = set(bowl_del['bowler_name'].unique())

print("--- Searching Famous Names in Dataset ---")
for name in famous_check:
    in_bat = [n for n in bat_names if name.lower() in n.lower()]
    in_bowl = [n for n in bowl_names if name.lower() in n.lower()]
    if in_bat or in_bowl:
        print(f"FOUND '{name}': Batting={in_bat}, Bowling={in_bowl}")
    else:
        print(f"NOT FOUND in dataset: '{name}'")
