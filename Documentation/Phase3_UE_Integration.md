# Phase 3 Agent Integration with Unreal Engine

This document describes how to integrate and use the Phase 3 autonomous agents (Performance Profiling, Bug Detection, Code Quality) with Unreal Engine projects via the Adastrea Director plugin.

## Overview

The Phase 3 agents provide autonomous monitoring and analysis capabilities for Unreal Engine projects:

- **Performance Profiling Agent**: Real-time FPS, memory, CPU/GPU monitoring with bottleneck detection
- **Bug Detection Agent**: Automated log analysis, crash detection, and test execution
- **Code Quality Agent**: Static code analysis, Blueprint complexity analysis, and technical debt tracking

## Architecture

```
┌─────────────────────────────────────────────────┐
│        Unreal Engine (C++ Plugin)               │
│  ┌──────────────────────────────────────────┐   │
│  │  AdastreaDirector Plugin                 │   │
│  │  - IPC Client                            │   │
│  │  - UI Widgets                            │   │
│  │  - Blueprint Functions                   │   │
│  └────────────────┬─────────────────────────┘   │
└───────────────────┼─────────────────────────────┘
                    │ TCP/IP (Port 5555)
                    ▼
┌─────────────────────────────────────────────────┐
│     Python Backend (IPC Server)                 │
│  ┌──────────────────────────────────────────┐   │
│  │  IntegratedIPCServer                     │   │
│  │  - Handler Registration                  │   │
│  │  - Agent Management                      │   │
│  │  - Event Bus                             │   │
│  └────────────────┬─────────────────────────┘   │
│                   │                             │
│  ┌────────────────┴──────────────────────────┐  │
│  │      Phase 3 Agents                       │  │
│  │  ┌──────────────────────────────────────┐ │  │
│  │  │  PerformanceProfilingAgent           │ │  │
│  │  │  - Metrics Collection                │ │  │
│  │  │  - Bottleneck Detection              │ │  │
│  │  │  - PIE Profiling                     │ │  │
│  │  └──────────────────────────────────────┘ │  │
│  │  ┌──────────────────────────────────────┐ │  │
│  │  │  BugDetectionAgent                   │ │  │
│  │  │  - Log Analysis                      │ │  │
│  │  │  - Crash Detection                   │ │  │
│  │  │  - Test Execution                    │ │  │
│  │  └──────────────────────────────────────┘ │  │
│  │  ┌──────────────────────────────────────┐ │  │
│  │  │  CodeQualityAgent                    │ │  │
│  │  │  - Code Analysis                     │ │  │
│  │  │  - Blueprint Analysis                │ │  │
│  │  │  - Technical Debt                    │ │  │
│  │  └──────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Setup

### Prerequisites

1. Python 3.9 or higher
2. Adastrea Director dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```
3. Unreal Engine 5.x with Remote Control plugin enabled (optional, for UE integration)

### Starting the IPC Server with Phase 3 Agents

```bash
# Navigate to the plugin Python directory
cd Plugins/AdastreaDirector/Python

# Start the integrated IPC server with Phase 3 agents enabled
python ipc_integration.py --enable-phase3 --port 5555

# Optional: Enable all features
python ipc_integration.py --enable-rag --enable-planning --enable-phase3 --port 5555
```

### Configuration

The IPC server can be configured with the following options:

- `--host`: Host address to bind to (default: `127.0.0.1`)
- `--port`: Port to listen on (default: `5555`)
- `--enable-rag`: Enable RAG system integration
- `--enable-planning`: Enable planning agents (Goal Analysis, Task Decomposition)
- `--enable-phase3`: **Enable Phase 3 autonomous agents**
- `--verbose`: Enable verbose logging

## IPC Protocol Commands

### Agent Lifecycle

#### Start Agent(s)
```json
{
  "command": "agent_start",
  "data": {
    "agent_id": "performance"  // "performance", "bug_detection", "code_quality", or "all"
  }
}
```

#### Stop Agent(s)
```json
{
  "command": "agent_stop",
  "data": {
    "agent_id": "all"  // "performance", "bug_detection", "code_quality", or "all"
  }
}
```

#### Get Agent Status
```json
{
  "command": "agent_status",
  "data": ""
}
```

**Response:**
```json
{
  "status": "success",
  "agents": {
    "performance": {
      "running": true,
      "status": "idle",
      "tasks_completed": 5
    },
    "bug_detection": {
      "running": true,
      "status": "busy",
      "tasks_completed": 12
    },
    "code_quality": {
      "running": false,
      "status": "stopped",
      "tasks_completed": 0
    }
  }
}
```

### Performance Profiling Commands

#### Collect Metrics
Collect performance metrics manually or from Unreal Engine:

```json
{
  "command": "collect_metrics",
  "data": {
    "frame_rate": 58.5,
    "memory_usage_mb": 3072.0,
    "cpu_usage_percent": 65.0,
    "gpu_usage_percent": 82.0,
    "draw_calls": 2400,
    "triangles": 750000
  }
}
```

Or leave empty to collect from UE via Remote Control API:
```json
{
  "command": "collect_metrics",
  "data": ""
}
```

#### Analyze Performance
```json
{
  "command": "analyze_performance",
  "data": ""
}
```

**Response:**
```json
{
  "status": "success",
  "analysis": {
    "summary": "Frame rate (58.5 FPS) below target (60.0 FPS)",
    "bottlenecks": [
      {
        "type": "frame_rate",
        "severity": "medium",
        "description": "Frame rate is 58.5 FPS, below target of 60.0 FPS"
      }
    ],
    "recommendations": [
      {
        "title": "Optimize Rendering Pipeline",
        "description": "Profile GPU and CPU usage...",
        "priority": "high"
      }
    ]
  }
}
```

#### Start PIE Profiling Session
```json
{
  "command": "start_pie_profiling",
  "data": {
    "duration_seconds": 60
  }
}
```

### Bug Detection Commands

#### Analyze Logs
```json
{
  "command": "analyze_logs",
  "data": {
    "log_content": "[2025-12-29] Error: Null pointer exception..."
  }
}
```

Or provide a log file path:
```json
{
  "command": "analyze_logs",
  "data": {
    "log_file": "/path/to/logfile.log"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "anomalies": [
    {
      "type": "error",
      "severity": "high",
      "description": "Error message detected in logs",
      "location": "Line 42"
    }
  ]
}
```

#### Run Automated Tests
```json
{
  "command": "run_tests",
  "data": {
    "test_suite": "unit_tests",
    "test_count": 50,
    "passed": 48,
    "failed": 2
  }
}
```

#### Get Detected Bugs
```json
{
  "command": "get_bugs",
  "data": {
    "severity": "high"  // Optional filter
  }
}
```

### Code Quality Commands

#### Analyze Code
```json
{
  "command": "analyze_code_quality",
  "data": {
    "file_path": "MyClass.py",
    "code_content": "def my_function():\n    x = 12345\n    return x"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "report": {
    "file_path": "MyClass.py",
    "lines_of_code": 15,
    "complexity_score": 45.0,
    "overall_score": 72.5,
    "code_smells": 3,
    "violations": 2,
    "refactorings": 3
  }
}
```

#### Analyze Blueprint Complexity
```json
{
  "command": "analyze_blueprint",
  "data": {
    "blueprint_path": "/Game/Blueprints/BP_MyActor"
  }
}
```

#### Get Technical Debt
```json
{
  "command": "get_technical_debt",
  "data": ""
}
```

**Response:**
```json
{
  "status": "success",
  "debt": {
    "total_debt_hours": 12.5,
    "debt_ratio": 0.25,
    "code_smells_count": 15,
    "violations_count": 8,
    "high_priority_items": 3,
    "trend": "stable"
  }
}
```

## Dashboard Monitoring

Use the enhanced agent dashboard to monitor all Phase 3 agents in real-time:

```bash
# From project root
python agent_dashboard.py --auto-start
```

### Dashboard Features

The dashboard displays:

1. **Agent Status Table**: Shows running status, state, tasks completed, and success rates
2. **Performance Metrics Panel**:
   - Real-time FPS monitoring
   - Memory usage with threshold indicators
   - CPU/GPU utilization with color coding
   - Draw calls and triangle counts
   - Average FPS over 60 seconds

3. **Bug Detection Panel**:
   - Total bugs by severity (critical, high, medium, low)
   - Crash count
   - Latest test run results with success rates

4. **Code Quality Panel**:
   - Average quality score across analyzed files
   - Code smells and violations count
   - Technical debt metrics (hours, ratio, high priority items)
   - Latest analysis summary

5. **Event Summary**: Counts of all event types
6. **Recent Events**: Real-time event feed with severity indicators
7. **System Health**: LLM API and Vector Database health checks

## Usage Examples

### Example 1: Performance Monitoring Loop

```python
from Plugins.AdastreaDirector.Python.ipc_integration import IntegratedIPCServer
import json
import time

# Initialize server with Phase 3 agents
server = IntegratedIPCServer(
    enable_phase3_agents=True
)

# Start performance agent
server._handle_agent_start(json.dumps({'agent_id': 'performance'}))

# Monitoring loop
for i in range(10):
    # Collect metrics
    metrics = {
        'frame_rate': 60.0 - (i * 0.5),  # Simulated degradation
        'memory_usage_mb': 2048 + (i * 100),
        'cpu_usage_percent': 50 + (i * 3),
        'gpu_usage_percent': 70 + (i * 2)
    }
    
    response = server._handle_collect_metrics(json.dumps(metrics))
    print(f"Collected: {response['metrics']['frame_rate']:.1f} FPS")
    
    time.sleep(1)

# Analyze performance
analysis = server._handle_analyze_performance("")
print(f"Analysis: {analysis['analysis']['summary']}")

# Stop agent
server._handle_agent_stop(json.dumps({'agent_id': 'performance'}))
```

### Example 2: Automated Bug Detection

```python
# Start bug detection agent
server._handle_agent_start(json.dumps({'agent_id': 'bug_detection'}))

# Analyze UE log file
log_content = open('/path/to/ue4.log', 'r').read()
response = server._handle_analyze_logs(log_content)

for anomaly in response['anomalies']:
    if anomaly['severity'] in ['high', 'critical']:
        print(f"⚠️  {anomaly['type']}: {anomaly['description']}")

# Get all detected bugs
bugs = server._handle_get_bugs(json.dumps({'severity': 'high'}))
print(f"Found {len(bugs['bugs'])} high-severity bugs")
```

### Example 3: Code Quality Audit

```python
# Start code quality agent
server._handle_agent_start(json.dumps({'agent_id': 'code_quality'}))

# Analyze multiple files
files = ['GameMode.py', 'PlayerController.py', 'InventorySystem.py']

for file_path in files:
    with open(file_path, 'r') as f:
        code_content = f.read()
    
    response = server._handle_analyze_code_quality(json.dumps({
        'file_path': file_path,
        'code_content': code_content
    }))
    
    report = response['report']
    print(f"{file_path}: Score {report['overall_score']:.1f}/100")

# Get technical debt summary
debt = server._handle_get_technical_debt("")
print(f"Total Technical Debt: {debt['debt']['total_debt_hours']:.1f} hours")
```

## Integration with Unreal Engine

### Blueprint Integration

Create Blueprint nodes that call the IPC commands:

1. **Start Profiling**: Call `agent_start` with `performance` agent_id
2. **Get Performance Metrics**: Call `collect_metrics` and display in UI
3. **Show Analysis**: Call `analyze_performance` and display recommendations
4. **Stop Profiling**: Call `agent_stop`

### C++ Integration

Use the existing IPC client in the AdastreaDirector plugin:

```cpp
// Example: Start performance profiling
FString Command = TEXT("agent_start");
FString Data = TEXT("{\"agent_id\":\"performance\"}");
IPCClient->SendCommand(Command, Data);

// Example: Get agent status
FString StatusCommand = TEXT("agent_status");
FString StatusData = TEXT("");
FString Response = IPCClient->SendCommandSync(StatusCommand, StatusData);
// Parse JSON response
```

## Best Practices

1. **Start agents only when needed** to conserve resources
2. **Monitor agent status** regularly to detect issues
3. **Use PIE profiling** for comprehensive performance analysis
4. **Analyze logs periodically** to catch issues early
5. **Track technical debt** to maintain code quality over time
6. **Set appropriate thresholds** for FPS, memory, and quality scores
7. **Review recommendations** from agents and prioritize fixes

## Troubleshooting

### Agents not starting
- Check that dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.9+
- Check IPC server logs for initialization errors

### Cannot collect UE metrics
- Ensure Unreal Engine Remote Control API is enabled
- Verify connection to `localhost:30010`
- Check that UE project is running (PIE or standalone)

### Dashboard not updating
- Confirm agents are running: call `agent_status`
- Check event bus is publishing events
- Verify dashboard refresh rate (default: 1 second)

### High memory usage
- Stop unnecessary agents
- Limit metrics history size (default: 1000 entries)
- Clear old analysis reports periodically

## Future Enhancements

- Real-time event streaming to UE Editor UI
- Custom threshold configuration per project
- Integration with CI/CD pipelines
- Automated regression testing
- ML-based anomaly prediction
- Multi-project monitoring dashboard

## See Also

- [Phase 3 Architecture](../wiki/architecture/Phase-3-Architecture.md)
- [Agent Orchestrator CLI](../README.md#agent-orchestrator)
- [Remote Control API](../remote_control/README.md)
- [Event Bus Documentation](../agents/phase3/README.md)
