#!/usr/bin/env python3
"""
Task Decomposition Agent for Phase 2 Planning

This agent is responsible for breaking down goals into actionable tasks.
It generates task hierarchies, estimates effort, identifies dependencies,
and prioritizes tasks.
"""

import re
import logging
from typing import List
from planning_models import (
    Goal, Task, TaskTree, DependencyGraph, Duration,
    TaskStatus, TaskPriority, ActionPlan
)
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

logger = logging.getLogger(__name__)


class TaskDecompositionAgent:
    """Agent responsible for breaking down goals into actionable tasks."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.3):
        """
        Initialize the task decomposition agent.
        
        Args:
            model_name: Name of the OpenAI model to use
            temperature: Temperature for response generation (lower for more focused)
        """
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self._initialize_chains()
    
    def _initialize_chains(self):
        """Initialize LLM chains for different decomposition tasks."""
        
        # Chain for decomposing goals into tasks
        decompose_template = """You are an expert software architect breaking down development goals into actionable tasks.

Given the following goal information:

Goal Description: {goal_description}
Goal Type: {goal_type}
Priority: {priority}
Complexity: {complexity}
Affected Areas: {affected_areas}

Break this goal down into specific, actionable tasks. For each task, provide:

Format your response as follows:

TASK 1:
Title: [Short, clear title]
Description: [Detailed description of what needs to be done]
Estimated Effort: [e.g., "2 hours", "1 day", "3 days"]
Dependencies: [Task numbers this depends on, or "None"]
File Modifications: [Files that need to be created/modified]
Priority: [critical/high/medium/low]

TASK 2:
[Same format]

...

Guidelines:
- Be specific and actionable
- Each task should be completable in 1-3 days maximum
- Break large tasks into smaller subtasks
- Identify dependencies clearly
- Consider testing tasks
- Include documentation tasks if needed
- Order tasks logically (foundations first)
- Aim for 3-10 tasks depending on goal complexity"""

        self.decompose_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=decompose_template,
                input_variables=[
                    "goal_description", "goal_type", "priority", 
                    "complexity", "affected_areas"
                ]
            )
        )
    
    def decompose_goal(self, goal: Goal) -> TaskTree:
        """
        Break down a goal into a hierarchical tree of tasks.
        
        Args:
            goal: The goal to decompose
            
        Returns:
            TaskTree with hierarchical task structure
        """
        # Prepare context for LLM
        affected_areas = ", ".join(goal.scope.affected_areas) if goal.scope else "Unknown"
        complexity = goal.scope.estimated_complexity if goal.scope else "medium"
        
        # Get LLM decomposition
        response = self.decompose_chain.invoke({
            "goal_description": goal.description,
            "goal_type": goal.goal_type.value,
            "priority": goal.priority.value,
            "complexity": complexity,
            "affected_areas": affected_areas
        })
        
        analysis_text = response["text"]
        
        # Parse tasks from response
        tasks = self._parse_tasks_from_response(analysis_text, goal.id)
        
        # Create root task representing the overall goal
        root_task = Task(
            title=f"Implement: {goal.description[:50]}" + ("..." if len(goal.description) > 50 else ""),
            description=goal.description,
            goal_id=goal.id,
            priority=goal.priority,
            status=TaskStatus.PENDING
        )
        
        # Create task tree
        task_tree = TaskTree(root_task=root_task)
        
        # Add parsed tasks as subtasks
        for task in tasks:
            task_tree.subtasks.append(TaskTree(root_task=task))
        
        return task_tree
    
    def _parse_tasks_from_response(self, response_text: str, goal_id: str) -> List[Task]:
        """
        Parse task definitions from LLM response.
        
        Args:
            response_text: Response from LLM
            goal_id: ID of the parent goal
            
        Returns:
            List of Task objects
        """
        tasks = []
        task_blocks = re.split(r'TASK \d+:', response_text, re.IGNORECASE)[1:]
        
        if not task_blocks or (len(task_blocks) == 1 and not task_blocks[0].strip()):
            logger.warning("No tasks found in LLM response. Response may not be in expected format.")
            return tasks
        
        for idx, block in enumerate(task_blocks, start=1):
            task = Task(goal_id=goal_id)
            
            # Parse title
            title_match = re.search(r'Title:\s*\[?(.*?)\]?(?:\n|$)', block, re.IGNORECASE)
            if title_match:
                task.title = title_match.group(1).strip()
            else:
                task.title = f"Task {idx}"
            
            # Parse description
            desc_match = re.search(
                r'Description:\s*\[?(.*?)\]?(?=Estimated Effort:|$)', 
                block, 
                re.IGNORECASE | re.DOTALL
            )
            if desc_match:
                task.description = desc_match.group(1).strip()
            
            # Parse estimated effort
            effort_match = re.search(
                r'Estimated Effort:\s*\[?(.*?)\]?(?:\n|$)', 
                block, 
                re.IGNORECASE
            )
            if effort_match:
                task.estimated_effort = effort_match.group(1).strip()
            
            # Parse dependencies (task numbers)
            deps_match = re.search(
                r'Dependencies:\s*\[?(.*?)\]?(?:\n|$)', 
                block, 
                re.IGNORECASE
            )
            if deps_match:
                deps_text = deps_match.group(1).strip().lower()
                if deps_text != "none":
                    # Extract task numbers
                    task_nums = re.findall(r'\d+', deps_text)
                    # We'll resolve these to actual task IDs after all tasks are created
                    task.metadata['dependency_indices'] = [int(n) for n in task_nums]
            
            # Parse file modifications
            files_match = re.search(
                r'File Modifications:\s*\[?(.*?)\]?(?=Priority:|$)', 
                block, 
                re.IGNORECASE | re.DOTALL
            )
            if files_match:
                files_text = files_match.group(1).strip()
                # Split by commas or newlines
                files = re.split(r'[,\n]', files_text)
                task.file_modifications = [f.strip() for f in files if f.strip()]
            
            # Parse priority
            priority_match = re.search(r'Priority:\s*\[?(\w+)', block, re.IGNORECASE)
            if priority_match:
                try:
                    task.priority = TaskPriority(priority_match.group(1).upper())
                except ValueError:
                    task.priority = TaskPriority.MEDIUM
            
            tasks.append(task)
        
        # Resolve dependencies by index
        for task in tasks:
            if 'dependency_indices' in task.metadata:
                for dep_idx in task.metadata['dependency_indices']:
                    if 1 <= dep_idx <= len(tasks):
                        task.dependencies.append(tasks[dep_idx - 1].id)
                    else:
                        logger.warning(
                            f"Invalid dependency index {dep_idx} for task '{task.title}'. "
                            f"Valid range: 1-{len(tasks)}"
                        )
                del task.metadata['dependency_indices']
        
        return tasks
    
    def estimate_effort(self, task: Task) -> Duration:
        """
        Estimate the effort required to complete a task.
        
        Args:
            task: The task to estimate
            
        Returns:
            Duration object with estimated effort
        """
        if task.estimated_effort:
            # Parse the estimated effort string
            effort_str = task.estimated_effort.lower()
            
            # Extract hours (supports both "hour" and "hours")
            hours_match = re.search(r'(\d+(?:\.\d+)?)\s*hours?', effort_str)
            if hours_match:
                return Duration(hours=float(hours_match.group(1)))
            
            # Extract days (supports both "day" and "days")
            days_match = re.search(r'(\d+(?:\.\d+)?)\s*days?', effort_str)
            if days_match:
                return Duration(days=float(days_match.group(1)))
        
        # Default estimate based on complexity heuristics
        description_length = len(task.description)
        files_count = len(task.file_modifications)
        
        # Simple heuristic: more files and longer description = more effort
        if files_count > 5 or description_length > 500:
            return Duration(days=3)
        elif files_count > 2 or description_length > 200:
            return Duration(days=1)
        else:
            return Duration(hours=4)
    
    def identify_dependencies(self, tasks: List[Task]) -> DependencyGraph:
        """
        Identify dependencies between tasks and create a dependency graph.
        
        Args:
            tasks: List of tasks to analyze
            
        Returns:
            DependencyGraph showing task dependencies
        """
        graph = DependencyGraph()
        
        # Add all tasks to graph
        for task in tasks:
            graph.add_task(task)
        
        # Add dependency edges from task metadata
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in graph.tasks:
                    graph.add_dependency(dep_id, task.id)
        
        return graph
    
    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Order tasks by priority and dependencies.
        
        Args:
            tasks: List of tasks to prioritize
            
        Returns:
            Sorted list of tasks
        """
        # Create dependency graph
        graph = self.identify_dependencies(tasks)
        
        # Priority order
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        
        def task_sort_key(task: Task):
            # First by priority
            priority_value = priority_order.get(task.priority, 2)
            
            # Then by number of dependencies (fewer dependencies first)
            dep_count = len(task.dependencies)
            
            # Then by number of tasks depending on this (more dependents first)
            dependents_count = len(graph.edges.get(task.id, []))
            
            return (priority_value, dep_count, -dependents_count)
        
        return sorted(tasks, key=task_sort_key)
    
    def create_action_plan(self, goal: Goal) -> ActionPlan:
        """
        Create a comprehensive action plan for a goal.
        
        Args:
            goal: The goal to plan for
            
        Returns:
            Complete ActionPlan with tasks, dependencies, and estimates
        """
        # Decompose goal into tasks
        task_tree = self.decompose_goal(goal)
        all_tasks = task_tree.get_all_tasks()[1:]  # Skip root task
        
        # Identify dependencies
        dependency_graph = self.identify_dependencies(all_tasks)
        
        # Calculate total estimated effort
        total_effort = Duration()
        for task in all_tasks:
            task_effort = self.estimate_effort(task)
            total_effort.hours += task_effort.hours
            total_effort.days += task_effort.days
        
        # Normalize the total effort (convert excess hours to days)
        total_effort.normalize()
        
        # Prioritize tasks
        prioritized_tasks = self.prioritize_tasks(all_tasks)
        
        # Create action plan
        action_plan = ActionPlan(
            goal=goal,
            tasks=prioritized_tasks,
            dependency_graph=dependency_graph,
            total_estimated_effort=total_effort
        )
        
        return action_plan
