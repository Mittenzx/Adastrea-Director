# Unreal Engine Remote Control API Client

Python client for interacting with Unreal Engine projects via the Remote Control API.

## ⚠️ Integration Status

**Q: Is this integrated with gui_director or VSCode extension?**

**A: No, not yet.** This is a standalone, production-ready module. For integration status and how to integrate:
- See **[REMOTE_CONTROL_INTEGRATION_STATUS.md](../REMOTE_CONTROL_INTEGRATION_STATUS.md)** for complete details
- TL;DR: Module exists and works, but needs 2-4 hours to integrate with GUI, 4-8 hours for VSCode

## Overview

This module provides a comprehensive interface to Unreal Engine's Remote Control API, enabling:
- Property get/set operations on UE objects
- Function calls on Blueprints and C++ classes
- Console command execution
- Real-time event streaming via WebSocket
- Base agent class for autonomous agents
- **Automated testing via TestAgent** (NEW)

## Quick Start

### Basic HTTP Client

```python
from remote_control import UnrealRemoteControlClient

# Create client
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

### WebSocket Event Client

```python
from remote_control import WebSocketEventClient, EventType

def on_property_changed(event):
    print(f"Property changed: {event}")

# Create WebSocket client
ws_client = WebSocketEventClient(host="localhost", port=30010)

# Add event handler
ws_client.add_event_handler(EventType.PROPERTY_CHANGED, on_property_changed)

# Connect and listen
ws_client.connect()
# ... events will be handled automatically ...
ws_client.disconnect()
```

### Remote Control Agent

```python
from remote_control import RemoteControlAgent

class MyAgent(RemoteControlAgent):
    def execute_task(self, task):
        # Use self.remote_control to interact with UE
        result = self.execute_command("stat fps")
        return {"success": True, "data": result}

# Use agent
with MyAgent(agent_id="my_agent", ue_host="localhost") as agent:
    result = agent.execute_task("profile_performance")
    print(result)
```

### Test Agent (NEW)

```python
from remote_control import TestAgent

# Create test agent for automated testing
with TestAgent(agent_id="automated_tester") as agent:
    # Define tests
    tests = [
        {
            "name": "test_fps_command",
            "type": "command",
            "command": "stat fps"
        },
        {
            "name": "test_player_health",
            "type": "property",
            "object_path": "/Game/Player.Player_C",
            "property_name": "Health",
            "expected_value": 100.0
        }
    ]
    
    # Run tests
    results = agent.run_test_suite(tests)
    agent.print_test_summary(results)
    
    # Export results
    agent.export_test_results("/tmp/test_results.json")
```

**See [TEST_AGENT_GUIDE.md](TEST_AGENT_GUIDE.md) for complete documentation.**

## Components

### UnrealRemoteControlClient

HTTP/REST client for synchronous operations:
- `health_check()` - Check connection status
- `get_property(object_path, property_name)` - Get property value
- `set_property(object_path, property_name, value)` - Set property value
- `call_function(object_path, function_name, parameters)` - Call function
- `execute_command(command)` - Execute console command
- `list_presets()` - List Remote Control presets
- `get_preset(preset_name)` - Get preset details

### WebSocketEventClient

WebSocket client for asynchronous event streaming:
- `connect()` - Establish connection
- `disconnect()` - Close connection
- `add_event_handler(event_type, handler)` - Register event handler
- `remove_event_handler(event_type, handler)` - Unregister event handler

Event types:
- `PROPERTY_CHANGED` - Property value changed
- `FUNCTION_CALLED` - Function was called
- `PRESET_CHANGED` - Preset was modified
- `CONNECTION_STATUS` - Connection status changed
- `ERROR` - Error occurred

### RemoteControlAgent

Base class for agents that interact with Unreal Engine:
- Combines HTTP and WebSocket clients
- Provides high-level helper methods
- Manages connection lifecycle
- Supports context manager pattern
- Abstract `execute_task()` method for subclass implementation

### TestAgent (NEW)

Specialized agent for automated testing:
- **Property Testing**: Validate object properties and values
- **Function Testing**: Execute and verify function calls
- **Command Testing**: Run console commands and check outputs
- **Test Suites**: Run multiple tests in sequence
- **Result Reporting**: Detailed pass/fail/error reporting
- **Export Results**: Save test results to JSON
- See [TEST_AGENT_GUIDE.md](TEST_AGENT_GUIDE.md) for full documentation

## Requirements

### Unreal Engine Setup

1. **Enable plugins** (Project Settings → Plugins):
   - Remote Control API
   - Remote Control Web Interface

2. **Launch Unreal Engine with flags**:
   ```bash
   UnrealEditor.exe MyProject.uproject -RCWebControlEnable -RCWebInterfaceEnable
   ```

3. **Verify connection**:
   - Open browser to `http://localhost:30010/remote/control/api`
   - Should see API documentation

### Python Dependencies

```bash
pip install requests websocket-client
```

## Configuration

Create `config/remote_control_config.yaml`:

```yaml
remote_control:
  default_host: "localhost"
  default_port: 30010
  timeout_seconds: 30
  retry_attempts: 3

websocket:
  enable: true
  reconnect_attempts: 10
  ping_interval_seconds: 30
```

## Testing

Run tests:

```bash
# All remote control tests
pytest tests/remote_control/ -v

# With coverage
pytest tests/remote_control/ --cov=remote_control --cov-report=html
```

All tests use mocking - no running Unreal Engine instance required.

## Examples

See `examples/remote_control_demo.py` for comprehensive examples including:
- Basic client operations
- WebSocket event handling
- Context manager usage
- Performance monitoring
- Error handling

## Documentation

- **📖 Comprehensive Connection Types Guide**: `../wiki/Remote-Connection-Types-and-Actions.md` - Complete directory of all remote connection types with comparisons
- **Full API Documentation**: `docs/remote-control/REMOTE_CONTROL_API.md`
- **Configuration Guide**: `config/remote_control_config.yaml`
- **Integration Guide**: `PHASE3_GUIDE.md`
- **Official UE Docs**: [Remote Control for Unreal Engine](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-for-unreal-engine)

## Architecture

```
┌─────────────────────────────────────┐
│   Python Application                │
│   ┌─────────────────────────────┐   │
│   │  RemoteControlAgent         │   │
│   │  - execute_task()           │   │
│   │  - execute_command()        │   │
│   │  - get/set_property()       │   │
│   └──────────┬──────────────────┘   │
│              │                       │
│   ┌──────────┴──────────────────┐   │
│   │  UnrealRemoteControlClient  │   │
│   │  HTTP/REST operations       │   │
│   └──────────┬──────────────────┘   │
│              │                       │
│   ┌──────────┴──────────────────┐   │
│   │  WebSocketEventClient       │   │
│   │  Real-time events           │   │
│   └─────────────────────────────┘   │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│   Remote Control API (UE)           │
│   Port 30010 (HTTP + WebSocket)     │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│   Unreal Engine 5.6+                │
│   Editor or Runtime                 │
└─────────────────────────────────────┘
```

## Error Handling

The module provides specific exceptions:
- `RemoteControlError` - Base exception
- `ConnectionError` - Connection failed
- `RequestError` - Request failed
- `TimeoutError` - Request timed out
- `ValidationError` - Input validation failed

All exceptions include descriptive error messages and can be caught specifically:

```python
from remote_control import RemoteControlError, ConnectionError

try:
    client = UnrealRemoteControlClient()
    client.execute_command("stat fps")
except ConnectionError as e:
    print(f"Cannot connect to UE: {e}")
except RemoteControlError as e:
    print(f"Remote Control error: {e}")
```

## Security Considerations

- Default configuration only accepts localhost connections
- Whitelist allowed commands in production
- Use authentication for non-localhost deployments
- Rate limiting to prevent abuse
- Validate all inputs before sending to UE

## Performance

- HTTP requests: ~10-50ms latency (localhost)
- WebSocket messages: ~1-5ms latency
- Automatic retry with exponential backoff
- Connection pooling via requests.Session
- Configurable timeouts and retry limits

## Limitations

- Single Remote Control preset active at a time
- Some operations only work in Editor mode
- API may vary across UE versions
- Network dependency (no offline mode)
- WebSocket connection can be unstable

## Troubleshooting

### Connection Failed

**Problem**: `ConnectionError: Failed to connect to Unreal Engine`

**Solutions**:
1. Verify UE is running
2. Check Remote Control plugins are enabled
3. Verify launch flags are set
4. Check port 30010 is not blocked
5. Try browser test: `http://localhost:30010/remote/control/api`

### Command Not Working

**Problem**: Console command returns no output

**Solutions**:
1. Verify command is valid in UE console
2. Check command whitelist in config
3. Try simpler command like "stat fps"
4. Check UE console for errors

### Property Not Found

**Problem**: `Failed to get property`

**Solutions**:
1. Verify object path is correct (copy from UE)
2. Check property is exposed via Remote Control
3. Verify object exists in current level
4. Check property name spelling

### WebSocket Disconnect

**Problem**: WebSocket keeps disconnecting

**Solutions**:
1. Increase ping interval
2. Check network stability
3. Verify UE WebSocket support is enabled
4. Review UE logs for WebSocket errors
5. Try disabling firewall temporarily

## Contributing

When adding new features:
1. Add tests in `tests/remote_control/`
2. Update this README
3. Add examples in `examples/`
4. Update type hints
5. Document exceptions

## Version History

### v0.1.0 (Current)
- Initial implementation
- HTTP client with full CRUD operations
- WebSocket event streaming
- Base agent class
- Comprehensive test suite (67 tests)
- Example implementations

## License

See project LICENSE file.

## Credits

Built for the Adastrea Director project.
Based on Unreal Engine Remote Control API documentation.
