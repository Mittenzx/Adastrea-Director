# Plugin Testing Integration

## Overview

This document describes the integration between the Adastrea Director Plugin and automated testing capabilities via the Remote Control API.

## Architecture

The plugin testing system enables copilot agents to connect to Unreal Engine and perform automated tests through a standardized interface.

```
┌─────────────────────────────────────────┐
│   Copilot Agent (Python)                │
│   ┌─────────────────────────────────┐   │
│   │  TestAgent                       │   │
│   │  - Define test cases              │   │
│   │  - Execute tests                  │   │
│   │  - Collect results                │   │
│   └──────────────┬──────────────────┘   │
└────────────────────┼──────────────────────┘
                     │
                     │ Remote Control API
                     │ (HTTP/REST + WebSocket)
                     │ Port 30010
                     ▼
┌─────────────────────────────────────────┐
│   Unreal Engine + Plugin                │
│   ┌─────────────────────────────────┐   │
│   │  Remote Control API              │   │
│   │  - Property operations            │   │
│   │  - Function calls                 │   │
│   │  - Console commands               │   │
│   └─────────────────────────────────┘   │
│   ┌─────────────────────────────────┐   │
│   │  Adastrea Director Plugin        │   │
│   │  - IPC Server                     │   │
│   │  - Python Bridge                  │   │
│   │  - Test Execution Support         │   │
│   └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Components

### 1. TestAgent (Python)

**Location**: `remote_control/test_agent.py`

The TestAgent is a specialized RemoteControlAgent that provides automated testing capabilities:

- **Property Testing**: Validate object properties and their values
- **Function Testing**: Execute Blueprint/C++ functions and verify results
- **Command Testing**: Run console commands and check outputs
- **Test Suites**: Execute multiple tests in sequence
- **Result Reporting**: Detailed pass/fail/error status with timing
- **Export**: Save test results to JSON format

**Key Features**:
- Context manager support for automatic connection management
- Type-safe test definitions
- Comprehensive error handling
- Performance metrics for each test

### 2. Remote Control API

**Location**: UE Plugin Remote Control System

The Remote Control API provides the communication layer:

- **HTTP/REST**: Synchronous property/function/command operations
- **WebSocket**: Real-time event streaming (optional)
- **Port**: Default 30010
- **Protocol**: JSON-based request/response

**Supported Operations**:
- `get_property(object_path, property_name)`: Read property value
- `set_property(object_path, property_name, value)`: Write property value
- `call_function(object_path, function_name, params)`: Execute function
- `execute_command(command)`: Run console command

### 3. UE Plugin Integration

**Location**: `Plugins/AdastreaDirector/`

The Adastrea Director plugin provides:

- **IPC Server**: Python backend communication
- **Python Bridge**: C++/Python interop layer
- **Test Support**: Infrastructure for test execution

## Setup

### 1. Unreal Engine Configuration

Enable Remote Control in your project:

1. **Enable Plugins** (Edit → Plugins):
   - Remote Control API
   - Remote Control Web Interface
   - Adastrea Director

2. **Launch with Remote Control**:
   ```bash
   # Windows
   UnrealEditor.exe MyProject.uproject -RCWebControlEnable -RCWebInterfaceEnable
   
   # Mac
   UnrealEditor MyProject.uproject -RCWebControlEnable -RCWebInterfaceEnable
   
   # Linux
   ./UnrealEditor MyProject.uproject -RCWebControlEnable -RCWebInterfaceEnable
   ```

3. **Verify Connection**:
   - Open browser to `http://localhost:30010/remote/control/api`
   - Should see API documentation page

### 2. Python Environment

Install required packages:

```bash
cd Adastrea-Director
pip install -r requirements.txt

# Or install just the testing dependencies:
pip install requests websocket-client
```

### 3. Test Agent Setup

No additional configuration needed. The TestAgent automatically connects to localhost:30010 by default.

## Usage

### Basic Test Execution

```python
from remote_control import TestAgent

# Create and start agent
with TestAgent(agent_id="automated_tester") as agent:
    # Define a test
    test = {
        "name": "test_fps_command",
        "type": "command",
        "command": "stat fps"
    }
    
    # Execute test
    result = agent.execute_task(test)
    
    # Check result
    if result.status == TestStatus.PASSED:
        print(f"✓ Test passed: {result.message}")
    else:
        print(f"✗ Test failed: {result.message}")
```

### Test Suite Execution

```python
from remote_control import TestAgent

# Define test suite
test_suite = [
    # Test 1: Console command
    {
        "name": "test_fps",
        "type": "command",
        "command": "stat fps"
    },
    
    # Test 2: Property validation
    {
        "name": "test_character_speed",
        "type": "property",
        "object_path": "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter",
        "property_name": "MaxWalkSpeed",
        "expected_value": 600.0
    },
    
    # Test 3: Function call
    {
        "name": "test_get_health",
        "type": "function",
        "object_path": "/Game/MyActor.MyActor_C",
        "function_name": "GetHealth",
        "parameters": {}
    }
]

# Execute suite
with TestAgent() as agent:
    results = agent.run_test_suite(test_suite)
    
    # Print summary
    agent.print_test_summary(results)
    
    # Export results
    agent.export_test_results("/tmp/test_results.json")
```

### CI/CD Integration

```python
#!/usr/bin/env python3
"""CI/CD test runner for Unreal Engine project."""

import sys
from remote_control import TestAgent, TestStatus

def run_ci_tests():
    """Run automated tests and exit with appropriate code."""
    
    # Define test suite
    tests = [
        # Add your tests here
    ]
    
    # Execute tests
    with TestAgent(agent_id="ci_tester") as agent:
        results = agent.run_test_suite(tests)
        
        # Export for CI system
        agent.export_test_results("test_results.json")
        
        # Print summary
        agent.print_test_summary(results)
        
        # Check for failures
        failed = sum(
            1 for r in results 
            if r.status in [TestStatus.FAILED, TestStatus.ERROR]
        )
        
        # Exit with appropriate code
        sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    run_ci_tests()
```

## Test Types

### Property Tests

Validate object properties:

```python
{
    "name": "test_player_health",
    "type": "property",
    "object_path": "/Game/Player.Player_C",
    "property_name": "Health",
    "expected_value": 100.0  # Optional
}
```

**Use Cases**:
- Validate initial game state
- Check configuration values
- Verify runtime property changes

### Function Tests

Execute and validate functions:

```python
{
    "name": "test_damage_calculation",
    "type": "function",
    "object_path": "/Game/Combat/DamageCalculator",
    "function_name": "CalculateDamage",
    "parameters": {"BaseDamage": 10.0, "Armor": 5.0},
    "expected_result": {"Damage": 5.0}  # Optional
}
```

**Use Cases**:
- Test game logic functions
- Validate calculation correctness
- Verify Blueprint/C++ interop

### Command Tests

Execute console commands:

```python
{
    "name": "test_performance",
    "type": "command",
    "command": "stat fps",
    "expected_output": "FPS"  # Optional
}
```

**Use Cases**:
- Monitor performance metrics
- Trigger debug commands
- Validate console functionality

## Best Practices

### 1. Test Organization

Organize tests by feature or system:

```python
gameplay_tests = [...]
performance_tests = [...]
ui_tests = [...]

with TestAgent() as agent:
    print("Running gameplay tests...")
    agent.run_test_suite(gameplay_tests)
    
    print("Running performance tests...")
    agent.run_test_suite(performance_tests)
```

### 2. Object Path Verification

Always verify object paths in UE Editor:

1. Right-click object in Content Browser
2. Select "Copy Reference"
3. Use exact path in test definition

### 3. Error Handling

Handle connection failures gracefully:

```python
from remote_control import TestAgent, RemoteControlError

agent = TestAgent()

try:
    agent.start()
    # Run tests...
except RemoteControlError as e:
    print(f"Connection failed: {e}")
    print("Ensure UE is running with Remote Control enabled")
    sys.exit(1)
finally:
    agent.stop()
```

### 4. Result Validation

Check test results programmatically:

```python
results = agent.run_test_suite(tests)

# Count failures
failures = [r for r in results if r.status == TestStatus.FAILED]
errors = [r for r in results if r.status == TestStatus.ERROR]

if failures or errors:
    print(f"⚠ {len(failures)} failures, {len(errors)} errors")
    for result in failures + errors:
        print(f"  - {result}")
```

## Examples

See complete working examples in:
- `examples/test_agent_example.py` - Comprehensive examples
- `remote_control/TEST_AGENT_GUIDE.md` - Full documentation

## Troubleshooting

### Connection Failed

**Problem**: Cannot connect to Unreal Engine

**Solutions**:
1. Verify UE is running
2. Check Remote Control plugins are enabled
3. Verify launch flags include `-RCWebControlEnable -RCWebInterfaceEnable`
4. Test in browser: `http://localhost:30010/remote/control/api`
5. Check firewall settings

### Property Not Found

**Problem**: Test reports property not found

**Solutions**:
1. Verify object path (use Copy Reference)
2. Check property name spelling
3. Ensure property is exposed in Remote Control
4. Verify object exists in current level

### Function Call Failed

**Problem**: Function call test fails

**Solutions**:
1. Verify function name is correct
2. Check function is exposed via Remote Control
3. Validate parameter types
4. Ensure function exists on the specified object

### Tests Timeout

**Problem**: Tests hang or timeout

**Solutions**:
1. Increase timeout: `TestAgent(timeout=60)`
2. Check UE console for errors
3. Verify command/function doesn't block
4. Test simpler operations first

## API Documentation

### TestAgent API

See `remote_control/TEST_AGENT_GUIDE.md` for complete API reference.

**Key Methods**:
- `start()`: Connect to UE
- `stop()`: Disconnect from UE
- `execute_task(task)`: Run single test
- `run_test_suite(tests)`: Run multiple tests
- `print_test_summary()`: Display results
- `export_test_results(path)`: Save to JSON

### Test Definition Format

```python
{
    "name": str,              # Test identifier
    "type": str,              # "property", "function", or "command"
    
    # For property tests:
    "object_path": str,       # UE object path
    "property_name": str,     # Property name
    "expected_value": Any,    # Optional: expected value
    
    # For function tests:
    "object_path": str,       # UE object path
    "function_name": str,     # Function name
    "parameters": dict,       # Function parameters
    "expected_result": Any,   # Optional: expected return value
    
    # For command tests:
    "command": str,           # Console command
    "expected_output": str,   # Optional: expected substring in output
}
```

## Integration with Existing Systems

### IPC Server Integration

The TestAgent uses the Remote Control API, which runs independently of the IPC server. Both can operate simultaneously:

- **IPC Server**: Python backend for AI/RAG features (port 5555)
- **Remote Control API**: Testing interface (port 30010)

No conflicts or coordination needed.

### Plugin UI Integration

The TestAgent is independent of the plugin UI:

- **Plugin UI**: In-editor panel for queries and ingestion
- **TestAgent**: External Python script for automated testing

Can be used independently or together.

## Future Enhancements

Potential improvements:

1. **Test Recording**: Record manual tests for replay
2. **Visual Regression Testing**: Screenshot comparison
3. **Performance Profiling**: Detailed timing analysis
4. **Parallel Execution**: Run tests concurrently
5. **Test Generation**: AI-generated test cases
6. **Blueprint Testing**: Specialized Blueprint node testing

## Support

- **Documentation**: [TEST_AGENT_GUIDE.md](remote_control/TEST_AGENT_GUIDE.md)
- **Examples**: [test_agent_example.py](examples/test_agent_example.py)
- **Issues**: [GitHub Issues](https://github.com/Mittenzx/Adastrea-Director/issues)
- **Remote Control API**: [README.md](remote_control/README.md)

## License

See project LICENSE file.
