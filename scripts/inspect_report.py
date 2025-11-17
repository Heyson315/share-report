from pathlib import Path

import pandas as pd

report = Path("output/reports/business/sharepoint_permissions_report.xlsx")
if not report.exists():
    print("Report not found:", report)
    raise SystemExit(1)

excel_file = pd.ExcelFile(report)
print("Report:", report)
print("Sheets:", excel_file.sheet_names)
for sheet in excel_file.sheet_names:
    sheet_dataframe = excel_file.parse(sheet)
    print(f"\nSheet: {sheet}  shape={sheet_dataframe.shape}")
    print(sheet_dataframe.head(5).to_string(index=False))
