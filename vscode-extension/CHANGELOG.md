# Changelog

All notable changes to the Adastrea Director VS Code extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-12-09

### Added - Phase 1 (Weeks 3-4): Copilot Integration ✅

**This release completes Phase 1 of the VS Code extension development plan!**

#### Chat Participant (@director)
- GitHub Copilot Chat participant for natural language interaction with Director
- Integration with Director's RAG system for context-aware responses
- Support for complex queries about Unreal Engine and project-specific topics

#### Slash Commands
- `/ask` - Ask general questions about Unreal Engine (default command)
- `/plan` - Generate structured development plans for features
- `/analyze` - Analyze goals and assess complexity
- `/context` - Retrieve context from Director's RAG system
- `/help` - Display available commands and usage examples

#### Context Integration
- Hover provider for Unreal Engine symbols (UObject, AActor, FVector, etc.)
- Code actions for selected code ("Ask Director about this code", "Get Director context")
- Enhanced context provider for project-specific knowledge
- Context-aware responses based on current file and surrounding code

#### Developer Experience
- Seamless integration with existing Director commands
- Follow-up suggestions after chat responses
- Rich markdown formatting in chat responses
- Webview panel for detailed context display
- Code action menu integration in editor

#### Configuration Settings
- `director.copilot.enabled` - Enable/disable Copilot Chat integration
- `director.copilot.enableHoverContext` - Toggle hover documentation
- `director.copilot.enableCodeActions` - Toggle code action menu items

#### Documentation
- Comprehensive [COPILOT_INTEGRATION.md](COPILOT_INTEGRATION.md) guide
- Updated README with Copilot features and examples
- Example workflows and best practices
- Troubleshooting guide for Copilot-specific issues

### Technical Improvements
- New `copilotParticipant.ts` module for chat request handling
- New `copilotContextProvider.ts` module for context integration
- Enhanced extension activation for Copilot APIs
- Type-safe implementation with full TypeScript support
- Graceful degradation if Copilot APIs unavailable

### Phase 1 Completion Status
- ✅ Weeks 1-2: Extension Setup (v0.1.0) - **COMPLETE**
- ✅ Weeks 3-4: Copilot Integration (v0.3.0) - **COMPLETE**
- ✅ Weeks 5-6: Basic Workflows (v0.1.0) - **COMPLETE**

**🎉 Phase 1 is now 100% complete!**

---

## [0.2.0] - 2025-12-09

### Added - Phase 2: Semi-Autonomous Development ✨

#### Code Generation & Application
- `Director: Generate and Apply Code` - Generate code from natural language goals
- Automated code modification generation with multiple approaches
- Code applicator service with intelligent approval workflow
- Support for create, modify, and delete operations
- Multi-file modification support in single operation
- Confidence scoring for each generated modification

#### Approval Workflow
- Interactive approval UI with multiple options:
  - ✓ Approve - Apply changes immediately
  - ✗ Reject - Reject with optional reason
  - 👁 Preview - View side-by-side diff
  - ✎ Edit - Open file for manual editing
- Auto-approval based on configurable confidence threshold
- `Director: Review Pending Changes` - Review queued modifications
- `Director: View Approval History` - View approval statistics
- `Director: Set Auto-Approval Threshold` - Configure auto-approval

#### Test Execution
- `Director: Run Tests` - Execute test suites via IPC server
- Support for multiple test types (all, ipc, plugin, unit, integration, remote)
- Dedicated test output channel
- Test results with pass/fail counts
- Optional webview for visual test results
- Navigation to test failure locations
- Integration with feedback system

#### Feedback & Learning
- `Director: Provide Feedback` - Submit manual feedback
- `Director: Show Feedback Statistics` - View feedback analytics
- Feedback collection for approval/rejection decisions
- Star ratings (1-5) for suggestions
- Feedback storage in workspace state
- Automatic sync to IPC server for learning
- Common rejection reason tracking
- Frequently approved file pattern identification

#### IPC Protocol Extensions
- `generate_code` - Request code generation for a goal
- `apply_feedback` - Send user feedback to server
- `get_confidence` - Get confidence score for changes
- Enhanced `run_tests` - Execute test suites

#### Configuration
- `director.autoApprovalThreshold` - Confidence threshold (0.0-1.0, default: 0.9)
- `director.autoRunTests` - Auto-run tests after code changes (default: false)
- `director.enableFeedbackCollection` - Enable feedback collection (default: true)
- `director.debugMode` - Enable debug mode with verbose logging (default: false)

#### Services
- **CodeApplicator**: Handles code application with approval workflow
- **TestExecutor**: Manages test execution and result display
- **FeedbackService**: Collects and analyzes user feedback

### Changed
- Updated package version to 0.2.0
- Extension context now stored globally for cross-function access
- TypeScript strict mode disabled for better compatibility
- IPC server enhanced with Phase 2 request handlers
- Connection workflow improved for Phase 2 service initialization

### Technical Details

#### New Services Architecture
```
Extension (extension.ts)
    ├── CodeApplicator (codeApplicator.ts)
    ├── TestExecutor (testExecutor.ts)
    └── FeedbackService (feedbackService.ts)
```

#### Approval Workflow
1. Code generated with confidence scores
2. High confidence (≥threshold) → Auto-apply
3. Low confidence → Request user approval
4. User approves/rejects with optional feedback
5. Feedback sent to server for learning

#### Previous Version Features (0.1.0)

#### Debug Mode
- Comprehensive debug mode with verbose logging
- `Director: Toggle Debug Mode` command
- `Director: Run Connection Diagnostics` command
- Separate "Adastrea Director - Debug" output channel
- Detailed logging of connection attempts, socket operations, and state changes
- Error logging with stack traces
- Request/response tracking with IDs and timing

#### Diagnostics
- `getDiagnostics()` method providing complete system information
- System information (platform, Node version, VS Code version)
- Extension configuration snapshot
- Client state details (connection status, pending requests)
- Socket information (addresses, ports, bytes transferred, ready state)
- Network connectivity testing
- Health check integration
- Troubleshooting recommendations

## [0.1.0] - 2025-12-09

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

#### Phase 2 (Complete ✅)
- ✅ Code generation and application
- ✅ Intelligent approval workflow
- ✅ Test execution integration
- ✅ Feedback and learning system
- ✅ Confidence-based auto-approval

#### Phase 3 (Planned)
- Fully autonomous development
- Multi-agent collaboration
- Continuous refactoring
- Performance optimization
- Automatic bug detection
- Test generation

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

- **0.2.0** (2025-12-09) - Phase 2: Semi-Autonomous Development
- **0.1.0** (2025-12-09) - Initial release with basic IPC communication

---

For the full roadmap and detailed documentation, see the [Adastrea Director repository](https://github.com/Mittenzx/Adastrea-Director).
