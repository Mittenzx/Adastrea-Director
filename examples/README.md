# Adastrea Director - Examples

This directory contains example scripts demonstrating various features of Adastrea Director.

## Available Examples

### Blueprint Creation
- **`blueprint_creation_demo.py`** - Demonstrates creating Blueprints in Unreal Engine
  - Basic Actor blueprints
  - Character blueprints
  - Multiple blueprints at once
  - Usage: `python examples/blueprint_creation_demo.py`

### Blueprint Graphs (Experimental)
- **`blueprint_graph_demo.py`** - Explores blueprint graph manipulation (visual scripting)
  - Shows experimental API for adding nodes and connections
  - Demonstrates alternative approaches (templates, scripts)
  - Explains C++ plugin extension requirements
  - Usage: `python examples/blueprint_graph_demo.py`
  - Note: Full graph manipulation requires C++ plugin - see `BLUEPRINT_GRAPHS_IMPLEMENTATION.md`

### Phase 2 Examples
- **`phase2_example.py`** - Planning and goal decomposition features
- **`cost_tracking_example.py`** - Cost tracking and monitoring

### Phase 3 Examples
- **`phase3_orchestrator_demo.py`** - Autonomous agent orchestration
- **`performance_agent_ue_integration.py`** - Performance profiling agent
- **`bug_detection_agent_ue_integration.py`** - Bug detection agent
- **`code_quality_agent_ue_integration.py`** - Code quality monitoring

### UE Integration
- **`ue_python_api_demo.py`** - Direct Unreal Engine Python API usage
- **`remote_control_demo.py`** - Remote Control API integration
- **`test_agent_example.py`** - Test agent example

## Prerequisites

Most examples require:
- Python 3.9 or higher
- Dependencies installed: `pip install -r requirements.txt`

Examples that interact with Unreal Engine require:
- Unreal Engine Editor running
- Python Editor Script Plugin enabled
- Remote Execution enabled in Project Settings

## Running Examples

```bash
# From the Adastrea-Director root directory
python examples/<example_name>.py
```

For Unreal Engine integration examples, make sure UE is running first:

```bash
# 1. Start Unreal Engine Editor
# 2. Enable Python Plugin (Edit → Plugins → Python Editor Script Plugin)
# 3. Enable Remote Execution (Edit → Project Settings → Python → Enable Remote Execution)
# 4. Run the example
python examples/blueprint_creation_demo.py
```

## Learn More

For detailed documentation, see the [Adastrea Director Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki).
