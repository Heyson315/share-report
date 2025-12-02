"""
Test performance benchmarking script and optimizations.

These tests validate that performance optimizations work correctly
and maintain expected behavior.
"""

import json
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_benchmark_script_imports():
    """Test that all benchmark dependencies can be imported."""
    try:
        from scripts.run_performance_benchmark import (
            benchmark_operation,
            create_test_csv,
            create_test_audit_json,
        )

        assert callable(benchmark_operation)
        assert callable(create_test_csv)
        assert callable(create_test_audit_json)
    except ImportError as import_error:
        pytest.fail(f"Failed to import benchmark modules: {import_error}")


def test_create_test_csv():
    """Test test CSV creation for benchmarking."""
    from scripts.run_performance_benchmark import create_test_csv

    with TemporaryDirectory() as temp_directory:
        test_csv_path = Path(temp_directory) / "test.csv"
        create_test_csv(test_csv_path, rows=100)

        assert test_csv_path.exists()

        # Verify structure
        with open(test_csv_path, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            header_row = next(csv_reader)
            assert len(header_row) == 5
            assert "Resource Path" in header_row

            # Count data rows
            data_row_count = sum(1 for _ in csv_reader)
            assert data_row_count == 100


def test_create_test_audit_json():
    """Test test audit JSON creation for benchmarking."""
    from scripts.run_performance_benchmark import create_test_audit_json

    with TemporaryDirectory() as temp_directory:
        test_json_path = Path(temp_directory) / "test.json"
        create_test_audit_json(test_json_path, controls=50)

        assert test_json_path.exists()

        # Verify structure
        with open(test_json_path, "r") as json_file:
            audit_data = json.load(json_file)

        assert len(audit_data) == 50
        assert "ControlId" in audit_data[0]
        assert "Title" in audit_data[0]
        assert "Severity" in audit_data[0]
        assert "Status" in audit_data[0]


def test_benchmark_operation():
    """Test benchmark_operation function."""
    from scripts.run_performance_benchmark import benchmark_operation

    def simple_test_function():
        """Simple test function that calculates a sum."""
        return sum(range(1000))

    benchmark_result = benchmark_operation("Test Operation", simple_test_function)

    assert benchmark_result["name"] == "Test Operation"
    assert benchmark_result["success"] is True
    assert benchmark_result["time_seconds"] >= 0
    assert benchmark_result["memory_mb"] >= 0
    assert benchmark_result["error"] is None


def test_benchmark_operation_with_error():
    """Test benchmark_operation with failing function."""
    from scripts.run_performance_benchmark import benchmark_operation

    def failing_test_function():
        """Function that raises an error."""
        raise ValueError("Test error")

    benchmark_result = benchmark_operation("Failing Operation", failing_test_function)

    assert benchmark_result["name"] == "Failing Operation"
    assert benchmark_result["success"] is False
    assert benchmark_result["error"] is not None
    assert "Test error" in benchmark_result["error"]


def test_clean_csv_optimization():
    """Test that optimized clean_csv maintains functionality."""
    from scripts.clean_csv import clean_csv

    with TemporaryDirectory() as temp_directory:
        # Create test CSV with comments and blank lines
        input_csv_path = Path(temp_directory) / "input.csv"
        output_csv_path = Path(temp_directory) / "output.csv"

        with open(input_csv_path, "w", encoding="utf-8") as csv_file:
            csv_file.write("# Comment line\n")
            csv_file.write("Header1,Header2,Header3\n")
            csv_file.write("\n")  # Blank line
            csv_file.write("Value1,Value2,Value3\n")
            csv_file.write("# Another comment\n")
            csv_file.write("Value4,Value5,Value6\n")

        cleaning_statistics = clean_csv(input_csv_path, output_csv_path)

        # Verify statistics
        assert cleaning_statistics["input_lines"] == 6
        assert cleaning_statistics["comment_lines"] == 2
        assert cleaning_statistics["blank_lines"] == 1
        assert cleaning_statistics["output_rows"] == 2  # Data rows only
        assert cleaning_statistics["header"] == ["Header1", "Header2", "Header3"]

        # Verify output file content
        with open(output_csv_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file)
            output_rows = list(csv_reader)

        assert len(output_rows) == 3  # Header + 2 data rows
        assert output_rows[0] == ["Header1", "Header2", "Header3"]
        assert output_rows[1] == ["Value1", "Value2", "Value3"]
        assert output_rows[2] == ["Value4", "Value5", "Value6"]


def test_sharepoint_connector_optimization():
    """Test that optimized sharepoint_connector maintains functionality."""
    import pandas as pd
    from src.integrations.sharepoint_connector import build_summaries

    # Create test DataFrame with SharePoint permissions data
    test_permissions_data = {
        "Resource Path": ["/path1", "/path2", "/path3"],
        "Item Type": ["File", "Folder", "File"],
        "Permission": ["Read", "Write", "Read"],
        "User Name": ["User1", "User2", "User1"],
        "User Email": ["user1@test.com", "user2@test.com", "user1@test.com"],
    }
    permissions_dataframe = pd.DataFrame(test_permissions_data)

    summary_results = build_summaries(permissions_dataframe)

    # Verify all expected summaries are present
    assert "by_item_type" in summary_results
    assert "by_permission" in summary_results
    assert "top_users" in summary_results
    assert "top_resources" in summary_results

    # Check by_item_type summary
    assert len(summary_results["by_item_type"]) == 2  # File and Folder

    # Check by_permission summary
    assert len(summary_results["by_permission"]) == 2  # Read and Write

    # Check top_users summary
    assert len(summary_results["top_users"]) == 2  # Two users


def test_dashboard_statistics_calculation():
    """Test that dashboard statistics calculation is correct."""
    from scripts.generate_security_dashboard import calculate_statistics

    audit_control_results = [
        {"Status": "Pass", "Severity": "High"},
        {"Status": "Fail", "Severity": "High"},
        {"Status": "Fail", "Severity": "Medium"},
        {"Status": "Manual", "Severity": "Low"},
        {"Status": "Pass", "Severity": "Low"},
    ]

    calculated_statistics = calculate_statistics(audit_control_results)

    assert calculated_statistics["total"] == 5
    assert calculated_statistics["pass"] == 2
    assert calculated_statistics["fail"] == 2
    assert calculated_statistics["manual"] == 1
    assert calculated_statistics["pass_rate"] == 40.0
    assert calculated_statistics["fail_rate"] == 40.0
    assert calculated_statistics["by_severity"]["High"] == 2
    assert calculated_statistics["by_severity"]["Medium"] == 1
    assert calculated_statistics["by_severity"]["Low"] == 2
    assert calculated_statistics["failed_by_severity"]["High"] == 1
    assert calculated_statistics["failed_by_severity"]["Medium"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
