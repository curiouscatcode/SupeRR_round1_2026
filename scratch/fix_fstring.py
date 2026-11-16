with open('scratch/build_step10_4_restoration.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'full_markdown_text = f"""'
replacement = 'full_markdown_text = """'
assert target in text
text = text.replace(target, replacement)

with open('scratch/build_step10_4_restoration.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Replaced f-string with regular string.")
