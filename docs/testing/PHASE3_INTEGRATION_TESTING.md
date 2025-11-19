# Phase 3 Integration Testing Guide

**Last Updated:** November 19, 2025  
**Status:** Active  
**Test Count:** 40+ integration tests

---

## Overview

This document describes the integration testing procedures for Phase 3 autonomous agents, covering multi-agent coordination, event bus operations, shared state management, performance benchmarks, and error handling scenarios.

---

## Test Organization

### Test Location
All Phase 3 integration tests are located in:
```
tests/integration/phase3/
├── __init__.py
├── test_agent_coordination.py          # Multi-agent lifecycle and coordination
├── test_event_bus_integration.py       # Event bus under load and concurrency
├── test_shared_state_integration.py    # State management and consistency
├── test_performance_benchmarks.py      # Performance under various loads
└── test_error_scenarios.py             # Error handling and recovery
```

### Test Categories

1. **Agent Coordination** - How multiple agents work together
2. **Event Bus Integration** - Event publishing, subscribing, and filtering
3. **Shared State Integration** - Concurrent state access and updates
4. **Performance Benchmarks** - System performance under load
5. **Error Scenarios** - Error handling and failure isolation

---

## Running Integration Tests

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure you're in the project root
cd /path/to/Adastrea-Director
```

### Run All Integration Tests

```bash
# Run all Phase 3 integration tests
pytest tests/integration/phase3/ -v

# Run with coverage report
pytest tests/integration/phase3/ --cov=agents.phase3 --cov-report=html

# Run with detailed output
pytest tests/integration/phase3/ -vv --tb=long
```

### Run Specific Test Files

```bash
# Run only agent coordination tests
pytest tests/integration/phase3/test_agent_coordination.py -v

# Run only event bus integration tests
pytest tests/integration/phase3/test_event_bus_integration.py -v

# Run only shared state tests
pytest tests/integration/phase3/test_shared_state_integration.py -v

# Run only performance benchmarks
pytest tests/integration/phase3/test_performance_benchmarks.py -v

# Run only error scenarios
pytest tests/integration/phase3/test_error_scenarios.py -v
```

### Run Specific Test Classes

```bash
# Run multi-agent lifecycle tests
pytest tests/integration/phase3/test_agent_coordination.py::TestMultiAgentLifecycle -v

# Run event coordination tests
pytest tests/integration/phase3/test_agent_coordination.py::TestEventCoordination -v

# Run state coordination tests
pytest tests/integration/phase3/test_agent_coordination.py::TestStateCoordination -v
```

### Run Performance Tests

Performance tests are marked with `@pytest.mark.slow` and can take longer:

```bash
# Run all performance benchmarks
pytest tests/integration/phase3/test_performance_benchmarks.py -v

# Run specific benchmark
pytest tests/integration/phase3/test_performance_benchmarks.py::TestEventBusPerformance -v

# Skip slow tests for quick validation
pytest tests/integration/phase3/ -v -m "not slow"
```

---

## Test Suite Details

### 1. Agent Coordination Tests

**File:** `test_agent_coordination.py`  
**Test Classes:** 4  
**Test Count:** 15+ tests

#### TestMultiAgentLifecycle
Tests agent startup, shutdown, and lifecycle coordination.

**Key Tests:**
- `test_multiple_agents_start_stop` - Multiple agents starting and stopping cleanly
- `test_agent_start_events` - Agents receiving start events from peers
- Agent state registration in shared context
- Simultaneous agent operations

**Usage Example:**
```bash
pytest tests/integration/phase3/test_agent_coordination.py::TestMultiAgentLifecycle -v
```

#### TestEventCoordination
Tests coordination through event publishing and subscribing.

**Key Tests:**
- `test_event_propagation` - Events reaching all subscribed agents
- `test_reactive_event_chain` - Agents reacting to other agents' events
- `test_concurrent_event_publishing` - Multiple agents publishing simultaneously
- Event ordering guarantees

**Usage Example:**
```bash
pytest tests/integration/phase3/test_agent_coordination.py::TestEventCoordination -v
```

#### TestStateCoordination
Tests coordination through shared state.

**Key Tests:**
- `test_state_synchronization` - Agents seeing each other's state
- `test_shared_data_coordination` - Coordinating via shared data
- `test_concurrent_state_updates` - Concurrent state modifications
- State consistency guarantees

#### TestErrorCoordination
Tests error handling in multi-agent scenarios.

**Key Tests:**
- `test_agent_failure_isolation` - One agent's failure doesn't affect others
- `test_error_event_propagation` - Error events are properly broadcast
- Error recovery mechanisms

---

### 2. Event Bus Integration Tests

**File:** `test_event_bus_integration.py`  
**Test Classes:** 4  
**Test Count:** 12+ tests

#### TestEventBusConcurrency
Tests event bus behavior under concurrent operations.

**Key Tests:**
- `test_concurrent_publishing` - 10 threads × 50 events each
- `test_concurrent_subscribe_unsubscribe` - Concurrent subscription changes
- `test_event_ordering` - Event ordering guarantees per agent
- Thread safety validation

**Expected Performance:**
- 500+ events published and delivered without loss
- No race conditions or deadlocks
- Consistent event ordering per source

#### TestEventFiltering
Tests event filtering and selective subscription.

**Key Tests:**
- `test_selective_subscription` - Agents only receive subscribed events
- `test_history_filtering_by_source` - Filter events by source agent
- `test_history_filtering_combined` - Combined type and source filtering
- Subscription isolation

#### TestEventBusScalability
Tests scalability with many subscribers and events.

**Key Tests:**
- `test_many_subscribers` - 100 subscribers receiving all events
- `test_large_event_history` - 2000+ events (history limit validation)
- `test_rapid_event_publishing` - 1000 events in < 1 second
- Memory management with large history

**Performance Targets:**
- Support 100+ concurrent subscribers
- Handle 1000+ events per second
- Maintain < 1 second for 1000 events

#### TestEventBusReliability
Tests reliability and error handling.

**Key Tests:**
- `test_subscriber_exception_isolation` - Handler exceptions don't break event bus
- `test_unsubscribe_during_iteration` - Safe unsubscription
- `test_event_bus_clear_history` - History management
- Graceful degradation

---

### 3. Shared State Integration Tests

**File:** `test_shared_state_integration.py`  
**Test Classes:** 7  
**Test Count:** 15+ tests

#### TestSharedStateConsistency
Tests state consistency under concurrent access.

**Key Tests:**
- `test_concurrent_agent_registration` - 20 threads × 10 agents
- `test_concurrent_state_updates` - 10 threads × 50 updates
- `test_concurrent_shared_data_access` - 10 threads × 100 operations
- Data consistency guarantees

**Expected Behavior:**
- All 200 agents successfully registered
- No data corruption
- State updates are atomic

#### TestProjectInfoManagement
Tests project information sharing between agents.

**Key Tests:**
- `test_project_info_sharing` - Multiple agents reading project info
- `test_code_structure_updates` - Code structure updates
- Consistent view across agents

#### TestChangeTracking
Tests change history tracking.

**Key Tests:**
- `test_concurrent_change_recording` - 10 agents × 50 changes
- `test_change_history_limit` - Respecting history size limits
- Change ordering and retrieval

#### TestConversationHistory
Tests conversation logging.

**Key Tests:**
- `test_conversation_recording` - Recording conversations
- `test_concurrent_conversation_logging` - Concurrent conversation updates
- History management

#### TestAgentMetricsAggregation
Tests aggregating metrics across agents.

**Key Tests:**
- `test_aggregate_metrics_across_agents` - Collecting metrics from 5 agents
- Metrics calculation (totals, averages, rates)
- Cross-agent analytics

#### TestStateCleaning
Tests state cleanup operations.

**Key Tests:**
- `test_clear_all` - Clearing all shared state
- `test_delete_shared_data` - Deleting specific keys
- State management

#### TestStateSnapshots
Tests capturing state snapshots.

**Key Tests:**
- `test_agent_state_snapshot` - Point-in-time state capture
- Snapshot immutability

---

### 4. Performance Benchmarks

**File:** `test_performance_benchmarks.py`  
**Test Classes:** 3  
**Test Count:** 8+ tests  
**Mark:** `@pytest.mark.slow`

#### TestEventBusPerformance
Benchmarks event bus performance.

**Key Benchmarks:**
- `test_event_publishing_throughput` - 1000 events throughput
- `test_event_publishing_latency` - Publish latency statistics
- `test_subscriber_notification_latency` - Notification latency
- `test_memory_usage` - Memory overhead

**Performance Targets:**
- **Throughput:** > 1000 events/second
- **Latency:** < 1ms per event (p50)
- **Memory:** < 100KB for 1000 events

#### TestSharedStatePerformance
Benchmarks shared state operations.

**Key Benchmarks:**
- `test_state_read_performance` - Read operation latency
- `test_state_write_performance` - Write operation latency
- `test_concurrent_access_overhead` - Contention overhead
- `test_large_dataset_performance` - Scaling with data size

**Performance Targets:**
- **Read latency:** < 0.1ms (p50)
- **Write latency:** < 0.5ms (p50)
- **Concurrent access:** Linear scaling up to 10 threads

#### TestMultiAgentPerformance
Benchmarks overall system performance.

**Key Benchmarks:**
- `test_agent_startup_time` - Time to start 10 agents
- `test_event_propagation_latency` - End-to-end event latency
- `test_system_throughput` - Overall system throughput
- `test_resource_usage` - CPU and memory under load

**Performance Targets:**
- **Startup:** < 1 second for 10 agents
- **Event latency:** < 10ms end-to-end
- **System throughput:** > 500 operations/second

---

### 5. Error Scenarios Tests

**File:** `test_error_scenarios.py`  
**Test Classes:** 4  
**Test Count:** 10+ tests

#### TestAgentFailureRecovery
Tests agent failure and recovery.

**Key Tests:**
- `test_agent_start_failure` - Handling agent start failures
- `test_agent_error_limit` - Stopping after max errors (10)
- `test_partial_agent_failure` - System continues despite failures
- Error state management

#### TestEventBusErrorHandling
Tests event bus error handling.

**Key Tests:**
- `test_subscriber_exception` - Handler exceptions don't break bus
- `test_invalid_event` - Handling invalid events
- `test_unsubscribe_errors` - Graceful unsubscribe failures
- Error isolation

#### TestSharedStateErrorHandling
Tests shared state error handling.

**Key Tests:**
- `test_concurrent_access_errors` - Handling concurrent access errors
- `test_invalid_state_updates` - Rejecting invalid updates
- `test_data_corruption_prevention` - Preventing data corruption
- State validation

#### TestSystemResilience
Tests overall system resilience.

**Key Tests:**
- `test_cascading_failure_prevention` - Preventing cascading failures
- `test_graceful_degradation` - System continues with partial failures
- `test_recovery_after_errors` - System recovery after errors
- Fault tolerance

---

## Test Fixtures

### Common Fixtures

```python
@pytest.fixture
def event_bus():
    """Create a fresh event bus for testing."""
    return EventBus()

@pytest.fixture
def shared_context():
    """Create a fresh shared context for testing."""
    return SharedContext()
```

### Test Agents

```python
class SimpleTestAgent(BaseAutonomousAgent):
    """Simple test agent for integration testing."""
    # Minimal implementation for testing
    
class ReactiveTestAgent(BaseAutonomousAgent):
    """Test agent that reacts to other agents' events."""
    # Reactive behavior for testing coordination

class FaultyAgent(BaseAutonomousAgent):
    """Agent that simulates various failure modes."""
    # Configurable failure modes for error testing
```

---

## Interpreting Test Results

### Success Criteria

All tests should:
- ✅ Pass with 100% success rate
- ✅ Complete in reasonable time (< 2 seconds for fast tests, < 30 seconds for benchmarks)
- ✅ Show no memory leaks
- ✅ Demonstrate thread safety
- ✅ Validate error handling

### Performance Expectations

| Test Type | Expected Time | Pass Threshold |
|-----------|---------------|----------------|
| Agent Coordination | < 2s | All pass |
| Event Bus | < 1s | All pass |
| Shared State | < 1s | All pass |
| Performance Benchmarks | < 30s | Meet targets |
| Error Scenarios | < 2s | All pass |

### Coverage Targets

| Component | Target Coverage | Current |
|-----------|-----------------|---------|
| Event Bus | > 90% | 96% |
| Shared State | > 90% | 98% |
| Base Agent | > 70% | 71% |
| Integration Tests | N/A | Comprehensive |

---

## Troubleshooting

### Common Issues

#### Test Failures Due to Timing
**Symptom:** Intermittent failures in concurrent tests  
**Solution:** Increase wait times or use synchronization primitives

#### Memory Issues
**Symptom:** Tests fail with memory errors  
**Solution:** Reduce test iterations or clean up resources more aggressively

#### Coverage Reporting
**Symptom:** Coverage not matching expectations  
**Solution:** Ensure all test files are included in coverage report

### Debug Mode

Run tests with additional debugging:

```bash
# Verbose output with full tracebacks
pytest tests/integration/phase3/ -vv --tb=long

# Show print statements
pytest tests/integration/phase3/ -v -s

# Stop on first failure
pytest tests/integration/phase3/ -v -x

# Show locals on failure
pytest tests/integration/phase3/ -v --showlocals
```

---

## Continuous Integration

### CI Configuration

Integration tests run automatically on:
- Pull requests
- Commits to main branch
- Nightly builds

### CI Commands

```bash
# Fast tests only (for PR validation)
pytest tests/integration/phase3/ -v -m "not slow"

# Full test suite (for nightly builds)
pytest tests/integration/phase3/ -v

# With coverage (for code review)
pytest tests/integration/phase3/ --cov=agents.phase3 --cov-report=xml
```

---

## Adding New Integration Tests

### Test Template

```python
"""
Integration tests for [Component].

[Brief description of what these tests cover]
"""

import pytest
from agents.phase3.event_bus import Event, EventBus, EventType
from agents.phase3.shared_state import SharedContext


class Test[ComponentName]:
    """Test [component] functionality."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus."""
        return EventBus()
    
    @pytest.fixture
    def shared_context(self):
        """Create a fresh shared context."""
        return SharedContext()
    
    def test_[specific_scenario](self, event_bus, shared_context):
        """Test [specific behavior]."""
        # Arrange
        # ... setup
        
        # Act
        # ... perform actions
        
        # Assert
        # ... verify results
```

### Best Practices

1. **Use Fixtures** - Ensure clean state for each test
2. **Test One Thing** - Each test should verify one behavior
3. **Clear Names** - Test names should describe what they test
4. **Document Expected Behavior** - Use docstrings
5. **Clean Up** - Always stop agents and clean resources
6. **Avoid Hardcoded Delays** - Use synchronization when possible
7. **Test Error Cases** - Don't just test happy paths

---

## Related Documentation

- **[PHASE3_GUIDE.md](../../PHASE3_GUIDE.md)** - Phase 3 user guide
- **[PHASE3_STATUS.md](../phases/PHASE3_STATUS.md)** - Current Phase 3 status
- **[TESTING.md](TESTING.md)** - General testing guidelines
- **[TEST_SUMMARY.md](TEST_SUMMARY.md)** - Overall test results

---

## Changelog

### November 19, 2025
- ✨ Initial integration testing guide created
- 📋 Documented all test suites
- 🎯 Added running instructions
- 📊 Performance benchmarks documented

---

**For questions or issues, see the main [TESTING.md](TESTING.md) guide or open a GitHub issue.**
