import pandas as pd

matches = pd.read_csv('data/matches.csv')
competitions = pd.read_csv('data/competitions.csv')
match_meta = matches.merge(competitions, on='comp_id', how='left')

ipl_all = match_meta[match_meta['comp_name'].str.contains('IPL', case=False, na=False)].sort_values(by=['season', 'match_number'])

print("Total IPL matches in matches.csv:", len(ipl_all))
print("\nBreakdown of stages by season in matches.csv:")
print(pd.crosstab(ipl_all['season'], ipl_all['stage'], margins=True))

print("\nBreakdown of knock_out column by season in matches.csv:")
print(pd.crosstab(ipl_all['season'], ipl_all['knock_out'], margins=True))

# Check if any match has stage != 'League' but knock_out == 0, or vice versa
mismatch = ipl_all[(ipl_all['knock_out'] == 1) != (ipl_all['stage'] != 'League')]
print("\nMismatches between knock_out == 1 and stage != 'League':", len(mismatch))
if len(mismatch) > 0:
    print(mismatch[['match_id', 'season', 'match_number', 'stage', 'knock_out']])
else:
    print("Perfect 1-to-1 consistency: every knockout match has knock_out=1 AND stage in ['Qualifier', 'Eliminator', 'Final'].")
