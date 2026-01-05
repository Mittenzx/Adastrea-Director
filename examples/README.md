# Adastrea Director - Examples

This directory contains example scripts demonstrating various features of Adastrea Director.

## 📝 Integration Status Note

The `remote_control_demo.py` example demonstrates the **Remote Control API client**, which is a **standalone module** that is now **fully integrated** with the VSCode extension (210+ commands) but **not yet integrated** with gui_director.py.

For integration status and how to integrate with gui_director, see:
- **[REMOTE_CONTROL_INTEGRATION_STATUS.md](../REMOTE_CONTROL_INTEGRATION_STATUS.md)** - Complete integration status
- **[VSCODE_COMMANDS_REFERENCE.md](../VSCODE_COMMANDS_REFERENCE.md)** - VSCode command reference
- **[REMOTE_CONTROL_QUICK_INTEGRATION.md](../REMOTE_CONTROL_QUICK_INTEGRATION.md)** - 5-minute GUI integration guide

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

### Planning Examples
- **`planning_example.py`** - Planning and goal decomposition features
- **`cost_tracking_example.py`** - Cost tracking and monitoring

### Phase 3 Examples
- **`phase3_orchestrator_demo.py`** - Autonomous agent orchestration
- **`performance_agent_ue_integration.py`** - Performance profiling agent
- **`bug_detection_agent_ue_integration.py`** - Bug detection agent
- **`code_quality_agent_ue_integration.py`** - Code quality monitoring

### UE Integration
- **`ue_python_api_demo.py`** - Direct Unreal Engine Python API usage
- **`python_research_demo.py`** - **NEW!** Complete examples for content generation and validation
  - Procedural environment generation (grids, circles, scatter)
  - Material instance library creation
  - Asset validation workflows
  - Batch processing operations
  - 8 comprehensive examples
- **`remote_control_demo.py`** - Remote Control API integration
- **`test_agent_example.py`** - Test agent example

## New Python Utilities (Research Results)

The following utility modules are available for use within Unreal Engine's Python environment:

### Content Generation (`ue_content_generation.py`)
- **ProceduralEnvironmentGenerator**: Create procedural layouts
  - Grid-based actor placement
  - Circular arrangements
  - Random scattering with variation
- **MaterialSystemAutomation**: Automated material instance creation
  - Single instance creation
  - Material library generation
  - Parameter configuration
- **BlueprintTemplateSystem**: Blueprint creation from templates
- **batch_spawn_actors**: Spawn multiple actors with custom configurations

### Content Validation (`ue_content_validation.py`)
- **TextureValidator**: Validate texture assets
  - Naming conventions
  - Dimension requirements (power of 2)
  - Size limits
- **MeshValidator**: Validate static mesh assets
  - Triangle count limits
  - LOD requirements
  - Collision setup
- **MaterialValidator**: Validate material assets
  - Naming conventions
  - Hierarchy validation
- **batch_validate_assets**: Validate multiple assets at once
- **validate_folder**: Validate all assets in a folder
- **generate_validation_report**: Generate validation reports

### Batch Processing (`ue_batch_processing.py`)
- **AssetBatchProcessor**: Batch operations on assets
  - Rename, move, duplicate, delete assets
- **LevelBatchOperations**: Batch operations on actors
  - Replace actor classes
  - Transform actors with filters
- **batch_generate_lods**: Generate LODs for multiple meshes
- **batch_optimize_textures**: Optimize multiple textures

For complete documentation, see [PYTHON_RESEARCH_UE427.md](../Documentation/research/PYTHON_RESEARCH_UE427.md)

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
