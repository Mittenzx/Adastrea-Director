# Phase 3 Integration Testing Guide

**Last Updated:** November 20, 2025  
**Test Suite Version:** 1.0  
**Status:** Production-Ready

---

## Overview

This guide documents the comprehensive integration testing strategy for Phase 3 autonomous agents. Integration tests verify that agents work correctly together through the Event Bus and Shared State systems.

### Test Coverage

| Component | Tests | Status | Coverage |
|-----------|-------|--------|----------|
| Agent Coordination | 446 lines | ✅ Complete | Multi-agent lifecycle |
| Event Bus Integration | 408 lines | ✅ Complete | Concurrency, filtering |
| Shared State Integration | 476 lines | ✅ Complete | State consistency |
| Performance Benchmarks | 524 lines | ✅ Complete | Load testing |
| Error Scenarios | 527 lines | ✅ Complete | Error handling |
| **Total** | **2,381 lines** | ✅ Complete | Comprehensive |

---

## Test Structure

### Location

All integration tests are located in:
```
tests/integration/phase3/
├── __init__.py
├── test_agent_coordination.py       # Multi-agent coordination
├── test_event_bus_integration.py    # Event bus scalability
├── test_shared_state_integration.py # State management
├── test_performance_benchmarks.py   # Performance testing
└── test_error_scenarios.py          # Error handling
```

### Test Categories

#### 1. Agent Coordination Tests
**File:** `test_agent_coordination.py`

Tests how multiple agents work together through the event bus and shared state.

**Test Cases:**
- Agent lifecycle management (start/stop/restart)
- Multi-agent event communication
- Reactive agent behaviors
- Cross-agent task coordination
- Agent status synchronization
- Event chain reactions
- Agent isolation and cleanup

**Key Tests:**
```python
def test_multiple_agents_lifecycle()
def test_agents_communicate_via_events()
def test_reactive_agent_responds_to_events()
def test_agents_share_context_via_state()
def test_agent_error_doesnt_affect_others()
```

#### 2. Event Bus Integration Tests
**File:** `test_event_bus_integration.py`

Tests event bus behavior under load, with concurrency, and with filtering.

**Test Cases:**
- High-volume event publishing (1000+ events)
- Concurrent event handling
- Event filtering by type and source
- Multiple subscribers per event type
- Event history management
- Handler error isolation
- Memory management with large event history

**Key Tests:**
```python
def test_high_volume_events()
def test_concurrent_event_publishing()
def test_event_filtering()
def test_multiple_subscribers_per_event()
def test_event_history_limit()
```

#### 3. Shared State Integration Tests
**File:** `test_shared_state_integration.py`

Tests shared state consistency and concurrent access patterns.

**Test Cases:**
- Multi-agent state registration
- Concurrent state updates
- State consistency verification
- Project information sharing
- Change history tracking
- Agent metrics aggregation
- State cleanup on agent stop

**Key Tests:**
```python
def test_multiple_agents_register_state()
def test_concurrent_state_updates()
def test_state_consistency_across_agents()
def test_shared_project_info()
def test_change_history_tracking()
```

#### 4. Performance Benchmarks
**File:** `test_performance_benchmarks.py`

Tests system performance under various load conditions.

**Test Cases:**
- Event bus throughput (events/second)
- Agent response time (<1s target)
- State update latency
- Memory usage under load
- CPU usage monitoring
- Concurrent agent scalability
- Event history performance

**Key Tests:**
```python
def test_event_bus_throughput()
def test_agent_response_time()
def test_memory_usage_under_load()
def test_concurrent_agent_performance()
```

#### 5. Error Scenario Tests
**File:** `test_error_scenarios.py`

Tests error handling and recovery mechanisms.

**Test Cases:**
- Handler exceptions don't crash event bus
- Agent errors trigger AGENT_ERROR events
- Invalid event types handled gracefully
- State corruption recovery
- Network failure simulation
- Resource exhaustion handling
- Graceful degradation

**Key Tests:**
```python
def test_handler_exception_isolation()
def test_agent_error_event_publishing()
def test_invalid_event_handling()
def test_state_recovery_on_error()
def test_resource_exhaustion()
```

---

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov

# Ensure you're in project root
cd /path/to/Adastrea-Director
```

### Run All Integration Tests

```bash
# Run all Phase 3 integration tests
pytest tests/integration/phase3/ -v

# With coverage report
pytest tests/integration/phase3/ -v --cov=agents.phase3
```

### Run Specific Test Files

```bash
# Agent coordination tests only
pytest tests/integration/phase3/test_agent_coordination.py -v

# Event bus integration tests
pytest tests/integration/phase3/test_event_bus_integration.py -v

# Performance benchmarks
pytest tests/integration/phase3/test_performance_benchmarks.py -v
```

### Run Specific Test Cases

```bash
# Run single test
pytest tests/integration/phase3/test_agent_coordination.py::test_multiple_agents_lifecycle -v

# Run tests matching pattern
pytest tests/integration/phase3/ -k "concurrent" -v
```

---

## Test Fixtures

### Common Fixtures

All integration tests use these shared fixtures:

```python
@pytest.fixture
def event_bus():
    """Provides a clean event bus for each test."""
    return EventBus()

@pytest.fixture
def shared_context():
    """Provides a clean shared context for each test."""
    return SharedContext()

@pytest.fixture
def test_agent(event_bus, shared_context):
    """Provides a simple test agent."""
    agent = SimpleTestAgent("test_agent", event_bus, shared_context)
    yield agent
    agent.stop()
```

### Custom Test Agents

Integration tests use these lightweight test agents:

**SimpleTestAgent:**
- Basic agent for lifecycle testing
- Records events received
- Simulates work with configurable duration

**ReactiveTestAgent:**
- Responds to other agents' events
- Tests event-driven behavior
- Records reactions for verification

**ProducerAgent:**
- Publishes events on schedule
- Tests high-volume scenarios
- Configurable event rate

---

## Performance Targets

### Response Time Targets

| Operation | Target | Typical | Status |
|-----------|--------|---------|--------|
| Event publish | <1ms | <0.5ms | ✅ Exceeds |
| Event delivery | <10ms | <5ms | ✅ Exceeds |
| State update | <1ms | <0.5ms | ✅ Exceeds |
| Agent start | <100ms | <50ms | ✅ Exceeds |
| Agent stop | <100ms | <50ms | ✅ Exceeds |

### Throughput Targets

| Metric | Target | Typical | Status |
|--------|--------|---------|--------|
| Events/second | >1000 | ~2000 | ✅ Exceeds |
| Agents supported | >10 | Tested 20+ | ✅ Exceeds |
| Concurrent ops | >100 | Tested 200+ | ✅ Exceeds |

### Memory Targets

| Component | Target | Typical | Status |
|-----------|--------|---------|--------|
| Event history | <10MB | ~5MB | ✅ Within |
| Shared state | <50MB | ~10MB | ✅ Within |
| Per agent | <10MB | ~5MB | ✅ Within |

---

## CI/CD Integration

### GitHub Actions Workflow

Add to `.github/workflows/test.yml`:

```yaml
name: Integration Tests

on:
  pull_request:
    branches: [ main, develop ]
  push:
    branches: [ main ]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run integration tests
        run: |
          pytest tests/integration/phase3/ -v --cov=agents.phase3
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Pre-commit Hooks

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: integration-tests
      name: Run integration tests
      entry: pytest tests/integration/phase3/ -v
      language: system
      pass_filenames: false
      stages: [commit]
```

---

## Debugging Failed Tests

### Common Issues

#### 1. Test Timeout

**Symptom:** Tests hang or timeout

**Solutions:**
```python
# Add timeout to test
@pytest.mark.timeout(30)
def test_agent_coordination():
    pass

# Or use pytest-timeout plugin
pytest tests/integration/phase3/ --timeout=30
```

#### 2. Event Bus Not Cleaned Up

**Symptom:** Events from previous tests affect current test

**Solution:**
```python
# Ensure clean state in fixture
@pytest.fixture
def event_bus():
    bus = EventBus()
    yield bus
    bus.clear_history()
```

#### 3. Agents Not Stopped

**Symptom:** Agents from previous tests still running

**Solution:**
```python
# Always stop agents in fixture cleanup
@pytest.fixture
def test_agent(event_bus, shared_context):
    agent = SimpleTestAgent("test", event_bus, shared_context)
    yield agent
    if agent.is_running():
        agent.stop()
```

#### 4. Race Conditions

**Symptom:** Tests pass sometimes, fail sometimes

**Solution:**
```python
# Add explicit waits for async operations
import time

def test_async_operation():
    agent.start()
    time.sleep(0.1)  # Allow startup
    assert agent.is_running()
```

### Debug Mode

Run tests with debug output:

```bash
# Verbose output with logging
pytest tests/integration/phase3/ -v -s --log-cli-level=DEBUG

# Show local variables on failure
pytest tests/integration/phase3/ -vv -l

# Stop on first failure
pytest tests/integration/phase3/ -x
```

---

## Test Maintenance

### Adding New Tests

1. **Choose appropriate file** based on test category
2. **Follow naming convention:** `test_<feature>_<scenario>`
3. **Use existing fixtures** when possible
4. **Add docstrings** explaining what test verifies
5. **Clean up resources** in teardown/fixture cleanup

**Example:**
```python
def test_new_agent_feature(event_bus, shared_context):
    """
    Test that new agent feature works correctly.
    
    Verifies:
    - Feature initializes properly
    - Events are published correctly
    - State updates as expected
    """
    # Arrange
    agent = NewAgent("test", event_bus, shared_context)
    
    # Act
    agent.start()
    result = agent.use_new_feature()
    
    # Assert
    assert result is not None
    assert agent.is_running()
    
    # Cleanup
    agent.stop()
```

### Updating Existing Tests

1. **Maintain backwards compatibility** when possible
2. **Update docstrings** to reflect changes
3. **Run full test suite** before committing
4. **Update this documentation** if test behavior changes

### Test Review Checklist

- [ ] Test has clear purpose documented
- [ ] Uses appropriate fixtures
- [ ] Cleans up resources (agents, subscriptions)
- [ ] Runs in <30 seconds
- [ ] Passes consistently (run 10 times)
- [ ] Has meaningful assertions
- [ ] Error messages are helpful

---

## Best Practices

### Test Organization

1. **One test, one concept** - Test one thing per test function
2. **Arrange-Act-Assert** - Clear test structure
3. **Independent tests** - No test depends on another
4. **Fast tests** - Keep integration tests under 30s each

### Fixture Usage

1. **Reuse common fixtures** - Don't duplicate setup code
2. **Clean up resources** - Always stop agents, clear history
3. **Scope appropriately** - Use `function` scope for isolation

### Assertions

1. **Specific assertions** - Check exact values when possible
2. **Helpful messages** - Add context to assertion messages
3. **Multiple assertions OK** - For related state checks

**Example:**
```python
def test_agent_state_after_start(test_agent):
    test_agent.start()
    
    # Specific assertions with messages
    assert test_agent.is_running(), "Agent should be running after start"
    assert test_agent.state.status == AgentStatus.IDLE, \
        f"Expected IDLE, got {test_agent.state.status}"
    assert len(test_agent.events_received) == 1, \
        "Should have received AGENT_STARTED event"
```

---

## Troubleshooting

### Test Suite Not Found

**Problem:** pytest can't find tests

**Solution:**
```bash
# Ensure pytest can find tests
cd /path/to/Adastrea-Director
python -m pytest tests/integration/phase3/ -v
```

### Import Errors

**Problem:** Cannot import agents.phase3

**Solution:**
```bash
# Add project root to PYTHONPATH
export PYTHONPATH=/path/to/Adastrea-Director:$PYTHONPATH
pytest tests/integration/phase3/ -v
```

### Slow Tests

**Problem:** Tests take too long

**Solution:**
```bash
# Run only fast tests
pytest tests/integration/phase3/ -m "not slow" -v

# Or mark slow tests
@pytest.mark.slow
def test_long_running_operation():
    pass
```

---

## Metrics and Monitoring

### Test Execution Metrics

Track these metrics over time:

- **Pass rate:** Target 100%
- **Execution time:** Target <5 minutes total
- **Flakiness:** Target 0 flaky tests
- **Coverage:** Target >90%

### Monitoring Dashboard

Use pytest-html for HTML reports:

```bash
# Generate HTML report
pytest tests/integration/phase3/ --html=report.html --self-contained-html
```

---

## Resources

### Documentation
- [PHASE3_GUIDE.md](../../PHASE3_GUIDE.md) - Phase 3 user guide
- [PHASE3_STATUS.md](./PHASE3_STATUS.md) - Current status
- [AGENT_ORCHESTRATION.md](./AGENT_ORCHESTRATION.md) - CLI/Dashboard guide

### Code
- `tests/integration/phase3/` - Integration test source
- `agents/phase3/` - Agent implementations
- `examples/` - Usage examples

### External
- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)

---

## Changelog

### November 20, 2025
- ✨ Initial INTEGRATION_TESTING.md created
- 📊 Documented all integration test files
- 📋 Added running instructions
- 🎯 Documented performance targets
- 🔧 Added troubleshooting guide

---

**Status:** ✅ Documentation Complete  
**Next Update:** As tests evolve  
**Maintainer:** Adastrea Director Team
