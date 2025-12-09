# GitHub Copilot Access to Unreal Engine Logs

This guide explains how GitHub Copilot in VSCode can access Unreal Engine output logs for better debugging assistance and context-aware suggestions.

## Overview

By default, log files (`.log`) are excluded from version control via `.gitignore` to prevent large, frequently-changing files from being committed. However, this also prevents GitHub Copilot from seeing these logs, which can be valuable for:

- **Debugging crashes and errors**: Copilot can analyze stack traces and error messages
- **Understanding runtime behavior**: See what's happening in your UE project
- **Getting context-aware suggestions**: Copilot can suggest fixes based on actual error logs
- **Troubleshooting issues**: Share log context with Copilot for assistance

## Solution: `.copilotignore` File

The repository includes a `.copilotignore` file that explicitly tells GitHub Copilot to include log files in its context, even though they're ignored by git.

### What's Included

The `.copilotignore` configuration includes:

- ✅ All `.log` files in the repository
- ✅ Unreal Engine logs in `Saved/Logs/` directories
- ✅ Test logs for debugging test failures
- ❌ Very large or binary crash dumps (`.dmp`, `.crash`)
- ❌ Verbose build logs from `Intermediate/Build/`

## How to Use

### 1. Enable GitHub Copilot in VSCode

Ensure you have GitHub Copilot installed and activated:
- Install the [GitHub Copilot extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- Sign in with your GitHub account
- Verify Copilot is active (check status bar)

### 2. Open UE Log Files

Open any Unreal Engine log file in VSCode:

```
<YourProject>/Saved/Logs/YourProject.log
```

Common UE log locations:
- **Project logs**: `<Project>/Saved/Logs/`
- **Engine logs**: `<EngineInstall>/Engine/Programs/UnrealBuildTool/Saved/Logs/`
- **Editor logs**: `<Project>/Saved/Logs/<ProjectName>.log`

### 3. Ask Copilot for Help

With a log file open or referenced, you can:

**Option A: Use Copilot Chat**
1. Open Copilot Chat (Ctrl+Shift+I or Cmd+Shift+I)
2. Ask questions about the log:
   ```
   What's causing this crash in the log?
   Explain this error message
   How can I fix this warning?
   ```

**Option B: Use Inline Suggestions**
1. Reference the log in code comments:
   ```cpp
   // TODO: Fix crash from YourProject.log line 1234
   // Error: Assertion failed: IsValid()
   ```
2. Copilot will suggest fixes based on the log context

**Option C: Use @workspace in Chat**
1. In Copilot Chat, use `@workspace` to include workspace files:
   ```
   @workspace What errors are in the Saved/Logs/ directory?
   ```

### 4. Working with Log Files

**Best Practices:**

- **Keep logs recent**: Delete old logs or rotate them regularly
- **Open specific logs**: Open the relevant log file when asking for help
- **Reference line numbers**: When asking about specific errors, mention line numbers
- **Use log snippets**: Copy relevant error sections into chat for focused help

**Example Workflow:**

1. Run your UE project and encounter a crash
2. Open `Saved/Logs/YourProject.log` in VSCode
3. Find the crash/error section
4. Ask Copilot in chat:
   ```
   I have a crash in YourProject.log with this error:
   [Error] Assertion failed: (Index >= 0) && (Index < ArrayNum)
   
   How can I fix this?
   ```
5. Copilot analyzes the log and suggests fixes

## Configuration

### Customize `.copilotignore`

You can edit `.copilotignore` to adjust what Copilot can see:

**To include more files:**
```gitignore
# Include blueprint logs
!*.log
!**/*Blueprint*.log
```

**To exclude specific logs:**
```gitignore
# Exclude verbose logs
**/VerboseOutput/*.log
```

**To include only specific directories:**
```gitignore
# Only include project logs, not engine logs
!Saved/Logs/*.log
```

### VSCode Settings

Ensure Copilot workspace indexing is enabled in VSCode settings:

```json
{
  "github.copilot.enable": {
    "*": true,
    "plaintext": true,
    "markdown": true,
    "log": true
  }
}
```

## Common Use Cases

### 1. Debugging Crashes

**Scenario**: Your UE project crashes on startup

**Solution**:
1. Open `Saved/Logs/YourProject.log`
2. Search for "Fatal error" or "Assertion failed"
3. Ask Copilot:
   ```
   @workspace What's causing this fatal error in the log?
   ```

### 2. Understanding Warnings

**Scenario**: You see warnings in the UE output log

**Solution**:
1. Open the log file with warnings
2. Copy the warning message
3. Ask Copilot:
   ```
   What does this warning mean and should I fix it?
   [LogScript: Warning] Accessed None trying to read property...
   ```

### 3. Performance Issues

**Scenario**: Your game is running slowly

**Solution**:
1. Enable profiling logs in UE (`stat unit`, `stat fps`)
2. Open the log file
3. Ask Copilot:
   ```
   Analyze the performance data in this log. What's causing slowdowns?
   ```

### 4. Blueprint/Python Errors

**Scenario**: Your blueprint or Python script has runtime errors

**Solution**:
1. Run the script and check logs
2. Open `Saved/Logs/YourProject.log`
3. Find Python/Blueprint errors
4. Ask Copilot for fixes with context

## Limitations

### What Copilot CAN Do:
- ✅ Read and analyze log files
- ✅ Suggest fixes based on error messages
- ✅ Explain UE error codes and warnings
- ✅ Provide debugging strategies
- ✅ Reference log content in code suggestions

### What Copilot CANNOT Do:
- ❌ Directly modify log files (and you shouldn't either!)
- ❌ Run UE commands or fix issues automatically
- ❌ Access logs outside the workspace
- ❌ See logs in real-time (refresh by reopening files)
- ❌ Handle extremely large logs (>1MB may be truncated)

## Troubleshooting

### Copilot Not Seeing Logs

**Problem**: Copilot doesn't seem to have context from log files

**Solutions**:
1. **Check `.copilotignore` exists**: Ensure the file is in the repository root
2. **Reload VSCode**: Close and reopen VSCode or reload window (Ctrl+Shift+P → "Reload Window")
3. **Verify log file is open**: Copilot prioritizes open files
4. **Check file size**: Very large logs (>1MB) may be skipped
5. **Use explicit references**: Mention the log file name in your question

### Log Files Still Ignored

**Problem**: `.copilotignore` not being respected

**Solutions**:
1. **Check Copilot version**: Update to the latest GitHub Copilot extension
2. **Verify syntax**: Ensure `.copilotignore` uses correct patterns
3. **Check workspace**: Log files must be in the VSCode workspace
4. **Manual inclusion**: Open the log file directly and reference it in chat

### Performance Issues

**Problem**: VSCode is slow with many log files

**Solutions**:
1. **Exclude verbose logs**: Add patterns to `.copilotignore` to exclude large logs
2. **Clean old logs**: Delete or archive logs you don't need
3. **Use specific patterns**: Instead of `!*.log`, use specific paths like `!Saved/Logs/*.log`
4. **Limit scope**: Close log files when not needed

## Security Considerations

### Private Information

Log files may contain:
- User IDs or session tokens
- File paths revealing system information
- API keys or credentials (if accidentally logged)
- Proprietary gameplay data

**Best Practices**:
1. **Review logs before sharing**: Check for sensitive info
2. **Exclude sensitive logs**: Add patterns to `.copilotignore`:
   ```gitignore
   # Exclude logs with sensitive data
   **/Credentials/*.log
   **/Auth/*.log
   ```
3. **Use local Copilot only**: Don't share logs externally
4. **Sanitize logs**: Remove sensitive data before analysis

### Team Considerations

If working in a team:
- **Communicate**: Let team members know logs are visible to Copilot
- **Document patterns**: Clearly document what logs are included/excluded
- **Regular review**: Periodically review `.copilotignore` for security

## Advanced Usage

### Integration with UE Python API

The repository includes `ue_python_api.py` which can log to UE output logs:

```python
from ue_python_api import UEPythonBridge, LogLevel

bridge = UEPythonBridge()
bridge.log_message("Debug info for Copilot", LogLevel.DISPLAY)
```

These messages will appear in the UE log file, making them accessible to Copilot.

### Automated Log Analysis

You can create scripts that use Copilot API to analyze logs:

```python
# Example: Parse log and ask Copilot for analysis
# (Requires Copilot API access)
with open("Saved/Logs/MyProject.log") as f:
    errors = [line for line in f if "Error" in line]
    # Feed to Copilot for analysis
```

### CI/CD Integration

For automated builds:
1. Logs are still in `.gitignore` (not committed)
2. Developers can access logs locally via Copilot
3. CI/CD can analyze logs separately

## Related Documentation

- [VSCode Extension README](vscode-extension/README.md) - VSCode extension for Director
- [UE Python API Guide](Plugins/AdastreaDirector/UE_PYTHON_API.md) - Direct UE Python API access
- [Bug Detection Agent](examples/bug_detection_agent_ue_integration.py) - Automated log analysis
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)

## FAQ

**Q: Will log files be committed to the repository?**  
A: No, `.gitignore` still applies. `.copilotignore` only affects what Copilot can see, not what's committed.

**Q: Can I use this with other AI assistants?**  
A: Yes! The concept is similar. Check if your AI assistant supports ignore files (e.g., `.cursorignore` for Cursor AI).

**Q: How often does Copilot update its context?**  
A: Copilot updates when you open/edit files. For new log entries, save and reopen the log file, or reference it explicitly in chat.

**Q: Can Copilot see logs from other projects?**  
A: No, only logs within the current VSCode workspace are accessible.

**Q: Does this work with the UE Plugin?**  
A: Yes! The UE Plugin logs to `<Project>/Saved/Logs/AdastreaDirector.log`, which Copilot can now access.

**Q: What about log rotation?**  
A: Copilot sees whatever files exist when you open them. Rotated logs (e.g., `Project.log.1`) are also accessible if they match the `.copilotignore` patterns.

## Contributing

If you have suggestions for improving Copilot log access:
1. Edit `.copilotignore` with your improvements
2. Update this guide
3. Submit a PR with your changes

## Summary

This setup allows GitHub Copilot to access Unreal Engine logs while keeping them out of version control. This provides:

- 🤖 **Better AI assistance** with access to runtime context
- 🔍 **Faster debugging** with AI-powered log analysis
- 📚 **Context-aware suggestions** based on actual errors
- 🔒 **Security maintained** - logs still not committed to git

Start using it today by opening a UE log file and asking Copilot for help!

---

*Part of the Adastrea Director project - Building tomorrow's game development tools, today.*
