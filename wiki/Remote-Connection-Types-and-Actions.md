# Remote Connection Types and Actions Directory

This document provides a comprehensive directory of all remote connection types available in Adastrea Director, their supported actions, and the Director plugin capabilities.

## Table of Contents

- [Overview](#overview)
- [HTTP Remote Control API](#http-remote-control-api)
- [WebSocket Event Client](#websocket-event-client)
- [Python IPC Server](#python-ipc-server)
- [UE Python API Integration](#ue-python-api-integration)
- [Director Plugin Actions](#director-plugin-actions)
- [Comparison Table](#comparison-table)
- [Best Practices](#best-practices)
- [Examples](#examples)

---

## Overview

Adastrea Director supports multiple remote connection types for interacting with Unreal Engine and the AI backend. Each connection type serves different purposes and has specific capabilities:

1. **HTTP Remote Control API** - Synchronous REST API for direct UE control
2. **WebSocket Event Client** - Real-time event streaming from UE
3. **Python IPC Server** - Inter-process communication between C++ plugin and Python backend
4. **UE Python API Integration** - Direct access to Unreal Engine's Python API
5. **Director Plugin** - Integrated UE plugin combining all capabilities

---

## HTTP Remote Control API

### Description
Python HTTP/REST client for synchronous operations with Unreal Engine's Remote Control API. Uses TCP port 30010 by default.

### Connection Details
- **Protocol**: HTTP/REST over TCP
- **Default Port**: 30010
- **Client Class**: `UnrealRemoteControlClient`
- **Location**: `remote_control/client.py`

### Available Actions

#### Connection Management
| Action | Method | Description | Parameters | Returns |
|--------|--------|-------------|------------|---------|
| Health Check | `health_check()` | Verify connection to UE | None | `bool` - Connection status |
| Close Connection | `close()` | Close HTTP session | None | `None` |

#### Property Operations
| Action | Method | Description | Parameters | Returns |
|--------|--------|-------------|------------|---------|
| Get Property | `get_property(object_path, property_name)` | Retrieve property value from UE object | `object_path` (str), `property_name` (str) | `RemoteControlResponse` with property value |
| Set Property | `set_property(object_path, property_name, value)` | Set property value on UE object | `object_path` (str), `property_name` (str), `value` (Any) | `RemoteControlResponse` |

#### Function Operations
| Action | Method | Description | Parameters | Returns |
|--------|--------|-------------|------------|---------|
| Call Function | `call_function(object_path, function_name, parameters)` | Execute function on UE object | `object_path` (str), `function_name` (str), `parameters` (dict) | `RemoteControlResponse` with return value |

#### Console Commands
| Action | Method | Description | Parameters | Returns |
|--------|--------|-------------|------------|---------|
| Execute Command | `execute_command(command)` | Run console command in UE | `command` (str) | `RemoteControlResponse` with command output |

#### Preset Operations
| Action | Method | Description | Parameters | Returns |
|--------|--------|-------------|------------|---------|
| List Presets | `list_presets()` | Get all Remote Control presets | None | `RemoteControlResponse` with preset list |
| Get Preset | `get_preset(preset_name)` | Get specific preset details | `preset_name` (str) | `RemoteControlResponse` with preset data |

### Features
- Automatic retry with exponential backoff (configurable attempts)
- Connection pooling via `requests.Session`
- Configurable timeouts (default: 30 seconds)
- Comprehensive error handling with specific exceptions
- Request/response validation
- ~10-50ms latency for localhost connections

### Error Handling
- `ConnectionError` - Connection to UE failed
- `RequestError` - API request failed
- `TimeoutError` - Request exceeded timeout
- `ValidationError` - Input validation failed
- `RemoteControlError` - Base exception for all errors

### Configuration Options
```python
UnrealRemoteControlClient(
    host="localhost",           # UE host address
    port=30010,                 # Remote Control API port
    timeout=30,                 # Request timeout (seconds)
    retry_attempts=3,           # Number of retry attempts
    retry_delay=5,              # Delay between retries (seconds)
    verify_ssl=False            # SSL certificate verification
)
```

### Example Usage
```python
from remote_control import UnrealRemoteControlClient

client = UnrealRemoteControlClient(host="localhost", port=30010)

# Check connection
if client.health_check():
    # Execute console command
    response = client.execute_command("stat fps")
    print(response.data)
    
    # Set property
    client.set_property(
        object_path="/Game/MyBlueprint.MyBlueprint_C",
        property_name="Speed",
        value=100.0
    )
    
    # Call function
    result = client.call_function(
        object_path="/Game/MyActor.MyActor_C",
        function_name="TakeDamage",
        parameters={"Amount": 10.0}
    )

client.close()
```

---

## WebSocket Event Client

### Description
Real-time event streaming client for asynchronous updates from Unreal Engine. Receives property changes, function calls, and other events.

### Connection Details
- **Protocol**: WebSocket over TCP
- **Default Port**: 30010 (same as HTTP, different endpoint)
- **Client Class**: `WebSocketEventClient`
- **Location**: `remote_control/websocket_client.py`

### Available Actions

#### Connection Management
| Action | Method | Description | Parameters | Returns |
|--------|--------|-------------|------------|---------|
| Connect | `connect()` | Establish WebSocket connection | None | `bool` - Success status |
| Disconnect | `disconnect()` | Close WebSocket connection | None | `None` |
| Reconnect | Internal | Automatic reconnection on failure | N/A | N/A |

#### Event Handling
| Action | Method | Description | Parameters | Returns |
|--------|--------|-------------|------------|---------|
| Add Event Handler | `add_event_handler(event_type, handler)` | Register callback for event type | `event_type` (EventType), `handler` (Callable) | `None` |
| Remove Event Handler | `remove_event_handler(event_type, handler)` | Unregister event handler | `event_type` (EventType), `handler` (Callable) | `None` |

### Event Types
| Event Type | Enum Value | Description | Triggered When |
|------------|------------|-------------|----------------|
| Property Changed | `EventType.PROPERTY_CHANGED` | UE object property modified | Property value changes |
| Function Called | `EventType.FUNCTION_CALLED` | Function executed on UE object | Function call occurs |
| Preset Changed | `EventType.PRESET_CHANGED` | Remote Control preset modified | Preset configuration changes |
| Connection Status | `EventType.CONNECTION_STATUS` | WebSocket connection state changed | Connect/disconnect events |
| Error | `EventType.ERROR` | Error occurred | Any error condition |

### Features
- Asynchronous event-driven architecture
- Multi-threaded event handling
- Automatic reconnection (configurable attempts)
- Ping/pong keep-alive mechanism
- ~1-5ms latency for event delivery
- Thread-safe event handler registration

### Configuration Options
```python
WebSocketEventClient(
    host="localhost",           # UE host address
    port=30010,                 # Remote Control API port
    reconnect_attempts=10,      # Max reconnection attempts
    reconnect_delay=2,          # Delay between reconnects (seconds)
    ping_interval=30            # Keep-alive ping interval (seconds)
)
```

### Example Usage
```python
from remote_control import WebSocketEventClient, EventType

def on_property_changed(event):
    print(f"Property changed: {event}")

def on_error(event):
    print(f"Error: {event.get('message')}")

# Create WebSocket client
ws_client = WebSocketEventClient(host="localhost", port=30010)

# Add event handlers
ws_client.add_event_handler(EventType.PROPERTY_CHANGED, on_property_changed)
ws_client.add_event_handler(EventType.ERROR, on_error)

# Connect and listen
ws_client.connect()
# ... events handled automatically in background thread ...
ws_client.disconnect()
```

---

## Python IPC Server

### Description
Inter-Process Communication server that bridges the Unreal Engine C++ plugin with the Python AI backend. Uses TCP sockets for JSON-based request/response communication.

### Connection Details
- **Protocol**: TCP Socket with JSON serialization
- **Default Port**: 5555 (configurable)
- **Server Class**: `IPCServer`
- **Location**: `Plugins/AdastreaDirector/Python/ipc_server.py`

### Available Actions

#### System Operations
| Action | Request Type | Description | Data Format | Response Fields |
|--------|--------------|-------------|-------------|-----------------|
| Health Check | `ping` | Verify server is running | Empty string `""` | `status`, `message`, `timestamp` |
| Get Metrics | `metrics` | Retrieve performance statistics | Empty string `""` | `status`, `metrics` (with request counts, times, errors) |
| Reset Metrics | `metrics` | Clear performance counters | String `"reset"` | `status`, `message` |

#### AI Backend Operations
| Action | Request Type | Description | Data Format | Response Fields |
|--------|--------------|-------------|-------------|-----------------|
| Documentation Query | `query` | Query RAG system for documentation | Query string | `status`, `result`, `sources`, `context` |
| Task Planning | `plan` | Generate task plan for goal | Goal description string | `status`, `plan`, `tasks`, `dependencies` |
| Goal Analysis | `analyze` | Analyze development goal | Goal description string | `status`, `analysis`, `recommendations` |
| Document Ingestion | `ingest` | Add documents to knowledge base | JSON with `docs_dir`, `db_path` | `status`, `message`, `documents_processed` |

#### Configuration Operations
| Action | Request Type | Description | Data Format | Response Fields |
|--------|--------------|-------------|-------------|-----------------|
| Set API Key | `set_api_key` | Configure LLM API key | JSON with `provider`, `api_key` | `status`, `message` |
| Get Config | `get_config` | Retrieve current configuration | Empty string `""` | `status`, `config` (dict) |

### Request/Response Format

**Request Format:**
```json
{
  "type": "query|plan|analyze|ping|metrics|ingest|set_api_key|get_config",
  "data": "request-specific data as string or JSON"
}
```

**Response Format:**
```json
{
  "status": "success|error",
  "message": "response message",
  "processing_time_ms": 0.5,
  "error": "error message (only if status is error)",
  ...additional fields depending on request type...
}
```

### Features
- Multi-threaded client handling (one thread per connection)
- Performance monitoring with detailed metrics
- Sub-millisecond latency (< 1ms typical)
- Request timing and statistics tracking
- Graceful error handling and recovery
- Extensible request handler system
- Optional RAG and planning agent integration

### Performance Metrics
(Measured on localhost with test suite `test_ipc_performance.py`)
- **Average Latency**: < 1ms (typical)
- **P95 Latency**: < 1ms (95th percentile)
- **Throughput**: Typically > 4000 requests/second (measured locally; varies with hardware and workload)
- **Exceeds Target**: Up to 50x better than 50ms requirement (in local tests)

### Configuration Options
```python
IPCServer(
    host='127.0.0.1',          # Bind address (localhost only for security)
    port=5555,                 # IPC port
    enable_rag=False,          # Enable RAG system integration
    enable_planning=False,     # Enable planning agents
    verbose=False              # Enable debug logging
)
```

### Example Usage
```python
# Start server with RAG and planning enabled
python ipc_server.py --port 5555 --enable-rag --enable-planning --verbose

# Client communication (from C++ plugin or Python)
import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 5555))

request = {
    'type': 'query',
    'data': 'What is the main gameplay loop?'
}
sock.sendall((json.dumps(request) + '\n').encode('utf-8'))

response = json.loads(sock.recv(4096).decode('utf-8'))
print(response)

sock.close()
```

---

## UE Python API Integration

### Description
Direct integration with Unreal Engine's built-in Python API (`import unreal`). Provides access to editor automation, asset operations, and runtime functionality from Python.

### Connection Details
- **Protocol**: Direct Python API (in-process)
- **Integration Type**: Hybrid (External Python + UE Python)
- **API Wrapper**: `UEPythonBridge`
- **Location**: `Plugins/AdastreaDirector/Python/ue_python_api.py`

### Available Actions

#### Asset Operations
| Action | Method | Description | Parameters | Returns |
|--------|--------|-------------|------------|---------|
| Get Selected Assets | `get_selected_assets()` | Get currently selected assets in Content Browser | None | List of `UEAssetInfo` objects |
| Find Assets by Class | `find_assets_by_class(asset_class, path="/Game")` | Find assets of a specific class | `asset_class` (str), `path` (str, optional) | List of `UEAssetInfo` objects |
| Load Asset | `load_asset(asset_path)` | Load asset by path | `asset_path` (str) | Asset object or `None` |
| Save Asset | `save_asset(asset_path)` | Save asset to disk | `asset_path` (str) | `bool` - Success status |

#### Actor Operations
| Action | Method | Description | Parameters | Returns |
|--------|--------|-------------|------------|---------|
| Spawn Actor | `spawn_actor(actor_class, location=(0,0,0), rotation=(0,0,0), actor_name=None)` | Create actor in level | `actor_class` (str), `location` (tuple, optional), `rotation` (tuple, optional), `actor_name` (str, optional) | Actor object or `None` |
| Get Actors by Class | `get_all_actors_of_class(actor_class)` | Find actors by class in current level | `actor_class` (str) | List of `UEActorInfo` objects |
| Get Selected Actors | `get_selected_actors()` | Get currently selected actors in level | None | List of `UEActorInfo` objects |
| Delete Actor | `delete_actor(actor_name)` | Remove actor from level by name | `actor_name` (str) | `bool` - Success status |

#### Editor Operations
| Action | Method | Description | Parameters | Returns |
|--------|--------|-------------|------------|---------|
| Execute Console Command | `execute_console_command(command)` | Run UE console command | `command` (str) | Command output |
| Show Notification | `show_notification(text, duration)` | Display editor notification | `text` (str), `duration` (float) | `None` |
| Log Message | `log_message(message, level)` | Write to UE log | `message` (str), `level` (str) | `None` |
| Get Editor World | `get_editor_world()` | Get current editor world | None | World object |

#### Project Information
| Action | Method | Description | Parameters | Returns |
|--------|--------|-------------|------------|---------|
| Get Engine Version | `get_engine_version()` | Get UE version string | None | Version string |
| Get Project Directory | `get_project_directory()` | Get project root path | None | Directory path |

### Features
- Direct access to full Unreal Engine Python API
- Asset registry integration
- Editor automation capabilities
- Level/actor manipulation
- Console command execution
- Comprehensive error handling
- 25+ comprehensive tests (100% passing)

### Architecture
The UE Python API uses a **hybrid architecture**:
1. **External Python Backend** - Runs the AI/RAG system independently
2. **UE Python Environment** - Executes within Unreal Engine Editor
3. **IPC Bridge** - Connects both environments for seamless integration

### Example Usage
```python
import unreal
from ue_python_api import UEPythonBridge

bridge = UEPythonBridge()

# Get selected assets
assets = bridge.get_selected_assets()
print(f"Found {len(assets)} selected assets")

# Find assets by class
blueprints = bridge.find_assets_by_class("Blueprint", path="/Game")

# Spawn an actor
actor = bridge.spawn_actor(
    "StaticMeshActor",
    location=(0.0, 0.0, 0.0),
    rotation=(0.0, 0.0, 0.0),
    actor_name="MyActor"
)

# Execute console command
result = bridge.execute_console_command("stat fps")

# Show notification
bridge.show_notification("Task completed!", duration=3.0)
```

---

## Director Plugin Actions

### Description
The Adastrea Director Unreal Engine plugin combines all remote connection types into an integrated in-editor experience. Provides UI, backend management, and AI assistance.

### Connection Details
- **Plugin Name**: AdastreaDirector
- **Integration**: C++ (UE Plugin) + Python Backend
- **UI Framework**: Slate (UE's native UI)
- **Location**: `Plugins/AdastreaDirector/`

### Available Actions

#### UI Operations
| Action | Component | Description | Access Method | Features |
|--------|-----------|-------------|---------------|----------|
| Open Panel | Main Plugin | Open AI assistant panel | Window → Developer Tools → Adastrea Director | Dockable tab integration |
| Query Tab | UI Tab | Ask questions to AI | Click "Query" tab | RAG-based answers, conversation history |
| Ingestion Tab | UI Tab | Add documents to knowledge base | Click "Ingestion" tab | Progress bar, status updates |
| Dashboard Tab | UI Tab | View system status | Click "Dashboard" tab | 6 status indicators, real-time monitoring |
| Settings Dialog | Settings UI | Configure API keys and options | Click ⚙️ or Ctrl+, | API key management, display settings |

#### Backend Management
| Action | Component | Description | When Triggered | Result |
|--------|-----------|-------------|----------------|--------|
| Start Python Backend | Process Manager | Launch Python IPC server | Plugin initialization | Backend ready for queries |
| Stop Python Backend | Process Manager | Shutdown Python server | Editor close or manual stop | Clean shutdown |
| Reconnect Backend | Connection Manager | Re-establish IPC connection | Connection lost or manual | Restored functionality |
| Check Backend Health | Health Monitor | Verify backend status | Every 0.5 seconds (dashboard) | Status indicators updated |

#### Query Operations
| Action | Purpose | Description | Input | Output |
|--------|---------|-------------|-------|--------|
| Documentation Query | RAG System | Search knowledge base | Natural language question | Answer with sources |
| Task Planning | Planning Agent | Break down development goals | Goal description | Task list with dependencies |
| Goal Analysis | Analysis Agent | Analyze goal feasibility | Goal description | Analysis and recommendations |
| Code Generation | Code Agent | Generate implementation | Feature description | Code examples |

#### Knowledge Base Operations
| Action | Purpose | Description | Input | Output |
|--------|---------|-------------|-------|--------|
| Ingest Documents | Document Processing | Add docs to vector DB | Documentation folder path | Processing status, doc count |
| Update Knowledge Base | Refresh | Re-ingest all documents | One-click action | Updated database |
| Clear History | Cleanup | Remove conversation history | User confirmation | Empty conversation |

#### Configuration Operations
| Action | Purpose | Description | Storage | Scope |
|--------|---------|-------------|---------|-------|
| Set API Key | Authentication | Configure LLM provider keys | Project Saved directory | Per-project |
| Set LLM Provider | Provider Selection | Choose Gemini or OpenAI | Config file | Per-project |
| Set Embedding Provider | Embeddings | Choose HuggingFace or OpenAI | Config file | Per-project |
| Adjust Font Size | Display | Change UI text size | Config file | Per-project |
| Toggle Auto-save | Behavior | Enable/disable auto-save | Config file | Per-project |

### Plugin Features

#### Current Features (Implemented)
- ✅ **Basic Plugin Shell** - C++ module structure, build system
- ✅ **Python Bridge** - IPC client, subprocess management
- ✅ **Python Backend IPC** - Performance-optimized server (< 1ms latency)
- ✅ **Basic UI** - Dockable Slate panel, query/results display
- ✅ **UE Python API** - Direct `import unreal` integration
- ✅ **Tabbed Interface** - Query, Ingestion, Dashboard tabs
- ✅ **Settings Dialog** - API key management, configuration
- ✅ **Status Dashboard** - 6 real-time status indicators
- ✅ **Document Ingestion** - In-editor document processing

#### Status Indicators
The Dashboard tab provides 6 color-coded status lights:

| Indicator | What It Shows | Green = | Yellow = | Red = |
|-----------|---------------|---------|----------|-------|
| 🔌 Python Process | Backend process state | Running | Starting | Not running |
| 🔗 IPC Connection | Socket connection | Connected | Connecting | Disconnected |
| 🤖 Python Bridge | Overall bridge health | Ready | Initializing | Error |
| 💚 Backend Health | Backend operational | Healthy | Degraded | Unhealthy |
| 🔍 Query Processing | Query system state | Available | Processing | Error |
| 📚 Document Ingestion | Ingestion system | Ready | Processing | Error |

#### Keyboard Shortcuts
- `Enter` - Send query (in query input field)
- `Ctrl+,` - Open Settings dialog

#### Planned Features
- 🚀 Planning agent integration
- 🚀 Performance profiling UI
- 🚀 Bug detection integration
- 🚀 Code quality monitoring
- 🚀 Agent orchestration dashboard

### Example Workflow
```
1. Open Unreal Engine Editor
2. Window → Developer Tools → Adastrea Director
3. Dashboard Tab → Verify all indicators are green
4. Settings (Ctrl+,) → Configure API keys → Save
5. Ingestion Tab → Browse docs folder → Start Ingestion
6. Query Tab → Type "What is the main gameplay loop?" → Send
7. View AI response with sources from your documentation
```

---

## Comparison Table

### Feature Comparison

| Feature | HTTP Remote Control | WebSocket Events | Python IPC | UE Python API | Director Plugin |
|---------|---------------------|------------------|------------|---------------|-----------------|
| **Connection Type** | HTTP/REST | WebSocket | TCP Socket | In-Process | Hybrid (All) |
| **Communication** | Synchronous | Asynchronous | Synchronous | Synchronous | Both |
| **Default Port** | 30010 | 30010 | 5555 | N/A | 5555 + 30010 |
| **Latency** | 10-50ms | 1-5ms | < 1ms | < 0.1ms | Varies |
| **Property Get/Set** | ✅ Yes | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Function Calls** | ✅ Yes | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Console Commands** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| **Event Streaming** | ❌ No | ✅ Yes | ❌ No | ✅ Yes* | ✅ Yes |
| **Asset Operations** | ❌ No | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Actor Operations** | ❌ No | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **AI/RAG Queries** | ❌ No | ❌ No | ✅ Yes | ❌ No | ✅ Yes |
| **Task Planning** | ❌ No | ❌ No | ✅ Yes | ❌ No | ✅ Yes |
| **Document Ingestion** | ❌ No | ❌ No | ✅ Yes | ❌ No | ✅ Yes |
| **UI Integration** | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Requires UE Running** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| **Python Backend** | ❌ No | ❌ No | ✅ Yes | ❌ No | ✅ Yes |
| **Retry Logic** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Error Handling** | ✅ Comprehensive | ✅ Good | ✅ Comprehensive | ⚠️ Basic | ✅ Comprehensive |

*Via Python delegates and callbacks

### Use Case Recommendations

| Use Case | Recommended Connection | Why | Alternative |
|----------|------------------------|-----|-------------|
| **Change UE property values** | HTTP Remote Control | Direct, reliable, well-documented | UE Python API |
| **Monitor real-time changes** | WebSocket Events | Low latency, async, event-driven | UE Python API |
| **Query documentation** | Python IPC / Plugin | AI/RAG integration, context-aware | N/A |
| **Plan development tasks** | Python IPC / Plugin | Planning agents available | N/A |
| **Automate editor tasks** | UE Python API | Full editor access, powerful | Plugin |
| **Create/manipulate assets** | UE Python API | Asset registry integration | HTTP (limited) |
| **Integrated UE workflow** | Director Plugin | All features in one UI | Python IPC |
| **External automation** | HTTP Remote Control | No plugin required | UE Python API |
| **Performance profiling** | HTTP + WebSocket | Commands + event monitoring | Plugin (future) |
| **Debugging/testing** | HTTP Remote Control | Easy to script and test | Python IPC |

### Performance Comparison

| Metric | HTTP Remote Control | WebSocket Events | Python IPC | UE Python API | Director Plugin |
|--------|---------------------|------------------|------------|---------------|-----------------|
| **Latency (avg)** | 10-50ms | 1-5ms | < 1ms | Variable* | 1-10ms |
| **Throughput** | ~100 req/s | ~1000 msg/s | > 4000 req/s¹ | CPU-bound | > 1000 req/s |
| **Overhead** | Low | Very Low | Very Low | Minimal | Low |
| **Connection Cost** | Per request | Persistent | Persistent | None | Persistent |
| **Memory Usage** | ~10MB | ~5MB | ~20MB | Minimal | ~50MB |
| **CPU Usage** | Low | Low | Low | Minimal | Medium |

*UE Python API latency is variable - minimal for simple property access, higher for complex operations like asset loading or world queries. No network overhead, but subject to Python interpreter and UE processing time.

¹Measured on localhost in optimal conditions; actual throughput may vary depending on hardware, OS, and workload.

---

## Best Practices

### When to Use Each Connection Type

#### HTTP Remote Control API
**Best For:**
- External scripts and automation
- Testing and debugging
- Property manipulation
- Console command execution
- One-off operations

**Avoid For:**
- High-frequency updates (use WebSocket)
- Real-time monitoring (use WebSocket)
- AI-powered queries (use Python IPC/Plugin)

**Tips:**
- Always check `health_check()` before operations
- Use retry logic for production systems
- Close connection when done to free resources
- Batch operations when possible

#### WebSocket Events
**Best For:**
- Real-time monitoring
- Event-driven architecture
- Property change notifications
- Performance profiling
- Long-running observations

**Avoid For:**
- Sending commands to UE (use HTTP)
- One-time queries (use HTTP)
- Heavy processing (offload to separate thread)

**Tips:**
- Always handle connection failures gracefully
- Use event handlers for specific event types
- Implement reconnection logic
- Keep handlers lightweight

#### Python IPC Server
**Best For:**
- AI/RAG-powered queries
- Task planning and goal analysis
- Document ingestion
- Backend integration
- Plugin communication

**Avoid For:**
- Direct UE manipulation (use HTTP or UE Python API)
- Real-time event handling (use WebSocket)
- Standalone UE automation (use HTTP)

**Tips:**
- Enable RAG and planning only when needed
- Monitor performance metrics
- Use async requests for long operations
- Handle JSON parsing errors

#### UE Python API
**Best For:**
- Editor automation
- Asset manipulation
- Actor operations
- Complex UE workflows
- Plugin development

**Avoid For:**
- Remote/external scripts (use HTTP)
- AI queries (use Python IPC)
- Runtime-only operations (check availability)

**Tips:**
- Check if `unreal` module is available
- Use try-except for UE API calls
- Test in editor before runtime
- Leverage asset registry for efficiency

#### Director Plugin
**Best For:**
- Integrated UE development workflow
- AI-assisted development
- Documentation queries while working
- In-editor task planning
- All-in-one solution

**Avoid For:**
- Automated external scripts (use HTTP)
- CI/CD pipelines (use HTTP)
- Headless operations (use Python IPC)

**Tips:**
- Configure API keys first
- Ingest documentation early
- Use dashboard to monitor health
- Leverage keyboard shortcuts for efficiency

### Security Considerations

#### HTTP Remote Control API
- ⚠️ Default configuration allows localhost only
- ⚠️ Whitelist commands in production
- ⚠️ Use authentication for remote access
- ⚠️ Validate all inputs before sending to UE

#### WebSocket Events
- ⚠️ Use secure WebSocket (WSS) for remote connections
- ⚠️ Implement authentication tokens
- ⚠️ Limit event types exposed
- ⚠️ Rate limiting for event handlers

#### Python IPC Server
- ⚠️ **CRITICAL**: Binds to localhost only (127.0.0.1)
- ⚠️ Never expose IPC port to network
- ⚠️ Validate all JSON inputs
- ⚠️ Sanitize file paths for ingestion
- ⚠️ Use secure API key storage

#### UE Python API
- ⚠️ Runs with full editor privileges
- ⚠️ Validate all file operations
- ⚠️ Sanitize asset paths
- ⚠️ Be cautious with asset deletion

#### Director Plugin
- ⚠️ API keys stored in plaintext in project directory
- ⚠️ Add config files to `.gitignore`
- ⚠️ Never commit API keys to version control
- ⚠️ Use project-specific keys (not personal keys)

### Performance Optimization

#### HTTP Remote Control API
- Use connection pooling (automatic with `requests.Session`)
- Batch multiple operations when possible
- Increase timeout for slow operations
- Use local connections for best performance

#### WebSocket Events
- Keep event handlers lightweight
- Offload heavy processing to background threads
- Adjust ping interval based on network stability
- Limit number of simultaneous handlers

#### Python IPC Server
- Enable only needed features (RAG, planning)
- Monitor metrics to identify bottlenecks
- Use connection pooling for multiple clients
- Profile slow request handlers

#### UE Python API
- Cache asset registry queries
- Use bulk operations for multiple assets
- Minimize editor UI updates
- Batch actor operations

#### Director Plugin
- Start backend on demand if startup is slow
- Clear conversation history periodically
- Ingest only necessary documentation
- Use dashboard to identify issues early

---

## Examples

### Example 1: Performance Monitoring with HTTP + WebSocket

```python
from remote_control import UnrealRemoteControlClient, WebSocketEventClient, EventType
import time

# Create clients
http_client = UnrealRemoteControlClient(host="localhost", port=30010)
ws_client = WebSocketEventClient(host="localhost", port=30010)

# Track performance metrics
fps_readings = []

def on_property_changed(event):
    if event.get('property') == 'CurrentFPS':
        fps_readings.append(event.get('value'))

# Setup WebSocket for monitoring
ws_client.add_event_handler(EventType.PROPERTY_CHANGED, on_property_changed)
ws_client.connect()

# Enable FPS display via HTTP
http_client.execute_command("stat fps")

# Monitor for 10 seconds
time.sleep(10)

# Calculate average FPS
if fps_readings:
    avg_fps = sum(fps_readings) / len(fps_readings)
    print(f"Average FPS: {avg_fps:.2f}")

# Cleanup
ws_client.disconnect()
http_client.close()
```

### Example 2: AI-Powered Asset Analysis with Plugin + UE Python API

```python
# This runs within the Director Plugin context

from ue_python_api import UEPythonBridge
import json

# Get Blueprint assets
bridge = UEPythonBridge()
blueprints = bridge.find_assets_by_class("Blueprint", path="/Game")

# Prepare data for AI analysis
asset_data = {
    "total_blueprints": len(blueprints),
    "asset_paths": [bp.asset_path for bp in blueprints[:10]]  # First 10
}

# Send to IPC server for AI analysis
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 5555))

request = {
    'type': 'analyze',
    'data': f"Analyze these blueprints: {json.dumps(asset_data)}"
}
sock.sendall((json.dumps(request) + '\n').encode('utf-8'))

response = json.loads(sock.recv(8192).decode('utf-8'))
print(f"AI Analysis: {response.get('analysis')}")

sock.close()

# Show result in UE
bridge.show_notification(f"Analyzed {len(blueprints)} blueprints", duration=5.0)
```

### Example 3: Automated Testing with Test Agent

```python
from remote_control import TestAgent

# Create test agent
with TestAgent(agent_id="automated_tester") as agent:
    # Define test suite
    tests = [
        {
            "name": "verify_fps_command",
            "type": "command",
            "command": "stat fps",
            "expected_output": None  # Just verify it executes
        },
        {
            "name": "check_player_health",
            "type": "property",
            "object_path": "/Game/Characters/Player.Player_C",
            "property_name": "Health",
            "expected_value": 100.0,
            "tolerance": 0.1
        },
        {
            "name": "test_damage_function",
            "type": "function",
            "object_path": "/Game/Characters/Player.Player_C",
            "function_name": "TakeDamage",
            "parameters": {"Amount": 10.0},
            "expected_return": True
        }
    ]
    
    # Run all tests
    results = agent.run_test_suite(tests)
    
    # Print summary
    agent.print_test_summary(results)
    
    # Export to file
    agent.export_test_results("/tmp/test_results.json")
```

### Example 4: Complete Workflow with Director Plugin

```
Step 1: Setup (First Time)
1. Open Unreal Engine Editor
2. Window → Developer Tools → Adastrea Director
3. Press Ctrl+, to open Settings
4. Select LLM Provider: Gemini
5. Enter your Gemini API Key
6. Select Embedding Provider: HuggingFace (Free)
7. Click Save

Step 2: Ingest Documentation
1. Click "Ingestion" tab
2. Browse and select your Docs folder
3. Set database path (or use default)
4. Click "Start Ingestion"
5. Wait for progress bar to complete
6. Status shows "Ingestion complete!"

Step 3: Query AI Assistant
1. Click "Query" tab
2. Type: "What are the main character abilities?"
3. Press Enter or click "Send Query"
4. View response with source citations
5. Ask follow-up questions naturally

Step 4: Plan Development Tasks
1. Type: "Create a plan to add a new inventory system"
2. Send query
3. Receive detailed task breakdown with:
   - Prioritized tasks
   - Dependencies
   - Effort estimates
   - Implementation approaches

Step 5: Monitor System Health
1. Click "Dashboard" tab
2. Verify all 6 indicators are green
3. If any are red:
   - Check "Detailed Status" section
   - Click "Reconnect" if needed
   - View "System Logs" for details
```

### Example 5: Remote Control Agent Pattern

```python
from remote_control import RemoteControlAgent

class PerformanceMonitorAgent(RemoteControlAgent):
    """Agent that monitors and optimizes performance."""
    
    def execute_task(self, task):
        """Execute performance monitoring task."""
        if task == "profile_fps":
            return self._profile_fps()
        elif task == "optimize_settings":
            return self._optimize_settings()
        else:
            return {"success": False, "error": "Unknown task"}
    
    def _profile_fps(self):
        """Profile current FPS."""
        # Enable FPS display
        result = self.execute_command("stat fps")
        
        # Get current FPS property (example)
        fps = self.get_property(
            "/Game/GameMode.GameMode_C",
            "CurrentFPS"
        )
        
        return {
            "success": True,
            "fps": fps,
            "recommendation": "Optimize" if fps < 60 else "Performance OK"
        }
    
    def _optimize_settings(self):
        """Apply performance optimizations."""
        # Reduce shadow quality
        self.execute_command("sg.ShadowQuality 2")
        
        # Reduce post-processing
        self.execute_command("sg.PostProcessQuality 2")
        
        return {
            "success": True,
            "message": "Applied performance optimizations"
        }

# Use the agent
with PerformanceMonitorAgent(
    agent_id="perf_monitor",
    ue_host="localhost",
    enable_websocket=True
) as agent:
    # Profile FPS
    result = agent.execute_task("profile_fps")
    print(f"FPS: {result['fps']}")
    
    # Optimize if needed
    if result.get('fps', 60) < 60:
        result = agent.execute_task("optimize_settings")
        print(result['message'])
```

---

## Additional Resources

### Documentation
- **HTTP Remote Control API**: `remote_control/README.md`
- **Python IPC Server**: `Plugins/AdastreaDirector/Python/README.md`
- **UE Python API**: `Plugins/AdastreaDirector/UE_PYTHON_API.md`
- **Director Plugin**: `Plugins/AdastreaDirector/README.md`
- **Test Agent Guide**: `remote_control/TEST_AGENT_GUIDE.md`

### Official Unreal Engine Documentation
- [Remote Control for Unreal Engine](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-for-unreal-engine)
- [Python in Unreal Engine](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)
- [Unreal Engine Python API Reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api)

### Testing
- **Remote Control Tests**: `tests/remote_control/` (67 tests)
- **Plugin Tests**: `Plugins/AdastreaDirector/Python/test_*.py` (25 tests)
- **IPC Performance Tests**: `Plugins/AdastreaDirector/Python/test_ipc_performance.py`

### Examples
- **Remote Control Demo**: `examples/remote_control_demo.py`
- **Phase 3 Demos**: `examples/phase3_*.py`
- **Plugin Examples**: `Plugins/AdastreaDirector/Python/README.md`

---

## Troubleshooting

### HTTP Remote Control API

**Problem**: Connection failed
- ✓ Verify UE is running
- ✓ Check Remote Control plugins are enabled
- ✓ Verify launch flags: `-RCWebControlEnable -RCWebInterfaceEnable`
- ✓ Test in browser: `http://localhost:30010/remote/control/api`

**Problem**: Command not working
- ✓ Verify command is valid in UE console
- ✓ Check command whitelist in config
- ✓ Try simpler command like "stat fps"

### WebSocket Events

**Problem**: Connection drops frequently
- ✓ Increase ping interval
- ✓ Check network stability
- ✓ Verify UE WebSocket support is enabled
- ✓ Review UE logs for WebSocket errors

### Python IPC Server

**Problem**: Server won't start
- ✓ Check if port 5555 is available
- ✓ Verify Python dependencies installed
- ✓ Check for firewall blocking
- ✓ Review server logs for errors

**Problem**: Slow responses
- ✓ Check metrics with `{"type": "metrics", "data": ""}`
- ✓ Disable RAG/planning if not needed
- ✓ Check Python process CPU usage

### UE Python API

**Problem**: Import unreal fails
- ✓ Verify running in UE Python environment
- ✓ Check if Python plugin is enabled in UE
- ✓ Use Editor (not runtime) for editor features

### Director Plugin

**Problem**: Plugin won't load
- ✓ Regenerate project files
- ✓ Rebuild project
- ✓ Check plugin .uplugin file is valid
- ✓ Verify plugin is in Plugins folder

**Problem**: Backend won't connect
- ✓ Check Dashboard tab for status indicators
- ✓ Verify Python is installed and accessible
- ✓ Click "Reconnect" button
- ✓ Check system logs for errors
- ✓ Verify port 5555 is available

---

## Version History

- **v1.0** (December 2024) - Initial comprehensive documentation
  - HTTP Remote Control API documented
  - WebSocket Event Client documented
  - Python IPC Server documented
  - UE Python API Integration documented
  - Director Plugin actions documented
  - Comparison tables added
  - Best practices and examples included

---

## Contributing

To add new remote connection types or actions:
1. Implement the connection type in appropriate module
2. Add comprehensive tests
3. Update this documentation with:
   - Description and connection details
   - Available actions table
   - Configuration options
   - Example usage
   - Update comparison table
4. Add to troubleshooting section if needed

---

## License

See project LICENSE file.

---

*Last Updated: December 2024*
*Adastrea Director - AI Game Development Assistant*
