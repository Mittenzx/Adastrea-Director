#!/usr/bin/env python
"""
Phase 3 Autonomous Agents - Demo Script

Demonstrates the capabilities of Phase 3 agents including:
- Performance profiling and analysis
- Bug detection and reporting
- Code quality analysis
"""

import sys
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from agents.phase3 import (
    EventBus,
    SharedContext,
    PerformanceProfilingAgent,
    BugDetectionAgent,
    CodeQualityAgent,
    EventType,
    ProjectInfo,
    CodeStructure
)

console = Console()


def print_header(title: str):
    """Print a styled header."""
    console.print()
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]", box=box.DOUBLE))
    console.print()


def demo_event_bus():
    """Demonstrate event bus functionality."""
    print_header("Event Bus Demo")
    
    event_bus = EventBus()
    
    # Track received events
    received = []
    
    def handler(event):
        received.append(event)
        console.print(f"  [green]✓[/green] Received: {event.event_type.value} from {event.source}")
    
    # Subscribe to events
    console.print("[yellow]Subscribing to events...[/yellow]")
    event_bus.subscribe(EventType.PERFORMANCE_ALERT, handler)
    event_bus.subscribe(EventType.BUG_DETECTED, handler)
    
    # Publish some events
    console.print("\n[yellow]Publishing events...[/yellow]")
    
    from agents.phase3.event_bus import Event
    
    event1 = Event(
        event_type=EventType.PERFORMANCE_ALERT,
        source="demo",
        payload={"message": "FPS dropped below target"}
    )
    event_bus.publish(event1)
    
    event2 = Event(
        event_type=EventType.BUG_DETECTED,
        source="demo",
        payload={"message": "Crash detected in PlayerController"}
    )
    event_bus.publish(event2)
    
    console.print(f"\n[green]✓[/green] Events published and received: {len(received)}")
    
    # Show history
    history = event_bus.get_history()
    console.print(f"[green]✓[/green] Events in history: {len(history)}")


def demo_shared_context():
    """Demonstrate shared context functionality."""
    print_header("Shared Context Demo")
    
    context = SharedContext()
    
    # Set project info
    console.print("[yellow]Setting project information...[/yellow]")
    project = ProjectInfo(
        name="Demo Game Project",
        root_path="/path/to/project",
        language="C++",
        framework="Unreal Engine 5.3"
    )
    context.set_project_info(project)
    console.print(f"[green]✓[/green] Project: {project.name} ({project.framework})")
    
    # Register agents
    console.print("\n[yellow]Registering agents...[/yellow]")
    context.register_agent("performance_agent")
    context.register_agent("bug_agent")
    context.register_agent("quality_agent")
    
    states = context.get_all_agent_states()
    console.print(f"[green]✓[/green] Registered agents: {len(states)}")
    
    for state in states:
        console.print(f"  • {state.agent_id} - Status: {state.status.value}")
    
    # Set code structure
    console.print("\n[yellow]Setting code structure...[/yellow]")
    code_structure = CodeStructure(
        total_files=150,
        total_lines=25000,
        languages=["C++", "Python", "Blueprint"]
    )
    context.set_code_structure(code_structure)
    console.print(f"[green]✓[/green] Code structure: {code_structure.total_files} files, {code_structure.total_lines} lines")


def demo_performance_agent():
    """Demonstrate performance profiling agent."""
    print_header("Performance Profiling Agent Demo")
    
    event_bus = EventBus()
    context = SharedContext()
    
    # Track alerts
    alerts = []
    
    def alert_handler(event):
        alerts.append(event)
    
    event_bus.subscribe(EventType.PERFORMANCE_ALERT, alert_handler)
    
    # Create agent
    console.print("[yellow]Starting Performance Profiling Agent...[/yellow]")
    agent = PerformanceProfilingAgent(
        event_bus=event_bus,
        shared_context=context,
        target_fps=60.0,
        memory_threshold_mb=4096.0
    )
    agent.start()
    console.print(f"[green]✓[/green] Agent started: {agent.agent_id}")
    
    # Simulate performance scenarios
    scenarios = [
        ("Good Performance", 60.0, 2000.0, 50.0, 60.0, 1500, 500000),
        ("Low FPS", 35.0, 2000.0, 70.0, 85.0, 2500, 850000),
        ("High Memory", 60.0, 5000.0, 50.0, 60.0, 1500, 500000),
        ("High CPU", 55.0, 2000.0, 95.0, 60.0, 1800, 600000),
    ]
    
    console.print("\n[yellow]Analyzing performance scenarios...[/yellow]\n")
    
    for name, fps, mem, cpu, gpu, draws, tris in scenarios:
        console.print(f"[cyan]Scenario:[/cyan] {name}")
        console.print(f"  FPS: {fps}, Memory: {mem} MB, CPU: {cpu}%, GPU: {gpu}%")
        
        metrics = agent.collect_metrics(fps, mem, cpu, gpu, draws, tris)
        analysis = agent.analyze_performance(metrics)
        
        # Display results
        if analysis.bottlenecks:
            console.print(f"  [red]⚠[/red]  {len(analysis.bottlenecks)} bottleneck(s) detected:")
            for bottleneck in analysis.bottlenecks:
                console.print(f"    • [{bottleneck.severity}] {bottleneck.description}")
            
            console.print(f"  [yellow]💡[/yellow] {len(analysis.recommendations)} recommendation(s):")
            for rec in analysis.recommendations[:2]:  # Show top 2
                console.print(f"    • [{rec.priority}] {rec.title}")
        else:
            console.print("  [green]✓[/green] Performance within acceptable parameters")
        
        console.print()
    
    console.print(f"[green]✓[/green] Performance alerts triggered: {len(alerts)}")
    
    # Show metrics history
    history = agent.get_metrics_history()
    console.print(f"[green]✓[/green] Metrics collected: {len(history)}")
    
    # Calculate average FPS
    avg_fps = agent.get_average_fps()
    if avg_fps:
        console.print(f"[green]✓[/green] Average FPS: {avg_fps:.1f}")
    
    agent.stop()
    console.print(f"[green]✓[/green] Agent stopped")


def demo_bug_detection_agent():
    """Demonstrate bug detection agent."""
    print_header("Bug Detection Agent Demo")
    
    event_bus = EventBus()
    context = SharedContext()
    
    # Track bug events
    bugs = []
    
    def bug_handler(event):
        bugs.append(event)
    
    event_bus.subscribe(EventType.BUG_DETECTED, bug_handler)
    event_bus.subscribe(EventType.CRASH_DETECTED, bug_handler)
    
    # Create agent
    console.print("[yellow]Starting Bug Detection Agent...[/yellow]")
    agent = BugDetectionAgent(
        event_bus=event_bus,
        shared_context=context
    )
    agent.start()
    console.print(f"[green]✓[/green] Agent started: {agent.agent_id}")
    
    # Simulate log analysis
    console.print("\n[yellow]Analyzing sample logs...[/yellow]")
    sample_log = """
[2025-11-12 10:15:23] INFO: Game started
[2025-11-12 10:15:25] WARNING: Texture resolution may be too high
[2025-11-12 10:15:30] ERROR: Null pointer exception in PlayerController.cpp:145
[2025-11-12 10:15:31] ERROR: Access violation at address 0x000000
[2025-11-12 10:15:32] WARNING: Memory usage high (3.5 GB)
[2025-11-12 10:15:35] INFO: Player spawned successfully
"""
    
    anomalies = agent.analyze_logs(sample_log)
    console.print(f"[yellow]⚠[/yellow]  Detected {len(anomalies)} anomalies:")
    
    for anomaly in anomalies:
        console.print(f"  • [{anomaly.severity}] {anomaly.description}")
        console.print(f"    Location: {anomaly.location}")
    
    # Simulate crash detection
    console.print("\n[yellow]Detecting crash...[/yellow]")
    crash = agent.detect_crashes(
        stack_trace="""
at PlayerController::Move() [PlayerController.cpp:145]
at GameMode::Tick() [GameMode.cpp:89]
at Engine::MainLoop() [Engine.cpp:234]
""",
        error_message="NullReferenceException: Attempted to access null pointer"
    )
    
    console.print(f"[red]✗[/red] Crash detected: {crash.crash_id}")
    console.print(f"  Error: {crash.error_message}")
    console.print(f"  Location: {crash.location}")
    
    # Create bug report
    console.print("\n[yellow]Creating bug report...[/yellow]")
    bug_report = agent.create_bug_report(
        title="Player movement causes crash",
        description="Moving the player in certain areas causes a null pointer exception",
        severity="high",
        reproduction_steps=[
            "Load level 'TestMap'",
            "Spawn player at coordinates (100, 200, 50)",
            "Press 'W' to move forward",
            "Observe crash"
        ],
        expected_behavior="Player moves smoothly without errors",
        actual_behavior="Game crashes with NullReferenceException"
    )
    
    console.print(f"[green]✓[/green] Bug report created: {bug_report.bug_id}")
    console.print(f"  Title: {bug_report.title}")
    console.print(f"  Severity: {bug_report.severity}")
    console.print(f"  Reproduction steps: {len(bug_report.reproduction_steps)}")
    
    console.print(f"\n[green]✓[/green] Total bugs detected: {len(agent.get_detected_bugs())}")
    console.print(f"[green]✓[/green] Total crashes: {len(agent.get_crash_history())}")
    
    agent.stop()
    console.print(f"[green]✓[/green] Agent stopped")


def demo_code_quality_agent():
    """Demonstrate code quality agent."""
    print_header("Code Quality Agent Demo")
    
    event_bus = EventBus()
    context = SharedContext()
    
    # Create agent
    console.print("[yellow]Starting Code Quality Agent...[/yellow]")
    agent = CodeQualityAgent(
        event_bus=event_bus,
        shared_context=context
    )
    agent.start()
    console.print(f"[green]✓[/green] Agent started: {agent.agent_id}")
    
    # Sample code with issues
    console.print("\n[yellow]Analyzing sample code...[/yellow]")
    sample_code = """
def process_player_input(self, player, input_x, input_y, input_z, input_action, input_modifier):
    # This method is very long and does too many things
    if input_action == 'move':
        if player.health > 0:
            if not player.is_frozen:
                speed = 500  # magic number
                player.x += input_x * speed
                player.y += input_y * speed
                if player.x > 1000:  # another magic number
                    player.x = 1000
                if player.y > 1000:
                    player.y = 1000
                # Process movement effects
                player.apply_movement_effect()
                player.update_animation('walk')
                player.play_sound('footstep')
    elif input_action == 'jump':
        # Similar long code block...
        pass
    # Many more lines...
    
# def old_function():
#     # This is commented code
#     pass

def calculate_damage(attacker, defender):
    damage = attacker.strength * 10  # magic number
    return damage
"""
    
    report = agent.analyze_code("sample_player.py", sample_code)
    
    # Display results
    console.print(f"\n[cyan]Analysis Results:[/cyan]")
    console.print(f"  Quality Score: [yellow]{report.overall_score:.1f}/100[/yellow]")
    console.print(f"  Lines of Code: {report.lines_of_code}")
    console.print(f"  Complexity: {report.complexity_score:.1f}")
    console.print(f"  Code Smells: {len(report.code_smells)}")
    console.print(f"  Violations: {len(report.violations)}")
    
    # Show code smells
    if report.code_smells:
        console.print(f"\n[yellow]⚠[/yellow]  Code Smells Detected:")
        for smell in report.code_smells[:5]:  # Show top 5
            console.print(f"  • [{smell.severity}] {smell.smell_type}: {smell.description}")
            console.print(f"    Location: {smell.location}")
            console.print(f"    [dim]Suggestion: {smell.suggestion}[/dim]")
    
    # Show refactoring opportunities
    if report.refactorings:
        console.print(f"\n[yellow]💡[/yellow] Refactoring Opportunities:")
        for refactoring in report.refactorings[:3]:  # Show top 3
            console.print(f"  • [{refactoring.priority}] {refactoring.refactoring_type}")
            console.print(f"    {refactoring.description}")
            console.print(f"    Effort: {refactoring.estimated_effort}")
            if refactoring.benefits:
                console.print(f"    Benefits: {', '.join(refactoring.benefits[:2])}")
    
    # Calculate technical debt
    console.print("\n[yellow]Calculating technical debt...[/yellow]")
    debt = agent.calculate_technical_debt()
    console.print(f"[cyan]Technical Debt:[/cyan]")
    console.print(f"  Total Hours: {debt.total_debt_hours:.1f}")
    console.print(f"  Debt Ratio: {debt.debt_ratio:.2f}")
    console.print(f"  High Priority Items: {debt.high_priority_items}")
    console.print(f"  Trend: {debt.trend}")
    
    agent.stop()
    console.print(f"\n[green]✓[/green] Agent stopped")


def main():
    """Run all demos."""
    console.print("\n[bold magenta]╔══════════════════════════════════════════════════════╗[/bold magenta]")
    console.print("[bold magenta]║  Phase 3: Autonomous Agents - Demo                  ║[/bold magenta]")
    console.print("[bold magenta]╚══════════════════════════════════════════════════════╝[/bold magenta]\n")
    
    try:
        # Run demos
        demo_event_bus()
        time.sleep(1)
        
        demo_shared_context()
        time.sleep(1)
        
        demo_performance_agent()
        time.sleep(1)
        
        demo_bug_detection_agent()
        time.sleep(1)
        
        demo_code_quality_agent()
        
        # Summary
        print_header("Demo Complete!")
        console.print("[green]✓[/green] All Phase 3 autonomous agents demonstrated successfully!")
        console.print("\n[cyan]Next Steps:[/cyan]")
        console.print("  1. Review PHASE3_GUIDE.md for detailed documentation")
        console.print("  2. Run tests: pytest tests/phase3/ -v")
        console.print("  3. Integrate with your Unreal Engine project")
        console.print()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n[red]Error during demo: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
