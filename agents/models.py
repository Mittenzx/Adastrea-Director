"""
Data models for the Adastrea Director agent system.

These models define the structure of goals, tasks, constraints, and other
entities used by the planning agents.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional


class GoalType(Enum):
    """Types of development goals."""
    FEATURE = "feature"
    BUG_FIX = "bug_fix"
    OPTIMIZATION = "optimization"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    INFRASTRUCTURE = "infrastructure"
    OTHER = "other"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class ConstraintType(Enum):
    """Types of constraints that can affect goals/tasks."""
    TIME = "time"
    RESOURCE = "resource"
    TECHNICAL = "technical"
    DEPENDENCY = "dependency"
    QUALITY = "quality"


@dataclass
class Duration:
    """Represents estimated time duration for tasks."""
    hours: float
    confidence: float = 0.7  # Confidence level (0-1) in the estimate
    
    def __str__(self) -> str:
        if self.hours < 1:
            return f"{int(self.hours * 60)}min"
        elif self.hours < 8:
            return f"{self.hours:.1f}h"
        else:
            days = self.hours / 8
            return f"{days:.1f}d"
    
    def to_timedelta(self) -> timedelta:
        """Convert to timedelta object."""
        return timedelta(hours=self.hours)


@dataclass
class Constraint:
    """Represents a constraint or requirement for a goal."""
    description: str
    constraint_type: str  # e.g., "technical", "resource", "time", "dependency"
    is_hard: bool = True  # Hard constraint vs soft preference
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectScope:
    """Defines the areas of the project affected by a goal."""
    files: List[str] = field(default_factory=list)
    directories: List[str] = field(default_factory=list)
    systems: List[str] = field(default_factory=list)  # e.g., "combat", "UI", "networking"
    external_dependencies: List[str] = field(default_factory=list)
    estimated_complexity: str = "medium"  # low, medium, high, very_high
    
    def __str__(self) -> str:
        parts = []
        if self.files:
            parts.append(f"{len(self.files)} files")
        if self.directories:
            parts.append(f"{len(self.directories)} directories")
        if self.systems:
            parts.append(f"Systems: {', '.join(self.systems)}")
        return " | ".join(parts) if parts else "No scope defined"


@dataclass
class Goal:
    """Represents a high-level development goal."""
    id: str
    description: str
    goal_type: GoalType
    constraints: List[Constraint] = field(default_factory=list)
    scope: Optional[ProjectScope] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"[{self.goal_type.value}] {self.description}"


@dataclass
class Task:
    """Represents an atomic task derived from a goal."""
    id: str
    description: str
    goal_id: str  # Reference to parent goal
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_duration: Optional[Duration] = None
    dependencies: List[str] = field(default_factory=list)  # IDs of tasks this depends on
    subtasks: List['Task'] = field(default_factory=list)
    files_to_modify: List[str] = field(default_factory=list)
    files_to_create: List[str] = field(default_factory=list)
    code_examples: List[str] = field(default_factory=list)
    implementation_notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    # Additional fields for backward compatibility with planning_models.py
    title: str = ""  # Alias for description for compatibility
    estimated_effort: Optional[str] = None  # String representation (e.g., "2 hours", "1 day")
    assignee: Optional[str] = None
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    file_modifications: List[str] = field(default_factory=list)  # Alias for files_to_modify
    
    def __str__(self) -> str:
        status_icon = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🚧",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.BLOCKED: "🚫",
            TaskStatus.CANCELLED: "❌",
        }
        icon = status_icon.get(self.status, "")
        duration_str = f" ({self.estimated_duration})" if self.estimated_duration else ""
        return f"{icon} {self.description}{duration_str}"


@dataclass
class TaskTree:
    """Represents a hierarchical decomposition of tasks."""
    goal: Goal
    root_tasks: List[Task]
    total_estimated_duration: Optional[Duration] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks in the tree (including subtasks)."""
        all_tasks = []
        
        def collect_tasks(task_list: List[Task]):
            for task in task_list:
                all_tasks.append(task)
                if task.subtasks:
                    collect_tasks(task.subtasks)
        
        collect_tasks(self.root_tasks)
        return all_tasks
    
    def get_task_count(self) -> int:
        """Get total number of tasks."""
        return len(self.get_all_tasks())
    
    def __str__(self) -> str:
        task_count = self.get_task_count()
        duration_str = f" ({self.total_estimated_duration})" if self.total_estimated_duration else ""
        return f"TaskTree: {task_count} tasks{duration_str}"


@dataclass
class DependencyGraph:
    """Represents task dependencies as a graph."""
    tasks: List[Task]
    adjacency_list: Dict[str, List[str]] = field(default_factory=dict)  # task_id -> [dependent_task_ids]
    
    def __post_init__(self):
        """Build adjacency list from tasks."""
        if not self.adjacency_list:
            self.adjacency_list = {}
            for task in self.tasks:
                self.adjacency_list[task.id] = task.dependencies
    
    def get_execution_order(self) -> List[List[str]]:
        """
        Get tasks grouped by execution level (tasks that can run in parallel).
        Returns a list of lists, where each inner list contains task IDs that can be executed in parallel.
        """
        # Track in-degree (number of dependencies) for each task
        in_degree = {task.id: len(task.dependencies) for task in self.tasks}
        
        # Start with tasks that have no dependencies
        result = []
        available = [task.id for task in self.tasks if len(task.dependencies) == 0]
        
        while available:
            result.append(available[:])  # Add current level
            next_available = []
            
            # Remove completed tasks from dependencies
            for task_id in available:
                # Find tasks that depend on this task
                for task in self.tasks:
                    if task_id in task.dependencies:
                        in_degree[task.id] -= 1
                        if in_degree[task.id] == 0:
                            next_available.append(task.id)
            
            available = next_available
        
        return result
    
    def has_cycles(self) -> bool:
        """Check if the dependency graph has cycles."""
        visited = set()
        rec_stack = set()
        
        def has_cycle_util(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            
            for dep_id in self.adjacency_list.get(task_id, []):
                if dep_id not in visited:
                    if has_cycle_util(dep_id):
                        return True
                elif dep_id in rec_stack:
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        for task in self.tasks:
            if task.id not in visited:
                if has_cycle_util(task.id):
                    return True
        
        return False


@dataclass
class Implementation:
    """Represents an implementation approach for a task."""
    approach_name: str
    description: str
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    complexity: str = "medium"  # low, medium, high
    estimated_duration: Optional[Duration] = None
    code_example: str = ""
    required_libraries: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"{self.approach_name} ({self.complexity} complexity)"


@dataclass
class FileModification:
    """Represents a proposed modification to a file."""
    file_path: str
    modification_type: str  # "create", "update", "delete"
    description: str
    code_snippet: str = ""
    line_numbers: Optional[tuple[int, int]] = None  # (start, end) for updates
    backup_recommended: bool = True
    
    def __str__(self) -> str:
        return f"{self.modification_type}: {self.file_path} - {self.description}"


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
