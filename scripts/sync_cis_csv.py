"""
Sync M365 CIS audit JSON data to a CSV file format.

This script reads the audit JSON file and writes a CSV with standardized columns,
which can be useful for importing into spreadsheets or other tools.
"""

import json
from pathlib import Path

import pandas as pd

JSON_INPUT_PATH = Path("output/reports/security/m365_cis_audit.json")
CSV_OUTPUT_PATH = Path("output/reports/security/m365_cis_audit.csv")

# Standard column ordering for CIS audit data
CIS_AUDIT_COLUMNS = [
    "ControlId",
    "Title",
    "Severity",
    "Expected",
    "Actual",
    "Status",
    "Evidence",
    "Reference",
    "Timestamp",
]


def main():
    """Main entry point for syncing JSON audit data to CSV format."""
    audit_data = json.loads(JSON_INPUT_PATH.read_text(encoding="utf-8-sig"))

    # Normalize to list format
    if isinstance(audit_data, dict):
        control_records = [audit_data]
    else:
        control_records = audit_data

    controls_dataframe = pd.DataFrame(control_records)

    # Reorder columns: standard columns first, then any extra columns at the end
    ordered_columns = [column for column in CIS_AUDIT_COLUMNS if column in controls_dataframe.columns] + [
        column for column in controls_dataframe.columns if column not in CIS_AUDIT_COLUMNS
    ]

    controls_dataframe = controls_dataframe[ordered_columns]

    CSV_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    controls_dataframe.to_csv(CSV_OUTPUT_PATH, index=False, encoding="utf-8")
    print("CSV synced from JSON:", CSV_OUTPUT_PATH)


if __name__ == "__main__":
    main()
