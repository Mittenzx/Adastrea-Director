# Changelog

All notable changes to the Adastrea Director VS Code extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-09

### Added

#### IPC Client
- TypeScript IPC client for communicating with Director IPC server (port 5555)
- TCP socket-based communication with JSON protocol
- Automatic reconnection with configurable retry logic
- Health check system (ping/pong)
- Request timeout handling (30 seconds)
- Connection state management (disconnected, connecting, connected, error)
- Event handlers for state changes and errors

#### Commands
- `Director: Connect to Unreal Engine` - Connect to the Director IPC server
- `Director: Disconnect from Unreal Engine` - Disconnect from the server
- `Director: Ask Question` - Ask a question to the Director AI
- `Director: Check Connection Status` - Check the current connection status

#### IPC API Methods
- `connect()` - Establish connection to IPC server
- `disconnect()` - Close connection
- `ping()` - Health check
- `query(question)` - Ask a question to the AI
- `plan(goal)` - Generate a development plan
- `analyze(goal)` - Analyze a development goal
- `getMetrics()` - Get performance metrics

#### User Interface
- Status bar indicator showing connection state
  - 🟢 Connected
  - 🟡 Connecting
  - 🔴 Error
  - ⚫ Disconnected
- Output channel for logging and responses
- Command palette integration
- Visual feedback for operations

#### Configuration
- `director.ipc.host` - IPC server host (default: localhost)
- `director.ipc.port` - IPC server port (default: 5555)
- `director.autoConnect` - Auto-connect on activation (default: false)
- `director.reconnectInterval` - Reconnection interval in ms (default: 5000)
- `director.maxReconnectAttempts` - Max reconnection attempts (default: 3)

#### Testing
- Unit tests for IPC client
- Integration tests for end-to-end communication
- Test script for manual integration testing
- 100% test pass rate

#### Documentation
- README.md with comprehensive documentation
- QUICKSTART.md for getting started
- CHANGELOG.md for version history
- Inline code documentation
- Configuration documentation
- Troubleshooting guide

### Technical Details

#### Architecture
```
VS Code Extension (TypeScript)
    ↓
IPC Client (TCP Socket + JSON)
    ↓
Director IPC Server (Python, Port 5555)
    ↓
Director Backend (RAG, Planning, Agents)
```

#### Protocol
- **Request Format**: `{"type": "query", "data": "question"}\n`
- **Response Format**: `{"status": "success", "result": "answer"}\n`
- **Supported Types**: ping, query, plan, analyze, metrics, run_tests

#### Dependencies
- @types/vscode ^1.80.0
- @types/node ^20.x
- typescript ^5.3.0
- @vscode/test-electron ^2.3.0
- @vscode/vsce ^3.2.1
- @types/mocha (dev)

### Known Limitations

- Single request at a time (sequential processing)
- No request ID tracking in protocol
- 30-second request timeout (not configurable)
- Limited error recovery options
- No offline mode or caching

### Future Enhancements

See [Remote-Connection-Types-and-Actions.md](../Remote-Connection-Types-and-Actions.md) for the full roadmap.

#### Phase 2 (Planned)
- Copilot integration for context-aware code generation
- Enhanced context retrieval from RAG system
- Plan generation with visualization
- Code application workflow

#### Phase 3 (Planned)
- Code generation pipeline
- Test execution integration
- Performance monitoring
- Automated improvement suggestions

## [Unreleased]

### Planned Features
- Multiple concurrent requests
- Request/response correlation with IDs
- Configurable timeouts
- Offline mode with queuing
- Response caching
- WebSocket support for real-time updates
- Advanced error recovery
- Plan visualization UI
- Code diff preview
- Test result visualization

---

## Version History

- **0.1.0** (2024-12-09) - Initial release with basic IPC communication

---

For the full roadmap and detailed documentation, see the [Adastrea Director repository](https://github.com/Mittenzx/Adastrea-Director).
