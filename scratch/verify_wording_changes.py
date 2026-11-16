import pymupdf

md_path = 'outputs/step_10_methodology_report/step_10_methodology_report.md'
pdf_path = 'outputs/step_10_methodology_report/step_10_methodology_report.pdf'

with open(md_path, 'r', encoding='utf-8') as f:
    md_text = f.read()

doc = pymupdf.open(pdf_path)
pdf_text = "\n".join([p.get_text() for p in doc])

phrases = [
    ("reduce small-sample instability through shrinkage", "Claim 1 (Shrinkage)"),
    ("strong pressure-weighted performance, including positive death-over results", "Claim 2 (Death Overs)"),
    ("addresses several limitations of conventional cricket metrics", "Claim 3 (Conventional Metrics)")
]

print("=== CHECKING REVISED WORDING ===")
for phrase, desc in phrases:
    in_md = phrase in md_text
    in_pdf = phrase in pdf_text
    print(f"{desc}:")
    print(f"  In Markdown: {in_md}")
    print(f"  In PDF     : {in_pdf}")
    assert in_md, f"Missing '{phrase}' from Markdown!"
    assert in_pdf, f"Missing '{phrase}' from PDF!"

print("\n=== CHECKING ABSENCE OF OVERSTATED CLAIMS ===")
overstated = [
    "eliminate small-sample noise",
    "peerless death-over containment",
    "resolves traditional cricket metric distortions"
]
for phrase in overstated:
    in_md = phrase in md_text.lower()
    in_pdf = phrase in pdf_text.lower()
    print(f"'{phrase}': absent from MD={not in_md}, absent from PDF={not in_pdf}")
    assert not in_md, f"Overstated phrase '{phrase}' still found in Markdown!"
    assert not in_pdf, f"Overstated phrase '{phrase}' still found in PDF!"

print("\nALL PHRASES VERIFIED PERFECTLY!")
