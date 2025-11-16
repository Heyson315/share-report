import json
from pathlib import Path

import pandas as pd

JSON_PATH = Path("output/reports/security/m365_cis_audit.json")
CSV_PATH = Path("output/reports/security/m365_cis_audit.csv")

COLUMNS = ["ControlId", "Title", "Severity", "Expected", "Actual", "Status", "Evidence", "Reference", "Timestamp"]


def main():
    data = json.loads(JSON_PATH.read_text(encoding="utf-8-sig"))
    if isinstance(data, dict):
        rows = [data]
    else:
        rows = data
    controls_dataframe = pd.DataFrame(rows)
    # Reorder columns if present; include any extras at the end
    cols = [c for c in COLUMNS if c in controls_dataframe.columns] + [
        c for c in controls_dataframe.columns if c not in COLUMNS
    ]
    controls_dataframe = controls_dataframe[cols]
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    controls_dataframe.to_csv(CSV_PATH, index=False, encoding="utf-8")
    print("CSV synced from JSON:", CSV_PATH)


if __name__ == "__main__":
    main()
