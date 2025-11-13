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

console = Console()


class AgentDashboard:
    """Real-time dashboard for monitoring agents."""
    
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
        }
        
        # Subscribe to all events
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to all relevant events."""
        for event_type in self.event_counts.keys():
            self.event_bus.subscribe(event_type, self._on_event)
    
    def _on_event(self, event):
        """Handle incoming events."""
        if event.event_type in self.event_counts:
            self.event_counts[event.event_type] += 1
    
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
        """Generate agent status table."""
        table = Table(title="Agent Status", box=box.ROUNDED, show_header=True)
        
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("State", justify="center")
        
        for name, agent in self.agents.items():
            status = agent.get_status()
            running = agent.is_running()
            
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
            
            table.add_row(name, status_text, state)
        
        return table
    
    def generate_event_summary_table(self) -> Table:
        """Generate event summary table."""
        table = Table(title="Event Summary", box=box.ROUNDED, show_header=True)
        
        table.add_column("Event Type", style="cyan")
        table.add_column("Count", justify="right", style="magenta")
        
        for event_type, count in self.event_counts.items():
            # Color code based on severity
            if count > 0:
                if event_type in [EventType.CRASH_DETECTED, EventType.TEST_FAILED]:
                    count_str = f"[red]{count}[/red]"
                elif event_type in [EventType.PERFORMANCE_ALERT, EventType.CODE_QUALITY_ISSUE]:
                    count_str = f"[yellow]{count}[/yellow]"
                else:
                    count_str = f"[green]{count}[/green]"
            else:
                count_str = str(count)
            
            # Format event type name
            type_name = event_type.value.replace('_', ' ').title()
            
            table.add_row(type_name, count_str)
        
        return table
    
    def generate_recent_events_panel(self, limit: int = 10) -> Panel:
        """Generate recent events panel."""
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
                if event.event_type in [EventType.CRASH_DETECTED, EventType.TEST_FAILED]:
                    style = "red"
                elif event.event_type in [EventType.PERFORMANCE_ALERT, EventType.CODE_QUALITY_ISSUE]:
                    style = "yellow"
                else:
                    style = "green"
                
                text.append(f"[{timestamp}] ", style="dim")
                text.append(f"{event_type}", style=style)
                text.append(f" from {source}\n", style="dim")
        
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
    
    def generate_layout(self) -> Layout:
        """Generate dashboard layout."""
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
        
        # Split left into status and events
        layout["left"].split_column(
            Layout(name="status"),
            Layout(name="event_summary", size=12)
        )
        
        # Split right into recent events and controls
        layout["right"].split_column(
            Layout(name="recent_events"),
            Layout(name="controls", size=6)
        )
        
        # Fill layouts
        layout["header"].update(self.generate_header())
        layout["status"].update(self.generate_agent_status_table())
        layout["event_summary"].update(self.generate_event_summary_table())
        layout["recent_events"].update(self.generate_recent_events_panel())
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
        
        try:
            with Live(self.generate_layout(), refresh_per_second=1, console=console) as live:
                while not self._stop_event.is_set():
                    time.sleep(self.update_interval)
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
