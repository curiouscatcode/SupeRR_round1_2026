with open('scratch/build_step10_pdf_fixed.py', 'r', encoding='utf-8') as f:
    text = f.read()

chunks = text.split('<div class="page-break"></div>')
print('=== PAGE 2 CONTENT ===')
print(chunks[1])
print('=== PAGE 7 CONTENT ===')
print(chunks[6])
print('=== PAGE 12 CONTENT ===')
print(chunks[11])
