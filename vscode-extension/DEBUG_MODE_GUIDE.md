# Debug Mode Guide

This guide explains how to use the debug mode and diagnostics features in the Adastrea Director VS Code extension.

## Overview

The extension includes comprehensive debugging capabilities to help troubleshoot connection issues, especially when the extension cannot reach the Director IPC server. This is particularly useful when working with automated tools like GitHub Copilot that need detailed connection information.

## Quick Start

### Enable Debug Mode

**Method 1: Command Palette**
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type and select: `Director: Toggle Debug Mode`
3. View logs in the "Adastrea Director - Debug" output panel

**Method 2: Settings**
```json
{
  "director.debugMode": true
}
```

### Run Diagnostics

1. Press `Ctrl+Shift+P`
2. Type and select: `Director: Run Connection Diagnostics`
3. View the comprehensive report in the "Adastrea Director" output panel

## Features

### 1. Debug Logging

When debug mode is enabled, the extension logs detailed information about all operations:

#### Connection Events
```
[2025-12-09T11:33:01.796Z] ℹ INFO: Starting connection attempt
  Details: {
  "host": "localhost",
  "port": 5555,
  "reconnectInterval": 2000,
  "maxReconnectAttempts": 3,
  "requestTimeout": 30000
}

[2025-12-09T11:33:01.797Z] ◆ DEBUG: Attempting to connect socket
  Details: {
  "host": "localhost",
  "port": 5555
}

[2025-12-09T11:33:01.805Z] ℹ INFO: Socket connected successfully
  Details: {
  "localAddress": "127.0.0.1",
  "localPort": 50946,
  "remoteAddress": "127.0.0.1",
  "remotePort": 5555
}
```

#### Request/Response Tracking
```
[2025-12-09T11:33:01.807Z] ◆ DEBUG: Sending request
  Details: {
  "type": "ping",
  "dataLength": 0,
  "requestId": 0,
  "pendingRequestsCount": 0
}

[2025-12-09T11:33:01.807Z] ◆ DEBUG: Request sent successfully
  Details: {
  "type": "ping",
  "requestId": 0
}

[2025-12-09T11:33:01.808Z] ◆ DEBUG: Received data from server
  Details: {
  "length": 102,
  "preview": "{\"status\": \"success\", \"message\": \"pong\"..."
}
```

#### Error Logging
```
[2025-12-09T11:33:01.820Z] ✗ ERROR: Socket error occurred
  Details: {
  "errorCode": "ECONNREFUSED",
  "errorMessage": "connect ECONNREFUSED 127.0.0.1:5555",
  "errorStack": "Error: connect ECONNREFUSED..."
}
```

### 2. Log Levels

The extension uses four log levels, each with a visual indicator:

- **ℹ INFO**: General information (connection state, operations)
- **⚠ WARNING**: Warnings (timeouts, reconnection attempts)
- **✗ ERROR**: Errors (connection failures, request errors)
- **◆ DEBUG**: Detailed debugging information (socket operations, data flow)

### 3. Connection Diagnostics

The diagnostics command provides a comprehensive report:

```
============================================================
CONNECTION DIAGNOSTICS
============================================================

1. System Information:
   Platform: linux
   Node Version: v20.19.6
   VS Code Version: 1.95.3

2. Extension Configuration:
   Host: localhost
   Port: 5555
   Reconnect Interval: 5000ms
   Max Reconnect Attempts: 3
   Request Timeout: 30000ms
   Debug Mode: true
   Auto Connect: false

3. Client State:
   Current State: connected
   Is Connected: true
   Reconnect Attempts: 0
   Pending Requests: 0
   Has Socket: true

4. Socket Information:
   Local Address: 127.0.0.1
   Local Port: 50946
   Remote Address: 127.0.0.1
   Remote Port: 5555
   Ready State: open
   Bytes Read: 234
   Bytes Written: 156
   Destroyed: false

5. Network Connectivity:
   Testing connection to localhost:5555...
   ✓ Port 5555 is reachable

6. Health Check:
   ✓ Ping successful (15ms)

7. Troubleshooting Steps:
   ✓ Connection appears healthy
```

### 4. Diagnostic Information API

For programmatic access, use the `getDiagnostics()` method:

```typescript
const diagnostics = client.getDiagnostics();

// Returns typed DiagnosticsInfo:
{
  timestamp: string;
  config: {
    host: string;
    port: number;
    reconnectInterval: number;
    maxReconnectAttempts: number;
    requestTimeout: number;
    debugMode: boolean;
  };
  state: {
    currentState: ConnectionState;
    isConnected: boolean;
    reconnectAttempts: number;
    pendingRequestsCount: number;
    hasSocket: boolean;
  };
  socket?: {
    localAddress?: string;
    localPort?: number;
    remoteAddress?: string;
    remotePort?: number;
    readyState: string;
    bytesRead: number;
    bytesWritten: number;
    pending: boolean;
    destroyed: boolean;
  };
}
```

## Common Scenarios

### Scenario 1: Connection Refused

**Symptoms:**
- Extension shows "Disconnected" or "Error" status
- Error message: "Failed to connect to Director"

**Diagnosis:**
1. Enable debug mode
2. Attempt to connect
3. Check debug output for error code

**Expected Debug Output:**
```
[timestamp] ✗ ERROR: Socket error occurred
  Details: {
  "errorCode": "ECONNREFUSED",
  "errorMessage": "connect ECONNREFUSED 127.0.0.1:5555"
}
```

**Solution:**
- Start the IPC server: `python Plugins/AdastreaDirector/Python/ipc_server.py --port 5555`
- Verify port 5555 is not in use by another process

### Scenario 2: Connection Timeout

**Symptoms:**
- Extension hangs on "Connecting..."
- No response after several seconds

**Diagnosis:**
1. Run diagnostics command
2. Check network connectivity test results

**Expected Diagnostic Output:**
```
5. Network Connectivity:
   Testing connection to localhost:5555...
   ✗ Connection timeout (server may not be running)
```

**Solution:**
- Check firewall settings
- Verify server is running and listening on the correct port
- Increase reconnection timeout in settings

### Scenario 3: Request Timeout

**Symptoms:**
- Query command hangs
- Error: "Request timeout"

**Diagnosis:**
1. Enable debug mode
2. Send a request
3. Monitor request/response timing in debug output

**Expected Debug Output:**
```
[timestamp] ◆ DEBUG: Sending request
[timestamp] ⚠ WARNING: Request timeout
  Details: {
  "type": "query",
  "requestId": 5,
  "timeout": 30000
}
```

**Solution:**
- Increase request timeout: `"director.requestTimeout": 60000`
- Check server logs for processing delays
- Verify server is responding to requests

### Scenario 4: Intermittent Disconnections

**Symptoms:**
- Connection drops randomly
- Frequent reconnection attempts

**Diagnosis:**
1. Enable debug mode
2. Monitor over time
3. Look for close/error events

**Expected Debug Output:**
```
[timestamp] ℹ INFO: Socket closed
[timestamp] ⚠ WARNING: Attempting to reconnect (1/3)...
[timestamp] ℹ INFO: Starting connection attempt
```

**Solution:**
- Check network stability
- Review server logs for crashes/restarts
- Increase keepalive timeout if needed

## Output Channels

The extension creates two output channels:

### 1. Adastrea Director
- **Purpose**: Normal operation logs and diagnostics
- **Content**: Connection status, query results, diagnostic reports
- **When to use**: General monitoring and diagnostics

### 2. Adastrea Director - Debug
- **Purpose**: Verbose debug logs
- **Content**: Detailed socket operations, request tracking, error details
- **When to use**: Troubleshooting connection issues
- **Note**: Only active when debug mode is enabled

## Best Practices

### When to Enable Debug Mode

✅ **Do enable** when:
- Troubleshooting connection issues
- Setting up the extension for the first time
- Reporting bugs or issues
- Working with automated tools that need connection visibility
- Experiencing intermittent disconnections

❌ **Don't enable** when:
- Normal operation (performance overhead)
- Connection is stable
- Logs are not needed

### Performance Considerations

Debug mode has minimal performance impact:
- Logging operations are asynchronous
- Only writes to output channel when debug mode is on
- No impact on IPC communication speed
- Slight increase in memory usage for log buffering

### Privacy and Security

Debug logs may contain:
- ✅ Connection parameters (host, port)
- ✅ Request types and timing
- ✅ Socket information (addresses, ports)
- ✅ Error messages and stack traces
- ❌ No sensitive data (API keys, passwords)
- ❌ No request/response content (except preview length)

## Troubleshooting Checklist

Use this checklist when debugging connection issues:

- [ ] Enable debug mode: `Director: Toggle Debug Mode`
- [ ] Run diagnostics: `Director: Run Connection Diagnostics`
- [ ] Check "Adastrea Director - Debug" output panel
- [ ] Verify IPC server is running: `python ipc_server.py --port 5555`
- [ ] Check port availability: `lsof -i :5555` (Linux/Mac) or `netstat -ano | findstr :5555` (Windows)
- [ ] Review system information in diagnostics
- [ ] Check network connectivity test result
- [ ] Verify health check (ping) result
- [ ] Review socket information for connection details
- [ ] Check for error codes in debug output
- [ ] Follow troubleshooting recommendations in diagnostic report

## API Reference

### Commands

| Command | ID | Description |
|---------|-----|-------------|
| Toggle Debug Mode | `director.toggleDebugMode` | Enable/disable debug logging |
| Run Diagnostics | `director.runDiagnostics` | Generate diagnostic report |

### Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `director.debugMode` | boolean | `false` | Enable verbose debug logging |

### IPC Client Methods

```typescript
// Toggle debug mode
client.setDebugMode(true);

// Check debug mode status
const isDebug = client.isDebugMode();

// Get diagnostics
const diagnostics = client.getDiagnostics();

// Event handlers
client.onDebugLog = (info: DebugInfo) => {
  console.log(`[${info.timestamp}] ${info.level}: ${info.message}`);
};
```

## Support

If debug mode doesn't help resolve your issue:

1. Capture debug output
2. Run diagnostics command
3. Include both outputs when reporting the issue
4. Provide steps to reproduce
5. Include system information from diagnostics

## Related Documentation

- [README.md](README.md) - Main documentation
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details

---

**Need Help?** Open an issue on [GitHub](https://github.com/Mittenzx/Adastrea-Director/issues) with debug output and diagnostics.
