#!/usr/bin/env python
"""
Agent Dashboard UI

Real-time terminal-based dashboard for monitoring Phase 3 autonomous agents.
Displays agent status, events, and metrics in a live-updating interface.
"""

import sys
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.text import Text
from threading import Event as ThreadEvent
import argparse

from agents.phase3 import (
    EventBus,
    SharedContext,
    PerformanceProfilingAgent,
    BugDetectionAgent,
    CodeQualityAgent,
    EventType,
    AgentStatus
)
from system_health import SystemHealthChecker

console = Console()


class AgentDashboard:
    """Real-time dashboard for monitoring agents."""
    
    # Configuration constants
    HEALTH_CHECK_INTERVAL = 5  # Seconds between health check updates
    
    def __init__(self, update_interval: float = 1.0):
        """
        Initialize the dashboard.
        
        Args:
            update_interval: How often to update the display (seconds)
        """
        self.event_bus = EventBus()
        self.shared_context = SharedContext()
        self.update_interval = update_interval
        self._stop_event = ThreadEvent()
        
        # Initialize agents
        self.agents = {
            'Performance': PerformanceProfilingAgent(
                event_bus=self.event_bus,
                shared_context=self.shared_context,
                target_fps=60.0,
                memory_threshold_mb=4096.0
            ),
            'Bug Detection': BugDetectionAgent(
                event_bus=self.event_bus,
                shared_context=self.shared_context
            ),
            'Code Quality': CodeQualityAgent(
                event_bus=self.event_bus,
                shared_context=self.shared_context
            )
        }
        
        # Event counters
        self.event_counts = {
            EventType.PERFORMANCE_ALERT: 0,
            EventType.BUG_DETECTED: 0,
            EventType.CRASH_DETECTED: 0,
            EventType.CODE_QUALITY_ISSUE: 0,
            EventType.REFACTORING_OPPORTUNITY: 0,
            EventType.TEST_COMPLETED: 0,
            EventType.TEST_FAILED: 0,
            EventType.AGENT_ERROR: 0,
        }
        
        # Track last errors for each agent
        self.agent_errors = {}
        
        # Initialize health checker
        self.health_checker = SystemHealthChecker()
        self.system_health = {}
        
        # Subscribe to all events
        self._subscribe_to_events()
        
        # Also subscribe to agent errors specifically
        self.event_bus.subscribe(EventType.AGENT_ERROR, self._on_agent_error)
    
    def _subscribe_to_events(self):
        """Subscribe to all relevant events."""
        for event_type in self.event_counts.keys():
            self.event_bus.subscribe(event_type, self._on_event)
    
    def _on_event(self, event):
        """Handle incoming events."""
        if event.event_type in self.event_counts:
            self.event_counts[event.event_type] += 1
    
    def _on_agent_error(self, event):
        """Handle agent error events to track error details."""
        agent_id = event.payload.get('agent_id', event.source)
        error_msg = event.payload.get('error', 'Unknown error')
        error_count = event.payload.get('error_count', 1)
        
        self.agent_errors[agent_id] = {
            'error': error_msg,
            'timestamp': event.timestamp,
            'count': error_count
        }
    
    def start_all_agents(self):
        """Start all agents."""
        for name, agent in self.agents.items():
            if not agent.is_running():
                agent.start()
    
    def stop_all_agents(self):
        """Stop all agents."""
        for name, agent in self.agents.items():
            if agent.is_running():
                agent.stop()
    
    def generate_header(self) -> Panel:
        """Generate dashboard header."""
        title = Text()
        title.append("🤖 Agent Dashboard ", style="bold cyan")
        title.append(f"- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
        
        return Panel(
            title,
            box=box.DOUBLE,
            style="cyan"
        )
    
    def generate_agent_status_table(self) -> Table:
        """Generate agent status table with detailed metrics."""
        table = Table(title="Agent Status", box=box.ROUNDED, show_header=True)
        
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("State", justify="center")
        table.add_column("Tasks", justify="right", style="dim")
        table.add_column("Success Rate", justify="right")
        table.add_column("Last Error", style="red", no_wrap=True)
        
        for name, agent in self.agents.items():
            status = agent.get_status()
            running = agent.is_running()
            agent_state = self.shared_context.get_agent_state(agent.agent_id)
            
            # Color code status
            if running:
                state = "[green]🟢 Running[/green]"
            else:
                state = "[red]🔴 Stopped[/red]"
            
            # Color code agent status
            if status == AgentStatus.BUSY:
                status_text = "[yellow]BUSY[/yellow]"
            elif status == AgentStatus.IDLE:
                status_text = "[green]IDLE[/green]"
            elif status == AgentStatus.ERROR:
                status_text = "[red]ERROR[/red]"
            else:
                status_text = status.value
            
            # Get metrics
            tasks_info = "-"
            success_rate_text = "-"
            last_error = "-"
            
            if agent_state:
                metrics = agent_state.metrics
                total_tasks = metrics.tasks_completed + metrics.tasks_failed
                if total_tasks > 0:
                    tasks_info = f"{metrics.tasks_completed}/{total_tasks}"
                    success_rate = metrics.success_rate()
                    
                    # Color code success rate
                    if success_rate >= 90:
                        success_rate_text = f"[green]{success_rate:.0f}%[/green]"
                    elif success_rate >= 70:
                        success_rate_text = f"[yellow]{success_rate:.0f}%[/yellow]"
                    else:
                        success_rate_text = f"[red]{success_rate:.0f}%[/red]"
                
                # Get last error
                if agent.agent_id in self.agent_errors:
                    error_info = self.agent_errors[agent.agent_id]
                    error_msg = error_info['error']
                    # Truncate long errors
                    if len(error_msg) > 30:
                        error_msg = error_msg[:27] + "..."
                    last_error = f"{error_msg}"
            
            table.add_row(name, status_text, state, tasks_info, success_rate_text, last_error)
        
        return table
    
    def generate_event_summary_table(self) -> Table:
        """Generate event summary table."""
        table = Table(title="Event Summary", box=box.ROUNDED, show_header=True)
        
        table.add_column("Event Type", style="cyan")
        table.add_column("Count", justify="right", style="magenta")
        
        for event_type, count in self.event_counts.items():
            # Color code based on severity
            if count > 0:
                if event_type in [EventType.CRASH_DETECTED, EventType.TEST_FAILED, EventType.AGENT_ERROR]:
                    count_str = f"[red bold]{count}[/red bold]"
                elif event_type in [EventType.PERFORMANCE_ALERT, EventType.CODE_QUALITY_ISSUE, EventType.BUG_DETECTED]:
                    count_str = f"[yellow]{count}[/yellow]"
                else:
                    count_str = f"[green]{count}[/green]"
            else:
                count_str = f"[dim]{count}[/dim]"
            
            # Format event type name
            type_name = event_type.value.replace('_', ' ').title()
            
            table.add_row(type_name, count_str)
        
        return table
    
    def generate_recent_events_panel(self, limit: int = 10) -> Panel:
        """Generate recent events panel with detailed information."""
        events = self.event_bus.get_history(limit=limit)
        
        if not events:
            text = Text("No events recorded", style="dim italic")
        else:
            text = Text()
            for event in events[-limit:]:
                timestamp = event.timestamp.strftime("%H:%M:%S")
                event_type = event.event_type.value
                source = event.source
                
                # Color code by event type
                if event.event_type in [EventType.CRASH_DETECTED, EventType.TEST_FAILED, EventType.AGENT_ERROR]:
                    style = "red"
                    icon = "❌"
                elif event.event_type in [EventType.PERFORMANCE_ALERT, EventType.CODE_QUALITY_ISSUE, EventType.BUG_DETECTED]:
                    style = "yellow"
                    icon = "⚠️"
                else:
                    style = "green"
                    icon = "✓"
                
                text.append(f"[{timestamp}] {icon} ", style="dim")
                text.append(f"{event_type}", style=style)
                text.append(f" from {source}", style="dim")
                
                # Show error details for error events
                if event.event_type == EventType.AGENT_ERROR and 'error' in event.payload:
                    error_msg = str(event.payload['error'])
                    if len(error_msg) > 50:
                        error_msg = error_msg[:47] + "..."
                    text.append(f"\n    {error_msg}", style="red dim")
                
                text.append("\n")
        
        return Panel(
            text,
            title="Recent Events",
            box=box.ROUNDED,
            style="blue"
        )
    
    def generate_controls_panel(self) -> Panel:
        """Generate controls panel."""
        text = Text()
        text.append("Controls:\n", style="bold cyan")
        text.append("  Press ", style="dim")
        text.append("Ctrl+C", style="bold yellow")
        text.append(" to exit\n", style="dim")
        text.append("  Use ", style="dim")
        text.append("agent_orchestrator_cli.py", style="bold cyan")
        text.append(" to control agents", style="dim")
        
        return Panel(
            text,
            box=box.ROUNDED,
            style="cyan"
        )
    
    def generate_error_details_panel(self) -> Panel:
        """Generate detailed error information panel."""
        from datetime import datetime
        
        text = Text()
        
        if not self.agent_errors:
            text.append("No errors reported", style="green italic")
        else:
            text.append("Agent Errors:\n", style="bold red")
            for agent_id, error_info in self.agent_errors.items():
                # Ensure timestamp is a datetime object
                timestamp = error_info['timestamp']
                if not isinstance(timestamp, datetime):
                    timestamp = datetime.fromtimestamp(timestamp)
                timestamp_str = timestamp.strftime("%H:%M:%S")
                
                error_msg = error_info['error']
                error_count = error_info['count']
                
                # Find agent name
                agent_name = agent_id
                for name, agent in self.agents.items():
                    if agent.agent_id == agent_id:
                        agent_name = name
                        break
                
                text.append(f"\n[{timestamp_str}] ", style="dim")
                text.append(f"{agent_name}", style="cyan")
                text.append(f" (x{error_count})\n", style="yellow")
                text.append(f"  {error_msg}", style="red")
        
        return Panel(
            text,
            title="Error Details",
            box=box.ROUNDED,
            style="red"
        )
    
    def update_system_health(self):
        """Update system health checks."""
        self.system_health = self.health_checker.check_all()
    
    def generate_system_health_panel(self) -> Panel:
        """Generate system health status panel."""
        text = Text()
        
        if not self.system_health:
            text.append("Health checks not yet run\n", style="dim italic")
            text.append("Run update_system_health() to check", style="dim")
        else:
            text.append("System Health:\n", style="bold cyan")
            
            for component, status in self.system_health.items():
                icon = "✓" if status.healthy else "✗"
                style = "green" if status.healthy else "red"
                
                text.append(f"\n{icon} ", style=style)
                text.append(f"{status.component}: ", style="cyan")
                text.append(f"{status.message}", style=style)
                
                # Show document count if available
                if status.details and 'document_count' in status.details:
                    doc_count = status.details['document_count']
                    text.append(f"\n   Documents: {doc_count}", style="dim")
        
        # Overall system health indicator
        is_healthy = all(s.healthy for s in self.system_health.values() 
                        if s.component in ['LLM API', 'Vector Database'])
        
        overall_style = "green" if is_healthy else "red"
        border_style = "green" if is_healthy else "red"
        
        return Panel(
            text,
            title=f"System Health ({'Healthy' if is_healthy else 'Issues Detected'})",
            box=box.ROUNDED,
            style=border_style
        )
    
    def generate_layout(self) -> Layout:
        """Generate dashboard layout with error details and system health."""
        layout = Layout()
        
        # Split into header and body
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )
        
        # Split body into left and right
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Split left into system health, status and events
        layout["left"].split_column(
            Layout(name="system_health", size=10),
            Layout(name="status"),
            Layout(name="event_summary", size=12)
        )
        
        # Split right into recent events, error details and controls
        # Adjust sizes based on whether there are errors
        error_size = 8 if self.agent_errors else 0
        layout["right"].split_column(
            Layout(name="recent_events"),
            Layout(name="error_details", size=error_size) if error_size > 0 else Layout(name="error_details", visible=False),
            Layout(name="controls", size=6)
        )
        
        # Update system health periodically (not every frame to reduce overhead)
        # We'll update it in the run loop
        
        # Fill layouts
        layout["header"].update(self.generate_header())
        layout["system_health"].update(self.generate_system_health_panel())
        layout["status"].update(self.generate_agent_status_table())
        layout["event_summary"].update(self.generate_event_summary_table())
        layout["recent_events"].update(self.generate_recent_events_panel())
        
        # Only show error details if there are errors
        if self.agent_errors:
            layout["error_details"].update(self.generate_error_details_panel())
        
        layout["controls"].update(self.generate_controls_panel())
        
        return layout
    
    def run(self, auto_start: bool = False):
        """
        Run the dashboard.
        
        Args:
            auto_start: Whether to automatically start all agents
        """
        if auto_start:
            console.print("[cyan]Starting all agents...[/cyan]")
            self.start_all_agents()
            time.sleep(0.5)
        
        # Initial health check
        console.print("[cyan]Running system health checks...[/cyan]")
        self.update_system_health()
        
        try:
            health_check_counter = 0
            with Live(self.generate_layout(), refresh_per_second=1, console=console) as live:
                while not self._stop_event.is_set():
                    time.sleep(self.update_interval)
                    
                    # Update system health periodically to reduce overhead
                    health_check_counter += 1
                    if health_check_counter >= self.HEALTH_CHECK_INTERVAL:
                        self.update_system_health()
                        health_check_counter = 0
                    
                    live.update(self.generate_layout())
        except KeyboardInterrupt:
            console.print("\n[yellow]Dashboard interrupted by user[/yellow]")
        finally:
            if auto_start:
                console.print("[cyan]Stopping all agents...[/cyan]")
                self.stop_all_agents()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Agent Dashboard - Real-time monitoring for Phase 3 agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start dashboard (agents stopped initially)
  python agent_dashboard.py

  # Start dashboard and auto-start all agents
  python agent_dashboard.py --auto-start

  # Custom update interval
  python agent_dashboard.py --interval 2.0
        """
    )
    
    parser.add_argument('--auto-start', action='store_true',
                       help='Automatically start all agents on launch')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='Update interval in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    try:
        dashboard = AgentDashboard(update_interval=args.interval)
        dashboard.run(auto_start=args.auto_start)
        return 0
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
