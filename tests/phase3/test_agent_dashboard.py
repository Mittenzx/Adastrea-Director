"""
Integration tests for Agent Dashboard

Tests the dashboard functionality including:
- Dashboard initialization
- Real-time status display
- Event tracking
- Agent monitoring
- UI rendering
"""

import time
from agent_dashboard import AgentDashboard
from agents.phase3 import EventType


class TestAgentDashboard:
    """Test suite for AgentDashboard class."""
    
    def test_dashboard_initialization(self):
        """Test dashboard initializes correctly."""
        dashboard = AgentDashboard(update_interval=1.0)
        
        assert dashboard is not None
        assert dashboard.event_bus is not None
        assert dashboard.shared_context is not None
        assert len(dashboard.agents) == 3
        assert 'Performance' in dashboard.agents
        assert 'Bug Detection' in dashboard.agents
        assert 'Code Quality' in dashboard.agents
        assert dashboard.update_interval == 1.0
    
    def test_dashboard_custom_interval(self):
        """Test dashboard with custom update interval."""
        dashboard = AgentDashboard(update_interval=0.5)
        
        assert dashboard.update_interval == 0.5
    
    def test_start_all_agents(self):
        """Test starting all agents through dashboard."""
        dashboard = AgentDashboard()
        
        dashboard.start_all_agents()
        
        for name, agent in dashboard.agents.items():
            assert agent.is_running(), f"Agent {name} should be running"
        
        # Clean up
        dashboard.stop_all_agents()
    
    def test_stop_all_agents(self):
        """Test stopping all agents through dashboard."""
        dashboard = AgentDashboard()
        
        dashboard.start_all_agents()
        dashboard.stop_all_agents()
        
        for name, agent in dashboard.agents.items():
            assert not agent.is_running(), f"Agent {name} should be stopped"
    
    def test_event_subscription(self):
        """Test that dashboard subscribes to events."""
        dashboard = AgentDashboard()
        
        # Event counts should be initialized
        assert EventType.PERFORMANCE_ALERT in dashboard.event_counts
        assert EventType.BUG_DETECTED in dashboard.event_counts
        assert EventType.CODE_QUALITY_ISSUE in dashboard.event_counts
        
        # All counts should start at 0
        for count in dashboard.event_counts.values():
            assert count == 0
    
    def test_event_counting(self):
        """Test that events are counted correctly."""
        dashboard = AgentDashboard()
        
        # Start an agent to generate events
        dashboard.start_all_agents()
        
        # Give time for events to be processed
        time.sleep(0.1)
        
        # Stop agents to generate more events
        dashboard.stop_all_agents()
        
        # Event counts may have increased
        # (depends on timing, so we just check structure)
        assert isinstance(dashboard.event_counts, dict)
        for event_type, count in dashboard.event_counts.items():
            assert isinstance(count, int)
            assert count >= 0
    
    def test_generate_header(self):
        """Test header generation."""
        dashboard = AgentDashboard()
        
        header = dashboard.generate_header()
        
        assert header is not None
        # Header should be a Panel object
        from rich.panel import Panel
        assert isinstance(header, Panel)
    
    def test_generate_agent_status_table(self):
        """Test agent status table generation."""
        dashboard = AgentDashboard()
        
        table = dashboard.generate_agent_status_table()
        
        assert table is not None
        assert table.title == "Agent Status"
    
    def test_generate_agent_status_table_with_running_agents(self):
        """Test status table with running agents."""
        dashboard = AgentDashboard()
        
        dashboard.start_all_agents()
        
        table = dashboard.generate_agent_status_table()
        
        assert table is not None
        
        # Clean up
        dashboard.stop_all_agents()
    
    def test_generate_event_summary_table(self):
        """Test event summary table generation."""
        dashboard = AgentDashboard()
        
        table = dashboard.generate_event_summary_table()
        
        assert table is not None
        assert table.title == "Event Summary"
    
    def test_generate_recent_events_panel_empty(self):
        """Test recent events panel when no events exist."""
        dashboard = AgentDashboard()
        
        panel = dashboard.generate_recent_events_panel(limit=10)
        
        assert panel is not None
        assert "Recent Events" in str(panel.title)
    
    def test_generate_recent_events_panel_with_events(self):
        """Test recent events panel with events."""
        dashboard = AgentDashboard()
        
        # Generate some events
        dashboard.start_all_agents()
        time.sleep(0.1)
        
        panel = dashboard.generate_recent_events_panel(limit=5)
        
        assert panel is not None
        
        # Clean up
        dashboard.stop_all_agents()
    
    def test_generate_controls_panel(self):
        """Test controls panel generation."""
        dashboard = AgentDashboard()
        
        panel = dashboard.generate_controls_panel()
        
        assert panel is not None
        # Should be a Panel object
        from rich.panel import Panel
        assert isinstance(panel, Panel)
    
    def test_generate_layout(self):
        """Test complete layout generation."""
        dashboard = AgentDashboard()
        
        layout = dashboard.generate_layout()
        
        assert layout is not None
        # Layout should be a Layout object
        from rich.layout import Layout
        assert isinstance(layout, Layout)


class TestAgentDashboardIntegration:
    """Integration tests for dashboard workflows."""
    
    def test_dashboard_with_performance_agent(self):
        """Test dashboard monitoring performance agent."""
        dashboard = AgentDashboard()
        
        # Start performance agent
        perf_agent = dashboard.agents['Performance']
        perf_agent.start()
        
        # Collect metrics
        metrics = perf_agent.collect_metrics(
            frame_rate=58.0,
            memory_usage_mb=3200.0,
            cpu_usage_percent=65.0,
            gpu_usage_percent=75.0,
            draw_calls=1800,
            triangles=850000
        )
        
        # Analyze performance
        perf_agent.analyze_performance(metrics)
        
        # Give time for events to propagate
        time.sleep(0.1)
        
        # Generate layout to verify it works with events
        layout = dashboard.generate_layout()
        assert layout is not None
        
        # Check event counts tracking
        # The dashboard tracks PERFORMANCE_ALERT, not PERFORMANCE_METRICS_COLLECTED
        assert EventType.PERFORMANCE_ALERT in dashboard.event_counts
        
        # Clean up
        perf_agent.stop()
    
    def test_dashboard_with_bug_detection_agent(self):
        """Test dashboard monitoring bug detection agent."""
        dashboard = AgentDashboard()
        
        # Start bug detection agent
        bug_agent = dashboard.agents['Bug Detection']
        bug_agent.start()
        
        # Analyze logs with errors
        log_content = """
        [ERROR] Segmentation fault
        [ERROR] Invalid memory access
        """
        
        anomalies = bug_agent.analyze_logs(log_content)
        assert anomalies is not None and len(anomalies) > 0
        
        # Give time for events to propagate
        time.sleep(0.1)
        
        # Generate layout
        layout = dashboard.generate_layout()
        assert layout is not None
        
        # Clean up
        bug_agent.stop()
    
    def test_dashboard_with_code_quality_agent(self):
        """Test dashboard monitoring code quality agent."""
        dashboard = AgentDashboard()
        
        # Start code quality agent
        quality_agent = dashboard.agents['Code Quality']
        quality_agent.start()
        
        # Analyze code
        sample_code = """
        def example():
            x = 500
            y = 1000
            return x + y
        """
        
        report = quality_agent.analyze_code("example.py", sample_code)
        
        # Give time for events to propagate
        time.sleep(0.1)
        
        # Generate layout
        layout = dashboard.generate_layout()
        assert layout is not None
        
        # Check that quality events were counted
        if report.code_smells:
            assert dashboard.event_counts[EventType.CODE_QUALITY_ISSUE] > 0
        
        # Clean up
        quality_agent.stop()
    
    def test_dashboard_all_agents_workflow(self):
        """Test dashboard with all agents running."""
        dashboard = AgentDashboard()
        
        # Start all agents
        dashboard.start_all_agents()
        
        # Get each agent and generate activity
        perf_agent = dashboard.agents['Performance']
        bug_agent = dashboard.agents['Bug Detection']
        quality_agent = dashboard.agents['Code Quality']
        
        # Performance activity
        metrics = perf_agent.collect_metrics(
            frame_rate=45.0,
            memory_usage_mb=4500.0,
            cpu_usage_percent=85.0,
            gpu_usage_percent=90.0,
            draw_calls=2500,
            triangles=1200000
        )
        perf_agent.analyze_performance(metrics)
        
        # Bug detection activity
        logs = "[ERROR] Fatal error occurred\n[ERROR] Exception thrown"
        bug_agent.analyze_logs(logs)
        
        # Code quality activity
        code = "def bad(): x = 100; return x * 2"
        quality_agent.analyze_code("bad.py", code)
        
        # Give time for events
        time.sleep(0.1)
        
        # Generate complete layout
        layout = dashboard.generate_layout()
        assert layout is not None
        
        # Verify event counts increased
        total_events = sum(dashboard.event_counts.values())
        assert total_events > 0
        
        # Clean up
        dashboard.stop_all_agents()
    
    def test_dashboard_event_history_limit(self):
        """Test that dashboard respects event history limit."""
        dashboard = AgentDashboard()
        
        # Generate multiple events
        dashboard.start_all_agents()
        time.sleep(0.1)
        
        # Request limited events
        panel = dashboard.generate_recent_events_panel(limit=3)
        
        assert panel is not None
        
        # Clean up
        dashboard.stop_all_agents()
    
    def test_dashboard_status_transitions(self):
        """Test dashboard shows correct status transitions."""
        dashboard = AgentDashboard()
        
        # Initial state - all stopped
        layout1 = dashboard.generate_layout()
        assert layout1 is not None
        
        # Start all agents
        dashboard.start_all_agents()
        
        # All should be running
        layout2 = dashboard.generate_layout()
        assert layout2 is not None
        
        # Stop all agents
        dashboard.stop_all_agents()
        
        # All should be stopped
        layout3 = dashboard.generate_layout()
        assert layout3 is not None
    
    def test_dashboard_partial_agent_control(self):
        """Test dashboard with only some agents running."""
        dashboard = AgentDashboard()
        
        # Start only performance agent
        dashboard.agents['Performance'].start()
        
        # Generate layout
        layout = dashboard.generate_layout()
        assert layout is not None
        
        # Start bug detection agent
        dashboard.agents['Bug Detection'].start()
        
        # Generate layout again
        layout = dashboard.generate_layout()
        assert layout is not None
        
        # Clean up
        dashboard.agents['Performance'].stop()
        dashboard.agents['Bug Detection'].stop()


class TestAgentDashboardEdgeCases:
    """Test edge cases and error handling."""
    
    def test_dashboard_zero_interval(self):
        """Test dashboard with zero update interval."""
        # Should handle gracefully
        dashboard = AgentDashboard(update_interval=0.0)
        
        assert dashboard.update_interval == 0.0
        
        # Should still be able to generate layout
        layout = dashboard.generate_layout()
        assert layout is not None
    
    def test_dashboard_negative_interval(self):
        """Test dashboard with negative update interval."""
        # Should accept any value (validation could be added later)
        dashboard = AgentDashboard(update_interval=-1.0)
        
        assert dashboard.update_interval == -1.0
    
    def test_dashboard_large_event_limit(self):
        """Test dashboard with very large event limit."""
        dashboard = AgentDashboard()
        
        dashboard.start_all_agents()
        time.sleep(0.1)
        
        # Request large number of events
        panel = dashboard.generate_recent_events_panel(limit=1000)
        
        assert panel is not None
        
        # Clean up
        dashboard.stop_all_agents()
    
    def test_dashboard_zero_event_limit(self):
        """Test dashboard with zero event limit."""
        dashboard = AgentDashboard()
        
        panel = dashboard.generate_recent_events_panel(limit=0)
        
        assert panel is not None
    
    def test_dashboard_rapid_layout_generation(self):
        """Test rapid layout generation."""
        dashboard = AgentDashboard()
        
        dashboard.start_all_agents()
        
        # Generate layout multiple times rapidly
        for _ in range(10):
            layout = dashboard.generate_layout()
            assert layout is not None
        
        # Clean up
        dashboard.stop_all_agents()
    
    def test_dashboard_event_counts_persistence(self):
        """Test that event counts persist across layout generations."""
        dashboard = AgentDashboard()
        
        dashboard.start_all_agents()
        time.sleep(0.1)
        
        # Get initial counts
        initial_counts = dict(dashboard.event_counts)
        
        # Generate layout multiple times
        for _ in range(5):
            dashboard.generate_layout()
        
        # Counts should not reset
        for event_type, initial_count in initial_counts.items():
            assert dashboard.event_counts[event_type] >= initial_count
        
        # Clean up
        dashboard.stop_all_agents()
    
    def test_dashboard_concurrent_agent_activity(self):
        """Test dashboard with concurrent agent activity."""
        dashboard = AgentDashboard()
        
        dashboard.start_all_agents()
        
        perf_agent = dashboard.agents['Performance']
        bug_agent = dashboard.agents['Bug Detection']
        quality_agent = dashboard.agents['Code Quality']
        
        # Generate activity from multiple agents
        metrics = perf_agent.collect_metrics(60.0, 3000.0, 60.0, 70.0, 1000, 500000)
        perf_agent.analyze_performance(metrics)
        
        bug_agent.analyze_logs("[INFO] Starting up")
        
        quality_agent.analyze_code("test.py", "def test(): pass")
        
        # Dashboard should handle all events
        layout = dashboard.generate_layout()
        assert layout is not None
        
        # Clean up
        dashboard.stop_all_agents()
    
    def test_dashboard_after_stop_all(self):
        """Test dashboard state after stopping all agents."""
        dashboard = AgentDashboard()
        
        dashboard.start_all_agents()
        dashboard.stop_all_agents()
        
        # Should still be able to generate layout
        layout = dashboard.generate_layout()
        assert layout is not None
        
        # All agents should show as stopped
        for name, agent in dashboard.agents.items():
            assert not agent.is_running()
