with open('scratch/build_step10_4_restoration.py', 'r', encoding='utf-8') as f:
    text = f.read()

pages = text.split('<div class="page-break"></div>')
print("=== PAGE 1 HTML ===")
# Find the start of <body> in Page 1
body_idx = pages[0].find('<body>')
print(pages[0][body_idx:])

print("\n" + "="*80)
print("=== PAGE 12 HTML ===")
print(pages[11][:pages[11].find('</body>')])
