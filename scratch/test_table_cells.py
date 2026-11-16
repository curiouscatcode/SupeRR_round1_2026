import pymupdf

doc = pymupdf.open()
page = doc.new_page()
rect = pymupdf.Rect(50, 50, 500, 200)
html = '''
<table>
<tr>
    <th>Rank</th><th>Player Name</th><th>Team / Franchise</th><th>Shrunk Score</th><th>Raw Score</th><th>Balls</th><th>Kish ESS</th><th>95% Bootstrap CI</th>
</tr>
<tr><td>#1</td><td>Player</td><td>Team (IPL/T20<span style="font-family: serif; font-weight: bold;">I</span>)</td><td>+0.1234</td><td>+0.5678</td><td>500</td><td>450.0</td><td>[+0.1000, +0.2000]</td></tr>
</table>
'''
page.insert_htmlbox(rect, html)
blocks = page.get_text('blocks')
for b in blocks:
    if b[4].strip().startswith('#'):
        lines = b[4].strip().split('\n')
        print('Row elements count:', len(lines))
        for idx, l in enumerate(lines):
            print(f'  [{idx}]: {repr(l)}')
