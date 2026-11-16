import json
import hashlib
import os

with open('scratch/baseline_protected_hashes.json', 'r', encoding='utf-8') as f:
    protected_hashes = json.load(f)

print(f"=== VERIFYING {len(protected_hashes)} PROTECTED BASELINE FILES ===")
all_pass = True
for fpath, expected_hash in protected_hashes.items():
    if not os.path.exists(fpath):
        print(f"FAIL: Missing file {fpath}")
        all_pass = False
        continue
    with open(fpath, 'rb') as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    if actual_hash != expected_hash:
        print(f"FAIL: Hash mismatch for {fpath}")
        print(f"  Expected: {expected_hash}")
        print(f"  Actual:   {actual_hash}")
        all_pass = False
    else:
        pass

if all_pass:
    print(f"SUCCESS: All {len(protected_hashes)} protected baseline files match their frozen SHA-256 hashes 100%!")
