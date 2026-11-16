import pymupdf

doc = pymupdf.open()
page = doc.new_page()
rect = pymupdf.Rect(50, 50, 500, 300)
html = '''
<style>
.formula-card-mono {
    background-color: #f7fafc;
    border-left: 3pt solid #3182ce;
    padding: 5pt 8pt;
    font-family: "Courier New", Courier, monospace;
    font-size: 8.5pt;
}
.formula-card-clean {
    background-color: #f8fafc;
    border: 1pt solid #e2e8f0;
    border-left: 3.5pt solid #3182ce;
    padding: 6pt 10pt;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 9pt;
    color: #1a202c;
}
</style>
<div class="formula-card-mono">
P(S<sub>t</sub>) = &radic;( T(S<sub>t</sub>) &times; L<sub>norm</sub>(S<sub>t</sub>) ) &isin; [0, 100]
</div>
<br>
<div class="formula-card-clean">
<b>P</b>(<i>S<sub>t</sub></i>) = [ <b>T</b>(<i>S<sub>t</sub></i>) &times; <i>L</i><sub>norm</sub>(<i>S<sub>t</sub></i>) ]<sup>1/2</sup> = &radic;( <b>T</b>(<i>S<sub>t</sub></i>) &times; <i>L</i><sub>norm</sub>(<i>S<sub>t</sub></i>) ) &isin; [0, 100]
</div>
'''
page.insert_htmlbox(rect, html)
doc.save('scratch/test_math.pdf')
print('Text extracted:')
print(doc[0].get_text())
