import pymupdf

test_html = """<!DOCTYPE html>
<html>
<head>
<style>
@page { size: letter; margin: 40pt; }
body { font-family: sans-serif; font-size: 10pt; line-height: 1.4; color: #2d3748; }
.formula-box {
    background-color: #f8fafc;
    border: 1pt solid #cbd5e0;
    border-left: 3pt solid #1a365d;
    border-radius: 3pt;
    padding: 8pt 14pt;
    margin: 10pt 0;
    text-align: center;
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 10.5pt;
    color: #1a202c;
    line-height: 1.6;
}
.formula-title {
    font-family: sans-serif;
    font-size: 8.5pt;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.5pt;
    color: #4a5568;
    margin-bottom: 4pt;
    text-align: left;
}
.math-line {
    margin: 3pt 0;
}
</style>
</head>
<body>
<h2>Math Typography Test</h2>

<div class="formula-box">
    <div class="formula-title">Continuous Pressure Index</div>
    <div class="math-line">
        <i>P</i> = &radic;( <i>T</i> &times; <i>L</i><sub>norm</sub> )
    </div>
</div>

<div class="formula-box">
    <div class="formula-title">Batting Task Difficulty — Innings 1</div>
    <div class="math-line">
        <i>Z</i><sub>bat,1</sub> = 0.45 &times; [ (RAR<sub>bat,1</sub> &minus; <i>R</i><sub>par</sub>) / <i>R</i><sub>par</sub> ] + 0.35 &times; [ (<i>W<sub>t</sub></i> &minus; &mu;<sub><i>W</i></sub>) / &sigma;<sub><i>W</i></sub> ] + 0.20 &times; [ <i>W<sub>t</sub></i> / (11 &minus; <i>W<sub>t</sub></i>) ]
    </div>
    <div class="math-line">
        <i>T</i><sub>bat,1</sub> = 100 / [ 1 + exp(&minus;1.20 &times; <i>Z</i><sub>bat,1</sub>) ]
    </div>
</div>

<div class="formula-box">
    <div class="formula-title">Batting Reliability Metric (PWSVA Shrunk)</div>
    <div class="math-line">
        <i>w<sub>i</sub></i> = ( <i>P<sub>i</sub></i> / 50 )<sup>&alpha;</sup>, &nbsp;&nbsp; with &alpha; = 1.00
    </div>
    <div class="math-line">
        <i>v</i><sub>bat, <i>i</i></sub> = ( <i>R<sub>i</sub></i> &minus; E[<i>R</i> | <i>c<sub>i</sub></i>] ) &minus; &lambda;<sub>eff, <i>i</i></sub> &times; ( <i>W</i><sub>striker, <i>i</i></sub> &minus; E[<i>W</i><sub>bat</sub> | <i>c<sub>i</sub></i>] )
    </div>
    <div class="math-line">
        <b>PWSVA</b><sub><i>p</i></sub><sup>shrunk</sup> = [ <i>N</i><sub>eff, <i>p</i></sub><sup>bat</sup> / ( <i>N</i><sub>eff, <i>p</i></sub><sup>bat</sup> + 600 ) ] &times; [ &sum; <i>w<sub>i</sub></i> &times; <i>v</i><sub>bat, <i>i</i></sub> / &sum; <i>w<sub>i</sub></i> ]
    </div>
</div>

<div class="formula-box">
    <div class="formula-title">Bowling Reliability Metric (SBVA Shrunk)</div>
    <div class="math-line">
        <i>v</i><sub>bowl, <i>i</i></sub> = ( E[<i>R</i><sub>conc</sub> | <i>c<sub>i</sub></i>] &minus; <i>R</i><sub>conc, <i>i</i></sub> ) + &lambda;<sub>eff, <i>i</i></sub> &times; ( <i>W</i><sub>bowl, <i>i</i></sub> &minus; E[<i>W</i><sub>bowl</sub> | <i>c<sub>i</sub></i>] )
    </div>
    <div class="math-line">
        <b>SBVA</b><sub><i>p</i></sub><sup>shrunk</sup> = [ <i>N</i><sub>eff, <i>p</i></sub><sup>bowl</sup> / ( <i>N</i><sub>eff, <i>p</i></sub><sup>bowl</sup> + 500 ) ] &times; [ &sum; <i>w<sub>i</sub></i> &times; <i>v</i><sub>bowl, <i>i</i></sub> / &sum;<sub>legal</sub> <i>w<sub>i</sub></i> ]
    </div>
</div>

</body>
</html>
"""

archive = pymupdf.Archive('.')
writer = pymupdf.DocumentWriter('scratch/test_math_clean.pdf')
story = pymupdf.Story(html=test_html, archive=archive)

def rectfn(rect_num, filled):
    mediabox = pymupdf.paper_rect('letter')
    rect = pymupdf.Rect(40, 45, mediabox.width - 40, mediabox.height - 45)
    return mediabox, rect, pymupdf.Identity

story.write(writer, rectfn)
writer.close()

doc = pymupdf.open('scratch/test_math_clean.pdf')
p = doc[0]
pix = p.get_pixmap(dpi=150)
pix.save('scratch/test_math_clean.png')
print('Saved test_math_clean.png. Total drawings:', len(p.get_drawings()))
print('Text blocks:')
for b in p.get_text('blocks'):
    print(b[4].strip())
