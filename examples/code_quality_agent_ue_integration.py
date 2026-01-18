"""
Code Quality Agent - Unreal Engine Integration Examples

This script demonstrates how to use the Code Quality Agent with Unreal Engine
integration via the Remote Control API for Blueprint analysis.

Examples:
1. Manual Python code analysis (no UE connection required)
2. Blueprint complexity analysis
3. Project-wide quality assessment
4. Blueprint metrics retrieval

Requirements:
- Unreal Engine running with Remote Control API enabled
- Python 3.9+
- All dependencies installed (see requirements.txt)
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.phase3 import EventBus, SharedContext, CodeQualityAgent
from remote_control import UnrealRemoteControlClient

console = Console()


def print_header(title: str):
    """Print a formatted header."""
    console.print()
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]", box=box.DOUBLE))
    console.print()


def example_1_manual_analysis():
    """Example 1: Manual Python code analysis without UE connection."""
    print_header("Example 1: Manual Python Code Analysis (No UE Required)")
    
    # Create agent without UE connection
    event_bus = EventBus()
    shared_context = SharedContext()
    agent = CodeQualityAgent(event_bus, shared_context)
    
    # Start agent
    agent.start()
    console.print("[green]✓[/green] Code Quality Agent started (manual mode)")
    
    # Sample Python code with various quality issues
    sample_code = '''
def calculate_player_score(player_name, level, experience, achievements, inventory_value, 
                          bonus_multiplier, time_played, enemies_defeated, 
                          quests_completed, deaths):
    """This function has too many parameters."""
    base_score = 100
    
    # Magic numbers everywhere!
    if level > 50:
        base_score += 500
    
    if experience > 100000:
        base_score += 1000
        
    # Very long method with lots of logic
    achievement_bonus = 0
    for achievement in achievements:
        if achievement.difficulty == "hard":
            achievement_bonus += 250
        elif achievement.difficulty == "medium":
            achievement_bonus += 100
        else:
            achievement_bonus += 50
            
    inventory_bonus = inventory_value * 1.5
    time_bonus = time_played * 10
    combat_bonus = enemies_defeated * 25
    quest_bonus = quests_completed * 150
    death_penalty = deaths * 50
    
    total_score = (base_score + achievement_bonus + inventory_bonus + 
                  time_bonus + combat_bonus + quest_bonus - death_penalty)
    total_score *= bonus_multiplier
    
    # Some commented out old code
    # if player_name == "admin":
    #     total_score *= 999
    
    return int(total_score)

class PlayerManager:
    """Manages players."""
    
    def __init__(self):
        self.players = {}
        
    def add_player(self, player):
        # Another magic number
        if len(self.players) < 1000:
            self.players[player.id] = player
'''
    
    console.print("\n[bold]Sample Code Analysis[/bold]")
    console.print("[dim]Analyzing code for quality issues...[/dim]\n")
    
    # Analyze code
    report = agent.analyze_code("sample_player_manager.py", sample_code)
    
    # Display results
    console.print(Panel(
        f"[bold]Quality Report[/bold]\n\n"
        f"File: sample_player_manager.py\n"
        f"Lines of Code: {report.lines_of_code}\n"
        f"Complexity Score: {report.complexity_score:.1f}/100\n"
        f"Overall Quality Score: [{'green' if report.overall_score >= 70 else 'yellow' if report.overall_score >= 50 else 'red'}]{report.overall_score:.1f}[/]/100\n",
        box=box.ROUNDED
    ))
    
    # Show code smells
    if report.code_smells:
        console.print("\n[bold yellow]Code Smells Detected:[/bold yellow]")
        table = Table(box=box.ROUNDED)
        table.add_column("Type", style="cyan")
        table.add_column("Severity", style="yellow")
        table.add_column("Description", style="white")
        
        for smell in report.code_smells:
            table.add_row(
                smell.smell_type,
                smell.severity,
                smell.description[:60] + "..." if len(smell.description) > 60 else smell.description
            )
        
        console.print(table)
    
    # Show violations
    if report.violations:
        console.print("\n[bold red]Standard Violations:[/bold red]")
        table = Table(box=box.ROUNDED)
        table.add_column("Rule", style="cyan")
        table.add_column("Description", style="white")
        
        for violation in report.violations[:5]:  # Show first 5
            table.add_row(
                violation.rule,
                violation.description[:70] + "..." if len(violation.description) > 70 else violation.description
            )
        
        console.print(table)
        if len(report.violations) > 5:
            console.print(f"[dim]... and {len(report.violations) - 5} more violations[/dim]")
    
    # Show refactoring suggestions
    if report.refactorings:
        console.print("\n[bold blue]Refactoring Opportunities:[/bold blue]")
        table = Table(box=box.ROUNDED)
        table.add_column("Type", style="cyan")
        table.add_column("Priority", style="yellow")
        table.add_column("Description", style="white")
        
        for refactoring in report.refactorings:
            table.add_row(
                refactoring.refactoring_type,
                refactoring.priority,
                refactoring.description[:60] + "..." if len(refactoring.description) > 60 else refactoring.description
            )
        
        console.print(table)
    
    # Stop agent
    agent.stop()
    console.print("\n[green]✓[/green] Code Quality Agent stopped")


def example_2_blueprint_analysis():
    """Example 2: Blueprint complexity analysis."""
    print_header("Example 2: Blueprint Complexity Analysis")
    
    console.print("[yellow]Note:[/yellow] This example requires Unreal Engine running with Remote Control API enabled")
    console.print("[yellow]Default connection:[/yellow] localhost:30010\n")
    
    # Try to connect to UE
    try:
        ue_client = UnrealRemoteControlClient(host="localhost", port=30010)
        
        # Test connection
        console.print("[bold]Testing connection to Unreal Engine...[/bold]")
        health = ue_client.health_check()
        
        if health.is_healthy:
            console.print("[green]✓[/green] Connected to Unreal Engine")
            console.print(f"  Version: {health.version}")
            console.print(f"  Status: {health.status}")
        else:
            console.print("[red]✗[/red] Cannot connect to Unreal Engine")
            console.print("[yellow]Skipping this example[/yellow]")
            return
        
        # Create agent with UE connection
        event_bus = EventBus()
        shared_context = SharedContext()
        agent = CodeQualityAgent(event_bus, shared_context, remote_control_client=ue_client)
        
        # Start agent
        agent.start()
        console.print("[green]✓[/green] Code Quality Agent started with UE integration")
        
        # Example Blueprint path (user would need to adjust for their project)
        blueprint_path = "/Game/Blueprints/BP_PlayerCharacter"
        
        console.print(f"\n[bold]Analyzing Blueprint:[/bold] {blueprint_path}")
        console.print("[dim]This is a demonstration - adjust the Blueprint path for your project[/dim]\n")
        
        try:
            report = agent.analyze_blueprint_complexity(blueprint_path)
            
            if report:
                # Display results
                console.print(Panel(
                    f"[bold]Blueprint Analysis Report[/bold]\n\n"
                    f"Blueprint: {blueprint_path}\n"
                    f"Node Count: {report.lines_of_code}\n"
                    f"Complexity Score: {report.complexity_score:.1f}/100\n"
                    f"Overall Quality: [{'green' if report.overall_score >= 70 else 'yellow' if report.overall_score >= 50 else 'red'}]{report.overall_score:.1f}[/]/100\n",
                    box=box.ROUNDED
                ))
                
                # Show issues if any
                if report.code_smells:
                    console.print("\n[bold yellow]Issues Detected:[/bold yellow]")
                    for smell in report.code_smells:
                        console.print(f"  • [{smell.severity}] {smell.description}")
                        console.print(f"    Suggestion: {smell.suggestion}")
                else:
                    console.print("\n[green]✓[/green] No major issues detected")
            else:
                console.print(f"[yellow]Blueprint not found or could not be analyzed: {blueprint_path}[/yellow]")
        
        except Exception as e:
            console.print(f"[red]Error analyzing Blueprint:[/red] {str(e)}")
        
        # Stop agent
        agent.stop()
        console.print("\n[green]✓[/green] Code Quality Agent stopped")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        console.print("[yellow]Make sure Unreal Engine is running with Remote Control API enabled[/yellow]")


def example_3_project_quality():
    """Example 3: Project-wide quality assessment."""
    print_header("Example 3: Project-Wide Quality Assessment")
    
    console.print("[yellow]Note:[/yellow] This example requires Unreal Engine running with Remote Control API enabled\n")
    
    try:
        ue_client = UnrealRemoteControlClient(host="localhost", port=30010)
        
        # Test connection
        health = ue_client.health_check()
        if not health.is_healthy:
            console.print("[red]✗[/red] Cannot connect to Unreal Engine")
            console.print("[yellow]Skipping this example[/yellow]")
            return
        
        console.print("[green]✓[/green] Connected to Unreal Engine")
        
        # Create agent with UE connection
        event_bus = EventBus()
        shared_context = SharedContext()
        agent = CodeQualityAgent(event_bus, shared_context, remote_control_client=ue_client)
        
        agent.start()
        console.print("[green]✓[/green] Code Quality Agent started")
        
        # Analyze project
        console.print("\n[bold]Analyzing project quality...[/bold]")
        console.print("[dim]Scanning for Python and C++ files...[/dim]\n")
        
        results = agent.analyze_ue_project_quality()
        
        # Display summary
        console.print(Panel(
            f"[bold]Project Quality Summary[/bold]\n\n"
            f"Total Files Analyzed: {results['total_files']}\n"
            f"Total Code Smells: {results['total_smells']}\n"
            f"Total Violations: {results['total_violations']}\n"
            f"Average Quality Score: {results['average_score']:.1f}/100",
            box=box.ROUNDED
        ))
        
        # Show analyzed files
        if results['files_analyzed']:
            console.print("\n[bold]Analyzed Files:[/bold]")
            table = Table(box=box.ROUNDED)
            table.add_column("File", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Score", style="green")
            
            for file_info in results['files_analyzed'][:10]:  # Show first 10
                score = file_info['score']
                score_color = "green" if score >= 70 else "yellow" if score >= 50 else "red"
                table.add_row(
                    file_info['path'][-50:] if len(file_info['path']) > 50 else file_info['path'],
                    file_info['type'],
                    f"[{score_color}]{score:.1f}[/]"
                )
            
            console.print(table)
            if len(results['files_analyzed']) > 10:
                console.print(f"[dim]... and {len(results['files_analyzed']) - 10} more files[/dim]")
        
        agent.stop()
        console.print("\n[green]✓[/green] Code Quality Agent stopped")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


def example_4_blueprint_metrics():
    """Example 4: Blueprint metrics retrieval."""
    print_header("Example 4: Blueprint Metrics Retrieval")
    
    console.print("[yellow]Note:[/yellow] This example requires Unreal Engine running with Remote Control API enabled\n")
    
    try:
        ue_client = UnrealRemoteControlClient(host="localhost", port=30010)
        
        health = ue_client.health_check()
        if not health.is_healthy:
            console.print("[red]✗[/red] Cannot connect to Unreal Engine")
            console.print("[yellow]Skipping this example[/yellow]")
            return
        
        console.print("[green]✓[/green] Connected to Unreal Engine")
        
        # Create agent
        event_bus = EventBus()
        shared_context = SharedContext()
        agent = CodeQualityAgent(event_bus, shared_context, remote_control_client=ue_client)
        
        agent.start()
        
        # Example Blueprints to check (user would adjust for their project)
        blueprints = [
            "/Game/Blueprints/BP_PlayerCharacter",
            "/Game/Blueprints/BP_GameMode",
            "/Game/Blueprints/BP_PlayerController"
        ]
        
        console.print("\n[bold]Retrieving Blueprint Metrics[/bold]")
        console.print("[dim]Checking multiple Blueprints...[/dim]\n")
        
        table = Table(title="Blueprint Metrics", box=box.ROUNDED)
        table.add_column("Blueprint", style="cyan")
        table.add_column("Exists", style="yellow")
        table.add_column("Node Count", style="green")
        table.add_column("Functions", style="blue")
        table.add_column("Variables", style="magenta")
        
        for bp_path in blueprints:
            metrics = agent.get_blueprint_metrics(bp_path)
            
            if metrics and metrics.get('exists'):
                table.add_row(
                    metrics['name'],
                    "[green]✓[/green]",
                    str(metrics.get('node_count', 0)),
                    str(metrics.get('function_count', 0)),
                    str(metrics.get('variable_count', 0))
                )
            else:
                table.add_row(
                    bp_path.split('/')[-1],
                    "[red]✗[/red]",
                    "-",
                    "-",
                    "-"
                )
        
        console.print(table)
        console.print("\n[dim]Note: Node, function, and variable counts require full Blueprint graph analysis")
        console.print("Current implementation shows basic existence check[/dim]")
        
        agent.stop()
        console.print("\n[green]✓[/green] Code Quality Agent stopped")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


def main():
    """Run all examples."""
    console.print(Panel.fit(
        "[bold cyan]Code Quality Agent - Unreal Engine Integration Examples[/bold cyan]\n\n"
        "This script demonstrates Code Quality Agent capabilities with UE integration.\n"
        "Some examples require Unreal Engine running with Remote Control API enabled.",
        box=box.DOUBLE
    ))
    
    examples = [
        ("1", "Manual Python Code Analysis", example_1_manual_analysis),
        ("2", "Blueprint Complexity Analysis", example_2_blueprint_analysis),
        ("3", "Project-Wide Quality Assessment", example_3_project_quality),
        ("4", "Blueprint Metrics Retrieval", example_4_blueprint_metrics),
    ]
    
    # Show menu
    console.print("\n[bold]Available Examples:[/bold]")
    for num, title, _ in examples:
        console.print(f"  {num}. {title}")
    console.print("  all. Run all examples")
    console.print("  q. Quit")
    
    choice = console.input("\n[bold cyan]Select an example (1-4, all, or q):[/bold cyan] ").strip().lower()
    
    if choice == 'q':
        console.print("[yellow]Goodbye![/yellow]")
        return
    
    if choice == 'all':
        for _, _, func in examples:
            func()
            console.input("\n[dim]Press Enter to continue to next example...[/dim]")
    elif choice in ['1', '2', '3', '4']:
        idx = int(choice) - 1
        examples[idx][2]()
    else:
        console.print("[red]Invalid choice[/red]")
    
    console.print("\n[bold green]Examples complete![/bold green]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        import traceback
        console.print(traceback.format_exc())
