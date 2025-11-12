# Unicode Encoding Fix for Windows Users

## Issue Summary

Users on Windows were encountering a `UnicodeDecodeError` when running ingestion scripts, particularly `ingest_game_repo.py`:

```
Exception in thread Thread-3 (_readerthread):
Traceback (most recent call last):
  File "C:\Users\...\Python312\Lib\threading.py", line 1052, in _bootstrap_inner
    self.run()
  File "C:\Users\...\Python312\Lib\subprocess.py", line 1597, in _readerthread
    buffer.append(fh.read())
  File "C:\Users\...\Python312\Lib\encodings\cp1252.py", line 23, in decode
    return codecs.charmap_decode(input,self.errors,decoding_table)[0]
UnicodeDecodeError: 'charmap' codec can't decode byte 0x8f in position 161: character maps to <undefined>
```

## Root Cause

On Windows, Python's `subprocess.run()` with `text=True` defaults to using the system's default encoding (typically `cp1252`). When git operations output UTF-8 encoded text (which is common for file names, commit messages, or repository content with international characters), the `cp1252` codec cannot decode certain byte sequences, causing a crash.

This is particularly problematic when:
- Cloning repositories with UTF-8 filenames
- Reading git commit hashes from repositories with UTF-8 commit messages
- Processing git output that contains emojis or international characters

## Solution

We've fixed all subprocess calls that capture git output by explicitly specifying:
1. `encoding='utf-8'` - Forces UTF-8 decoding regardless of system default
2. `errors='replace'` - Replaces invalid sequences with placeholder characters instead of crashing

### Files Fixed

1. **`ingest_game_repo.py`** (2 locations)
   - `get_current_commit_hash()` - git rev-parse command
   - `clone_repository()` - git clone command

2. **`gui_director.py`** (1 location)
   - Git clone operation in the GUI

3. **`tests/test_game_repo_ingestion.py`** (2 locations)
   - Integration test git clone operations

4. **`tests/test_chromadb_telemetry_fix.py`** (1 location)
   - Test subprocess call

### Example of Fix

**Before:**
```python
result = subprocess.run(
    ["git", "clone", "--depth", "1", repo_url, str(clone_dir)],
    capture_output=True,
    text=True,
    timeout=300,
)
```

**After:**
```python
result = subprocess.run(
    ["git", "clone", "--depth", "1", repo_url, str(clone_dir)],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace',  # Replace invalid UTF-8 sequences instead of failing
    timeout=300,
)
```

## Verification

You can verify the fix works by running:

```bash
# Run the comprehensive test suite
python tests/test_subprocess_encoding.py

# Run the simple verification script
python verify_encoding_fix.py
```

Both scripts will confirm that:
- ✅ Subprocess calls properly handle UTF-8 encoding
- ✅ Git commands work with unicode content
- ✅ No UnicodeDecodeError occurs

## Impact

This fix ensures that:
- **Windows users** can successfully run ingestion scripts without encoding errors
- **International users** can work with repositories containing non-ASCII characters
- **All platforms** benefit from consistent UTF-8 handling

## Platform Compatibility

- ✅ **Windows**: Fixed - explicitly uses UTF-8
- ✅ **Linux**: Works as before (UTF-8 is default)
- ✅ **macOS**: Works as before (UTF-8 is default)

## Related Issues

This fix resolves the issue described in the problem statement where users encountered:
```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x8f in position 161
```

The byte `0x8f` is not a valid character in the cp1252 encoding but is valid in UTF-8, which is why explicitly specifying UTF-8 encoding resolves the issue.

## For Developers

If you're adding new subprocess calls that capture output in this project, always include:
```python
subprocess.run(
    [...],
    capture_output=True,
    text=True,
    encoding='utf-8',      # Always specify encoding
    errors='replace',      # Handle invalid sequences gracefully
)
```

This ensures consistent behavior across all platforms and prevents encoding-related crashes.
