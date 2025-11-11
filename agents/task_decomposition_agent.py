"""
Task Decomposition Agent

Responsible for breaking down goals into actionable tasks.
"""

import uuid
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from agents.models import (
    Goal,
    Task,
    TaskTree,
    TaskPriority,
    DependencyGraph,
    Duration,
)


class TaskDecompositionOutput(BaseModel):
    """Pydantic model for structured task decomposition output."""
    tasks: List[Dict[str, Any]] = Field(description="List of tasks with description, priority, estimated_hours, and dependencies")


class TaskDecompositionAgent:
    """
    Agent responsible for decomposing goals into actionable tasks.
    
    This agent breaks down high-level goals into a hierarchy of concrete tasks,
    estimates effort, identifies dependencies, and prioritizes work.
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.3,
    ):
        """
        Initialize the Task Decomposition Agent.
        
        Args:
            model_name: Name of the OpenAI model to use
            temperature: Temperature for response generation
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
        )
        
        # Setup output parser
        self.parser = PydanticOutputParser(pydantic_object=TaskDecompositionOutput)
        
        # Create prompt template
        self.prompt_template = PromptTemplate(
            template="""You are an expert software development planning assistant specializing in breaking down development goals into actionable tasks.

Goal Information:
- Description: {goal_description}
- Type: {goal_type}
- Complexity: {complexity}
- Key Objectives: {key_objectives}
- Constraints: {constraints}

Break this goal down into specific, actionable tasks. For each task:
1. Provide a clear, concise description (action-oriented)
2. Estimate effort in hours (be realistic)
3. Assign priority (critical, high, medium, low)
4. Identify dependencies on other tasks (use task descriptions for reference)
5. Specify files to modify or create if applicable

Guidelines:
- Create atomic tasks that can be completed independently (when dependencies allow)
- Include setup, implementation, testing, and documentation tasks
- Consider the logical order of tasks
- Break down complex tasks into subtasks
- Typical task sizes: 1-8 hours for implementation, 0.5-2 hours for testing
- Include code review as a task for significant changes

Provide 5-15 tasks depending on goal complexity.

{format_instructions}

Generate the task decomposition in the specified JSON format.
""",
            input_variables=["goal_description", "goal_type", "complexity", "key_objectives", "constraints"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
    
    def decompose_goal(self, goal: Goal) -> TaskTree:
        """
        Decompose a goal into a hierarchy of actionable tasks.
        
        Args:
            goal: Goal object to decompose
        
        Returns:
            TaskTree containing the decomposed tasks
        """
        # Prepare context for LLM
        key_objectives = goal.metadata.get("key_objectives", [])
        constraints_str = "\n".join([f"- {c.description} ({c.constraint_type})" for c in goal.constraints])
        
        # Generate task decomposition
        chain = self.prompt_template | self.llm | self.parser
        result = chain.invoke({
            "goal_description": goal.description,
            "goal_type": goal.goal_type.value,
            "complexity": goal.scope.estimated_complexity if goal.scope else "medium",
            "key_objectives": "\n".join([f"- {obj}" for obj in key_objectives]),
            "constraints": constraints_str if constraints_str else "None specified",
        })
        
        # Convert to Task objects
        tasks = []
        task_id_map = {}  # Map descriptions to IDs for dependency resolution
        
        for task_dict in result.tasks:
            task_id = str(uuid.uuid4())[:8]
            description = task_dict.get("description", "")
            
            # Parse priority
            priority = TaskPriority.MEDIUM
            priority_str = task_dict.get("priority", "medium").lower()
            try:
                priority = TaskPriority(priority_str)
            except ValueError:
                # If the priority string is invalid, default to MEDIUM priority.
                pass
            
            # Parse duration
            estimated_hours = task_dict.get("estimated_hours", 2.0)
            duration = Duration(hours=float(estimated_hours), confidence=0.7)
            
            # Create task
            task = Task(
                id=task_id,
                description=description,
                goal_id=goal.id,
                priority=priority,
                estimated_duration=duration,
                dependencies=[],  # Will be filled in second pass
                files_to_modify=task_dict.get("files_to_modify", []),
                files_to_create=task_dict.get("files_to_create", []),
            )
            
            tasks.append(task)
            task_id_map[description] = task_id
        
        # Second pass: resolve dependencies
        for i, task_dict in enumerate(result.tasks):
            dep_descriptions = task_dict.get("dependencies", [])
            for dep_desc in dep_descriptions:
                # Try to match dependency description to task
                if dep_desc in task_id_map:
                    tasks[i].dependencies.append(task_id_map[dep_desc])
        
        # Calculate total duration
        total_hours = sum(task.estimated_duration.hours for task in tasks if task.estimated_duration)
        total_duration = Duration(hours=total_hours, confidence=0.6)
        
        # Create TaskTree
        task_tree = TaskTree(
            goal=goal,
            root_tasks=tasks,
            total_estimated_duration=total_duration,
        )
        
        return task_tree
    
    def estimate_effort(self, task: Task) -> Duration:
        """
        Estimate or re-estimate the effort required for a task.
        
        Args:
            task: Task to estimate
        
        Returns:
            Duration object with estimated effort
        """
        if task.estimated_duration:
            return task.estimated_duration
        
        # Simple heuristic-based estimation if no estimate exists
        base_hours = 4.0  # Default to 4 hours
        
        # Adjust based on various factors
        if task.files_to_create:
            base_hours += len(task.files_to_create) * 2
        if task.files_to_modify:
            base_hours += len(task.files_to_modify) * 1
        if task.subtasks:
            subtask_hours = sum(self.estimate_effort(st).hours for st in task.subtasks)
            base_hours = subtask_hours
        
        # Cap at reasonable maximum
        base_hours = min(base_hours, 40.0)
        
        return Duration(hours=base_hours, confidence=0.5)
    
    def identify_dependencies(self, tasks: List[Task]) -> DependencyGraph:
        """
        Analyze and identify dependencies between tasks.
        
        Args:
            tasks: List of tasks to analyze
        
        Returns:
            DependencyGraph object
        """
        return DependencyGraph(tasks=tasks)
    
    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Order tasks by priority and dependencies.
        
        Args:
            tasks: List of tasks to prioritize
        
        Returns:
            Sorted list of tasks
        """
        # Create dependency graph
        dep_graph = DependencyGraph(tasks=tasks)
        
        # Get execution order (respects dependencies)
        execution_levels = dep_graph.get_execution_order()
        
        # Flatten while preserving level groupings
        prioritized = []
        for level in execution_levels:
            # Within each level, sort by priority
            level_tasks = [t for t in tasks if t.id in level]
            level_tasks.sort(key=lambda t: (
                # Priority order: CRITICAL, HIGH, MEDIUM, LOW
                ["critical", "high", "medium", "low"].index(t.priority.value)
            ))
            prioritized.extend(level_tasks)
        
        return prioritized
    
    def refine_task_breakdown(self, task: Task, max_hours: float = 8.0) -> List[Task]:
        """
        Refine a task by breaking it into smaller subtasks if it's too large.
        
        Args:
            task: Task to potentially break down
            max_hours: Maximum hours for a single task
        
        Returns:
            List of tasks (original task or broken down subtasks)
        """
        if not task.estimated_duration or task.estimated_duration.hours <= max_hours:
            return [task]
        
        # Simple breakdown based on file operations
        subtasks = []
        
        if task.files_to_create:
            # Create separate tasks for file creation
            for i, file_path in enumerate(task.files_to_create):
                subtask_id = f"{task.id}-create-{i}"
                subtask = Task(
                    id=subtask_id,
                    description=f"Create {file_path}",
                    goal_id=task.goal_id,
                    priority=task.priority,
                    estimated_duration=Duration(hours=2.0),
                    files_to_create=[file_path],
                )
                subtasks.append(subtask)
        
        if task.files_to_modify:
            # Create separate tasks for file modifications
            for i, file_path in enumerate(task.files_to_modify):
                subtask_id = f"{task.id}-modify-{i}"
                subtask = Task(
                    id=subtask_id,
                    description=f"Modify {file_path} for: {task.description}",
                    goal_id=task.goal_id,
                    priority=task.priority,
                    estimated_duration=Duration(hours=1.5),
                    files_to_modify=[file_path],
                    dependencies=[t.id for t in subtasks if t.files_to_create],  # Depend on creation tasks
                )
                subtasks.append(subtask)
        
        if not subtasks:
            # If no file operations, just split by time
            num_subtasks = int(task.estimated_duration.hours / max_hours) + 1
            hours_per_subtask = task.estimated_duration.hours / num_subtasks
            
            for i in range(num_subtasks):
                subtask_id = f"{task.id}-part-{i+1}"
                subtask = Task(
                    id=subtask_id,
                    description=f"{task.description} (Part {i+1}/{num_subtasks})",
                    goal_id=task.goal_id,
                    priority=task.priority,
                    estimated_duration=Duration(hours=hours_per_subtask),
                    dependencies=[f"{task.id}-part-{i}"] if i > 0 else [],
                )
                subtasks.append(subtask)
        
        return subtasks if subtasks else [task]
