import pymupdf

test_html = """<!DOCTYPE html>
<html>
<head>
<style>
@page { size: letter; margin: 40pt; }
body { font-family: sans-serif; font-size: 10pt; line-height: 1.4; color: #2d3748; }
.formula-box {
    border: 1pt solid #cbd5e0;
    padding: 8pt 14pt;
    margin: 8pt 0;
    text-align: center;
}
.eq-table {
    margin: 0 auto;
    border-collapse: collapse;
}
.eq-table td {
    padding: 2pt 3pt;
    vertical-align: middle;
    text-align: center;
    border: none;
    font-family: serif;
    font-size: 10pt;
}
.frac-table {
    border-collapse: collapse;
    margin: 0 2pt;
}
.frac-table td {
    padding: 1pt 4pt;
    text-align: center;
    border: none;
    font-family: serif;
    font-size: 9.5pt;
}
.frac-num {
    border-bottom: 0.8pt solid #2d3748 !important;
}
</style>
</head>
<body>
<h2>Test Single Row Equation</h2>

<div class="formula-box">
    <table class="eq-table">
        <tr>
            <td><i>Z</i><sub>bat,1</sub> = 0.45 &times;</td>
            <td>
                <table class="frac-table">
                    <tr><td class="frac-num">RAR<sub>bat,1</sub> &minus; <i>R</i><sub>par</sub></td></tr>
                    <tr><td><i>R</i><sub>par</sub></td></tr>
                </table>
            </td>
            <td>+ 0.35 &times;</td>
            <td>
                <table class="frac-table">
                    <tr><td class="frac-num"><i>W<sub>t</sub></i> &minus; &mu;<sub><i>W</i></sub></td></tr>
                    <tr><td>&sigma;<sub><i>W</i></sub></td></tr>
                </table>
            </td>
            <td>+ 0.20 &times;</td>
            <td>
                <table class="frac-table">
                    <tr><td class="frac-num"><i>W<sub>t</sub></i></td></tr>
                    <tr><td>11 &minus; <i>W<sub>t</sub></i></td></tr>
                </table>
            </td>
        </tr>
    </table>
    <table class="eq-table" style="margin-top: 6pt;">
        <tr>
            <td><i>T</i><sub>bat,1</sub> =</td>
            <td>
                <table class="frac-table">
                    <tr><td class="frac-num">100</td></tr>
                    <tr><td>1 + exp(&minus;1.20 &times; <i>Z</i><sub>bat,1</sub>)</td></tr>
                </table>
            </td>
        </tr>
    </table>
</div>

</body>
</html>
"""

archive = pymupdf.Archive('.')
writer = pymupdf.DocumentWriter('scratch/test_math_row.pdf')
story = pymupdf.Story(html=test_html, archive=archive)

def rectfn(rect_num, filled):
    mediabox = pymupdf.paper_rect('letter')
    rect = pymupdf.Rect(40, 45, mediabox.width - 40, mediabox.height - 45)
    return mediabox, rect, pymupdf.Identity

story.write(writer, rectfn)
writer.close()

doc = pymupdf.open('scratch/test_math_row.pdf')
p = doc[0]
for b in p.get_text('blocks'):
    print(b)
pix = p.get_pixmap(dpi=150)
pix.save('scratch/test_math_row.png')
print('Saved test_math_row.png')
