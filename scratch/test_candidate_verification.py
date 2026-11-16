import sys
import os
import re
import hashlib
import pandas as pd
import pymupdf

# Test scratch/step_10_4_candidate.pdf against verify_step10_3 logic
with open('outputs/step_10_3_final_audit/verify_step10_3.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace pdf_path
target_old = "pdf_path = 'outputs/step_10_methodology_report/step_10_methodology_report.pdf'"
target_new = "pdf_path = 'scratch/step_10_4_candidate.pdf'"
assert target_old in code, "Target string not found in verify_step10_3.py"
code_modified = code.replace(target_old, target_new)

exec(code_modified, {'__name__': '__main__', '__file__': 'scratch/test_candidate_verification.py'})
