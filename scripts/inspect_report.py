#!/usr/bin/env python3
"""
SharePoint Report Inspector

Quick inspection tool for SharePoint permissions Excel reports.
Displays sheet names, shapes, and sample data.

Usage:
    python scripts/inspect_report.py
"""
import sys
from pathlib import Path

import pandas as pd

# Configuration
REPORT_PATH = Path("output/reports/business/sharepoint_permissions_report.xlsx")


def main() -> None:
    """Inspect SharePoint permissions Excel report."""
    if not REPORT_PATH.exists():
        print(f"ERROR: Report not found: {REPORT_PATH}", file=sys.stderr)
        sys.exit(1)

    try:
        excel_file = pd.ExcelFile(REPORT_PATH)
        print(f"📊 Report: {REPORT_PATH}")
        print(f"📄 Sheets: {excel_file.sheet_names}\n")

        for sheet in excel_file.sheet_names:
            sheet_dataframe = excel_file.parse(sheet)
            print(f"Sheet: {sheet}  (shape={sheet_dataframe.shape})")
            print(sheet_dataframe.head(5).to_string(index=False))
            print()
    except Exception as e:
        print(f"ERROR: Failed to read report: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
