"""
Adastrea Director - Agent System

This package contains the agent implementations for the Adastrea Director
system, organized by development phase.

Phase 1: Foundation Agents (Document Ingestion, Query)
Phase 2: Planning Agents (Goal Analysis, Task Decomposition, Code Generation)
Phase 3: Autonomous Agents (Performance, Bug Detection, Code Quality)
Phase 4: Creative Agents (Narrative, Asset, Game Design)
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
