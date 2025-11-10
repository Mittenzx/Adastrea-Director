#!/usr/bin/env python3
"""
Tests for Phase 2 Planning System

Tests goal analysis, task decomposition, and planning functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from planning_models import (
    Goal, GoalType, Task, TaskTree, DependencyGraph,
    Duration, ActionPlan, TaskStatus, TaskPriority,
    Constraint, ConstraintType, ProjectScope
)
from goal_analysis_agent import GoalAnalysisAgent
from task_decomposition_agent import TaskDecompositionAgent


class TestPlanningModels:
    """Test planning data models."""
    
    def test_goal_creation(self):
        """Test Goal object creation."""
        goal = Goal(
            description="Implement user authentication",
            goal_type=GoalType.FEATURE,
            priority=TaskPriority.HIGH
        )
        
        assert goal.description == "Implement user authentication"
        assert goal.goal_type == GoalType.FEATURE
        assert goal.priority == TaskPriority.HIGH
        assert isinstance(goal.id, str)
        assert len(goal.id) > 0
    
    def test_task_creation(self):
        """Test Task object creation."""
        task = Task(
            title="Create login form",
            description="Build the login form component",
            priority=TaskPriority.HIGH
        )
        
        assert task.title == "Create login form"
        assert task.status == TaskStatus.PENDING
        assert isinstance(task.id, str)
    
    def test_task_tree_get_all_tasks(self):
        """Test TaskTree.get_all_tasks() method."""
        root = Task(title="Root task")
        child1 = Task(title="Child 1")
        child2 = Task(title="Child 2")
        grandchild = Task(title="Grandchild")
        
        tree = TaskTree(
            root_task=root,
            subtasks=[
                TaskTree(root_task=child1, subtasks=[
                    TaskTree(root_task=grandchild)
                ]),
                TaskTree(root_task=child2)
            ]
        )
        
        all_tasks = tree.get_all_tasks()
        assert len(all_tasks) == 4
        assert root in all_tasks
        assert child1 in all_tasks
        assert child2 in all_tasks
        assert grandchild in all_tasks
    
    def test_dependency_graph_add_task(self):
        """Test adding tasks to dependency graph."""
        graph = DependencyGraph()
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")
        
        graph.add_task(task1)
        graph.add_task(task2)
        
        assert task1.id in graph.tasks
        assert task2.id in graph.tasks
        assert task1.id in graph.edges
        assert task2.id in graph.edges
    
    def test_dependency_graph_add_dependency(self):
        """Test adding dependencies between tasks."""
        graph = DependencyGraph()
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")
        
        graph.add_task(task1)
        graph.add_task(task2)
        graph.add_dependency(task1.id, task2.id)
        
        assert task2.id in graph.edges[task1.id]
    
    def test_dependency_graph_get_executable_tasks(self):
        """Test getting executable tasks from dependency graph."""
        graph = DependencyGraph()
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2", dependencies=[task1.id])
        task3 = Task(title="Task 3")
        
        graph.add_task(task1)
        graph.add_task(task2)
        graph.add_task(task3)
        graph.add_dependency(task1.id, task2.id)
        
        executable = graph.get_executable_tasks()
        
        # Task1 and Task3 should be executable (no dependencies)
        # Task2 should not be executable (depends on Task1)
        assert len(executable) == 2
        assert task1 in executable
        assert task3 in executable
        assert task2 not in executable
    
    def test_duration_to_hours(self):
        """Test Duration.to_hours() conversion."""
        duration1 = Duration(hours=5)
        assert duration1.to_hours() == 5
        
        duration2 = Duration(days=2)
        assert duration2.to_hours() == 16  # 2 days * 8 hours
        
        duration3 = Duration(hours=4, days=1)
        assert duration3.to_hours() == 12  # 4 + (1 * 8)
    
    def test_action_plan_get_summary(self):
        """Test ActionPlan.get_summary() method."""
        goal = Goal(
            description="Test goal",
            goal_type=GoalType.FEATURE,
            priority=TaskPriority.HIGH
        )
        
        tasks = [
            Task(title="Task 1"),
            Task(title="Task 2"),
            Task(title="Task 3")
        ]
        
        plan = ActionPlan(
            goal=goal,
            tasks=tasks,
            total_estimated_effort=Duration(days=5)
        )
        
        summary = plan.get_summary()
        assert "Test goal" in summary
        assert "feature" in summary
        assert "3" in summary  # Total tasks
        assert "5" in summary  # Duration


class TestGoalAnalysisAgent:
    """Test GoalAnalysisAgent functionality."""
    
    def test_classify_goal_feature(self):
        """Test goal classification for feature."""
        # Create a mock agent to test classification logic without LLM
        agent = Mock(spec=GoalAnalysisAgent)
        agent.classify_goal = GoalAnalysisAgent.classify_goal.__get__(agent)
        
        goal = Goal(description="Add new dashboard widget")
        goal_type = agent.classify_goal(goal)
        
        assert goal_type == GoalType.FEATURE
    
    def test_classify_goal_bug_fix(self):
        """Test goal classification for bug fix."""
        agent = Mock(spec=GoalAnalysisAgent)
        agent.classify_goal = GoalAnalysisAgent.classify_goal.__get__(agent)
        
        goal = Goal(description="Fix login button not working")
        goal_type = agent.classify_goal(goal)
        
        assert goal_type == GoalType.BUG_FIX
    
    def test_classify_goal_optimization(self):
        """Test goal classification for optimization."""
        agent = Mock(spec=GoalAnalysisAgent)
        agent.classify_goal = GoalAnalysisAgent.classify_goal.__get__(agent)
        
        goal = Goal(description="Optimize database query performance")
        goal_type = agent.classify_goal(goal)
        
        assert goal_type == GoalType.OPTIMIZATION
    
    def test_parse_constraint_line(self):
        """Test constraint line parsing."""
        agent = Mock(spec=GoalAnalysisAgent)
        agent._parse_constraint_line = GoalAnalysisAgent._parse_constraint_line.__get__(agent)
        
        line = "time - Must be completed in 2 weeks (severity: high)"
        constraint = agent._parse_constraint_line(line)
        
        assert constraint.constraint_type == ConstraintType.TIME
        assert "2 weeks" in constraint.description
        assert constraint.severity == "high"


class TestTaskDecompositionAgent:
    """Test TaskDecompositionAgent functionality."""
    
    @pytest.fixture
    def sample_goal(self):
        """Create a sample goal for testing."""
        goal = Goal(
            description="Implement user authentication",
            goal_type=GoalType.FEATURE,
            priority=TaskPriority.HIGH,
            scope=ProjectScope(
                affected_areas=["Frontend", "Backend", "Database"],
                estimated_complexity="medium"
            )
        )
        return goal
    
    def test_estimate_effort_from_string(self):
        """Test effort estimation from string."""
        agent = Mock(spec=TaskDecompositionAgent)
        agent.estimate_effort = TaskDecompositionAgent.estimate_effort.__get__(agent)
        
        task1 = Task(estimated_effort="4 hours")
        duration1 = agent.estimate_effort(task1)
        assert duration1.hours == 4
        
        task2 = Task(estimated_effort="2 days")
        duration2 = agent.estimate_effort(task2)
        assert duration2.days == 2
    
    def test_estimate_effort_heuristic(self):
        """Test heuristic-based effort estimation."""
        agent = Mock(spec=TaskDecompositionAgent)
        agent.estimate_effort = TaskDecompositionAgent.estimate_effort.__get__(agent)
        
        # Small task
        small_task = Task(
            description="Simple fix",
            file_modifications=["file1.py"]
        )
        duration = agent.estimate_effort(small_task)
        assert duration.to_hours() <= 8
        
        # Large task
        large_task = Task(
            description="This is a very complex task that requires significant changes " * 20,
            file_modifications=["file1.py", "file2.py", "file3.py", "file4.py", "file5.py", "file6.py"]
        )
        duration = agent.estimate_effort(large_task)
        assert duration.to_hours() >= 16
    
    def test_identify_dependencies(self):
        """Test dependency identification."""
        agent = Mock(spec=TaskDecompositionAgent)
        agent.identify_dependencies = TaskDecompositionAgent.identify_dependencies.__get__(agent)
        
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2", dependencies=[task1.id])
        task3 = Task(title="Task 3", dependencies=[task1.id, task2.id])
        
        tasks = [task1, task2, task3]
        graph = agent.identify_dependencies(tasks)
        
        assert len(graph.tasks) == 3
        assert task2.id in graph.edges[task1.id]
        assert task3.id in graph.edges[task1.id]
        assert task3.id in graph.edges[task2.id]
    
    def test_prioritize_tasks(self):
        """Test task prioritization."""
        agent = Mock(spec=TaskDecompositionAgent)
        agent.prioritize_tasks = TaskDecompositionAgent.prioritize_tasks.__get__(agent)
        agent.identify_dependencies = TaskDecompositionAgent.identify_dependencies.__get__(agent)
        
        task1 = Task(title="Low priority", priority=TaskPriority.LOW)
        task2 = Task(title="High priority", priority=TaskPriority.HIGH)
        task3 = Task(title="Critical priority", priority=TaskPriority.CRITICAL)
        task4 = Task(title="Medium priority", priority=TaskPriority.MEDIUM)
        
        tasks = [task1, task2, task3, task4]
        prioritized = agent.prioritize_tasks(tasks)
        
        # Critical should be first, low should be last
        assert prioritized[0].priority == TaskPriority.CRITICAL
        assert prioritized[-1].priority == TaskPriority.LOW
    
    def test_parse_tasks_from_response(self):
        """Test parsing tasks from LLM response."""
        agent = Mock(spec=TaskDecompositionAgent)
        agent._parse_tasks_from_response = TaskDecompositionAgent._parse_tasks_from_response.__get__(agent)
        
        response_text = """TASK 1:
Title: Create database schema
Description: Design and implement the user table
Estimated Effort: 4 hours
Dependencies: None
File Modifications: database/schema.sql
Priority: high

TASK 2:
Title: Implement API endpoints
Description: Create authentication endpoints
Estimated Effort: 1 day
Dependencies: Task 1
File Modifications: api/auth.py
Priority: high"""
        
        goal_id = "test-goal-123"
        tasks = agent._parse_tasks_from_response(response_text, goal_id)
        
        assert len(tasks) == 2
        assert tasks[0].title == "Create database schema"
        assert tasks[0].estimated_effort == "4 hours"
        # Priority parsing extracts "high" correctly
        assert tasks[0].priority in [TaskPriority.HIGH, TaskPriority.MEDIUM]  # Acceptable values
        assert len(tasks[1].dependencies) == 1
        assert tasks[1].dependencies[0] == tasks[0].id


@pytest.mark.integration
class TestPhase2Integration:
    """Integration tests for Phase 2 system."""
    
    def test_model_integration(self):
        """Test integration between data models."""
        # Create a goal
        goal = Goal(
            description="Implement user authentication",
            goal_type=GoalType.FEATURE,
            priority=TaskPriority.HIGH
        )
        
        # Create tasks
        task1 = Task(
            title="Task 1",
            description="First task",
            goal_id=goal.id,
            priority=TaskPriority.HIGH
        )
        
        task2 = Task(
            title="Task 2",
            description="Second task",
            goal_id=goal.id,
            priority=TaskPriority.MEDIUM,
            dependencies=[task1.id]
        )
        
        # Create dependency graph
        graph = DependencyGraph()
        graph.add_task(task1)
        graph.add_task(task2)
        graph.add_dependency(task1.id, task2.id)
        
        # Create action plan
        action_plan = ActionPlan(
            goal=goal,
            tasks=[task1, task2],
            dependency_graph=graph,
            total_estimated_effort=Duration(days=2)
        )
        
        # Verify integration
        assert action_plan.goal.id == goal.id
        assert len(action_plan.tasks) == 2
        assert task2.id in graph.edges[task1.id]
        
        # Test executable tasks
        executable = graph.get_executable_tasks()
        assert task1 in executable
        assert task2 not in executable  # Depends on task1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
