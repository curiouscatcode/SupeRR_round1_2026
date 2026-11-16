with open('scratch/build_step10_4_restoration.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('table_html = "<table>')
print(text[idx-600:idx+100])
