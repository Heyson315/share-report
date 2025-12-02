import argparse
import json
import sys
from pathlib import Path

import pandas as pd

DEFAULT_JSON_INPUT_PATH = Path("output/reports/security/m365_cis_audit.json")


def build_report(json_input_path: Path, excel_output_path: Path = None) -> None:
    """
    Build an Excel report from M365 CIS audit JSON results.

    Args:
        json_input_path: Path to the audit JSON file containing CIS control results.
        excel_output_path: Path for the output Excel file. If None, auto-generates
                          based on the JSON filename.
    """
    if excel_output_path is None:
        # Auto-name Excel based on JSON filename
        excel_output_path = json_input_path.with_suffix(".xlsx")
    json_input_path = Path(json_input_path)
    excel_output_path = Path(excel_output_path)

    # Validate input file exists
    if not json_input_path.exists():
        print(f"ERROR: Input file not found: {json_input_path}", file=sys.stderr)
        sys.exit(1)

    excel_output_path.parent.mkdir(parents=True, exist_ok=True)

    # Handle potential UTF-8 BOM from PowerShell's UTF8 encoding
    try:
        audit_data = json.loads(json_input_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as json_error:
        print(f"ERROR: Invalid JSON in {json_input_path}: {json_error}", file=sys.stderr)
        sys.exit(1)
    except (PermissionError, UnicodeDecodeError) as file_error:
        print(f"ERROR: Cannot read {json_input_path}: {file_error}", file=sys.stderr)
        sys.exit(1)
    except Exception as unexpected_error:
        print(
            f"ERROR: Unexpected error reading {json_input_path}: {unexpected_error}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Normalize data to list format
    if isinstance(audit_data, dict):
        # In case it's a single object
        control_records = [audit_data]
    else:
        control_records = audit_data

    controls_dataframe = pd.DataFrame(control_records)

    # Create Overview sheet with status/severity breakdown
    status_severity_overview = (
        controls_dataframe.groupby(["Status", "Severity"])
        .size()
        .reset_index(name="Count")
        .sort_values(["Severity", "Status", "Count"], ascending=[True, True, False])
    )

    # Create detailed Controls sheet with all columns
    control_details_columns = [
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
    controls_detail_dataframe = controls_dataframe[control_details_columns]

    with pd.ExcelWriter(excel_output_path, engine="openpyxl") as excel_writer:
        status_severity_overview.to_excel(excel_writer, sheet_name="Overview", index=False)
        controls_detail_dataframe.to_excel(excel_writer, sheet_name="Controls", index=False)

    print("Excel report written:", excel_output_path)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description="Convert M365 CIS audit JSON to Excel report.")
    argument_parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_JSON_INPUT_PATH,
        help="Path to CIS audit JSON",
    )
    argument_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path to Excel output (optional, auto-names from JSON if omitted)",
    )
    parsed_args = argument_parser.parse_args()
    build_report(parsed_args.input, parsed_args.output)
