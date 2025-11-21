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
    """Represents estimated time duration for tasks. Supports both APIs for compatibility."""
    hours: float = 0.0
    days: float = 0.0
    confidence: float = 0.7  # Confidence level (0-1) in the estimate (agents.models API)
    
    def to_hours(self) -> float:
        """Convert duration to total hours (planning_models API)."""
        return self.hours + (self.days * 8)  # Assuming 8-hour workday
    
    def normalize(self) -> None:
        """Normalize duration by converting excess hours into days (planning_models API)."""
        if self.hours >= 8:
            extra_days = self.hours // 8
            self.days += extra_days
            self.hours = self.hours % 8
    
    def to_timedelta(self) -> timedelta:
        """Convert to timedelta object (agents.models API)."""
        return timedelta(hours=self.to_hours())
    
    def __str__(self) -> str:
        """String representation supporting both APIs."""
        # Handle fractional values by converting to more readable format
        total_days = int(self.days)
        rem_days = self.days - total_days
        total_hours = self.hours + rem_days * 8
        int_hours = int(total_hours)
        rem_hours = total_hours - int_hours
        minutes = int(round(rem_hours * 60))
        
        parts = []
        if total_days > 0:
            parts.append(f"{total_days} day{'s' if total_days != 1 else ''}")
        if int_hours > 0:
            parts.append(f"{int_hours} hour{'s' if int_hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        if not parts:
            return "0 hours"
        return ", ".join(parts)


@dataclass
class Constraint:
    """Represents a constraint or requirement for a goal. Supports both APIs."""
    description: str = ""
    constraint_type: Any = None  # Can be str or ConstraintType enum for compatibility
    is_hard: bool = True  # Hard constraint vs soft preference (agents.models API)
    # Additional fields from planning_models for compatibility
    id: str = field(default_factory=lambda: str(__import__('uuid').uuid4()))
    severity: str = "medium"  # low, medium, high, critical (planning_models API)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize constraint_type properly for both APIs."""
        if self.constraint_type is None:
            self.constraint_type = ConstraintType.TECHNICAL if 'ConstraintType' in dir() else "technical"
        # Convert string to enum if needed
        if isinstance(self.constraint_type, str) and self.constraint_type in ['time', 'resource', 'technical', 'dependency', 'quality']:
            try:
                self.constraint_type = ConstraintType(self.constraint_type)
            except:
                pass  # Keep as string if enum not available


@dataclass
class ProjectScope:
    """Defines the areas of the project affected by a goal. Supports both APIs."""
    # agents.models fields
    files: List[str] = field(default_factory=list)
    directories: List[str] = field(default_factory=list)
    systems: List[str] = field(default_factory=list)  # e.g., "combat", "UI", "networking"
    external_dependencies: List[str] = field(default_factory=list)
    estimated_complexity: str = "medium"  # low, medium, high, very_high
    # planning_models fields for compatibility
    affected_areas: List[str] = field(default_factory=list)  # Alias for systems
    requires_new_dependencies: bool = False
    breaking_changes: bool = False
    documentation_needs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        parts = []
        if self.files:
            parts.append(f"{len(self.files)} files")
        if self.directories:
            parts.append(f"{len(self.directories)} directories")
        if self.systems or self.affected_areas:
            areas = self.systems + self.affected_areas
            parts.append(f"Systems: {', '.join(areas)}")
        return " | ".join(parts) if parts else "No scope defined"


@dataclass
class Goal:
    """Represents a high-level development goal."""
    id: str = field(default_factory=lambda: str(__import__('uuid').uuid4()))
    description: str = ""
    goal_type: GoalType = GoalType.FEATURE
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
    id: str = field(default_factory=lambda: str(__import__('uuid').uuid4()))
    description: str = ""
    goal_id: str = ""  # Reference to parent goal
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
    """Represents a hierarchical decomposition of tasks. Supports both APIs."""
    # Support both APIs
    goal: Optional[Goal] = None  # agents.models API
    root_tasks: List[Task] = field(default_factory=list)  # agents.models API
    root_task: Optional[Task] = None  # planning_models API
    subtasks: List['TaskTree'] = field(default_factory=list)  # planning_models API (recursive structure)
    total_estimated_duration: Optional[Duration] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks in the tree (supports both APIs)."""
        all_tasks = []
        
        # agents.models API (flat list with subtasks)
        if self.root_tasks:
            def collect_tasks(task_list: List[Task]):
                for task in task_list:
                    all_tasks.append(task)
                    if task.subtasks:
                        collect_tasks(task.subtasks)
            collect_tasks(self.root_tasks)
        
        # planning_models API (recursive tree structure)
        if self.root_task:
            all_tasks.extend(self._iter_all_tasks())
        
        return all_tasks
    
    def _iter_all_tasks(self):
        """Yield all tasks in the tree (planning_models API, generator for efficiency)."""
        if self.root_task:
            yield self.root_task
        for subtree in self.subtasks:
            yield from subtree._iter_all_tasks()
    
    def get_task_count(self) -> int:
        """Get total number of tasks."""
        return len(self.get_all_tasks())
    
    def __str__(self) -> str:
        task_count = self.get_task_count()
        duration_str = f" ({self.total_estimated_duration})" if self.total_estimated_duration else ""
        return f"TaskTree: {task_count} tasks{duration_str}"


@dataclass
class DependencyGraph:
    """Represents task dependencies as a graph. Supports both APIs for compatibility."""
    # Support both APIs: List[Task] (agents.models) and Dict[str, Task] (planning_models)
    tasks: Any = field(default_factory=lambda: [])  # Can be List[Task] or Dict[str, Task]
    adjacency_list: Dict[str, List[str]] = field(default_factory=dict)  # agents.models API
    edges: Dict[str, List[str]] = field(default_factory=dict)  # planning_models API (alias)
    
    def __post_init__(self):
        """Build adjacency list from tasks for both APIs."""
        # Convert Dict to List if needed for agents.models API
        if isinstance(self.tasks, dict):
            task_list = list(self.tasks.values())
        else:
            task_list = self.tasks if isinstance(self.tasks, list) else []
        
        # Build adjacency list if not provided
        if not self.adjacency_list and not self.edges:
            self.adjacency_list = {}
            self.edges = {}
            for task in task_list:
                self.adjacency_list[task.id] = task.dependencies
                self.edges[task.id] = task.dependencies
        elif self.adjacency_list and not self.edges:
            self.edges = self.adjacency_list
        elif self.edges and not self.adjacency_list:
            self.adjacency_list = self.edges
    
    # planning_models API methods
    def add_task(self, task: Task):
        """Add a task to the graph (planning_models API)."""
        if isinstance(self.tasks, dict):
            self.tasks[task.id] = task
        else:
            if not isinstance(self.tasks, list):
                self.tasks = []
            self.tasks.append(task)
        
        if task.id not in self.edges:
            self.edges[task.id] = []
        if task.id not in self.adjacency_list:
            self.adjacency_list[task.id] = []
    
    def add_dependency(self, from_task_id: str, to_task_id: str):
        """Add a dependency edge (planning_models API)."""
        if from_task_id not in self.edges:
            self.edges[from_task_id] = []
        if to_task_id not in self.edges[from_task_id]:
            self.edges[from_task_id].append(to_task_id)
        
        if from_task_id not in self.adjacency_list:
            self.adjacency_list[from_task_id] = []
        if to_task_id not in self.adjacency_list[from_task_id]:
            self.adjacency_list[from_task_id].append(to_task_id)
    
    def get_executable_tasks(self) -> List[Task]:
        """Get tasks that can be executed (planning_models API)."""
        executable = []
        task_dict = self.tasks if isinstance(self.tasks, dict) else {t.id: t for t in self.tasks}
        
        for task_id, task in task_dict.items():
            if task.status == TaskStatus.COMPLETED:
                continue
            
            # Check if all dependencies are completed
            dependencies_met = True
            for dep_id in task.dependencies:
                if dep_id in task_dict:
                    dep_task = task_dict[dep_id]
                    if dep_task.status != TaskStatus.COMPLETED:
                        dependencies_met = False
                        break
            
            if dependencies_met:
                executable.append(task)
        
        return executable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert dependency graph to dictionary (planning_models API)."""
        task_dict = self.tasks if isinstance(self.tasks, dict) else {t.id: t for t in self.tasks}
        return {
            "tasks": {task_id: {
                "id": task.id,
                "title": task.title or task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "dependencies": task.dependencies
            } for task_id, task in task_dict.items()},
            "edges": self.edges
        }
    
    # agents.models API methods
    def get_execution_order(self) -> List[List[str]]:
        """
        Get tasks grouped by execution level (agents.models API).
        Returns a list of lists, where each inner list contains task IDs that can be executed in parallel.
        """
        task_list = self.tasks if isinstance(self.tasks, list) else list(self.tasks.values())
        in_degree = {task.id: len(task.dependencies) for task in task_list}
        
        result = []
        available = [task.id for task in task_list if len(task.dependencies) == 0]
        
        while available:
            result.append(available[:])
            next_available = []
            
            for task_id in available:
                for task in task_list:
                    if task_id in task.dependencies:
                        in_degree[task.id] -= 1
                        if in_degree[task.id] == 0:
                            next_available.append(task.id)
            
            available = next_available
        
        return result
    
    def has_cycles(self) -> bool:
        """Check if the dependency graph has cycles (agents.models API)."""
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
        
        task_list = self.tasks if isinstance(self.tasks, list) else list(self.tasks.values())
        for task in task_list:
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
