#!/usr/bin/env python3
"""
Clean a CSV file by removing comment lines (# ...), blank lines, and repeated headers.
Also normalizes whitespace around commas and trims field whitespace.

Usage (PowerShell):
  python scripts/clean_csv.py --input "data/raw/sharepoint/Hassan Rahman_2025-8-16-20-24-4_1.csv" \\
    --output "data/processed/sharepoint_permissions_clean.csv"

If --input/--output are omitted, defaults will be used for the SharePoint CSV.
"""
from __future__ import annotations

import argparse
import csv
from io import StringIO
from pathlib import Path

DEFAULT_INPUT_PATH = Path("data/raw/sharepoint/Hassan Rahman_2025-8-16-20-24-4_1.csv")
DEFAULT_OUTPUT_PATH = Path("data/processed/sharepoint_permissions_clean.csv")


def clean_csv(input_csv_path: Path, output_csv_path: Path) -> dict:
    """
    Clean CSV file by removing comments, blank lines, and repeated headers.

    Args:
        input_csv_path: Path to the input CSV file to clean.
        output_csv_path: Path where the cleaned CSV will be written.

    Returns:
        Dictionary containing cleaning statistics with keys:
        - input_lines: Total lines read from input
        - output_rows: Data rows written to output
        - comment_lines: Lines removed as comments
        - blank_lines: Empty lines removed
        - skipped_repeated_headers: Duplicate header rows skipped
        - header: The header row as a list
    """
    input_csv_path = Path(input_csv_path)
    output_csv_path = Path(output_csv_path)
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    cleaning_statistics = {
        "input_lines": 0,
        "output_rows": 0,
        "comment_lines": 0,
        "blank_lines": 0,
        "skipped_repeated_headers": 0,
        "header": None,
    }

    # First pass: filter out comment and blank lines, keep original quoting intact
    non_comment_lines = []
    with input_csv_path.open("r", encoding="utf-8-sig", errors="replace") as input_file:
        for raw_line in input_file:
            cleaning_statistics["input_lines"] += 1
            stripped_line = raw_line.strip()
            if not stripped_line:
                cleaning_statistics["blank_lines"] += 1
                continue
            if stripped_line.startswith("#"):
                cleaning_statistics["comment_lines"] += 1
                continue
            non_comment_lines.append(raw_line)

    # Second pass: parse CSV properly respecting quotes
    csv_content_buffer = StringIO("".join(non_comment_lines))
    csv_reader = csv.reader(csv_content_buffer)

    with output_csv_path.open("w", encoding="utf-8", newline="") as output_file:
        csv_writer = csv.writer(output_file, lineterminator="\n")

        header_row = None

        for data_row in csv_reader:
            # Normalize whitespace in each cell
            for cell_index in range(len(data_row)):
                data_row[cell_index] = data_row[cell_index].strip()

            if header_row is None:
                header_row = data_row
                # Strip potential BOM from first header column if still present
                if header_row and header_row[0].startswith("\ufeff"):
                    header_row[0] = header_row[0].lstrip("\ufeff")
                cleaning_statistics["header"] = header_row
                csv_writer.writerow(header_row)
                continue

            # Skip repeated header rows
            if data_row == header_row:
                cleaning_statistics["skipped_repeated_headers"] += 1
                continue

            # Guard against BOM in first data column
            if data_row and data_row[0].startswith("\ufeff"):
                data_row[0] = data_row[0].lstrip("\ufeff")

            csv_writer.writerow(data_row)
            cleaning_statistics["output_rows"] += 1

    return cleaning_statistics


def main():
    """Main entry point for the CSV cleaning script."""
    argument_parser = argparse.ArgumentParser(
        description="Clean CSV files by removing comments, blank lines, and repeated headers."
    )
    argument_parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH, help="Input CSV path")
    argument_parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Output CSV path")
    parsed_args = argument_parser.parse_args()

    cleaning_statistics = clean_csv(parsed_args.input, parsed_args.output)

    print("CSV cleaned successfully:")
    print(f"  Input lines:            {cleaning_statistics['input_lines']}")
    print(f"  Comment lines removed:  {cleaning_statistics['comment_lines']}")
    print(f"  Blank lines removed:    {cleaning_statistics['blank_lines']}")
    print(f"  Repeated headers skip:  {cleaning_statistics['skipped_repeated_headers']}")
    print(f"  Output data rows:       {cleaning_statistics['output_rows']}")
    print(f"  Header:                 {cleaning_statistics['header']}")
    print(f"  Output file:            {parsed_args.output}")


if __name__ == "__main__":
    main()
