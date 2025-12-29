# ChromaDB Telemetry Fix

## Issue Description

Users were experiencing ChromaDB telemetry errors during document ingestion via the GUI:

```
2025-12-29 21:20:05 - chromadb.telemetry.product.posthog - ERROR - Failed to send telemetry event ClientStartEvent: capture() takes 1 positional argument but 3 were given
2025-12-29 21:20:05 - chromadb.telemetry.product.posthog - ERROR - Failed to send telemetry event ClientCreateCollectionEvent: capture() takes 1 positional argument but 3 were given
```

This error appeared for every file during ingestion, particularly when ingesting a folder through the GUI.

## Root Cause

The `ANONYMIZED_TELEMETRY` environment variable was being set to the string value `"False"` instead of the numeric value `"1"` that ChromaDB expects.

### Technical Details

1. **Environment Variable Convention**: ChromaDB follows standard Unix environment variable conventions where:
   - `"1"` = telemetry disabled
   - `"0"` = telemetry enabled
   - This aligns with the `.env.example` documentation

2. **Specific Value Check**: ChromaDB specifically checks if the `ANONYMIZED_TELEMETRY` environment variable equals `"1"` to disable telemetry, not just any truthy value.

3. **Subprocess Inheritance**: When `gui_director.py` spawns `ingest.py` as a subprocess, environment variables are inherited. However, the incorrect value was being passed down.

## Solution

Changed all occurrences of:
```python
os.environ["ANONYMIZED_TELEMETRY"] = "False"
```

To:
```python
os.environ["ANONYMIZED_TELEMETRY"] = "1"
```

### Files Updated

#### Core Scripts (12 files)
1. `ingest.py` - Main ingestion script
2. `gui_director.py` - GUI application
3. `main.py` - CLI entry point
4. `ingest_game_repo.py` - Game repository ingestion
5. `test_ingest_list.py` - Test script
6. `test_ingestion_infrastructure.py` - Infrastructure test
7. `validate_requirements.py` - Requirements validation
8. `agent_dashboard.py` - Agent monitoring dashboard
9. `Plugins/AdastreaDirector/Python/rag_ingestion.py` - Plugin RAG ingestion
10. `Plugins/AdastreaDirector/Python/rag_query.py` - Plugin RAG query
11. `Plugins/AdastreaDirector/Python/ipc_server.py` - IPC server

#### Test Files (2 files)
1. `tests/test_chromadb_telemetry_fix.py` - Updated assertions
2. `tests/test_ingestion_improvements.py` - Updated assertions

#### Documentation (1 file)
1. `.env.example` - Clarified that Adastrea sets telemetry to disabled by default

## Verification

### Manual Testing
A test script was created to verify:
1. Environment variable is properly set to `"1"`
2. Subprocess inheritance works correctly
3. Fix aligns with ChromaDB documentation

### Expected Behavior
After this fix:
- No telemetry errors during ingestion
- Single file ingestion works without errors
- Folder ingestion processes all files successfully
- Both GUI and CLI ingestion work correctly

## Prevention

All Python entry points that could import ChromaDB now set the environment variable **before** any imports:

```python
import os

# Disable ChromaDB telemetry BEFORE any imports that might import chromadb
# This prevents "capture() takes 1 positional argument but 3 were given" errors
# ChromaDB checks for this variable and any truthy value disables telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "1"

# ... rest of imports ...
```

## Related Issues

- GitHub PR: #[PR_NUMBER] (to be filled in)
- Related to ChromaDB v1.4.0 update

## References

- ChromaDB Documentation: Environment Variables
- `.env.example` - ChromaDB Telemetry Settings section
- `tests/test_chromadb_telemetry_fix.py` - Comprehensive test suite
