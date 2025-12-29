#!/usr/bin/env python3
"""
Adastrea Director - Planning System (Phase 2)

Main interface for the planning system that coordinates goal analysis,
task decomposition, and code generation agents.

Usage:
    python planner.py "Add a new combat ability system"
    python planner.py --interactive
"""

import sys
import argparse
from typing import Dict, Any

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.table import Table

    from agents import (
        GoalAnalysisAgent,
        TaskDecompositionAgent,
        CodeGenerationAgent,
        Goal,
    )
    from exceptions import APIKeyError
    from llm_config import get_provider_name
    from logging_config import setup_logging, get_logger
except ImportError as e:
    print(f"Error: Missing required dependencies")
    print(f"Details: {e}")
    print(f"\nTo install dependencies, run:")
    print(f"  pip install -r requirements.txt")
    print(f"\nOr use the setup script:")
    print(f"  ./setup.sh")
    sys.exit(1)

console = Console()
logger = get_logger(__name__)


class PlanningSystem:
    """
    Main planning system that coordinates all Phase 2 agents.
    
    This system takes high-level goals and produces actionable implementation
    plans with code suggestions.
    """
    
    def __init__(
        self,
        model_name: str = None,
        enable_code_generation: bool = True,
    ):
        """
        Initialize the planning system.
        
        Args:
            model_name: LLM model to use (default: gemini-1.5-flash for Gemini, gpt-3.5-turbo for OpenAI)
            enable_code_generation: Whether to enable code generation agent
        """
        logger.info(f"Initializing PlanningSystem with model={model_name}, code_gen={enable_code_generation}")
        self.model_name = model_name
        self.enable_code_generation = enable_code_generation
        
        # Initialize agents
        console.print("[cyan]Initializing planning agents...[/cyan]")
        
        try:
            logger.info("Creating GoalAnalysisAgent")
            self.goal_agent = GoalAnalysisAgent(model_name=model_name)
            logger.info("Creating TaskDecompositionAgent")
            self.task_agent = TaskDecompositionAgent(model_name=model_name)
            
            if enable_code_generation:
                logger.info("Creating CodeGenerationAgent")
                self.code_agent = CodeGenerationAgent(model_name=model_name)
            else:
                logger.info("Code generation disabled")
                self.code_agent = None
            
            logger.info("Planning system initialized successfully")
            console.print("[green]✓ Planning system initialized[/green]\n")
        
        except Exception as e:
            error_msg = str(e).lower()
            if "api" in error_msg and "key" in error_msg:
                error = APIKeyError(get_provider_name(), str(e))
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
            else:
                console.print(f"[red]Error initializing planning system: {e}[/red]")
            sys.exit(1)
    
    def create_plan(self, goal_description: str) -> Dict[str, Any]:
        """
        Create a complete implementation plan for a goal.
        
        Args:
            goal_description: Natural language description of the goal
        
        Returns:
            Dictionary containing the complete plan with goal, tasks, and suggestions
        """
        logger.info(f"Creating plan for goal: {goal_description[:100]}...")
        console.print(f"\n[bold cyan]Planning:[/bold cyan] {goal_description}\n")
        
        # Step 1: Analyze goal
        logger.debug("Step 1: Analyzing goal")
        with console.status("[cyan]Analyzing goal...[/cyan]"):
            goal = self.goal_agent.parse_goal(goal_description)
            feasibility = self.goal_agent.analyze_goal_feasibility(goal)
        
        logger.info(f"Goal analyzed: type={goal.goal_type.value}, priority={goal.priority.value}")
        
        console.print("[green]✓ Goal analyzed[/green]")
        self._display_goal(goal, feasibility)
        
        # Step 2: Decompose into tasks
        logger.debug("Step 2: Decomposing into tasks")
        with console.status("[cyan]Decomposing into tasks...[/cyan]"):
            task_tree = self.task_agent.decompose_goal(goal)
            prioritized_tasks = self.task_agent.prioritize_tasks(task_tree.root_tasks)
        
        task_count = task_tree.get_task_count()
        logger.info(f"Created {task_count} tasks")
        console.print(f"[green]✓ Created {task_count} tasks[/green]")
        self._display_tasks(prioritized_tasks)
        
        # Step 3: Generate code suggestions (if enabled)
        code_suggestions = {}
        if self.code_agent and self.enable_code_generation:
            console.print("\n[cyan]Generating code suggestions for key tasks...[/cyan]")
            # Generate for first 3 tasks as examples
            for task in prioritized_tasks[:3]:
                with console.status(f"[cyan]Processing: {task.description}...[/cyan]"):
                    implementations = self.code_agent.suggest_implementation(task)
                    modifications = self.code_agent.propose_modifications(task)
                    code_suggestions[task.id] = {
                        "implementations": implementations,
                        "modifications": modifications,
                    }
            console.print("[green]✓ Code suggestions generated[/green]")
        
        return {
            "goal": goal,
            "task_tree": task_tree,
            "prioritized_tasks": prioritized_tasks,
            "code_suggestions": code_suggestions,
            "feasibility": feasibility,
        }
    
    def _display_goal(self, goal: Goal, feasibility: Dict[str, Any]):
        """Display goal analysis results."""
        # Goal information
        goal_info = f"""
**Goal Type:** {goal.goal_type.value}
**Priority:** {goal.priority.value}
**Complexity:** {goal.scope.estimated_complexity if goal.scope else 'unknown'}

**Key Objectives:**
{chr(10).join([f"• {obj}" for obj in goal.metadata.get('key_objectives', [])])}

**Constraints:**
{chr(10).join([f"• {c.description} ({c.constraint_type})" for c in goal.constraints]) if goal.constraints else "None"}

**Affected Systems:**
{', '.join(goal.scope.systems) if goal.scope and goal.scope.systems else 'Not specified'}
"""
        console.print(Panel(Markdown(goal_info), title="Goal Analysis", border_style="cyan"))
        
        # Feasibility
        risk_color = {
            "low": "green",
            "medium": "yellow",
            "high": "red",
            "very_high": "red bold",
        }.get(feasibility["risk_level"], "yellow")
        
        feasibility_info = f"""
**Feasibility Score:** {feasibility['feasibility_score']}/100
**Risk Level:** {feasibility['risk_level']}

**Recommendations:**
{chr(10).join([f"• {rec}" for rec in feasibility['recommendations']])}
"""
        console.print(
            Panel(
                Markdown(feasibility_info),
                title="Feasibility Analysis",
                border_style=risk_color,
            )
        )
    
    def _display_tasks(self, tasks):
        """Display task breakdown."""
        table = Table(title="Task Breakdown", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Task", style="white")
        table.add_column("Priority", justify="center", width=10)
        table.add_column("Duration", justify="right", width=10)
        table.add_column("Dependencies", justify="center", width=12)
        
        for i, task in enumerate(tasks, 1):
            priority_color = {
                "critical": "red bold",
                "high": "yellow",
                "medium": "white",
                "low": "dim",
            }.get(task.priority.value, "white")
            
            deps_count = len(task.dependencies)
            deps_str = f"{deps_count} tasks" if deps_count > 0 else "-"
            
            table.add_row(
                str(i),
                task.description,
                f"[{priority_color}]{task.priority.value}[/{priority_color}]",
                str(task.estimated_duration) if task.estimated_duration else "-",
                deps_str,
            )
        
        console.print(table)
        console.print()
    
    def export_plan(self, plan: Dict[str, Any], format: str = "markdown") -> str:
        """
        Export a plan to a file format.
        
        Args:
            plan: Plan dictionary from create_plan()
            format: Export format (markdown, json, or text)
        
        Returns:
            String containing the formatted plan
        """
        if format == "markdown":
            return self._export_markdown(plan)
        elif format == "json":
            import json
            # Convert non-serializable objects
            serializable = {
                "goal": {
                    "id": plan["goal"].id,
                    "description": plan["goal"].description,
                    "type": plan["goal"].goal_type.value,
                    "priority": plan["goal"].priority.value,
                },
                "tasks": [
                    {
                        "id": task.id,
                        "description": task.description,
                        "priority": task.priority.value,
                        "duration_hours": task.estimated_duration.hours if task.estimated_duration else None,
                        "dependencies": task.dependencies,
                    }
                    for task in plan["prioritized_tasks"]
                ],
                "feasibility_score": plan["feasibility"]["feasibility_score"],
                "risk_level": plan["feasibility"]["risk_level"],
            }
            return json.dumps(serializable, indent=2)
        else:  # text
            return self._export_text(plan)
    
    def _export_markdown(self, plan: Dict[str, Any]) -> str:
        """Export plan as Markdown."""
        goal = plan["goal"]
        tasks = plan["prioritized_tasks"]
        feasibility = plan["feasibility"]
        
        md = f"""# Implementation Plan: {goal.description}

## Goal Analysis

- **Type:** {goal.goal_type.value}
- **Priority:** {goal.priority.value}
- **Complexity:** {goal.scope.estimated_complexity if goal.scope else 'unknown'}
- **Feasibility Score:** {feasibility['feasibility_score']}/100
- **Risk Level:** {feasibility['risk_level']}

### Key Objectives

{chr(10).join([f"- {obj}" for obj in goal.metadata.get('key_objectives', [])])}

### Constraints

{chr(10).join([f"- {c.description} ({c.constraint_type})" for c in goal.constraints]) if goal.constraints else "None"}

### Recommendations

{chr(10).join([f"- {rec}" for rec in feasibility['recommendations']])}

## Task Breakdown

"""
        for i, task in enumerate(tasks, 1):
            md += f"\n### Task {i}: {task.description}\n\n"
            md += f"- **Priority:** {task.priority.value}\n"
            md += f"- **Estimated Duration:** {task.estimated_duration}\n"
            
            if task.dependencies:
                md += f"- **Dependencies:** {len(task.dependencies)} tasks\n"
            
            if task.files_to_create:
                md += f"- **Files to Create:** {', '.join(task.files_to_create)}\n"
            
            if task.files_to_modify:
                md += f"- **Files to Modify:** {', '.join(task.files_to_modify)}\n"
            
            md += "\n"
        
        return md
    
    def _export_text(self, plan: Dict[str, Any]) -> str:
        """Export plan as plain text."""
        return self._export_markdown(plan)  # Markdown works as plain text too


def main():
    """Main entry point for the planning CLI."""
    parser = argparse.ArgumentParser(
        description="Adastrea Director - Planning System (Phase 2)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "goal",
        nargs="?",
        type=str,
        help="Goal description (if not provided, enters interactive mode)",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="LLM model to use (default: gemini-1.5-flash for Gemini, gpt-3.5-turbo for OpenAI)",
    )
    parser.add_argument(
        "--export",
        type=str,
        choices=["markdown", "json", "text"],
        help="Export plan to file",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path for export",
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(debug=args.debug)
    logger.info("Planning system starting")
    logger.debug(f"Arguments: {vars(args)}")
    
    try:
        # Initialize planning system
        planner = PlanningSystem(model_name=args.model)
    except APIKeyError as e:
        logger.error(f"Failed to initialize planning system due to API key error: {e}", exc_info=True)
        provider_name = get_provider_name()
        console.print("[red]Failed to initialize planning system due to an API key problem.[/red]")
        console.print(f"[yellow]Provider: {provider_name}[/yellow]")
        console.print(f"[yellow]Details: {e}[/yellow]\n")
        console.print(
            "[cyan]Common fixes:[/cyan]\n"
            "  • Verify that your LLM API key is set (e.g., in environment variables or config file)\n"
            "  • Ensure the API key is valid and has not expired or been revoked\n"
            "  • If you recently changed providers, update the corresponding API key\n"
            "  • Re-run with [bold]--debug[/bold] for more detailed logs"
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to initialize planning system: {e}", exc_info=True)
        console.print("[red]Failed to initialize planning system.[/red]")
        console.print(f"[yellow]Details: {e}[/yellow]\n")
        console.print(
            "[cyan]Common fixes:[/cyan]\n"
            "  • Check that your LLM API key is configured correctly\n"
            "  • Ensure required dependencies are installed and up to date\n"
            "  • Verify your internet connection and any proxy settings\n"
            "  • Re-run with [bold]--debug[/bold] for more detailed logs"
        )
        sys.exit(1)
    
    # Interactive mode or single goal
    if args.interactive or not args.goal:
        console.print("\n[bold cyan]🤖 Adastrea Director - Planning Mode[/bold cyan]\n")
        console.print("Enter a development goal to create an implementation plan.")
        console.print("Type 'quit' or 'exit' to leave.\n")
        
        while True:
            try:
                goal_input = console.input("[bold green]Goal:[/bold green] ").strip()
                
                if goal_input.lower() in ["quit", "exit", "q"]:
                    console.print("\n[cyan]Goodbye![/cyan]\n")
                    break
                
                if not goal_input:
                    continue
                
                # Create plan
                plan = planner.create_plan(goal_input)
                
                # Ask if user wants to export
                console.print("\n[cyan]Plan created successfully![/cyan]")
                export_choice = console.input(
                    "[yellow]Export plan? (y/n):[/yellow] "
                ).strip().lower()
                
                if export_choice == "y":
                    format_choice = console.input(
                        "[yellow]Format (markdown/json/text):[/yellow] "
                    ).strip().lower()
                    format_choice = format_choice if format_choice in ["markdown", "json", "text"] else "markdown"
                    
                    filename = f"plan_{plan['goal'].id}.{format_choice if format_choice != 'text' else 'txt'}"
                    
                    content = planner.export_plan(plan, format=format_choice)
                    with open(filename, "w") as f:
                        f.write(content)
                    
                    console.print(f"[green]✓ Plan exported to {filename}[/green]\n")
                
            except KeyboardInterrupt:
                console.print("\n\n[cyan]Goodbye![/cyan]\n")
                break
            except EOFError:
                console.print("\n[cyan]Goodbye![/cyan]\n")
                break
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]\n")
    
    else:
        # Single goal mode
        plan = planner.create_plan(args.goal)
        
        # Export if requested
        if args.export:
            content = planner.export_plan(plan, format=args.export)
            
            if args.output:
                with open(args.output, "w") as f:
                    f.write(content)
                console.print(f"\n[green]✓ Plan exported to {args.output}[/green]")
            else:
                console.print("\n" + content)


if __name__ == "__main__":
    main()
