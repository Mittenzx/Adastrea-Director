# Agent Architecture (Phase 3)

This document describes the architecture of the autonomous agent system in Adastrea Director.

## Overview

The Agent System (Phase 3) provides a flexible, extensible framework for autonomous agents that can proactively monitor, analyze, and assist with game development tasks.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Orchestrator                             │
│  • Agent Lifecycle Management                                │
│  • Event Coordination                                        │
│  • Resource Allocation                                       │
└─────────────┬───────────────────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌────────────┐    ┌────────────┐
│ Event Bus  │    │   Shared   │
│            │◄───┤   State    │
│ (Pub/Sub)  │    │  Manager   │
└─────┬──────┘    └────────────┘
      │
      ├──────────┬──────────┬──────────┐
      ▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Performance│ │   Bug    │ │   Code   │ │  Future  │
│  Agent   │ │Detection │ │ Quality  │ │  Agents  │
│          │ │  Agent   │ │  Agent   │ │          │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

## Core Components

### 1. Agent Orchestrator

**Purpose:** Manages the lifecycle and coordination of all agents.

**Responsibilities:**
- Start/stop agents
- Monitor agent health
- Handle agent failures
- Resource allocation
- Event coordination

**Implementation:**
```python
class AgentOrchestrator:
    def __init__(self):
        self.agents = {}
        self.event_bus = EventBus()
        self.shared_state = SharedState()
    
    def start_agent(self, agent_type: str):
        agent = AgentFactory.create(agent_type)
        agent.start()
        self.agents[agent_type] = agent
    
    def stop_agent(self, agent_type: str):
        if agent_type in self.agents:
            self.agents[agent_type].stop()
            del self.agents[agent_type]
```

### 2. Event Bus

**Purpose:** Facilitates communication between agents via publish-subscribe pattern.

**Features:**
- Asynchronous message passing
- Topic-based subscriptions
- Event filtering
- Event history

**Example:**
```python
# Agent publishes event
event_bus.publish("performance.warning", {
    "metric": "fps",
    "value": 30,
    "threshold": 60,
    "timestamp": datetime.now()
})

# Other agents subscribe
event_bus.subscribe("performance.*", performance_callback)
event_bus.subscribe("*.warning", alert_callback)
```

### 3. Shared State

**Purpose:** Thread-safe state management across all agents.

**Features:**
- Atomic operations
- State persistence
- Rollback support
- State queries

**Example:**
```python
# Agent updates state
shared_state.set("last_performance_check", datetime.now())

# Agent reads state
last_check = shared_state.get("last_performance_check")

# Atomic increment
shared_state.increment("alert_count")
```

### 4. Base Agent

All agents inherit from a base agent class:

```python
class BaseAgent(ABC):
    def __init__(self, event_bus, shared_state):
        self.event_bus = event_bus
        self.shared_state = shared_state
        self.running = False
    
    @abstractmethod
    def run(self):
        """Main agent loop"""
        pass
    
    @abstractmethod
    def on_event(self, event):
        """Handle incoming events"""
        pass
    
    def start(self):
        self.running = True
        threading.Thread(target=self.run).start()
    
    def stop(self):
        self.running = False
```

## Agent Types

### Performance Agent

**Purpose:** Monitor and optimize performance metrics.

**Capabilities:**
- FPS monitoring
- Memory usage tracking
- CPU profiling
- GPU utilization
- Frame time analysis

**Events Published:**
- `performance.warning` - Performance issue detected
- `performance.report` - Periodic performance report
- `performance.optimized` - Optimization applied

**Events Subscribed:**
- `system.start` - Begin monitoring
- `system.stop` - Stop monitoring

### Bug Detection Agent

**Purpose:** Identify potential bugs and issues.

**Capabilities:**
- Log analysis
- Crash detection
- Error pattern recognition
- Reproduction step generation

**Events Published:**
- `bug.detected` - New bug found
- `bug.analyzed` - Bug analysis complete
- `bug.reproduced` - Reproduction steps available

**Events Subscribed:**
- `system.error` - System error occurred
- `crash.reported` - Crash detected

### Code Quality Agent

**Purpose:** Monitor code quality and suggest improvements.

**Capabilities:**
- Code smell detection
- Complexity analysis
- Style checking
- Best practice validation

**Events Published:**
- `quality.issue` - Quality issue found
- `quality.suggestion` - Improvement suggested
- `quality.improved` - Quality metric improved

**Events Subscribed:**
- `code.changed` - Code was modified
- `build.completed` - Build finished

## Communication Patterns

### Event-Driven

Agents communicate via events:

```python
# Pattern 1: Reactive
@subscribe("performance.warning")
def on_performance_warning(event):
    # React to performance issues
    analyze_and_optimize(event.data)

# Pattern 2: Proactive
def agent_loop():
    while running:
        metrics = collect_metrics()
        if metrics.fps < threshold:
            event_bus.publish("performance.warning", metrics)
        time.sleep(interval)
```

### Request-Response

For synchronous operations:

```python
# Agent requests action
result = orchestrator.request_action("analyze_code", {
    "file": "player.cpp",
    "lines": [100, 150]
})

# Orchestrator handles request
def request_action(action_type, params):
    if action_type == "analyze_code":
        return code_analyzer.analyze(params)
```

### State Sharing

Agents share state via shared state manager:

```python
# Agent A sets state
shared_state.set("last_optimization", {
    "timestamp": datetime.now(),
    "improvement": 15.3  # % FPS improvement
})

# Agent B reads state
last_opt = shared_state.get("last_optimization")
if last_opt and is_recent(last_opt["timestamp"]):
    # Consider recent optimization in analysis
    pass
```

## Agent Lifecycle

### Initialization

```
Create Agent → Register with Orchestrator → Subscribe to Events → Initialize State
```

### Running

```
Event Loop:
  1. Check for events
  2. Process events
  3. Perform periodic tasks
  4. Publish results
  5. Update state
```

### Shutdown

```
Stop Signal → Cleanup → Unsubscribe → Final Report → Terminate
```

## Design Patterns

### 1. Observer Pattern

Agents observe events via the event bus:
- Loose coupling
- Scalable
- Easy to add new agents

### 2. Singleton Pattern

Shared state and event bus are singletons:
- Single source of truth
- Consistent state
- Easy access

### 3. Factory Pattern

Agent creation via factory:
- Encapsulated creation logic
- Easy to add new agent types
- Configuration-driven

### 4. Template Method Pattern

Base agent defines workflow:
- Consistent agent structure
- Reusable base functionality
- Easy to extend

## Scalability

### Current Scale

- **Agents:** Up to 10 concurrent
- **Events:** 1000+ events/second
- **State:** Thread-safe for concurrent access

### Future Scaling

**Distributed Agents:**
```
Orchestrator → Message Queue → Agent Workers
                 (RabbitMQ)     (Multiple processes)
```

**Agent Clustering:**
```
Load Balancer → Agent Cluster 1
             → Agent Cluster 2
             → Agent Cluster 3
```

## Integration Points

### With RAG System (P1)

Agents use RAG for context:
```python
# Agent queries documentation
context = rag_system.query("How to optimize rendering?")
optimization = analyze_with_context(metrics, context)
```

### With Planning System (P2)

Agents create plans:
```python
# Agent generates optimization plan
plan = planner.create_plan("Optimize rendering for target FPS")
execute_plan(plan)
```

### With Remote Control API

External systems control agents:
```python
# HTTP API
POST /agents/start
POST /agents/stop
GET /agents/status
GET /agents/events
```

## Testing

### Unit Tests

Test individual agent components:
```python
def test_performance_agent_detects_low_fps():
    agent = PerformanceAgent(mock_event_bus, mock_state)
    metrics = {"fps": 30}
    agent.analyze(metrics)
    assert mock_event_bus.published("performance.warning")
```

### Integration Tests

Test agent interactions:
```python
def test_agents_coordinate_optimization():
    orchestrator = AgentOrchestrator()
    orchestrator.start_agent("performance")
    orchestrator.start_agent("code_quality")
    
    # Trigger performance issue
    simulate_low_fps()
    
    # Verify agents coordinated
    assert check_optimization_applied()
```

### End-to-End Tests

Test complete workflows:
```python
def test_full_optimization_workflow():
    # Start system
    orchestrator.start_all()
    
    # Simulate issue
    trigger_performance_issue()
    
    # Verify resolution
    wait_for_resolution()
    assert performance_improved()
```

## Security Considerations

### Sandboxing

Agents run in restricted environment:
- Limited file system access
- No arbitrary code execution
- Resource limits

### Authorization

Agents require permissions:
```python
@requires_permission("file.read")
def read_code_file(path):
    return read_file(path)

@requires_permission("system.modify")
def apply_optimization(optimization):
    modify_system(optimization)
```

## Future Enhancements

### Planned Agent Types

1. **Asset Management Agent**
   - Optimize asset sizes
   - Detect unused assets
   - Suggest LOD improvements

2. **Testing Agent**
   - Generate test cases
   - Run automated tests
   - Report coverage

3. **Documentation Agent**
   - Generate documentation
   - Keep docs up-to-date
   - Suggest improvements

### Advanced Features

- **Machine Learning:** Learn from past optimizations
- **Multi-Agent Collaboration:** Agents work together on complex tasks
- **Adaptive Behavior:** Agents adapt to project patterns

## Related Documentation

- [System Architecture](System-Architecture.md)
- [Phase 3 Guide](../phases/Phase-3-Autonomous-Agents.md)
- [Autonomous Agents Usage](../usage/Autonomous-Agents.md)
- [Remote Control API](../api/Remote-Control-API.md)

---

[← Back to Architecture](System-Architecture.md) | [Deployment Modes →](Deployment-Modes.md)
