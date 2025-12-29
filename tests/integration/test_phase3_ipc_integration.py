"""
Integration tests for Phase 3 agent IPC integration.

Tests the IPC server integration with Phase 3 autonomous agents
(Performance Profiling, Bug Detection, Code Quality).
"""

import pytest
import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "Plugins" / "AdastreaDirector" / "Python"))

from Plugins.AdastreaDirector.Python.ipc_integration import IntegratedIPCServer


class TestPhase3IPCIntegration:
    """Test Phase 3 agent integration with IPC server."""
    
    @pytest.fixture
    def ipc_server(self):
        """Create an IPC server with Phase 3 agents enabled."""
        server = IntegratedIPCServer(
            host='127.0.0.1',
            port=5556,  # Use different port to avoid conflicts
            enable_rag=False,
            enable_planning=False,
            enable_phase3_agents=True
        )
        yield server
        # Cleanup: stop any running agents
        if server.performance_agent:
            if server.performance_agent.is_running():
                server.performance_agent.stop()
        if server.bug_detection_agent:
            if server.bug_detection_agent.is_running():
                server.bug_detection_agent.stop()
        if server.code_quality_agent:
            if server.code_quality_agent.is_running():
                server.code_quality_agent.stop()
    
    def test_phase3_agents_initialized(self, ipc_server):
        """Test that Phase 3 agents are properly initialized."""
        assert ipc_server.enable_phase3_agents is True
        assert ipc_server.event_bus is not None
        assert ipc_server.shared_context is not None
        assert ipc_server.performance_agent is not None
        assert ipc_server.bug_detection_agent is not None
        assert ipc_server.code_quality_agent is not None
    
    def test_agent_start_handler(self, ipc_server):
        """Test starting agents via IPC handler."""
        # Start performance agent
        response = ipc_server._handle_agent_start(json.dumps({'agent_id': 'performance'}))
        
        assert response['status'] == 'success'
        assert ipc_server.performance_agent.is_running()
        
        # Stop for cleanup
        ipc_server.performance_agent.stop()
    
    def test_agent_stop_handler(self, ipc_server):
        """Test stopping agents via IPC handler."""
        # Start then stop
        ipc_server.performance_agent.start()
        assert ipc_server.performance_agent.is_running()
        
        response = ipc_server._handle_agent_stop(json.dumps({'agent_id': 'performance'}))
        
        assert response['status'] == 'success'
        assert not ipc_server.performance_agent.is_running()
    
    def test_agent_status_handler(self, ipc_server):
        """Test getting agent status via IPC handler."""
        response = ipc_server._handle_agent_status('')
        
        assert response['status'] == 'success'
        assert 'agents' in response
        assert 'performance' in response['agents']
        assert 'bug_detection' in response['agents']
        assert 'code_quality' in response['agents']
        
        # Check structure
        perf_status = response['agents']['performance']
        assert 'running' in perf_status
        assert 'status' in perf_status
        assert 'metrics' in perf_status
    
    def test_collect_metrics_handler_manual(self, ipc_server):
        """Test collecting performance metrics via IPC handler (manual mode)."""
        metrics_data = {
            'frame_rate': 60.0,
            'memory_usage_mb': 2048.0,
            'cpu_usage_percent': 45.0,
            'gpu_usage_percent': 70.0,
            'draw_calls': 1500,
            'triangles': 500000
        }
        
        response = ipc_server._handle_collect_metrics(json.dumps(metrics_data))
        
        assert response['status'] == 'success'
        assert 'metrics' in response
        assert response['metrics']['frame_rate'] == 60.0
        assert response['metrics']['memory_usage_mb'] == 2048.0
    
    def test_analyze_logs_handler(self, ipc_server):
        """Test log analysis via IPC handler."""
        log_content = """
        [2025-12-29 10:00:00] Info: Application started
        [2025-12-29 10:00:05] Warning: Memory usage high
        [2025-12-29 10:00:10] Error: Null pointer exception in function XYZ
        [2025-12-29 10:00:15] Error: Access violation at address 0x12345678
        """
        
        response = ipc_server._handle_analyze_logs(log_content)
        
        assert response['status'] == 'success'
        assert 'anomalies' in response
        assert len(response['anomalies']) > 0
        
        # Check that errors were detected
        error_anomalies = [a for a in response['anomalies'] if a['type'] == 'error']
        assert len(error_anomalies) > 0
    
    def test_run_tests_handler(self, ipc_server):
        """Test running automated tests via IPC handler."""
        test_params = {
            'test_suite': 'unit_tests',
            'test_count': 50,
            'passed': 48,
            'failed': 2
        }
        
        response = ipc_server._handle_run_tests(json.dumps(test_params))
        
        assert response['status'] == 'success'
        assert 'results' in response
        assert response['results']['total_tests'] == 50
        assert response['results']['passed'] == 48
        assert response['results']['failed'] == 2
        assert response['results']['success_rate'] == 96.0
    
    def test_get_bugs_handler(self, ipc_server):
        """Test getting detected bugs via IPC handler."""
        # Create a test bug first
        ipc_server.bug_detection_agent.create_bug_report(
            title="Test Bug",
            description="This is a test bug",
            severity="high",
            reproduction_steps=["Step 1", "Step 2"],
            expected_behavior="Should work correctly",
            actual_behavior="Crashes"
        )
        
        response = ipc_server._handle_get_bugs('')
        
        assert response['status'] == 'success'
        assert 'bugs' in response
        assert len(response['bugs']) > 0
        assert response['bugs'][0]['title'] == "Test Bug"
    
    def test_analyze_code_quality_handler(self, ipc_server):
        """Test code quality analysis via IPC handler."""
        code_content = """
def long_function_with_many_lines():
    # This function is intentionally long
    x = 1
    y = 2
    z = 3
    result = x + y + z
    # More code here...
    for i in range(1000):
        result += i
    return result

def function_with_magic_numbers():
    threshold = 12345  # Magic number
    limit = 99999  # Another magic number
    return threshold + limit
"""
        
        code_params = {
            'file_path': 'test.py',
            'code_content': code_content
        }
        
        response = ipc_server._handle_analyze_code_quality(json.dumps(code_params))
        
        assert response['status'] == 'success'
        assert 'report' in response
        assert response['report']['file_path'] == 'test.py'
        assert response['report']['lines_of_code'] > 0
        assert 'overall_score' in response['report']
    
    def test_get_technical_debt_handler(self, ipc_server):
        """Test getting technical debt via IPC handler."""
        # Analyze some code first to generate debt
        code_content = """
def bad_function():
    x = 12345  # Magic number
    if x > 10000:
        # Commented code: print(x)
        pass
"""
        ipc_server.code_quality_agent.analyze_code('bad_code.py', code_content)
        
        response = ipc_server._handle_get_technical_debt('')
        
        assert response['status'] == 'success'
        assert 'debt' in response
        assert 'total_debt_hours' in response['debt']
        assert 'debt_ratio' in response['debt']
        assert 'code_smells_count' in response['debt']
        assert 'violations_count' in response['debt']
    
    def test_agent_lifecycle_all(self, ipc_server):
        """Test starting and stopping all agents at once."""
        # Start all agents
        start_response = ipc_server._handle_agent_start(json.dumps({'agent_id': 'all'}))
        assert start_response['status'] == 'success'
        
        # Check all are running
        assert ipc_server.performance_agent.is_running()
        assert ipc_server.bug_detection_agent.is_running()
        assert ipc_server.code_quality_agent.is_running()
        
        # Stop all agents
        stop_response = ipc_server._handle_agent_stop(json.dumps({'agent_id': 'all'}))
        assert stop_response['status'] == 'success'
        
        # Check all are stopped
        assert not ipc_server.performance_agent.is_running()
        assert not ipc_server.bug_detection_agent.is_running()
        assert not ipc_server.code_quality_agent.is_running()


class TestIPCServerWithoutPhase3:
    """Test IPC server initialization without Phase 3 agents."""
    
    def test_server_without_phase3_agents(self):
        """Test that server works without Phase 3 agents enabled."""
        server = IntegratedIPCServer(
            host='127.0.0.1',
            port=5557,
            enable_rag=False,
            enable_planning=False,
            enable_phase3_agents=False
        )
        
        assert server.enable_phase3_agents is False
        assert server.performance_agent is None
        assert server.bug_detection_agent is None
        assert server.code_quality_agent is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
