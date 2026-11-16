with open('scratch/build_step10_pdf_fixed.py', 'r', encoding='utf-8') as f:
    text = f.read()

chunks = text.split('<div class="page-break"></div>')
print(f'Number of pages: {len(chunks)}')
for i, c in enumerate(chunks):
    lines = [l.strip() for l in c.split('\n') if l.strip()]
    heading = 'No heading'
    for l in lines:
        if '<h' in l:
            heading = l
            break
    print(f'Page {i+1}: {heading[:80]} (length: {len(c)})')
