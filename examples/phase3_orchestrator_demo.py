#!/usr/bin/env python
"""
Phase 3 Agent Orchestrator Demo

Demonstrates the Agent Orchestrator CLI and Dashboard functionality.
Shows how to programmatically control agents and monitor their status.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich import box

# Import orchestrator
from agent_orchestrator_cli import AgentOrchestrator

console = Console()


def print_header(title: str):
    """Print a styled header."""
    console.print()
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]", box=box.DOUBLE))
    console.print()


def demo_orchestrator():
    """Demonstrate the agent orchestrator."""
    print_header("Agent Orchestrator Demo")
    
    # Create orchestrator
    console.print("[yellow]Creating orchestrator...[/yellow]")
    orchestrator = AgentOrchestrator()
    
    # Configure project
    console.print("\n[yellow]Configuring project...[/yellow]")
    orchestrator.configure_project(
        name="Demo Game Project",
        root_path="/path/to/project",
        language="C++",
        framework="Unreal Engine 5.3"
    )
    
    # List available agents
    console.print("\n[yellow]Available agents:[/yellow]")
    orchestrator.list_agents()
    
    # Show initial status
    console.print("\n[yellow]Initial status:[/yellow]")
    orchestrator.display_status()
    
    # Start performance agent
    console.print("\n[yellow]Starting performance agent...[/yellow]")
    orchestrator.start_agent('performance')
    time.sleep(0.5)
    
    # Show status after starting one agent
    console.print("\n[yellow]Status after starting performance agent:[/yellow]")
    orchestrator.display_status()
    
    # Start remaining agents
    console.print("\n[yellow]Starting bug detection and code quality agents...[/yellow]")
    orchestrator.start_agent('bug_detection')
    orchestrator.start_agent('code_quality')
    time.sleep(0.5)
    
    # Show status with all agents running
    console.print("\n[yellow]Status with all agents running:[/yellow]")
    orchestrator.display_status()
    
    # Simulate some agent activity
    console.print("\n[yellow]Simulating agent activity...[/yellow]")
    
    # Performance agent
    perf_agent = orchestrator.agents['performance']
    metrics = perf_agent.collect_metrics(
        frame_rate=45.0,  # Low FPS
        memory_usage_mb=3000.0,
        cpu_usage_percent=75.0,
        gpu_usage_percent=85.0,
        draw_calls=2000,
        triangles=800000
    )
    analysis = perf_agent.analyze_performance(metrics)
    console.print(f"[green]✓[/green] Performance analysis: {len(analysis.bottlenecks)} bottleneck(s)")
    
    # Bug detection agent
    bug_agent = orchestrator.agents['bug_detection']
    log_content = """
[ERROR] Null pointer exception in PlayerController
[ERROR] Access violation at address 0x123456
[WARNING] Memory usage high
"""
    anomalies = bug_agent.analyze_logs(log_content)
    console.print(f"[green]✓[/green] Log analysis: {len(anomalies)} anomaly(ies) detected")
    
    # Code quality agent
    quality_agent = orchestrator.agents['code_quality']
    sample_code = """
def bad_function():
    x = 500  # magic number
    y = 1000  # magic number
    return x * y
"""
    report = quality_agent.analyze_code("sample.py", sample_code)
    console.print(f"[green]✓[/green] Code analysis: Quality score {report.overall_score:.1f}/100")
    
    time.sleep(1)
    
    # Show events
    console.print("\n[yellow]Recent events:[/yellow]")
    orchestrator.display_events(limit=10)
    
    # Stop all agents
    console.print("\n[yellow]Stopping all agents...[/yellow]")
    orchestrator.stop_all()
    time.sleep(0.5)
    
    # Show final status
    console.print("\n[yellow]Final status:[/yellow]")
    orchestrator.display_status()
    
    console.print("\n[green]✓[/green] Demo complete!")
    console.print("\n[cyan]Next steps:[/cyan]")
    console.print("  1. Try: python agent_orchestrator_cli.py status")
    console.print("  2. Try: python agent_orchestrator_cli.py start --all")
    console.print("  3. Try: python agent_dashboard.py --auto-start")
    console.print()


def main():
    """Run the demo."""
    try:
        demo_orchestrator()
        return 0
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"\n[red]Error during demo: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
