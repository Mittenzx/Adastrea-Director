#!/usr/bin/env python
"""
Agent Orchestrator CLI

Command-line interface for managing and controlling Phase 3 autonomous agents.
Allows starting, stopping, monitoring, and configuring multiple agents.
"""

import sys
import argparse
from typing import Any, Dict, List

from logging_config import get_logger

logger = get_logger(__name__)

try:
    from rich.console import Console
    from rich.table import Table
    from rich import box

    from agents.phase3 import (
        EventBus,
        SharedContext,
        PerformanceProfilingAgent,
        BugDetectionAgent,
        CodeQualityAgent,
        ProjectInfo
    )
    logger.debug("Successfully imported agent orchestrator dependencies")
except ImportError as e:
    # Only exit if this module is being run directly, not imported
    if __name__ == '__main__':
        logger.error(f"Missing required dependencies: {e}")
        print(f"Error: Missing required dependencies")
        print(f"Details: {e}")
        print(f"\nTo install dependencies, run:")
        print(f"  pip install -r requirements.txt")
        print(f"\nOr use the setup script:")
        print(f"  ./setup.sh")
        sys.exit(1)
    else:
        # Re-raise the ImportError if imported as a module
        logger.error(f"Import error when loading agent orchestrator: {e}")
        raise

console = Console()


class AgentOrchestrator:
    """Orchestrator for managing multiple Phase 3 agents."""
    
    def __init__(self):
        """Initialize the orchestrator."""
        logger.info("Initializing Agent Orchestrator")
        self.event_bus = EventBus()
        self.shared_context = SharedContext()
        self.agents: Dict[str, Any] = {}
        self._running = False
        
        # Initialize agents (not started yet)
        self._init_agents()
        logger.debug(f"Initialized {len(self.agents)} agents")
    
    def _init_agents(self):
        """Initialize all available agents."""
        self.agents = {
            'performance': PerformanceProfilingAgent(
                event_bus=self.event_bus,
                shared_context=self.shared_context,
                target_fps=60.0,
                memory_threshold_mb=4096.0
            ),
            'bug_detection': BugDetectionAgent(
                event_bus=self.event_bus,
                shared_context=self.shared_context
            ),
            'code_quality': CodeQualityAgent(
                event_bus=self.event_bus,
                shared_context=self.shared_context
            )
        }
    
    def start_agent(self, agent_name: str) -> bool:
        """
        Start a specific agent.
        
        Args:
            agent_name: Name of the agent to start
            
        Returns:
            True if successful, False otherwise
        """
        if agent_name not in self.agents:
            logger.warning(f"Attempted to start unknown agent: {agent_name}")
            console.print(f"[red]Error:[/red] Unknown agent '{agent_name}'")
            return False
        
        agent = self.agents[agent_name]
        if agent.is_running():
            logger.debug(f"Agent '{agent_name}' is already running")
            console.print(f"[yellow]Warning:[/yellow] Agent '{agent_name}' is already running")
            return False
        
        try:
            agent.start()
            logger.info(f"Successfully started agent: {agent_name}")
            console.print(f"[green]✓[/green] Started agent: {agent_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to start agent '{agent_name}': {e}", exc_info=True)
            console.print(f"[red]Error starting agent '{agent_name}':[/red] {e}")
            return False
    
    def stop_agent(self, agent_name: str) -> bool:
        """
        Stop a specific agent.
        
        Args:
            agent_name: Name of the agent to stop
            
        Returns:
            True if successful, False otherwise
        """
        if agent_name not in self.agents:
            logger.warning(f"Attempted to stop unknown agent: {agent_name}")
            console.print(f"[red]Error:[/red] Unknown agent '{agent_name}'")
            return False
        
        agent = self.agents[agent_name]
        if not agent.is_running():
            logger.debug(f"Agent '{agent_name}' is not running")
            console.print(f"[yellow]Warning:[/yellow] Agent '{agent_name}' is not running")
            return False
        
        try:
            agent.stop()
            logger.info(f"Successfully stopped agent: {agent_name}")
            console.print(f"[green]✓[/green] Stopped agent: {agent_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop agent '{agent_name}': {e}", exc_info=True)
            console.print(f"[red]Error stopping agent '{agent_name}':[/red] {e}")
            return False
    
    def start_all(self) -> None:
        """Start all agents."""
        console.print("[bold cyan]Starting all agents...[/bold cyan]")
        for agent_name in self.agents:
            self.start_agent(agent_name)
    
    def stop_all(self) -> None:
        """Stop all agents."""
        console.print("[bold cyan]Stopping all agents...[/bold cyan]")
        for agent_name in self.agents:
            if self.agents[agent_name].is_running():
                self.stop_agent(agent_name)
    
    def get_status(self) -> Dict[str, Dict]:
        """
        Get status of all agents.
        
        Returns:
            Dictionary mapping agent names to their status information
        """
        status = {}
        for agent_name, agent in self.agents.items():
            status[agent_name] = {
                'running': agent.is_running(),
                'status': agent.get_status().value,
                'agent_id': agent.agent_id
            }
        return status
    
    def display_status(self) -> None:
        """Display status of all agents in a table."""
        table = Table(title="Agent Status", box=box.ROUNDED)
        
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("State", style="green")
        table.add_column("Agent ID", style="blue")
        
        for agent_name, agent in self.agents.items():
            running = "🟢 Running" if agent.is_running() else "🔴 Stopped"
            status = agent.get_status().value
            agent_id = agent.agent_id
            
            table.add_row(agent_name, status, running, agent_id)
        
        console.print(table)
    
    def get_event_history(self, limit: int = 10) -> List:
        """
        Get recent event history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        history = self.event_bus.get_history(limit=limit)
        return history
    
    def display_events(self, limit: int = 10) -> None:
        """
        Display recent events.
        
        Args:
            limit: Maximum number of events to display
        """
        events = self.get_event_history(limit)
        
        if not events:
            console.print("[yellow]No events recorded[/yellow]")
            return
        
        table = Table(title=f"Recent Events (Last {len(events)})", box=box.ROUNDED)
        
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Source", style="magenta")
        table.add_column("Timestamp", style="blue")
        table.add_column("Details", style="white")
        
        for event in events[-limit:]:
            event_type = event.event_type.value
            source = event.source
            timestamp = event.timestamp.strftime("%H:%M:%S")
            details = str(event.payload)[:50] + "..." if len(str(event.payload)) > 50 else str(event.payload)
            
            table.add_row(event_type, source, timestamp, details)
        
        console.print(table)
    
    def configure_project(self, name: str, root_path: str, language: str = "C++", 
                         framework: str = "Unreal Engine") -> None:
        """
        Configure project information.
        
        Args:
            name: Project name
            root_path: Root path to project
            language: Primary programming language
            framework: Framework being used
        """
        project = ProjectInfo(
            name=name,
            root_path=root_path,
            language=language,
            framework=framework
        )
        self.shared_context.set_project_info(project)
        console.print(f"[green]✓[/green] Project configured: {name}")
    
    def list_agents(self) -> None:
        """List all available agents."""
        console.print("[bold cyan]Available Agents:[/bold cyan]")
        for agent_name in self.agents:
            console.print(f"  • {agent_name}")


def cmd_start(orchestrator: AgentOrchestrator, args) -> int:
    """Handle start command."""
    if args.all:
        orchestrator.start_all()
    elif args.agent:
        for agent in args.agent:
            orchestrator.start_agent(agent)
    else:
        console.print("[red]Error:[/red] Specify --agent or --all")
        return 1
    return 0


def cmd_stop(orchestrator: AgentOrchestrator, args) -> int:
    """Handle stop command."""
    if args.all:
        orchestrator.stop_all()
    elif args.agent:
        for agent in args.agent:
            orchestrator.stop_agent(agent)
    else:
        console.print("[red]Error:[/red] Specify --agent or --all")
        return 1
    return 0


def cmd_status(orchestrator: AgentOrchestrator, args) -> int:
    """Handle status command."""
    orchestrator.display_status()
    
    if args.verbose:
        console.print("\n")
        orchestrator.display_events(limit=args.events)
    
    return 0


def cmd_events(orchestrator: AgentOrchestrator, args) -> int:
    """Handle events command."""
    orchestrator.display_events(limit=args.limit)
    return 0


def cmd_list(orchestrator: AgentOrchestrator, args) -> int:
    """Handle list command."""
    orchestrator.list_agents()
    return 0


def cmd_config(orchestrator: AgentOrchestrator, args) -> int:
    """Handle config command."""
    if args.project_name and args.project_path:
        orchestrator.configure_project(
            name=args.project_name,
            root_path=args.project_path,
            language=args.language,
            framework=args.framework
        )
        return 0
    else:
        console.print("[red]Error:[/red] Both --project-name and --project-path are required")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Agent Orchestrator CLI - Manage Phase 3 autonomous agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start all agents
  python agent_orchestrator_cli.py start --all

  # Start specific agents
  python agent_orchestrator_cli.py start --agent performance bug_detection

  # Check status
  python agent_orchestrator_cli.py status

  # View recent events
  python agent_orchestrator_cli.py events --limit 20

  # Configure project
  python agent_orchestrator_cli.py config --project-name "My Game" --project-path "/path/to/project"

  # Stop all agents
  python agent_orchestrator_cli.py stop --all
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start agents')
    start_parser.add_argument('--agent', nargs='+', choices=['performance', 'bug_detection', 'code_quality'],
                            help='Agent(s) to start')
    start_parser.add_argument('--all', action='store_true', help='Start all agents')
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop agents')
    stop_parser.add_argument('--agent', nargs='+', choices=['performance', 'bug_detection', 'code_quality'],
                           help='Agent(s) to stop')
    stop_parser.add_argument('--all', action='store_true', help='Stop all agents')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show agent status')
    status_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed status with events')
    status_parser.add_argument('--events', type=int, default=5, help='Number of events to show in verbose mode')
    
    # Events command
    events_parser = subparsers.add_parser('events', help='Show recent events')
    events_parser.add_argument('--limit', type=int, default=10, help='Number of events to display')
    
    # List command
    subparsers.add_parser('list', help='List available agents')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configure project settings')
    config_parser.add_argument('--project-name', help='Project name')
    config_parser.add_argument('--project-path', help='Project root path')
    config_parser.add_argument('--language', default='C++', help='Primary programming language')
    config_parser.add_argument('--framework', default='Unreal Engine', help='Framework being used')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Create orchestrator
    orchestrator = AgentOrchestrator()
    
    # Execute command
    commands = {
        'start': cmd_start,
        'stop': cmd_stop,
        'status': cmd_status,
        'events': cmd_events,
        'list': cmd_list,
        'config': cmd_config
    }
    
    try:
        return commands[args.command](orchestrator, args)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        orchestrator.stop_all()
        return 130
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
