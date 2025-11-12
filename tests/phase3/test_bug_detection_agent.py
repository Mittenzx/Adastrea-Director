"""
Tests for the Bug Detection Agent.
"""

import pytest
from datetime import datetime
from agents.phase3.event_bus import EventBus, EventType
from agents.phase3.shared_state import SharedContext, AgentStatus
from agents.phase3.bug_detection_agent import (
    BugDetectionAgent,
    Anomaly,
    Crash,
    TestResults,
    BugReport
)


class TestBugDetectionAgent:
    """Tests for BugDetectionAgent class."""
    
    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        event_bus = EventBus()
        shared_context = SharedContext()
        agent = BugDetectionAgent(
            event_bus=event_bus,
            shared_context=shared_context
        )
        return agent, event_bus, shared_context
    
    def test_agent_initialization(self, setup):
        """Test agent initialization."""
        agent, event_bus, shared_context = setup
        
        assert agent.agent_id == "bug_detection_agent"
        assert not agent.is_running()
        assert len(agent.get_detected_bugs()) == 0
        assert len(agent.get_crash_history()) == 0
    
    def test_agent_start_stop(self, setup):
        """Test starting and stopping the agent."""
        agent, event_bus, shared_context = setup
        
        agent.start()
        assert agent.is_running()
        assert agent.get_status() == AgentStatus.BUSY
        
        agent.stop()
        assert not agent.is_running()
        assert agent.get_status() == AgentStatus.STOPPED
    
    def test_analyze_logs_with_errors(self, setup):
        """Test log analysis with error patterns."""
        agent, event_bus, shared_context = setup
        
        log_content = """
[INFO] Application started
[ERROR] Null pointer exception in module X
[WARNING] Memory usage high
[ERROR] Access violation at address 0x123
"""
        
        anomalies = agent.analyze_logs(log_content)
        
        # Should detect null pointer and access violation
        assert len(anomalies) > 0
        assert any("null pointer" in a.description.lower() for a in anomalies)
        assert any("access violation" in a.description.lower() for a in anomalies)
    
    def test_analyze_logs_with_warnings(self, setup):
        """Test log analysis with warnings."""
        agent, event_bus, shared_context = setup
        
        log_content = """
[INFO] Starting process
[WARNING:] Resource usage high
[WARNING:] Deprecated function called
"""
        
        anomalies = agent.analyze_logs(log_content)
        
        # Should detect warnings (at least some)
        assert len(anomalies) > 0
        warning_anomalies = [a for a in anomalies if a.anomaly_type == "warning"]
        assert len(warning_anomalies) >= 1
    
    def test_analyze_logs_clean(self, setup):
        """Test log analysis with clean logs."""
        agent, event_bus, shared_context = setup
        
        log_content = """
[INFO] Application started successfully
[INFO] All systems operational
[INFO] Processing complete
"""
        
        anomalies = agent.analyze_logs(log_content)
        
        # Should detect no anomalies in clean logs
        assert len(anomalies) == 0
    
    def test_detect_crashes(self, setup):
        """Test crash detection."""
        agent, event_bus, shared_context = setup
        
        # Track crash events
        crashes = []
        event_bus.subscribe(EventType.CRASH_DETECTED, lambda e: crashes.append(e))
        
        stack_trace = """
at PlayerController::Update() [PlayerController.cpp:123]
at GameLoop::Tick() [GameLoop.cpp:45]
"""
        error_message = "NullReferenceException"
        
        crash = agent.detect_crashes(stack_trace, error_message)
        
        assert crash.error_message == error_message
        assert crash.stack_trace == stack_trace
        assert crash.crash_id.startswith("crash_")
        
        # Event should be published
        assert len(crashes) == 1
    
    def test_run_automated_tests(self, setup):
        """Test running automated tests."""
        agent, event_bus, shared_context = setup
        
        # Track test events
        test_events = []
        event_bus.subscribe(EventType.TEST_COMPLETED, lambda e: test_events.append(e))
        event_bus.subscribe(EventType.TEST_FAILED, lambda e: test_events.append(e))
        
        # Run tests with some failures
        results = agent.run_automated_tests(
            test_suite="unit_tests",
            test_count=10,
            passed=8,
            failed=2
        )
        
        assert results.total_tests == 10
        assert results.passed == 8
        assert results.failed == 2
        assert results.success_rate() == 80.0
        
        # Event should be published (TEST_FAILED because there were failures)
        assert len(test_events) == 1
        assert test_events[0].event_type == EventType.TEST_FAILED
    
    def test_run_automated_tests_all_pass(self, setup):
        """Test running tests with all passing."""
        agent, event_bus, shared_context = setup
        
        test_events = []
        event_bus.subscribe(EventType.TEST_COMPLETED, lambda e: test_events.append(e))
        
        results = agent.run_automated_tests(
            test_suite="integration_tests",
            test_count=5,
            passed=5,
            failed=0
        )
        
        assert results.success_rate() == 100.0
        assert len(test_events) == 1
        assert test_events[0].event_type == EventType.TEST_COMPLETED
    
    def test_create_bug_report(self, setup):
        """Test creating a bug report."""
        agent, event_bus, shared_context = setup
        
        # Track bug events
        bugs = []
        event_bus.subscribe(EventType.BUG_DETECTED, lambda e: bugs.append(e))
        
        bug_report = agent.create_bug_report(
            title="Player spawn crash",
            description="Game crashes when spawning player",
            severity="high",
            reproduction_steps=["Step 1", "Step 2", "Step 3"],
            expected_behavior="Player spawns correctly",
            actual_behavior="Game crashes"
        )
        
        assert bug_report.title == "Player spawn crash"
        assert bug_report.severity == "high"
        assert len(bug_report.reproduction_steps) == 3
        assert bug_report.bug_id.startswith("bug_")
        
        # Event should be published
        assert len(bugs) == 1
        
        # Bug should be in detected bugs list
        detected = agent.get_detected_bugs()
        assert len(detected) == 1
        assert detected[0] == bug_report
    
    def test_get_detected_bugs_filtered(self, setup):
        """Test getting detected bugs filtered by severity."""
        agent, event_bus, shared_context = setup
        
        # Create bugs with different severities
        agent.create_bug_report(
            title="Bug 1",
            description="Test",
            severity="high",
            reproduction_steps=[],
            expected_behavior="",
            actual_behavior=""
        )
        
        agent.create_bug_report(
            title="Bug 2",
            description="Test",
            severity="low",
            reproduction_steps=[],
            expected_behavior="",
            actual_behavior=""
        )
        
        agent.create_bug_report(
            title="Bug 3",
            description="Test",
            severity="high",
            reproduction_steps=[],
            expected_behavior="",
            actual_behavior=""
        )
        
        # Get all bugs
        all_bugs = agent.get_detected_bugs()
        assert len(all_bugs) == 3
        
        # Get only high severity
        high_bugs = agent.get_detected_bugs(severity="high")
        assert len(high_bugs) == 2
        
        # Get only low severity
        low_bugs = agent.get_detected_bugs(severity="low")
        assert len(low_bugs) == 1
    
    def test_crash_history(self, setup):
        """Test crash history tracking."""
        agent, event_bus, shared_context = setup
        
        # Detect multiple crashes
        agent.detect_crashes("stack trace 1", "error 1")
        agent.detect_crashes("stack trace 2", "error 2")
        agent.detect_crashes("stack trace 3", "error 3")
        
        history = agent.get_crash_history()
        assert len(history) == 3
        assert all(isinstance(c, Crash) for c in history)
    
    def test_test_history(self, setup):
        """Test test history tracking."""
        agent, event_bus, shared_context = setup
        
        # Run multiple test suites
        agent.run_automated_tests("suite1", 10, 10, 0)
        agent.run_automated_tests("suite2", 5, 4, 1)
        agent.run_automated_tests("suite3", 8, 7, 1)
        
        history = agent.get_test_history()
        assert len(history) == 3
        assert all(isinstance(r, TestResults) for r in history)
