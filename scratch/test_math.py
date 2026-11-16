import pymupdf

test_html = """<!DOCTYPE html>
<html>
<head>
<style>
@page { size: letter; margin: 40pt; }
body { font-family: sans-serif; font-size: 10pt; line-height: 1.4; color: #2d3748; }
.formula-card {
    background-color: #f8fafc;
    border: 1pt solid #cbd5e0;
    border-radius: 4pt;
    padding: 10pt 16pt;
    margin: 10pt 0;
    text-align: center;
}
.math-eq {
    font-family: 'Times New Roman', Times, serif;
    font-size: 11pt;
    color: #1a202c;
    margin: 4pt 0;
}
.frac-table {
    display: inline-table;
    vertical-align: middle;
    border-collapse: collapse;
    margin: 0 2pt;
}
.frac-table td {
    padding: 1pt 4pt;
    text-align: center;
    border: none;
    font-family: 'Times New Roman', Times, serif;
    font-size: 10.5pt;
}
.frac-num {
    border-bottom: 1pt solid #2d3748 !important;
}
.frac-den {
}
</style>
</head>
<body>
<h2>Test Formula Display</h2>

<div class="formula-card">
    <div class="math-eq">
        <i>P</i> = &radic;(<i>T</i> &times; <i>L</i><sub>norm</sub>)
    </div>
</div>

<div class="formula-card">
    <div class="math-eq">
        <i>Z</i><sub>bat,1</sub> = 0.45 &times; 
        <table class="frac-table">
            <tr><td class="frac-num">RAR<sub>bat,1</sub> &minus; <i>R</i><sub>par</sub></td></tr>
            <tr><td class="frac-den"><i>R</i><sub>par</sub></td></tr>
        </table>
        + 0.35 &times;
        <table class="frac-table">
            <tr><td class="frac-num"><i>W<sub>t</sub></i> &minus; &mu;<sub><i>W</i></sub></td></tr>
            <tr><td class="frac-den">&sigma;<sub><i>W</i></sub></td></tr>
        </table>
        + 0.20 &times;
        <table class="frac-table">
            <tr><td class="frac-num"><i>W<sub>t</sub></i></td></tr>
            <tr><td class="frac-den">11 &minus; <i>W<sub>t</sub></i></td></tr>
        </table>
    </div>
    <div class="math-eq" style="margin-top: 8pt;">
        <i>T</i><sub>bat,1</sub> = 
        <table class="frac-table">
            <tr><td class="frac-num">100</td></tr>
            <tr><td class="frac-den">1 + exp(&minus;1.20 &times; <i>Z</i><sub>bat,1</sub>)</td></tr>
        </table>
    </div>
</div>

<div class="formula-card">
    <div class="math-eq">
        <b>PWSVA</b><sub><i>p</i></sub><sup>shrunk</sup> = 
        <table class="frac-table">
            <tr><td class="frac-num"><i>N</i><sub>eff, <i>p</i></sub><sup>bat</sup></td></tr>
            <tr><td class="frac-den"><i>N</i><sub>eff, <i>p</i></sub><sup>bat</sup> + 600</td></tr>
        </table>
        &times;
        <table class="frac-table">
            <tr><td class="frac-num">&sum; <i>w<sub>i</sub></i> &times; <i>v</i><sub>bat, <i>i</i></sub></td></tr>
            <tr><td class="frac-den">&sum; <i>w<sub>i</sub></i></td></tr>
        </table>
    </div>
</div>

</body>
</html>
"""

archive = pymupdf.Archive('.')
writer = pymupdf.DocumentWriter('scratch/test_math_render.pdf')
story = pymupdf.Story(html=test_html, archive=archive)

def rectfn(rect_num, filled):
    mediabox = pymupdf.paper_rect('letter')
    rect = pymupdf.Rect(40, 45, mediabox.width - 40, mediabox.height - 45)
    return mediabox, rect, pymupdf.Identity

story.write(writer, rectfn)
writer.close()

doc = pymupdf.open('scratch/test_math_render.pdf')
page = doc[0]
pix = page.get_pixmap(dpi=150)
pix.save('scratch/test_math_render.png')
print('Saved test_math_render.png, total drawings:', len(page.get_drawings()))
