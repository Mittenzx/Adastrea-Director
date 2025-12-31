"""
Adastrea Director - Agent System

This package contains the agent implementations for the Adastrea Director system.

Includes:
- Goal Analysis: Parse and understand development goals
- Task Decomposition: Break down goals into actionable tasks
- Code Generation: Generate implementation approaches
- Autonomous Agents: Performance profiling, bug detection, and code quality monitoring
"""

from agents.models import (
    Goal,
    GoalType,
    Task,
    TaskPriority,
    TaskStatus,
    Constraint,
    ConstraintType,
    ProjectScope,
    TaskTree,
    DependencyGraph,
    Implementation,
    FileModification,
    Duration,
    ActionPlan,
)

from agents.goal_analysis_agent import GoalAnalysisAgent
from agents.task_decomposition_agent import TaskDecompositionAgent
from agents.code_generation_agent import CodeGenerationAgent

__all__ = [
    # Data Models
    "Goal",
    "GoalType",
    "Task",
    "TaskPriority",
    "TaskStatus",
    "Constraint",
    "ConstraintType",
    "ProjectScope",
    "TaskTree",
    "DependencyGraph",
    "Implementation",
    "FileModification",
    "Duration",
    "ActionPlan",
    # Agents
    "GoalAnalysisAgent",
    "TaskDecompositionAgent",
    "CodeGenerationAgent",
]
