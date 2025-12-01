#!/usr/bin/env python3
"""
Processed CSV Inspector

Quick inspection tool for cleaned SharePoint permissions CSV files.
Displays shape, columns, sample data, and top statistics.

Usage:
    python scripts/inspect_processed_csv.py
"""
import sys
from pathlib import Path

import pandas as pd

# Configuration
CSV_PATH = Path("data/processed/sharepoint_permissions_clean.csv")


def main() -> None:
    """Inspect processed SharePoint permissions CSV."""
    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found: {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    try:
        permissions_dataframe = pd.read_csv(CSV_PATH)
        print(f"📊 Shape: {permissions_dataframe.shape}")
        print(f"📋 Columns: {list(permissions_dataframe.columns)}\n")

        print("Sample Data (5 rows):")
        print(permissions_dataframe.head(5).to_string(index=False))
        print()

        # Display statistics if columns exist
        if "Item Type" in permissions_dataframe.columns:
            unique_types = sorted(permissions_dataframe["Item Type"].dropna().unique().tolist())[:10]
            print(f"Unique item types (first 10): {unique_types}")

        if "Permission" in permissions_dataframe.columns:
            top_perms = permissions_dataframe["Permission"].dropna().value_counts().head(5).to_dict()
            print(f"Top 5 permissions by count: {top_perms}")

    except Exception as e:
        print(f"ERROR: Failed to read CSV: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
