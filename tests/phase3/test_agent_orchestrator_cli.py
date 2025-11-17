"""
Integration tests for Agent Orchestrator CLI

Tests the orchestrator functionality including:
- Agent lifecycle management (start/stop)
- Status reporting
- Event handling
- Project configuration
- CLI commands
"""

from agent_orchestrator_cli import AgentOrchestrator
from agents.phase3 import EventType


class TestAgentOrchestrator:
    """Test suite for AgentOrchestrator class."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes with all agents."""
        orchestrator = AgentOrchestrator()
        
        assert orchestrator is not None
        assert orchestrator.event_bus is not None
        assert orchestrator.shared_context is not None
        assert len(orchestrator.agents) == 3
        assert 'performance' in orchestrator.agents
        assert 'bug_detection' in orchestrator.agents
        assert 'code_quality' in orchestrator.agents
    
    def test_list_agents(self):
        """Test listing available agents."""
        orchestrator = AgentOrchestrator()
        
        # Should not raise any errors
        orchestrator.list_agents()
    
    def test_get_status_all_stopped(self):
        """Test getting status when all agents are stopped."""
        orchestrator = AgentOrchestrator()
        
        status = orchestrator.get_status()
        
        assert len(status) == 3
        for agent_name, agent_status in status.items():
            assert agent_status['running'] is False
            assert agent_status['agent_id'] is not None
    
    def test_start_single_agent(self):
        """Test starting a single agent."""
        orchestrator = AgentOrchestrator()
        
        result = orchestrator.start_agent('performance')
        
        assert result is True
        assert orchestrator.agents['performance'].is_running()
        
        # Clean up
        orchestrator.stop_agent('performance')
    
    def test_start_invalid_agent(self):
        """Test starting a non-existent agent."""
        orchestrator = AgentOrchestrator()
        
        result = orchestrator.start_agent('invalid_agent')
        
        assert result is False
    
    def test_start_agent_already_running(self):
        """Test starting an agent that is already running."""
        orchestrator = AgentOrchestrator()
        
        orchestrator.start_agent('performance')
        result = orchestrator.start_agent('performance')
        
        assert result is False
        
        # Clean up
        orchestrator.stop_agent('performance')
    
    def test_stop_single_agent(self):
        """Test stopping a single agent."""
        orchestrator = AgentOrchestrator()
        
        orchestrator.start_agent('performance')
        result = orchestrator.stop_agent('performance')
        
        assert result is True
        assert not orchestrator.agents['performance'].is_running()
    
    def test_stop_invalid_agent(self):
        """Test stopping a non-existent agent."""
        orchestrator = AgentOrchestrator()
        
        result = orchestrator.stop_agent('invalid_agent')
        
        assert result is False
    
    def test_stop_agent_not_running(self):
        """Test stopping an agent that is not running."""
        orchestrator = AgentOrchestrator()
        
        result = orchestrator.stop_agent('performance')
        
        assert result is False
    
    def test_start_all_agents(self):
        """Test starting all agents at once."""
        orchestrator = AgentOrchestrator()
        
        orchestrator.start_all()
        
        for agent_name, agent in orchestrator.agents.items():
            assert agent.is_running(), f"Agent {agent_name} should be running"
        
        # Clean up
        orchestrator.stop_all()
    
    def test_stop_all_agents(self):
        """Test stopping all agents at once."""
        orchestrator = AgentOrchestrator()
        
        orchestrator.start_all()
        orchestrator.stop_all()
        
        for agent_name, agent in orchestrator.agents.items():
            assert not agent.is_running(), f"Agent {agent_name} should be stopped"
    
    def test_get_status_with_running_agents(self):
        """Test getting status when agents are running."""
        orchestrator = AgentOrchestrator()
        
        orchestrator.start_agent('performance')
        orchestrator.start_agent('bug_detection')
        
        status = orchestrator.get_status()
        
        assert status['performance']['running'] is True
        assert status['bug_detection']['running'] is True
        assert status['code_quality']['running'] is False
        
        # Clean up
        orchestrator.stop_all()
    
    def test_display_status(self):
        """Test status display method."""
        orchestrator = AgentOrchestrator()
        
        # Should not raise any errors
        orchestrator.display_status()
        
        orchestrator.start_agent('performance')
        orchestrator.display_status()
        
        # Clean up
        orchestrator.stop_agent('performance')
    
    def test_configure_project(self):
        """Test project configuration."""
        orchestrator = AgentOrchestrator()
        
        orchestrator.configure_project(
            name="Test Project",
            root_path="/test/path",
            language="C++",
            framework="Unreal Engine 5.3"
        )
        
        project_info = orchestrator.shared_context.get_project_info()
        
        assert project_info is not None
        assert project_info.name == "Test Project"
        assert project_info.root_path == "/test/path"
        assert project_info.language == "C++"
        assert project_info.framework == "Unreal Engine 5.3"
    
    def test_get_event_history_empty(self):
        """Test getting event history when no events exist."""
        orchestrator = AgentOrchestrator()
        
        events = orchestrator.get_event_history(limit=10)
        
        # Should return empty list or only system events
        assert isinstance(events, list)
    
    def test_get_event_history_with_events(self):
        """Test getting event history after agent activity."""
        orchestrator = AgentOrchestrator()
        
        # Start an agent to generate events
        orchestrator.start_agent('performance')
        
        events = orchestrator.get_event_history(limit=10)
        
        assert len(events) > 0
        # Should have at least an agent_started event
        event_types = [e.event_type for e in events]
        assert EventType.AGENT_STARTED in event_types
        
        # Clean up
        orchestrator.stop_agent('performance')
    
    def test_display_events(self):
        """Test event display method."""
        orchestrator = AgentOrchestrator()
        
        # Should handle empty events gracefully
        orchestrator.display_events(limit=5)
        
        # Start agent and display events
        orchestrator.start_agent('performance')
        orchestrator.display_events(limit=5)
        
        # Clean up
        orchestrator.stop_agent('performance')


class TestAgentOrchestrationIntegration:
    """Integration tests for complete orchestration workflows."""
    
    def test_performance_agent_workflow(self):
        """Test complete workflow with performance agent."""
        orchestrator = AgentOrchestrator()
        
        # Configure project
        orchestrator.configure_project(
            name="Test Game",
            root_path="/test/game",
            language="C++",
            framework="Unreal Engine"
        )
        
        # Start performance agent
        result = orchestrator.start_agent('performance')
        assert result is True
        
        # Get agent and collect metrics
        perf_agent = orchestrator.agents['performance']
        metrics = perf_agent.collect_metrics(
            frame_rate=55.0,
            memory_usage_mb=3500.0,
            cpu_usage_percent=70.0,
            gpu_usage_percent=80.0,
            draw_calls=1500,
            triangles=700000
        )
        
        assert metrics is not None
        assert metrics.frame_rate == 55.0
        
        # Analyze performance
        analysis = perf_agent.analyze_performance(metrics)
        assert analysis is not None
        
        # Check events
        events = orchestrator.get_event_history(limit=10)
        event_types = [e.event_type for e in events]
        assert EventType.AGENT_STARTED in event_types
        assert EventType.PERFORMANCE_METRICS_COLLECTED in event_types
        
        # Stop agent
        result = orchestrator.stop_agent('performance')
        assert result is True
    
    def test_bug_detection_agent_workflow(self):
        """Test complete workflow with bug detection agent."""
        orchestrator = AgentOrchestrator()
        
        # Start bug detection agent
        result = orchestrator.start_agent('bug_detection')
        assert result is True
        
        # Get agent and analyze logs
        bug_agent = orchestrator.agents['bug_detection']
        log_content = """
        [ERROR] Null pointer exception in PlayerController::Tick
        [ERROR] Failed to load asset: /Game/Assets/Character
        [WARNING] Memory leak detected in NetworkManager
        [ERROR] Assertion failed: IsValid(Player)
        """
        
        anomalies = bug_agent.analyze_logs(log_content)
        assert len(anomalies) > 0
        
        # Check events
        events = orchestrator.get_event_history(limit=10)
        event_types = [e.event_type for e in events]
        assert EventType.AGENT_STARTED in event_types
        
        # Stop agent
        result = orchestrator.stop_agent('bug_detection')
        assert result is True
    
    def test_code_quality_agent_workflow(self):
        """Test complete workflow with code quality agent."""
        orchestrator = AgentOrchestrator()
        
        # Start code quality agent
        result = orchestrator.start_agent('code_quality')
        assert result is True
        
        # Get agent and analyze code
        quality_agent = orchestrator.agents['code_quality']
        sample_code = """
        def process_data():
            x = 100
            y = 200
            z = 300
            return x + y + z
        
        def another_function():
            a = 1
            b = 2
            c = 3
            d = 4
            e = 5
            return a + b + c + d + e
        """
        
        report = quality_agent.analyze_code("sample.py", sample_code)
        assert report is not None
        assert report.overall_score >= 0
        assert report.overall_score <= 100
        
        # Check events
        events = orchestrator.get_event_history(limit=10)
        event_types = [e.event_type for e in events]
        assert EventType.AGENT_STARTED in event_types
        
        # Stop agent
        result = orchestrator.stop_agent('code_quality')
        assert result is True
    
    def test_multi_agent_coordination(self):
        """Test multiple agents running simultaneously."""
        orchestrator = AgentOrchestrator()
        
        # Start all agents
        orchestrator.start_all()
        
        # Verify all are running
        status = orchestrator.get_status()
        for agent_name, agent_status in status.items():
            assert agent_status['running'] is True
        
        # Generate activity from each agent
        perf_agent = orchestrator.agents['performance']
        bug_agent = orchestrator.agents['bug_detection']
        quality_agent = orchestrator.agents['code_quality']
        
        # Performance metrics
        perf_metrics = perf_agent.collect_metrics(
            frame_rate=45.0,
            memory_usage_mb=5000.0,
            cpu_usage_percent=90.0,
            gpu_usage_percent=95.0,
            draw_calls=3000,
            triangles=1500000
        )
        perf_agent.analyze_performance(perf_metrics)
        
        # Bug detection
        logs = "[ERROR] Critical failure\n[ERROR] Crash detected"
        bug_agent.analyze_logs(logs)
        
        # Code quality
        code = "def bad_code():\n    x = 1000\n    return x * 2"
        quality_agent.analyze_code("bad.py", code)
        
        # Check that all agents generated events
        events = orchestrator.get_event_history(limit=20)
        sources = set(e.source for e in events)
        
        assert 'performance_profiling_agent' in sources
        assert 'bug_detection_agent' in sources
        assert 'code_quality_agent' in sources
        
        # Stop all agents
        orchestrator.stop_all()
        
        # Verify all are stopped
        status = orchestrator.get_status()
        for agent_name, agent_status in status.items():
            assert agent_status['running'] is False
    
    def test_agent_restart(self):
        """Test stopping and restarting an agent."""
        orchestrator = AgentOrchestrator()
        
        # Start agent
        orchestrator.start_agent('performance')
        assert orchestrator.agents['performance'].is_running()
        
        # Stop agent
        orchestrator.stop_agent('performance')
        assert not orchestrator.agents['performance'].is_running()
        
        # Restart agent
        orchestrator.start_agent('performance')
        assert orchestrator.agents['performance'].is_running()
        
        # Clean up
        orchestrator.stop_agent('performance')
    
    def test_event_history_ordering(self):
        """Test that event history maintains chronological order."""
        orchestrator = AgentOrchestrator()
        
        # Start multiple agents in sequence
        orchestrator.start_agent('performance')
        orchestrator.start_agent('bug_detection')
        orchestrator.start_agent('code_quality')
        
        events = orchestrator.get_event_history(limit=10)
        
        # Events should be in chronological order (oldest to newest)
        if len(events) > 1:
            for i in range(len(events) - 1):
                assert events[i].timestamp <= events[i + 1].timestamp
        
        # Clean up
        orchestrator.stop_all()


class TestAgentOrchestrationEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_agent_name(self):
        """Test handling of empty agent name."""
        orchestrator = AgentOrchestrator()
        
        result = orchestrator.start_agent('')
        assert result is False
    
    def test_none_agent_name(self):
        """Test handling of None agent name."""
        orchestrator = AgentOrchestrator()
        
        # Should handle gracefully
        try:
            result = orchestrator.start_agent(None)
            assert result is False
        except (TypeError, AttributeError):
            # Also acceptable to raise exception
            pass
    
    def test_rapid_start_stop(self):
        """Test rapid start/stop cycles."""
        orchestrator = AgentOrchestrator()
        
        for _ in range(5):
            orchestrator.start_agent('performance')
            orchestrator.stop_agent('performance')
        
        # Agent should end up stopped
        assert not orchestrator.agents['performance'].is_running()
    
    def test_stop_all_when_none_running(self):
        """Test stop_all when no agents are running."""
        orchestrator = AgentOrchestrator()
        
        # Should not raise errors
        orchestrator.stop_all()
        
        status = orchestrator.get_status()
        for agent_name, agent_status in status.items():
            assert agent_status['running'] is False
    
    def test_start_all_idempotent(self):
        """Test that start_all is idempotent."""
        orchestrator = AgentOrchestrator()
        
        orchestrator.start_all()
        orchestrator.start_all()  # Second call should be safe
        
        status = orchestrator.get_status()
        for agent_name, agent_status in status.items():
            assert agent_status['running'] is True
        
        # Clean up
        orchestrator.stop_all()
    
    def test_event_history_with_limit(self):
        """Test event history respects limit parameter."""
        orchestrator = AgentOrchestrator()
        
        # Generate many events
        for agent_name in ['performance', 'bug_detection', 'code_quality']:
            orchestrator.start_agent(agent_name)
            orchestrator.stop_agent(agent_name)
        
        # Request limited events
        events = orchestrator.get_event_history(limit=3)
        
        assert len(events) <= 3
    
    def test_concurrent_agent_operations(self):
        """Test concurrent operations on different agents."""
        orchestrator = AgentOrchestrator()
        
        # Start first agent
        orchestrator.start_agent('performance')
        
        # Start second agent while first is running
        orchestrator.start_agent('bug_detection')
        
        # Stop first agent while second is running
        orchestrator.stop_agent('performance')
        
        # Verify states
        assert not orchestrator.agents['performance'].is_running()
        assert orchestrator.agents['bug_detection'].is_running()
        
        # Clean up
        orchestrator.stop_agent('bug_detection')
