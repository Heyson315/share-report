import argparse
from pathlib import Path

import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("output/reports/security/m365_cis_audit.xlsx"),
        help="Path to m365_cis_audit Excel report",
    )
    args = parser.parse_args()

    report = Path(args.report)
    if not report.exists():
        print("Report not found:", report)
        raise SystemExit(1)

    excel_file = pd.ExcelFile(report)
    print("Report:", report)
    print("Sheets:", excel_file.sheet_names)
    for sheet in excel_file.sheet_names:
        sheet_dataframe = excel_file.parse(sheet)
        print(f"\nSheet: {sheet}  shape={sheet_dataframe.shape}")
        print(sheet_dataframe.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
