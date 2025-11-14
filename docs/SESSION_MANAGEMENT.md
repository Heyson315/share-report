# Session Management Guide

## Overview

The M365 Security Toolkit now includes comprehensive session management capabilities that track user operations, maintain audit trails, and enable better compliance reporting.

## Features

- **Unique Session Tracking**: Each operation gets a unique session ID
- **Event Logging**: Track progress and events throughout operation lifecycle
- **User Attribution**: Automatically detect and record the user performing operations
- **Persistence**: Sessions are saved to JSON for historical analysis
- **Query Capabilities**: Filter sessions by operation type, user, date range
- **Statistics**: Generate usage reports and analytics
- **Integration**: Works seamlessly with cost tracking and MCP server operations

## Quick Start

### Basic Usage

```python
from src.core.session_manager import create_session, complete_session

# Create a session
session = create_session('security_audit', metadata={'tenant': 'contoso.onmicrosoft.com'})
print(f"Session ID: {session.session_id}")

# Add events as operation progresses
session.add_event('progress', 'Connecting to Exchange Online')
session.add_event('progress', 'Running CIS controls checks')
session.add_event('progress', 'Analyzing results')

# Complete the session
complete_session(session.session_id, status='success')
```

### Using Session Manager Directly

```python
from src.core.session_manager import SessionManager

# Create manager instance
manager = SessionManager()

# Create a session
session = manager.create_session(
    operation_type='sharepoint_analysis',
    metadata={'site': 'https://contoso.sharepoint.com'}
)

# Work with session
session.add_event('start', 'Beginning permission analysis')
# ... perform work ...
session.add_event('complete', 'Analysis finished')

# Complete session
manager.complete_session(session.session_id, status='success')
```

## Session Operations

### Operation Types

Common operation types used throughout the toolkit:

- `security_audit` - M365 CIS security audits
- `sharepoint_analysis` - SharePoint permissions analysis
- `remediation` - Security remediation operations
- `dashboard_generation` - Dashboard and report generation
- `gpt5_testing` - GPT-5 API testing and development
- `general` - General operations

### Session Status Values

- `active` - Session is currently in progress
- `success` - Session completed successfully
- `error` - Session encountered an error
- `cancelled` - Session was cancelled by user

### Event Types

- `start` - Operation started
- `progress` - Progress update
- `error` - Error occurred
- `complete` - Operation completed

## Querying Session History

### Get All Sessions

```python
from src.core.session_manager import get_session_manager

manager = get_session_manager()

# Get all sessions from last 30 days
history = manager.get_session_history(days=30)

for session in history:
    print(f"{session['start_time']}: {session['operation_type']} - {session['status']}")
```

### Filter by Operation Type

```python
# Get only audit sessions
audit_sessions = manager.get_session_history(
    operation_type='security_audit',
    days=30
)
```

### Filter by User

```python
# Get sessions for specific user
user_sessions = manager.get_session_history(
    user='admin@contoso.com',
    days=7
)
```

### Combined Filters

```python
# Get failed audit sessions for specific user
failed_audits = manager.get_session_history(
    operation_type='security_audit',
    user='admin@contoso.com',
    days=30
)
failed_audits = [s for s in failed_audits if s['status'] == 'error']
```

## Statistics and Reporting

### Get Session Statistics

```python
from src.core.session_manager import get_session_manager

manager = get_session_manager()

# Get statistics for last 30 days
stats = manager.get_statistics(days=30)

print(f"Total Sessions: {stats['total_sessions']}")
print(f"Active Sessions: {stats['active_sessions']}")
print(f"Average Duration: {stats['avg_duration_seconds']} seconds")
print(f"By Operation Type: {stats['by_operation_type']}")
print(f"By User: {stats['by_user']}")
print(f"By Status: {stats['by_status']}")
```

### Print Formatted Statistics

```python
# Print formatted statistics report
manager.print_statistics(days=30)
```

Output example:
```
================================================================================
  Session Statistics - Last 30 Days
================================================================================

📊 Overview:
   Total Sessions: 45
   Active Sessions: 2
   Average Duration: 127.3 seconds

🔧 By Operation Type:
   security_audit: 25
   sharepoint_analysis: 12
   dashboard_generation: 8

👤 By User:
   admin@contoso.com: 30
   auditor@contoso.com: 15

✅ By Status:
   success: 42
   error: 3
================================================================================
```

## Integration with Cost Tracking

Session IDs are automatically integrated with the GPT-5 cost tracker:

```python
from src.core.cost_tracker import GPT5CostTracker
from src.core.session_manager import create_session

# Create a session
session = create_session('gpt5_analysis', metadata={'task': 'financial_report'})

# Create cost tracker with session ID
tracker = GPT5CostTracker(
    budget_limit=10.00,
    session_id=session.session_id
)

# All tracked requests will include the session ID
result = tracker.track_request(
    model='gpt-5',
    prompt_tokens=1500,
    completion_tokens=2000,
    request_type='analysis'
)

# Session ID is in the log entry
print(f"Session ID: {result['request']['session_id']}")
```

This allows you to:
- Track GPT-5 costs per session
- Associate costs with specific operations
- Generate cost reports by operation type
- Monitor budget usage per user

## Integration with MCP Server

The MCP server automatically creates and manages sessions for all operations:

```python
# When using MCP server tools, sessions are automatically created
# For example, when running a security audit:

# MCP server creates session
session = self.session_manager.create_session(
    operation_type='security_audit',
    metadata={
        'timestamped': True,
        'spo_admin_url': spo_admin_url,
        'skip_purview': False
    }
)

# Events are logged throughout the operation
session.add_event('start', 'Starting M365 CIS security audit')
session.add_event('progress', 'Building PowerShell command')
session.add_event('progress', 'Executing PowerShell audit script')
session.add_event('progress', 'Audit script completed, parsing results')

# Session is completed with final status
session.add_event('complete', f'Audit completed with 92.5% compliance')
self.session_manager.complete_session(session.session_id, status='success')
```

The session ID is included in the operation summary returned to the user.

## Storage and Persistence

### Storage Location

Sessions are stored in:
```
output/sessions/session_log.json
```

### Storage Format

```json
[
  {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "user": "admin@contoso.com",
    "operation_type": "security_audit",
    "metadata": {
      "tenant": "contoso.onmicrosoft.com",
      "compliance": "CIS"
    },
    "start_time": "2025-11-14T10:30:00",
    "end_time": "2025-11-14T10:32:15",
    "status": "success",
    "duration_seconds": 135.2,
    "events": [
      {
        "timestamp": "2025-11-14T10:30:00",
        "type": "start",
        "description": "Session started for security_audit",
        "data": {}
      },
      {
        "timestamp": "2025-11-14T10:32:15",
        "type": "complete",
        "description": "Session completed with status: success",
        "data": {}
      }
    ]
  }
]
```

### Custom Storage Location

```python
from src.core.session_manager import SessionManager

# Use custom storage location
manager = SessionManager(storage_path='/path/to/custom/sessions.json')
```

## Best Practices

### 1. Always Create Sessions for Operations

```python
# ✅ Good
session = create_session('security_audit')
try:
    # ... perform audit ...
    complete_session(session.session_id, status='success')
except Exception as e:
    session.add_event('error', str(e))
    complete_session(session.session_id, status='error')

# ❌ Bad - no session tracking
# ... perform audit without session ...
```

### 2. Add Meaningful Events

```python
# ✅ Good - detailed progress tracking
session.add_event('progress', 'Connecting to Exchange Online')
session.add_event('progress', 'Running CIS control 1.1.1')
session.add_event('progress', 'Running CIS control 1.1.2')
session.add_event('complete', 'Audit completed: 95% compliance')

# ❌ Bad - no progress information
session.add_event('start', 'Starting')
session.add_event('complete', 'Done')
```

### 3. Include Relevant Metadata

```python
# ✅ Good
session = create_session(
    'security_audit',
    metadata={
        'tenant': 'contoso.onmicrosoft.com',
        'compliance_framework': 'CIS',
        'initiated_by': 'scheduled_task'
    }
)

# ❌ Bad
session = create_session('security_audit')
```

### 4. Always Complete Sessions

```python
# ✅ Good - ensures session is closed
try:
    session = create_session('analysis')
    # ... work ...
    complete_session(session.session_id, status='success')
except Exception:
    complete_session(session.session_id, status='error')

# ❌ Bad - session left open
session = create_session('analysis')
# ... work ...
# Session never completed
```

### 5. Use Appropriate Status Values

```python
# ✅ Good - accurate status
try:
    # ... work ...
    complete_session(session.session_id, status='success')
except Exception:
    complete_session(session.session_id, status='error')

# ❌ Bad - always marking as success
try:
    # ... work that might fail ...
except Exception:
    pass
complete_session(session.session_id, status='success')
```

## Advanced Usage

### Custom Session Manager

```python
from src.core.session_manager import SessionManager

# Create manager with custom settings
manager = SessionManager(storage_path='/custom/path/sessions.json')

# Create multiple sessions
audit_session = manager.create_session('security_audit')
analysis_session = manager.create_session('sharepoint_analysis')

# Work with sessions concurrently
audit_session.add_event('progress', 'Step 1')
analysis_session.add_event('progress', 'Step 1')

# Complete sessions independently
manager.complete_session(audit_session.session_id, status='success')
manager.complete_session(analysis_session.session_id, status='success')
```

### Programmatic Analysis

```python
from src.core.session_manager import get_session_manager
from datetime import datetime, timedelta

manager = get_session_manager()

# Get sessions from specific time range
history = manager.get_session_history(days=7)

# Calculate success rate
total = len(history)
successful = len([s for s in history if s['status'] == 'success'])
success_rate = (successful / total * 100) if total > 0 else 0

print(f"Success Rate: {success_rate:.1f}%")

# Find longest running operation
longest = max(
    [s for s in history if s['duration_seconds']],
    key=lambda s: s['duration_seconds']
)
print(f"Longest operation: {longest['operation_type']} - {longest['duration_seconds']}s")

# Operations by day of week
from collections import defaultdict
by_day = defaultdict(int)
for session in history:
    dt = datetime.fromisoformat(session['start_time'])
    day_name = dt.strftime('%A')
    by_day[day_name] += 1

print("Operations by day:")
for day, count in sorted(by_day.items(), key=lambda x: x[1], reverse=True):
    print(f"  {day}: {count}")
```

## Troubleshooting

### Sessions Not Persisting

Check that the output directory exists and is writable:

```bash
mkdir -p output/sessions
chmod 755 output/sessions
```

### Cannot Find Session

Ensure you're using the correct session ID and the session hasn't been completed (removed from active sessions):

```python
# Check active sessions
manager = get_session_manager()
print(f"Active sessions: {list(manager.active_sessions.keys())}")

# Check history
history = manager.get_session_history(days=1)
print(f"Recent sessions: {[s['session_id'] for s in history]}")
```

### Session Manager Not Available

Ensure the module is properly imported:

```python
try:
    from src.core.session_manager import get_session_manager
    manager = get_session_manager()
except ImportError as e:
    print(f"Session manager not available: {e}")
```

## API Reference

### Session Class

```python
class Session:
    def __init__(session_id, user, operation_type, metadata)
    def add_event(event_type, description, data)
    def complete(status)
    def get_duration() -> timedelta
    def to_dict() -> dict
    @classmethod from_dict(data) -> Session
```

### SessionManager Class

```python
class SessionManager:
    def __init__(storage_path)
    def create_session(operation_type, user, metadata) -> Session
    def get_session(session_id) -> Session
    def complete_session(session_id, status)
    def get_session_history(operation_type, user, days) -> List[dict]
    def get_statistics(days) -> dict
    def print_statistics(days)
```

### Helper Functions

```python
def get_session_manager(storage_path) -> SessionManager
def create_session(operation_type, metadata) -> Session
def complete_session(session_id, status)
```

## See Also

- [Cost Tracking Guide](../src/core/cost_tracker.py) - GPT-5 cost tracking
- [MCP Server Guide](CUSTOM_MCP_SERVER_GUIDE.md) - MCP server integration
- [Security Audit Workflow](SECURITY_M365_CIS.md) - Security audit operations
