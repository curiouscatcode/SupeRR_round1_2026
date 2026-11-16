with open('scratch/build_step10_4_restoration.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'page-break' in l:
        print(f"Line {i+1}: {l.strip()}")

# Also print lines from the last page-break to the end of html string
last_pb = [i for i, l in enumerate(lines) if 'page-break' in l][-1]
print(f"\nLast page-break at line {last_pb+1}. Total lines: {len(lines)}")
