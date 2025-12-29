"""
Phase 3 Agent Integration with Unreal Engine - Usage Example

This example demonstrates how to use the integrated IPC server with Phase 3
autonomous agents for performance profiling, bug detection, and code quality
monitoring in Unreal Engine projects.

Requirements:
- Python 3.9+
- All Adastrea Director dependencies installed
- Optionally: Unreal Engine with Remote Control API enabled

Usage:
    # Start the integrated IPC server with Phase 3 agents
    python examples/phase3_ue_integration_example.py
    
    # In Unreal Engine, connect to the IPC server and send commands
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "Plugins" / "AdastreaDirector" / "Python"))

from Plugins.AdastreaDirector.Python.ipc_integration import IntegratedIPCServer
from rich.console import Console
from rich.table import Table
from rich import box
import json

console = Console()


def print_banner():
    """Print example banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║   Phase 3 Agents - Unreal Engine Integration Example     ║
║                                                           ║
║   Performance Profiling • Bug Detection • Code Quality   ║
╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def demonstrate_performance_monitoring(server):
    """Demonstrate performance monitoring capabilities."""
    console.print("\n[bold yellow]1. Performance Monitoring[/bold yellow]")
    console.print("   Collecting and analyzing performance metrics...\n")
    
    # Simulate collecting metrics
    metrics_data = {
        'frame_rate': 58.5,
        'memory_usage_mb': 3072.0,
        'cpu_usage_percent': 65.0,
        'gpu_usage_percent': 82.0,
        'draw_calls': 2400,
        'triangles': 750000
    }
    
    response = server._handle_collect_metrics(json.dumps(metrics_data))
    
    if response['status'] == 'success':
        metrics = response['metrics']
        
        table = Table(title="Performance Metrics", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_column("Status", style="green")
        
        table.add_row("Frame Rate", f"{metrics['frame_rate']:.1f} FPS", 
                     "⚠️  Below target" if metrics['frame_rate'] < 60 else "✓ Good")
        table.add_row("Memory", f"{metrics['memory_usage_mb']:.0f} MB", "✓ Normal")
        table.add_row("CPU Usage", f"{metrics['cpu_usage_percent']:.1f}%", "✓ Normal")
        table.add_row("GPU Usage", f"{metrics['gpu_usage_percent']:.1f}%", "✓ Normal")
        
        console.print(table)
    else:
        console.print(f"[red]Error: {response.get('error', 'Unknown error')}[/red]")


def demonstrate_bug_detection(server):
    """Demonstrate bug detection capabilities."""
    console.print("\n[bold yellow]2. Bug Detection & Log Analysis[/bold yellow]")
    console.print("   Analyzing logs for errors and anomalies...\n")
    
    # Simulate log analysis
    sample_log = """
[2025-12-29 10:00:00] Info: Game started successfully
[2025-12-29 10:00:15] Warning: Texture streaming budget exceeded
[2025-12-29 10:00:30] Error: Null pointer exception in PlayerController::Tick
[2025-12-29 10:00:31] Error: Access violation at 0xDEADBEEF
[2025-12-29 10:01:00] Warning: Memory leak detected in InventorySystem
[2025-12-29 10:01:30] Info: Level loaded: MainMenu
    """
    
    response = server._handle_analyze_logs(sample_log)
    
    if response['status'] == 'success':
        anomalies = response['anomalies']
        
        table = Table(title=f"Detected Anomalies ({len(anomalies)} found)", box=box.ROUNDED)
        table.add_column("Type", style="cyan")
        table.add_column("Severity", style="yellow")
        table.add_column("Location", style="dim")
        table.add_column("Description")
        
        for anomaly in anomalies[:5]:  # Show first 5
            severity_style = "red" if anomaly['severity'] in ['high', 'critical'] else "yellow"
            table.add_row(
                anomaly['type'],
                f"[{severity_style}]{anomaly['severity']}[/{severity_style}]",
                anomaly['location'],
                anomaly['description'][:50] + "..." if len(anomaly['description']) > 50 else anomaly['description']
            )
        
        console.print(table)
    else:
        console.print(f"[red]Error: {response.get('error', 'Unknown error')}[/red]")


def demonstrate_code_quality(server):
    """Demonstrate code quality analysis capabilities."""
    console.print("\n[bold yellow]3. Code Quality Analysis[/bold yellow]")
    console.print("   Analyzing code for quality issues...\n")
    
    # Sample Blueprint-like Python code
    sample_code = """
def complex_blueprint_function(actor, target, damage, effect_type, multiplier, override_flag):
    # This function has too many parameters (code smell)
    base_damage = 12345  # Magic number (code smell)
    
    if actor and target:
        if damage > 0:
            if effect_type == 'fire':
                if multiplier > 1.0:
                    # Deeply nested conditions (complexity issue)
                    final_damage = damage * multiplier * base_damage
                    target.apply_damage(final_damage)
                else:
                    target.apply_damage(damage)
    
    # def old_damage_calculation():  # Commented code (code smell)
    #     return damage * 100
    
    return True
"""
    
    code_params = {
        'file_path': 'BP_CombatSystem.py',
        'code_content': sample_code
    }
    
    response = server._handle_analyze_code_quality(json.dumps(code_params))
    
    if response['status'] == 'success':
        report = response['report']
        
        table = Table(title="Code Quality Report", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        score_style = "green" if report['overall_score'] >= 80 else "yellow" if report['overall_score'] >= 60 else "red"
        
        table.add_row("File", report['file_path'])
        table.add_row("Lines of Code", str(report['lines_of_code']))
        table.add_row("Complexity Score", f"{report['complexity_score']:.1f}")
        table.add_row("Code Smells", f"[yellow]{report['code_smells']}[/yellow]")
        table.add_row("Violations", f"[yellow]{report['violations']}[/yellow]")
        table.add_row("Overall Score", f"[{score_style}]{report['overall_score']:.1f}/100[/{score_style}]")
        
        console.print(table)
        
        # Get technical debt
        debt_response = server._handle_get_technical_debt('')
        if debt_response['status'] == 'success':
            debt = debt_response['debt']
            console.print(f"\n💸 Technical Debt: {debt['total_debt_hours']:.1f} hours "
                         f"({debt['code_smells_count']} code smells, {debt['violations_count']} violations)")
    else:
        console.print(f"[red]Error: {response.get('error', 'Unknown error')}[/red]")


def demonstrate_agent_control(server):
    """Demonstrate agent lifecycle control."""
    console.print("\n[bold yellow]4. Agent Lifecycle Control[/bold yellow]")
    console.print("   Starting and monitoring Phase 3 agents...\n")
    
    # Start all agents
    console.print("   Starting all agents...")
    start_response = server._handle_agent_start(json.dumps({'agent_id': 'all'}))
    
    if start_response['status'] == 'success':
        console.print("   [green]✓ All agents started successfully[/green]")
        
        # Wait a moment
        time.sleep(1)
        
        # Get status
        status_response = server._handle_agent_status('')
        
        if status_response['status'] == 'success':
            agents = status_response['agents']
            
            table = Table(title="Agent Status", box=box.ROUNDED)
            table.add_column("Agent", style="cyan")
            table.add_column("Running", style="green")
            table.add_column("Status")
            
            for agent_name, agent_info in agents.items():
                if 'running' in agent_info:
                    running_icon = "🟢" if agent_info['running'] else "🔴"
                    status = agent_info.get('status', 'unknown')
                    table.add_row(
                        agent_name.replace('_', ' ').title(),
                        running_icon,
                        status
                    )
            
            console.print(table)
        
        # Stop all agents
        console.print("\n   Stopping all agents...")
        stop_response = server._handle_agent_stop(json.dumps({'agent_id': 'all'}))
        
        if stop_response['status'] == 'success':
            console.print("   [green]✓ All agents stopped successfully[/green]")
    else:
        console.print(f"   [red]Error: {start_response.get('error', 'Unknown error')}[/red]")


def main():
    """Main entry point."""
    print_banner()
    
    console.print("\n[bold]Initializing Integrated IPC Server with Phase 3 Agents...[/bold]\n")
    
    # Create integrated server with Phase 3 agents
    try:
        server = IntegratedIPCServer(
            host='127.0.0.1',
            port=5555,
            enable_rag=False,
            enable_planning=False,
            enable_phase3_agents=True  # Enable Phase 3 agents
        )
        
        console.print("[green]✓ Server initialized successfully[/green]")
        console.print(f"[dim]  Event Bus: Active[/dim]")
        console.print(f"[dim]  Shared Context: Active[/dim]")
        console.print(f"[dim]  Performance Agent: Ready[/dim]")
        console.print(f"[dim]  Bug Detection Agent: Ready[/dim]")
        console.print(f"[dim]  Code Quality Agent: Ready[/dim]")
        
        # Demonstrate capabilities
        demonstrate_performance_monitoring(server)
        demonstrate_bug_detection(server)
        demonstrate_code_quality(server)
        demonstrate_agent_control(server)
        
        console.print("\n[bold green]✓ All demonstrations completed successfully![/bold green]")
        console.print("\n[dim]To use these agents in your UE project:[/dim]")
        console.print("[dim]1. Start the IPC server: python ipc_integration.py --enable-phase3[/dim]")
        console.print("[dim]2. Send commands via the IPC protocol from UE[/dim]")
        console.print("[dim]3. Monitor agents in real-time: python agent_dashboard.py[/dim]")
        
    except Exception as e:
        console.print(f"\n[red]Error initializing server: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
