# Unreal Engine Logs Directory

This directory stores logs captured from Unreal Engine via the Adastrea Director system.

## Log Format

Logs are saved with the following naming convention:
- `ue_output_YYYY-MM-DD_HH-MM-SS.log` - Individual session logs
- Each log file contains timestamped output from UE

## Purpose

These logs are captured for:
1. **Agent Analysis**: AI agents can process these logs to identify problems, performance issues, and opportunities for improvement
2. **Debugging**: Historical record of UE output for troubleshooting
3. **Performance Monitoring**: Track UE behavior over time
4. **Automated Issue Detection**: Feed to bug detection and code quality agents

## Log Capture Sources

Logs are captured from multiple sources:
- **MCP Python Execution**: Output from Python scripts run in UE via MCP
- **Console Commands**: Results from UE console commands
- **Remote Control API**: Output from remote control operations
- **Plugin IPC**: Communication logs from the Adastrea Director plugin

## Usage

Logs are automatically created when:
1. The GUI's Unreal MCP tab is used to interact with UE
2. Remote execution commands are sent to UE
3. Agents perform automated operations in UE

## Retention

- Logs are kept indefinitely by default
- Consider implementing log rotation if disk space becomes an issue
- Old logs can be safely deleted without affecting current operations
