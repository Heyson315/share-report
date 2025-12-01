#!/usr/bin/env python3
"""
CIS Report Inspector

Quick inspection tool for M365 CIS audit Excel reports.
Displays sheet names, shapes, and sample data.

Usage:
    python scripts/inspect_cis_report.py [--report path/to/report.xlsx]
"""
import argparse
import sys
from pathlib import Path

import pandas as pd


def main() -> None:
    """Inspect M365 CIS audit Excel report."""
    parser = argparse.ArgumentParser(description="Inspect M365 CIS audit Excel report")
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("output/reports/security/m365_cis_audit.xlsx"),
        help="Path to M365 CIS audit Excel report",
    )
    args = parser.parse_args()

    report = Path(args.report)
    if not report.exists():
        print(f"ERROR: Report not found: {report}", file=sys.stderr)
        sys.exit(1)

    try:
        excel_file = pd.ExcelFile(report)
        print(f"📊 Report: {report}")
        print(f"📄 Sheets: {excel_file.sheet_names}\n")

        for sheet in excel_file.sheet_names:
            sheet_dataframe = excel_file.parse(sheet)
            print(f"Sheet: {sheet}  (shape={sheet_dataframe.shape})")
            print(sheet_dataframe.head(10).to_string(index=False))
            print()
    except Exception as e:
        print(f"ERROR: Failed to read report: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
