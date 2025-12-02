from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from scripts.clean_csv import clean_csv

SAMPLE_CSV_CONTENT = """# Comment line should be removed

Resource Path,Item Type,Permission,User Name,User Email,User Or Group Type,Link ID,Link Type,AccessViaLinkID
"parent/path,with,comma",pdf,Contribute,John Doe,john@example.com,Internal,,,
Resource Path,Item Type,Permission,User Name,User Email,User Or Group Type,Link ID,Link Type,AccessViaLinkID
another/path,docx,Contribute,Jane Doe,jane@example.com,Internal,,,
"""


def test_clean_csv_basic():
    """Test basic CSV cleaning functionality with comments, blanks, and repeated headers."""
    with TemporaryDirectory() as temp_directory:
        temp_dir_path = Path(temp_directory)
        input_csv_path = temp_dir_path / "input.csv"
        output_csv_path = temp_dir_path / "output.csv"
        input_csv_path.write_text(SAMPLE_CSV_CONTENT, encoding="utf-8")

        cleaning_statistics = clean_csv(input_csv_path, output_csv_path)

        assert cleaning_statistics["comment_lines"] == 1
        assert cleaning_statistics["blank_lines"] == 1
        assert cleaning_statistics["skipped_repeated_headers"] == 1
        assert cleaning_statistics["output_rows"] == 2

        cleaned_dataframe = pd.read_csv(output_csv_path)
        expected_column_names = [
            "Resource Path",
            "Item Type",
            "Permission",
            "User Name",
            "User Email",
            "User Or Group Type",
            "Link ID",
            "Link Type",
            "AccessViaLinkID",
        ]
        assert list(cleaned_dataframe.columns) == expected_column_names
        assert cleaned_dataframe.shape == (2, 9)
        # Quoted comma should be preserved as a single field
        assert cleaned_dataframe.iloc[0]["Resource Path"] == "parent/path,with,comma"
