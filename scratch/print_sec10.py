with open('scratch/test_complete_builder.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('## Section 10')
print('=== Markdown Section 10 ===')
print(text[idx:idx+800])

idx2 = text.find('Section 10 &mdash;')
print('=== HTML Section 10 ===')
print(text[idx2-50:idx2+600])
