#!/usr/bin/env python3
"""
DEPRECATED: This module is deprecated. Please use agents.models instead.

Data models for Planning Agents

This module now re-exports all models from agents.models for backward compatibility.
All new code should import directly from agents.models.

This file is kept for backward compatibility with existing code that imports from planning_models.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "planning_models is deprecated. Please use 'from agents.models import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export all models from agents.models for backward compatibility
from agents.models import (
    # Enums
    GoalType,
    TaskStatus,
    TaskPriority,
    ConstraintType,
    # Data classes
    Constraint,
    ProjectScope,
    Goal,
    Task,
    TaskTree,
    DependencyGraph,
    Duration,
    ActionPlan,
)

__all__ = [
    # Enums
    "GoalType",
    "TaskStatus",
    "TaskPriority",
    "ConstraintType",
    # Data classes
    "Constraint",
    "ProjectScope",
    "Goal",
    "Task",
    "TaskTree",
    "DependencyGraph",
    "Duration",
    "ActionPlan",
]
