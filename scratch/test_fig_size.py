import pymupdf

test_html = """<!DOCTYPE html>
<html>
<head>
<style>
@page { size: letter; margin: 34pt 40pt; }
body { font-family: sans-serif; font-size: 8.8pt; }
.figure-container { text-align: center; margin: 4pt 0; }
img.fig { width: 380pt; }
p.cap { font-size: 7.5pt; margin: 2pt 0; }
</style>
</head>
<body>
<h2>Test Figure Page</h2>
<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig01_batting_top20_rankings.png" class="fig">
    <p class="cap">Figure 1: Top 20 Batting</p>
</div>
<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig02_bowling_top20_rankings.png" class="fig">
    <p class="cap">Figure 2: Top 20 Bowling</p>
</div>
</body>
</html>
"""

archive = pymupdf.Archive('.')
writer = pymupdf.DocumentWriter('scratch/test_fig_height.pdf')
story = pymupdf.Story(html=test_html, archive=archive)

def rectfn(rect_num, filled):
    mediabox = pymupdf.paper_rect('letter')
    rect = pymupdf.Rect(40, 34, mediabox.width - 40, mediabox.height - 34)
    return mediabox, rect, pymupdf.Identity

story.write(writer, rectfn)
writer.close()

doc = pymupdf.open('scratch/test_fig_height.pdf')
print('Total pages in test:', len(doc))
for i, page in enumerate(doc):
    for b in page.get_text('blocks'):
        print(f'P{i+1}: [{b[1]:.1f} - {b[3]:.1f}] {b[4].strip()}')
