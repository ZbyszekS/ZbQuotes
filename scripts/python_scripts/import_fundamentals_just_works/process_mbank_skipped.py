# This script shows all csv rows where yf_symbol is in yf_info_skipped.json
from pathlib import Path
import json
import csv

# directory where import_data.py lives
SCRIPT_DIR = Path(__file__).resolve().parent
# ZbQuotes
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent

MBANK_CSV_FILE_NAME = "mbank_foreign.csv"
MBANK_CSV_DATA_PATH = PROJECT_ROOT / "resources" / "data" / "processed_data" / MBANK_CSV_FILE_NAME

YF_ALL_INFO_SKIPPED_FILE_NAME = "yf_info_skipped.json"
YF_ALL_INFO_SKIPPED_DATA_PATH = PROJECT_ROOT / "resources" / "data" / "processed_data" / YF_ALL_INFO_SKIPPED_FILE_NAME

CSV_FOUND_SKIPPED_FILE_NAME = "mbank_foreign_csv_found_skipped.csv"
CSV_FOUND_SKIPPED_DATA_PATH = PROJECT_ROOT / "resources" / "data" / "processed_data" / CSV_FOUND_SKIPPED_FILE_NAME




def show_skipped():
    with open(YF_ALL_INFO_SKIPPED_DATA_PATH, "r", encoding="utf-8") as f:
        skipped = json.load(f)
    with open(MBANK_CSV_DATA_PATH, "r", encoding="utf-8") as f:
        count_found, counter_csv = 0, 1
        all_found = []
        reader = csv.DictReader(f)
        for row in reader:
            yf_ticker = row["yf_symbol"]
            if yf_ticker in skipped:
                count_found += 1
                skipped_row = {"original_number": counter_csv}
                skipped_row.update(row)
                all_found.append(skipped_row)
            counter_csv += 1
    
    print(f"Found: {count_found}, Total: {counter_csv}")
    
    with open(CSV_FOUND_SKIPPED_DATA_PATH, "w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_found[0].keys())
        writer.writeheader()
        writer.writerows(all_found)
    
def main():
    show_skipped()

if __name__ == "__main__":
    main()