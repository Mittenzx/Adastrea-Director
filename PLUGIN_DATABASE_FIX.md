# Fix for Plugin Database Status Issues

## Issue Summary

The plugin had two issues related to database management:

1. **Error when clicking "Refresh Database Status"**: The plugin displayed the error "Unknown Request Type: db_info"
2. **Unable to select existing database**: Users couldn't easily select an already populated database without re-ingesting

## Root Cause Analysis

### Issue 1: Missing db_info Handler
- The plugin C++ code (`SAdastreaDirectorPanel.cpp`) calls the `db_info` request type to get database information
- The base `IPCServer` class (used by the plugin) didn't have a `db_info` handler registered
- The handler only existed in `IntegratedIPCServer` which is used when RAG is explicitly enabled via command-line flags
- Since the plugin starts `ipc_server.py` directly, it uses the base `IPCServer` class

### Issue 2: Database Path Configuration
- The database path was hardcoded to a specific user's directory: `C:\Users\David Henderson\Documents\Adastrea-Director\chroma_db_adastrea`
- The refresh button wasn't passing the database path from the UI to the backend
- Users couldn't easily point to existing databases

## Changes Made

### 1. Added db_info Handler to Base IPCServer

**File**: `Plugins/AdastreaDirector/Python/ipc_server.py`

- Added `_handle_db_info()` method that:
  - Accepts optional `persist_directory` and `collection_name` parameters
  - Auto-detects database location if not provided
  - Returns database information (collection name, document count, location)
  - Returns helpful error messages if database not found or dependencies missing

- Registered the handler in `_register_default_handlers()`:
  ```python
  self.register_handler('db_info', self._handle_db_info)
  ```

### 2. Fixed Collection Name Inconsistency

**File**: `Plugins/AdastreaDirector/Python/ipc_server.py`

- Updated `DEFAULT_COLLECTION_NAME` from `"adastrea_docs"` to `"adastrea_game_docs"`
- Updated all handlers to use consistent collection name:
  - `_handle_ingest`: Now defaults to `adastrea_game_docs`
  - `_handle_clear_history`: Now uses `adastrea_game_docs`
  - `_handle_db_info`: Now defaults to `adastrea_game_docs`

This ensures consistency with the C++ plugin code which uses `adastrea_game_docs`.

### 3. Updated UI for Database Selection

**File**: `Plugins/AdastreaDirector/Source/AdastreaDirectorEditor/Private/SAdastreaDirectorPanel.cpp`

#### Changed Default Database Path
- **Before**: `TEXT("C:\\Users\\David Henderson\\Documents\\Adastrea-Director\\chroma_db_adastrea")`
- **After**: `FPaths::ProjectDir() / TEXT("chroma_db_adastrea")`

This makes the default path relative to the user's project directory instead of a hardcoded user path.

#### Updated Refresh Handler
The `OnRefreshDbStatusClicked()` method now:
- Reads the database path from the UI text box
- Converts it to a full path
- Builds a JSON request with `persist_directory` and `collection_name`
- Passes this to the backend instead of an empty `{}`

```cpp
// Build JSON request with database path if provided
TSharedPtr<FJsonObject> RequestObject = MakeShared<FJsonObject>();
RequestObject->SetStringField(TEXT("persist_directory"), DbPath);
RequestObject->SetStringField(TEXT("collection_name"), TEXT("adastrea_game_docs"));
```

#### Updated Hint Text
Changed the database path hint from:
- **Before**: "Path to ChromaDB database..."
- **After**: "Path to ChromaDB database (can select existing database)..."

This makes it clear that users can select existing databases.

## Testing

Created and ran comprehensive tests to verify:

1. ✅ `db_info` handler is properly registered
2. ✅ Handler is callable and returns proper responses
3. ✅ Handler accepts `persist_directory` parameter
4. ✅ Collection name is consistent across all handlers
5. ✅ Full request processing flow works correctly
6. ✅ No security vulnerabilities introduced (CodeQL scan passed)
7. ✅ Python syntax is valid

## User Impact

### Before Fix
- Clicking "Refresh Database Status" resulted in error: "Unknown Request Type: db_info"
- Users had to modify hardcoded paths or couldn't easily use existing databases
- Collection name mismatch could cause database not found errors

### After Fix
- ✅ "Refresh Database Status" button now works correctly
- ✅ Users can select any existing ChromaDB database directory
- ✅ Default database path uses project directory (portable)
- ✅ Collection names are consistent between C++ and Python
- ✅ Clear error messages when database not found or dependencies missing

## Usage

### To Use an Existing Database

1. Click "Browse..." next to Database Path
2. Select your existing ChromaDB directory (e.g., `chroma_db_adastrea`)
3. Click "Refresh" to see database status
4. The status will show:
   - Collection name
   - Number of documents
   - Database location

### To Create a New Database

1. Enter or browse to a new directory path for Database Path
2. Enter or browse to your documentation folder
3. Click "Start Ingestion"
4. After ingestion completes, click "Refresh" to see database status

## Technical Details

### Handler Implementation

The `_handle_db_info` method follows this flow:

1. Parse JSON data for optional `persist_directory` and `collection_name`
2. If no persist directory provided, attempt auto-detection
3. Return error if no database found
4. Create `RAGQueryAgent` with specified parameters
5. Call `get_database_info()` to retrieve database statistics
6. Return success with database info or error with details

### Error Handling

The handler gracefully handles:
- Missing database (returns clear error message)
- Missing dependencies (returns installation instructions)
- Invalid parameters (handles gracefully)
- JSON parsing errors (accepts empty or malformed data)

## Files Changed

1. `Plugins/AdastreaDirector/Python/ipc_server.py`
   - Added `_handle_db_info()` method
   - Registered handler in `_register_default_handlers()`
   - Fixed collection name inconsistency

2. `Plugins/AdastreaDirector/Source/AdastreaDirectorEditor/Private/SAdastreaDirectorPanel.cpp`
   - Updated default database path to use project directory
   - Updated `OnRefreshDbStatusClicked()` to pass database path to backend
   - Updated hint text to clarify existing database selection

## Backward Compatibility

✅ All changes are backward compatible:
- Existing databases will continue to work
- Auto-detection still works if no path is provided
- Collection name consistency fixes a potential bug
- Default paths are more portable across different user environments
