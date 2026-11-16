import os
import pymupdf

# Test rendering a single page with the 2 images from Page 8 and Page 11
html = """<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: sans-serif; margin: 0; padding: 0; }
.figure-container { text-align: center; margin-top: 4pt; margin-bottom: 6pt; }
.figure-container img { max-width: 98%; height: auto; border: 0.5pt solid #cbd5e0; }
.figure-caption { font-size: 7.2pt; font-style: italic; color: #718096; margin-top: 2pt; }
.page-break { page-break-after: always; }
</style>
</head>
<body>
<h2>Test Page 8</h2>
<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig03_batting_score_vs_sample_size.png" alt="Batting Shrinkage Funnel" style="max-height: 280pt;">
    <div class="figure-caption">Figure 3: Batting Empirical Bayes Shrinkage Funnel (K = 600).</div>
</div>
<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig04_bowling_score_vs_sample_size.png" alt="Bowling Shrinkage Funnel" style="max-height: 280pt;">
    <div class="figure-caption">Figure 4: Bowling Empirical Bayes Shrinkage Funnel (K = 500).</div>
</div>
<div class="page-break"></div>
<h2>Test Page 11</h2>
<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig10_batting_phase_heatmap.png" alt="Batting Phase Heatmap" style="max-height: 280pt;">
    <div class="figure-caption">Figure 7: Batting Phase Performance Heatmap.</div>
</div>
<div class="figure-container">
    <img src="outputs/step_8_eda/figures/fig11_bowling_phase_heatmap.png" alt="Bowling Phase Heatmap" style="max-height: 280pt;">
    <div class="figure-caption">Figure 8: Bowling Phase Performance Heatmap.</div>
</div>
</body>
</html>
"""

raw_path = "scratch/test_images_out.pdf"
archive = pymupdf.Archive('.')
writer = pymupdf.DocumentWriter(raw_path)
story = pymupdf.Story(html=html, archive=archive)

def rectfn(rect_num, filled):
    mediabox = pymupdf.paper_rect('letter')
    rect = pymupdf.Rect(40, 34, mediabox.width - 40, mediabox.height - 34)
    return mediabox, rect, pymupdf.Identity

story.write(writer, rectfn)
writer.close()

doc = pymupdf.open(raw_path)
print("Rendered test PDF total pages:", len(doc))
for i, p in enumerate(doc):
    imgs = p.get_images()
    print(f"Page {i+1}: images count = {len(imgs)}, text = {repr(p.get_text()[:60])}")
