#!/usr/bin/env python3
"""
generate_security_dashboard.py

Generate an interactive HTML dashboard from M365 CIS audit JSON results.
Features:
- Summary cards (Pass/Fail/Manual counts, severity breakdown)
- Trend charts if historical data exists
- Control status table with filtering/sorting
- Failed controls highlighted with remediation links
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def load_audit_results(json_file_path: Path) -> List[Dict[str, Any]]:
    """
    Load audit results from JSON file.

    Args:
        json_file_path: Path to the JSON file containing audit results.

    Returns:
        List of dictionaries representing CIS control results.
    """
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)


def calculate_statistics(audit_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate summary statistics from audit results.

    Args:
        audit_results: List of CIS control audit results.

    Returns:
        Dictionary containing statistics including pass/fail counts,
        severity breakdowns, and pass/fail rates.
    """
    audit_statistics = {
        "total": len(audit_results),
        "pass": 0,
        "fail": 0,
        "manual": 0,
        "error": 0,
        "by_severity": {"High": 0, "Medium": 0, "Low": 0},
        "failed_by_severity": {"High": 0, "Medium": 0, "Low": 0},
    }

    for control_result in audit_results:
        control_status = control_result.get("Status", "Unknown")
        control_severity = control_result.get("Severity", "Unknown")

        if control_status == "Pass":
            audit_statistics["pass"] += 1
        elif control_status == "Fail":
            audit_statistics["fail"] += 1
            if control_severity in audit_statistics["failed_by_severity"]:
                audit_statistics["failed_by_severity"][control_severity] += 1
        elif control_status == "Manual":
            audit_statistics["manual"] += 1
        elif control_status == "Error":
            audit_statistics["error"] += 1

        if control_severity in audit_statistics["by_severity"]:
            audit_statistics["by_severity"][control_severity] += 1

    total_controls = audit_statistics["total"]
    audit_statistics["pass_rate"] = (
        round((audit_statistics["pass"] / total_controls) * 100, 2) if total_controls > 0 else 0
    )
    audit_statistics["fail_rate"] = (
        round((audit_statistics["fail"] / total_controls) * 100, 2) if total_controls > 0 else 0
    )

    return audit_statistics


def load_historical_data(reports_directory: Path) -> List[Dict[str, Any]]:
    """
    Load historical audit data for trend analysis.

    Args:
        reports_directory: Directory containing historical audit JSON files.

    Returns:
        List of dictionaries with timestamp and statistics for each historical audit.
        Returns up to 10 most recent data points.
    """
    historical_data_points = []

    # Look for timestamped JSON files
    audit_json_files = sorted(reports_directory.glob("m365_cis_audit_*.json"))

    for audit_file_path in audit_json_files:
        try:
            # Extract timestamp from filename first (faster than loading file)
            filename_without_extension = audit_file_path.stem
            if "_" not in filename_without_extension:
                continue

            filename_parts = filename_without_extension.split("_")
            if len(filename_parts) < 5:
                continue

            date_string = filename_parts[3]
            time_string = filename_parts[4] if len(filename_parts) > 4 else "000000"

            try:
                audit_timestamp = datetime.strptime(f"{date_string}_{time_string}", "%Y%m%d_%H%M%S")
            except ValueError as timestamp_error:
                print(
                    f"Warning: Could not parse timestamp from {audit_file_path.name}: {timestamp_error}",
                    file=sys.stderr,
                )
                continue

            # Only load file if timestamp is valid
            audit_results = load_audit_results(audit_file_path)
            audit_statistics = calculate_statistics(audit_results)

            historical_data_points.append(
                {
                    "timestamp": audit_timestamp.strftime("%Y-%m-%d %H:%M"),
                    "pass_rate": audit_statistics["pass_rate"],
                    "pass": audit_statistics["pass"],
                    "fail": audit_statistics["fail"],
                    "manual": audit_statistics["manual"],
                }
            )

        except json.JSONDecodeError as json_error:
            print(f"Warning: Invalid JSON in {audit_file_path.name}: {json_error}", file=sys.stderr)
            continue
        except FileNotFoundError:
            print(
                f"Warning: File disappeared during processing: {audit_file_path.name}",
                file=sys.stderr,
            )
            continue
        except (KeyError, TypeError) as data_error:
            print(
                f"Warning: Unexpected data structure in {audit_file_path.name}: {data_error}",
                file=sys.stderr,
            )
            continue
        except Exception as unexpected_error:
            print(
                f"Warning: Unexpected error processing {audit_file_path.name}: "
                f"{type(unexpected_error).__name__}: {unexpected_error}",
                file=sys.stderr,
            )
            continue

    return historical_data_points[-10:]  # Return last 10 data points


def generate_html_dashboard(
    audit_results: List[Dict[str, Any]],
    audit_statistics: Dict[str, Any],
    historical_data: List[Dict[str, Any]],
    output_html_path: Path,
) -> None:
    """
    Generate interactive HTML dashboard from audit data.

    Args:
        audit_results: List of CIS control audit results.
        audit_statistics: Calculated statistics dictionary.
        historical_data: List of historical data points for trend chart.
        output_html_path: Path where the HTML dashboard will be saved.
    """
    # Prepare data for trend chart
    trend_chart_labels = [data_point["timestamp"] for data_point in historical_data]
    trend_chart_pass_rates = [data_point["pass_rate"] for data_point in historical_data]

    # Sort results by severity and status
    severity_sort_order = {"High": 0, "Medium": 1, "Low": 2}
    status_sort_order = {"Fail": 0, "Error": 1, "Manual": 2, "Pass": 3}

    def get_control_sort_key(control_result: Dict[str, Any]) -> tuple:
        """Get sort key tuple for a control result."""
        severity_rank = severity_sort_order.get(control_result.get("Severity", "Low"), 3)
        status_rank = status_sort_order.get(control_result.get("Status", "Pass"), 3)
        return (severity_rank, status_rank)

    sorted_audit_results = sorted(audit_results, key=get_control_sort_key)

    # Generate HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>M365 CIS Security Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: #0078d4;
            margin-bottom: 10px;
        }}
        .header .meta {{
            color: #666;
            font-size: 14px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card h3 {{
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            margin-bottom: 15px;
            letter-spacing: 1px;
        }}
        .stat-value {{
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stat-value.pass {{ color: #28a745; }}
        .stat-value.fail {{ color: #dc3545; }}
        .stat-value.manual {{ color: #6c757d; }}
        .stat-card .subtitle {{
            color: #999;
            font-size: 12px;
        }}
        .chart-container {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: {'block' if len(historical_data) > 1 else 'none'};
        }}
        .chart-container h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 18px;
        }}
        .controls-table {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        .controls-table h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 18px;
        }}
        .filter-controls {{
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            padding: 8px 16px;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            border-radius: 5px;
            transition: all 0.3s;
        }}
        .filter-btn:hover {{
            background: #f8f9fa;
        }}
        .filter-btn.active {{
            background: #0078d4;
            color: white;
            border-color: #0078d4;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: #0078d4;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        .status-pass {{ background: #d4edda; color: #155724; }}
        .status-fail {{ background: #f8d7da; color: #721c24; }}
        .status-manual {{ background: #e2e3e5; color: #383d41; }}
        .status-error {{ background: #fff3cd; color: #856404; }}
        .severity-high {{ color: #dc3545; font-weight: bold; }}
        .severity-medium {{ color: #fd7e14; font-weight: bold; }}
        .severity-low {{ color: #6c757d; }}
        .control-title {{
            font-weight: 500;
            color: #333;
        }}
        .footer {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-top: 20px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ M365 CIS Security Dashboard</h1>
            <div class="meta">
                <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
                <strong>Total Controls:</strong> {audit_statistics['total']} |
                <strong>Pass Rate:</strong> {audit_statistics['pass_rate']}%
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Passed Controls</h3>
                <div class="stat-value pass">{audit_statistics['pass']}</div>
                <div class="subtitle">{audit_statistics['pass_rate']}% of total</div>
            </div>
            <div class="stat-card">
                <h3>Failed Controls</h3>
                <div class="stat-value fail">{audit_statistics['fail']}</div>
                <div class="subtitle">{audit_statistics['fail_rate']}% of total</div>
            </div>
            <div class="stat-card">
                <h3>Manual Review</h3>
                <div class="stat-value manual">{audit_statistics['manual']}</div>
                <div class="subtitle">Requires investigation</div>
            </div>
            <div class="stat-card">
                <h3>High Severity Failures</h3>
                <div class="stat-value fail">{audit_statistics['failed_by_severity']['High']}</div>
                <div class="subtitle">Critical issues</div>
            </div>
        </div>

        <div class="chart-container">
            <h2>📈 Pass Rate Trend</h2>
            <canvas id="trendChart"></canvas>
        </div>

        <div class="controls-table">
            <h2>🔍 Control Status Details</h2>
            <div class="filter-controls">
                <button class="filter-btn active" onclick="filterTable('all')">All</button>
                <button class="filter-btn" onclick="filterTable('pass')">Pass</button>
                <button class="filter-btn" onclick="filterTable('fail')">Fail</button>
                <button class="filter-btn" onclick="filterTable('manual')">Manual</button>
                <button class="filter-btn" onclick="filterTable('high')">High Severity</button>
            </div>
            <table id="controlsTable">
                <thead>
                    <tr>
                        <th>Control ID</th>
                        <th>Title</th>
                        <th>Severity</th>
                        <th>Status</th>
                        <th>Actual</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Add table rows for each control
    for control_result in sorted_audit_results:
        control_id = control_result.get("ControlId", "N/A")
        control_title = control_result.get("Title", "N/A")
        control_severity = control_result.get("Severity", "Unknown")
        control_status = control_result.get("Status", "Unknown")
        actual_value = control_result.get("Actual", "N/A")

        status_css_class = f"status-{control_status.lower()}"
        severity_css_class = f"severity-{control_severity.lower()}"

        html_content += f"""
                    <tr data-status="{control_status.lower()}" data-severity="{control_severity.lower()}">
                        <td><strong>{control_id}</strong></td>
                        <td class="control-title">{control_title}</td>
                        <td class="{severity_css_class}">{control_severity}</td>
                        <td><span class="status-badge {status_css_class}">{control_status}</span></td>
                        <td>{actual_value}</td>
                    </tr>
"""

    html_content += f"""
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><strong>Next Audit Recommended:</strong> {(datetime.now()).strftime('%Y-%m-%d')}
            (7 days from last audit)</p>
            <p>For remediation guidance, see PostRemediateM365CIS.ps1 with -WhatIf parameter</p>
        </div>
    </div>

    <script>
        // Trend Chart
        const trendChartCanvas = document.getElementById('trendChart');
        if (trendChartCanvas) {{
            new Chart(trendChartCanvas, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(trend_chart_labels)},
                    datasets: [{{
                        label: 'Pass Rate (%)',
                        data: {json.dumps(trend_chart_pass_rates)},
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.4,
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            display: false
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}

        // Filter functionality
        function filterTable(filterType) {{
            const tableRows = document.querySelectorAll('#controlsTable tbody tr');
            const filterButtons = document.querySelectorAll('.filter-btn');

            // Update button states
            filterButtons.forEach(button => button.classList.remove('active'));
            event.target.classList.add('active');

            // Filter rows based on selected filter
            tableRows.forEach(tableRow => {{
                const rowStatus = tableRow.dataset.status;
                const rowSeverity = tableRow.dataset.severity;

                if (filterType === 'all') {{
                    tableRow.style.display = '';
                }} else if (filterType === 'high') {{
                    tableRow.style.display = rowSeverity === 'high' ? '' : 'none';
                }} else {{
                    tableRow.style.display = rowStatus === filterType ? '' : 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""

    # Write HTML to file
    output_html_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as output_file:
        output_file.write(html_content)


def main():
    """Main entry point for the security dashboard generator."""
    argument_parser = argparse.ArgumentParser(description="Generate M365 CIS Security Dashboard")
    argument_parser.add_argument(
        "--input",
        type=Path,
        help="Path to audit JSON file (default: latest in output/reports/security/)",
    )
    argument_parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/reports/security/dashboard.html"),
        help="Output HTML file path (default: output/reports/security/dashboard.html)",
    )

    parsed_args = argument_parser.parse_args()

    # Find input file
    if parsed_args.input:
        input_json_path = parsed_args.input
    else:
        # Look for latest audit file
        reports_directory = Path("output/reports/security")
        audit_json_files = list(reports_directory.glob("m365_cis_audit*.json"))
        if not audit_json_files:
            print(
                "ERROR: No audit JSON files found in output/reports/security/",
                file=sys.stderr,
            )
            print(
                "Run Invoke-M365CISAudit.ps1 first to generate audit data.",
                file=sys.stderr,
            )
            sys.exit(1)
        input_json_path = max(audit_json_files, key=lambda path: path.stat().st_mtime)
        print(f"Using latest audit file: {input_json_path}")

    if not input_json_path.exists():
        print(f"ERROR: Input file not found: {input_json_path}", file=sys.stderr)
        sys.exit(1)

    # Load and process data
    print(f"Loading audit results from {input_json_path}...")
    audit_results = load_audit_results(input_json_path)
    audit_statistics = calculate_statistics(audit_results)

    print(
        f"Calculating statistics: {audit_statistics['total']} controls, " f"{audit_statistics['pass_rate']}% pass rate"
    )

    # Load historical data for trend analysis
    reports_directory = input_json_path.parent
    historical_data = load_historical_data(reports_directory)
    if historical_data:
        print(f"Found {len(historical_data)} historical data points for trend analysis")

    # Generate dashboard
    print(f"Generating HTML dashboard: {parsed_args.output}")
    generate_html_dashboard(audit_results, audit_statistics, historical_data, parsed_args.output)

    print(f"✅ Dashboard generated successfully: {parsed_args.output}")
    print(f"   Open in browser to view: file://{parsed_args.output.absolute()}")


if __name__ == "__main__":
    main()
