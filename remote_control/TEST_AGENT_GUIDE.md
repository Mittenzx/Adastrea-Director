# Test Agent Guide

## Overview

The **TestAgent** is a specialized agent that enables automated testing of Unreal Engine projects through the Remote Control API. It allows copilot agents to connect to the UE plugin and perform comprehensive automated tests.

## Features

- **Property Testing**: Validate object properties and their values
- **Function Testing**: Execute and verify Blueprint/C++ function calls
- **Command Testing**: Run console commands and check outputs
- **Test Suites**: Organize and run multiple tests in sequence
- **Result Reporting**: Detailed test results with pass/fail/error status
- **Export Results**: Save test results to JSON format
- **Error Handling**: Robust error detection and reporting

## Architecture

```
┌─────────────────────────────────────┐
│   Python Test Agent                 │
│   - Define test cases                │
│   - Execute tests                    │
│   - Collect results                  │
└──────────────┬──────────────────────┘
               │ Remote Control API
               ▼
┌─────────────────────────────────────┐
│   Unreal Engine                     │
│   - Remote Control API enabled      │
│   - Plugin connected                 │
│   - Game/Editor running              │
└─────────────────────────────────────┘
```

## Requirements

### Unreal Engine Setup

1. **Enable Remote Control Plugins**:
   - Remote Control API
   - Remote Control Web Interface

2. **Launch with Remote Control Enabled**:
   ```bash
   UnrealEditor.exe MyProject.uproject -RCWebControlEnable -RCWebInterfaceEnable
   ```

3. **Verify Connection**:
   - Open browser to `http://localhost:30010/remote/info`
   - Should see API route information

### Python Dependencies

```bash
pip install requests websocket-client
```

## Quick Start

### Basic Usage

```python
from remote_control import TestAgent, TestStatus

# Create test agent
agent = TestAgent(
    agent_id="my_test_agent",
    ue_host="localhost",
    ue_port=30010
)

# Connect to Unreal Engine
agent.start()

# Run a simple test
result = agent.execute_task({
    "name": "test_fps_command",
    "type": "command",
    "command": "stat fps"
})

print(f"Test result: {result.status.value}")

# Cleanup
agent.stop()
```

### Using Context Manager

```python
from remote_control import TestAgent

# Context manager automatically handles start/stop
with TestAgent(agent_id="test_agent") as agent:
    result = agent.execute_task({
        "name": "test_health",
        "type": "property",
        "object_path": "/Game/Player.Player_C",
        "property_name": "Health",
        "expected_value": 100.0
    })
    print(result)
```

## Test Types

### 1. Property Tests

Test object properties and validate their values.

```python
property_test = {
    "name": "test_player_health",
    "type": "property",
    "object_path": "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter",
    "property_name": "Health",
    "expected_value": 100.0  # Optional: validate specific value
}

result = agent.execute_task(property_test)
```

**Fields**:
- `name`: Test identifier
- `type`: Must be `"property"`
- `object_path`: Full path to UE object
- `property_name`: Name of property to test
- `expected_value`: (Optional) Expected property value

**Result Status**:
- `PASSED`: Property exists and matches expected value (if provided)
- `FAILED`: Property value doesn't match expected
- `ERROR`: Property not found or access error

### 2. Function Tests

Execute Blueprint or C++ functions and validate results.

```python
function_test = {
    "name": "test_take_damage",
    "type": "function",
    "object_path": "/Game/Player.Player_C",
    "function_name": "TakeDamage",
    "parameters": {"Amount": 10.0},
    "expected_result": {"success": True}  # Optional: validate return value
}

result = agent.execute_task(function_test)
```

**Fields**:
- `name`: Test identifier
- `type`: Must be `"function"`
- `object_path`: Full path to UE object
- `function_name`: Name of function to call
- `parameters`: Dictionary of function parameters
- `expected_result`: (Optional) Expected return value

**Result Status**:
- `PASSED`: Function executed and result matches (if expected result provided)
- `FAILED`: Function result doesn't match expected
- `ERROR`: Function not found or execution error

### 3. Command Tests

Execute console commands and check outputs.

```python
command_test = {
    "name": "test_fps_display",
    "type": "command",
    "command": "stat fps",
    "expected_output": "FPS"  # Optional: check for substring in output
}

result = agent.execute_task(command_test)
```

**Fields**:
- `name`: Test identifier
- `type`: Must be `"command"`
- `command`: Console command to execute
- `expected_output`: (Optional) Expected substring in output

**Result Status**:
- `PASSED`: Command executed and output contains expected string (if provided)
- `FAILED`: Expected output not found
- `ERROR`: Command execution error

## Test Suites

Run multiple tests in sequence:

```python
from remote_control import TestAgent

# Define test suite
tests = [
    {
        "name": "test_fps",
        "type": "command",
        "command": "stat fps"
    },
    {
        "name": "test_player_speed",
        "type": "property",
        "object_path": "/Game/Player.Player_C",
        "property_name": "MaxWalkSpeed",
        "expected_value": 600.0
    },
    {
        "name": "test_health_function",
        "type": "function",
        "object_path": "/Game/Player.Player_C",
        "function_name": "GetHealth"
    }
]

# Run test suite
with TestAgent() as agent:
    results = agent.run_test_suite(tests)
    
    # Print summary
    agent.print_test_summary(results)
    
    # Export results
    agent.export_test_results("/tmp/test_results.json")
```

## Test Results

### TestResult Object

Each test returns a `TestResult` object with:

```python
result.test_name      # Test identifier
result.status         # TestStatus enum (PASSED/FAILED/ERROR/etc.)
result.duration       # Execution time in seconds
result.message        # Status message or error details
result.timestamp      # When test was executed
result.details        # Additional test-specific details
```

### Test Status Values

- `PENDING`: Test queued but not started
- `RUNNING`: Test currently executing
- `PASSED`: Test completed successfully
- `FAILED`: Test completed but assertion failed
- `ERROR`: Test encountered an error
- `SKIPPED`: Test was skipped

### Printing Results

```python
# Print individual result
print(result)  # ✓ test_name (1.50s): Test passed

# Print test suite summary
agent.print_test_summary()
# Outputs:
# ======================================================================
# TEST SUMMARY
# ======================================================================
# ✓ test_fps (0.15s): Command executed successfully
# ✓ test_player_speed (0.23s): Property value matches expected: 600.0
# ✗ test_health (0.10s): Expected 100, got 75
# ----------------------------------------------------------------------
# Total Tests:  3
# Passed:       2
# Failed:       1
# Errors:       0
# Skipped:      0
# Duration:     0.48s
# ======================================================================
```

## Exporting Results

### JSON Export

```python
agent.export_test_results("/path/to/results.json")
```

Output format:

```json
{
  "agent_id": "test_agent",
  "timestamp": "2025-11-22T18:30:00.123456",
  "total_tests": 3,
  "results": [
    {
      "test_name": "test_fps",
      "status": "passed",
      "duration": 0.15,
      "message": "Command executed successfully",
      "timestamp": "2025-11-22T18:30:00.123456",
      "details": {
        "command": "stat fps",
        "output": {"result": "FPS: 60"}
      }
    }
  ]
}
```

## Advanced Usage

### Custom Test Agent

Extend `TestAgent` for specialized testing:

```python
from remote_control import TestAgent, TestStatus, TestResult

class PerformanceTestAgent(TestAgent):
    """Specialized agent for performance testing."""
    
    def test_frame_rate(self, min_fps=30):
        """Test that frame rate meets minimum threshold."""
        result = self.execute_command("stat fps")
        
        # Parse FPS from output
        fps = self._parse_fps(result)
        
        if fps >= min_fps:
            return TestResult(
                test_name="frame_rate_test",
                status=TestStatus.PASSED,
                message=f"FPS {fps} meets minimum {min_fps}"
            )
        else:
            return TestResult(
                test_name="frame_rate_test",
                status=TestStatus.FAILED,
                message=f"FPS {fps} below minimum {min_fps}"
            )
    
    def _parse_fps(self, output):
        """Extract FPS value from command output."""
        # Implementation depends on output format
        pass

# Use custom agent
with PerformanceTestAgent() as agent:
    result = agent.test_frame_rate(min_fps=60)
    print(result)
```

### Continuous Testing

Run tests periodically:

```python
import time
from remote_control import TestAgent

def continuous_test_loop(agent, tests, interval=60):
    """Run tests every 'interval' seconds."""
    iteration = 0
    
    while True:
        iteration += 1
        print(f"\n=== Test Iteration {iteration} ===")
        
        results = agent.run_test_suite(tests)
        agent.print_test_summary(results)
        
        # Check for failures
        failures = [r for r in results if r.status == TestStatus.FAILED]
        if failures:
            print(f"⚠ {len(failures)} test(s) failed!")
            # Could send alert here
        
        time.sleep(interval)

# Run continuous tests
with TestAgent() as agent:
    continuous_test_loop(agent, my_tests, interval=300)  # Every 5 minutes
```

### Integration with CI/CD

```python
import sys
from remote_control import TestAgent, TestStatus

def run_ci_tests(test_suite):
    """Run tests and exit with appropriate code for CI."""
    with TestAgent() as agent:
        results = agent.run_test_suite(test_suite)
        
        # Export results
        agent.export_test_results("test_results.json")
        
        # Print summary
        agent.print_test_summary(results)
        
        # Check for failures
        failed = sum(1 for r in results if r.status in [TestStatus.FAILED, TestStatus.ERROR])
        
        if failed > 0:
            print(f"\n✗ {failed} test(s) failed")
            sys.exit(1)
        else:
            print("\n✓ All tests passed")
            sys.exit(0)

if __name__ == "__main__":
    run_ci_tests(my_test_suite)
```

## Best Practices

### 1. Use Descriptive Test Names

```python
# Good
{"name": "test_player_health_after_damage", ...}

# Bad
{"name": "test1", ...}
```

### 2. Verify Object Paths

Always verify object paths are correct before running tests:

```python
# In UE Editor:
# 1. Right-click object in Content Browser
# 2. Copy Reference
# 3. Use the path in your test
```

### 3. Handle Connection Failures

```python
from remote_control import TestAgent, RemoteControlError

agent = TestAgent()

try:
    agent.start()
    # Run tests...
except RemoteControlError as e:
    print(f"Failed to connect: {e}")
    print("Is Unreal Engine running with Remote Control enabled?")
```

### 4. Clean Up Resources

Always stop the agent or use context manager:

```python
# Option 1: Manual cleanup
agent = TestAgent()
try:
    agent.start()
    # Tests...
finally:
    agent.stop()

# Option 2: Context manager (recommended)
with TestAgent() as agent:
    # Tests...
```

### 5. Organize Tests

Group related tests together:

```python
gameplay_tests = [...]
performance_tests = [...]
ui_tests = [...]

# Run by category
with TestAgent() as agent:
    print("Running gameplay tests...")
    agent.run_test_suite(gameplay_tests)
    
    print("Running performance tests...")
    agent.run_test_suite(performance_tests)
```

## Troubleshooting

### Connection Failed

**Problem**: `RemoteControlError: Failed to connect to Unreal Engine`

**Solutions**:
1. Verify UE is running
2. Check Remote Control plugins are enabled
3. Verify launch flags: `-RCWebControlEnable -RCWebInterfaceEnable`
4. Test in browser: `http://localhost:30010/remote/info`
5. Check firewall settings

### Property Not Found

**Problem**: `ERROR: Error getting property: Property not found`

**Solutions**:
1. Verify object path is correct (use Copy Reference in UE)
2. Check property name spelling
3. Ensure property is exposed in Remote Control
4. Verify object exists in current level
5. Check property access modifiers

### Function Call Failed

**Problem**: `ERROR: Error calling function: Function not found`

**Solutions**:
1. Verify function name is correct
2. Check function is exposed via Remote Control
3. Ensure function is callable (not pure/const in some contexts)
4. Verify parameter types match
5. Check function exists on the specified object

### Test Timeout

**Problem**: Test takes too long or hangs

**Solutions**:
1. Increase timeout: `TestAgent(timeout=60)`
2. Check if UE is responding
3. Verify command/function doesn't block
4. Check UE console for errors

## Examples

See `examples/test_agent_example.py` for complete working examples.

## API Reference

### TestAgent Class

```python
TestAgent(
    agent_id: str = "test_agent",
    ue_host: str = "localhost",
    ue_port: int = 30010,
    enable_websocket: bool = False,
    timeout: int = 30
)
```

**Methods**:
- `start()`: Connect to Unreal Engine
- `stop()`: Disconnect from Unreal Engine
- `execute_task(task)`: Run a single test
- `run_test_suite(tests)`: Run multiple tests
- `get_test_results()`: Get all test results
- `clear_test_results()`: Clear result history
- `print_test_summary(results=None)`: Print test summary
- `export_test_results(filepath, format="json")`: Export results

### TestResult Class

```python
TestResult(
    test_name: str,
    status: TestStatus,
    duration: float = 0.0,
    message: str = "",
    details: Optional[Dict] = None
)
```

**Methods**:
- `to_dict()`: Convert to dictionary
- `__str__()`: Get formatted string representation

### TestStatus Enum

- `PENDING`: Test not yet started
- `RUNNING`: Test in progress
- `PASSED`: Test succeeded
- `FAILED`: Test assertion failed
- `ERROR`: Test encountered error
- `SKIPPED`: Test was skipped

## Contributing

When extending TestAgent functionality:

1. Add tests in `tests/remote_control/test_test_agent.py`
2. Update this documentation
3. Add examples in `examples/test_agent_example.py`
4. Update type hints
5. Document exceptions

## Support

- **Issues**: [GitHub Issues](https://github.com/Mittenzx/Adastrea-Director/issues)
- **Documentation**: [Remote Control API Guide](../remote_control/README.md)
- **Examples**: `examples/test_agent_example.py`

## License

See project LICENSE file.
