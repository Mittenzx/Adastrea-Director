# IPC Server MCP Integration Guide

## Overview

The IPC server now exposes GUI functionality (MCP operations and UE log access) through new request handlers. This allows VS Code Copilot to interact with Unreal Engine and access logs without needing the GUI.

## New Request Types

### MCP Operations

#### `mcp_connect`
Connect to Unreal Engine via MCP.

**Request:**
```json
{
  "type": "mcp_connect",
  "data": ""
}
```

**Response (Success):**
```json
{
  "status": "success",
  "connected": true,
  "project_info": {
    "info": "Project details..."
  },
  "processing_time_ms": 150.5
}
```

**Response (Error):**
```json
{
  "status": "error",
  "error": "Failed to connect to Unreal Engine. Ensure UE is running with Python Remote Execution enabled.",
  "connected": false,
  "processing_time_ms": 10.2
}
```

#### `mcp_disconnect`
Disconnect from Unreal Engine.

**Request:**
```json
{
  "type": "mcp_disconnect",
  "data": ""
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Disconnected from Unreal Engine",
  "processing_time_ms": 5.1
}
```

#### `mcp_status`
Check MCP connection status.

**Request:**
```json
{
  "type": "mcp_status",
  "data": ""
}
```

**Response:**
```json
{
  "status": "success",
  "connected": true,
  "server_info": {
    "name": "AdastreaMCP",
    "version": "0.1.0",
    "connected": true
  },
  "processing_time_ms": 2.3
}
```

#### `mcp_execute_python`
Execute Python code in Unreal Engine.

**Request:**
```json
{
  "type": "mcp_execute_python",
  "data": "{\"code\": \"import unreal\\nprint(unreal.SystemLibrary.get_engine_version())\"}"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "isError": false,
    "content": [
      {
        "type": "text",
        "text": "5.3.0-12345678"
      }
    ]
  },
  "processing_time_ms": 120.7
}
```

#### `mcp_console_command`
Execute a console command in Unreal Engine.

**Request:**
```json
{
  "type": "mcp_console_command",
  "data": "{\"command\": \"stat fps\"}"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "isError": false,
    "content": [
      {
        "type": "text",
        "text": "FPS: 60.00"
      }
    ]
  },
  "processing_time_ms": 85.3
}
```

#### `mcp_list_tools`
List all available MCP tools.

**Request:**
```json
{
  "type": "mcp_list_tools",
  "data": ""
}
```

**Response:**
```json
{
  "status": "success",
  "tools": [
    {
      "name": "editor_run_python",
      "description": "Execute Python code in Unreal Editor",
      "inputSchema": {
        "type": "object",
        "properties": {
          "code": {
            "type": "string",
            "description": "Python code to execute"
          }
        },
        "required": ["code"]
      }
    },
    {
      "name": "editor_list_assets",
      "description": "List all Unreal assets in the project",
      "inputSchema": {
        "type": "object",
        "properties": {}
      }
    }
  ],
  "processing_time_ms": 3.2
}
```

#### `mcp_call_tool`
Call any MCP tool with custom arguments.

**Request:**
```json
{
  "type": "mcp_call_tool",
  "data": "{\"tool\": \"editor_list_assets\", \"arguments\": {}}"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "isError": false,
    "content": [
      {
        "type": "text",
        "text": "['/Game/Blueprints/MyBlueprint', '/Game/Materials/M_Default']"
      }
    ]
  },
  "processing_time_ms": 200.4
}
```

### Log Access Operations

#### `get_ue_logs` / `list_ue_logs`
Get a list of recent UE log files.

**Request:**
```json
{
  "type": "get_ue_logs",
  "data": "{\"limit\": 10}"
}
```

**Response:**
```json
{
  "status": "success",
  "logs": [
    {
      "filename": "ue_gui_session_2025-12-10_10-28-45.log",
      "path": "/path/to/logs/ue_gui_session_2025-12-10_10-28-45.log",
      "size": 15234,
      "modified": 1702210125.5
    },
    {
      "filename": "ue_gui_session_2025-12-10_09-15-30.log",
      "path": "/path/to/logs/ue_gui_session_2025-12-10_09-15-30.log",
      "size": 8912,
      "modified": 1702205730.2
    }
  ],
  "count": 2,
  "processing_time_ms": 12.5
}
```

#### `read_ue_log`
Read the contents of a specific UE log file.

**Request:**
```json
{
  "type": "read_ue_log",
  "data": "{\"filename\": \"ue_gui_session_2025-12-10_10-28-45.log\", \"max_lines\": 1000}"
}
```

**Response:**
```json
{
  "status": "success",
  "filename": "ue_gui_session_2025-12-10_10-28-45.log",
  "content": "================================================================================\nUnreal Engine Output Log\n...",
  "line_count": 856,
  "truncated": false,
  "max_lines": 1000,
  "processing_time_ms": 45.7
}
```

**Security Note:** The `read_ue_log` handler includes security checks to prevent directory traversal attacks. Files must be within the logs directory.

## Usage from VS Code Extension

### TypeScript Example

```typescript
import { IPCClient } from './ipcClient';

const client = new IPCClient('localhost', 5555);

// Connect to UE via MCP
async function connectToUnreal() {
  const response = await client.sendRequest({
    type: 'mcp_connect',
    data: ''
  });
  
  if (response.status === 'success' && response.connected) {
    console.log('Connected to Unreal Engine');
    console.log('Project:', response.project_info);
  }
}

// Execute Python in UE
async function runPythonInUE(code: string) {
  const response = await client.sendRequest({
    type: 'mcp_execute_python',
    data: JSON.stringify({ code })
  });
  
  if (response.status === 'success') {
    const result = response.result.content[0].text;
    console.log('Result:', result);
  }
}

// Get recent UE logs
async function getRecentLogs() {
  const response = await client.sendRequest({
    type: 'get_ue_logs',
    data: JSON.stringify({ limit: 5 })
  });
  
  if (response.status === 'success') {
    console.log(`Found ${response.count} logs`);
    for (const log of response.logs) {
      console.log(`- ${log.filename} (${log.size} bytes)`);
    }
  }
}

// Read a specific log
async function readLog(filename: string) {
  const response = await client.sendRequest({
    type: 'read_ue_log',
    data: JSON.stringify({ filename, max_lines: 500 })
  });
  
  if (response.status === 'success') {
    console.log('Log content:', response.content);
  }
}
```

## Usage from Python

### Python Example

```python
import socket
import json

def send_ipc_request(request_type, data=""):
    """Send a request to the IPC server."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5555))
    
    request = {
        'type': request_type,
        'data': data
    }
    
    sock.sendall((json.dumps(request) + '\n').encode('utf-8'))
    response_data = sock.recv(4096).decode('utf-8')
    sock.close()
    
    return json.loads(response_data)

# Connect to UE
response = send_ipc_request('mcp_connect')
print(f"Connected: {response.get('connected')}")

# Execute Python
code = "import unreal\nprint(unreal.SystemLibrary.get_engine_version())"
response = send_ipc_request('mcp_execute_python', json.dumps({'code': code}))
print(f"Result: {response}")

# Get logs
response = send_ipc_request('get_ue_logs', json.dumps({'limit': 5}))
print(f"Found {response['count']} logs")

# Read a log
if response['logs']:
    filename = response['logs'][0]['filename']
    log_response = send_ipc_request('read_ue_log', json.dumps({'filename': filename}))
    print(f"Log content: {log_response['content'][:200]}...")
```

## Integration with VS Code Copilot Chat

### Adding MCP Commands to Chat Participant

Update the VS Code extension's `@director` chat participant to support MCP operations:

```typescript
// In chatParticipant.ts
vscode.chat.createChatParticipant('director', async (request, context, stream, token) => {
  if (request.command === 'connect-ue') {
    // Connect to Unreal Engine
    const response = await client.sendRequest({
      type: 'mcp_connect',
      data: ''
    });
    
    if (response.status === 'success') {
      stream.markdown('✅ Connected to Unreal Engine\n\n');
      stream.markdown(`Project: ${response.project_info.info}`);
    } else {
      stream.markdown(`❌ Connection failed: ${response.error}`);
    }
  }
  
  if (request.command === 'exec') {
    // Execute Python in UE
    const code = request.prompt;
    const response = await client.sendRequest({
      type: 'mcp_execute_python',
      data: JSON.stringify({ code })
    });
    
    if (response.status === 'success') {
      stream.markdown('```\n' + response.result.content[0].text + '\n```');
    }
  }
  
  if (request.command === 'analyze-logs') {
    // Analyze recent UE logs
    const logsResponse = await client.sendRequest({
      type: 'get_ue_logs',
      data: JSON.stringify({ limit: 1 })
    });
    
    if (logsResponse.status === 'success' && logsResponse.logs.length > 0) {
      const logFile = logsResponse.logs[0];
      const logContent = await client.sendRequest({
        type: 'read_ue_log',
        data: JSON.stringify({ filename: logFile.filename, max_lines: 500 })
      });
      
      if (logContent.status === 'success') {
        // Analyze the log content with Copilot
        stream.markdown('Analyzing UE logs...\n\n');
        // Pass log content to LLM for analysis
        const analysis = await analyzeWithLLM(logContent.content);
        stream.markdown(analysis);
      }
    }
  }
});
```

### Example Slash Commands

Add these to the VS Code extension:

- `@director /connect-ue` - Connect to Unreal Engine
- `@director /exec <code>` - Execute Python code in UE
- `@director /console <command>` - Run UE console command
- `@director /analyze-logs` - Analyze recent UE logs for errors
- `@director /list-tools` - List available MCP tools

## Error Handling

All handlers return consistent error responses:

```json
{
  "status": "error",
  "error": "Error message here",
  "processing_time_ms": 5.2
}
```

Common error scenarios:
- **Not connected**: "Not connected to Unreal Engine. Call mcp_connect first."
- **MCP not available**: "MCP server not available. Ensure mcp_server module is installed."
- **Invalid JSON**: "Invalid request format. Expected JSON with..."
- **File not found**: "Log file not found: filename.log"
- **Access denied**: "Access denied: File must be in logs directory"

## Security Considerations

### Path Traversal Protection

The `read_ue_log` handler includes security checks:
1. Resolves the requested file path
2. Resolves the logs directory path
3. Ensures the file is within the logs directory
4. Rejects requests for files outside the logs directory

Example:
```python
# This will be rejected
request = {
  'type': 'read_ue_log',
  'data': '{"path": "../../../etc/passwd"}'
}
# Response: {"status": "error", "error": "Access denied: File must be in logs directory"}
```

### File Size Limits

The `read_ue_log` handler limits the number of lines returned (default: 1000) to prevent memory issues with very large log files.

## Performance Metrics

All requests include `processing_time_ms` in the response for performance monitoring. The IPC server tracks:
- Total requests
- Request count by type
- Average, min, max processing time by type
- Error count by type

Use the `metrics` request type to get current statistics:

```json
{
  "type": "metrics",
  "data": ""
}
```

## Testing

Run the test suite:

```bash
cd Adastrea-Director
pytest tests/test_ipc_mcp_integration.py -v
```

The test suite includes:
- 12 MCP handler tests
- 6 log access handler tests
- 2 handler registration tests
- Total: 20 tests

## Troubleshooting

### MCP Connection Issues

**Problem:** `mcp_connect` returns error "Failed to connect to Unreal Engine"

**Solutions:**
1. Ensure Unreal Engine is running
2. Enable Python Editor Script Plugin in UE
3. Enable Remote Execution in Project Settings → Python
4. Check that multicast discovery is not blocked by firewall

### Log Access Issues

**Problem:** `get_ue_logs` returns empty list

**Solutions:**
1. Ensure the GUI has been used to connect to UE at least once
2. Check that the logs directory exists: `logs/`
3. Verify log files have `.log` extension

**Problem:** `read_ue_log` returns "Access denied"

**Solutions:**
1. Use only `filename` parameter, not full paths
2. Ensure the file is in the logs directory
3. Check file permissions

## Next Steps

### VS Code Extension Updates

To fully integrate these new IPC handlers:

1. **Update `ipcClient.ts`** to include helper methods:
   ```typescript
   async connectToUnreal() { ... }
   async executeUEPython(code: string) { ... }
   async getUELogs(limit?: number) { ... }
   async readUELog(filename: string) { ... }
   ```

2. **Add new commands** to `package.json`:
   ```json
   {
     "command": "director.connectUnreal",
     "title": "Director: Connect to Unreal Engine (MCP)"
   }
   ```

3. **Update chat participant** to handle MCP slash commands

4. **Add UE log viewer** in VS Code UI

### Future Enhancements

- **Streaming logs**: Real-time log streaming via WebSocket
- **Log filtering**: Server-side log filtering by level/source
- **Log search**: Search across multiple log files
- **Asset management**: Additional MCP tools for asset operations
- **Performance profiling**: Integrated performance profiling tools
