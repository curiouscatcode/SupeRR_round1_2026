import pymupdf, os

fig_rel = 'outputs/step_8_eda/figures/fig01_batting_top20_rankings.png'

html = f"""
<h1>Figure Test</h1>
<p>Top 20 Batters Chart:</p>
<img src="{fig_rel}" style="width: 450pt;">
"""

archive = pymupdf.Archive('.')
writer = pymupdf.DocumentWriter('scratch/test_story_img2.pdf')
story = pymupdf.Story(html=html, archive=archive)

def rectfn(rect_num, filled):
    mediabox = pymupdf.paper_rect('letter')
    rect = pymupdf.Rect(54, 54, mediabox.width - 54, mediabox.height - 54)
    return mediabox, rect, pymupdf.Identity

story.write(writer, rectfn)
writer.close()

doc = pymupdf.open('scratch/test_story_img2.pdf')
print('Success with image via Archive! Pages:', len(doc), 'Images on page 0:', len(doc[0].get_images()))
