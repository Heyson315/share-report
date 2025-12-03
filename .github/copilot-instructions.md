# Copilot Instructions: M365 Security & SharePoint Analysis Toolkit

> 🤖 **Quick Start for AI Agents**: New to this project? 
> - **Fast Track** (15 min): [AI Agent Quick Start](AI_AGENT_QUICKSTART.md)
> - **Complete Index**: [AI Development Index](AI_DEVELOPMENT_INDEX.md) - Navigate all AI resources

## Architecture Overview

This is a **hybrid Python/PowerShell enterprise security toolkit** with a **plugin-based MCP extension system** for Microsoft 365 security auditing and SharePoint permissions analysis.

### Core Architecture Principles

**Three-Layer Design:**
1. **Core Toolkit** (Required) - Foundational Python/PowerShell security auditing
2. **Extension System** (Optional) - Plugin-based MCP server for AI assistant integration  
3. **Integration Layer** - Seamless connection between core and extensions

**Why This Matters:**
- Core toolkit works standalone without extensions
- Extensions are true add-ons that enhance capabilities
- Clean separation enables independent development and testing
- Plugin architecture supports future extensibility (GPT-5, custom integrations)

### Data Flow Pipeline
```
M365 Services → PowerShell Audits → Python Processing → Reports → [Optional: MCP/AI Analysis]
     ↓               ↓                    ↓              ↓              ↓
  EXO, Graph,   CIS Controls      CSV Cleaning,   Excel/HTML     MCP Server,
  SPO, Purview   (M365CIS.psm1)  Data Transform   Dashboards    AI Insights
```

### Directory Structure
```
📦 Project Root
├── 📂 scripts/                    # Standalone Python & PowerShell utilities
│   ├── clean_csv.py               # CSV sanitization (BOM, comments, duplicates)
│   ├── m365_cis_report.py         # JSON → Excel converter
│   ├── generate_security_dashboard.py  # Interactive HTML dashboards
│   └── 📂 powershell/
│       ├── Invoke-M365CISAudit.ps1     # Main audit orchestrator
│       ├── Compare-M365CISResults.ps1   # Audit trending
│       ├── PostRemediateM365CIS.ps1     # Safe remediation
│       └── 📂 modules/
│           └── M365CIS.psm1       # Core audit functions (483+ lines)
├── 📂 src/                        # Python modules (proper package structure)
│   ├── 📂 core/                   # Core functionality
│   │   ├── excel_generator.py    # Report generation engine
│   │   └── cost_tracker.py       # GPT-5 cost monitoring
│   ├── 📂 integrations/           # External services
│   │   ├── sharepoint_connector.py  # SharePoint analysis
│   │   └── openai_gpt5.py        # GPT-5 client
│   └── 📂 extensions/             # 🆕 Plugin-based extensions
│       └── 📂 mcp/                # Model Context Protocol server
│           ├── server.py          # Main MCP server (async)
│           ├── setup.py           # Interactive setup wizard
│           ├── 📂 tools/          # Pluggable MCP tool definitions
│           │   ├── __init__.py    # Plugin registry
│           │   └── [future plugins here]
│           └── README.md          # Extension documentation
├── 📂 tests/                      # pytest-based testing
├── 📂 config/
│   ├── audit_config.json          # Tenant configuration
│   └── 📂 benchmarks/             # CIS control metadata (JSON)
├── 📂 output/reports/
│   ├── security/                  # JSON/CSV/XLSX audit results
│   └── business/                  # Excel/HTML domain reports
├── 📂 data/
│   ├── raw/                       # Unprocessed exports
│   ├── processed/                 # Cleaned CSVs
│   └── archive/                   # Historical snapshots
├── 📂 .github/workflows/          # CI/CD automation
│   ├── m365-security-ci.yml       # Quality gates & testing
│   └── m365-automated-audit.yml   # Scheduled audits
├── requirements.txt               # Core dependencies (REQUIRED)
├── requirements-extensions.txt    # 🆕 Optional extensions (MCP, GPT-5)
└── requirements-dev.txt           # Development tools
```

**Key Architectural Decisions:**
- `scripts/` contains **standalone utilities** (now has `__init__.py` for package support)
- `src/` is a **proper Python package** for reusable modules
- `src/extensions/` follows **plugin pattern** - extensions are optional and isolated
- PowerShell modules in `scripts/powershell/modules/` for M365 API interaction
- Hybrid approach: PowerShell for M365 APIs (native), Python for data processing (pandas/openpyxl)

## Recent Architectural Changes (Dec 2025)

### Plugin-Based MCP Refactoring (PR #85)
**Problem:** Monolithic MCP server made it hard to add new tools and test independently.

**Solution:** Plugin-based architecture with dynamic tool discovery:
- Each MCP tool is now a separate plugin in `src/extensions/mcp/tools/`
- Plugin registry automatically discovers and loads tools
- Enables independent testing and development of each tool
- Supports future extensions without modifying core server

**Migration Pattern:**
```python
# OLD (Monolithic)
@self.server.tool("my_tool")
async def my_tool(): ...

# NEW (Plugin-based)
# src/extensions/mcp/tools/my_plugin.py
class MyToolPlugin:
    @staticmethod
    async def execute(...): ...
```

### Enhanced CI/CD Pipeline Improvements
**New Features:**
- **Redundant security checks** across multiple workflows
- **Static analysis** with PSScriptAnalyzer and Bandit
- **Pester testing** for PowerShell modules
- **Code quality gates** prevent merging on failures
- **Automated coverage badges** updated on each commit

**Testing Conventions:**
- Pester tests use `Should -Be` syntax (not `Should Be` - proper PowerShell)
- Parameterized test cases via `-TestCases` for DRY principles
- Coverage reporting integrated into CI artifacts

## Development & Testing Workflow

### Python Development Pattern
- **Code Quality**: Black formatter (120 chars), flake8 linting, mypy type checking in `pyproject.toml`
- **Testing**: `pytest` with `TemporaryDirectory()` for file I/O, pandas validation
- **Dependencies**: 
  - `requirements.txt` - Core toolkit (REQUIRED)
  - `requirements-extensions.txt` - 🆕 Optional plugins (MCP, GPT-5)
  - `requirements-dev.txt` - Development tools
- **Performance**: Built-in benchmarking via `scripts/run_performance_benchmark.py --baseline`
- **Module Execution**:
  - ❌ `python -m scripts.file` (scripts recently became package but use direct execution)
  - ✅ `python scripts/file.py` (preferred for scripts)
  - ✅ `python -m src.integrations.sharepoint_connector` (proper for src/ modules)

### PowerShell Development Pattern
- **Module Pattern**: All functions prefixed with verb (`Test-CIS-*`, `Connect-M365CIS`, `New-CISResult`)
- **Return Standard**: `[PSCustomObject]` with fields: `ControlId`, `Title`, `Severity`, `Expected`, `Actual`, `Status`, `Evidence`, `Reference`, `Timestamp`
- **Error Handling**: Always wrap in try/catch returning `Status='Manual'` on failures
- **Path Handling**: Use absolute paths resolved from repo root via `Split-Path`
- **Testing**: Pester v5 with `Should -Be` (not `Should Be`), `-TestCases` for parameterized tests

### GitHub Actions CI/CD
**Triggers:** Push to Primary, feature/* branches, PRs, manual dispatch

**Jobs:**
1. **python-quality-checks** - Linting, formatting, type checking, unit tests
2. **powershell-security-scan** - PSScriptAnalyzer, Pester tests  
3. **security-scanning** - Bandit, CodeQL, dependency review
4. **monthly-automated-audit** - Scheduled M365 security assessments

**Quality Gates:**
- All tests must pass (pytest, Pester)
- Code coverage >70% (critical paths >90%)
- No high-severity security findings
- All linters pass (Black, flake8, PSScriptAnalyzer)

## Critical Workflows

### 1. M365 CIS Security Audit (Core Workflow)
```powershell
# Full audit with timestamping
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "scripts/powershell/Invoke-M365CISAudit.ps1" `
  -Timestamped `
  -SPOAdminUrl "https://tenant-admin.sharepoint.com"

# Convert JSON to Excel
python scripts/m365_cis_report.py

# Generate interactive dashboard
python scripts/generate_security_dashboard.py
```

**What This Does:**
- Connects to EXO, Graph, SPO, Purview, Intune
- Executes 15+ CIS controls via `M365CIS.psm1` functions
- Outputs timestamped JSON for audit trail
- Generates Excel reports with formatting
- Creates HTML dashboards with Chart.js visualizations

### 2. SharePoint Permissions Analysis
```powershell
# Step 1: Clean raw CSV (critical - SharePoint exports are messy)
python scripts/clean_csv.py `
  --input "data/raw/sharepoint/export.csv" `
  --output "data/processed/sharepoint_clean.csv"

# Step 2: Generate business report
python -m src.integrations.sharepoint_connector `
  --input "data/processed/sharepoint_clean.csv" `
  --output "output/reports/business/sharepoint_permissions.xlsx"
```

**CSV Cleaning Handles:**
- UTF-8 BOM removal (`encoding='utf-8-sig'`)
- Comment lines (`# ...`)
- Blank lines
- Duplicate headers (common in SharePoint exports)
- Quoted commas (preserves paths like `"parent/path,with,comma"`)

### 3. MCP Server Integration (Optional Extension)
```bash
# Install optional dependencies first
pip install -r requirements-extensions.txt

# Setup MCP server (interactive wizard)
python -m src.extensions.mcp.setup

# Run MCP server for AI assistant integration
python -m src.extensions.mcp.server
```

**Available MCP Tools:**
- `run_security_audit` - Execute CIS compliance audit
- `analyze_sharepoint_permissions` - Permission analysis
- `get_security_dashboard` - Generate HTML dashboard
- `remediate_security_issues` - Safe remediation with preview
- `get_compliance_status` - Current compliance metrics

**Plugin Development:**
```python
# src/extensions/mcp/tools/my_plugin.py
class MyToolPlugin:
    """New MCP tool plugin"""
    
    name = "my_tool_name"
    description = "What this tool does"
    
    @staticmethod
    async def execute(**kwargs):
        """Tool implementation"""
        return {"status": "success", "data": ...}
```

### 4. Safe Remediation Workflow
```powershell
# Preview changes (SAFE - no modifications)
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "scripts/powershell/PostRemediateM365CIS.ps1" -WhatIf

# Apply changes (CAUTION - modifies tenant)
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "scripts/powershell/PostRemediateM365CIS.ps1" -Force
```

**Best Practice:** Always run `-WhatIf` first in production!

### 5. Audit Comparison & Trending
```powershell
# Compare two audit runs
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "scripts/powershell/Compare-M365CISResults.ps1" `
  -BeforeFile "before.json" `
  -AfterFile "after.json" `
  -OutputHtml "comparison.html"
```

## Project-Specific Conventions

### File Path Handling
**PowerShell:**
```powershell
# ✅ Always use absolute paths
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$scriptPath = Join-Path $repoRoot "scripts\powershell\MyScript.ps1"
```

**Python:**
```python
# ✅ Use pathlib.Path with automatic directory creation
from pathlib import Path

output_path = Path("output/reports/security/report.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
```

### CSV Processing Pattern
**Problem:** SharePoint exports contain:
- UTF-8 BOM
- Comment lines (`# Export date: ...`)
- Blank lines
- Repeated headers (when data spans multiple pages)
- Quoted commas in paths

**Solution (`scripts/clean_csv.py`):**
```python
# 1. Read with BOM handling
content = input_path.read_text(encoding='utf-8-sig')

# 2. Filter comments and blanks
lines = [line for line in content.splitlines() 
         if line.strip() and not line.startswith('#')]

# 3. Use csv.reader to preserve quoted commas
reader = csv.reader(lines)

# 4. Track and skip duplicate headers
# 5. Return stats dict for validation
```

### PowerShell Module Pattern (`M365CIS.psm1`)
**Conventions (483+ lines of production code):**
```powershell
function Test-CIS-X.Y.Z {
    <#
    .SYNOPSIS
    Brief control description
    #>
    try {
        # Get actual configuration
        $actual = Get-SomeM365Config
        $expected = "Required Value"
        
        # Determine status
        $status = if ($actual -eq $expected) { "Pass" } else { "Fail" }
        
        # Return standardized result
        return New-CISResult `
            -ControlId "X.Y.Z" `
            -Title "Control Title" `
            -Severity "Medium" `
            -Expected $expected `
            -Actual $actual `
            -Status $status `
            -Evidence "Detailed evidence" `
            -Reference "https://docs.microsoft.com/..."
    }
    catch {
        # Always return Manual status on errors
        return New-CISResult `
            -ControlId "X.Y.Z" `
            -Title "Control Title" `
            -Severity "Medium" `
            -Expected "N/A" `
            -Actual "Error: $($_.Exception.Message)" `
            -Status "Manual" `
            -Evidence "Error occurred" `
            -Reference "https://docs.microsoft.com/..."
    }
}
```

**Critical Features:**
- Multi-service connection (EXO, Graph, SPO, Purview) with graceful fallbacks
- Auto-fix OneDrive PSModulePath for synced modules
- Explicit module imports with `-ErrorAction Stop`

### Excel Report Generation Pattern
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
import pandas as pd

# 1. Aggregate data with pandas
df = pd.DataFrame(data)
summary = df.groupby('category').size().reset_index(name='count')

# 2. Create workbook
wb = Workbook()
ws = wb.active

# 3. Write headers with formatting
ws.append(list(summary.columns))
for col in range(1, len(summary.columns) + 1):
    cell = ws.cell(1, col)
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color='4472C4', fill_type='solid')
    cell.alignment = Alignment(horizontal='center')

# 4. Write data rows
for _, row in summary.iterrows():
    ws.append(list(row))

# 5. Auto-size columns
for col in range(1, len(summary.columns) + 1):
    ws.column_dimensions[get_column_letter(col)].width = 15

# 6. Save with directory creation
output_path.parent.mkdir(parents=True, exist_ok=True)
wb.save(output_path)
```

### Error Handling Pattern
**❌ Bad (Generic Exception):**
```python
try:
    data = json.loads(file.read())
except Exception as e:  # Too broad!
    print(f"Error: {e}")
```

**✅ Good (Specific Exceptions):**
```python
try:
    data = json.loads(json_path.read_text(encoding='utf-8-sig'))
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON in {json_path}: {e}", file=sys.stderr)
    sys.exit(1)
except (PermissionError, UnicodeDecodeError) as e:
    print(f"ERROR: Cannot read {json_path}: {e}", file=sys.stderr)
    sys.exit(1)
```

**Benefits:**
- Precise error identification
- Better debugging information
- Allows selective exception handling

### Testing Pattern
**Python (pytest with tempfile):**
```python
from tempfile import TemporaryDirectory
from pathlib import Path
import pandas as pd

def test_process_csv():
    with TemporaryDirectory() as td:
        td = Path(td)
        input_file = td / "input.csv"
        output_file = td / "output.csv"
        
        # Write test input
        input_file.write_text("col1,col2\n1,2", encoding="utf-8")
        
        # Run function
        stats = process_csv(input_file, output_file)
        
        # Validate with pandas
        assert output_file.exists()
        df = pd.read_csv(output_file)
        assert df.shape == (1, 2)
        assert stats['output_rows'] == 1
```

**PowerShell (Pester v5):**
```powershell
Describe "Test-CIS-Function" {
    It "Should return Pass status when compliant" {
        # Arrange
        Mock Get-SomeConfig { return "ExpectedValue" }
        
        # Act
        $result = Test-CIS-X.Y.Z
        
        # Assert
        $result.Status | Should -Be "Pass"  # Note: -Be not Be
    }
}
```

## External Dependencies & Integration Points

### PowerShell Modules (Install with `-Scope CurrentUser`)
```powershell
Install-Module ExchangeOnlineManagement -Scope CurrentUser -Force
Install-Module Microsoft.Graph.Authentication -Scope CurrentUser -Force
Install-Module Microsoft.Graph.Identity.DirectoryManagement -Scope CurrentUser
Install-Module Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser
```

### Python Packages (Core vs Extensions)
**Core (Required):**
- `pandas` - CSV/Excel I/O, data aggregation
- `openpyxl` - Excel formatting
- `pytest` - Testing framework

**Extensions (Optional):**
- `mcp` - Model Context Protocol SDK
- `msgraph-sdk` - Microsoft Graph real-time access
- `azure-identity` - Azure AD authentication
- `openai` - GPT-5 integration

### Authentication Flow
1. **Interactive (Default):** `Connect-M365CIS` → Browser login with MFA support
2. **Service Principal (CI/CD):** Environment variables for unattended automation
3. **Required Scopes:** `User.Read.All`, `Policy.Read.All`, `Directory.Read.All`, `Organization.Read.All`
4. **Admin Roles:** Exchange Admin, Global Reader/Security Reader, SharePoint Admin

## Git Conventions & Output Organization

### Version Control Strategy (.gitignore)
- **✅ Include:** JSON/CSV reports (text-based, diffable, lightweight)
- **❌ Exclude:** Excel files (binary, causes bloat - use Git LFS if needed)
- **❌ Exclude:** Virtual envs (`.venv/`), `__pycache__/`, coverage HTML

**Rationale:** Text evidence is audit-friendly and version-controllable; binaries bloat repo history.

### Output Organization
```
output/reports/
├── security/           # CIS audit results (JSON/CSV/XLSX/HTML)
├── business/           # SharePoint/domain reports (XLSX)
data/
├── raw/                # Unprocessed exports (not in git)
├── processed/          # Cleaned CSVs (git-tracked)
└── archive/            # Historical snapshots (timestamped)
```

## Common Pitfalls & Solutions

### ❌ Module Execution Errors
```bash
# ❌ DON'T: Use -m with scripts (recently fixed but still discouraged)
python -m scripts.clean_csv

# ✅ DO: Direct execution for scripts
python scripts/clean_csv.py

# ✅ DO: Use -m for src/ modules (proper packages)
python -m src.integrations.sharepoint_connector
```

### ❌ CSV Header Assumptions
```python
# ❌ DON'T: Assume clean headers
df = pd.read_csv("raw_export.csv")  # May have BOM, comments!

# ✅ DO: Always clean first
from scripts.clean_csv import clean_csv
clean_csv(raw_path, clean_path)
df = pd.read_csv(clean_path)
```

### ❌ Hardcoded Paths
```python
# ❌ DON'T: Hardcode tenant URLs or file paths
output = "C:\\Users\\Me\\output.xlsx"

# ✅ DO: Use parameters with defaults
output_path = Path(output_param or "output/reports/business/report.xlsx")
```

### ❌ Generic Exception Handlers
```python
# ❌ DON'T: Catch all exceptions generically
except Exception as e:
    print(f"Error: {e}")

# ✅ DO: Use specific exception types
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}", file=sys.stderr)
except (PermissionError, UnicodeDecodeError) as e:
    print(f"Cannot read file: {e}", file=sys.stderr)
```

### ✅ Best Practices Summary
- Use `-Timestamped` flag for audit evidence versioning
- Validate JSON structure with `inspect_cis_report.py` before Excel conversion
- Use `-WhatIf` for safe remediation previews
- Leverage historical trending with multiple timestamped audit runs
- Configure tools via `pyproject.toml` (Black 120 chars, pytest coverage)
- Use `TemporaryDirectory()` for all file I/O tests

## Quick Reference for AI Agents

| Task | Command | Location |
|------|---------|----------|
| Run M365 Audit | `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/powershell/Invoke-M365CISAudit.ps1" -Timestamped` | `scripts/powershell/` |
| Clean CSV | `python scripts/clean_csv.py --input "raw.csv" --output "clean.csv"` | `scripts/` |
| Generate Excel Report | `python scripts/m365_cis_report.py` | `scripts/` |
| Generate HTML Dashboard | `python scripts/generate_security_dashboard.py` | `scripts/` |
| Analyze SharePoint | `python -m src.integrations.sharepoint_connector --input "clean.csv"` | `src/integrations/` |
| Run Tests | `pytest --cov=scripts --cov=src --cov-report=html` | `tests/` |
| Code Formatting | `black --line-length 120 scripts/ src/` | Root |
| Linting | `flake8 scripts/ src/ --max-line-length 120` | Root |
| MCP Server (Optional) | `python -m src.extensions.mcp.server` | `src/extensions/mcp/` |
| Performance Benchmark | `python scripts/run_performance_benchmark.py --baseline` | `scripts/` |

## AI Development Resources

**Essential Guides for AI Coding Agents:**
- 📘 **[AI Agent Quick Start](AI_AGENT_QUICKSTART.md)** - 15-minute onboarding guide with common task patterns
- 🧪 **[AI Workflow Testing](AI_WORKFLOW_TESTING.md)** - Comprehensive testing patterns and automation strategies
- 🤖 **[MCP Tool Patterns](MCP_TOOL_PATTERNS.md)** - Model Context Protocol tool development patterns
- 📖 **[AI Development Index](AI_DEVELOPMENT_INDEX.md)** - Complete navigation hub for all AI resources
- 🎨 **[Web Design Guide](../docs/WEB_DESIGN_GUIDE.md)** - Web design patterns for SharePoint and GoDaddy

**When to Use Each Guide:**
- 📘 **Starting new task?** → Read [AI Agent Quick Start](AI_AGENT_QUICKSTART.md)
- 🧪 **Writing tests?** → Reference [AI Workflow Testing](AI_WORKFLOW_TESTING.md)
- 🤖 **Building MCP tools?** → Follow [MCP Tool Patterns](MCP_TOOL_PATTERNS.md)
- 🎨 **Designing web interfaces?** → Follow [Web Design Guide](../docs/WEB_DESIGN_GUIDE.md)
- 🏗️ **Understanding architecture?** → Continue reading this document

## Extension Development Patterns

### Adding New MCP Plugin
```python
# src/extensions/mcp/tools/my_new_tool.py
class MyNewToolPlugin:
    """
    Description of what this tool does
    """
    
    # Plugin metadata
    name = "my_new_tool"
    description = "Brief description"
    
    @staticmethod
    async def execute(param1: str, param2: int = 100) -> dict:
        """
        Execute the tool
        
        Args:
            param1: Description
            param2: Description with default
            
        Returns:
            Dict with status, data, message
        """
        try:
            # Tool implementation
            result = await some_async_operation(param1, param2)
            
            return {
                "status": "success",
                "data": result,
                "message": f"Successfully processed {param1}"
            }
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "message": f"Tool failed: {type(e).__name__}",
                "error": str(e)
            }
```

### Plugin Registration (Automatic)
```python
# src/extensions/mcp/tools/__init__.py (auto-discovers plugins)
from pathlib import Path
import importlib

def discover_plugins():
    """Auto-discover and load all MCP tool plugins"""
    plugins = []
    tools_dir = Path(__file__).parent
    
    for file in tools_dir.glob("*_plugin.py"):
        module_name = file.stem
        module = importlib.import_module(f".{module_name}", package=__package__)
        
        # Find plugin classes
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and attr_name.endswith("Plugin"):
                plugins.append(attr)
    
    return plugins
```

## Debugging & Troubleshooting

### PowerShell Module Path Issues
**Symptom:** `Import-Module M365CIS.psm1` fails even though file exists

**Solution:** `Connect-M365CIS` auto-fixes OneDrive PSModulePath:
```powershell
# Automatically added by Connect-M365CIS
$oneDrivePath = Join-Path $env:USERPROFILE "OneDrive\PowerShell\Modules"
if (-not ($env:PSModulePath -split ';' -contains $oneDrivePath)) {
    $env:PSModulePath += ";$oneDrivePath"
}
```

### CSV Parsing Failures
**Symptom:** `pandas.errors.ParserError: Error tokenizing data`

**Solution:** Use `scripts/clean_csv.py` first - handles BOM, comments, duplicate headers

**Validation:**
```bash
# Inspect cleaned CSV before processing
python scripts/inspect_processed_csv.py data/processed/clean.csv
```

### Excel Generation Errors
**Symptom:** `FileNotFoundError: [Errno 2] No such file or directory`

**Solution:** Always create parent directories:
```python
output_path = Path("output/reports/business/report.xlsx")
output_path.parent.mkdir(parents=True, exist_ok=True)
wb.save(output_path)
```

### MCP Extension Not Found
**Symptom:** `ImportError: No module named 'mcp'`

**Solution:** Extensions are optional - install them separately:
```bash
pip install -r requirements-extensions.txt
```

**Check What's Installed:**
```bash
pip list | grep -E "(mcp|msgraph|azure-identity)"
```

---

**🎯 Architecture Summary:** This is a hybrid Python/PowerShell toolkit with optional plugin-based MCP extensions. Core security auditing works standalone; extensions enhance with AI assistant integration. Always read supporting guides in `.github/` for specific development tasks!