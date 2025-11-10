#!/usr/bin/env python3
"""
Data models for Phase 2 Planning Agents

This module defines the core data structures used by planning agents
to represent goals, tasks, constraints, and dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import uuid4


class GoalType(Enum):
    """Classification of development goals."""
    FEATURE = "feature"
    BUG_FIX = "bug_fix"
    OPTIMIZATION = "optimization"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    INFRASTRUCTURE = "infrastructure"


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority level of a task."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConstraintType(Enum):
    """Types of constraints that can affect goals/tasks."""
    TIME = "time"
    RESOURCE = "resource"
    TECHNICAL = "technical"
    DEPENDENCY = "dependency"
    QUALITY = "quality"


@dataclass
class Constraint:
    """Represents a constraint on a goal or task."""
    id: str = field(default_factory=lambda: str(uuid4()))
    constraint_type: ConstraintType = ConstraintType.TECHNICAL
    description: str = ""
    severity: str = "medium"  # low, medium, high, critical
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectScope:
    """Defines the scope of a project affected by a goal."""
    affected_areas: List[str] = field(default_factory=list)
    estimated_complexity: str = "medium"  # low, medium, high
    requires_new_dependencies: bool = False
    breaking_changes: bool = False
    documentation_needs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Goal:
    """Represents a high-level development goal."""
    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    goal_type: GoalType = GoalType.FEATURE
    constraints: List[Constraint] = field(default_factory=list)
    scope: Optional[ProjectScope] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Represents an actionable task derived from a goal."""
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    goal_id: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_effort: Optional[str] = None  # e.g., "2 hours", "1 day"
    dependencies: List[str] = field(default_factory=list)  # Task IDs
    assignee: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    file_modifications: List[str] = field(default_factory=list)
    code_examples: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskTree:
    """Hierarchical representation of tasks."""
    root_task: Task
    subtasks: List['TaskTree'] = field(default_factory=list)
    
    def get_all_tasks(self) -> List[Task]:
        """Get a flat list of all tasks in the tree."""
        tasks = [self.root_task]
        for subtree in self.subtasks:
            tasks.extend(subtree.get_all_tasks())
        return tasks


@dataclass
class DependencyGraph:
    """Represents dependencies between tasks."""
    tasks: Dict[str, Task] = field(default_factory=dict)
    edges: Dict[str, List[str]] = field(default_factory=dict)  # task_id -> [dependent_task_ids]
    
    def add_task(self, task: Task):
        """Add a task to the graph."""
        self.tasks[task.id] = task
        if task.id not in self.edges:
            self.edges[task.id] = []
    
    def add_dependency(self, from_task_id: str, to_task_id: str):
        """Add a dependency edge (from_task must complete before to_task)."""
        if from_task_id not in self.edges:
            self.edges[from_task_id] = []
        if to_task_id not in self.edges[from_task_id]:
            self.edges[from_task_id].append(to_task_id)
    
    def get_executable_tasks(self) -> List[Task]:
        """Get tasks that can be executed (all dependencies completed)."""
        executable = []
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.COMPLETED:
                continue
            
            # Check if all dependencies are completed
            dependencies_met = True
            for dep_id in task.dependencies:
                if dep_id in self.tasks:
                    dep_task = self.tasks[dep_id]
                    if dep_task.status != TaskStatus.COMPLETED:
                        dependencies_met = False
                        break
            
            if dependencies_met:
                executable.append(task)
        
        return executable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert dependency graph to dictionary for serialization."""
        return {
            "tasks": {task_id: {
                "id": task.id,
                "title": task.title,
                "status": task.status.value,
                "priority": task.priority.value,
                "dependencies": task.dependencies
            } for task_id, task in self.tasks.items()},
            "edges": self.edges
        }


@dataclass
class Duration:
    """Represents time duration for tasks."""
    hours: float = 0.0
    days: float = 0.0
    
    def to_hours(self) -> float:
        """Convert duration to hours."""
        return self.hours + (self.days * 8)  # Assuming 8-hour workday
    
    def __str__(self) -> str:
        if self.days > 0:
            return f"{self.days} day{'s' if self.days != 1 else ''}"
        elif self.hours > 0:
            return f"{self.hours} hour{'s' if self.hours != 1 else ''}"
        return "0 hours"


@dataclass
class ActionPlan:
    """Comprehensive action plan for implementing a goal."""
    goal: Goal
    tasks: List[Task] = field(default_factory=list)
    dependency_graph: Optional[DependencyGraph] = None
    total_estimated_effort: Optional[Duration] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_summary(self) -> str:
        """Generate a human-readable summary of the action plan."""
        lines = [
            f"Action Plan for: {self.goal.description}",
            f"Goal Type: {self.goal.goal_type.value}",
            f"Priority: {self.goal.priority.value}",
            f"Total Tasks: {len(self.tasks)}",
        ]
        
        if self.total_estimated_effort:
            lines.append(f"Estimated Effort: {self.total_estimated_effort}")
        
        if self.goal.constraints:
            lines.append(f"Constraints: {len(self.goal.constraints)}")
        
        return "\n".join(lines)
