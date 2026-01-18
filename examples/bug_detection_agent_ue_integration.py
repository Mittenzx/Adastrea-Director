"""
Bug Detection Agent - Unreal Engine Integration Examples

This script demonstrates how to use the Bug Detection Agent with Unreal Engine
integration via the Remote Control API.

Examples:
1. Manual log analysis (no UE connection required)
2. Real-time UE log monitoring
3. Automated playtest execution
4. Continuous monitoring setup

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
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.phase3 import EventBus, SharedContext, BugDetectionAgent
from remote_control import UnrealRemoteControlClient

console = Console()


def print_header(title: str):
    """Print a formatted header."""
    console.print()
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]", box=box.DOUBLE))
    console.print()


def example_1_manual_analysis():
    """Example 1: Manual log analysis without UE connection."""
    print_header("Example 1: Manual Log Analysis (No UE Required)")
    
    # Create agent without UE connection
    event_bus = EventBus()
    shared_context = SharedContext()
    agent = BugDetectionAgent(event_bus, shared_context)
    
    # Start agent
    agent.start()
    console.print("[green]✓[/green] Bug Detection Agent started (manual mode)")
    
    # Sample log content with various issues
    sample_log = """
    [2025-01-15 10:30:15] INFO: Game started successfully
    [2025-01-15 10:30:20] WARNING: Low memory detected (< 500MB available)
    [2025-01-15 10:30:25] ERROR: Null pointer exception in PlayerController
    [2025-01-15 10:30:26] ERROR: Failed to load texture: /Game/Textures/PlayerSkin
    [2025-01-15 10:30:30] WARNING: Draw calls exceeding 5000 per frame
    [2025-01-15 10:30:35] INFO: Player respawned at checkpoint
    [2025-01-15 10:30:40] ERROR: Access violation at 0x00007FF123456789
    [2025-01-15 10:30:41] CRITICAL: Game crash detected
    """
    
    console.print("\n[bold]Sample Log Content:[/bold]")
    console.print(sample_log)
    
    # Analyze logs
    console.print("\n[bold]Analyzing logs...[/bold]")
    anomalies = agent.analyze_logs(sample_log)
    
    # Display results
    if anomalies:
        table = Table(title="Detected Anomalies", box=box.ROUNDED)
        table.add_column("Type", style="cyan")
        table.add_column("Severity", style="yellow")
        table.add_column("Description", style="white")
        table.add_column("Location", style="green")
        
        for anomaly in anomalies:
            table.add_row(
                anomaly.anomaly_type,
                anomaly.severity,
                anomaly.description[:50] + "..." if len(anomaly.description) > 50 else anomaly.description,
                anomaly.location or "N/A"
            )
        
        console.print(table)
        console.print(f"\n[green]✓[/green] Found {len(anomalies)} anomalies")
    else:
        console.print("[yellow]No anomalies detected[/yellow]")
    
    # Stop agent
    agent.stop()
    console.print("\n[green]✓[/green] Bug Detection Agent stopped")


def example_2_ue_log_monitoring():
    """Example 2: Real-time UE log monitoring."""
    print_header("Example 2: Real-time UE Log Monitoring")
    
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
        agent = BugDetectionAgent(event_bus, shared_context, remote_control_client=ue_client)
        
        # Start agent
        agent.start()
        console.print("[green]✓[/green] Bug Detection Agent started with UE integration")
        
        # Monitor logs for 30 seconds
        console.print("\n[bold]Monitoring UE logs for 30 seconds...[/bold]")
        console.print("[dim]Press Ctrl+C to stop early[/dim]\n")
        
        try:
            anomalies = agent.monitor_ue_logs(duration_seconds=30)
            
            # Display results
            if anomalies:
                table = Table(title="Anomalies Detected During Monitoring", box=box.ROUNDED)
                table.add_column("Time", style="cyan")
                table.add_column("Type", style="yellow")
                table.add_column("Severity", style="red")
                table.add_column("Description", style="white")
                
                for anomaly in anomalies:
                    table.add_row(
                        anomaly.timestamp.strftime("%H:%M:%S"),
                        anomaly.anomaly_type,
                        anomaly.severity,
                        anomaly.description[:60] + "..." if len(anomaly.description) > 60 else anomaly.description
                    )
                
                console.print(table)
                console.print(f"\n[green]✓[/green] Detected {len(anomalies)} anomalies in 30 seconds")
            else:
                console.print("[green]✓[/green] No anomalies detected during monitoring period")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring interrupted by user[/yellow]")
        
        # Stop agent
        agent.stop()
        console.print("[green]✓[/green] Bug Detection Agent stopped")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        console.print("[yellow]Make sure Unreal Engine is running with Remote Control API enabled[/yellow]")


def example_3_automated_playtest():
    """Example 3: Automated playtest execution."""
    print_header("Example 3: Automated Playtest")
    
    console.print("[yellow]Note:[/yellow] This example requires Unreal Engine running with Remote Control API enabled")
    console.print("[yellow]Default connection:[/yellow] localhost:30010\n")
    
    # Try to connect to UE
    try:
        ue_client = UnrealRemoteControlClient(host="localhost", port=30010)
        
        # Test connection
        console.print("[bold]Testing connection to Unreal Engine...[/bold]")
        health = ue_client.health_check()
        
        if not health.is_healthy:
            console.print("[red]✗[/red] Cannot connect to Unreal Engine")
            console.print("[yellow]Skipping this example[/yellow]")
            return
        
        console.print("[green]✓[/green] Connected to Unreal Engine")
        
        # Create agent with UE connection
        event_bus = EventBus()
        shared_context = SharedContext()
        agent = BugDetectionAgent(event_bus, shared_context, remote_control_client=ue_client)
        
        # Start agent
        agent.start()
        console.print("[green]✓[/green] Bug Detection Agent started with UE integration")
        
        # Run automated playtest for 60 seconds
        console.print("\n[bold]Running automated playtest for 60 seconds...[/bold]")
        console.print("[dim]This will start PIE and monitor for errors[/dim]\n")
        
        try:
            results = agent.automated_playtest(duration_seconds=60)
            
            # Display results
            console.print(Panel(
                f"[bold]Test Results[/bold]\n\n"
                f"Test Run ID: {results.test_run_id}\n"
                f"Duration: {results.duration_seconds:.1f} seconds\n"
                f"Total Tests: {results.total_tests}\n"
                f"Passed: [green]{results.passed}[/green]\n"
                f"Failed: [red]{results.failed}[/red]\n"
                f"Errors: [yellow]{results.errors}[/yellow]\n"
                f"Success Rate: {results.success_rate():.1f}%",
                box=box.ROUNDED
            ))
            
            # Show failures if any
            if results.failures:
                console.print("\n[bold red]Failures Detected:[/bold red]")
                table = Table(box=box.ROUNDED)
                table.add_column("Error", style="red")
                
                for failure in results.failures[:10]:  # Show first 10
                    error_msg = failure.get('description', failure.get('error', str(failure)))
                    table.add_row(error_msg[:80] + "..." if len(error_msg) > 80 else error_msg)
                
                console.print(table)
                
                if len(results.failures) > 10:
                    console.print(f"[dim]... and {len(results.failures) - 10} more errors[/dim]")
            else:
                console.print("\n[green]✓[/green] No errors detected during playtest")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Playtest interrupted by user[/yellow]")
        
        # Stop agent
        agent.stop()
        console.print("\n[green]✓[/green] Bug Detection Agent stopped")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        console.print("[yellow]Make sure Unreal Engine is running with Remote Control API enabled[/yellow]")


def example_4_continuous_monitoring():
    """Example 4: Continuous monitoring setup."""
    print_header("Example 4: Continuous Monitoring")
    
    console.print("[yellow]Note:[/yellow] This demonstrates the continuous monitoring API")
    console.print("[yellow]In production, monitoring would run in a background thread[/yellow]\n")
    
    # Create agent
    event_bus = EventBus()
    shared_context = SharedContext()
    
    # For this demo, we'll work without UE connection
    agent = BugDetectionAgent(event_bus, shared_context)
    agent.start()
    
    console.print("[green]✓[/green] Bug Detection Agent started")
    
    # Demonstrate continuous monitoring API
    console.print("\n[bold]Starting continuous monitoring...[/bold]")
    agent.start_continuous_monitoring()
    console.print(f"[green]✓[/green] Monitoring active: {agent.is_monitoring_active()}")
    
    console.print("\n[dim]In production, the agent would now continuously monitor UE logs")
    console.print("in a background thread, automatically detecting and reporting issues.[/dim]")
    
    # Simulate some time passing
    console.print("\n[bold]Simulating monitoring for 5 seconds...[/bold]")
    for i in range(5):
        time.sleep(1)
        console.print(f"  Monitoring... ({i+1}/5)")
    
    # Stop monitoring
    console.print("\n[bold]Stopping continuous monitoring...[/bold]")
    agent.stop_continuous_monitoring()
    console.print(f"[green]✓[/green] Monitoring active: {agent.is_monitoring_active()}")
    
    # Stop agent
    agent.stop()
    console.print("[green]✓[/green] Bug Detection Agent stopped")


def main():
    """Run all examples."""
    console.print(Panel.fit(
        "[bold cyan]Bug Detection Agent - Unreal Engine Integration Examples[/bold cyan]\n\n"
        "This script demonstrates Bug Detection Agent capabilities with UE integration.\n"
        "Some examples require Unreal Engine running with Remote Control API enabled.",
        box=box.DOUBLE
    ))
    
    examples = [
        ("1", "Manual Log Analysis", example_1_manual_analysis),
        ("2", "Real-time UE Log Monitoring", example_2_ue_log_monitoring),
        ("3", "Automated Playtest", example_3_automated_playtest),
        ("4", "Continuous Monitoring", example_4_continuous_monitoring),
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
