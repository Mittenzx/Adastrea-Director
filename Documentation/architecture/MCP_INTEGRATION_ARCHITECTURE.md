# MCP Integration Architecture

**Visual reference for Adastrea-Director + Adastrea-MCP integration**

---

## System Overview

The Adastrea ecosystem consists of two complementary MCP servers that work together to provide comprehensive Unreal Engine development assistance:

```
┌─────────────────────────────────────────────────────────────────┐
│                          AI LAYER                                │
│  Claude Desktop, VS Code Copilot, Cline, Zed, etc.             │
│  - Natural language interface                                    │
│  - Tool discovery and execution                                  │
│  - Context management                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ MCP Protocol (stdio/JSON-RPC)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    ADASTREA-MCP SERVER                           │
│                    (Node.js/TypeScript)                          │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STATIC ANALYSIS LAYER (37 tools, 13 resources)          │   │
│  │                                                           │   │
│  │  • .uproject Parser         • Blueprint Inspector       │   │
│  │  • C++ Code Analysis        • Asset Registry Scanner    │   │
│  │  • Module/Plugin Detection  • Build Config Analyzer     │   │
│  │  • Code Generator (8 tools) • UE5.6+ Knowledge DB       │   │
│  │  • Actor Templates          • Component Analysis        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ INTEGRATION LAYER (Phase 2.1 Infrastructure)            │   │
│  │                                                           │   │
│  │  • DirectorClient (HTTP)    • Graceful Fallback         │   │
│  │  • EditorBridge             • Auto-reconnection         │   │
│  │  • Health Monitoring        • Error Handling            │   │
│  └─────────────────┬───────────────────────────────────────┘   │
└────────────────────┼───────────────────────────────────────────┘
                     │
                     │ REST API (HTTP/JSON)
                     │ http://localhost:3001
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                 ADASTREA-DIRECTOR REST API                       │
│                    (Python Flask/FastAPI)                        │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ REST API ENDPOINTS (To Be Implemented)                   │   │
│  │                                                           │   │
│  │  GET  /health               - Connection status          │   │
│  │  GET  /api/editor/state     - Current editor state       │   │
│  │  GET  /api/project/info     - Project information        │   │
│  │  POST /api/console/execute  - Run console command        │   │
│  │  POST /api/python/execute   - Execute Python in UE       │   │
│  │  POST /api/assets/list      - List project assets        │   │
│  └─────────────────┬───────────────────────────────────────┘   │
│                    │                                             │
│  ┌─────────────────▼───────────────────────────────────────┐   │
│  │ MCP TOOL BRIDGE (Delegates to existing MCP tools)        │   │
│  │                                                           │   │
│  │  • editor_run_python        • editor_list_assets         │   │
│  │  • editor_console_command   • editor_project_info        │   │
│  │  • editor_get_map_info      • editor_create_object       │   │
│  │  • editor_take_screenshot   • 6 more tools...            │   │
│  └─────────────────┬───────────────────────────────────────┘   │
└────────────────────┼───────────────────────────────────────────┘
                     │
                     │ Python Remote Execution Protocol
                     │ (Multicast UDP 239.0.0.1:6766 discovery)
                     │ (TCP command channel)
                     │
┌────────────────────▼────────────────────────────────────────────┐
│              UNREAL ENGINE EDITOR                                │
│              (with Python Editor Script Plugin)                  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ PYTHON REMOTE EXECUTION                                  │   │
│  │  • Execute Python scripts                                │   │
│  │  • Access UE Python API                                  │   │
│  │  • Asset management                                      │   │
│  │  • Level editing                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ UNREAL ENGINE SYSTEMS                                    │   │
│  │  • Asset Registry   • Blueprint System                   │   │
│  │  • Level Editor     • Console Commands                   │   │
│  │  • Actor System     • Python Interpreter                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Example: "Spawn a Cube at (0,0,100)"

```
1. AI Agent (VS Code Copilot)
   ↓ "Spawn a cube at position 0,0,100"
   
2. Adastrea-MCP Server (Node.js)
   ↓ Analyzes request
   ↓ Determines runtime operation needed
   ↓ Calls Director REST API
   
3. HTTP Request
   POST http://localhost:3001/api/python/execute
   {
     "code": "import unreal\nactor = unreal.EditorLevelLibrary.spawn_actor_from_class(...)"
   }
   
4. Adastrea-Director REST API (Python)
   ↓ Receives HTTP request
   ↓ Validates request
   ↓ Delegates to MCP tool: editor_run_python
   
5. Python Remote Execution
   ↓ Sends command to UE Editor
   ↓ Waits for response
   
6. Unreal Engine Editor
   ↓ Executes Python code
   ↓ Spawns StaticMeshActor
   ↓ Returns result
   
7. Response flows back:
   UE Editor → Director → HTTP Response → Adastrea-MCP → AI Agent
   
8. AI Agent displays: "✅ Created StaticMeshActor at (0,0,100)"
```

---

## Component Responsibilities

### Adastrea-MCP (Node.js)

**What it does:**
- Serves as the single MCP endpoint for AI agents
- Performs static analysis without UE running
- Generates UE-compliant code
- Provides UE5.6+ knowledge and best practices
- Coordinates with Director for runtime operations

**When to use:**
- Analyzing project structure
- Generating boilerplate code
- Querying UE knowledge
- Working on multiple projects
- When UE Editor is closed

### Adastrea-Director (Python)

**What it does:**
- Provides REST API for runtime operations
- Executes commands in live UE Editor
- Manages Python Remote Execution protocol
- Bridges HTTP to UE communication
- Handles UE Editor state queries

**When to use:**
- Spawning/modifying actors
- Executing console commands
- Running Python in UE Editor
- Querying live asset data
- Taking editor screenshots

---

## Communication Protocols

### 1. AI Agent ↔ Adastrea-MCP: MCP Protocol (stdio)

**Protocol**: Model Context Protocol over stdio  
**Format**: JSON-RPC messages  
**Transport**: Standard input/output streams

Example MCP message:
```json
{
  "type": "tools/call",
  "id": "msg_123",
  "params": {
    "name": "execute_console_command",
    "arguments": {
      "command": "stat fps"
    }
  }
}
```

### 2. Adastrea-MCP ↔ Adastrea-Director: REST API (HTTP)

**Protocol**: HTTP/REST  
**Format**: JSON  
**Transport**: TCP on localhost:3001

Example HTTP request:
```http
POST /api/console/execute HTTP/1.1
Host: localhost:3001
Content-Type: application/json

{
  "command": "stat fps"
}
```

### 3. Adastrea-Director ↔ UE Editor: Python Remote Execution

**Protocol**: Custom JSON protocol  
**Discovery**: UDP Multicast (239.0.0.1:6766)  
**Commands**: TCP connection (dynamic port)

Example discovery message:
```json
{
  "version": 1,
  "magic": "ue_py",
  "node_id": "...",
  "node_endpoints": {
    "command_endpoint": "127.0.0.1:6776"
  }
}
```

---

## Deployment Configurations

### Configuration 1: Full Stack (Recommended)

**Components:**
- Adastrea-MCP server (Node.js)
- Adastrea-Director REST API (Python)
- Unreal Engine with Python plugin

**Startup order:**
1. Start Unreal Engine project
2. Start Adastrea-Director REST API
3. Configure AI client to use Adastrea-MCP
4. Adastrea-MCP auto-connects to Director

**Benefits:**
- Maximum capabilities
- Offline static analysis available
- Runtime operations when needed
- Graceful degradation

### Configuration 2: Director Only (Lightweight)

**Components:**
- Adastrea-Director MCP stdio (Python)
- Unreal Engine with Python plugin

**Startup order:**
1. Start Unreal Engine project
2. Configure AI client with Director stdio MCP

**Benefits:**
- Simpler setup
- No Node.js dependency
- Direct UE integration

**Limitations:**
- No static analysis
- No code generation
- No UE knowledge database

### Configuration 3: MCP Only (Static Analysis)

**Components:**
- Adastrea-MCP server (Node.js)

**Startup order:**
1. Start Adastrea-MCP server
2. Configure AI client

**Benefits:**
- Works offline
- No UE required
- Multi-project support

**Limitations:**
- No runtime operations
- Can't execute in UE
- No live data

---

## Graceful Degradation

### When Director is Unavailable

Adastrea-MCP automatically falls back to offline mode:

| Operation | Fallback Behavior |
|-----------|-------------------|
| List assets | Uses cached asset registry from previous scan |
| Get project info | Reads .uproject file |
| Blueprint inspection | Static analysis of .uasset metadata |
| Spawn actor | Returns error with helpful message |
| Console command | Returns error with helpful message |
| Python execution | Returns error with helpful message |

### Connection States

```
┌─────────────┐
│  Connected  │ ← Director available, UE running
└─────┬───────┘
      │
      ↓ Connection lost / UE closed
      │
┌─────▼───────┐
│ Degraded    │ ← Director unavailable, use cache
└─────┬───────┘
      │
      ↓ Automatic retry after 30s
      │
┌─────▼───────┐
│ Reconnected │ ← Director back online
└─────────────┘
```

---

## Security Considerations

### Network Security

**Current:**
- Localhost connections only (127.0.0.1)
- No authentication required
- CORS enabled for localhost

**Future (Optional):**
- API key authentication
- Token-based auth (JWT)
- Rate limiting
- IP whitelisting

### Trust Boundaries

```
TRUSTED:
┌────────────────────────────────────┐
│ AI Agent (same machine)            │
│ Adastrea-MCP (localhost)           │
│ Adastrea-Director (localhost)      │
│ UE Editor (local process)          │
└────────────────────────────────────┘

UNTRUSTED:
- Remote connections (rejected by default)
- Network traffic outside localhost
- Arbitrary code execution (sandboxed by UE)
```

---

## Performance Characteristics

### Latency Breakdown

**Static Analysis (Adastrea-MCP only):**
- Tool execution: < 10ms
- File system access: 10-50ms
- Code generation: 50-200ms
- **Total: 50-250ms**

**Runtime Operations (via Director):**
- HTTP request/response: 1-5ms (localhost)
- MCP tool execution: 10-50ms
- Python Remote Execution: 50-200ms
- UE command execution: 50-500ms (depends on operation)
- **Total: 100-750ms**

### Throughput

- **Concurrent requests**: 10+ (limited by UE Editor)
- **Requests per second**: 5-20 (depends on operation complexity)
- **Connection pool**: 1 (single UE Editor instance)

### Resource Usage

**Adastrea-MCP:**
- Memory: ~50-100MB
- CPU: < 5% idle, 10-20% active
- Disk: Minimal (reads only)

**Adastrea-Director REST API:**
- Memory: ~100-150MB
- CPU: < 5% idle, 10-30% active
- Network: Localhost only

---

## Error Handling Flow

```
AI Agent Request
      ↓
Adastrea-MCP
      ↓
  ┌───┴────┐
  │ Local? │ → Yes → Execute locally → Return result
  └───┬────┘
      ↓ No (needs Director)
      │
  ┌───▼───────────┐
  │ Director up?  │ → No → Return error (graceful message)
  └───┬───────────┘
      ↓ Yes
      │
  HTTP Request to Director
      ↓
  ┌───▼──────────┐
  │ UE running?  │ → No → Return error (helpful message)
  └───┬──────────┘
      ↓ Yes
      │
  Execute in UE
      ↓
  ┌───▼──────────┐
  │ Success?     │ → No → Return UE error
  └───┬──────────┘
      ↓ Yes
      │
  Return result to AI
```

---

## Future Enhancements

### Phase 2: Advanced Integration

1. **WebSocket Support**
   - Bidirectional real-time communication
   - Editor event subscriptions
   - Automatic state updates

2. **Event Streaming**
   - Asset changes
   - Level modifications
   - Compilation results
   - Test execution

3. **Batch Operations**
   - Execute multiple commands atomically
   - Transaction support
   - Rollback capability

### Phase 3: Intelligence Layer

1. **Context Awareness**
   - Remember previous operations
   - Suggest related actions
   - Predict next steps

2. **Performance Optimization**
   - Request caching
   - Connection pooling
   - Parallel execution

3. **Advanced Security**
   - Multi-user support
   - Role-based permissions
   - Audit logging

---

## Testing Strategy

### Unit Tests
- Each MCP tool in isolation
- REST endpoint handlers
- HTTP client functionality
- Error handling paths

### Integration Tests
- End-to-end tool execution
- Director connection handling
- Fallback behavior
- Timeout handling

### Performance Tests
- Latency measurement
- Throughput testing
- Resource usage monitoring
- Stress testing

### Acceptance Tests
- AI agent workflows
- Real-world use cases
- Multi-tool operations
- Error recovery

---

## Monitoring & Observability

### Health Checks

**Adastrea-MCP:**
- Director connection status
- Last successful request timestamp
- Error rate (last hour)
- Average response time

**Adastrea-Director:**
- UE Editor connection status
- Python Remote Execution health
- Request count (last hour)
- Failed request count

### Logging

**Log Levels:**
- ERROR: Connection failures, execution errors
- WARN: Degraded mode, retries, timeouts
- INFO: Successful operations, state changes
- DEBUG: Request/response details, timing

### Metrics

**Track:**
- Requests per minute
- Average latency (p50, p95, p99)
- Error rate
- Connection uptime %
- Cache hit rate

---

## Related Documentation

- **[MCP_READINESS_PLAN.md](../development/MCP_READINESS_PLAN.md)** - Complete integration strategy
- **[MCP_INTEGRATION_QUICKSTART.md](../development/MCP_INTEGRATION_QUICKSTART.md)** - Quick implementation guide
- **[MCP_SERVER_GUIDE.md](../../mcp_server/MCP_SERVER_GUIDE.md)** - Adastrea-Director MCP usage
- **Adastrea-MCP Docs** - In separate repository

---

**Version**: 1.0  
**Last Updated**: December 31, 2025  
**Status**: Design Complete, Implementation Pending
