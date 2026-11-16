import os
from PIL import Image
import numpy as np
import glob

print("=== PAGE-BY-PAGE VISUAL INSPECTION OF FINAL PDF PAGES ===")

pages = sorted(glob.glob('scratch/pdf_pages_final/page_*.png'))
print(f"Total rendered pages: {len(pages)}")

for p in pages:
    im = Image.open(p).convert('RGB')
    arr = np.array(im)
    w, h = im.size
    
    # 1. Dark pixels (text/lines: < 80 in all channels)
    dark_pixels = np.sum((arr[:, :, 0] < 80) & (arr[:, :, 1] < 80) & (arr[:, :, 2] < 80))
    
    # 2. Check for solid blue blocks (> 180 blue, < 100 red, < 160 green)
    solid_blue = np.sum((arr[:, :, 2] > 180) & (arr[:, :, 0] < 100) & (arr[:, :, 1] < 160))
    
    # 3. Header check (top 100 px)
    header_pixels = np.sum(arr[:100, :, :] < 150)
    
    # 4. Footer check (bottom 100 px)
    footer_pixels = np.sum(arr[-100:, :, :] < 150)
    
    pname = os.path.basename(p)
    print(f"{pname} ({w}x{h}): dark_px={dark_pixels}, solid_blue={solid_blue}, header_px={header_pixels}, footer_px={footer_pixels}")

print("\nAll pages inspected successfully.")
