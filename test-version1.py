"""
CSV Log Comparator

This script automates renaming, organizing, and comparing CSV log files stored in the 'logs' folder.

Features:
- Automatically prepends modification datetime to CSV filenames missing it.
- Groups CSV files by log type parsed from filenames.
- Organizes CSV files into subfolders named after their log type (e.g., 'logs/digital/').
- Allows user to select two versions of the same log type to compare.
- Compares rows by a unique key column (default 'id').
- Outputs added, removed, and changed rows in a readable console report.

Usage:
- Place CSV log files in the 'logs' folder.
- Run this script.
- Follow prompts to select log type and versions.
"""

import os  # For getting file modification time (os.path.getmtime)
import csv  # To read CSV files with DictReader (handles CSV rows as dicts)
from pathlib import Path  # For clean path handling and directory iteration
from datetime import datetime  # To convert timestamps to readable date/time and format strings
import re  # To parse and extract date/time and log type info from filenames using regular expression
from collections import defaultdict  # To group log files by type conveniently without key errors

LOGS_FOLDER = Path("logs")
DELIMITER = ";"  # Adjust if your CSV uses another delimiter

def extract_prefix_and_type(filename):
    """
    Extract date/time prefix and log type from filename.
    
    Expected filename format:
        YYYY-MM-DD_HH-MM_<logtype>.csv

    Args:
        filename (str): Name of the CSV file.

    Returns:
        tuple: (date_time_str, log_type_str) if matched, else (None, None).
    """
    match = re.match(r"^(\d{4}-\d{2}-\d{2}_\d{2}-\d{2})_(.+)\.csv$", filename)
    if match:
        date_time, log_type = match.groups()
        return date_time, log_type
    else:
        return None, None
    
def list_log_folders_and_files(base_folder):
    """
    Scan subfolders in the base logs folder and list CSVs sorted by date.

    Returns:
        dict: { log_type (folder name): [ (datetime_str, Path), ... ] }
    """
    logs = {}
    for subfolder in base_folder.iterdir():
        if subfolder.is_dir():
            log_type = subfolder.name
            entries = []
            for file_path in subfolder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() == ".csv":
                    dt_str, _ = extract_prefix_and_type(file_path.name)
                    if dt_str:
                        entries.append((dt_str, file_path))
            if entries:
                entries.sort(key=lambda x: x[0], reverse=True)
                logs[log_type] = entries
    return logs

def load_csv_to_dict(file_path, key_column='id'):
    """
    Load CSV data into a dictionary keyed by a unique column.

    Args:
        file_path (Path): Path to the CSV file.
        key_column (str): Column name to use as dictionary key (default 'id').

    Returns:
        dict: { key_value: {column_name: cell_value, ...} }
    """
    data = {}
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=DELIMITER)
        for row in reader:
            key = row.get(key_column)
            if key is not None:
                data[key] = row
    return data

def compare_dicts(old_data, new_data):
    """
    Compare two CSV data dictionaries to find added, removed, and changed rows.

    Args:
        old_data (dict): Data from the old CSV {key: row_dict}.
        new_data (dict): Data from the new CSV {key: row_dict}.

    Returns:
        tuple:
            - added (set): Keys present only in new_data.
            - removed (set): Keys present only in old_data.
            - changed (dict): Keys with differing values, mapping to dict of changed columns:
                { key: {column: (old_value, new_value), ...} }
    """
    old_keys = set(old_data.keys())
    new_keys = set(new_data.keys())

    added = new_keys - old_keys
    removed = old_keys - new_keys
    changed = {}

    common = old_keys & new_keys
    for key in common:
        old_row = old_data[key]
        new_row = new_data[key]
        diffs = {}
        for col in old_row.keys():
            if old_row[col] != new_row.get(col):
                diffs[col] = (old_row[col], new_row.get(col))
        if diffs:
            changed[key] = diffs

    return added, removed, changed

def print_comparison_results(added, removed, changed, old_data, new_data):
    """
    Print a detailed comparison report to the console, showing added, removed,
    and changed rows with full row data and specific column changes.

    Args:
        added (set): Keys added in new_data.
        removed (set): Keys removed from old_data.
        changed (dict): Keys with changed columns and their old/new values.
        old_data (dict): Old CSV data.
        new_data (dict): New CSV data.
    """
    # Determine consistent column order from available data
    sample_data = old_data or new_data 
    columns = list(next(iter(sample_data.values())).keys())

    print("\n=== Comparison Results ===\n")

    if added:
        print(f"Added rows ({len(added)}):")
        for key in added:
            new_row = new_data[key]
            new_line = DELIMITER.join(new_row[col] for col in columns)
            print(f"  + {key}:")
            print(f"    NEW: {new_line}")
    else:
        print("No added rows.")

    if removed:
        print(f"\nRemoved rows ({len(removed)}):")
        for key in removed:
            old_row = old_data[key]
            old_line = DELIMITER.join(old_row[col] for col in columns)
            print(f"  - {key}:")
            print(f"    OLD: {old_line}")
    else:
        print("\nNo removed rows.")

    if changed:
        print(f"\nChanged rows ({len(changed)}):")
        for key, diffs in changed.items():
            print(f"  * {key}:")
            for col, (old_val, new_val) in diffs.items():
                print(f"      {col}: '{old_val}' -> '{new_val}'")
            old_line = DELIMITER.join(old_data[key][col] for col in columns)
            new_line = DELIMITER.join(new_data[key][col] for col in columns)

            print(f"    OLD: {old_line}")
            print(f"    NEW: {new_line}")
    else:
        print("\nNo changed rows.")

def get_modification_date(file_path):
    """
    Get the last modification datetime of a file.

    Args:
        file_path (Path): File path.

    Returns:
        datetime: Modification datetime.
    """
    timestamp = os.path.getmtime(file_path)
    return datetime.fromtimestamp(timestamp)

def file_starts_with_date(filename):
    """
    Check if a filename starts with a datetime prefix in the format YYYY-MM-DD_HH-MM_.

    Args:
        filename (str): Filename to check.

    Returns:
        bool: True if filename starts with date/time prefix, else False.
    """
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}_", filename))

def rename_files_with_date_prefix(folder):
    """
    Rename files in a folder by prepending their modification datetime if not already present.

    Args:
        folder (Path): Folder containing files to rename.
    """
    for file_path in folder.iterdir():
        if file_path.is_file():
            original_name = file_path.name
            if file_starts_with_date(original_name):
                print(f"Skipping (already dated): {original_name}")
                continue

            mod_date = get_modification_date(file_path).strftime("%Y-%m-%d_%H-%M")
            new_name = f"{mod_date}_{original_name}"
            new_path = file_path.with_name(new_name)

            # Handle name collisions by appending counter suffix
            counter = 1
            while new_path.exists():
                new_name = f"{mod_date}_{counter}_{original_name}"
                new_path = file_path.with_name(new_name)
                counter += 1

            print(f"Renaming '{original_name}' -> '{new_name}'")
            file_path.rename(new_path)

def organize_files_by_log_type(folder):
    """
    Organizes renamed CSV log files into subfolders by log type.

    Each file is expected to be named in the format:
        YYYY-MM-DD_HH-MM_<logtype>.csv

    The function:
    - Extracts the log type from the filename.
    - Creates a subfolder (e.g., logs/digital/) if it does not exist.
    - Moves the file into the corresponding subfolder.
    - Avoids overwriting files by adding a counter if duplicates exist.

    Args:
        folder (Path): The parent folder containing the renamed CSV files.
    """
    for file_path in folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == ".csv":
            _, log_type = extract_prefix_and_type(file_path.name)
            if log_type:
                target_folder = folder / log_type
                target_folder.mkdir(parents = True, exist_ok=True)
                new_path = target_folder / file_path.name

                # If file already exists in the target folder, avoid overwriting
                counter = 1
                while new_path.exists():
                    new_filename = f"{file_path.stem}_{counter}{file_path.suffix}"
                    new_path = target_folder / new_filename
                    counter += 1
                
                try:
                    print(f"Moving '{file_path.name}' -> '{new_path}'")
                    file_path.rename(new_path)
                except Exception as e:
                    print(f"Failed to move '{file_path.name}' to '{new_path}': {e}")
                

def main():
    """
    Main program execution:
    - Rename files in the logs folder if needed.
    - List available log types.
    - Let user select log type and two versions to compare.
    - Load, compare, and print differences.
    """
    rename_files_with_date_prefix(LOGS_FOLDER)
    organize_files_by_log_type(LOGS_FOLDER) 
    logs = list_log_folders_and_files(LOGS_FOLDER)
    if not logs:
        print("No log files found in logs subfolders.")
        return

    print("Available log types:")
    for i, log_type in enumerate(logs.keys(), start=1):
        print(f"{i}. {log_type}")

    try:
        choice = int(input("\nSelect a log type by number: "))
        selected_log_type = list(logs.keys())[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    versions = logs[selected_log_type]
    print(f"\nAvailable versions for '{selected_log_type}':")
    for i, (dt, path) in enumerate(versions, start=1):
        print(f"{i}. {dt} — {path.name}")

    try:
        old_idx = int(input("\nSelect OLD version number to compare: "))
        new_idx = int(input("Select NEW version number to compare: "))
        if old_idx < 1 or old_idx > len(versions) or new_idx < 1 or new_idx > len(versions):
            raise IndexError
    except (ValueError, IndexError):
        print("Invalid version selection.")
        return

    old_file = versions[old_idx - 1][1]
    new_file = versions[new_idx - 1][1]

    print(f"\nLoading files:\n  OLD: {old_file}\n  NEW: {new_file}")

    old_data = load_csv_to_dict(old_file, key_column='id')
    new_data = load_csv_to_dict(new_file, key_column='id')

    added, removed, changed = compare_dicts(old_data, new_data)
    print_comparison_results(added, removed, changed, old_data, new_data)

try:
    while True:
        main()
        again = input("\nPress Enter to compare again, or type 'q' to quit: ").strip().lower()
        if again == 'q':
            print("Exiting.")
            break
except KeyboardInterrupt: # Beware: Using Ctrl+C will exit the script and is not used for copying in the terminal. More info in README.
    print("\nExited with Ctrl+C.")




