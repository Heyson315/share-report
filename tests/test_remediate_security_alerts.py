#!/usr/bin/env python3
"""
Unit Tests for Security Alert Remediation System

Tests the automated remediation engine including:
- Alert remediation logic
- Safety checking
- Logging mechanisms
- Whatif/dry-run mode
- Escalation workflows

Reference: test_remediate_security_alerts.py - Remediation engine test suite
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.remediate_security_alerts import SecurityAlertRemediator


class TestSecurityAlertRemediator(unittest.TestCase):
    """
    Test suite for Security Alert Remediation System.

    Tests:
        - Initialization and file loading
        - Auto-remediation safety checks
        - Remediation actions
        - Logging mechanisms
        - WhatIf mode
        - Escalation workflows

    Reference: #TestSecurityAlertRemediator - Main test class
    """

    def setUp(self):
        """Set up test environment with temporary files."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Create test alerts database
        self.alerts_db_path = self.temp_path / "alerts_db.json"
        self.test_alerts_db = {
            "metadata": {
                "collection_date": datetime.utcnow().isoformat(),
                "total_alerts": 3,
                "last_updated": datetime.utcnow().isoformat(),
            },
            "alerts": [
                {
                    "id": "SAF-001",
                    "source": "safety",
                    "package": "requests",
                    "installed_version": "2.25.0",
                    "fixed_version": "2.31.0",
                    "severity": "HIGH",
                    "status": "open",
                },
                {
                    "id": "M365-001",
                    "source": "m365_cis",
                    "control_id": "1.1.1",
                    "severity": "MEDIUM",
                    "status": "open",
                },
                {
                    "id": "BAN-001",
                    "source": "bandit",
                    "confidence": "HIGH",
                    "severity": "LOW",
                    "status": "open",
                },
            ],
        }

        # Write test database
        with open(self.alerts_db_path, "w", encoding="utf-8") as f:
            json.dump(self.test_alerts_db, f, indent=2)

        # Create remediation log path
        self.remediation_log_path = self.temp_path / "remediation_log.json"

    def tearDown(self):
        """Clean up temporary files."""
        import shutil

        if self.temp_path.exists():
            shutil.rmtree(self.temp_path, ignore_errors=True)

    def test_initialization(self):
        """
        Test remediator initialization.

        Reference: #test_initialization - Initialization test
        """
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        self.assertIsNotNone(remediator.alerts_db)
        self.assertEqual(remediator.alerts_db["metadata"]["total_alerts"], 3)
        self.assertEqual(len(remediator.alerts_db["alerts"]), 3)
        self.assertIsInstance(remediator.remediation_log, list)

    def test_initialization_missing_alerts_db(self):
        """
        Test initialization with missing alerts database.

        Reference: #test_initialization_missing_alerts_db - Error handling test
        """
        nonexistent_path = self.temp_path / "nonexistent.json"

        with self.assertRaises(SystemExit):
            SecurityAlertRemediator(nonexistent_path, self.remediation_log_path)

    def test_can_auto_remediate_safety(self):
        """
        Test auto-remediation check for Safety alerts.

        Safety alerts can be auto-remediated (dependency updates).

        Reference: #test_can_auto_remediate_safety - Safety check test
        """
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        safety_alert = {"id": "SAF-001", "source": "safety", "severity": "HIGH"}

        self.assertTrue(remediator.can_auto_remediate(safety_alert))

    def test_can_auto_remediate_m365_safe_control(self):
        """
        Test auto-remediation check for safe M365 CIS controls.

        Only specific safe controls can be auto-remediated.

        Reference: #test_can_auto_remediate_m365_safe_control - M365 safety check
        """
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        safe_alert = {"id": "M365-001", "source": "m365_cis", "control_id": "1.1.1"}

        self.assertTrue(remediator.can_auto_remediate(safe_alert))

    def test_can_auto_remediate_m365_unsafe_control(self):
        """
        Test auto-remediation check for unsafe M365 CIS controls.

        Unsafe controls should not be auto-remediated.

        Reference: #test_can_auto_remediate_m365_unsafe_control - Safety validation
        """
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        unsafe_alert = {"id": "M365-002", "source": "m365_cis", "control_id": "5.1.1"}

        self.assertFalse(remediator.can_auto_remediate(unsafe_alert))

    def test_can_auto_remediate_bandit_low_severity(self):
        """
        Test auto-remediation check for low severity Bandit alerts.

        Only LOW severity with HIGH confidence can be auto-remediated.

        Reference: #test_can_auto_remediate_bandit_low_severity - Bandit safety check
        """
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        safe_bandit = {
            "id": "BAN-001",
            "source": "bandit",
            "severity": "LOW",
            "confidence": "HIGH",
        }

        self.assertTrue(remediator.can_auto_remediate(safe_bandit))

    def test_can_auto_remediate_bandit_high_severity(self):
        """
        Test auto-remediation check for high severity Bandit alerts.

        HIGH severity Bandit alerts should not be auto-remediated.

        Reference: #test_can_auto_remediate_bandit_high_severity - Risk prevention
        """
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        unsafe_bandit = {
            "id": "BAN-002",
            "source": "bandit",
            "severity": "HIGH",
            "confidence": "HIGH",
        }

        self.assertFalse(remediator.can_auto_remediate(unsafe_bandit))

    def test_can_auto_remediate_codeql(self):
        """
        Test auto-remediation check for CodeQL alerts.

        CodeQL alerts should never be auto-remediated.

        Reference: #test_can_auto_remediate_codeql - Manual review required
        """
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        codeql_alert = {"id": "CQL-001", "source": "codeql", "severity": "LOW"}

        self.assertFalse(remediator.can_auto_remediate(codeql_alert))

    def test_log_action(self):
        """
        Test remediation action logging.

        Reference: #test_log_action - Logging mechanism test
        """
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        # Log an action
        remediator._log_action(
            alert_id="SAF-001",
            action="remediated",
            result="success",
            details={"package": "requests", "new_version": "2.31.0"},
        )

        # Verify log entry
        self.assertEqual(len(remediator.remediation_log), 1)
        log_entry = remediator.remediation_log[0]

        self.assertEqual(log_entry["alert_id"], "SAF-001")
        self.assertEqual(log_entry["action"], "remediated")
        self.assertEqual(log_entry["result"], "success")
        self.assertIn("timestamp", log_entry)
        self.assertIn("details", log_entry)

        # Verify log was saved to file
        self.assertTrue(self.remediation_log_path.exists())

        # Load and verify saved log
        with open(self.remediation_log_path, "r", encoding="utf-8") as f:
            saved_log = json.load(f)

        self.assertEqual(len(saved_log), 1)
        self.assertEqual(saved_log[0]["alert_id"], "SAF-001")

    def test_remediate_safety_alert_whatif(self):
        """
        Test Safety alert remediation in WhatIf mode.

        WhatIf mode should preview changes without applying them.

        Reference: #test_remediate_safety_alert_whatif - Dry-run test
        """
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        safety_alert = remediator.alerts_db["alerts"][0]

        # Test WhatIf mode
        result = remediator.remediate_safety_alert(safety_alert, whatif=True)

        self.assertIsNotNone(result)
        self.assertIn("status", result)
        # WhatIf mode returns status="preview"
        self.assertEqual(result["status"], "preview")
        self.assertIn("message", result)
        self.assertIn("Would update", result["message"])

    def test_load_existing_remediation_log(self):
        """
        Test loading existing remediation log.

        Reference: #test_load_existing_remediation_log - Log persistence test
        """
        # Create existing log
        existing_log = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "alert_id": "SAF-001",
                "action": "remediated",
                "result": "success",
                "details": {},
            }
        ]

        with open(self.remediation_log_path, "w", encoding="utf-8") as f:
            json.dump(existing_log, f, indent=2)

        # Load remediator
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        # Verify existing log was loaded
        self.assertEqual(len(remediator.remediation_log), 1)
        self.assertEqual(remediator.remediation_log[0]["alert_id"], "SAF-001")

    def test_save_alerts_db(self):
        """
        Test saving alerts database with updated timestamp.

        Reference: #test_save_alerts_db - Database persistence test
        """
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        # Modify alerts database
        original_timestamp = remediator.alerts_db["metadata"]["last_updated"]

        # Save database
        import time

        time.sleep(0.1)  # Ensure timestamp changes
        remediator._save_alerts_db()

        # Reload and verify
        with open(self.alerts_db_path, "r", encoding="utf-8") as f:
            saved_db = json.load(f)

        # Timestamp should be updated
        self.assertNotEqual(saved_db["metadata"]["last_updated"], original_timestamp)

    def test_multiple_log_entries(self):
        """
        Test multiple remediation actions logging.

        Reference: #test_multiple_log_entries - Log accumulation test
        """
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        # Log multiple actions
        remediator._log_action("SAF-001", "remediated", "success", {})
        remediator._log_action("M365-001", "escalated", "pending", {})
        remediator._log_action("BAN-001", "remediated", "failed", {})

        # Verify all entries logged
        self.assertEqual(len(remediator.remediation_log), 3)

        # Verify correct order
        self.assertEqual(remediator.remediation_log[0]["alert_id"], "SAF-001")
        self.assertEqual(remediator.remediation_log[1]["alert_id"], "M365-001")
        self.assertEqual(remediator.remediation_log[2]["alert_id"], "BAN-001")

    def test_can_auto_remediate_unknown_source(self):
        """
        Test auto-remediation check for unknown alert sources.

        Unknown sources should not be auto-remediated.

        Reference: #test_can_auto_remediate_unknown_source - Default safety behavior
        """
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        unknown_alert = {"id": "UNK-001", "source": "unknown_source", "severity": "HIGH"}

        self.assertFalse(remediator.can_auto_remediate(unknown_alert))

    def test_alert_status_tracking(self):
        """
        Test that alert status is properly tracked in database.

        Reference: #test_alert_status_tracking - Status management test
        """
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        # Verify initial statuses
        for alert in remediator.alerts_db["alerts"]:
            self.assertEqual(alert["status"], "open")

    def test_remediation_log_timestamps(self):
        """
        Test that remediation logs include proper timestamps.

        Reference: #test_remediation_log_timestamps - Timestamp validation
        """
        remediator = SecurityAlertRemediator(self.alerts_db_path, self.remediation_log_path)

        # Log an action
        before_time = datetime.utcnow()
        remediator._log_action("SAF-001", "remediated", "success", {})
        after_time = datetime.utcnow()

        # Verify timestamp is within expected range
        log_time = datetime.fromisoformat(remediator.remediation_log[0]["timestamp"])
        self.assertGreaterEqual(log_time, before_time)
        self.assertLessEqual(log_time, after_time)


if __name__ == "__main__":
    unittest.main()
