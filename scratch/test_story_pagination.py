import pymupdf

test_html = """<!DOCTYPE html>
<html>
<head>
<style>
@page { size: letter; margin: 40pt; }
body { font-family: sans-serif; font-size: 10pt; }
table { width: 100%; border-collapse: collapse; margin: 10pt 0; }
.header-cell { background-color: #1a365d; color: white; padding: 4pt; font-weight: bold; }
td { border: 1pt solid #ccc; padding: 4pt; }
.figure-container { text-align: center; margin: 8pt 0; }
img.figure-img { max-width: 440pt; max-height: 270pt; }
</style>
</head>
<body>
<h1>Test Title</h1>
<table>
<tr><td class="header-cell">Col 1</td><td class="header-cell">Col 2</td><td class="header-cell">Col 3</td></tr>
<tr><td>A</td><td>B</td><td>C</td></tr>
<tr><td>D</td><td>E</td><td>F</td></tr>
</table>

<div class="figure-container" style="page-break-before: always;">
    <img src="outputs/step_8_eda/figures/fig01_batting_top20_rankings.png" class="figure-img">
    <p>Figure 1</p>
</div>

<div class="figure-container" style="page-break-before: always;">
    <img src="outputs/step_8_eda/figures/fig02_bowling_top20_rankings.png" class="figure-img">
    <p>Figure 2</p>
</div>

<div style="page-break-before: always;">
<table>
<tr><td class="header-cell">Col X</td><td class="header-cell">Col Y</td><td class="header-cell">Col Z</td></tr>
<tr><td>1</td><td>2</td><td>3</td></tr>
</table>
</div>
</body>
</html>
"""

archive = pymupdf.Archive('.')
writer = pymupdf.DocumentWriter('scratch/test_pagination_no_th.pdf')
story = pymupdf.Story(html=test_html, archive=archive)

def rectfn(rect_num, filled):
    mediabox = pymupdf.paper_rect('letter')
    rect = pymupdf.Rect(40, 45, mediabox.width - 40, mediabox.height - 45)
    return mediabox, rect, pymupdf.Identity

story.write(writer, rectfn)
writer.close()

doc = pymupdf.open('scratch/test_pagination_no_th.pdf')
print('Total pages in test:', len(doc))
for i, page in enumerate(doc):
    drawings = page.get_drawings()
    blue_drawings = [d for d in drawings if d.get('fill') == (0.10196078568696976, 0.21176470816135406, 0.364705890417099)]
    print(f'Page {i+1}: total drawings={len(drawings)}, blue table headers={len(blue_drawings)}')
