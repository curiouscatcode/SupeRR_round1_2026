import os
import sys
import gc
import re
import pandas as pd
import pymupdf

# Load build_step10_4_restoration.py
with open('scratch/build_step10_4_restoration.py', 'r', encoding='utf-8') as f:
    script_text = f.read()

# Let's inspect how the HTML template is built inside build_step10_4_restoration.py
print("Script length:", len(script_text))
