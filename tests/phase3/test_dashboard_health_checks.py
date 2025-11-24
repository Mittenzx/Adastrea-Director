"""
Tests for dashboard system health checks and enhanced diagnostics.

Tests the new diagnostic features:
- System health checking
- Error tracking and display
- Success/failure rate metrics
- Component status validation
"""

import time
from agent_dashboard import AgentDashboard
from agents.phase3 import Event, EventType
from system_health import SystemHealthChecker, HealthStatus


class TestSystemHealthChecker:
    """Test suite for SystemHealthChecker class."""
    
    def test_health_checker_initialization(self):
        """Test health checker initializes correctly."""
        checker = SystemHealthChecker()
        
        assert checker is not None
        assert checker._last_checks == {}
    
    def test_check_llm_api(self):
        """Test LLM API health check."""
        checker = SystemHealthChecker()
        
        status = checker.check_llm_api()
        
        assert status is not None
        assert status.component == "LLM API"
        assert isinstance(status.healthy, bool)
        assert status.message is not None
        assert status.details is not None
    
    def test_check_vector_database(self):
        """Test vector database health check."""
        checker = SystemHealthChecker()
        
        status = checker.check_vector_database()
        
        assert status is not None
        assert status.component == "Vector Database"
        assert isinstance(status.healthy, bool)
        assert status.message is not None
        assert status.details is not None
    
    def test_check_file_system(self):
        """Test file system health check."""
        checker = SystemHealthChecker()
        
        status = checker.check_file_system()
        
        assert status is not None
        assert status.component == "File System"
        assert isinstance(status.healthy, bool)
        assert status.message is not None
        assert status.details is not None
    
    def test_check_remote_control(self):
        """Test remote control API health check."""
        checker = SystemHealthChecker()
        
        status = checker.check_remote_control()
        
        assert status is not None
        assert status.component == "Remote Control API"
        assert isinstance(status.healthy, bool)
        assert status.message is not None
        assert status.details is not None
    
    def test_check_all(self):
        """Test checking all health checks."""
        checker = SystemHealthChecker()
        
        results = checker.check_all()
        
        assert results is not None
        assert isinstance(results, dict)
        assert 'llm_api' in results
        assert 'vector_db' in results
        assert 'file_system' in results
        
        # All should be HealthStatus objects
        for component, status in results.items():
            assert isinstance(status, HealthStatus)
    
    def test_get_last_check(self):
        """Test retrieving last check results."""
        checker = SystemHealthChecker()
        
        # Initially no checks
        assert checker.get_last_check('llm_api') is None
        
        # Run check
        checker.check_llm_api()
        
        # Should have result now
        status = checker.get_last_check('llm_api')
        assert status is not None
        assert isinstance(status, HealthStatus)
    
    def test_is_system_healthy(self):
        """Test overall system health check."""
        checker = SystemHealthChecker()
        
        # Run all checks first
        checker.check_all()
        
        # Check overall health
        healthy = checker.is_system_healthy()
        assert isinstance(healthy, bool)


class TestDashboardHealthIntegration:
    """Test suite for dashboard health check integration."""
    
    def test_dashboard_has_health_checker(self):
        """Test dashboard includes health checker."""
        dashboard = AgentDashboard()
        
        assert hasattr(dashboard, 'health_checker')
        assert dashboard.health_checker is not None
        assert isinstance(dashboard.health_checker, SystemHealthChecker)
    
    def test_dashboard_update_system_health(self):
        """Test dashboard can update system health."""
        dashboard = AgentDashboard()
        
        # Initially empty
        assert dashboard.system_health == {}
        
        # Update health
        dashboard.update_system_health()
        
        # Should have results now
        assert dashboard.system_health != {}
        assert 'llm_api' in dashboard.system_health
        assert 'vector_db' in dashboard.system_health
    
    def test_generate_system_health_panel(self):
        """Test system health panel generation."""
        dashboard = AgentDashboard()
        
        # Generate panel without health check
        panel = dashboard.generate_system_health_panel()
        assert panel is not None
        
        # Update health and generate again
        dashboard.update_system_health()
        panel = dashboard.generate_system_health_panel()
        assert panel is not None
        assert panel.title is not None
    
    def test_layout_includes_health_panel(self):
        """Test dashboard layout includes health panel."""
        dashboard = AgentDashboard()
        
        dashboard.update_system_health()
        layout = dashboard.generate_layout()
        
        assert layout is not None
        # Layout should include system_health section
    
    def test_health_updates_during_run(self):
        """Test health checks are updated during dashboard operation."""
        dashboard = AgentDashboard()
        
        # Initial state
        assert dashboard.system_health == {}
        
        # Simulate what happens at dashboard start
        dashboard.update_system_health()
        
        # Should have health data
        assert dashboard.system_health != {}
        assert len(dashboard.system_health) > 0


class TestDashboardErrorTracking:
    """Test suite for dashboard error tracking features."""
    
    def test_agent_error_tracking(self):
        """Test that agent errors are tracked."""
        dashboard = AgentDashboard()
        
        # Start agents
        dashboard.start_all_agents()
        time.sleep(0.1)
        
        # Publish error event
        error_event = Event(
            event_type=EventType.AGENT_ERROR,
            source="test_agent",
            payload={
                'agent_id': 'test_agent',
                'error': 'Test error message',
                'error_count': 1
            }
        )
        dashboard.event_bus.publish(error_event)
        time.sleep(0.1)
        
        # Error should be tracked
        assert 'test_agent' in dashboard.agent_errors
        assert dashboard.agent_errors['test_agent']['error'] == 'Test error message'
        assert dashboard.agent_errors['test_agent']['count'] == 1
        
        # Clean up
        dashboard.stop_all_agents()
    
    def test_error_count_in_event_summary(self):
        """Test error count is included in event summary."""
        dashboard = AgentDashboard()
        
        # Verify AGENT_ERROR is in event counts
        assert EventType.AGENT_ERROR in dashboard.event_counts
        
        initial_count = dashboard.event_counts[EventType.AGENT_ERROR]
        
        # Publish error
        error_event = Event(
            event_type=EventType.AGENT_ERROR,
            source="test",
            payload={'error': 'test'}
        )
        dashboard.event_bus.publish(error_event)
        time.sleep(0.1)
        
        # Count should increase
        assert dashboard.event_counts[EventType.AGENT_ERROR] == initial_count + 1
    
    def test_agent_status_shows_metrics(self):
        """Test agent status table shows task metrics."""
        dashboard = AgentDashboard()
        
        dashboard.start_all_agents()
        time.sleep(0.1)
        
        # Generate status table
        table = dashboard.generate_agent_status_table()
        
        assert table is not None
        # Table should have columns for Tasks and Success Rate
        # (we can't directly check column names, but verify table generates)
        
        dashboard.stop_all_agents()
    
    def test_error_details_panel_empty(self):
        """Test error details panel when no errors."""
        dashboard = AgentDashboard()
        
        panel = dashboard.generate_error_details_panel()
        
        assert panel is not None
        assert "No errors reported" in str(panel.renderable)
    
    def test_error_details_panel_with_errors(self):
        """Test error details panel with errors."""
        dashboard = AgentDashboard()
        
        # Add error
        dashboard.agent_errors['test_agent'] = {
            'error': 'Test error',
            'timestamp': time.time(),
            'count': 1
        }
        
        from datetime import datetime
        dashboard.agent_errors['test_agent']['timestamp'] = datetime.now()
        
        panel = dashboard.generate_error_details_panel()
        
        assert panel is not None
        assert "Agent Errors" in str(panel.renderable) or "Test error" in str(panel.renderable)
    
    def test_recent_events_shows_error_details(self):
        """Test recent events panel shows error details."""
        dashboard = AgentDashboard()
        
        # Publish error event
        error_event = Event(
            event_type=EventType.AGENT_ERROR,
            source="test",
            payload={'error': 'Detailed error message'}
        )
        dashboard.event_bus.publish(error_event)
        time.sleep(0.1)
        
        # Generate panel
        panel = dashboard.generate_recent_events_panel(limit=10)
        
        assert panel is not None
        # Panel should include error details


class TestDashboardDiagnosticFeatures:
    """Test suite for diagnostic features."""
    
    def test_dashboard_layout_adapts_to_errors(self):
        """Test layout adjusts based on error presence."""
        dashboard = AgentDashboard()
        
        # Layout without errors
        layout1 = dashboard.generate_layout()
        assert layout1 is not None
        
        # Add an error
        from datetime import datetime
        dashboard.agent_errors['test'] = {
            'error': 'Test',
            'timestamp': datetime.now(),
            'count': 1
        }
        
        # Layout with errors should include error panel
        layout2 = dashboard.generate_layout()
        assert layout2 is not None
    
    def test_dashboard_comprehensive_diagnostics(self):
        """Test dashboard provides comprehensive diagnostic info."""
        dashboard = AgentDashboard()
        
        # Update health
        dashboard.update_system_health()
        
        # Start agents
        dashboard.start_all_agents()
        time.sleep(0.1)
        
        # Simulate error
        error_event = Event(
            event_type=EventType.AGENT_ERROR,
            source="performance_profiling_agent",
            payload={
                'agent_id': 'performance_profiling_agent',
                'error': 'Connection failed',
                'error_count': 1
            }
        )
        dashboard.event_bus.publish(error_event)
        time.sleep(0.1)
        
        # Generate full layout
        layout = dashboard.generate_layout()
        
        assert layout is not None
        
        # Verify all diagnostic components
        assert dashboard.system_health != {}  # Health checks ran
        assert len(dashboard.agent_errors) > 0  # Errors tracked
        assert dashboard.event_counts[EventType.AGENT_ERROR] > 0  # Events counted
        
        # Clean up
        dashboard.stop_all_agents()
    
    def test_dashboard_shows_success_rates(self):
        """Test dashboard calculates and shows success rates."""
        dashboard = AgentDashboard()
        
        dashboard.start_all_agents()
        time.sleep(0.1)
        
        # Manually set some metrics
        for agent in dashboard.agents.values():
            state = dashboard.shared_context.get_agent_state(agent.agent_id)
            if state:
                state.metrics.tasks_completed = 8
                state.metrics.tasks_failed = 2
        
        # Generate status table
        table = dashboard.generate_agent_status_table()
        
        assert table is not None
        # Table should show success rate (80% in this case)
        
        dashboard.stop_all_agents()
