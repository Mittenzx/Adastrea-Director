# Remote Control API Implementation Plan for Adastrea Director

**Date Created:** 2025-11-12  
**Status:** Planning Phase  
**Target Phase:** Phase 3 (Autonomous Agents)  
**Dependencies:** Phase 2 completion ✅

---

## Executive Summary

This document provides a comprehensive implementation plan for integrating Unreal Engine's Remote Control API into Adastrea Director. The integration will transform the Director from an advisory system into an **active development partner** capable of directly interacting with, testing, and modifying Unreal Engine projects in real-time.

### Key Objectives

1. **Enable Autonomous Agent Actions**: Allow agents to execute changes in Unreal Engine projects
2. **Automate Testing**: Implement automated playtesting and validation
3. **Real-time Monitoring**: Provide performance profiling and bug detection
4. **Asset Management**: Automate asset operations and optimizations
5. **Version Control Integration**: Track and manage agent-made changes

### Strategic Value

- **Phase 2 (Current)**: Remote Control-aware planning and task generation
- **Phase 3 (Target)**: Autonomous agents that can execute and validate changes
- **Phase 4 (Future)**: Creative partnership with advanced automation

---

## Table of Contents

1. [Background & Context](#background--context)
2. [Architecture Design](#architecture-design)
3. [Implementation Phases](#implementation-phases)
4. [Technical Specifications](#technical-specifications)
5. [Agent Enhancement Details](#agent-enhancement-details)
6. [Version Control Integration](#version-control-integration)
7. [Security & Safety](#security--safety)
8. [Testing Strategy](#testing-strategy)
9. [Documentation Requirements](#documentation-requirements)
10. [Success Criteria](#success-criteria)

---

## Background & Context

### Current State Analysis

**Completed (Phase 1 & 2):**
- ✅ Document ingestion and RAG system
- ✅ Goal analysis and task decomposition
- ✅ Planning CLI and GUI interfaces
- ✅ Game repository ingestion (`ingest_game_repo.py`)

**Current Limitations:**
- ❌ Agents cannot execute or test implementations
- ❌ No real-time interaction with Unreal Engine
- ❌ Manual validation required for all suggestions
- ❌ No automated testing capabilities
- ❌ Cannot monitor runtime performance

### What Remote Control API Enables

According to the comprehensive Unreal Engine Editor Implementation Guide and existing REMOTE_CONTROL_API.md documentation:

**Core Capabilities:**
1. **Property Manipulation** - Read/write Blueprint-exposed properties
2. **Function Execution** - Call Blueprint functions remotely
3. **Asset Management** - Create/modify Data Assets programmatically
4. **Scene Automation** - Spawn and manipulate actors
5. **Console Commands** - Execute debug and profiling commands
6. **Real-time Monitoring** - WebSocket-based event streaming

**Agent Transformation:**
- **Performance Profiling Agent**: Advisory → Active profiling with real data
- **Bug Detection Agent**: Code review → Automated testing & detection
- **Code Quality Agent**: Static analysis → Runtime validation
- **Asset Management Agent**: NEW - Full automation capability
- **Testing Automation Agent**: NEW - Complete test execution

### Hybrid Approach Philosophy

The guide emphasizes a **hybrid approach** distinguishing between:

🧑 **Manual Editor Work** (Human Required):
- Initial Blueprint logic creation
- Visual level design and artistic composition
- UI/UX design and widget layout
- Material artistic design
- Creative decision-making

🤖 **API Automation** (Remote Control):
- Modifying Data Asset properties
- Triggering Blueprint functions
- Batch updating parameters
- Spawning/manipulating actors
- Automated testing and validation

🔀 **Hybrid Tasks** (Both):
- Data Asset creation (manual design, automated population)
- Blueprint implementation (manual logic, automated testing)
- Scene setup (manual composition, procedural population)

---

## Architecture Design

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Adastrea Director (Python)                  │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Agent Orchestration Layer                │    │
│  │  - Goal Analysis Agent                             │    │
│  │  - Task Decomposition Agent                        │    │
│  │  - Planning Agent                                  │    │
│  └────────────┬───────────────────────────────────────┘    │
│               │                                             │
│  ┌────────────▼───────────────────────────────────────┐    │
│  │        Remote Control Client Layer                 │    │
│  │  - UnrealRemoteControlClient                       │    │
│  │  - Connection Management                           │    │
│  │  - Request/Response Handling                       │    │
│  │  - WebSocket Event Streaming                       │    │
│  └────────────┬───────────────────────────────────────┘    │
│               │                                             │
│  ┌────────────▼───────────────────────────────────────┐    │
│  │        Enhanced Agent Layer (Phase 3)              │    │
│  │  - Performance Profiling Agent                     │    │
│  │  - Bug Detection Agent                             │    │
│  │  - Code Quality Agent                              │    │
│  │  - Asset Management Agent (NEW)                    │    │
│  │  - Testing Automation Agent (NEW)                  │    │
│  └────────────┬───────────────────────────────────────┘    │
│               │                                             │
│  ┌────────────▼───────────────────────────────────────┐    │
│  │        Version Control Integration                 │    │
│  │  - VersionControlAgent                             │    │
│  │  - RepositorySyncManager                           │    │
│  │  - ConflictResolver                                │    │
│  │  - PullRequestManager                              │    │
│  └────────────┬───────────────────────────────────────┘    │
│               │ HTTP/WebSocket                             │
└───────────────┼────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│              Unreal Engine Remote Control API                │
│  ┌──────────────────────────────────────────────────┐       │
│  │  - Property Read/Write                           │       │
│  │  - Function Calls                                │       │
│  │  - Blueprint Events                              │       │
│  │  - Console Commands                              │       │
│  │  - Asset Operations                              │       │
│  │  - Remote Control Presets                        │       │
│  └──────────────┬───────────────────────────────────┘       │
│                 │                                            │
└─────────────────┼────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Unreal Engine 5.x Project                       │
│              (Editor or Packaged Game)                       │
└─────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. UnrealRemoteControlClient (Core Client)

```python
class UnrealRemoteControlClient:
    """
    Python client for Unreal Engine Remote Control API.
    Provides high-level interface for interacting with UE projects.
    """
    
    def __init__(self, host: str = "localhost", port: int = 30010)
    
    # Property Operations
    def get_property(self, object_path: str, property_name: str) -> Any
    def set_property(self, object_path: str, property_name: str, value: Any) -> bool
    def batch_set_properties(self, updates: List[PropertyUpdate]) -> BatchResult
    
    # Function Operations
    def call_function(self, object_path: str, function_name: str, 
                     parameters: Dict[str, Any] = None) -> Dict[str, Any]
    def call_blueprint_event(self, blueprint_path: str, event_name: str) -> bool
    
    # Console Commands
    def execute_command(self, command: str) -> str
    def execute_commands_batch(self, commands: List[str]) -> List[str]
    
    # Asset Operations
    def load_asset(self, asset_path: str) -> AssetInfo
    def save_asset(self, asset_path: str) -> bool
    def list_assets(self, path: str, asset_type: str = None) -> List[AssetInfo]
    
    # Actor Operations
    def spawn_actor(self, actor_class: str, transform: Transform) -> str
    def destroy_actor(self, actor_path: str) -> bool
    def get_actor_property(self, actor_path: str, property_name: str) -> Any
    
    # Level Operations
    def load_level(self, level_path: str) -> bool
    def save_level(self) -> bool
    def get_current_level(self) -> str
    
    # Play-in-Editor Operations
    def start_play_in_editor(self, mode: PIEMode = PIEMode.SELECTED_VIEWPORT) -> bool
    def stop_play_in_editor(self) -> bool
    def pause_play_in_editor(self) -> bool
    
    # WebSocket Operations
    def subscribe_to_property(self, object_path: str, property_name: str, 
                             callback: Callable) -> str
    def unsubscribe(self, subscription_id: str) -> bool
    
    # Preset Operations
    def list_presets(self) -> List[PresetInfo]
    def load_preset(self, preset_name: str) -> Preset
    def execute_preset_function(self, preset_name: str, function_name: str) -> Any
    
    # Health & Status
    def health_check(self) -> bool
    def get_server_info(self) -> ServerInfo
```

#### 2. RemoteControlAgent (Base Class)

```python
class RemoteControlAgent:
    """
    Base class for agents that interact with Unreal Engine via Remote Control API.
    Provides common functionality for all Remote Control-enabled agents.
    """
    
    def __init__(self, remote_control_client: UnrealRemoteControlClient,
                 version_control: VersionControlAgent = None)
    
    # Agent Lifecycle
    def initialize(self) -> bool
    def shutdown(self) -> bool
    
    # Action Execution with Version Control
    def execute_action(self, action: AgentAction) -> ActionResult
    def validate_action(self, action: AgentAction) -> ValidationResult
    def rollback_action(self, action_id: str) -> bool
    
    # Monitoring & Logging
    def log_action(self, action: AgentAction, result: ActionResult) -> None
    def get_action_history(self) -> List[ActionResult]
    
    # Error Handling
    def handle_error(self, error: Exception) -> ErrorResolution
    def retry_action(self, action: AgentAction, max_retries: int = 3) -> ActionResult
```

#### 3. VersionControlAgent

```python
class VersionControlAgent:
    """
    Manages version control for agent-made changes via Remote Control API.
    Ensures all changes are tracked, reversible, and reviewable.
    """
    
    def __init__(self, repo_path: str)
    
    # Change Management
    def before_agent_action(self, agent_name: str, action: str) -> str
    def after_agent_action(self, agent_name: str, branch_name: str, 
                          changes: List[str]) -> CommitInfo
    def rollback_to_main(self) -> bool
    
    # Synchronization
    def sync_repository(self) -> SyncStatus
    def check_for_conflicts(self) -> List[str]
    def resolve_conflicts(self, strategy: ConflictStrategy) -> bool
    
    # PR Management
    def create_pull_request(self, branch_name: str, agent_name: str,
                           changes: List[str]) -> PullRequest
```

---

## Implementation Phases

### Phase 3.1: Foundation (Weeks 1-4)

**Goal:** Establish basic Remote Control API integration and testing infrastructure.

#### Week 1-2: Core Client Development

**Tasks:**
1. ✅ Create `remote_control/` directory structure
2. ✅ Implement `UnrealRemoteControlClient` base class
3. ✅ Add HTTP request/response handling
4. ✅ Implement property get/set operations
5. ✅ Add function call operations
6. ✅ Create error handling and retry logic
7. ✅ Write unit tests for client operations

**Deliverables:**
- `remote_control/client.py` - Core client implementation
- `remote_control/models.py` - Data models for API objects
- `remote_control/exceptions.py` - Custom exceptions
- `tests/test_remote_control_client.py` - Unit tests

**Dependencies:**
```python
# requirements.txt additions
requests>=2.31.0
websocket-client>=1.6.0
websockets>=12.0,<13.0.0  # For async WebSocket support
```

#### Week 3: WebSocket Integration

**Tasks:**
1. ✅ Implement WebSocket connection management
2. ✅ Add property subscription system
3. ✅ Create event streaming handler
4. ✅ Implement reconnection logic
5. ✅ Add WebSocket unit tests

**Deliverables:**
- `remote_control/websocket_client.py` - WebSocket client
- `remote_control/event_handler.py` - Event processing
- `tests/test_websocket_client.py` - WebSocket tests

#### Week 4: Version Control Integration

**Tasks:**
1. ✅ Implement `VersionControlAgent` class
2. ✅ Add git repository synchronization
3. ✅ Create branch management system
4. ✅ Implement commit automation
5. ✅ Add PR creation (GitHub API)
6. ✅ Write version control tests

**Deliverables:**
- `version_control/agent.py` - Version control agent
- `version_control/sync_manager.py` - Repository sync
- `version_control/pr_manager.py` - Pull request automation
- `tests/test_version_control.py` - Version control tests

**Configuration File:** `config/remote_control_config.yaml`
```yaml
remote_control:
  default_host: "localhost"
  default_port: 30010
  timeout_seconds: 30
  retry_attempts: 3
  retry_delay_seconds: 5
  
websocket:
  enable: true
  reconnect_attempts: 10
  reconnect_delay_seconds: 2
  
version_control:
  auto_sync: true
  sync_interval_minutes: 15
  create_feature_branches: true
  branch_prefix: "agent"
  auto_create_pr: true
  require_approval: true
```

### Phase 3.2: Agent Enhancement (Weeks 5-10)

**Goal:** Enhance existing agents with Remote Control capabilities and create new agents.

#### Week 5-6: Performance Profiling Agent Enhancement

**Tasks:**
1. ✅ Extend `PerformanceProfilingAgent` with Remote Control
2. ✅ Implement console command execution (`stat fps`, `stat gpu`)
3. ✅ Add PIE automation (start/stop game sessions)
4. ✅ Create performance metric collection
5. ✅ Implement automated benchmarking
6. ✅ Add performance report generation

**Deliverables:**
- `agents/performance_profiling_agent.py` - Enhanced agent
- `agents/performance_metrics.py` - Metrics collection
- `tests/test_performance_profiling.py` - Agent tests

**Example Workflow:**
```python
class EnhancedPerformanceProfilingAgent(RemoteControlAgent):
    def profile_level(self, level_name: str) -> PerformanceReport:
        # Sync repository before action
        self.version_control.sync_repository()
        
        # Load level via Remote Control
        self.remote_control.load_level(level_name)
        
        # Start PIE
        self.remote_control.start_play_in_editor()
        
        # Collect metrics
        fps_data = self.remote_control.execute_command("stat fps")
        gpu_data = self.remote_control.execute_command("stat gpu")
        memory_data = self.remote_control.execute_command("stat memory")
        
        # Stop PIE
        self.remote_control.stop_play_in_editor()
        
        # Analyze and report
        report = self.analyze_metrics(fps_data, gpu_data, memory_data)
        
        # Log action
        self.log_action("profile_level", report)
        
        return report
```

#### Week 7-8: Bug Detection Agent Enhancement

**Tasks:**
1. ✅ Extend `BugDetectionAgent` with automated playtesting
2. ✅ Implement test scenario execution
3. ✅ Add real-time error monitoring
4. ✅ Create reproduction step generation
5. ✅ Implement regression testing
6. ✅ Add bug report automation

**Deliverables:**
- `agents/bug_detection_agent.py` - Enhanced agent
- `agents/test_scenarios.py` - Test scenario definitions
- `tests/test_bug_detection.py` - Agent tests

#### Week 9: Asset Management Agent (NEW)

**Tasks:**
1. ✅ Create `AssetManagementAgent` class
2. ✅ Implement asset listing and querying
3. ✅ Add property batch operations
4. ✅ Create texture optimization workflows
5. ✅ Implement LOD generation
6. ✅ Add asset validation rules

**Deliverables:**
- `agents/asset_management_agent.py` - New agent
- `agents/asset_optimization.py` - Optimization rules
- `tests/test_asset_management.py` - Agent tests

#### Week 10: Testing Automation Agent (NEW)

**Tasks:**
1. ✅ Create `TestAutomationAgent` class
2. ✅ Implement test suite execution
3. ✅ Add test result collection
4. ✅ Create test environment setup
5. ✅ Implement continuous testing loop
6. ✅ Add test report generation

**Deliverables:**
- `agents/test_automation_agent.py` - New agent
- `agents/test_runner.py` - Test execution engine
- `tests/test_automation_agent.py` - Agent tests

### Phase 3.3: Integration & Documentation (Weeks 11-12)

**Goal:** Integrate all components, comprehensive testing, and documentation.

#### Week 11: Integration Testing

**Tasks:**
1. ✅ End-to-end integration tests
2. ✅ Performance testing under load
3. ✅ Error handling validation
4. ✅ Version control workflow testing
5. ✅ Security audit
6. ✅ Bug fixes and optimization

**Deliverables:**
- `tests/integration/` - Integration test suite
- `tests/performance/` - Performance tests
- Bug fix commits and optimizations

#### Week 12: Documentation & Examples

**Tasks:**
1. ✅ Update AGENTS.md with Remote Control capabilities
2. ✅ Create REMOTE_CONTROL_QUICKSTART.md
3. ✅ Write API reference documentation
4. ✅ Create example workflows and tutorials
5. ✅ Update PROJECT_PLAN.md with Phase 3 completion
6. ✅ Record demo videos (optional)

**Deliverables:**
- `REMOTE_CONTROL_QUICKSTART.md` - Quick start guide
- `docs/remote_control_api_reference.md` - API reference
- `examples/remote_control/` - Example scripts
- Updated AGENTS.md and PROJECT_PLAN.md

---

## Technical Specifications

### Directory Structure

```
Adastrea-Director/
├── remote_control/
│   ├── __init__.py
│   ├── client.py                    # Core HTTP client
│   ├── websocket_client.py          # WebSocket client
│   ├── models.py                    # Data models
│   ├── exceptions.py                # Custom exceptions
│   └── event_handler.py             # Event processing
│
├── version_control/
│   ├── __init__.py
│   ├── agent.py                     # Version control agent
│   ├── sync_manager.py              # Repository sync
│   ├── pr_manager.py                # Pull request automation
│   └── conflict_resolver.py         # Conflict resolution
│
├── agents/
│   ├── remote_control_agent.py      # Base class
│   ├── performance_profiling_agent.py
│   ├── bug_detection_agent.py
│   ├── code_quality_agent.py
│   ├── asset_management_agent.py    # NEW
│   └── test_automation_agent.py     # NEW
│
├── config/
│   ├── remote_control_config.yaml   # Remote Control settings
│   └── agent_config.yaml            # Agent configurations
│
├── tests/
│   ├── test_remote_control_client.py
│   ├── test_websocket_client.py
│   ├── test_version_control.py
│   ├── test_agents/
│   │   ├── test_performance_profiling.py
│   │   ├── test_bug_detection.py
│   │   ├── test_asset_management.py
│   │   └── test_test_automation.py
│   ├── integration/
│   │   ├── test_end_to_end.py
│   │   └── test_agent_coordination.py
│   └── performance/
│       └── test_load_performance.py
│
├── examples/
│   └── remote_control/
│       ├── basic_property_update.py
│       ├── automated_profiling.py
│       ├── batch_asset_optimization.py
│       └── continuous_testing.py
│
└── docs/
    ├── REMOTE_CONTROL_QUICKSTART.md
    └── remote_control_api_reference.md
```

### Data Models

```python
# remote_control/models.py

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum

@dataclass
class PropertyUpdate:
    """Represents a property update operation."""
    object_path: str
    property_name: str
    property_value: Any
    generate_transaction: bool = True

@dataclass
class FunctionCall:
    """Represents a function call operation."""
    object_path: str
    function_name: str
    parameters: Dict[str, Any]

@dataclass
class BatchResult:
    """Result of batch operations."""
    successful: List[str]
    failed: List[Dict[str, str]]
    total_count: int
    success_rate: float

@dataclass
class AssetInfo:
    """Information about a Unreal asset."""
    asset_path: str
    asset_name: str
    asset_type: str
    package_name: str
    metadata: Dict[str, Any]

@dataclass
class Transform:
    """3D transformation data."""
    location: Dict[str, float]  # {X, Y, Z}
    rotation: Dict[str, float]  # {Pitch, Yaw, Roll}
    scale: Dict[str, float]     # {X, Y, Z}

class PIEMode(Enum):
    """Play-in-Editor modes."""
    SELECTED_VIEWPORT = "SelectedViewport"
    NEW_WINDOW = "NewWindow"
    STANDALONE = "Standalone"
    SIMULATE = "Simulate"

@dataclass
class ServerInfo:
    """Remote Control server information."""
    version: str
    engine_version: str
    project_name: str
    is_editor: bool
    active_presets: List[str]

@dataclass
class PerformanceMetrics:
    """Performance profiling metrics."""
    fps: float
    frame_time_ms: float
    gpu_time_ms: float
    cpu_time_ms: float
    memory_mb: float
    draw_calls: int
    primitives: int

@dataclass
class AgentAction:
    """Represents an agent action to be executed."""
    agent_name: str
    action_type: str
    action_name: str
    parameters: Dict[str, Any]
    requires_version_control: bool = True
    requires_approval: bool = False

@dataclass
class ActionResult:
    """Result of an agent action."""
    success: bool
    action: AgentAction
    changes_made: List[str]
    commit_info: Optional['CommitInfo']
    pr_info: Optional['PullRequest']
    error_message: Optional[str]
    execution_time_seconds: float

@dataclass
class CommitInfo:
    """Git commit information."""
    commit_hash: str
    branch_name: str
    commit_message: str
    files_changed: List[str]
    timestamp: str

class SyncStatus(Enum):
    """Repository synchronization status."""
    UP_TO_DATE = "up_to_date"
    UPDATED = "updated"
    CONFLICT_DETECTED = "conflict"
    ERROR = "error"

@dataclass
class PullRequest:
    """Pull request information."""
    pr_number: int
    pr_url: str
    title: str
    branch_name: str
    status: str
```

### Configuration Management

```python
# remote_control/config.py

import yaml
from pathlib import Path
from typing import Dict, Any

class RemoteControlConfig:
    """Manages Remote Control API configuration."""
    
    def __init__(self, config_path: str = "config/remote_control_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'remote_control': {
                'default_host': 'localhost',
                'default_port': 30010,
                'timeout_seconds': 30,
                'retry_attempts': 3,
                'retry_delay_seconds': 5
            },
            'websocket': {
                'enable': True,
                'reconnect_attempts': 10,
                'reconnect_delay_seconds': 2
            },
            'version_control': {
                'auto_sync': True,
                'sync_interval_minutes': 15,
                'create_feature_branches': True,
                'branch_prefix': 'agent',
                'auto_create_pr': True,
                'require_approval': True
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path."""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def save(self) -> None:
        """Save current configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
```

---

## Agent Enhancement Details

### 1. Performance Profiling Agent

**Enhanced Capabilities:**
- Execute profiling console commands (`stat fps`, `stat gpu`, `stat memory`, `stat unit`)
- Automate Play-in-Editor sessions for testing
- Collect real-time performance metrics
- Generate performance comparison reports
- Detect performance regressions automatically

**Implementation Snippet:**
```python
class EnhancedPerformanceProfilingAgent(RemoteControlAgent):
    def run_performance_benchmark(self, level_path: str, 
                                  duration_seconds: int = 60) -> PerformanceReport:
        """Run automated performance benchmark on a level."""
        
        # Create feature branch
        branch = self.version_control.before_agent_action(
            "PerformanceProfilingAgent", "benchmark"
        )
        
        try:
            # Load level
            self.remote_control.load_level(level_path)
            
            # Start PIE
            self.remote_control.start_play_in_editor(PIEMode.SELECTED_VIEWPORT)
            
            # Collect metrics over duration
            metrics = []
            start_time = time.time()
            
            while time.time() - start_time < duration_seconds:
                # Execute profiling commands
                fps = self._parse_fps(self.remote_control.execute_command("stat fps"))
                gpu = self._parse_gpu(self.remote_control.execute_command("stat gpu"))
                memory = self._parse_memory(self.remote_control.execute_command("stat memory"))
                
                metrics.append(PerformanceMetrics(
                    fps=fps,
                    gpu_time_ms=gpu,
                    memory_mb=memory,
                    timestamp=time.time()
                ))
                
                time.sleep(1)
            
            # Stop PIE
            self.remote_control.stop_play_in_editor()
            
            # Generate report
            report = self._generate_report(metrics)
            
            # Commit results
            self.version_control.after_agent_action(
                "PerformanceProfilingAgent",
                branch,
                [f"performance_report_{level_path}.json"]
            )
            
            return report
            
        except Exception as e:
            self.version_control.rollback_to_main()
            raise
```

### 2. Bug Detection Agent

**Enhanced Capabilities:**
- Execute automated playtest scenarios
- Monitor for crashes and errors in real-time
- Generate bug reproduction steps automatically
- Run regression tests on bug fixes
- Create detailed bug reports with game state

**Implementation Snippet:**
```python
class EnhancedBugDetectionAgent(RemoteControlAgent):
    def run_playtest_scenario(self, scenario: TestScenario) -> BugReport:
        """Execute automated playtest scenario and detect bugs."""
        
        branch = self.version_control.before_agent_action(
            "BugDetectionAgent", f"playtest_{scenario.name}"
        )
        
        try:
            # Load test level
            self.remote_control.load_level(scenario.level_path)
            
            # Spawn test controller
            controller = self.remote_control.spawn_actor(
                "BP_TestController",
                Transform(location={'X': 0, 'Y': 0, 'Z': 0})
            )
            
            # Start PIE
            self.remote_control.start_play_in_editor()
            
            # Execute test actions
            bugs_found = []
            for action in scenario.actions:
                try:
                    result = self.remote_control.call_function(
                        controller,
                        action.function_name,
                        action.parameters
                    )
                    
                    # Check for errors or unexpected states
                    if self._is_error_state(result):
                        bugs_found.append(self._create_bug_report(action, result))
                        
                except Exception as e:
                    bugs_found.append(self._create_bug_report(action, str(e)))
            
            # Stop PIE
            self.remote_control.stop_play_in_editor()
            
            # Generate bug report
            report = BugReport(
                scenario=scenario.name,
                bugs_found=bugs_found,
                total_actions=len(scenario.actions),
                success_rate=1.0 - (len(bugs_found) / len(scenario.actions))
            )
            
            # Save report and commit
            self._save_bug_report(report)
            self.version_control.after_agent_action(
                "BugDetectionAgent",
                branch,
                [f"bug_report_{scenario.name}.json"]
            )
            
            return report
            
        except Exception as e:
            self.version_control.rollback_to_main()
            raise
```

### 3. Asset Management Agent (NEW)

**Capabilities:**
- Batch update Data Asset properties
- Optimize texture settings automatically
- Generate LODs for meshes
- Validate asset naming conventions
- Clean up unused assets

**Implementation Snippet:**
```python
class AssetManagementAgent(RemoteControlAgent):
    def optimize_textures(self, asset_path: str) -> OptimizationReport:
        """Optimize all textures in the specified path."""
        
        branch = self.version_control.before_agent_action(
            "AssetManagementAgent", "optimize_textures"
        )
        
        try:
            # List all textures
            textures = self.remote_control.list_assets(
                asset_path,
                asset_type="Texture2D"
            )
            
            optimized = []
            for texture in textures:
                # Get current properties
                size = self.remote_control.get_property(
                    texture.asset_path,
                    "Size"
                )
                compression = self.remote_control.get_property(
                    texture.asset_path,
                    "CompressionSettings"
                )
                
                # Apply optimizations if needed
                if size['X'] > 4096 or size['Y'] > 4096:
                    self.remote_control.set_property(
                        texture.asset_path,
                        "MaxTextureSize",
                        4096
                    )
                    optimized.append(texture.asset_path)
                
                # Ensure proper compression
                if compression != "TC_Default":
                    self.remote_control.set_property(
                        texture.asset_path,
                        "CompressionSettings",
                        "TC_Default"
                    )
                    optimized.append(texture.asset_path)
                
                # Save asset
                self.remote_control.save_asset(texture.asset_path)
            
            # Generate report
            report = OptimizationReport(
                total_textures=len(textures),
                optimized_count=len(set(optimized)),
                optimized_assets=list(set(optimized))
            )
            
            # Commit changes
            self.version_control.after_agent_action(
                "AssetManagementAgent",
                branch,
                optimized
            )
            
            return report
            
        except Exception as e:
            self.version_control.rollback_to_main()
            raise
```

### 4. Testing Automation Agent (NEW)

**Capabilities:**
- Execute automated test suites
- Validate gameplay mechanics
- Run integration tests
- Generate test reports
- Continuous testing loops

**Implementation Snippet:**
```python
class TestAutomationAgent(RemoteControlAgent):
    def run_test_suite(self, suite_name: str) -> TestResults:
        """Execute a complete test suite."""
        
        branch = self.version_control.before_agent_action(
            "TestAutomationAgent", f"run_tests_{suite_name}"
        )
        
        try:
            # Load test suite
            test_cases = self._load_test_suite(suite_name)
            results = []
            
            for test_case in test_cases:
                # Setup test environment
                self.remote_control.load_level(test_case.level)
                
                # Start PIE
                self.remote_control.start_play_in_editor()
                
                # Execute test
                try:
                    result = self.remote_control.call_function(
                        "BP_TestRunner",
                        "ExecuteTest",
                        {"TestName": test_case.name}
                    )
                    
                    results.append(TestResult(
                        test_name=test_case.name,
                        passed=result.get('Success', False),
                        duration=result.get('Duration', 0),
                        message=result.get('Message', '')
                    ))
                    
                except Exception as e:
                    results.append(TestResult(
                        test_name=test_case.name,
                        passed=False,
                        duration=0,
                        message=str(e)
                    ))
                
                finally:
                    # Stop PIE
                    self.remote_control.stop_play_in_editor()
            
            # Generate test report
            test_results = TestResults(
                suite_name=suite_name,
                total_tests=len(results),
                passed=sum(1 for r in results if r.passed),
                failed=sum(1 for r in results if not r.passed),
                results=results
            )
            
            # Save and commit
            self._save_test_results(test_results)
            self.version_control.after_agent_action(
                "TestAutomationAgent",
                branch,
                [f"test_results_{suite_name}.json"]
            )
            
            return test_results
            
        except Exception as e:
            self.version_control.rollback_to_main()
            raise
```

---

## Version Control Integration

### Workflow Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Action Workflow                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Pre-Action: Sync Repository                             │
│     - Pull latest changes from remote                        │
│     - Check for conflicts                                    │
│     - Ensure working tree is clean                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Create Feature Branch                                    │
│     - Branch name: agent/{agent_name}/{action}/{timestamp}   │
│     - Checkout branch                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Execute Agent Action via Remote Control API             │
│     - Call Unreal Engine functions                           │
│     - Modify properties                                      │
│     - Execute commands                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Validate Changes                                         │
│     - Run tests                                              │
│     - Check for errors                                       │
│     - Verify expected outcomes                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Commit Changes                                           │
│     - Stage modified files                                   │
│     - Create descriptive commit message                      │
│     - Include agent metadata                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Push to Remote (Optional)                                │
│     - Push branch to GitHub                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  7. Create Pull Request                                      │
│     - Generate PR description                                │
│     - Include validation results                             │
│     - Assign reviewers                                       │
│     - Add labels                                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  8. Human Review & Approval                                  │
│     - Review changes                                         │
│     - Request changes if needed                              │
│     - Approve and merge                                      │
└─────────────────────────────────────────────────────────────┘
```

### Commit Message Format

```
[Agent: {agent_name}] {action_summary}

Detailed description:
- Change 1: {description}
- Change 2: {description}
- Change 3: {description}

Validation Results:
- Tests: {PASSED/FAILED}
- Build: {SUCCESS/FAILED}
- Performance: {No regression/Regression detected}

Remote Control API:
- Endpoint: {api_endpoint}
- Operations: {operation_count}
- Duration: {execution_time}

Agent Context:
- Trigger: {trigger_event}
- Parameters: {parameters}
- Version: {agent_version}

Generated by: Adastrea Director v{version}
Timestamp: {iso_timestamp}
```

### Pull Request Template

```markdown
## Automated Changes by Adastrea Director

**Agent:** {agent_name}
**Action:** {action_name}
**Branch:** {branch_name}
**Timestamp:** {timestamp}

### Changes Made

{detailed_change_list}

### Validation Results

- [ ] Tests passed: {test_results}
- [ ] Build successful: {build_status}
- [ ] Performance impact: {performance_status}
- [ ] No regressions detected: {regression_status}

### Remote Control API Operations

- **Endpoints called:** {endpoint_count}
- **Properties modified:** {property_count}
- **Functions executed:** {function_count}
- **Total operations:** {total_operations}

### Review Checklist

- [ ] Changes are as expected
- [ ] No unintended side effects
- [ ] Performance impact is acceptable
- [ ] Documentation updated if needed
- [ ] Tests cover new functionality

### Files Changed

{file_list}

---

*This PR was automatically generated by Adastrea Director.*  
*Review and merge when ready, or request changes.*
```

---

## Security & Safety

### Access Control

1. **Network Security**
   - Remote Control API accessible only on localhost by default
   - Use VPN/secure tunnel for remote access
   - Never expose to public internet

2. **Authentication** (Future Enhancement)
   - API key authentication
   - OAuth integration
   - Role-based access control

3. **Property Whitelisting**
   - Define allowed properties for modification
   - Block critical system properties
   - Require approval for sensitive changes

### Safety Mechanisms

1. **Validation Before Execution**
   ```python
   def validate_action(self, action: AgentAction) -> ValidationResult:
       # Check if action is allowed
       if not self._is_action_allowed(action):
           return ValidationResult(valid=False, reason="Action not whitelisted")
       
       # Check if properties are safe to modify
       if action.action_type == "property_update":
           if not self._is_property_safe(action.parameters['property_name']):
               return ValidationResult(valid=False, reason="Property is protected")
       
       # Check for potential side effects
       side_effects = self._analyze_side_effects(action)
       if side_effects.severity >= Severity.HIGH:
           return ValidationResult(
               valid=False,
               reason=f"High-severity side effects: {side_effects}"
           )
       
       return ValidationResult(valid=True)
   ```

2. **Rollback Capability**
   - Git-based rollback for file changes
   - Property value history tracking
   - Emergency stop functionality

3. **Human Oversight**
   - Require approval for critical operations
   - Notifications for all agent actions
   - Dashboard for monitoring agent activity

4. **Rate Limiting**
   - Limit API calls per second
   - Prevent infinite loops
   - Resource usage monitoring

### Sandboxing Strategy

1. **Test Environment First**
   - All actions tested in isolated environment
   - Validation before production deployment
   - Separate Remote Control instances for dev/prod

2. **Incremental Rollout**
   - Enable features one at a time
   - Monitor for issues before enabling next feature
   - Gradual permission expansion

---

## Testing Strategy

### Unit Tests

**Coverage Target:** 90%+

**Test Categories:**
1. Remote Control Client Operations
2. WebSocket Connection Management
3. Version Control Integration
4. Agent Action Execution
5. Error Handling and Recovery

**Example Test:**
```python
# tests/test_remote_control_client.py

import pytest
from remote_control.client import UnrealRemoteControlClient
from remote_control.exceptions import ConnectionError, APIError

class TestUnrealRemoteControlClient:
    @pytest.fixture
    def client(self):
        return UnrealRemoteControlClient(host="localhost", port=30010)
    
    def test_health_check_success(self, client, mock_server):
        """Test successful health check."""
        mock_server.expect_get("/remote/health").respond(200, {"status": "ok"})
        
        assert client.health_check() == True
    
    def test_health_check_failure(self, client, mock_server):
        """Test health check failure."""
        mock_server.expect_get("/remote/health").respond(500)
        
        assert client.health_check() == False
    
    def test_get_property(self, client, mock_server):
        """Test getting a property value."""
        mock_server.expect_get("/remote/object/property").respond(200, {
            "PropertyValue": 1500.0
        })
        
        value = client.get_property(
            "/Game/DataAssets/Ships/DA_Ship_Fighter.DA_Ship_Fighter",
            "MaxSpeed"
        )
        
        assert value == 1500.0
    
    def test_set_property(self, client, mock_server):
        """Test setting a property value."""
        mock_server.expect_put("/remote/object/property").respond(200)
        
        result = client.set_property(
            "/Game/DataAssets/Ships/DA_Ship_Fighter.DA_Ship_Fighter",
            "MaxSpeed",
            1800.0
        )
        
        assert result == True
    
    def test_call_function(self, client, mock_server):
        """Test calling a Blueprint function."""
        mock_server.expect_put("/remote/object/call").respond(200, {
            "ReturnValue": {"Success": True}
        })
        
        result = client.call_function(
            "/Game/Blueprints/Ships/BP_PlayerShip.BP_PlayerShip_C",
            "SetBoostEnabled",
            {"bEnabled": True}
        )
        
        assert result["ReturnValue"]["Success"] == True
    
    def test_connection_error_retry(self, client, mock_server):
        """Test retry logic on connection error."""
        # First two attempts fail, third succeeds
        mock_server.expect_get("/remote/health").respond(500)
        mock_server.expect_get("/remote/health").respond(500)
        mock_server.expect_get("/remote/health").respond(200, {"status": "ok"})
        
        assert client.health_check() == True
        assert client.retry_count == 2
```

### Integration Tests

**Test Scenarios:**
1. End-to-end agent workflows
2. Version control integration
3. Multi-agent coordination
4. Error recovery and rollback
5. Performance under load

**Example Integration Test:**
```python
# tests/integration/test_agent_workflow.py

import pytest
from agents.performance_profiling_agent import EnhancedPerformanceProfilingAgent
from remote_control.client import UnrealRemoteControlClient
from version_control.agent import VersionControlAgent

class TestAgentWorkflow:
    @pytest.fixture
    def setup_environment(self, tmp_path):
        # Setup test repository
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        
        # Initialize git repo
        # ... setup code ...
        
        return repo_path
    
    def test_performance_profiling_workflow(self, setup_environment):
        """Test complete performance profiling workflow."""
        
        # Initialize components
        remote_control = UnrealRemoteControlClient()
        version_control = VersionControlAgent(setup_environment)
        agent = EnhancedPerformanceProfilingAgent(remote_control, version_control)
        
        # Execute profiling
        report = agent.profile_level("/Game/Maps/TestLevel")
        
        # Verify results
        assert report is not None
        assert report.fps > 0
        assert report.metrics_count > 0
        
        # Verify version control
        assert version_control.has_uncommitted_changes() == False
        assert version_control.current_branch.startswith("agent/")
        
        # Verify PR creation
        pr = version_control.get_latest_pr()
        assert pr is not None
        assert "PerformanceProfilingAgent" in pr.title
```

### Performance Tests

**Metrics to Monitor:**
- API response time
- Agent execution time
- Memory usage
- Concurrent operation handling
- WebSocket message throughput

### Manual Testing Checklist

**Before Release:**
- [ ] Test with real Unreal Engine project
- [ ] Verify all agent workflows
- [ ] Test error scenarios
- [ ] Validate version control integration
- [ ] Check documentation accuracy
- [ ] Test on multiple platforms (Windows, Linux, Mac)
- [ ] Verify security measures
- [ ] Test rollback functionality

---

## Documentation Requirements

### 1. Quick Start Guide

**File:** `REMOTE_CONTROL_QUICKSTART.md`

**Contents:**
- Installation instructions
- Basic configuration
- First Remote Control connection
- Simple examples
- Troubleshooting common issues

### 2. API Reference

**File:** `docs/remote_control_api_reference.md`

**Contents:**
- Complete API documentation
- All classes and methods
- Parameter descriptions
- Return value specifications
- Code examples for each method

### 3. Agent Guide

**Update:** `AGENTS.md`

**Additions:**
- Remote Control capabilities per agent
- New agent descriptions
- Workflow examples
- Best practices

### 4. Configuration Guide

**File:** `docs/configuration_guide.md`

**Contents:**
- Configuration file format
- Available options
- Environment variables
- Security settings
- Performance tuning

### 5. Examples & Tutorials

**Directory:** `examples/remote_control/`

**Files:**
- `01_basic_connection.py` - Connect to UE
- `02_property_operations.py` - Get/set properties
- `03_function_calls.py` - Call Blueprint functions
- `04_automated_profiling.py` - Performance profiling
- `05_batch_operations.py` - Batch asset updates
- `06_continuous_testing.py` - Automated testing loop

---

## Success Criteria

### Phase 3.1 (Foundation)

✅ **Technical:**
- [ ] UnrealRemoteControlClient implements all core operations
- [ ] WebSocket client maintains stable connection
- [ ] Version control integration tracks all changes
- [ ] Error handling covers 95%+ of failure scenarios
- [ ] Unit test coverage >90%

✅ **Functional:**
- [ ] Successfully connect to Unreal Engine Remote Control API
- [ ] Execute property get/set operations
- [ ] Call Blueprint functions
- [ ] Create and manage git branches automatically
- [ ] Generate pull requests with detailed descriptions

### Phase 3.2 (Agent Enhancement)

✅ **Technical:**
- [ ] All agents inherit from RemoteControlAgent base class
- [ ] Agents coordinate with version control system
- [ ] Integration tests pass for all agent workflows
- [ ] Performance benchmarks meet targets

✅ **Functional:**
- [ ] Performance Profiling Agent collects real-time metrics
- [ ] Bug Detection Agent executes automated playtests
- [ ] Asset Management Agent optimizes assets successfully
- [ ] Testing Automation Agent runs complete test suites
- [ ] All agents create proper commit messages and PRs

### Phase 3.3 (Integration & Documentation)

✅ **Technical:**
- [ ] End-to-end integration tests pass
- [ ] No security vulnerabilities detected
- [ ] Performance under load is acceptable
- [ ] All documentation is complete

✅ **Functional:**
- [ ] Agents work together in coordinated workflows
- [ ] Human oversight mechanisms function correctly
- [ ] Rollback capability works as expected
- [ ] Quick start guide enables new users to connect within 10 minutes

### Overall Success Metrics

**Quantitative:**
- Agent action success rate: >95%
- API response time: <500ms average
- WebSocket connection uptime: >99%
- Test coverage: >90%
- Documentation completeness: 100%

**Qualitative:**
- Developer productivity increase
- Reduced manual testing time
- Improved code quality metrics
- Faster bug detection and resolution
- Positive user feedback

---

## Risk Management

### Identified Risks

1. **Unreal Engine Version Compatibility**
   - **Risk:** Remote Control API may change between UE versions
   - **Mitigation:** Test with multiple UE versions, version detection logic
   - **Impact:** Medium | **Probability:** Medium

2. **Network Stability**
   - **Risk:** Unstable connections may interrupt agent operations
   - **Mitigation:** Robust retry logic, connection health monitoring
   - **Impact:** High | **Probability:** Low

3. **Version Control Conflicts**
   - **Risk:** Multiple agents or human changes create merge conflicts
   - **Mitigation:** Branch isolation, conflict detection, human oversight
   - **Impact:** High | **Probability:** Medium

4. **Security Vulnerabilities**
   - **Risk:** Exposed Remote Control API could be exploited
   - **Mitigation:** Localhost-only by default, authentication, whitelisting
   - **Impact:** Critical | **Probability:** Low

5. **Agent Errors Causing Project Corruption**
   - **Risk:** Bugs in agent logic corrupt Unreal Engine project
   - **Mitigation:** Validation before execution, rollback capability, backups
   - **Impact:** Critical | **Probability:** Low

6. **Performance Overhead**
   - **Risk:** Remote Control operations slow down development workflow
   - **Mitigation:** Async operations, rate limiting, performance optimization
   - **Impact:** Medium | **Probability:** Low

---

## Timeline & Milestones

### Month 1: Foundation

**Week 1-2:** Core Client Development
- Complete UnrealRemoteControlClient implementation
- Add comprehensive error handling
- Write unit tests

**Week 3:** WebSocket Integration
- Implement WebSocket client
- Add property subscription system
- Test real-time event streaming

**Week 4:** Version Control Integration
- Complete VersionControlAgent
- Implement branch management
- Add PR automation

**Milestone:** ✅ Basic Remote Control integration functional

### Month 2: Agent Enhancement

**Week 5-6:** Performance Profiling Agent
- Enhance with Remote Control capabilities
- Implement automated benchmarking
- Create performance report generation

**Week 7-8:** Bug Detection Agent
- Add automated playtesting
- Implement error monitoring
- Create bug report automation

**Milestone:** ✅ First two enhanced agents operational

### Month 3: New Agents & Integration

**Week 9:** Asset Management Agent
- Complete new agent implementation
- Add asset optimization workflows
- Test batch operations

**Week 10:** Testing Automation Agent
- Complete test execution engine
- Implement test suite management
- Add continuous testing capability

**Week 11:** Integration Testing
- End-to-end workflow testing
- Performance optimization
- Security audit

**Week 12:** Documentation & Polish
- Complete all documentation
- Create examples and tutorials
- Final testing and bug fixes

**Milestone:** ✅ Phase 3 complete, ready for production use

---

## Next Steps (Immediate Actions)

### For Development Team

1. **Review this implementation plan**
   - Provide feedback on architecture
   - Suggest modifications if needed
   - Approve for implementation

2. **Setup development environment**
   - Install Unreal Engine 5.6
   - Enable Remote Control API plugin
   - Create test project

3. **Prioritize implementation phases**
   - Confirm timeline is acceptable
   - Adjust resource allocation
   - Set up project tracking

### For Phase 2 (Current)

1. **Update planning agents**
   - Add Remote Control-aware task types
   - Include automated testing tasks
   - Plan for validation steps

2. **Documentation updates**
   - Reference Remote Control in generated plans
   - Include automation opportunities
   - Note hybrid approach (manual vs automated)

3. **Prepare for Phase 3**
   - Finalize Phase 2 remaining work
   - Begin Remote Control experimentation
   - Create proof-of-concept examples

---

## Appendix

### A. Reference Documents

1. **Unreal Engine Documentation**
   - [Remote Control for Unreal Engine](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-for-unreal-engine)
   - [Remote Control API Reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/PluginIndex/RemoteControl)
   - [Remote Control Quick Start](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-quick-start-for-unreal-engine)

2. **Adastrea Director Documentation**
   - [AGENTS.md](AGENTS.md) - Agent architecture
   - [REMOTE_CONTROL_API.md](REMOTE_CONTROL_API.md) - Existing assessment
   - [PROJECT_PLAN.md](PROJECT_PLAN.md) - Project roadmap

3. **Community Resources**
   - [Python Wrapper](https://github.com/cgtoolbox/UnrealRemoteControlWrapper)
   - [TypeScript Client](https://github.com/sovietspaceship/ue4-remote-control)
   - [Unreal MCP Server](https://github.com/ChiR24/Unreal_mcp)

### B. Glossary

**Terms:**
- **Remote Control API**: Unreal Engine plugin enabling external control
- **PIE**: Play-in-Editor, testing mode in Unreal Editor
- **Data Asset**: Blueprint-based asset for configuration data
- **WebSocket**: Protocol for real-time bidirectional communication
- **Remote Control Preset**: Collection of exposed properties and functions
- **Version Control Agent**: Component managing git operations for agent changes

### C. Open Questions

1. **Multi-project Support**
   - How to handle multiple Unreal Engine projects?
   - Should each project have its own Remote Control client instance?

2. **Conflict Resolution Strategy**
   - What is the preferred automatic conflict resolution strategy?
   - When should human intervention be mandatory?

3. **Performance Baselines**
   - What are acceptable performance thresholds for agent operations?
   - How much latency is tolerable for Remote Control API calls?

4. **Authentication Requirements**
   - Is authentication needed for Remote Control API in Phase 3?
   - What authentication method should be used (API key, OAuth)?

5. **CI/CD Integration**
   - How should Remote Control API integrate with CI/CD pipelines?
   - Should agents run in CI environment or only locally?

---

**Document Status:** Draft for Review  
**Requires Approval:** Yes  
**Target Start Date:** Upon Phase 2 completion  
**Estimated Completion:** 3 months from start  

---

*Last Updated: 2025-11-12*  
*Author: Copilot SWE Agent*  
*Version: 1.0.0*
