import pymupdf

# Let's inspect where page breaks occur and how we can optimize them
doc = pymupdf.open('outputs/step_10_methodology_report/step_10_methodology_report.pdf')
print("Page count:", len(doc))
for i, page in enumerate(doc):
    rect = page.rect
    blocks = page.get_text('blocks')
    # Filter out header and footer blocks
    content_blocks = [b for b in blocks if b[1] > 35 and b[3] < rect.height - 35]
    if content_blocks:
        top_y = min(b[1] for b in content_blocks)
        bottom_y = max(b[3] for b in content_blocks)
        span_y = bottom_y - top_y
        print(f"Page {i+1}: content Y=[{top_y:.1f}, {bottom_y:.1f}], height={span_y:.1f} pt ({len(content_blocks)} blocks)")
    else:
        print(f"Page {i+1}: EMPTY!")
