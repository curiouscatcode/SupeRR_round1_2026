import os
import glob

print("Searching for occurrences of 642, 186634, 186,634, 183, 255...")

matches_found = []
for root, dirs, files in os.walk('.'):
    # skip .git
    if '.git' in root:
        continue
    for f in files:
        if f.endswith(('.py', '.md', '.csv', '.txt', '.json')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    if '642' in content or '186634' in content or '186,634' in content:
                        print(f"Found in: {path}")
            except Exception as e:
                pass
