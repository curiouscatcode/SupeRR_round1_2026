import os
import re

# 1. Update Markdown
md_path = 'outputs/step_10_methodology_report/step_10_methodology_report.md'
with open(md_path, 'r', encoding='utf-8') as f:
    md_text = f.read()

# Replace 1: eliminate small-sample noise
md_text = md_text.replace(
    'to eliminate small-sample noise while preserving genuine ratings for high-volume players.',
    'to reduce small-sample instability through shrinkage while preserving genuine ratings for high-volume players.'
)
md_text = md_text.replace(
    'preventing small-sample noise from dominating official leaderboards',
    'reducing small-sample instability through shrinkage to prevent volatile outliers from dominating official leaderboards'
)

# Replace 2: peerless death-over containment and breakthroughs
md_text = md_text.replace(
    'dominate global bowling reliability through elite economy and breakthrough wickets in high-leverage overs.',
    'lead bowling reliability, demonstrating strong pressure-weighted performance, including positive death-over results.'
)

# Replace 3: resolves traditional cricket metric distortions
md_text = md_text.replace(
    'resolves traditional cricket metric distortions, establishing transparent',
    'addresses several limitations of conventional cricket metrics, establishing transparent'
)

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_text)

print("Markdown updated with revised wording.")

# 2. Update build_step10_user_updates.py
script_path = 'scratch/build_step10_user_updates.py'
with open(script_path, 'r', encoding='utf-8') as f:
    script_text = f.read()

script_text = script_text.replace(
    'based on Kish ESS to eliminate small-sample noise.',
    'based on Kish ESS to reduce small-sample instability through shrinkage.'
)
script_text = script_text.replace(
    'dominate bowling through peerless death-over containment and breakthroughs.',
    'demonstrate strong pressure-weighted performance, including positive death-over results.'
)
script_text = script_text.replace(
    'resolves traditional cricket metric distortions, establishing robust',
    'addresses several limitations of conventional cricket metrics, establishing robust'
)

with open(script_path, 'w', encoding='utf-8') as f:
    f.write(script_text)

print("Build script updated with revised wording.")
