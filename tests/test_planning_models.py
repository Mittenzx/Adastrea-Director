"""
Tests for planning agent data models.
"""

from datetime import timedelta

from agents.models import (
    Goal,
    GoalType,
    Task,
    TaskPriority,
    TaskStatus,
    Constraint,
    ProjectScope,
    TaskTree,
    DependencyGraph,
    Implementation,
    FileModification,
    Duration,
)


class TestDuration:
    """Tests for Duration model."""
    
    def test_duration_creation(self):
        duration = Duration(hours=4.0, confidence=0.8)
        assert duration.hours == 4.0
        assert duration.confidence == 0.8
    
    def test_duration_str_minutes(self):
        duration = Duration(hours=0.5)
        assert str(duration) == "30min"
    
    def test_duration_str_hours(self):
        duration = Duration(hours=4.5)
        assert str(duration) == "4.5h"
    
    def test_duration_str_days(self):
        duration = Duration(hours=16.0)
        assert str(duration) == "2.0d"
    
    def test_duration_to_timedelta(self):
        duration = Duration(hours=5.0)
        td = duration.to_timedelta()
        assert isinstance(td, timedelta)
        assert td.total_seconds() == 5 * 3600


class TestConstraint:
    """Tests for Constraint model."""
    
    def test_constraint_creation(self):
        constraint = Constraint(
            description="Must use existing API",
            constraint_type="technical",
            is_hard=True
        )
        assert constraint.description == "Must use existing API"
        assert constraint.constraint_type == "technical"
        assert constraint.is_hard is True
    
    def test_constraint_with_metadata(self):
        constraint = Constraint(
            description="Budget limit",
            constraint_type="resource",
            metadata={"max_cost": 1000}
        )
        assert constraint.metadata["max_cost"] == 1000


class TestProjectScope:
    """Tests for ProjectScope model."""
    
    def test_project_scope_creation(self):
        scope = ProjectScope(
            files=["main.py", "utils.py"],
            directories=["agents/", "tests/"],
            systems=["combat", "UI"],
            estimated_complexity="high"
        )
        assert len(scope.files) == 2
        assert len(scope.directories) == 2
        assert "combat" in scope.systems
        assert scope.estimated_complexity == "high"
    
    def test_project_scope_str(self):
        scope = ProjectScope(
            files=["a.py", "b.py"],
            systems=["UI"]
        )
        scope_str = str(scope)
        assert "2 files" in scope_str
        assert "UI" in scope_str


class TestGoal:
    """Tests for Goal model."""
    
    def test_goal_creation(self):
        goal = Goal(
            id="goal-123",
            description="Add combat system",
            goal_type=GoalType.FEATURE,
            priority=TaskPriority.HIGH
        )
        assert goal.id == "goal-123"
        assert goal.description == "Add combat system"
        assert goal.goal_type == GoalType.FEATURE
        assert goal.priority == TaskPriority.HIGH
    
    def test_goal_with_constraints(self):
        constraint = Constraint("Must be performant", "technical")
        goal = Goal(
            id="goal-123",
            description="Optimize rendering",
            goal_type=GoalType.OPTIMIZATION,
            constraints=[constraint]
        )
        assert len(goal.constraints) == 1
        assert goal.constraints[0].description == "Must be performant"
    
    def test_goal_str(self):
        goal = Goal(
            id="goal-123",
            description="Fix crash bug",
            goal_type=GoalType.BUG_FIX
        )
        goal_str = str(goal)
        assert "bug_fix" in goal_str
        assert "Fix crash bug" in goal_str


class TestTask:
    """Tests for Task model."""
    
    def test_task_creation(self):
        task = Task(
            id="task-1",
            description="Implement player controller",
            goal_id="goal-123",
            priority=TaskPriority.HIGH,
            estimated_duration=Duration(hours=4.0)
        )
        assert task.id == "task-1"
        assert task.description == "Implement player controller"
        assert task.goal_id == "goal-123"
        assert task.status == TaskStatus.PENDING
    
    def test_task_with_dependencies(self):
        task = Task(
            id="task-2",
            description="Write tests",
            goal_id="goal-123",
            dependencies=["task-1"]
        )
        assert len(task.dependencies) == 1
        assert "task-1" in task.dependencies
    
    def test_task_with_files(self):
        task = Task(
            id="task-1",
            description="Create module",
            goal_id="goal-123",
            files_to_create=["module.py"],
            files_to_modify=["__init__.py"]
        )
        assert "module.py" in task.files_to_create
        assert "__init__.py" in task.files_to_modify
    
    def test_task_str(self):
        task = Task(
            id="task-1",
            description="Test task",
            goal_id="goal-123",
            status=TaskStatus.COMPLETED,
            estimated_duration=Duration(hours=2.0)
        )
        task_str = str(task)
        assert "✅" in task_str
        assert "Test task" in task_str


class TestTaskTree:
    """Tests for TaskTree model."""
    
    def test_task_tree_creation(self):
        goal = Goal(
            id="goal-1",
            description="Test goal",
            goal_type=GoalType.FEATURE
        )
        task1 = Task(id="task-1", description="Task 1", goal_id="goal-1")
        task2 = Task(id="task-2", description="Task 2", goal_id="goal-1")
        
        tree = TaskTree(
            goal=goal,
            root_tasks=[task1, task2],
            total_estimated_duration=Duration(hours=8.0)
        )
        
        assert tree.goal.id == "goal-1"
        assert len(tree.root_tasks) == 2
        assert tree.total_estimated_duration.hours == 8.0
    
    def test_get_all_tasks_flat(self):
        goal = Goal(id="goal-1", description="Test", goal_type=GoalType.FEATURE)
        task1 = Task(id="task-1", description="Task 1", goal_id="goal-1")
        task2 = Task(id="task-2", description="Task 2", goal_id="goal-1")
        
        tree = TaskTree(goal=goal, root_tasks=[task1, task2])
        all_tasks = tree.get_all_tasks()
        
        assert len(all_tasks) == 2
        assert task1 in all_tasks
        assert task2 in all_tasks
    
    def test_get_all_tasks_with_subtasks(self):
        goal = Goal(id="goal-1", description="Test", goal_type=GoalType.FEATURE)
        subtask = Task(id="subtask-1", description="Subtask", goal_id="goal-1")
        task = Task(
            id="task-1",
            description="Task",
            goal_id="goal-1",
            subtasks=[subtask]
        )
        
        tree = TaskTree(goal=goal, root_tasks=[task])
        all_tasks = tree.get_all_tasks()
        
        assert len(all_tasks) == 2
        assert task in all_tasks
        assert subtask in all_tasks
    
    def test_get_task_count(self):
        goal = Goal(id="goal-1", description="Test", goal_type=GoalType.FEATURE)
        task1 = Task(id="task-1", description="Task 1", goal_id="goal-1")
        task2 = Task(id="task-2", description="Task 2", goal_id="goal-1")
        
        tree = TaskTree(goal=goal, root_tasks=[task1, task2])
        assert tree.get_task_count() == 2


class TestDependencyGraph:
    """Tests for DependencyGraph model."""
    
    def test_dependency_graph_creation(self):
        task1 = Task(id="task-1", description="Task 1", goal_id="goal-1", dependencies=[])
        task2 = Task(id="task-2", description="Task 2", goal_id="goal-1", dependencies=["task-1"])
        
        graph = DependencyGraph(tasks=[task1, task2])
        
        assert len(graph.tasks) == 2
        assert "task-1" in graph.adjacency_list
        assert "task-2" in graph.adjacency_list
    
    def test_get_execution_order_linear(self):
        task1 = Task(id="task-1", description="Task 1", goal_id="goal-1", dependencies=[])
        task2 = Task(id="task-2", description="Task 2", goal_id="goal-1", dependencies=["task-1"])
        task3 = Task(id="task-3", description="Task 3", goal_id="goal-1", dependencies=["task-2"])
        
        graph = DependencyGraph(tasks=[task1, task2, task3])
        execution_order = graph.get_execution_order()
        
        assert len(execution_order) == 3
        assert execution_order[0] == ["task-1"]
        assert execution_order[1] == ["task-2"]
        assert execution_order[2] == ["task-3"]
    
    def test_get_execution_order_parallel(self):
        task1 = Task(id="task-1", description="Task 1", goal_id="goal-1", dependencies=[])
        task2 = Task(id="task-2", description="Task 2", goal_id="goal-1", dependencies=[])
        task3 = Task(id="task-3", description="Task 3", goal_id="goal-1", dependencies=["task-1", "task-2"])
        
        graph = DependencyGraph(tasks=[task1, task2, task3])
        execution_order = graph.get_execution_order()
        
        assert len(execution_order) == 2
        assert set(execution_order[0]) == {"task-1", "task-2"}
        assert execution_order[1] == ["task-3"]
    
    def test_has_cycles_no_cycle(self):
        task1 = Task(id="task-1", description="Task 1", goal_id="goal-1", dependencies=[])
        task2 = Task(id="task-2", description="Task 2", goal_id="goal-1", dependencies=["task-1"])
        
        graph = DependencyGraph(tasks=[task1, task2])
        assert graph.has_cycles() is False
    
    def test_has_cycles_with_cycle(self):
        task1 = Task(id="task-1", description="Task 1", goal_id="goal-1", dependencies=["task-2"])
        task2 = Task(id="task-2", description="Task 2", goal_id="goal-1", dependencies=["task-1"])
        
        graph = DependencyGraph(tasks=[task1, task2])
        assert graph.has_cycles() is True


class TestImplementation:
    """Tests for Implementation model."""
    
    def test_implementation_creation(self):
        impl = Implementation(
            approach_name="Approach A",
            description="Use pattern X",
            pros=["Fast", "Simple"],
            cons=["Limited"],
            complexity="low",
            code_example="def foo(): pass"
        )
        assert impl.approach_name == "Approach A"
        assert len(impl.pros) == 2
        assert len(impl.cons) == 1
        assert impl.complexity == "low"
    
    def test_implementation_str(self):
        impl = Implementation(
            approach_name="Direct Implementation",
            description="Test",
            complexity="high"
        )
        impl_str = str(impl)
        assert "Direct Implementation" in impl_str
        assert "high" in impl_str


class TestFileModification:
    """Tests for FileModification model."""
    
    def test_file_modification_creation(self):
        mod = FileModification(
            file_path="src/main.py",
            modification_type="update",
            description="Add new function",
            code_snippet="def new_func(): pass"
        )
        assert mod.file_path == "src/main.py"
        assert mod.modification_type == "update"
        assert mod.backup_recommended is True
    
    def test_file_modification_with_line_numbers(self):
        mod = FileModification(
            file_path="test.py",
            modification_type="update",
            description="Update line 10",
            line_numbers=(10, 15)
        )
        assert mod.line_numbers == (10, 15)
    
    def test_file_modification_str(self):
        mod = FileModification(
            file_path="file.py",
            modification_type="create",
            description="New file"
        )
        mod_str = str(mod)
        assert "create" in mod_str
        assert "file.py" in mod_str
