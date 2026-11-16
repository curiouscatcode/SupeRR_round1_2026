import re

files = [
    'outputs/step_10_methodology_report/step_10_methodology_report.md',
    'scratch/build_step10_user_updates.py',
    'scratch/build_step10_4_restoration.py'
]

targets = [
    'eliminate small-sample noise',
    'peerless death-over containment and breakthroughs',
    'resolves traditional cricket metric distortions',
    'peerless death-over containment',
    'resolves traditional cricket metric',
    'small-sample noise'
]

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f'=== {fpath} ===')
    for t in targets:
        matches = list(re.finditer(re.escape(t), content, re.IGNORECASE))
        if matches:
            print(f'  Target "{t}": {len(matches)} matches')
            for m in matches:
                start = max(0, m.start() - 30)
                end = min(len(content), m.end() + 40)
                snippet = content[start:end].replace('\n', ' ')
                print(f'    [{m.start()}]: ...{snippet}...')
