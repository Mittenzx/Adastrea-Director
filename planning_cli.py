#!/usr/bin/env python3
"""
Planning CLI - Goal Decomposition

Command-line interface for goal analysis and task decomposition.
Allows users to input development goals and receive actionable task plans.
"""

import sys
import argparse
from typing import Optional
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    
    from agents.goal_analysis_agent import GoalAnalysisAgent
    from agents.task_decomposition_agent import TaskDecompositionAgent
    from agents.models import ActionPlan
    
except ImportError as e:
    print(f"Error: Missing required dependencies: {e}")
    print("Please install requirements.txt")
    sys.exit(1)

console = Console(legacy_windows=False)


class PlanningCLI:
    """Command-line interface for goal decomposition and planning."""
    
    def __init__(self, debug: bool = False):
        """Initialize the planning CLI."""
        self.goal_agent = GoalAnalysisAgent()
        self.task_agent = TaskDecompositionAgent()
        self.debug = debug
    
    def print_banner(self):
        """Print the application banner."""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              🎯 ADASTREA DIRECTOR                         ║
║              Goal Decomposition System                    ║
║                                                           ║
║         Break down goals into actionable tasks            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """
        console.print(banner, style="bold cyan")
    
    def analyze_goal(self, goal_description: str) -> ActionPlan:
        """
        Analyze a goal and create an action plan.
        
        Args:
            goal_description: Description of the development goal
            
        Returns:
            Complete ActionPlan
        """
        with console.status("[cyan]Analyzing goal...[/cyan]", spinner="dots"):
            # Parse and analyze the goal
            goal = self.goal_agent.parse_goal(goal_description)
        
        console.print("[green]✓ Goal analysis complete[/green]\n")
        
        # Display goal analysis
        self.display_goal_analysis(goal)
        
        with console.status("[cyan]Breaking down into tasks...[/cyan]", spinner="dots"):
            # Create action plan with tasks
            action_plan = self.task_agent.create_action_plan(goal)
        
        console.print("[green]✓ Task decomposition complete[/green]\n")
        
        return action_plan
    
    def display_goal_analysis(self, goal):
        """Display goal analysis results."""
        analysis_text = f"""
**Goal Analysis**

**Type:** {goal.goal_type.value}
**Priority:** {goal.priority.value}

**Description:**
{goal.description}

**Scope:**
- Complexity: {goal.scope.estimated_complexity if goal.scope else 'unknown'}
- Requires New Dependencies: {'Yes' if goal.scope and goal.scope.requires_new_dependencies else 'No'}
- Breaking Changes: {'Yes' if goal.scope and goal.scope.breaking_changes else 'No'}
        """
        
        if goal.scope and goal.scope.affected_areas:
            analysis_text += "\n**Affected Areas:**\n"
            for area in goal.scope.affected_areas:
                analysis_text += f"- {area}\n"
        
        if goal.constraints:
            analysis_text += "\n**Constraints:**\n"
            for constraint in goal.constraints:
                analysis_text += f"- {constraint.constraint_type.value}: {constraint.description} (severity: {constraint.severity})\n"
        
        console.print(Panel(Markdown(analysis_text), title="Goal Analysis", border_style="cyan"))
    
    def display_action_plan(self, action_plan: ActionPlan):
        """Display the complete action plan."""
        # Summary
        summary_text = action_plan.get_summary()
        console.print(Panel(summary_text, title="Action Plan Summary", border_style="green"))
        console.print()
        
        # Tasks table
        table = Table(title="Tasks", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Title", style="cyan")
        table.add_column("Priority", style="yellow")
        table.add_column("Estimated", style="green")
        table.add_column("Dependencies", style="dim")
        
        for idx, task in enumerate(action_plan.tasks, start=1):
            deps = str(len(task.dependencies)) if task.dependencies else "None"
            effort = task.estimated_effort or "TBD"
            
            table.add_row(
                str(idx),
                task.title,
                task.priority.value,
                effort,
                deps
            )
        
        console.print(table)
        console.print()
        
        # Task details
        console.print("[bold cyan]Task Details:[/bold cyan]\n")
        for idx, task in enumerate(action_plan.tasks, start=1):
            task_panel = self._format_task_detail(idx, task)
            console.print(task_panel)
            console.print()
        
        # Dependency information
        if action_plan.dependency_graph:
            executable = action_plan.dependency_graph.get_executable_tasks()
            if executable:
                console.print(f"[green]✓ {len(executable)} tasks can be started immediately[/green]")
    
    def _format_task_detail(self, idx: int, task) -> Panel:
        """Format a task detail panel."""
        detail_text = f"""**Description:**
{task.description}

**Estimated Effort:** {task.estimated_effort or 'TBD'}
**Priority:** {task.priority.value}
**Status:** {task.status.value}
"""
        
        if task.dependencies:
            detail_text += f"\n**Dependencies:** {len(task.dependencies)} task(s)"
        
        if task.file_modifications:
            detail_text += "\n\n**File Modifications:**\n"
            for file in task.file_modifications:
                detail_text += f"- {file}\n"
        
        return Panel(
            Markdown(detail_text),
            title=f"Task {idx}: {task.title}",
            border_style="cyan"
        )
    
    def run_interactive(self):
        """Run in interactive mode."""
        self.print_banner()
        console.print("\n[cyan]Enter a development goal to decompose into tasks.[/cyan]")
        console.print("[dim]Type 'quit' to exit.[/dim]\n")
        
        while True:
            try:
                goal_description = console.input("[bold green]Goal:[/bold green] ").strip()
                
                if not goal_description:
                    continue
                
                if goal_description.lower() in ['quit', 'exit', 'q']:
                    console.print("\n[cyan]Goodbye![/cyan]\n")
                    break
                
                # Analyze and decompose the goal
                action_plan = self.analyze_goal(goal_description)
                
                # Display results
                self.display_action_plan(action_plan)
                
                console.print()
                
            except KeyboardInterrupt:
                console.print("\n\n[cyan]Interrupted. Type 'quit' to exit.[/cyan]\n")
                continue
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]\n")
                if self.debug:
                    import traceback
                    console.print("[dim]Full traceback:[/dim]")
                    traceback.print_exc()
    
    def run_single_goal(self, goal_description: str, output_file: Optional[str] = None):
        """
        Process a single goal and optionally save to file.
        
        Args:
            goal_description: Description of the goal
            output_file: Optional file path to save the action plan
        """
        self.print_banner()
        console.print()
        
        # Analyze and decompose
        action_plan = self.analyze_goal(goal_description)
        
        # Display results
        self.display_action_plan(action_plan)
        
        # Save to file if requested
        if output_file:
            self._save_action_plan(action_plan, output_file)
            console.print(f"\n[green]✓ Action plan saved to {output_file}[/green]\n")
    
    def _save_action_plan(self, action_plan: ActionPlan, output_file: str):
        """Save action plan to a markdown file."""
        output_path = Path(output_file)
        
        try:
            # Ensure parent directory exists
            if output_path.parent and not output_path.parent.exists():
                output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with output_path.open('w', encoding='utf-8') as f:
                f.write(f"# Action Plan: {action_plan.goal.description}\n\n")
                f.write(f"**Created:** {action_plan.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"## Goal Analysis\n\n")
                f.write(f"- **Type:** {action_plan.goal.goal_type.value}\n")
                f.write(f"- **Priority:** {action_plan.goal.priority.value}\n")
                
                if action_plan.goal.scope:
                    f.write(f"- **Complexity:** {action_plan.goal.scope.estimated_complexity}\n")
                
                f.write(f"\n## Summary\n\n")
                f.write(f"- Total Tasks: {len(action_plan.tasks)}\n")
                if action_plan.total_estimated_effort:
                    f.write(f"- Estimated Effort: {action_plan.total_estimated_effort}\n")
                
                f.write(f"\n## Tasks\n\n")
                for idx, task in enumerate(action_plan.tasks, start=1):
                    f.write(f"### {idx}. {task.title}\n\n")
                    f.write(f"{task.description}\n\n")
                    f.write(f"- **Priority:** {task.priority.value}\n")
                    f.write(f"- **Estimated Effort:** {task.estimated_effort or 'TBD'}\n")
                    
                    if task.dependencies:
                        f.write(f"- **Dependencies:** {len(task.dependencies)} task(s)\n")
                    
                    if task.file_modifications:
                        f.write(f"- **Files to modify:**\n")
                        for file in task.file_modifications:
                            f.write(f"  - {file}\n")
                    
                    f.write("\n")
        except OSError as e:
            console.print(f"[red]Error: Failed to save action plan to '{output_file}': {e}[/red]")
            return


def main():
    """Main entry point for the planning CLI."""
    parser = argparse.ArgumentParser(
        description="Adastrea Director - Goal Decomposition System"
    )
    parser.add_argument(
        "--goal",
        type=str,
        help="Development goal to analyze (for single-goal mode)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file to save the action plan (markdown format)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with full exception tracebacks"
    )
    
    args = parser.parse_args()
    
    cli = PlanningCLI(debug=args.debug)
    
    if args.goal:
        # Single goal mode
        cli.run_single_goal(args.goal, args.output)
    elif args.interactive:
        # Interactive mode
        cli.run_interactive()
    else:
        # Default to interactive mode
        cli.run_interactive()


if __name__ == "__main__":
    main()
