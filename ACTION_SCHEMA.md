# Adastrea Director - Action Schema v1.0

**Status:** Phase 2 Foundation Document  
**Last Updated:** 2025-11-08  
**Purpose:** Define the formal, machine-readable schema for actions that the Planner agent will generate

---

## 1. Overview

This document establishes a formal JSON schema for "actions" - the atomic units of work that compose executable plans in the Adastrea Director system. Each action represents a discrete, auditable task that can be executed, tracked, and validated.

Actions form the building blocks of plans, enabling the AI to:
- Break down high-level goals into concrete steps
- Track execution status and dependencies
- Provide clear audit trails for all operations
- Enable human review before execution

---

## 2. Core Schema Definition

### 2.1 Action Object Structure

Each action is a JSON object conforming to the following schema:

```json
{
  "schema_version": "1.0",
  "action_id": "string",
  "description": "string",
  "type": "string",
  "parameters": {},
  "dependencies": [],
  "status": "string"
}
```

### 2.2 Field Specifications

#### `schema_version` (string, required)
- **Description:** Version of the action schema being used
- **Format:** Semantic versioning (e.g., "1.0", "1.1", "2.0")
- **Purpose:** Ensures compatibility and enables schema evolution
- **Example:** `"1.0"`

#### `action_id` (string, required)
- **Description:** Unique identifier for this action within a plan
- **Format:** Alphanumeric string, typically prefixed with action type
- **Constraints:** Must be unique within a single plan
- **Example:** `"file_create_001"`, `"cmd_run_042"`

#### `description` (string, required)
- **Description:** Human-readable summary of what the action accomplishes
- **Purpose:** Enables human review and plan understanding
- **Best Practices:** Should be concise but informative, action-oriented
- **Example:** `"Create new QuestManager class in the game systems directory"`

#### `type` (string, required)
- **Description:** Category of the action, defining its behavior
- **Valid Values:**
  - `file.create` - Create a new file
  - `file.modify` - Modify an existing file
  - `file.delete` - Delete a file
  - `file.move` - Move or rename a file
  - `command.run` - Execute a shell command
  - `goal.breakdown` - Meta-action to decompose a goal into sub-actions
  - `code.generate` - Generate code based on specifications
  - `test.run` - Execute tests
  - `review.request` - Request human review
- **Extensibility:** Additional types can be added in future schema versions

#### `parameters` (object, required)
- **Description:** Action-specific parameters defining what and how to execute
- **Structure:** Key-value pairs, specific to each action type
- **Validation:** Must contain all required fields for the specified action type
- **Example:** See section 3 for type-specific parameter definitions

#### `dependencies` (array, required)
- **Description:** List of action_id values that must complete before this action can execute
- **Format:** Array of strings, each matching an action_id in the same plan
- **Empty Array:** `[]` indicates no dependencies
- **Purpose:** Defines execution order and enables parallel execution where possible
- **Example:** `["file_create_001", "code_gen_003"]`

#### `status` (string, required)
- **Description:** Current execution state of the action
- **Valid Values:**
  - `pending` - Not yet started, waiting for dependencies or execution
  - `in_progress` - Currently being executed
  - `completed` - Successfully finished
  - `failed` - Execution failed (should include error details in extended schema)
  - `blocked` - Cannot proceed due to failed dependency
  - `skipped` - Intentionally skipped based on plan logic
- **Immutability:** Status should only transition forward through valid state changes

---

## 3. Action Type Specifications

### 3.1 File Operations

#### Type: `file.create`
**Purpose:** Create a new file with specified content

**Required Parameters:**
- `file_path` (string): Absolute or relative path to the new file
- `content` (string): Content to write to the file

**Optional Parameters:**
- `encoding` (string): Character encoding (default: "utf-8")
- `create_dirs` (boolean): Create parent directories if needed (default: true)

**Example:**
```json
{
  "schema_version": "1.0",
  "action_id": "file_create_001",
  "description": "Create new game design document for quest system",
  "type": "file.create",
  "parameters": {
    "file_path": "docs/game_design/quest_system.md",
    "content": "# Quest System Design\n\n## Overview\nThis document outlines...",
    "encoding": "utf-8",
    "create_dirs": true
  },
  "dependencies": [],
  "status": "pending"
}
```

#### Type: `file.modify`
**Purpose:** Modify an existing file's content

**Required Parameters:**
- `file_path` (string): Path to the file to modify
- `operation` (string): Type of modification ("replace", "append", "insert", "patch")
- `content` (string): New content or content to add

**Optional Parameters:**
- `line_number` (integer): For "insert" operations, line to insert at
- `search_pattern` (string): For "replace" operations, pattern to find
- `backup` (boolean): Create backup before modifying (default: true)

**Example:**
```json
{
  "schema_version": "1.0",
  "action_id": "file_modify_002",
  "description": "Add new function to Player controller class",
  "type": "file.modify",
  "parameters": {
    "file_path": "Source/Adastrea/Public/PlayerController.h",
    "operation": "insert",
    "content": "    void HandleQuestCompletion(int32 QuestID);",
    "line_number": 45,
    "backup": true
  },
  "dependencies": ["file_create_001"],
  "status": "pending"
}
```

#### Type: `file.delete`
**Purpose:** Delete a file from the filesystem

**Required Parameters:**
- `file_path` (string): Path to the file to delete

**Optional Parameters:**
- `backup` (boolean): Create backup before deletion (default: true)
- `confirm` (boolean): Require explicit confirmation (default: true)

**Example:**
```json
{
  "schema_version": "1.0",
  "action_id": "file_delete_003",
  "description": "Remove deprecated configuration file",
  "type": "file.delete",
  "parameters": {
    "file_path": "Config/OldSettings.ini",
    "backup": true,
    "confirm": true
  },
  "dependencies": [],
  "status": "pending"
}
```

#### Type: `file.move`
**Purpose:** Move or rename a file

**Required Parameters:**
- `source_path` (string): Current path of the file
- `destination_path` (string): New path for the file

**Optional Parameters:**
- `overwrite` (boolean): Overwrite if destination exists (default: false)

**Example:**
```json
{
  "schema_version": "1.0",
  "action_id": "file_move_004",
  "description": "Reorganize quest blueprints to new directory structure",
  "type": "file.move",
  "parameters": {
    "source_path": "Content/Quests/QuestBP.uasset",
    "destination_path": "Content/GameSystems/Quests/QuestBP.uasset",
    "overwrite": false
  },
  "dependencies": [],
  "status": "pending"
}
```

### 3.2 Command Execution

#### Type: `command.run`
**Purpose:** Execute a shell command or script

**Required Parameters:**
- `command` (string): The command to execute

**Optional Parameters:**
- `working_directory` (string): Directory to execute command in
- `timeout` (integer): Maximum execution time in seconds
- `capture_output` (boolean): Capture stdout/stderr (default: true)
- `environment` (object): Additional environment variables

**Example:**
```json
{
  "schema_version": "1.0",
  "action_id": "cmd_run_005",
  "description": "Run unit tests for quest system",
  "type": "command.run",
  "parameters": {
    "command": "python -m pytest tests/quest_system/",
    "working_directory": ".",
    "timeout": 300,
    "capture_output": true,
    "environment": {
      "PYTEST_ARGS": "--verbose --cov"
    }
  },
  "dependencies": ["file_create_001", "file_modify_002"],
  "status": "pending"
}
```

### 3.3 Planning Operations

#### Type: `goal.breakdown`
**Purpose:** Decompose a high-level goal into sub-actions (meta-action)

**Required Parameters:**
- `goal_description` (string): The goal to decompose
- `context` (object): Relevant context for planning

**Optional Parameters:**
- `max_depth` (integer): Maximum recursion depth for breakdown
- `constraints` (array): Constraints to consider during planning

**Example:**
```json
{
  "schema_version": "1.0",
  "action_id": "goal_breakdown_006",
  "description": "Break down quest system implementation into concrete tasks",
  "type": "goal.breakdown",
  "parameters": {
    "goal_description": "Implement a quest system with branching storylines",
    "context": {
      "project_type": "Unreal Engine 5",
      "language": "C++",
      "existing_systems": ["inventory", "dialogue"]
    },
    "max_depth": 3,
    "constraints": ["Must integrate with existing dialogue system"]
  },
  "dependencies": [],
  "status": "pending"
}
```

### 3.4 Code Operations

#### Type: `code.generate`
**Purpose:** Generate code based on specifications

**Required Parameters:**
- `target_file` (string): File to generate or modify
- `code_type` (string): Type of code ("class", "function", "blueprint", etc.)
- `specifications` (object): Detailed specifications for generation

**Example:**
```json
{
  "schema_version": "1.0",
  "action_id": "code_gen_007",
  "description": "Generate QuestManager C++ class skeleton",
  "type": "code.generate",
  "parameters": {
    "target_file": "Source/Adastrea/Public/QuestManager.h",
    "code_type": "class",
    "specifications": {
      "class_name": "UQuestManager",
      "parent_class": "UObject",
      "includes_required": ["CoreMinimal.h", "Quest.h"],
      "methods": [
        {"name": "StartQuest", "return_type": "void", "parameters": ["int32 QuestID"]},
        {"name": "CompleteQuest", "return_type": "bool", "parameters": ["int32 QuestID"]}
      ]
    }
  },
  "dependencies": [],
  "status": "pending"
}
```

### 3.5 Testing Operations

#### Type: `test.run`
**Purpose:** Execute tests to validate functionality

**Required Parameters:**
- `test_suite` (string): Test suite or file to run
- `test_framework` (string): Testing framework ("pytest", "unittest", etc.)

**Optional Parameters:**
- `test_filter` (string): Pattern to filter which tests run
- `coverage` (boolean): Generate coverage report (default: false)

**Example:**
```json
{
  "schema_version": "1.0",
  "action_id": "test_run_008",
  "description": "Run integration tests for quest system",
  "type": "test.run",
  "parameters": {
    "test_suite": "tests/integration/quest_tests.py",
    "test_framework": "pytest",
    "test_filter": "test_quest_*",
    "coverage": true
  },
  "dependencies": ["code_gen_007", "file_modify_002"],
  "status": "pending"
}
```

### 3.6 Review Operations

#### Type: `review.request`
**Purpose:** Request human review before proceeding

**Required Parameters:**
- `review_type` (string): Type of review needed ("code", "design", "plan", etc.)
- `artifacts` (array): Files or outputs to review

**Optional Parameters:**
- `reviewer` (string): Specific reviewer to request
- `blocking` (boolean): Whether execution should pause (default: true)

**Example:**
```json
{
  "schema_version": "1.0",
  "action_id": "review_req_009",
  "description": "Request code review for quest system implementation",
  "type": "review.request",
  "parameters": {
    "review_type": "code",
    "artifacts": [
      "Source/Adastrea/Public/QuestManager.h",
      "Source/Adastrea/Private/QuestManager.cpp"
    ],
    "reviewer": "lead_developer",
    "blocking": true
  },
  "dependencies": ["code_gen_007"],
  "status": "pending"
}
```

---

## 4. Complete Plan Example

A complete plan is an array of action objects that can be executed sequentially or in parallel based on dependencies:

```json
{
  "plan_id": "plan_quest_system_001",
  "plan_version": "1.0",
  "created_at": "2025-11-08T20:00:00Z",
  "goal": "Implement basic quest system for Adastrea",
  "actions": [
    {
      "schema_version": "1.0",
      "action_id": "file_create_001",
      "description": "Create quest system design document",
      "type": "file.create",
      "parameters": {
        "file_path": "docs/quest_system.md",
        "content": "# Quest System\n\n## Overview\n..."
      },
      "dependencies": [],
      "status": "pending"
    },
    {
      "schema_version": "1.0",
      "action_id": "code_gen_002",
      "description": "Generate QuestManager class",
      "type": "code.generate",
      "parameters": {
        "target_file": "Source/Adastrea/Public/QuestManager.h",
        "code_type": "class",
        "specifications": {
          "class_name": "UQuestManager",
          "parent_class": "UObject"
        }
      },
      "dependencies": ["file_create_001"],
      "status": "pending"
    },
    {
      "schema_version": "1.0",
      "action_id": "test_run_003",
      "description": "Run quest system tests",
      "type": "test.run",
      "parameters": {
        "test_suite": "tests/quest_tests.py",
        "test_framework": "pytest"
      },
      "dependencies": ["code_gen_002"],
      "status": "pending"
    },
    {
      "schema_version": "1.0",
      "action_id": "review_req_004",
      "description": "Request review of implementation",
      "type": "review.request",
      "parameters": {
        "review_type": "code",
        "artifacts": ["Source/Adastrea/Public/QuestManager.h"]
      },
      "dependencies": ["test_run_003"],
      "status": "pending"
    }
  ]
}
```

---

## 5. Status Transitions

Valid status transitions for actions:

```
pending → in_progress → completed
                     → failed
                     
pending → blocked (when dependency fails)
        → skipped (when conditionally excluded)
```

---

## 6. Extension Points

### 6.1 Custom Action Types

The schema supports custom action types for project-specific needs. Follow the naming convention:
- Use dot notation: `category.subcategory.action`
- Prefix custom types with `custom.` to avoid conflicts
- Document parameters clearly

### 6.2 Additional Metadata

Actions can include additional fields for extended functionality:
- `priority` (integer): Execution priority
- `estimated_duration` (integer): Expected execution time in seconds
- `retry_policy` (object): Retry behavior on failure
- `tags` (array): Classification tags
- `created_by` (string): Agent or user who created the action

---

## 7. Implementation Notes

### For Planner Agent (`planner.py`)
- Generate actions conforming to this schema
- Validate all required fields are present
- Ensure action_id uniqueness within plans
- Build valid dependency graphs (no cycles)

### For Task Executor (`task_executor.py`)
- Parse and validate action schemas
- Implement handlers for each action type
- Track status transitions
- Handle dependency resolution
- Provide detailed error reporting

### For Human Review Interface
- Display actions in readable format
- Allow status modification
- Enable dependency visualization
- Support plan editing before execution

---

## 8. Schema Evolution

Future versions of this schema will:
- Maintain backward compatibility where possible
- Use `schema_version` field for compatibility checks
- Document breaking changes clearly
- Provide migration guides for major versions

**Current Version:** 1.0  
**Next Planned Version:** 1.1 (to include error handling fields)

---

## 9. References

- **PROJECT_PLAN.md** - Phase 2 implementation roadmap
- **AGENTS.md** - Agent architecture and responsibilities
- **Future:** `planner.py` - Action generation implementation
- **Future:** `task_executor.py` - Action execution engine

---

**Document Status:** Final v1.0  
**Approved For:** Phase 2 implementation  
**Next Steps:** Implement `planner.py` and `task_executor.py` modules based on this schema
