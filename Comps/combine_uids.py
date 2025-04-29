import csv
import os
from pathlib import Path

from comp_rates_config import RECENT_PHASE


def get_unique_uids_from_csvs(file_paths: list[str | Path]) -> set[int]:
    """Returns a set of unique UIDs from multiple CSV files."""
    unique_uids = set[int]()
    for file_path in file_paths:
        with open(file_path, encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            unique_uids.update(int(row["uid"]) for row in reader)
    return unique_uids


csv_files: list[str | Path] = []
if os.path.exists("../data/raw_csvs_real/"):
    csv_files.append("../data/raw_csvs_real/" + RECENT_PHASE + ".csv")
    csv_files.append("../data/raw_csvs_real/" + RECENT_PHASE + "_da.csv")
else:
    csv_files.append("../data/raw_csvs/" + RECENT_PHASE + ".csv")
    csv_files.append("../data/raw_csvs/" + RECENT_PHASE + "_da.csv")

# Usage:
unique_uids = get_unique_uids_from_csvs(csv_files)

print(len(list(unique_uids)))

if os.path.exists("../char_results/uids - Copy.csv"):
    # Read UIDs from the CSV file into a set for fast lookup
    with open("../char_results/uids - Copy.csv") as file:
        csv_reader = csv.reader(file)
        exclude_uids = {int(row[0]) for row in csv_reader}  # Store as integers

    # Filter out UIDs that exist in the CSV
    unique_uids = [uid for uid in unique_uids if uid not in exclude_uids]

with open("../char_results/uids_unique.csv", "w", newline="") as file:
    for uid in list(unique_uids):
        csv.writer(file).writerow([uid])
