from pathlib import Path

import pandas as pd

csv_path = Path("data/processed/sharepoint_permissions_clean.csv")
permissions_dataframe = pd.read_csv(csv_path)
print("Shape:", permissions_dataframe.shape)
print("Columns:", list(permissions_dataframe.columns))
print("\nHead (5 rows):")
print(permissions_dataframe.head(5).to_string(index=False))
print("\nUnique item types (first 10):", sorted(permissions_dataframe["Item Type"].dropna().unique().tolist())[:10])
print("Top 5 permissions by count:", permissions_dataframe["Permission"].dropna().value_counts().head(5).to_dict())
