# Unreal Engine Log Capture - Usage Guide

## Overview

The Adastrea Director now automatically captures all Unreal Engine output when using the GUI's Unreal MCP tab. These logs are saved to the `logs/` directory with timestamps and can be processed by AI agents for problem detection and improvement suggestions.

## How It Works

### Automatic Log Capture

When you connect to Unreal Engine through the GUI:

1. A new log session is automatically started
2. All interactions with UE are captured:
   - Python code execution and output
   - Console commands and results
   - MCP tool calls and responses
   - Errors and warnings
3. Logs are saved to `logs/ue_gui_session_YYYY-MM-DD_HH-MM-SS.log`
4. When you disconnect, the session is closed with a summary

### Log File Format

Each log file contains:

```
================================================================================
Unreal Engine Output Log
Session Started: 2025-12-10 10:28:45
Captured by: Adastrea Director
================================================================================

[2025-12-10 10:28:45.692] [INFO] [MCP-Python]
Python Code Executed:
```python
import unreal
print(unreal.SystemLibrary.get_engine_version())
```

Output:
5.3.0-12345678

--------------------------------------------------------------------------------

[2025-12-10 10:28:45.692] [INFO] [Console]
Console Command: stat fps

Output:
FPS: 60.00
--------------------------------------------------------------------------------

================================================================================
Session Ended: 2025-12-10 10:28:45
Duration: 0:00:00.001691
================================================================================
```

### Log Sources

Logs capture output from multiple sources, identified by the `[source]` tag:

- **GUI**: General GUI operations
- **GUI-Python**: Python code executed through the GUI
- **GUI-Console**: Console commands from the GUI
- **MCP-Python**: Python execution via MCP
- **MCP-Tool**: MCP tool executions
- **MCP-Result**: Tool execution results
- **MCP-Error**: Error messages
- **Console**: Console command output

## Using Logs with AI Agents

### Phase 3 Agents

The captured logs are designed to be processed by Adastrea Director's Phase 3 autonomous agents:

#### 1. Performance Agent

The performance agent can analyze logs to:
- Identify FPS drops and performance issues
- Detect slow Python operations
- Find optimization opportunities
- Track performance over time

**Example Usage:**
```bash
python agents/phase3/performance_agent.py --analyze-logs logs/ue_gui_session_*.log
```

#### 2. Bug Detection Agent

The bug detection agent can examine logs for:
- Python errors and exceptions
- UE crashes and warnings
- Failed command executions
- Pattern anomalies

**Example Usage:**
```bash
python agents/phase3/bug_detection_agent.py --scan-logs logs/
```

#### 3. Code Quality Agent

The code quality agent can review logs to:
- Identify repeated commands (potential automation candidates)
- Find inefficient workflows
- Suggest best practices
- Recommend refactoring opportunities

**Example Usage:**
```bash
python agents/phase3/code_quality_agent.py --review-logs logs/ue_gui_session_*.log
```

### Manual Analysis

You can also analyze logs manually:

```bash
# Find all errors in recent logs
grep -r "ERROR" logs/

# Count Python executions per session
grep -c "Python Code Executed" logs/ue_gui_session_*.log

# Extract all console commands
grep -A 1 "Console Command:" logs/*.log

# Find performance-related output
grep -i "fps\|performance\|optimization" logs/*.log
```

### GitHub Copilot Integration

GitHub Copilot agents can access these logs for debugging assistance:

```markdown
@copilot Please analyze the latest UE log file in logs/ and help me understand why the actor spawn is failing.
```

## Log Management

### Viewing Recent Logs

```bash
# List all log files by date
ls -lt logs/ue_*.log

# View the most recent log
cat logs/ue_gui_session_*.log | tail -1

# Follow a log in real-time (if session is active)
tail -f logs/ue_gui_session_*.log
```

### Log Rotation

Logs are automatically created with timestamps, so no manual rotation is needed. However, you may want to:

```bash
# Archive logs older than 30 days
find logs/ -name "ue_*.log" -mtime +30 -exec gzip {} \;

# Delete logs older than 90 days
find logs/ -name "ue_*.log" -mtime +90 -delete
```

### Programmatic Access

You can access logs programmatically using the `UELogCapture` class:

```python
from ue_log_capture import UELogCapture

# Create a capture instance
capture = UELogCapture()

# List recent log files
recent_logs = capture.list_log_files(limit=10)
for log_path in recent_logs:
    print(f"Log: {log_path}")
    
# Start a new session
log_path = capture.start_session("my_test")

# Log custom events
capture.log("Testing custom logging", source="Test", level="INFO")
capture.log_python_execution(
    code="import unreal",
    output="Success",
    error=""
)

# End the session
capture.end_session()
```

## Best Practices

### 1. Keep Sessions Focused

For better analysis, keep GUI sessions focused on specific tasks:
- Connect → Test specific feature → Disconnect
- This creates clear, analyzable log files

### 2. Add Context

When testing, you can add context by logging custom messages:
```python
from ue_log_capture import get_global_capture

capture = get_global_capture()
capture.log("Starting blueprint compilation test", source="Test", level="INFO")
```

### 3. Regular Review

Set up a weekly review of logs:
- Identify recurring errors
- Track performance trends
- Find improvement opportunities

### 4. Integration with CI/CD

You can integrate log analysis into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Analyze UE Logs
  run: |
    python agents/phase3/bug_detection_agent.py --scan-logs logs/
    python agents/phase3/performance_agent.py --analyze-logs logs/
```

## Troubleshooting

### Logs Not Being Created

If logs are not being created:

1. Check that the `logs/` directory exists
2. Verify write permissions on the directory
3. Check for errors in the GUI console
4. Ensure you're connected to UE before operations

### Large Log Files

If log files become too large:

1. Disconnect and reconnect to start a new session
2. Clear the MCP output display regularly
3. Implement log size limits (see `UELogCapture` class)

### Missing Information

If logs are missing information:

1. Ensure all operations go through the GUI
2. Check that the session is active (indicator in GUI)
3. Verify the log capture is enabled in settings

## Future Enhancements

Planned improvements to log capture:

- [ ] GUI controls to start/stop logging manually
- [ ] Log viewer in the GUI
- [ ] Automatic log analysis on disconnect
- [ ] Integration with agent dashboard
- [ ] Real-time log streaming to agents
- [ ] Log compression for old files
- [ ] Export logs in different formats (JSON, CSV)

## API Reference

For detailed API documentation, see the module docstrings in `ue_log_capture.py`.

### Key Classes

- **`UELogCapture`**: Main log capture class
- **`UELogCapture.start_session(session_name)`**: Start a new log session
- **`UELogCapture.log(content, source, level)`**: Log arbitrary content
- **`UELogCapture.log_python_execution(code, output, error)`**: Log Python execution
- **`UELogCapture.log_console_command(command, output)`**: Log console commands
- **`UELogCapture.log_tool_execution(tool_name, parameters, result)`**: Log tool calls
- **`UELogCapture.end_session()`**: End the current session
- **`UELogCapture.list_log_files(limit)`**: List recent log files

### Global Functions

- **`get_global_capture()`**: Get the global capture instance
- **`start_capture(session_name)`**: Start a session on the global instance
- **`log_output(content, source, level)`**: Log to the global instance
- **`end_capture()`**: End the global instance session

## Contributing

If you have suggestions for improving the log capture system:

1. Open an issue describing your idea
2. Submit a PR with your enhancement
3. Update this documentation accordingly

## See Also

- [Phase 3 Agent Guide](https://github.com/Mittenzx/Adastrea-Director/wiki) - How to use autonomous agents
- [MCP Server Guide](mcp_server/MCP_SERVER_GUIDE.md) - Unreal MCP integration
- [GitHub Copilot Integration](COPILOT_UE_LOGS_GUIDE.md) - Using logs with Copilot
