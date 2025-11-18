# Phase 3 Integration Testing

This directory contains comprehensive integration tests for Phase 3 autonomous agents, event bus, and shared state management systems.

## Overview

The integration tests validate how multiple Phase 3 components work together, including:
- **Agent Coordination**: Multiple agents working together through event bus and shared state
- **Event Bus**: Concurrent event publishing, filtering, and delivery
- **Shared State**: Concurrent state access and consistency
- **Performance**: Throughput, latency, and scalability benchmarks
- **Error Handling**: Failure isolation, recovery, and consistency under errors

## Test Files

### test_agent_coordination.py
Tests coordination between multiple agents:
- **Multi-Agent Lifecycle**: Starting, stopping multiple agents
- **Event Coordination**: Agents publishing and reacting to events
- **State Coordination**: Agents sharing data through shared state
- **Error Coordination**: Failure isolation between agents

**Key Test Classes:**
- `TestMultiAgentLifecycle`: Agent lifecycle management
- `TestEventCoordination`: Event-based coordination
- `TestStateCoordination`: State-based coordination
- `TestErrorCoordination`: Error handling in multi-agent scenarios

### test_event_bus_integration.py
Tests event bus under multi-agent scenarios:
- **Concurrency**: Multiple threads publishing events
- **Filtering**: Event filtering by type and source
- **Scalability**: Performance with many subscribers
- **Reliability**: Error handling and isolation

**Key Test Classes:**
- `TestEventBusConcurrency`: Concurrent operations
- `TestEventFiltering`: Event filtering capabilities
- `TestEventBusScalability`: Scalability testing
- `TestEventBusReliability`: Error handling

### test_shared_state_integration.py
Tests shared state management with concurrent access:
- **Consistency**: State consistency under concurrent updates
- **Project Info**: Sharing project information
- **Change Tracking**: Recording code changes
- **Conversation History**: Logging agent conversations

**Key Test Classes:**
- `TestSharedStateConsistency`: Concurrent access consistency
- `TestProjectInfoManagement`: Project info sharing
- `TestChangeTracking`: Change recording
- `TestConversationHistory`: Conversation logging

### test_performance_benchmarks.py
Performance benchmarks for all Phase 3 components:
- **Event Bus**: Throughput, latency, scalability
- **Shared State**: Read/write performance
- **Integration**: Multi-agent coordination overhead
- **Memory**: Memory usage characteristics

**Key Test Classes:**
- `TestEventBusPerformance`: Event bus benchmarks
- `TestSharedStatePerformance`: Shared state benchmarks
- `TestIntegrationPerformance`: Integrated performance
- `TestMemoryUsage`: Memory usage tests

**Note**: These tests are marked as `@pytest.mark.slow` and take longer to run.

### test_error_scenarios.py
Error handling and recovery scenarios:
- **Agent Failures**: Start failures, runtime errors
- **Event Bus Errors**: Subscriber exceptions
- **State Corruption**: Handling corrupted state
- **Recovery**: System recovery mechanisms

**Key Test Classes:**
- `TestAgentFailureRecovery`: Agent failure handling
- `TestEventBusErrorHandling`: Event bus errors
- `TestSharedStateErrorHandling`: State error handling
- `TestDataConsistency`: Data consistency under errors
- `TestRecoveryMechanisms`: Recovery testing

## Running Tests

### Run All Integration Tests
```bash
# From project root
pytest tests/integration/phase3/ -v
```

### Run Specific Test File
```bash
pytest tests/integration/phase3/test_agent_coordination.py -v
```

### Run Specific Test Class
```bash
pytest tests/integration/phase3/test_agent_coordination.py::TestMultiAgentLifecycle -v
```

### Run Specific Test
```bash
pytest tests/integration/phase3/test_agent_coordination.py::TestMultiAgentLifecycle::test_multiple_agents_start_stop -v
```

### Run Performance Benchmarks
```bash
# Performance tests are marked as slow
pytest tests/integration/phase3/test_performance_benchmarks.py -v -m slow
```

### Skip Slow Tests
```bash
# Skip performance benchmarks for quick testing
pytest tests/integration/phase3/ -v -m "not slow"
```

### Run with Coverage
```bash
pytest tests/integration/phase3/ -v --cov=agents.phase3 --cov-report=html
```

### Parallel Execution
```bash
# Install pytest-xdist first: pip install pytest-xdist
pytest tests/integration/phase3/ -v -n auto
```

## Performance Baselines

### Event Bus
- **Throughput**: >500 events/second (target: >1000)
- **Latency**: <10ms mean delivery time with 50 subscribers
- **Scalability**: Linear scaling up to 50 agents

### Shared State
- **Read Performance**: <1ms for 100 key reads
- **Write Performance**: <5ms for 100 key writes
- **Consistency**: No race conditions under concurrent access

### Multi-Agent Coordination
- **Coordination Overhead**: <100ms for 10 agents, 50 events each
- **Throughput**: >100 coordinated operations/second

## Test Coverage Goals

- **Line Coverage**: >90% for all Phase 3 components
- **Branch Coverage**: >85% for critical paths
- **Integration Coverage**: All component interactions tested

## Continuous Integration

These tests are run as part of the CI pipeline:
1. Unit tests (tests/phase3/)
2. Integration tests (tests/integration/phase3/)
3. Performance benchmarks (nightly builds only)

## Debugging Failed Tests

### Common Issues

1. **Timing Issues**: Some tests use `time.sleep()` for coordination
   - Increase sleep times if tests are flaky on slow systems
   - Consider using proper synchronization primitives

2. **Resource Cleanup**: Tests should clean up resources
   - Agents should be stopped after tests
   - Use pytest fixtures for automatic cleanup

3. **Concurrency Issues**: Threading tests can be non-deterministic
   - Use locks for shared counters
   - Verify thread completion with `.join()`

### Debug Mode
```bash
# Run with detailed output
pytest tests/integration/phase3/ -v -s

# Run with pdb on failure
pytest tests/integration/phase3/ --pdb

# Run with logging
pytest tests/integration/phase3/ -v --log-cli-level=DEBUG
```

## Adding New Tests

When adding new integration tests:

1. **Follow Naming Convention**: `test_*.py` for files, `Test*` for classes, `test_*` for methods

2. **Use Fixtures**: Create reusable fixtures for common setup
   ```python
   @pytest.fixture
   def event_bus():
       return EventBus()
   ```

3. **Clean Up Resources**: Always clean up in teardown or use context managers
   ```python
   def test_example(event_bus, shared_context):
       agent = SimpleAgent("test", event_bus, shared_context)
       agent.start()
       try:
           # Test code
           pass
       finally:
           agent.stop()
   ```

4. **Mark Slow Tests**: Use `@pytest.mark.slow` for benchmarks
   ```python
   @pytest.mark.slow
   def test_performance_benchmark():
       # Benchmark code
       pass
   ```

5. **Document Expected Behavior**: Add docstrings explaining what's being tested
   ```python
   def test_agent_coordination(self):
       """Test that agents can coordinate through events."""
       # Test implementation
   ```

## Test Maintenance

### Regular Updates
- Review test performance baselines quarterly
- Update tests when new Phase 3 features are added
- Keep documentation in sync with test changes

### Performance Monitoring
- Track benchmark results over time
- Alert on significant performance regressions
- Update baselines after architecture changes

### Code Reviews
- All new integration tests require code review
- Verify tests are deterministic and maintainable
- Check resource cleanup and error handling

## Related Documentation

- [Phase 3 Guide](../../../PHASE3_GUIDE.md)
- [Agent Architecture](../../../AGENTS.md)
- [Testing Strategy](../../../docs/testing/TESTING_STRATEGY.md)

## Contact

For questions about integration tests:
- Review existing tests for examples
- Check CI logs for failure details
- Consult Phase 3 implementation documentation

---

**Last Updated**: November 18, 2025
