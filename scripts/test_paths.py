import os
from pathlib import Path

# directory where import_data.py lives
# ZbQuotes root directory
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
print(f"SCRIPT_DIR: {SCRIPT_DIR}")
print(f"PROJECT_ROOT: {PROJECT_ROOT}")