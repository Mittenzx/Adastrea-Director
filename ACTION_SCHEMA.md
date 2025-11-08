# Adastrea Director - Action Schema (Draft v1.0)

**Author:** Planner-01
**Status:** Proposal

## 1. Introduction

This document defines the Action Schema for the Adastrea Director. The schema is a definitive list of concrete, low-level actions that the AI can include in a "plan." Each action is designed to be simple, auditable, and easily executable by a script.

The proposed format for a plan is a JSON array of action objects.

## 2. Schema Specification

### Action: `readFile`
- **Description:** Reads the entire content of a specified file.
- **Parameters:**
    - `path` (string): The full path to the file.
- **Example:**
  ```json
  {
    "action": "readFile",
    "params": {
      "path": "gdd/ADASTREA_GDD.md"
    }
  }
  ```

### Action: `writeFile`
- **Description:** Writes or overwrites a file with the provided content.
- **Parameters:**
    - `path` (string): The full path to the file.
    - `content` (string): The content to be written to the file.
- **Example:**
  ```json
  {
    "action": "writeFile",
    "params": {
      "path": "gdd/NEW_FEATURE.md",
      "content": "# New Feature Idea\n\nThis is a new gameplay mechanic..."
    }
  }
  ```

### Action: `createCppClass`
- **Description:** Scaffolds a new C++ class in the Unreal Engine project structure.
- **Parameters:**
    - `class_name` (string): The name of the class (e.g., "AQuestManager").
    - `parent_class` (string): The parent class to inherit from (e.g., "AActor").
    - `header_path` (string): The destination path for the `.h` file.
    - `source_path` (string): The destination path for the `.cpp` file.
- **Example:**
  ```json
  {
    "action": "createCppClass",
    "params": {
      "class_name": "AQuestManager",
      "parent_class": "UObject",
      "header_path": "Source/Adastrea/Public/Quests/QuestManager.h",
      "source_path": "Source/Adastrea/Private/Quests/QuestManager.cpp"
    }
  }
  ```

### Action: `executeShellCommand`
- **Description:** Executes a shell command in the project's root directory. This is a powerful but potentially dangerous action.
- **Parameters:**
    - `command` (string): The command to execute (e.g., "git status").
- **Example:**
  ```json
  {
    "action": "executeShellCommand",
    "params": {
      "command": "python -m unittest discover tests"
    }
  }
  ```

## 3. Next Steps
Once this schema is approved, the next task is to build the "Plan Executor" module in Python. This module will be responsible for parsing a plan and calling the appropriate function for each action.
