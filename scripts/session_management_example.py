#!/usr/bin/env python3
"""
Session Management Example
==========================

This script demonstrates how to use the session management system
in the M365 Security Toolkit.

Usage:
    python scripts/session_management_example.py
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.session_manager import create_session, complete_session, get_session_manager


def example_basic_session():
    """Basic session creation and completion"""
    print("\n" + "=" * 80)
    print("Example 1: Basic Session Management")
    print("=" * 80)

    # Create a session
    session = create_session("example_operation", metadata={"example": "basic", "version": "1.0"})

    print(f"\n✅ Session Created:")
    print(f"   Session ID: {session.session_id}")
    print(f"   User: {session.user}")
    print(f"   Operation: {session.operation_type}")
    print(f"   Started: {session.start_time}")

    # Simulate work with events
    print("\n📝 Adding Events...")
    session.add_event("start", "Beginning operation")
    time.sleep(0.5)

    session.add_event("progress", "Processing step 1", {"step": 1, "total": 3})
    time.sleep(0.5)

    session.add_event("progress", "Processing step 2", {"step": 2, "total": 3})
    time.sleep(0.5)

    session.add_event("progress", "Processing step 3", {"step": 3, "total": 3})

    # Complete the session
    complete_session(session.session_id, status="success")
    print(f"\n✅ Session Completed")
    print(f"   Duration: {session.get_duration().total_seconds():.2f} seconds")
    print(f"   Status: {session.status}")
    print(f"   Events: {len(session.events)}")


def example_error_handling():
    """Session with error handling"""
    print("\n" + "=" * 80)
    print("Example 2: Error Handling in Sessions")
    print("=" * 80)

    session = create_session("example_with_error", metadata={"will_fail": True})

    print(f"\n✅ Session Created: {session.session_id}")

    try:
        # Simulate work
        session.add_event("start", "Starting operation")
        session.add_event("progress", "Working on task")

        # Simulate an error
        raise ValueError("Simulated error for demonstration")

    except Exception as e:
        # Log error event
        session.add_event("error", f"Operation failed: {str(e)}")
        complete_session(session.session_id, status="error")

        print(f"\n❌ Session Failed")
        print(f"   Error: {str(e)}")
        print(f"   Status: {session.status}")
        print(f"   Events: {len(session.events)}")


def example_multiple_sessions():
    """Managing multiple concurrent sessions"""
    print("\n" + "=" * 80)
    print("Example 3: Multiple Concurrent Sessions")
    print("=" * 80)

    manager = get_session_manager()

    # Create multiple sessions
    sessions = []
    for i in range(3):
        session = manager.create_session(
            operation_type=f"concurrent_operation_{i+1}", metadata={"index": i + 1, "batch": "example"}
        )
        sessions.append(session)
        print(f"\n✅ Created Session {i+1}: {session.session_id}")

    # Work on all sessions
    for i, session in enumerate(sessions):
        session.add_event("progress", f"Processing task {i+1}")
        time.sleep(0.3)

    # Complete all sessions
    for i, session in enumerate(sessions):
        manager.complete_session(session.session_id, status="success")
        print(f"✅ Completed Session {i+1}")

    print(f"\n📊 Active Sessions: {len(manager.active_sessions)}")


def example_query_history():
    """Querying session history"""
    print("\n" + "=" * 80)
    print("Example 4: Querying Session History")
    print("=" * 80)

    manager = get_session_manager()

    # Get all recent sessions
    history = manager.get_session_history(days=1)
    print(f"\n📋 Recent Sessions (Last 24 hours): {len(history)}")

    # Show last 5 sessions
    for session in history[-5:]:
        status_emoji = "✅" if session["status"] == "success" else "❌"
        duration = session.get("duration_seconds", 0)
        print(f"   {status_emoji} {session['operation_type']}: {duration:.2f}s - {session['status']}")

    # Query by operation type
    example_sessions = manager.get_session_history(operation_type="example_operation", days=1)
    print(f"\n🔍 Example Operations: {len(example_sessions)}")

    # Query by status
    failed_sessions = [s for s in history if s["status"] == "error"]
    print(f"❌ Failed Sessions: {len(failed_sessions)}")


def example_statistics():
    """Session statistics and reporting"""
    print("\n" + "=" * 80)
    print("Example 5: Session Statistics")
    print("=" * 80)

    manager = get_session_manager()

    # Get statistics
    stats = manager.get_statistics(days=1)

    print(f"\n📊 Statistics (Last 24 hours):")
    print(f"   Total Sessions: {stats['total_sessions']}")
    print(f"   Active Sessions: {stats['active_sessions']}")
    print(f"   Average Duration: {stats['avg_duration_seconds']:.2f} seconds")

    print(f"\n🔧 By Operation Type:")
    for op_type, count in sorted(stats["by_operation_type"].items(), key=lambda x: x[1], reverse=True):
        print(f"   {op_type}: {count}")

    print(f"\n✅ By Status:")
    for status, count in sorted(stats["by_status"].items(), key=lambda x: x[1], reverse=True):
        status_emoji = "✅" if status == "success" else "❌" if status == "error" else "⏸️"
        print(f"   {status_emoji} {status}: {count}")

    # Print formatted statistics
    print("\n" + "=" * 80)
    print("Formatted Statistics Report:")
    print("=" * 80)
    manager.print_statistics(days=1)


def example_session_with_metadata():
    """Session with rich metadata"""
    print("\n" + "=" * 80)
    print("Example 6: Session with Rich Metadata")
    print("=" * 80)

    # Create session with detailed metadata
    session = create_session(
        "security_audit_example",
        metadata={
            "tenant": "example.onmicrosoft.com",
            "compliance_framework": "CIS",
            "version": "3.0.0",
            "controls_tested": ["1.1.1", "1.1.2", "1.1.3"],
            "initiated_by": "automated_schedule",
            "notification_email": "admin@example.com",
        },
    )

    print(f"\n✅ Session Created with Rich Metadata:")
    print(f"   Session ID: {session.session_id}")
    print(f"   Operation: {session.operation_type}")

    print(f"\n📋 Metadata:")
    for key, value in session.metadata.items():
        print(f"   {key}: {value}")

    # Add events with data
    session.add_event(
        "progress", "CIS Control 1.1.1 checked", {"control": "1.1.1", "status": "Pass", "severity": "Critical"}
    )

    session.add_event(
        "progress", "CIS Control 1.1.2 checked", {"control": "1.1.2", "status": "Fail", "severity": "High"}
    )

    session.add_event(
        "progress", "CIS Control 1.1.3 checked", {"control": "1.1.3", "status": "Pass", "severity": "Medium"}
    )

    # Complete with summary
    complete_session(session.session_id, status="success")

    print(f"\n✅ Audit Completed:")
    print(f"   Events Logged: {len(session.events)}")
    print(f"   Duration: {session.get_duration().total_seconds():.2f} seconds")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("  M365 Security Toolkit - Session Management Examples")
    print("=" * 80)
    print("\nThis script demonstrates various session management features.")

    # Run examples
    example_basic_session()
    example_error_handling()
    example_multiple_sessions()
    example_query_history()
    example_statistics()
    example_session_with_metadata()

    # Final summary
    print("\n" + "=" * 80)
    print("  Examples Complete!")
    print("=" * 80)
    print("\n💡 Tips:")
    print("   • Always create sessions for operations")
    print("   • Add meaningful events to track progress")
    print("   • Complete sessions with appropriate status")
    print("   • Use metadata for better organization")
    print("   • Query history for analysis and reporting")
    print("\n📖 Learn More:")
    print("   • Documentation: docs/SESSION_MANAGEMENT.md")
    print("   • Source Code: src/core/session_manager.py")
    print("   • Tests: tests/test_session_manager.py")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
