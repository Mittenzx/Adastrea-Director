# Phase 2: Goal Decomposition System - User Guide

## Overview

Phase 2 introduces **intelligent goal decomposition** - the ability to take high-level development goals and automatically break them down into concrete, actionable tasks with dependencies, priorities, and effort estimates.

## Features

### 🎯 Goal Analysis Agent
- Parses natural language goal descriptions
- Classifies goals (feature, bug fix, optimization, etc.)
- Identifies constraints and requirements
- Determines project scope and complexity
- Detects breaking changes and new dependencies

### 📋 Task Decomposition Agent
- Breaks goals into specific, actionable tasks
- Estimates effort for each task
- Identifies task dependencies
- Prioritizes tasks intelligently
- Creates dependency graphs for execution planning

### 💻 Planning CLI
- Interactive and command-line modes
- Rich console output with tables
- Export action plans to Markdown

## Installation

Phase 2 uses the same dependencies as Phase 1. If you already have Phase 1 working, you're ready to use Phase 2!

```bash
# If needed, install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY=your_api_key_here
```

## Quick Start

### Interactive Mode

Run the planning CLI in interactive mode to decompose goals one at a time:

```bash
python planning_cli.py --interactive
```

You'll be presented with a prompt where you can enter development goals:

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              🎯 ADASTREA DIRECTOR                         ║
║          Phase 2: Goal Decomposition System               ║
║                                                           ║
║         Break down goals into actionable tasks            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Enter a development goal to decompose into tasks.
Type 'quit' to exit.

Goal: Implement user authentication system
```

### Single Goal Mode

Process a single goal and optionally save the action plan to a file:

```bash
python planning_cli.py --goal "Implement user authentication system" --output action_plan.md
```

This will:
1. Analyze the goal
2. Generate tasks with dependencies
3. Display the action plan in the console
4. Save the plan to `action_plan.md`

## Usage Examples

### Example 1: Feature Development

**Goal:** "Add a player inventory system with item management"

**Output:**
- Goal Type: feature
- Priority: high
- Complexity: high
- Tasks generated:
  1. Design inventory data structure
  2. Create backend API for inventory operations
  3. Implement UI components for inventory display
  4. Add item drag-and-drop functionality
  5. Create unit tests for inventory logic
  6. Write documentation for inventory API

### Example 2: Bug Fix

**Goal:** "Fix memory leak in particle system"

**Output:**
- Goal Type: bug_fix
- Priority: high
- Complexity: medium
- Tasks generated:
  1. Profile application to identify leak source
  2. Review particle pooling implementation
  3. Fix object reference issues
  4. Add memory profiling tests
  5. Verify fix in production environment

### Example 3: Optimization

**Goal:** "Optimize database queries for faster page loads"

**Output:**
- Goal Type: optimization
- Priority: medium
- Complexity: medium
- Tasks generated:
  1. Analyze slow query logs
  2. Add database indexes
  3. Implement query result caching
  4. Optimize N+1 query patterns
  5. Benchmark performance improvements

## Programmatic Usage

You can also use Phase 2 agents programmatically in your own scripts:

```python
from goal_analysis_agent import GoalAnalysisAgent
from task_decomposition_agent import TaskDecompositionAgent

# Initialize agents
goal_agent = GoalAnalysisAgent()
task_agent = TaskDecompositionAgent()

# Analyze a goal
goal_description = "Implement user authentication system"
goal = goal_agent.parse_goal(goal_description)

print(f"Goal Type: {goal.goal_type.value}")
print(f"Priority: {goal.priority.value}")
print(f"Constraints: {len(goal.constraints)}")

# Decompose into tasks
action_plan = task_agent.create_action_plan(goal)

print(f"\nTotal Tasks: {len(action_plan.tasks)}")
print(f"Estimated Effort: {action_plan.total_estimated_effort}")

# Get executable tasks (no dependencies)
executable = action_plan.dependency_graph.get_executable_tasks()
print(f"\nTasks ready to start: {len(executable)}")

for task in action_plan.tasks:
    print(f"\n{task.title}")
    print(f"  Priority: {task.priority.value}")
    print(f"  Effort: {task.estimated_effort}")
    print(f"  Description: {task.description[:100]}...")
```

## Data Models

### Goal

Represents a high-level development goal:

```python
@dataclass
class Goal:
    id: str
    description: str
    goal_type: GoalType  # FEATURE, BUG_FIX, OPTIMIZATION, etc.
    constraints: List[Constraint]
    scope: Optional[ProjectScope]
    priority: TaskPriority
    metadata: Dict[str, Any]
```

### Task

Represents an actionable task:

```python
@dataclass
class Task:
    id: str
    title: str
    description: str
    goal_id: str
    status: TaskStatus  # PENDING, IN_PROGRESS, COMPLETED, etc.
    priority: TaskPriority
    estimated_effort: Optional[str]
    dependencies: List[str]  # Task IDs
    file_modifications: List[str]
    metadata: Dict[str, Any]
```

### ActionPlan

Complete plan for implementing a goal:

```python
@dataclass
class ActionPlan:
    goal: Goal
    tasks: List[Task]
    dependency_graph: Optional[DependencyGraph]
    total_estimated_effort: Optional[Duration]
    created_at: datetime
```

## Tips for Best Results

### Writing Effective Goals

1. **Be Specific**: "Add user authentication with JWT tokens" is better than "Add login"
2. **Include Context**: Mention affected systems or components
3. **Mention Constraints**: Include time, resource, or technical constraints
4. **Specify Quality Requirements**: Mention testing, documentation needs

### Examples of Good Goals

✅ **Good:** "Implement a caching layer for database queries to reduce API response time below 100ms, with Redis integration and cache invalidation strategy"

❌ **Too Vague:** "Make the app faster"

✅ **Good:** "Fix the memory leak in the particle system's object pooling mechanism that causes crashes after 30 minutes of gameplay"

❌ **Too Vague:** "Fix bug"

## Integration with Phase 1

Phase 2 works alongside Phase 1's RAG system. You can:

1. Use Phase 1 to query your project documentation
2. Use Phase 2 to break down goals into tasks
3. Use Phase 1 to get implementation guidance for specific tasks

Example workflow:

```bash
# 1. Query documentation for context
python main.py
> "What is our authentication architecture?"

# 2. Create action plan based on understanding
python planning_cli.py --goal "Add OAuth2 support to existing authentication"

# 3. For each task, query for implementation details
python main.py
> "How do I implement OAuth2 token validation?"
```

## Advanced Features

### Dependency Graph Analysis

The `DependencyGraph` helps you understand task relationships:

```python
# Get tasks that can be started immediately
executable_tasks = action_plan.dependency_graph.get_executable_tasks()

# Get all tasks that depend on a specific task
dependent_task_ids = action_plan.dependency_graph.edges[task.id]

# Convert to dictionary for visualization
graph_dict = action_plan.dependency_graph.to_dict()
```

### Custom Effort Estimation

Override the default effort estimation:

```python
from planning_models import Duration

# Create a custom duration
custom_duration = Duration(hours=4, days=1)
print(custom_duration.to_hours())  # 12 hours total
```

### Task Filtering and Sorting

```python
# Get high-priority tasks only
high_priority_tasks = [
    task for task in action_plan.tasks 
    if task.priority == TaskPriority.HIGH
]

# Get tasks without dependencies
independent_tasks = [
    task for task in action_plan.tasks 
    if not task.dependencies
]
```

## Troubleshooting

### "No module named 'planning_models'"

Make sure you're running from the project root directory:

```bash
cd /path/to/Adastrea-Director
python planning_cli.py --interactive
```

### "OpenAI API key error"

Set your API key:

```bash
export OPENAI_API_KEY=your_key_here
# Or create .env file with OPENAI_API_KEY=your_key_here
```

### Task decomposition seems incomplete

Try being more specific with your goal description. Include:
- What system/component is affected
- What the desired outcome is
- Any technical constraints or requirements

## Next Steps

- Phase 3 will add **autonomous monitoring agents** for proactive issue detection
- Phase 4 will add **creative content generation** for narratives and assets

## Feedback

Phase 2 is designed to be iterative. The more you use it, the better it becomes at understanding your project's needs.

---

**Last Updated:** 2025-11-10
**Version:** 2.0.0
**Status:** ✅ Production Ready
