# CSV Log Comparator

This Python tool helps you manage and compare CSV log files stored locally. It is designed to be beginner-friendly, modular, and easy to extend.

## Features

- Automatically **renames** CSV files by prepending their **modification date and time** (if missing).
- Organizes renamed CSV files into **subfolders by log type** (e.g., 'logs/digital/').
- Lets you **interactively choose two versions** of the same log type to compare.
- Compares rows using a unique key (`id` column by default).
- Outputs added, removed, and changed rows with full content and field-specific differences.
- Uses only built-in Python modules (no installation required).

## Requirements

- Python 3.x
- No external libraries needed; uses only standard Python modules.

## Setup

1. Place your CSV log files into the `logs` folder.
2. If the filenames do not start with a timestamp (`YYYY-MM-DD_HH-MM_`), the script will:
   - Automatically detect their last modified time,
   - Prepend that to the filename.
3. Adjust the `DELIMITER` in the script if your CSV uses something other than `;`.

## Note

- When copying text from the terminal, avoid using **Ctrl+C** as it will stop the script.  
- On Windows, use the terminal's **Edit → Mark** feature (right-click the title bar) to select and copy text without interrupting the program.  
- In other terminals like VS Code’s integrated terminal or Git Bash, you can usually select text and press **Ctrl+Shift+C** or right-click → Copy to copy safely.  
- Use **Ctrl+C** only when you want to exit the script.

## Running

Run the script from the command line:

```bash
python test-version1.py
