# Adastrea Director VS Code Extension

VS Code extension for [Adastrea Director](https://github.com/Mittenzx/Adastrea-Director) - an AI-powered game development assistant for Unreal Engine.

## Features

- **IPC Connection**: Connect to Director IPC server (Python backend) on port 5555
- **AI Queries**: Ask questions about your Unreal Engine project
- **Connection Management**: Automatic reconnection with configurable retry logic
- **Health Checks**: Regular health checks to ensure connection stability
- **Status Indicator**: Visual status bar indicator showing connection state

## Requirements

- VS Code 1.80.0 or higher
- [Adastrea Director](https://github.com/Mittenzx/Adastrea-Director) IPC server running
- Node.js 18+ (for development)

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

- `Director: Connect to Unreal Engine` - Connect to the Director IPC server
- `Director: Disconnect from Unreal Engine` - Disconnect from the server
- `Director: Ask Question` - Ask a question to the Director AI
- `Director: Check Connection Status` - Check the current connection status

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

- `ping` - Health check
- `query` - Ask a question to the AI
- `plan` - Generate a development plan
- `analyze` - Analyze a development goal
- `metrics` - Get performance metrics

## Status Bar Indicator

The extension adds a status bar item showing the connection state:

- 🔴 **Error** - Connection error
- 🟡 **Connecting** - Attempting to connect
- 🟢 **Connected** - Successfully connected
- ⚫ **Disconnected** - Not connected

Click the status bar item to check the current status.

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
