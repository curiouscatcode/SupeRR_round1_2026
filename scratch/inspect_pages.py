with open('scratch/build_step10_4_restoration.py', 'r', encoding='utf-8') as f:
    text = f.read()

pages = text.split('<div class="page-break"></div>')
print('Total split pages:', len(pages))
for i, p in enumerate(pages):
    print(f'=== Page {i+1} === (length {len(p)})')
    lines = [l.strip() for l in p.strip().splitlines() if l.strip()]
    if lines:
        print('  First line:', lines[0][:80])
        print('  Last line :', lines[-1][:80])
