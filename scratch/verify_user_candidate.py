import sys
import os

with open('outputs/step_10_3_final_audit/verify_step10_3.py', 'r', encoding='utf-8') as f:
    code = f.read()

target_old = "pdf_path = 'outputs/step_10_methodology_report/step_10_methodology_report.pdf'"
target_new = "pdf_path = 'scratch/step_10_user_candidate_final.pdf'"
code = code.replace(target_old, target_new)

exec(code, {'__name__': '__main__', '__file__': 'test_verify.py'})
