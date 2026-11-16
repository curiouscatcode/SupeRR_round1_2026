import pymupdf

doc = pymupdf.open()
page = doc.new_page()
rect = pymupdf.Rect(50, 50, 500, 200)
html = '''
<table>
<tr><td>#1</td><td>Player</td><td>Team (IPL/T20<span style="font-family: serif; font-weight: bold;">I</span>)</td><td>+0.1234</td><td>+0.5678</td><td>500</td><td>450.0</td><td>[+0.1000, +0.2000]</td></tr>
</table>
'''
page.insert_htmlbox(rect, html)
blocks = page.get_text('blocks')
print('Blocks:')
for b in blocks:
    lines = b[4].strip().split('\n')
    print('Length:', len(lines))
    print(lines)
