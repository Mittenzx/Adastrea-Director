# Auto-Ingestion and GitHub Integration

This document describes the new auto-ingestion and GitHub integration features added to Adastrea Director.

## Overview

Two major features have been implemented:

1. **Codebase Auto-Ingestion** - Automatically detect and ingest your project's source code
2. **GitHub Integration** - Clone and ingest GitHub repositories with automatic updates

These features make it easy to keep your knowledge base up-to-date without manual intervention.

## Installation

Install the optional file watching dependency:

```bash
pip install watchdog
```

This enables real-time file monitoring for incremental updates. The system works without it, but you won't get automatic updates when files change.

## Features

### Codebase Auto-Ingestion

Automatically ingest your Unreal Engine project codebase:

#### Features:
- **Project Detection** - Automatically finds Source, Content, Docs, Config, Plugins directories
- **File Type Filtering** - Supports C++, C#, Python, JavaScript/TypeScript, documentation, config files
- **Smart Exclusions** - Ignores build artifacts, dependencies (node_modules, __pycache__), IDE files
- **Incremental Updates** - Only re-ingests changed files (hash-based detection)
- **File Watching** - Real-time monitoring of file changes (requires watchdog)
- **Scheduled Ingestion** - Background updates at configurable intervals
- **Progress Callbacks** - Integration with GUI for progress display

#### Quick Start:

```python
from auto_ingestion import AutoIngestion

# Create instance
auto_ingest = AutoIngestion(
    project_root="/path/to/your/project",
    collection_name="my_project",
    persist_directory="./chroma_db_project",
)

# Detect project directories
dirs = auto_ingest.detect_project()
print(f"Found {len(dirs)} project directories")

# Run full ingestion
stats = auto_ingest.run_full_ingestion()
print(f"Added: {stats['added']}, Updated: {stats['updated']}")

# Enable file watching (requires watchdog)
auto_ingest.start_file_watching()

# Enable scheduled ingestion (every 1 hour)
auto_ingest.start_scheduled_ingestion(interval_hours=1.0)
```

#### Command-Line Usage:

```bash
# Auto-ingest current project
python auto_ingestion.py /path/to/project

# With file watching
python auto_ingestion.py /path/to/project --watch

# With scheduled updates every 2 hours
python auto_ingestion.py /path/to/project --schedule 2.0

# Run immediately and watch
python auto_ingestion.py /path/to/project --run-now --watch
```

### GitHub Integration

Clone and automatically ingest GitHub repositories:

#### Features:
- **Repository Cloning** - Clone public and private repositories
- **Authentication** - Token-based authentication for private repos
- **Automatic Ingestion** - Ingest on clone with configurable options
- **Update Detection** - Check for new commits and sync
- **Branch Switching** - Switch branches and re-ingest
- **Repository Tracking** - Persistent tracking of cloned repos
- **Progress Callbacks** - Integration with GUI for progress display

#### Quick Start:

```python
from github_integration import GitHubIntegration

# Create instance
integration = GitHubIntegration(
    repos_directory="./repos",
    github_token="ghp_xxxxx",  # Optional for public repos
)

# Clone and ingest repository
repo = integration.clone_repository(
    repo_url="owner/repo",
    branch="main",  # Optional
    auto_ingest=True,
)

print(f"Cloned {repo.name}")
print(f"  Documents: {repo.document_count}")
print(f"  Chunks: {repo.chunk_count}")

# Check for updates
has_updates = integration.check_for_updates("owner/repo")
if has_updates:
    # Update and re-ingest
    integration.update_repository("owner/repo")

# Switch to different branch
integration.switch_branch("owner/repo", "develop")

# List all tracked repositories
repos = integration.list_repositories()
for r in repos:
    print(f"{r.name} - {r.current_branch}")
```

#### Command-Line Usage:

```bash
# Clone and ingest repository
export GITHUB_TOKEN="ghp_xxxxx"
python github_integration.py clone --repo owner/repo

# Clone specific branch
python github_integration.py clone --repo owner/repo --branch develop

# Update repository
python github_integration.py update --repo owner/repo

# List tracked repositories
python github_integration.py list

# Re-ingest repository
python github_integration.py ingest --repo owner/repo
```

## Example Usage

A comprehensive example script is provided:

```bash
# Auto-ingest current project
python example_auto_ingestion.py --project .

# Auto-ingest with file watching
python example_auto_ingestion.py --project . --watch

# Auto-ingest with scheduled updates every 2 hours
python example_auto_ingestion.py --project . --schedule 2.0

# Clone and ingest GitHub repository
python example_auto_ingestion.py --github owner/repo

# Clone specific branch
python example_auto_ingestion.py --github owner/repo --branch develop

# Clone private repository
export GITHUB_TOKEN=ghp_xxxxx
python example_auto_ingestion.py --github owner/private-repo
```

## Configuration

### Supported File Types

By default, the following file types are ingested:

**Code Files:**
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

**Unreal Assets:**
- `.uasset`, `.umap` (metadata only)

### Excluded Directories

The following directories are automatically excluded:

- Version control: `.git`, `.svn`, `.hg`
- Dependencies: `node_modules`, `__pycache__`, `.pytest_cache`
- Build artifacts: `Binaries`, `Intermediate`, `Build`
- Unreal temp: `Saved`
- IDE files: `.vs`, `.vscode`, `.idea`

### Customization

You can customize file types and exclusions:

```python
from auto_ingestion import ProjectDetector

detector = ProjectDetector("/path/to/project")

# Custom file extensions
custom_extensions = {".cpp", ".h", ".py", ".md"}

# Scan with custom extensions
files = detector.scan_project_files(extensions=custom_extensions)
```

## Progress Callbacks

Both modules support progress callbacks for GUI integration:

```python
def progress_callback(data):
    percent = data['percent']
    message = data['message']
    details = data['details']
    timestamp = data['timestamp']
    
    print(f"[{percent:3.0f}%] {message}")
    if details:
        print(f"  {details}")

auto_ingest = AutoIngestion(
    project_root="/path/to/project",
    progress_callback=progress_callback,
)
```

## Architecture

### Auto-Ingestion Architecture

```
ProjectDetector
  ├─ Detect project directories (Source, Content, etc.)
  ├─ Scan files with extension filtering
  └─ Exclude unwanted directories

AutoIngestion
  ├─ Project detection
  ├─ Full ingestion (incremental, hash-based)
  ├─ File watching (watchdog)
  │  ├─ FileWatchHandler (on_modified, on_created)
  │  └─ File queue for batch processing
  └─ Scheduled ingestion (background thread)
```

### GitHub Integration Architecture

```
GitHubAPI
  ├─ Repository info
  ├─ Latest commit
  └─ Branch listing

GitHubIntegration
  ├─ Repository cloning (git)
  ├─ Update detection (git fetch)
  ├─ Branch switching (git checkout)
  ├─ Auto-ingestion
  └─ Repository tracking (JSON persistence)
     └─ Repository dataclass
        ├─ name, url, clone_path
        ├─ current_branch, last_commit
        └─ document_count, chunk_count
```

## Testing

Comprehensive test suites are provided:

```bash
# Run auto-ingestion tests
pytest test_auto_ingestion.py -v

# Run GitHub integration tests
pytest test_github_integration.py -v

# Run both
pytest test_auto_ingestion.py test_github_integration.py -v
```

## Troubleshooting

### File Watching Not Working

If file watching doesn't work:

1. Install watchdog:
   ```bash
   pip install watchdog
   ```

2. Check if watchdog is available:
   ```python
   from auto_ingestion import WATCHDOG_AVAILABLE
   print(f"Watchdog available: {WATCHDOG_AVAILABLE}")
   ```

### GitHub Clone Failures

If cloning fails:

1. **Authentication Error** - Set GITHUB_TOKEN environment variable:
   ```bash
   export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
   ```

2. **Rate Limiting** - GitHub has rate limits. Wait and try again.

3. **Repository Not Found** - Check repository name and access permissions.

### Performance Issues

If ingestion is slow:

1. **Large Repositories** - Use incremental mode (default)
2. **Many Files** - Increase delay between files
3. **Rate Limiting** - Increase delay in batch processing

## Integration with GUI

These modules are designed for integration with the system.

```python
# Create auto-ingestion tab
auto_ingest = AutoIngestion(
    project_root=project_root,
    progress_callback=self.update_progress_bar,
)

# Run in background thread
threading.Thread(
    target=auto_ingest.run_full_ingestion,
    daemon=True,
).start()
```

## Future Enhancements

Planned improvements:

- [ ] GUI tabs for auto-ingestion and GitHub repos
- [ ] Visual repository browser
- [ ] Conflict resolution for updates
- [ ] Custom ingestion rules per directory
- [x] Integration with Unreal Engine project files (.uproject) - See IMPLEMENTATION_SUMMARY_AUTO_INGESTION.md
- [ ] Automatic detection of plugin dependencies
- [ ] Multi-repository synchronization

## See Also

- `PLUGIN_ROADMAP.md` - Full feature roadmap
- `example_auto_ingestion.py` - Complete examples
- `test_auto_ingestion.py` - Test suite
- `test_github_integration.py` - Test suite

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

## License

See LICENSE file for details.
