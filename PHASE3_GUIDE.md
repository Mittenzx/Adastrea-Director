# Phase 3: Autonomous Agents - User Guide

**Version:** 1.0  
**Last Updated:** 2025-11-12  
**Status:** Active Development

---

## Overview

Phase 3 introduces **autonomous agents** that run in the background to monitor performance, detect bugs, and maintain code quality. These agents work proactively to identify issues before they impact development.

### Key Features

1. **Event-Driven Architecture** - Agents communicate through a central event bus
2. **Shared State Management** - Coordinated context sharing between agents
3. **Real-time Monitoring** - Continuous performance and quality tracking
4. **Proactive Detection** - Identify issues before human QA
5. **Actionable Recommendations** - Not just alerts, but suggested fixes

---

## Architecture

### System Components

```
┌─────────────────────────────────────────┐
│        Event Bus                        │
│  - Publish/Subscribe messaging           │
│  - Event history tracking                │
│  - Decoupled communication               │
└─────────────────────────────────────────┘
                  ↕
┌─────────────────────────────────────────┐
│     Shared Context                      │
│  - Agent states                          │
│  - Project information                   │
│  - Code structure                        │
│  - Change tracking                       │
└─────────────────────────────────────────┘
                  ↕
┌────────────┬────────────┬───────────────┐
│  Perf      │   Bug      │   Code        │
│  Profiling │ Detection  │   Quality     │
│  Agent     │   Agent    │   Agent       │
└────────────┴────────────┴───────────────┘
```

---

## Agents

### 1. Performance Profiling Agent 🎯

**Purpose:** Monitor and analyze game performance in real-time.

#### Capabilities

- **Metric Collection**
  - Frame rate (FPS)
  - Memory usage (MB)
  - CPU utilization (%)
  - GPU utilization (%)
  - Draw calls per frame
  - Triangle count

- **Bottleneck Detection**
  - Low frame rate detection
  - Memory threshold violations
  - CPU/GPU saturation
  - Excessive draw calls
  - Severity classification (low, medium, high, critical)

- **Optimization Recommendations**
  - Specific, actionable suggestions
  - Estimated impact levels
  - Implementation difficulty ratings
  - Priority rankings

#### Usage Example

```python
from agents.phase3 import PerformanceProfilingAgent, EventBus, SharedContext

# Initialize infrastructure
event_bus = EventBus()
shared_context = SharedContext()

# Create and start agent
perf_agent = PerformanceProfilingAgent(
    event_bus=event_bus,
    shared_context=shared_context,
    target_fps=60.0,
    memory_threshold_mb=4096.0
)

perf_agent.start()

# Collect metrics (typically from Unreal Engine)
metrics = perf_agent.collect_metrics(
    frame_rate=55.0,
    memory_usage_mb=3500.0,
    cpu_usage_percent=75.0,
    gpu_usage_percent=85.0,
    draw_calls=2500,
    triangles=850000
)

# Analyze performance
analysis = perf_agent.analyze_performance(metrics)

print(f"Performance Summary: {analysis.summary}")
print(f"Bottlenecks Found: {len(analysis.bottlenecks)}")
print(f"Recommendations: {len(analysis.recommendations)}")

for rec in analysis.recommendations:
    print(f"  - [{rec.priority}] {rec.title}")
    print(f"    {rec.description}")

perf_agent.stop()
```

#### Event Types

The Performance Profiling Agent publishes:
- `PERFORMANCE_METRICS_COLLECTED` - When metrics are collected
- `PERFORMANCE_ALERT` - When performance issues are detected

### 2. Bug Detection Agent 🐛

**Purpose:** Proactively find and report bugs through automated analysis.

#### Capabilities

- **Log Analysis**
  - Pattern recognition for common errors
  - Error/warning detection
  - Anomaly identification
  - Context extraction

- **Crash Detection**
  - Stack trace analysis
  - Error message parsing
  - Location identification
  - Reproducibility tracking

- **Automated Testing**
  - Test execution
  - Result tracking
  - Failure analysis
  - Success rate monitoring

- **Bug Reporting**
  - Structured bug reports
  - Reproduction steps
  - Environment details
  - Severity classification

#### Usage Example

```python
from agents.phase3 import BugDetectionAgent, EventBus, SharedContext

# Initialize
event_bus = EventBus()
shared_context = SharedContext()

bug_agent = BugDetectionAgent(
    event_bus=event_bus,
    shared_context=shared_context
)

bug_agent.start()

# Analyze logs
with open('game_log.txt', 'r') as f:
    log_content = f.read()

anomalies = bug_agent.analyze_logs(log_content)
print(f"Anomalies detected: {len(anomalies)}")

for anomaly in anomalies:
    print(f"  [{anomaly.severity}] {anomaly.description}")
    print(f"    Location: {anomaly.location}")

# Report a crash
crash = bug_agent.detect_crashes(
    stack_trace="...",
    error_message="NullReferenceException in PlayerController"
)

# Create bug report
bug_report = bug_agent.create_bug_report(
    title="Player controller crash on spawn",
    description="Game crashes when spawning player in certain conditions",
    severity="high",
    reproduction_steps=[
        "Start game in debug mode",
        "Select level 'TestMap'",
        "Click 'Spawn Player'",
        "Observe crash"
    ],
    expected_behavior="Player spawns successfully",
    actual_behavior="Game crashes with NullReferenceException"
)

print(f"Bug Report Created: {bug_report.bug_id}")

bug_agent.stop()
```

#### Event Types

The Bug Detection Agent publishes:
- `BUG_DETECTED` - When a bug is identified
- `CRASH_DETECTED` - When a crash occurs
- `TEST_COMPLETED` - When tests finish
- `TEST_FAILED` - When tests fail

### 3. Code Quality Agent 📊

**Purpose:** Maintain code quality through static analysis and recommendations.

#### Capabilities

- **Code Smell Detection**
  - Long methods (>50 lines)
  - Magic numbers
  - Duplicate code
  - Commented code
  - Long parameter lists

- **Standards Checking**
  - PEP 8 compliance (Python)
  - Line length limits
  - Trailing whitespace
  - Tab vs. space usage

- **Refactoring Suggestions**
  - Extract method
  - Extract constant
  - Extract function
  - Remove dead code
  - Effort estimates and benefits

- **Technical Debt Tracking**
  - Total debt hours
  - Debt ratio
  - Trend analysis
  - High priority item count

#### Usage Example

```python
from agents.phase3 import CodeQualityAgent, EventBus, SharedContext

# Initialize
event_bus = EventBus()
shared_context = SharedContext()

quality_agent = CodeQualityAgent(
    event_bus=event_bus,
    shared_context=shared_context
)

quality_agent.start()

# Analyze a file
with open('src/player_controller.py', 'r') as f:
    code_content = f.read()

report = quality_agent.analyze_code(
    file_path='src/player_controller.py',
    code_content=code_content
)

print(f"Quality Score: {report.overall_score:.1f}/100")
print(f"Lines of Code: {report.lines_of_code}")
print(f"Complexity: {report.complexity_score:.1f}")
print(f"Code Smells: {len(report.code_smells)}")
print(f"Violations: {len(report.violations)}")

# Show refactoring opportunities
for refactoring in report.refactorings:
    print(f"\n[{refactoring.priority}] {refactoring.refactoring_type}")
    print(f"  {refactoring.description}")
    print(f"  Effort: {refactoring.estimated_effort}")
    print(f"  Benefits: {', '.join(refactoring.benefits)}")

# Calculate technical debt
debt = quality_agent.calculate_technical_debt()
print(f"\nTechnical Debt: {debt.total_debt_hours:.1f} hours")
print(f"Debt Ratio: {debt.debt_ratio:.2f}")
print(f"Trend: {debt.trend}")

quality_agent.stop()
```

#### Event Types

The Code Quality Agent publishes:
- `CODE_QUALITY_ISSUE` - When quality issues are found
- `REFACTORING_OPPORTUNITY` - When refactoring is suggested

---

## Event Bus

The Event Bus enables decoupled communication between agents.

### Event Types

All event types are defined in `EventType` enum:

```python
class EventType(Enum):
    # Performance
    PERFORMANCE_ALERT = "performance_alert"
    PERFORMANCE_METRICS_COLLECTED = "performance_metrics_collected"
    
    # Bug Detection
    BUG_DETECTED = "bug_detected"
    CRASH_DETECTED = "crash_detected"
    
    # Code Quality
    CODE_QUALITY_ISSUE = "code_quality_issue"
    REFACTORING_OPPORTUNITY = "refactoring_opportunity"
    
    # Testing
    TEST_COMPLETED = "test_completed"
    TEST_FAILED = "test_failed"
    
    # System
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    AGENT_ERROR = "agent_error"
    
    # Custom
    CUSTOM = "custom"
```

### Subscribing to Events

```python
from agents.phase3 import EventBus, EventType

event_bus = EventBus()

def handle_performance_alert(event):
    print(f"Performance alert: {event.payload['summary']}")
    print(f"Bottlenecks: {event.payload['bottleneck_count']}")

event_bus.subscribe(EventType.PERFORMANCE_ALERT, handle_performance_alert)
```

### Publishing Events

```python
from agents.phase3 import Event, EventType

event = Event(
    event_type=EventType.CUSTOM,
    source="my_component",
    payload={"message": "Custom event data"}
)

event_bus.publish(event)
```

### Event History

```python
# Get all recent events
all_events = event_bus.get_history(limit=100)

# Filter by type
perf_events = event_bus.get_history(
    event_type=EventType.PERFORMANCE_ALERT,
    limit=50
)

# Filter by source
agent_events = event_bus.get_history(
    source="performance_profiling_agent",
    limit=50
)
```

---

## Shared Context

The Shared Context provides centralized state management.

### Agent Registration

```python
from agents.phase3 import SharedContext

context = SharedContext()

# Register an agent
state = context.register_agent("my_agent")

# Update agent state
context.update_agent_state(
    "my_agent",
    status=AgentStatus.BUSY,
    current_task="Processing data"
)

# Get agent state
state = context.get_agent_state("my_agent")
print(f"Status: {state.status}")
print(f"Task: {state.current_task}")
```

### Project Information

```python
from agents.phase3 import ProjectInfo

project = ProjectInfo(
    name="My Game Project",
    root_path="/path/to/project",
    language="C++",
    framework="Unreal Engine 5.3"
)

context.set_project_info(project)
```

### Change Tracking

```python
from agents.phase3 import Change
from datetime import datetime

change = Change(
    change_id="commit_abc123",
    timestamp=datetime.now(),
    file_path="Source/MyGame/PlayerController.cpp",
    description="Fixed player movement bug",
    author="developer@example.com"
)

context.add_change(change)

# Get recent changes
recent = context.get_recent_changes(limit=10)
```

---

## Best Practices

### 1. Agent Lifecycle Management

Always start and stop agents properly:

```python
agent = PerformanceProfilingAgent(event_bus, shared_context)

try:
    agent.start()
    # ... use agent ...
finally:
    agent.stop()
```

### 2. Error Handling

Agents handle errors internally, but monitor for `AGENT_ERROR` events:

```python
def handle_agent_error(event):
    agent_id = event.payload['agent_id']
    error = event.payload['error']
    logger.error(f"Agent {agent_id} error: {error}")

event_bus.subscribe(EventType.AGENT_ERROR, handle_agent_error)
```

### 3. Performance Monitoring

Monitor agent performance through metrics:

```python
state = context.get_agent_state("performance_profiling_agent")
metrics = state.metrics

print(f"Tasks completed: {metrics.tasks_completed}")
print(f"Success rate: {metrics.success_rate():.1f}%")
print(f"Avg completion time: {metrics.average_completion_time:.2f}s")
```

### 4. Event Cleanup

Clear event history periodically to manage memory:

```python
# Clear history older than 1 hour
event_bus.clear_history()
```

---

## Integration with Unreal Engine

Phase 3 agents are designed to integrate with Unreal Engine via the Remote Control API (planned for future implementation):

### Future Integration Points

1. **Performance Profiling**
   - Execute `stat fps`, `stat gpu`, `stat memory` commands
   - Monitor Blueprint execution times
   - Track asset loading performance

2. **Bug Detection**
   - Automate Play In Editor (PIE) sessions
   - Monitor console logs in real-time
   - Capture screenshots on crashes

3. **Code Quality**
   - Analyze Blueprint complexity
   - Check asset organization
   - Validate naming conventions

---

## Testing

### Running Phase 3 Tests

```bash
# Run all Phase 3 tests
pytest tests/phase3/ -v

# Run specific test file
pytest tests/phase3/test_event_bus.py -v

# Run with coverage
pytest tests/phase3/ --cov=agents.phase3 --cov-report=html
```

### Test Coverage

Current test coverage:
- Event Bus: 96%
- Shared State: 98%
- Performance Profiling Agent: 93%
- Bug Detection Agent: 45% (implementation phase)
- Code Quality Agent: 36% (implementation phase)

---

## Troubleshooting

### Agent Not Starting

**Problem:** Agent fails to start  
**Solution:** Check agent is properly registered with shared context

```python
# Verify registration
state = context.get_agent_state(agent.agent_id)
if state is None:
    print("Agent not registered!")
```

### Events Not Being Received

**Problem:** Subscriber not receiving events  
**Solution:** Verify subscription before publishing

```python
# Check subscriber count
count = event_bus.get_subscriber_count(EventType.PERFORMANCE_ALERT)
print(f"Subscribers: {count}")
```

### High Memory Usage

**Problem:** Event history consuming too much memory  
**Solution:** Reduce history size or clear periodically

```python
# Clear old events
event_bus.clear_history()

# Limit history size (done at initialization)
event_bus._max_history_size = 500
```

---

## Roadmap

### Completed ✅
- Event Bus infrastructure
- Shared State Management
- Base autonomous agent architecture
- Performance Profiling Agent
- Bug Detection Agent (foundation)
- Code Quality Agent (foundation)

### In Progress 🚧
- Additional tests for Bug/Quality agents
- Agent orchestration CLI
- Dashboard UI for monitoring

### Planned 📋
- Unreal Engine Remote Control integration
- Real-time monitoring dashboard
- Automated regression testing
- Performance trend visualization
- Email/Slack alert integration

---

## API Reference

See inline documentation in:
- `agents/phase3/event_bus.py`
- `agents/phase3/shared_state.py`
- `agents/phase3/base_agent.py`
- `agents/phase3/performance_profiling_agent.py`
- `agents/phase3/bug_detection_agent.py`
- `agents/phase3/code_quality_agent.py`

---

## Contributing

When extending Phase 3:

1. **New Agents:** Inherit from `BaseAutonomousAgent`
2. **New Events:** Add to `EventType` enum
3. **New Tests:** Add to `tests/phase3/`
4. **Documentation:** Update this guide

---

## Support

- **Issues:** [GitHub Issues](https://github.com/Mittenzx/Adastrea-Director/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Mittenzx/Adastrea-Director/discussions)
- **Documentation:** [ROADMAP.md](ROADMAP.md), [AGENTS.md](AGENTS.md)

---

**Version:** 1.0  
**Last Updated:** 2025-11-12  
**Authors:** Adastrea Director Team
