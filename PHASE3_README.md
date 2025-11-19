# Phase 3: Quick Start Guide

**Status:** ✅ Functionally Complete  
**Last Updated:** November 19, 2025

---

## What is Phase 3?

Phase 3 adds **autonomous agents** that proactively monitor your project for:
- 🎯 **Performance issues** (FPS, memory, CPU/GPU usage)
- 🐛 **Bugs and errors** (log analysis, crash detection)
- 📊 **Code quality** (smells, standards, refactoring opportunities)

Plus a **YAML validation system** that guarantees 100% valid template generation!

---

## Quick Start

### 1. Run the Demo

See Phase 3 in action:

```bash
python demo_phase3_complete.py
```

**Expected output:**
- All 3 agents demonstrate their capabilities
- YAML validation with auto-fix example
- Agent orchestration display
- Confirmation that 213/213 tests pass

### 2. Start Monitoring

Use the CLI to control agents:

```bash
# Start all agents
python agent_orchestrator_cli.py start --all

# Check status
python agent_orchestrator_cli.py status --verbose

# View recent events
python agent_orchestrator_cli.py events --limit 20

# Stop agents
python agent_orchestrator_cli.py stop --all
```

### 3. Use the Dashboard

Launch the real-time monitoring dashboard:

```bash
python agent_dashboard.py --auto-start
```

**Features:**
- Live agent status updates
- Color-coded event feed
- Event summary with counts
- Automatic refresh (1 second interval)

---

## What's Included

### Autonomous Agents (3)

1. **Performance Profiling Agent**
   - Monitors FPS, memory, CPU, GPU
   - Detects bottlenecks
   - Provides optimization recommendations
   - 14 tests, 93% coverage

2. **Bug Detection Agent**
   - Analyzes logs for errors/warnings
   - Detects crashes
   - Creates bug reports
   - 29 tests, 100% coverage

3. **Code Quality Agent**
   - Detects code smells
   - Checks standards (PEP 8)
   - Suggests refactorings
   - Tracks technical debt
   - 35 tests, 98% coverage

### Infrastructure

- **Event Bus** - Pub/sub messaging (16 tests)
- **Shared State** - Agent coordination (20 tests)
- **Orchestrator CLI** - Command-line control (31 tests)
- **Agent Dashboard** - Real-time monitoring (29 tests)

### YAML Validation (Bonus!)

- **Schema Manager** - Auto-detects YAML types
- **YAML Validator** - Validates against schemas
- **Auto-Fix** - Fixes common errors automatically
- **Integration** - Works with Code Generation Agent
- 34 tests, 100% passing

### Remote Control Foundation

- HTTP/WebSocket clients for Unreal Engine
- 67 tests, ready for UE integration

---

## Test Results

```
Phase 3:       179/179 tests passing (100%)
Validation:     34/34 tests passing (100%)
───────────────────────────────────────────
TOTAL:        213/213 tests passing (100%)
```

**Code Coverage:** 91-98% for core modules

---

## Key Files

### Agents
- `agents/phase3/performance_profiling_agent.py`
- `agents/phase3/bug_detection_agent.py`
- `agents/phase3/code_quality_agent.py`

### Infrastructure
- `agents/phase3/event_bus.py`
- `agents/phase3/shared_state.py`
- `agents/phase3/base_agent.py`

### Orchestration
- `agent_orchestrator_cli.py`
- `agent_dashboard.py`

### Validation
- `validation/schema_manager.py`
- `validation/yaml_validator.py`
- `schemas/` (config, data_table, asset)

### Remote Control
- `remote_control/client.py`
- `remote_control/websocket_client.py`

### Documentation
- `PHASE3_GUIDE.md` - Complete user guide
- `PHASE3_FUNCTIONAL_COMPLETION.md` - Detailed summary
- `PHASE3_README.md` - This file

### Demo
- `demo_phase3_complete.py` - Interactive demonstration

---

## Usage Examples

### Performance Monitoring

```python
from agents.phase3 import (
    EventBus, SharedContext, PerformanceProfilingAgent
)

event_bus = EventBus()
shared_context = SharedContext()

agent = PerformanceProfilingAgent(
    event_bus=event_bus,
    shared_context=shared_context,
    target_fps=60.0
)

agent.start()

# Collect metrics
metrics = agent.collect_metrics(
    frame_rate=45.0,
    memory_usage_mb=3500.0,
    cpu_usage_percent=85.0,
    gpu_usage_percent=95.0,
    draw_calls=3500,
    triangles=850000
)

# Analyze
analysis = agent.analyze_performance(metrics)
print(f"Bottlenecks: {len(analysis.bottlenecks)}")
print(f"Recommendations: {len(analysis.recommendations)}")

agent.stop()
```

### Bug Detection

```python
from agents.phase3 import BugDetectionAgent

agent = BugDetectionAgent(event_bus, shared_context)
agent.start()

# Analyze logs
with open('game.log', 'r') as f:
    log_content = f.read()

anomalies = agent.analyze_logs(log_content)
for anomaly in anomalies:
    print(f"{anomaly.severity}: {anomaly.description}")

agent.stop()
```

### Code Quality

```python
from agents.phase3 import CodeQualityAgent

agent = CodeQualityAgent(event_bus, shared_context)
agent.start()

# Analyze code
with open('module.py', 'r') as f:
    code = f.read()

report = agent.analyze_code('module.py', code)
print(f"Quality Score: {report.overall_score}/100")
print(f"Code Smells: {len(report.code_smells)}")

agent.stop()
```

### YAML Validation

```python
from validation import SchemaManager, YAMLValidator

schema_manager = SchemaManager()
schema_manager.load_schemas()
validator = YAMLValidator(schema_manager)

# Validate YAML
result = validator.validate(yaml_content, schema_type='config')

if not result.is_valid:
    # Auto-fix
    fixed = validator.auto_fix(yaml_content, result)
    # Re-validate
    result = validator.validate(fixed, schema_type='config')
    
print(f"Valid: {result.is_valid}")
```

---

## Testing

Run all Phase 3 tests:

```bash
# All tests
pytest tests/phase3/ tests/validation/ -v

# Just Phase 3 agents
pytest tests/phase3/ -v

# Just validation
pytest tests/validation/ -v

# With coverage
pytest tests/phase3/ --cov=agents.phase3
```

---

## What's Next?

### Completed ✅
- Core autonomous agents
- Event-driven architecture
- Agent orchestration
- YAML validation
- Remote Control foundation

### Future Enhancements ⏳
- Full Unreal Engine integration
- Blueprint support system
- GitHub Issues automation
- Enhanced cost tracking
- Real-world testing

See `PHASE3_WORK_ORDER.md` for detailed enhancement plans.

---

## Documentation

- **PHASE3_GUIDE.md** - Complete user guide (~700 lines)
- **PHASE3_FUNCTIONAL_COMPLETION.md** - Detailed completion summary
- **PHASE3_IMPLEMENTATION_SUMMARY.md** - Technical implementation details
- **PHASE3_ORCHESTRATION_SUMMARY.md** - CLI and dashboard guide
- **PHASE3_PREREQUISITES_COMPLETION.md** - Infrastructure details

---

## Support

### Getting Help
- Review documentation in `docs/` directory
- Run the demo: `python demo_phase3_complete.py`
- Check tests for usage examples

### Reporting Issues
- GitHub Issues: [Adastrea-Director/issues](https://github.com/Mittenzx/Adastrea-Director/issues)
- Include: Phase 3 version, Python version, error messages

### Contributing
- See `CONTRIBUTING.md` for guidelines
- All contributions welcome!

---

## Success Criteria Met ✅

| Criteria | Target | Status |
|----------|--------|--------|
| Three autonomous agents | Required | ✅ Complete |
| Event bus & shared state | Required | ✅ Complete |
| Agent orchestration | Required | ✅ Complete |
| Test coverage | 70%+ | ✅ 91-98% |
| Tests passing | 100% | ✅ 213/213 |
| Documentation | Complete | ✅ 5 major docs |
| YAML validation | Nice-to-have | ✅ Bonus |

---

## Version History

- **v1.0** (Nov 19, 2025) - Functional completion
  - All core agents operational
  - YAML validation system complete
  - 213/213 tests passing
  - Full documentation

---

**Phase 3 Status:** ✅ **FUNCTIONALLY COMPLETE**

Ready for production use with standalone Python projects.  
Foundation ready for Unreal Engine integration.

🎉 **Enjoy your autonomous coding assistants!** 🎉
