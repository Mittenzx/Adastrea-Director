#!/usr/bin/env python3
"""
Planning Example: Goal Decomposition System Demo

This example demonstrates how to use the planning agents
to decompose development goals into actionable tasks.

Usage:
    python examples/planning_example.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    from goal_analysis_agent import GoalAnalysisAgent
    from task_decomposition_agent import TaskDecompositionAgent
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    
except ImportError as e:
    print(f"Error: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

console = Console()


def print_header():
    """Print example header."""
    header = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║            Planning Example: Goal Decomposition           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    console.print(header, style="bold cyan")


def example_1_basic_goal_analysis():
    """Example 1: Basic goal analysis."""
    console.print("\n[bold]Example 1: Basic Goal Analysis[/bold]\n", style="green")
    
    # Initialize agent
    console.print("Initializing Goal Analysis Agent...", style="dim")
    goal_agent = GoalAnalysisAgent()
    
    # Define a goal
    goal_description = "Implement a real-time chat system with WebSocket support"
    console.print(f"\n[cyan]Goal:[/cyan] {goal_description}\n")
    
    # Parse the goal
    with console.status("[cyan]Analyzing goal...[/cyan]", spinner="dots"):
        goal = goal_agent.parse_goal(goal_description)
    
    # Display results
    console.print("[green]✓ Analysis complete![/green]\n")
    
    info_text = f"""
**Goal Type:** {goal.goal_type.value}
**Priority:** {goal.priority.value}
**Complexity:** {goal.scope.estimated_complexity if goal.scope else 'unknown'}

**Constraints Identified:** {len(goal.constraints)}
"""
    
    if goal.constraints:
        info_text += "\n**Constraint Details:**\n"
        for constraint in goal.constraints[:3]:  # Show first 3
            info_text += f"- {constraint.constraint_type.value}: {constraint.description}\n"
    
    if goal.scope and goal.scope.affected_areas:
        info_text += f"\n**Affected Areas:** {len(goal.scope.affected_areas)}\n"
        for area in goal.scope.affected_areas[:3]:  # Show first 3
            info_text += f"- {area}\n"
    
    console.print(Panel(info_text, title="Goal Analysis Results", border_style="cyan"))
    
    return goal


def example_2_task_decomposition(goal):
    """Example 2: Task decomposition."""
    console.print("\n\n[bold]Example 2: Task Decomposition[/bold]\n", style="green")
    
    # Initialize agent
    console.print("Initializing Task Decomposition Agent...", style="dim")
    task_agent = TaskDecompositionAgent()
    
    # Create action plan
    with console.status("[cyan]Breaking down into tasks...[/cyan]", spinner="dots"):
        action_plan = task_agent.create_action_plan(goal)
    
    console.print("[green]✓ Decomposition complete![/green]\n")
    
    # Display summary
    summary = f"""
**Total Tasks:** {len(action_plan.tasks)}
**Estimated Effort:** {action_plan.total_estimated_effort}
    """
    console.print(Panel(summary, title="Action Plan Summary", border_style="green"))
    
    # Display tasks in a table
    console.print("\n[bold]Generated Tasks:[/bold]\n")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Task", style="cyan")
    table.add_column("Priority", style="yellow")
    table.add_column("Estimated", style="green")
    
    for idx, task in enumerate(action_plan.tasks[:5], start=1):  # Show first 5
        effort = task.estimated_effort or "TBD"
        table.add_row(
            str(idx),
            task.title[:50] + "..." if len(task.title) > 50 else task.title,
            task.priority.value,
            effort
        )
    
    if len(action_plan.tasks) > 5:
        table.add_row("...", f"({len(action_plan.tasks) - 5} more tasks)", "", "")
    
    console.print(table)
    
    return action_plan


def example_3_dependency_analysis(action_plan):
    """Example 3: Dependency analysis."""
    console.print("\n\n[bold]Example 3: Dependency Analysis[/bold]\n", style="green")
    
    if not action_plan.dependency_graph:
        console.print("[yellow]No dependency graph available[/yellow]")
        return
    
    # Get executable tasks
    executable = action_plan.dependency_graph.get_executable_tasks()
    
    console.print(f"[cyan]Tasks ready to start immediately:[/cyan] {len(executable)}")
    
    if executable:
        console.print("\n[bold]Executable Tasks:[/bold]")
        for task in executable[:3]:  # Show first 3
            console.print(f"  • {task.title}", style="green")
        
        if len(executable) > 3:
            console.print(f"  ... and {len(executable) - 3} more")
    
    # Show dependency statistics
    total_edges = sum(len(deps) for deps in action_plan.dependency_graph.edges.values())
    console.print(f"\n[cyan]Total dependencies:[/cyan] {total_edges}")
    
    # Find tasks with most dependencies
    tasks_by_deps = sorted(
        action_plan.tasks,
        key=lambda t: len(t.dependencies),
        reverse=True
    )
    
    if tasks_by_deps[0].dependencies:
        console.print(f"\n[bold]Most complex task (by dependencies):[/bold]")
        console.print(f"  • {tasks_by_deps[0].title}", style="yellow")
        console.print(f"    Depends on: {len(tasks_by_deps[0].dependencies)} other task(s)")


def example_4_task_details(action_plan):
    """Example 4: Detailed task information."""
    console.print("\n\n[bold]Example 4: Task Details[/bold]\n", style="green")
    
    if not action_plan.tasks:
        return
    
    # Show details for first task
    task = action_plan.tasks[0]
    
    detail_text = f"""
**Title:** {task.title}

**Description:**
{task.description}

**Priority:** {task.priority.value}
**Status:** {task.status.value}
**Estimated Effort:** {task.estimated_effort or 'To be determined'}
    """
    
    if task.dependencies:
        detail_text += f"\n**Dependencies:** {len(task.dependencies)} task(s)"
    
    if task.file_modifications:
        detail_text += "\n\n**Files to Modify:**"
        for file in task.file_modifications[:5]:
            detail_text += f"\n- {file}"
        if len(task.file_modifications) > 5:
            detail_text += f"\n- ... and {len(task.file_modifications) - 5} more files"
    
    console.print(Panel(detail_text, title=f"Task 1: {task.title}", border_style="cyan"))


def example_5_programmatic_usage():
    """Example 5: Programmatic usage patterns."""
    console.print("\n\n[bold]Example 5: Programmatic Usage Patterns[/bold]\n", style="green")
    
    console.print("[cyan]Key usage patterns:[/cyan]\n")
    
    patterns = [
        ("Goal Classification", "goal_agent.classify_goal(goal)"),
        ("Constraint Identification", "goal_agent.identify_constraints(goal)"),
        ("Scope Determination", "goal_agent.determine_scope(goal)"),
        ("Task Decomposition", "task_agent.decompose_goal(goal)"),
        ("Effort Estimation", "task_agent.estimate_effort(task)"),
        ("Dependency Analysis", "task_agent.identify_dependencies(tasks)"),
        ("Task Prioritization", "task_agent.prioritize_tasks(tasks)"),
        ("Action Plan Creation", "task_agent.create_action_plan(goal)"),
    ]
    
    for name, code in patterns:
        console.print(f"  • [bold]{name}:[/bold]")
        console.print(f"    [dim]{code}[/dim]\n")


def main():
    """Run all examples."""
    print_header()
    
    console.print("\n[yellow]Note: This example requires a Gemini API key (set GEMINI_API_KEY environment variable).[/yellow]")
    console.print("[dim]Set GEMINI_API_KEY environment variable or create .env file (or LLM_PROVIDER=openai for legacy OpenAI support)[/dim]\n")
    
    try:
        # Example 1: Goal Analysis
        goal = example_1_basic_goal_analysis()
        
        # Example 2: Task Decomposition
        action_plan = example_2_task_decomposition(goal)
        
        # Example 3: Dependency Analysis
        example_3_dependency_analysis(action_plan)
        
        # Example 4: Task Details
        example_4_task_details(action_plan)
        
        # Example 5: Programmatic Usage
        example_5_programmatic_usage()
        
        console.print("\n[bold green]✓ All examples completed successfully![/bold green]\n")
        console.print("[cyan]Next steps:[/cyan]")
        console.print("  • Try planning_cli.py for interactive goal decomposition")
        console.print("  • Read the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki) for detailed documentation")
        console.print("  • Integrate with your development workflow\n")
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Examples interrupted by user[/yellow]\n")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        console.print("[yellow]Make sure you have:[/yellow]")
        console.print("  1. Set GEMINI_API_KEY environment variable (or LLM_PROVIDER=openai with OPENAI_API_KEY)")
        console.print("  2. Installed all requirements (pip install -r requirements.txt)")
        console.print("  3. Internet connection for API calls\n")
        raise


if __name__ == "__main__":
    main()
