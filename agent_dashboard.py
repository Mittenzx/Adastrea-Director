#!/usr/bin/env python
"""
Agent Dashboard UI

Real-time terminal-based dashboard for monitoring Phase 3 autonomous agents.
Displays agent status, events, and metrics in a live-updating interface.
"""

import os
import sys
import time
from datetime import datetime
from threading import Event as ThreadEvent
import argparse

# Disable ChromaDB telemetry BEFORE any imports that might import chromadb
# This prevents "capture() takes 1 positional argument but 3 were given" errors
# ChromaDB checks for this variable and disables telemetry when set to "1"
os.environ["ANONYMIZED_TELEMETRY"] = "1"

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich import box
    from rich.text import Text

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
except ImportError as e:
    # Only exit if this module is being run directly, not imported
    if __name__ == '__main__':
        print("Error: Missing required dependencies")
        print(f"Details: {e}")
        print("\nTo install dependencies, run:")
        print("  pip install -r requirements.txt")
        print("\nOr use the setup script:")
        print("  ./setup.sh")
        sys.exit(1)
    else:
        # Re-raise the ImportError if imported as a module
        raise

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
                elif event.event_type in [EventType.PERFORMANCE_ALERT,
                                          EventType.CODE_QUALITY_ISSUE,
                                          EventType.BUG_DETECTED]:
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

        border_style = "green" if is_healthy else "red"

        return Panel(
            text,
            title=f"System Health ({'Healthy' if is_healthy else 'Issues Detected'})",
            box=box.ROUNDED,
            style=border_style
        )

    def generate_performance_metrics_panel(self) -> Panel:
        """Generate performance metrics panel with real-time data."""
        text = Text()

        if not self.agents.get('Performance'):
            text.append("Performance agent not available", style="dim italic")
        else:
            agent = self.agents['Performance']

            # Get recent metrics
            recent_metrics = agent.get_metrics_history(limit=1)

            if not recent_metrics:
                text.append("No metrics collected yet", style="yellow italic")
            else:
                metrics = recent_metrics[-1]

                text.append("Performance Metrics:\n", style="bold cyan")

                # FPS with color coding
                fps = metrics.frame_rate
                if fps >= 55:
                    fps_style = "green"
                elif fps >= 30:
                    fps_style = "yellow"
                else:
                    fps_style = "red"
                text.append("\n📊 Frame Rate: ", style="dim")
                text.append(f"{fps:.1f} FPS", style=f"bold {fps_style}")

                # Memory usage
                mem = metrics.memory_usage_mb
                mem_threshold = agent.memory_threshold_mb
                if mem < mem_threshold * 0.7:
                    mem_style = "green"
                elif mem < mem_threshold:
                    mem_style = "yellow"
                else:
                    mem_style = "red"
                text.append("\n💾 Memory: ", style="dim")
                text.append(f"{mem:.0f} MB", style=f"bold {mem_style}")
                text.append(f" / {mem_threshold:.0f} MB", style="dim")

                # CPU usage
                cpu = metrics.cpu_usage_percent
                if cpu < 70:
                    cpu_style = "green"
                elif cpu < 90:
                    cpu_style = "yellow"
                else:
                    cpu_style = "red"
                text.append("\n🖥️  CPU: ", style="dim")
                text.append(f"{cpu:.1f}%", style=f"bold {cpu_style}")

                # GPU usage
                gpu = metrics.gpu_usage_percent
                if gpu < 80:
                    gpu_style = "green"
                elif gpu < 95:
                    gpu_style = "yellow"
                else:
                    gpu_style = "red"
                text.append("\n🎮 GPU: ", style="dim")
                text.append(f"{gpu:.1f}%", style=f"bold {gpu_style}")

                # Draw calls and triangles
                if metrics.draw_calls > 0:
                    text.append("\n📐 Draw Calls: ", style="dim")
                    text.append(f"{metrics.draw_calls:,}", style="cyan")
                if metrics.triangles > 0:
                    text.append("\n🔺 Triangles: ", style="dim")
                    text.append(f"{metrics.triangles:,}", style="cyan")

                # Average FPS
                avg_fps = agent.get_average_fps(duration_seconds=60)
                if avg_fps:
                    text.append("\n\n📈 Avg FPS (60s): ", style="dim")
                    text.append(f"{avg_fps:.1f}", style="cyan")

        return Panel(
            text,
            title="Performance Profiling",
            box=box.ROUNDED,
            style="magenta"
        )

    def generate_bug_detection_panel(self) -> Panel:
        """Generate bug detection status panel."""
        text = Text()

        if not self.agents.get('Bug Detection'):
            text.append("Bug detection agent not available", style="dim italic")
        else:
            agent = self.agents['Bug Detection']

            # Get bug statistics
            bugs = agent.get_detected_bugs()
            crashes = agent.get_crash_history()
            test_history = agent.get_test_history()

            text.append("Bug Detection Status:\n", style="bold cyan")

            # Bug counts by severity
            text.append("\n🐛 Total Bugs: ", style="dim")
            if bugs:
                critical_bugs = len([b for b in bugs if b.severity == 'critical'])
                high_bugs = len([b for b in bugs if b.severity == 'high'])
                medium_bugs = len([b for b in bugs if b.severity == 'medium'])
                low_bugs = len([b for b in bugs if b.severity == 'low'])

                text.append(f"{len(bugs)}", style="bold yellow")
                text.append("\n  Critical: ", style="dim")
                text.append(f"{critical_bugs}", style="red bold" if critical_bugs > 0 else "dim")
                text.append("\n  High: ", style="dim")
                text.append(f"{high_bugs}", style="yellow bold" if high_bugs > 0 else "dim")
                text.append("\n  Medium: ", style="dim")
                text.append(f"{medium_bugs}", style="yellow" if medium_bugs > 0 else "dim")
                text.append("\n  Low: ", style="dim")
                text.append(f"{low_bugs}", style="cyan" if low_bugs > 0 else "dim")
            else:
                text.append("0", style="green bold")

            # Crashes
            text.append("\n💥 Crashes: ", style="dim")
            crash_style = "red bold" if len(crashes) > 0 else "green bold"
            text.append(f"{len(crashes)}", style=crash_style)

            # Test results
            if test_history:
                latest_test = test_history[-1]
                text.append("\n\n🧪 Latest Test Run:\n", style="dim")
                text.append("  Passed: ", style="dim")
                text.append(f"{latest_test.passed}/{latest_test.total_tests}", style="green")
                text.append("\n  Failed: ", style="dim")
                fail_style = "red" if latest_test.failed > 0 else "green"
                text.append(f"{latest_test.failed}", style=fail_style)
                text.append("\n  Success Rate: ", style="dim")
                success_rate = latest_test.success_rate()
                sr_style = "green" if success_rate >= 90 else "yellow" if success_rate >= 70 else "red"
                text.append(f"{success_rate:.1f}%", style=sr_style)
            else:
                text.append("\n\n🧪 No test runs recorded", style="dim italic")

        return Panel(
            text,
            title="Bug Detection",
            box=box.ROUNDED,
            style="red"
        )

    def generate_code_quality_panel(self) -> Panel:
        """Generate code quality monitoring panel."""
        text = Text()

        if not self.agents.get('Code Quality'):
            text.append("Code quality agent not available", style="dim italic")
        else:
            agent = self.agents['Code Quality']

            # Get quality reports
            reports = agent.get_quality_reports(limit=10)

            text.append("Code Quality Status:\n", style="bold cyan")

            if not reports:
                text.append("\nNo code analyzed yet", style="yellow italic")
            else:
                # Overall quality score (average)
                avg_score = sum(r.overall_score for r in reports) / len(reports)
                score_style = "green" if avg_score >= 80 else "yellow" if avg_score >= 60 else "red"
                text.append("\n📊 Average Quality Score: ", style="dim")
                text.append(f"{avg_score:.1f}/100", style=f"bold {score_style}")

                # Total issues
                total_smells = sum(len(r.code_smells) for r in reports)
                total_violations = sum(len(r.violations) for r in reports)

                text.append("\n\n👃 Code Smells: ", style="dim")
                smell_style = "red" if total_smells > 10 else "yellow" if total_smells > 5 else "green"
                text.append(f"{total_smells}", style=smell_style)

                text.append("\n⚠️  Violations: ", style="dim")
                viol_style = "red" if total_violations > 20 else "yellow" if total_violations > 10 else "green"
                text.append(f"{total_violations}", style=viol_style)

                # Technical debt
                debt = agent.calculate_technical_debt()
                text.append("\n\n💸 Technical Debt:\n", style="dim")
                text.append("  Hours: ", style="dim")
                if debt.total_debt_hours > 40:
                    debt_style = "red"
                elif debt.total_debt_hours > 20:
                    debt_style = "yellow"
                else:
                    debt_style = "green"
                text.append(f"{debt.total_debt_hours:.1f}h", style=debt_style)
                text.append("\n  Ratio: ", style="dim")
                text.append(f"{debt.debt_ratio:.2f}", style="cyan")
                text.append("\n  High Priority: ", style="dim")
                hp_style = "red" if debt.high_priority_items > 0 else "green"
                text.append(f"{debt.high_priority_items}", style=hp_style)

                # Recent analysis
                latest = reports[-1]
                text.append("\n\n📄 Latest Analysis:\n", style="dim")
                text.append("  File: ", style="dim")
                file_name = latest.file_path.split('/')[-1] if '/' in latest.file_path else latest.file_path
                text.append(f"{file_name}\n", style="cyan")
                text.append("  Score: ", style="dim")
                text.append(f"{latest.overall_score:.1f}/100", style=score_style)

        return Panel(
            text,
            title="Code Quality",
            box=box.ROUNDED,
            style="blue"
        )

    def generate_layout(self) -> Layout:
        """Generate enhanced dashboard layout with performance, bug detection, and code quality panels."""
        layout = Layout()

        # Split into header and body
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )

        # Split body into top and bottom sections
        layout["body"].split_row(
            Layout(name="left_column"),
            Layout(name="middle_column"),
            Layout(name="right_column")
        )

        # Left column: System health, agent status
        layout["left_column"].split_column(
            Layout(name="system_health", size=10),
            Layout(name="status")
        )

        # Middle column: Performance metrics, bug detection, code quality
        layout["middle_column"].split_column(
            Layout(name="performance_metrics", size=18),
            Layout(name="bug_detection", size=15),
            Layout(name="code_quality", size=15)
        )

        # Right column: Event summary, recent events, error details, controls
        error_size = 8 if self.agent_errors else 0
        if error_size > 0:
            error_layout = Layout(name="error_details", size=error_size)
        else:
            error_layout = Layout(name="error_details", visible=False)

        layout["right_column"].split_column(
            Layout(name="event_summary", size=12),
            Layout(name="recent_events"),
            error_layout,
            Layout(name="controls", size=6)
        )

        # Fill layouts
        layout["header"].update(self.generate_header())
        layout["system_health"].update(self.generate_system_health_panel())
        layout["status"].update(self.generate_agent_status_table())
        layout["performance_metrics"].update(self.generate_performance_metrics_panel())
        layout["bug_detection"].update(self.generate_bug_detection_panel())
        layout["code_quality"].update(self.generate_code_quality_panel())
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
