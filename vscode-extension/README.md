# Adastrea Director VS Code Extension

VS Code extension for [Adastrea Director](https://github.com/Mittenzx/Adastrea-Director) - an AI-powered game development assistant for Unreal Engine.

## 🌟 What's New in Phase 2

**Semi-Autonomous Development** is here! The extension now includes:

- 🤖 **Automated Code Generation** - Generate and apply code from natural language
- ✅ **Automated Testing** - Run tests and view results directly in VS Code
- 👤 **Intelligent Approval Workflow** - Review changes with confidence scores
- 📊 **Feedback & Learning** - Help improve suggestions through feedback
- 🎯 **Auto-Approval** - High-confidence changes applied automatically

See [PHASE2_GUIDE.md](PHASE2_GUIDE.md) for complete Phase 2 documentation.

## Features

### Phase 1: Foundation (Complete ✅)
- **IPC Connection**: Connect to Director IPC server (Python backend) on port 5555
- **AI Queries**: Ask questions about your Unreal Engine project
- **Connection Management**: Automatic reconnection with configurable retry logic
- **Health Checks**: Regular health checks to ensure connection stability
- **Status Indicator**: Visual status bar indicator showing connection state

### Phase 2: Semi-Autonomous Development (Complete ✅)
- **Code Generation**: Automated code generation with multiple approaches
- **Code Application**: Apply code changes with intelligent approval workflow
- **Automated Testing**: Execute and view test results
- **Approval Workflow**: Review, approve, reject, or modify code changes
- **Confidence Scoring**: AI-generated confidence levels for each change
- **Auto-Approval**: Configurable thresholds for automatic application
- **Feedback System**: Collect and analyze user feedback for continuous learning
- **Statistics**: View approval rates, feedback metrics, and patterns

## Requirements

- VS Code 1.80.0 or higher
- [Adastrea Director](https://github.com/Mittenzx/Adastrea-Director) IPC server running
- Node.js 18+ (for development)
- (Optional) [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) for AI-assisted debugging with UE logs

### 🤖 GitHub Copilot + UE Logs

The repository includes a `.copilotignore` configuration that allows GitHub Copilot to access Unreal Engine output logs for better debugging assistance, even though these files are excluded from version control.

**Benefits:**
- 🐛 Get AI help analyzing UE crashes and errors
- 💡 Receive context-aware suggestions based on actual runtime behavior
- 🔍 Debug issues faster with Copilot's understanding of log patterns
- 📊 Analyze performance logs and get optimization suggestions

**Quick Start:**
1. Ensure GitHub Copilot extension is installed
2. Open any UE log file (e.g., `Saved/Logs/YourProject.log`)
3. Use Copilot Chat to ask about errors or crashes
4. Get instant analysis and suggested fixes

📖 **See:** [COPILOT_UE_LOGS_GUIDE.md](../COPILOT_UE_LOGS_GUIDE.md) for complete setup and usage instructions

## Installation

### From Source (Development)

1. Clone the Adastrea Director repository:
   ```bash
   git clone https://github.com/Mittenzx/Adastrea-Director.git
   cd Adastrea-Director/vscode-extension
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Compile the extension:
   ```bash
   npm run compile
   ```

4. Open the extension in VS Code:
   ```bash
   code .
   ```

5. Press `F5` to launch the extension in debug mode

## Usage

### Starting the Director IPC Server

Before using the extension, start the Director IPC server:

```bash
cd Adastrea-Director
python Plugins/AdastreaDirector/Python/ipc_server.py --port 5555
```

### Connecting to Director

1. Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Run the command: `Director: Connect to Unreal Engine`
3. The status bar will show the connection status

### Asking Questions

1. Open the Command Palette
2. Run the command: `Director: Ask Question`
3. Enter your question about Unreal Engine or your project
4. View the response in the Output panel (Adastrea Director)

### Available Commands

#### Phase 1 Commands
- `Director: Connect to Unreal Engine` - Connect to the Director IPC server
- `Director: Disconnect from Unreal Engine` - Disconnect from the server
- `Director: Ask Question` - Ask a question to the Director AI
- `Director: Check Connection Status` - Check the current connection status
- `Director: Toggle Debug Mode` - Enable/disable verbose debug logging
- `Director: Run Connection Diagnostics` - Run comprehensive connection diagnostics

#### Phase 2 Commands (New! ✨)
- `Director: Generate and Apply Code` - Generate code from natural language and apply with approval
- `Director: Run Tests` - Execute test suite and view results
- `Director: Review Pending Changes` - Review code changes waiting for approval
- `Director: View Approval History` - View approval statistics and history
- `Director: Show Feedback Statistics` - View feedback metrics and patterns
- `Director: Set Auto-Approval Threshold` - Configure confidence threshold for auto-approval
- `Director: Provide Feedback` - Manually provide feedback on suggestions

## Configuration

Configure the extension in VS Code settings:

```json
{
  "director.ipc.host": "localhost",
  "director.ipc.port": 5555,
  "director.autoConnect": false,
  "director.reconnectInterval": 5000,
  "director.maxReconnectAttempts": 3
}
```

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `director.ipc.host` | string | `"localhost"` | Host address for Director IPC server |
| `director.ipc.port` | number | `5555` | Port for Director IPC server |
| `director.autoConnect` | boolean | `false` | Automatically connect on extension activation |
| `director.reconnectInterval` | number | `5000` | Reconnection interval in milliseconds |
| `director.maxReconnectAttempts` | number | `3` | Maximum number of reconnection attempts |
| `director.requestTimeout` | number | `30000` | Request timeout in milliseconds |
| `director.debugMode` | boolean | `false` | Enable debug mode with verbose logging |
| `director.autoApprovalThreshold` | number | `0.9` | Auto-approval confidence threshold (0.0-1.0) |
| `director.autoRunTests` | boolean | `false` | Automatically run tests after code changes |
| `director.enableFeedbackCollection` | boolean | `true` | Enable automatic feedback collection |

## Connection Protocol

The extension communicates with the Director IPC server using a simple TCP socket protocol with JSON messages:

**Request Format:**
```json
{
  "type": "query",
  "data": "Your question here"
}
```

**Response Format:**
```json
{
  "status": "success",
  "result": "Answer here",
  "message": "pong"
}
```

### Supported Request Types

#### Phase 1 Request Types
- `ping` - Health check
- `query` - Ask a question to the AI
- `plan` - Generate a development plan
- `analyze` - Analyze a development goal
- `metrics` - Get performance metrics

#### Phase 2 Request Types (New! ✨)
- `generate_code` - Generate code modifications for a goal
- `apply_feedback` - Send user feedback for learning
- `get_confidence` - Get confidence score for a change
- `run_tests` - Execute test suite

### Protocol Limitations

**Important:** The current IPC protocol has the following limitations:

1. **No Request IDs**: The protocol does not include request IDs for correlation. Responses are matched to requests using FIFO (First-In-First-Out) order.

2. **Sequential Processing**: Because of the FIFO limitation, requests should be processed sequentially. Concurrent requests may result in incorrect response correlation.

3. **Single Connection**: The extension maintains a single connection to the IPC server. Multiple concurrent operations share this connection.

**Future Improvement**: A future version of the protocol should add request IDs to support concurrent requests and more robust error handling.

## Status Bar Indicator

The extension adds a status bar item showing the connection state:

- 🔴 **Error** - Connection error
- 🟡 **Connecting** - Attempting to connect
- 🟢 **Connected** - Successfully connected
- ⚫ **Disconnected** - Not connected

Click the status bar item to check the current status.

## Debug Mode

The extension includes a comprehensive debug mode that provides detailed logging and diagnostics to help troubleshoot connection issues.

### Enabling Debug Mode

**Option 1: Via Command Palette**
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Run `Director: Toggle Debug Mode`
3. Debug logs will appear in the "Adastrea Director - Debug" output channel

**Option 2: Via Settings**
```json
{
  "director.debugMode": true
}
```

### Debug Features

When debug mode is enabled, the extension provides:

1. **Verbose Logging**: Detailed logs of all operations
   - Connection attempts with socket details
   - Request/response tracking
   - Error details with stack traces
   - State changes and transitions

2. **Diagnostic Information**:
   - System information (platform, Node version, VS Code version)
   - Extension configuration
   - Client state (connection status, pending requests, etc.)
   - Socket information (addresses, ports, bytes transferred)
   - Network connectivity tests
   - Health check results

3. **Connection Diagnostics**:
   - Run `Director: Run Connection Diagnostics` to get a comprehensive report
   - Tests network connectivity to the IPC server
   - Provides troubleshooting recommendations
   - All output is logged to the "Adastrea Director" output channel

### Debug Output Channels

The extension creates two output channels:

1. **Adastrea Director** - Normal operation logs and diagnostics
2. **Adastrea Director - Debug** - Verbose debug logs (only when debug mode is enabled)

### Example Debug Output

```
[2025-12-09T11:33:01.796Z] ℹ INFO: Starting connection attempt
  Details: {
  "host": "localhost",
  "port": 5555,
  "reconnectInterval": 2000,
  "maxReconnectAttempts": 3,
  "requestTimeout": 30000
}
[2025-12-09T11:33:01.805Z] ℹ INFO: Socket connected successfully
  Details: {
  "localAddress": "127.0.0.1",
  "localPort": 50946,
  "remoteAddress": "127.0.0.1",
  "remotePort": 5555
}
```

### When to Use Debug Mode

Enable debug mode when:
- Troubleshooting connection issues
- The extension can't reach the IPC server
- Experiencing intermittent disconnections
- Need detailed connection information for diagnostics
- Reporting bugs or issues

## Troubleshooting

### Connection Refused

If you see "Connection refused" errors:

1. Ensure the Director IPC server is running:
   ```bash
   python Plugins/AdastreaDirector/Python/ipc_server.py --port 5555
   ```

2. Check if port 5555 is available:
   ```bash
   # On Linux/Mac
   lsof -i :5555
   
   # On Windows
   netstat -ano | findstr :5555
   ```

3. Verify the host and port settings in VS Code configuration

### Connection Timeout

If connections timeout:

1. Check firewall settings
2. Verify the IPC server is accessible from your machine
3. Try increasing `director.reconnectInterval`

### Health Check Failures

If health checks fail after connecting:

1. Check the IPC server logs for errors
2. Verify the server is responding to ping requests
3. Try disconnecting and reconnecting

## Development

### Building

```bash
npm run compile
```

### Running Tests

```bash
npm test
```

### Watching for Changes

```bash
npm run watch
```

### Packaging

```bash
npm run vscode:prepublish
npx @vscode/vsce package
```

## Architecture

```
┌─────────────────┐
│   VS Code       │
│   Extension     │
└────────┬────────┘
         │
         │ TCP Socket (JSON)
         │ Port 5555
         │
┌────────▼────────┐
│  Director IPC   │
│     Server      │
│   (Python)      │
└────────┬────────┘
         │
         │
┌────────▼────────┐
│  Director RAG   │
│  Planning Agents│
│  UE Python API  │
└─────────────────┘
```

## Roadmap

See the [parent repository](https://github.com/Mittenzx/Adastrea-Director) for the full roadmap.

### Phase 1 (Current)
- ✅ Extension project structure
- ✅ TypeScript IPC client
- ✅ Connection management
- ✅ Health checks
- ✅ Basic communication

### Phase 2 (Next)
- [ ] Copilot integration
- [ ] Context retrieval from RAG
- [ ] Plan generation command
- [ ] Enhanced UI features

### Phase 3 (Future)
- [ ] Code generation pipeline
- [ ] UE Python API integration
- [ ] Test execution
- [ ] Performance monitoring

## Contributing

Contributions are welcome! Please see the [main repository](https://github.com/Mittenzx/Adastrea-Director) for contribution guidelines.

## License

See [LICENSE](../LICENSE) in the parent repository.

## Links

- [Adastrea Director](https://github.com/Mittenzx/Adastrea-Director)
- [Documentation](https://github.com/Mittenzx/Adastrea-Director/wiki)
- [Issue Tracker](https://github.com/Mittenzx/Adastrea-Director/issues)

---

*Part of the Adastrea Director project - Building tomorrow's game development tools, today.*
