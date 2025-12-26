# Quick Reference: Auto-Ingestion & GitHub Integration

## TL;DR

Two new features added to Adastrea Director for automatic knowledge base management:

1. **Auto-Ingestion**: Automatically detect and ingest your project's source code
2. **GitHub Integration**: Clone and ingest GitHub repositories

## Quick Start

### Install Dependencies

```bash
pip install watchdog  # Optional but recommended for file watching
```

### Auto-Ingest Your Project

```bash
# Simple one-time ingestion
python auto_ingestion.py /path/to/your/project --run-now

# With file watching (real-time updates)
python auto_ingestion.py /path/to/your/project --watch

# With scheduled updates every hour
python auto_ingestion.py /path/to/your/project --schedule 1.0

# Both file watching and scheduled updates
python auto_ingestion.py /path/to/your/project --watch --schedule 2.0
```

### Clone and Ingest GitHub Repos

```bash
# Public repository
python github_integration.py clone --repo owner/repo

# Private repository (set token first)
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
python github_integration.py clone --repo owner/private-repo

# Specific branch
python github_integration.py clone --repo owner/repo --branch develop

# List tracked repositories
python github_integration.py list

# Update a repository
python github_integration.py update --repo owner/repo
```

## Python API Examples

### Auto-Ingestion

```python
from auto_ingestion import AutoIngestion

# Create instance
auto = AutoIngestion(
    project_root="/path/to/project",
    collection_name="my_project",
)

# Run full ingestion
stats = auto.run_full_ingestion()
print(f"Added: {stats['added']}, Updated: {stats['updated']}")

# Enable file watching
auto.start_file_watching()

# Enable scheduled ingestion
auto.start_scheduled_ingestion(interval_hours=1.0)
```

### GitHub Integration

```python
from github_integration import GitHubIntegration

# Create instance
gh = GitHubIntegration(github_token="ghp_xxxxx")

# Clone and ingest
repo = gh.clone_repository("owner/repo", auto_ingest=True)

# Check for updates
if gh.check_for_updates("owner/repo"):
    gh.update_repository("owner/repo")

# Switch branch
gh.switch_branch("owner/repo", "develop")
```

## Key Features

### Auto-Ingestion
- ✅ Auto-detects project directories (Source, Content, Docs, etc.)
- ✅ Supports 15+ file types (C++, C#, Python, JS/TS, docs, configs)
- ✅ Incremental updates (only changed files)
- ✅ Real-time file watching
- ✅ Scheduled background ingestion
- ✅ Smart exclusions (build artifacts, node_modules, etc.)

### GitHub Integration
- ✅ Clone public and private repositories
- ✅ Token-based authentication
- ✅ Automatic ingestion on clone
- ✅ Update detection and sync
- ✅ Branch switching
- ✅ Repository tracking

## Supported File Types

**Code:**
- C++: `.cpp`, `.h`, `.hpp`, `.cc`, `.cxx`
- C#: `.cs`
- Python: `.py`
- JavaScript/TypeScript: `.js`, `.jsx`, `.ts`, `.tsx`

**Documentation:**
- Markdown: `.md`
- Text: `.txt`, `.rst`

**Configuration:**
- JSON: `.json`
- YAML: `.yaml`, `.yml`
- Config: `.ini`, `.cfg`

## Excluded Directories

Automatically excluded:
- Version control: `.git`, `.svn`, `.hg`
- Dependencies: `node_modules`, `__pycache__`
- Build artifacts: `Binaries`, `Intermediate`, `Build`
- Unreal temp: `Saved`
- IDE files: `.vs`, `.vscode`, `.idea`

## Example Script

Use the comprehensive example:

```bash
# Auto-ingest with visualization
python example_auto_ingestion.py --project . --watch

# Clone GitHub repo with progress
python example_auto_ingestion.py --github owner/repo
```

## Progress Callbacks

Both modules support progress callbacks for GUI integration:

```python
def progress_callback(data):
    print(f"[{data['percent']}%] {data['message']}")

auto = AutoIngestion(
    project_root="/path/to/project",
    progress_callback=progress_callback,
)
```

## Troubleshooting

### File Watching Not Working?
Install watchdog: `pip install watchdog`

### GitHub Clone Failing?
Set your token: `export GITHUB_TOKEN="ghp_xxxxx"`

### Slow Ingestion?
It's working! Large projects take time. Progress is shown.

## Documentation

- **AUTO_INGESTION_README.md** - Complete feature documentation
- **IMPLEMENTATION_SUMMARY_AUTO_INGESTION.md** - Technical details
- **PLUGIN_ROADMAP.md** - Feature status and roadmap

## Tests

Run the test suites:

```bash
pytest test_auto_ingestion.py -v
pytest test_github_integration.py -v
```

## What's Next?

Optional future enhancements:
- GUI tabs for visual control
- Visual repository browser
- Custom ingestion rules
- Multi-repository sync
- Integration with .uproject files

---

**Status:** ✅ Production Ready
**Version:** 1.0.0
**Date:** December 2025
