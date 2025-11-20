"""
Performance Agent with Unreal Engine Integration - Example

This example demonstrates how to use the Performance Profiling Agent
with the Unreal Engine Remote Control API to collect and analyze
real-time performance metrics.

Requirements:
- Unreal Engine with Remote Control plugin enabled
- UE project running with PIE or standalone
- Remote Control API accessible at http://localhost:30010

Usage:
    python examples/performance_agent_ue_integration.py
"""

import time
import sys
import random
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.phase3.event_bus import EventBus, EventType
from agents.phase3.shared_state import SharedContext, ProjectInfo
from agents.phase3.performance_profiling_agent import PerformanceProfilingAgent
from remote_control.client import UnrealRemoteControlClient
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich import box

console = Console()


def print_banner():
    """Print example banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║  Performance Agent - Unreal Engine Integration Example   ║
╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def setup_infrastructure():
    """
    Setup Event Bus, Shared Context, and Remote Control client.
    
    Returns:
        Tuple of (event_bus, shared_context, ue_client)
    """
    console.print("\n[bold yellow]Setting up infrastructure...[/bold yellow]")
    
    # Create Event Bus
    event_bus = EventBus()
    console.print("  ✓ Event Bus created", style="green")
    
    # Create Shared Context
    shared_context = SharedContext()
    console.print("  ✓ Shared Context created", style="green")
    
    # Setup project info
    project_info = ProjectInfo(
        name="Example UE Project",
        root_path="/path/to/project",
        language="C++",
        framework="Unreal Engine 5.3"
    )
    shared_context.set_project_info(project_info)
    console.print("  ✓ Project info configured", style="green")
    
    # Create Remote Control client
    try:
        ue_client = UnrealRemoteControlClient(host="localhost", port=30010)
        
        # Test connection
        if ue_client.health_check():
            console.print("  ✓ Connected to Unreal Engine", style="green")
        else:
            console.print("  ⚠ Could not connect to Unreal Engine (continuing with mock)", style="yellow")
            ue_client = None
    except Exception as e:
        console.print(f"  ⚠ Remote Control not available: {e}", style="yellow")
        ue_client = None
    
    return event_bus, shared_context, ue_client


def setup_event_monitoring(event_bus):
    """
    Setup event monitoring to display agent events in real-time.
    
    Args:
        event_bus: The event bus to monitor
    """
    events_received = []
    
    def on_metrics_collected(event):
        metrics = event.payload.get('metrics', {})
        events_received.append({
            'type': 'Metrics',
            'fps': metrics.get('frame_rate', 0),
            'memory': metrics.get('memory_usage_mb', 0)
        })
    
    def on_performance_alert(event):
        events_received.append({
            'type': 'Alert',
            'summary': event.payload.get('summary', 'Unknown'),
            'bottlenecks': event.payload.get('bottleneck_count', 0)
        })
    
    event_bus.subscribe(EventType.PERFORMANCE_METRICS_COLLECTED, on_metrics_collected)
    event_bus.subscribe(EventType.PERFORMANCE_ALERT, on_performance_alert)
    
    return events_received


def demonstrate_manual_metrics(agent):
    """
    Demonstrate manual metrics collection (without UE).
    
    Args:
        agent: The Performance Profiling Agent
    """
    console.print("\n[bold cyan]Example 1: Manual Metrics Collection[/bold cyan]")
    console.print("Simulating performance metrics without Unreal Engine...\n")
    
    # Collect metrics manually
    metrics = agent.collect_metrics(
        frame_rate=55.0,
        memory_usage_mb=3800.0,
        cpu_usage_percent=75.0,
        gpu_usage_percent=85.0,
        draw_calls=2500,
        triangles=850000
    )
    
    # Display metrics
    table = Table(title="Collected Metrics", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Frame Rate", f"{metrics.frame_rate:.1f} FPS")
    table.add_row("Memory Usage", f"{metrics.memory_usage_mb:.1f} MB")
    table.add_row("CPU Usage", f"{metrics.cpu_usage_percent:.1f}%")
    table.add_row("GPU Usage", f"{metrics.gpu_usage_percent:.1f}%")
    table.add_row("Draw Calls", f"{metrics.draw_calls:,}")
    table.add_row("Triangles", f"{metrics.triangles:,}")
    
    console.print(table)
    
    # Analyze performance
    console.print("\n[bold yellow]Analyzing performance...[/bold yellow]")
    analysis = agent.analyze_performance(metrics)
    
    console.print(f"\n[bold]Summary:[/bold] {analysis.summary}")
    console.print(f"[bold]Bottlenecks:[/bold] {len(analysis.bottlenecks)} detected")
    console.print(f"[bold]Recommendations:[/bold] {len(analysis.recommendations)} generated")
    
    # Display bottlenecks
    if analysis.bottlenecks:
        console.print("\n[bold red]Detected Bottlenecks:[/bold red]")
        for i, bottleneck in enumerate(analysis.bottlenecks, 1):
            console.print(f"  {i}. [{bottleneck.severity.upper()}] {bottleneck.description}")
    
    # Display recommendations
    if analysis.recommendations:
        console.print("\n[bold green]Recommendations:[/bold green]")
        for i, rec in enumerate(analysis.recommendations, 1):
            console.print(f"\n  {i}. {rec.title}")
            console.print(f"     Priority: {rec.priority} | Impact: {rec.estimated_impact}")
            console.print(f"     {rec.description[:100]}...")


def demonstrate_ue_metrics(agent):
    """
    Demonstrate collecting metrics from Unreal Engine.
    
    Args:
        agent: The Performance Profiling Agent with UE client
    """
    console.print("\n\n[bold cyan]Example 2: Unreal Engine Metrics Collection[/bold cyan]")
    
    if agent.remote_control_client is None:
        console.print("[yellow]⚠ Unreal Engine not connected. Skipping this example.[/yellow]")
        return
    
    console.print("Collecting real-time metrics from Unreal Engine...\n")
    
    # Collect metrics from UE
    for i in range(3):
        console.print(f"[dim]Sample {i+1}/3...[/dim]")
        metrics = agent.collect_metrics_from_ue()
        
        if metrics:
            console.print(f"  FPS: {metrics.frame_rate:.1f} | "
                         f"Memory: {metrics.memory_usage_mb:.1f} MB | "
                         f"CPU: {metrics.cpu_usage_percent:.1f}% | "
                         f"GPU: {metrics.gpu_usage_percent:.1f}%")
        else:
            console.print("  [red]Failed to collect metrics[/red]")
        
        time.sleep(1)
    
    # Get average FPS
    avg_fps = agent.get_average_fps(duration_seconds=60)
    if avg_fps:
        console.print(f"\n[bold]Average FPS (last 60s):[/bold] {avg_fps:.1f}")
    
    # Display history
    history = agent.get_metrics_history(limit=3)
    if history:
        console.print(f"\n[bold]Recent Metrics History:[/bold] {len(history)} samples")


def demonstrate_pie_profiling(agent):
    """
    Demonstrate automated PIE profiling.
    
    Args:
        agent: The Performance Profiling Agent with UE client
    """
    console.print("\n\n[bold cyan]Example 3: Automated PIE Profiling[/bold cyan]")
    
    if agent.remote_control_client is None:
        console.print("[yellow]⚠ Unreal Engine not connected. Skipping this example.[/yellow]")
        return
    
    console.print("This will start PIE, collect metrics, and stop PIE automatically.")
    console.print("[dim]Note: This requires a UE project with a valid level.[/dim]\n")
    
    # Confirm before starting
    response = input("Start PIE profiling for 10 seconds? (y/n): ")
    if response.lower() != 'y':
        console.print("[yellow]Skipped PIE profiling.[/yellow]")
        return
    
    console.print("\n[bold yellow]Starting PIE profiling...[/bold yellow]")
    
    # Start PIE profiling
    analysis = agent.start_pie_profiling(duration_seconds=10)
    
    if analysis:
        console.print("\n[bold green]✓ PIE Profiling Complete[/bold green]")
        console.print(f"\n[bold]Summary:[/bold] {analysis.summary}")
        console.print(f"[bold]Bottlenecks:[/bold] {len(analysis.bottlenecks)}")
        console.print(f"[bold]Recommendations:[/bold] {len(analysis.recommendations)}")
        
        # Display detailed analysis
        if analysis.bottlenecks:
            console.print("\n[bold]Detected Issues:[/bold]")
            for bottleneck in analysis.bottlenecks:
                console.print(f"  • [{bottleneck.severity}] {bottleneck.description}")
        
        if analysis.recommendations:
            console.print("\n[bold]Top Recommendations:[/bold]")
            for rec in analysis.recommendations[:3]:
                console.print(f"  • {rec.title}")
    else:
        console.print("\n[red]✗ PIE Profiling Failed[/red]")


def demonstrate_real_time_monitoring(agent, duration=10):
    """
    Demonstrate real-time performance monitoring with live display.
    
    Args:
        agent: The Performance Profiling Agent
        duration: How long to monitor (seconds)
    """
    console.print("\n\n[bold cyan]Example 4: Real-Time Performance Monitoring[/bold cyan]")
    console.print(f"Monitoring performance for {duration} seconds...\n")
    
    def generate_display():
        """Generate the live display layout."""
        # Get latest metrics
        history = agent.get_metrics_history(limit=1)
        metrics = history[0] if history else None
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="metrics", size=10),
            Layout(name="status", size=3)
        )
        
        # Header
        layout["header"].update(Panel(
            "[bold cyan]Performance Monitor[/bold cyan]",
            border_style="cyan"
        ))
        
        # Metrics table
        if metrics:
            metrics_table = Table(box=box.SIMPLE)
            metrics_table.add_column("Metric", style="cyan")
            metrics_table.add_column("Value", style="green")
            
            metrics_table.add_row("FPS", f"{metrics.frame_rate:.1f}")
            metrics_table.add_row("Memory", f"{metrics.memory_usage_mb:.1f} MB")
            metrics_table.add_row("CPU", f"{metrics.cpu_usage_percent:.1f}%")
            metrics_table.add_row("GPU", f"{metrics.gpu_usage_percent:.1f}%")
            
            layout["metrics"].update(Panel(metrics_table, title="Current Metrics"))
        else:
            layout["metrics"].update(Panel("[yellow]Waiting for metrics...[/yellow]"))
        
        # Status
        avg_fps = agent.get_average_fps(duration_seconds=60)
        status_text = f"Average FPS: {avg_fps:.1f}" if avg_fps else "Collecting data..."
        layout["status"].update(Panel(status_text, border_style="green"))
        
        return layout
    
    # Monitor with live display
    try:
        with Live(generate_display(), refresh_per_second=2) as live:
            start_time = time.time()
            
            while time.time() - start_time < duration:
                # Collect metrics
                if agent.remote_control_client:
                    agent.collect_metrics_from_ue()
                else:
                    # Simulate metrics
                    agent.collect_metrics(
                        frame_rate=58 + random.uniform(-5, 5),
                        memory_usage_mb=3500 + random.uniform(-200, 200),
                        cpu_usage_percent=70 + random.uniform(-10, 10),
                        gpu_usage_percent=80 + random.uniform(-10, 10),
                        draw_calls=2400 + int(random.uniform(-200, 200)),
                        triangles=800000 + int(random.uniform(-50000, 50000))
                    )
                
                # Update display
                live.update(generate_display())
                time.sleep(0.5)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped by user[/yellow]")
    
    console.print("\n[green]✓ Monitoring complete[/green]")


def main():
    """Main example function."""
    print_banner()
    
    # Setup
    event_bus, shared_context, ue_client = setup_infrastructure()
    events_received = setup_event_monitoring(event_bus)
    
    # Create Performance Agent
    console.print("\n[bold yellow]Creating Performance Profiling Agent...[/bold yellow]")
    agent = PerformanceProfilingAgent(
        event_bus=event_bus,
        shared_context=shared_context,
        target_fps=60.0,
        memory_threshold_mb=4096.0,
        remote_control_client=ue_client
    )
    console.print("  ✓ Performance Agent created", style="green")
    
    # Start agent
    agent.start()
    console.print("  ✓ Agent started", style="green")
    
    try:
        # Run examples
        demonstrate_manual_metrics(agent)
        demonstrate_ue_metrics(agent)
        demonstrate_pie_profiling(agent)
        demonstrate_real_time_monitoring(agent, duration=10)
        
        # Summary
        console.print("\n\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
        console.print("[bold cyan]           Example Complete            [/bold cyan]")
        console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]")
        
        console.print(f"\n[bold]Events Captured:[/bold] {len(events_received)}")
        console.print(f"[bold]Metrics Collected:[/bold] {len(agent.get_metrics_history())}")
        
        avg_fps = agent.get_average_fps()
        if avg_fps:
            console.print(f"[bold]Average FPS:[/bold] {avg_fps:.1f}")
        
    finally:
        # Cleanup
        console.print("\n[bold yellow]Cleaning up...[/bold yellow]")
        agent.stop()
        console.print("  ✓ Agent stopped", style="green")
        
        if ue_client:
            # Close UE connection if needed
            console.print("  ✓ Remote Control connection closed", style="green")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Example interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
