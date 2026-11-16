import pymupdf

doc = pymupdf.open()
page = doc.new_page()
rect = pymupdf.Rect(50, 50, 500, 200)
html = '''
<p style="font-family: sans-serif; font-size: 14pt;">
Sans: T20I vs T201<br>
Serif: T20<span style="font-family: serif;">I</span> vs T201<br>
Times: T20<span style="font-family: 'Times New Roman', serif;">I</span> vs T201<br>
Small-caps / styled: T20<span style="font-size: 11pt; font-weight: bold;">I</span> vs T201
</p>
'''
page.insert_htmlbox(rect, html)
doc.save('scratch/test_font.pdf')
print('Saved test_font.pdf successfully')
