# Agent Orchestration and Monitoring

This guide covers the Agent Orchestrator CLI and Dashboard UI for managing Phase 3 autonomous agents.

## Overview

The Agent Orchestration system provides two complementary tools:

1. **Agent Orchestrator CLI** - Command-line interface for controlling agents
2. **Agent Dashboard** - Real-time terminal UI for monitoring agents

## Agent Orchestrator CLI

### Features

- Start/stop individual agents or all agents at once
- Check agent status and health
- View recent events from agents
- Configure project settings
- List available agents

### Usage

```bash
# List available agents
python agent_orchestrator_cli.py list

# Check status of all agents
python agent_orchestrator_cli.py status

# Start all agents
python agent_orchestrator_cli.py start --all

# Start specific agents
python agent_orchestrator_cli.py start --agent performance bug_detection

# View recent events
python agent_orchestrator_cli.py events --limit 20

# Check detailed status with events
python agent_orchestrator_cli.py status --verbose --events 10

# Configure project
python agent_orchestrator_cli.py config \
  --project-name "My Game" \
  --project-path "/path/to/project" \
  --language "C++" \
  --framework "Unreal Engine 5.3"

# Stop specific agents
python agent_orchestrator_cli.py stop --agent performance

# Stop all agents
python agent_orchestrator_cli.py stop --all
```

### Available Agents

- **performance** - Performance Profiling Agent
  - Monitors FPS, memory usage, CPU/GPU utilization
  - Detects performance bottlenecks
  - Generates optimization recommendations

- **bug_detection** - Bug Detection Agent
  - Analyzes logs for errors and warnings
  - Detects crashes with stack traces
  - Creates bug reports with reproduction steps
  - Runs automated tests

- **code_quality** - Code Quality Agent
  - Analyzes code for smells and anti-patterns
  - Detects violations of coding standards
  - Suggests refactoring opportunities
  - Calculates technical debt

### Command Reference

#### start

Start one or more agents.

```bash
python agent_orchestrator_cli.py start [--agent AGENT [AGENT ...]] [--all]
```

Options:
- `--agent AGENT` - Name of agent(s) to start
- `--all` - Start all agents

#### stop

Stop one or more agents.

```bash
python agent_orchestrator_cli.py stop [--agent AGENT [AGENT ...]] [--all]
```

Options:
- `--agent AGENT` - Name of agent(s) to stop
- `--all` - Stop all agents

#### status

Show agent status information.

```bash
python agent_orchestrator_cli.py status [-v] [--events N]
```

Options:
- `-v, --verbose` - Show detailed status with events
- `--events N` - Number of events to show in verbose mode (default: 5)

#### events

Display recent events from agents.

```bash
python agent_orchestrator_cli.py events [--limit N]
```

Options:
- `--limit N` - Number of events to display (default: 10)

#### list

List all available agents.

```bash
python agent_orchestrator_cli.py list
```

#### config

Configure project settings.

```bash
python agent_orchestrator_cli.py config \
  --project-name NAME \
  --project-path PATH \
  [--language LANG] \
  [--framework FRAMEWORK]
```

Options:
- `--project-name NAME` - Project name (required)
- `--project-path PATH` - Project root path (required)
- `--language LANG` - Primary programming language (default: C++)
- `--framework FRAMEWORK` - Framework being used (default: Unreal Engine)

## Agent Dashboard

### Features

- Real-time agent status monitoring
- Live event feed
- Event summary with counts
- Visual status indicators
- Auto-refresh display

### Usage

```bash
# Start dashboard (agents stopped initially)
python agent_dashboard.py

# Start dashboard and auto-start all agents
python agent_dashboard.py --auto-start

# Custom update interval (seconds)
python agent_dashboard.py --interval 2.0

# Combination
python agent_dashboard.py --auto-start --interval 0.5
```

### Dashboard Layout

The dashboard displays four main panels:

1. **Header** - Shows current date/time
2. **Agent Status** - Real-time status of all agents
   - Agent name
   - Current status (IDLE, BUSY, ERROR, STOPPED)
   - Running state (🟢 Running / 🔴 Stopped)
3. **Event Summary** - Count of each event type
   - Color-coded by severity
   - Red: Critical events (crashes, test failures)
   - Yellow: Warning events (performance alerts, quality issues)
   - Green: Normal events (test completion, metrics)
4. **Recent Events** - Live feed of latest events
   - Timestamp
   - Event type (color-coded)
   - Source agent
5. **Controls** - Keyboard shortcuts and help

### Controlling the Dashboard

- **Ctrl+C** - Exit the dashboard
- Use `agent_orchestrator_cli.py` in another terminal to control agents while dashboard is running

### Dashboard Options

```bash
python agent_dashboard.py [-h] [--auto-start] [--interval INTERVAL]
```

Options:
- `--auto-start` - Automatically start all agents on launch
- `--interval INTERVAL` - Update interval in seconds (default: 1.0)

## Integration with Unreal Engine

### Setup

1. Configure your project:
```bash
python agent_orchestrator_cli.py config \
  --project-name "YourGame" \
  --project-path "/path/to/UE/Project" \
  --language "C++" \
  --framework "Unreal Engine 5.3"
```

2. Start agents:
```bash
python agent_orchestrator_cli.py start --all
```

3. Monitor in real-time:
```bash
python agent_dashboard.py
```

### Workflow

1. **Development Mode**
   - Start dashboard with `--auto-start`
   - Work on your Unreal project
   - Agents continuously monitor performance, code quality, and logs
   - Dashboard shows real-time feedback

2. **Testing Mode**
   - Start specific agents (e.g., `bug_detection`)
   - Run your game/tests
   - Agent analyzes logs and generates reports
   - View events with `agent_orchestrator_cli.py events`

3. **Code Review Mode**
   - Start `code_quality` agent
   - Agent analyzes code as you work
   - Provides refactoring suggestions
   - Tracks technical debt trends

## Event Types

The system publishes various event types:

- `agent_started` - Agent has started
- `agent_stopped` - Agent has stopped
- `performance_metrics_collected` - Performance data collected
- `performance_alert` - Performance issue detected
- `bug_detected` - Bug found and reported
- `crash_detected` - Crash detected and logged
- `test_completed` - Automated tests completed successfully
- `test_failed` - Automated tests failed
- `code_quality_issue` - Code quality problem detected
- `refactoring_opportunity` - Refactoring suggestion available

## Examples

### Example 1: Quick Status Check

```bash
# Check what's running
python agent_orchestrator_cli.py status

# See recent activity
python agent_orchestrator_cli.py events --limit 5
```

### Example 2: Start Performance Monitoring

```bash
# Start performance agent
python agent_orchestrator_cli.py start --agent performance

# Monitor in real-time
python agent_dashboard.py
```

### Example 3: Full Development Session

```bash
# Terminal 1: Start dashboard with all agents
python agent_dashboard.py --auto-start

# Terminal 2: Your Unreal Engine work
# (Agents run in background, dashboard shows activity)

# When done, stop all agents
python agent_orchestrator_cli.py stop --all
```

### Example 4: Code Quality Analysis

```bash
# Start code quality agent
python agent_orchestrator_cli.py start --agent code_quality

# Analyze code (programmatically)
python -c "
from agent_orchestrator_cli import AgentOrchestrator
orch = AgentOrchestrator()
agent = orch.agents['code_quality']
agent.start()

# Analyze a file
with open('MyCode.cpp', 'r') as f:
    code = f.read()
report = agent.analyze_code('MyCode.cpp', code)
print(f'Quality Score: {report.overall_score}/100')
print(f'Code Smells: {len(report.code_smells)}')
print(f'Violations: {len(report.violations)}')

agent.stop()
"
```

## Demo Script

A complete demo is available:

```bash
python examples/phase3_orchestrator_demo.py
```

This demonstrates:
- Creating and configuring the orchestrator
- Starting agents
- Simulating agent activity
- Viewing status and events
- Stopping agents

## Troubleshooting

### Agents won't start

**Issue:** Agent fails to start with error message.

**Solution:**
1. Check that dependencies are installed: `pip install -r requirements.txt`
2. Verify Python version: Python 3.9+ required
3. Check for port conflicts if using remote control features

### Dashboard not updating

**Issue:** Dashboard appears frozen.

**Solution:**
1. Try reducing update interval: `--interval 0.5`
2. Check terminal size (minimum 80x24 recommended)
3. Restart dashboard

### Events not showing

**Issue:** Events panel is empty.

**Solution:**
1. Ensure agents are running: `python agent_orchestrator_cli.py status`
2. Generate activity by analyzing code or logs
3. Events are ephemeral - recent events may have scrolled off

## Best Practices

1. **Use Dashboard for Active Development**
   - Keep dashboard running during development
   - Provides real-time feedback
   - Easy to spot issues as they occur

2. **Use CLI for Automation**
   - Integrate CLI commands into build scripts
   - Automate agent control in CI/CD
   - Script complex workflows

3. **Configure Project Early**
   - Set up project config first
   - Helps agents understand context
   - Improves analysis accuracy

4. **Monitor Event Counts**
   - Watch for increasing error counts
   - Track refactoring opportunities
   - Identify trends over time

5. **Stop Agents When Not Needed**
   - Conserves resources
   - Prevents event queue buildup
   - Clean slate for next session

## Next Steps

- Review [PHASE3_GUIDE.md](../PHASE3_GUIDE.md) for agent details
- Try the demo: `python examples/phase3_orchestrator_demo.py`
- Integrate into your workflow
- Customize agent thresholds and settings

## Support

For issues or questions:
- Check [TROUBLESHOOTING.md](../guides/TROUBLESHOOTING.md)
- Review agent logs
- Open an issue on GitHub
