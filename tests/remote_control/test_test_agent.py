"""
Tests for TestAgent.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from datetime import datetime

from remote_control.test_agent import TestAgent, TestResult, TestStatus
from remote_control.models import RemoteControlError


class TestTestResult:
    """Test suite for TestResult class."""
    
    def test_result_initialization(self):
        """Test TestResult is initialized correctly."""
        result = TestResult(
            test_name="test_example",
            status=TestStatus.PASSED,
            duration=1.5,
            message="Test passed",
            details={"key": "value"}
        )
        
        assert result.test_name == "test_example"
        assert result.status == TestStatus.PASSED
        assert result.duration == 1.5
        assert result.message == "Test passed"
        assert result.details == {"key": "value"}
        assert isinstance(result.timestamp, datetime)
    
    def test_result_to_dict(self):
        """Test converting TestResult to dictionary."""
        result = TestResult(
            test_name="test_example",
            status=TestStatus.PASSED,
            duration=1.5,
            message="Test passed"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["test_name"] == "test_example"
        assert result_dict["status"] == "passed"
        assert result_dict["duration"] == 1.5
        assert result_dict["message"] == "Test passed"
        assert "timestamp" in result_dict
        assert "details" in result_dict
    
    def test_result_str_passed(self):
        """Test string representation of passed test."""
        result = TestResult(
            test_name="test_example",
            status=TestStatus.PASSED,
            duration=1.5,
            message="Test passed"
        )
        
        result_str = str(result)
        
        assert "✓" in result_str
        assert "test_example" in result_str
        assert "1.50s" in result_str
        assert "Test passed" in result_str
    
    def test_result_str_failed(self):
        """Test string representation of failed test."""
        result = TestResult(
            test_name="test_example",
            status=TestStatus.FAILED,
            duration=0.5,
            message="Assertion failed"
        )
        
        result_str = str(result)
        
        assert "✗" in result_str
        assert "test_example" in result_str


class TestTestAgent:
    """Test suite for TestAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        with patch('remote_control.base_agent.UnrealRemoteControlClient'):
            agent = TestAgent(
                agent_id="test_agent",
                ue_host="localhost",
                ue_port=30010,
            )
            return agent
    
    def test_agent_initialization(self, agent):
        """Test agent is initialized correctly."""
        assert agent.agent_id == "test_agent"
        assert agent.ue_host == "localhost"
        assert agent.ue_port == 30010
        assert agent.test_results == []
    
    def test_execute_task_invalid_format(self, agent):
        """Test execute_task with invalid task format."""
        result = agent.execute_task("invalid_task")
        
        assert result.test_name == "unknown"
        assert result.status == TestStatus.ERROR
        assert "Invalid task format" in result.message
    
    def test_execute_task_unknown_type(self, agent):
        """Test execute_task with unknown test type."""
        task = {
            "name": "test_unknown",
            "type": "unknown_type"
        }
        
        result = agent.execute_task(task)
        
        assert result.test_name == "test_unknown"
        assert result.status == TestStatus.ERROR
        assert "Unknown test type" in result.message
    
    def test_execute_task_property(self, agent):
        """Test execute_task with property test."""
        task = {
            "name": "test_health",
            "type": "property",
            "object_path": "/Game/Player.Player_C",
            "property_name": "Health",
            "expected_value": 100.0
        }
        
        # Mock get_property
        agent.get_property = Mock(return_value=100.0)
        
        result = agent.execute_task(task)
        
        assert result.test_name == "test_health"
        assert result.status == TestStatus.PASSED
        assert "matches expected" in result.message
        agent.get_property.assert_called_once_with(
            "/Game/Player.Player_C", "Health"
        )
    
    def test_execute_task_function(self, agent):
        """Test execute_task with function test."""
        task = {
            "name": "test_damage",
            "type": "function",
            "object_path": "/Game/Player.Player_C",
            "function_name": "TakeDamage",
            "parameters": {"Amount": 10.0}
        }
        
        # Mock call_function
        agent.call_function = Mock(return_value={"success": True})
        
        result = agent.execute_task(task)
        
        assert result.test_name == "test_damage"
        assert result.status == TestStatus.PASSED
        agent.call_function.assert_called_once()
    
    def test_execute_task_command(self, agent):
        """Test execute_task with command test."""
        task = {
            "name": "test_fps",
            "type": "command",
            "command": "stat fps"
        }
        
        # Mock execute_command
        agent.execute_command = Mock(return_value={"output": "FPS: 60"})
        
        result = agent.execute_task(task)
        
        assert result.test_name == "test_fps"
        assert result.status == TestStatus.PASSED
        agent.execute_command.assert_called_once_with("stat fps")
    
    def test_test_property_success(self, agent):
        """Test property test passes."""
        task = {
            "name": "test_property",
            "object_path": "/Game/Test",
            "property_name": "Value",
            "expected_value": 42
        }
        
        agent.get_property = Mock(return_value=42)
        
        result = agent._test_property(task)
        
        assert result.status == TestStatus.PASSED
        assert result.details["expected"] == 42
        assert result.details["actual"] == 42
    
    def test_test_property_failure(self, agent):
        """Test property test fails when values don't match."""
        task = {
            "name": "test_property",
            "object_path": "/Game/Test",
            "property_name": "Value",
            "expected_value": 42
        }
        
        agent.get_property = Mock(return_value=100)
        
        result = agent._test_property(task)
        
        assert result.status == TestStatus.FAILED
        assert "Expected 42, got 100" in result.message
    
    def test_test_property_no_expected_value(self, agent):
        """Test property test passes when no expected value provided."""
        task = {
            "name": "test_property",
            "object_path": "/Game/Test",
            "property_name": "Value"
        }
        
        agent.get_property = Mock(return_value=42)
        
        result = agent._test_property(task)
        
        assert result.status == TestStatus.PASSED
        assert "retrieved successfully" in result.message
    
    def test_test_property_error(self, agent):
        """Test property test handles errors."""
        task = {
            "name": "test_property",
            "object_path": "/Game/Test",
            "property_name": "Value"
        }
        
        agent.get_property = Mock(side_effect=RemoteControlError("Property not found"))
        
        result = agent._test_property(task)
        
        assert result.status == TestStatus.ERROR
        assert "Error getting property" in result.message
    
    def test_test_property_missing_fields(self, agent):
        """Test property test handles missing required fields."""
        task = {
            "name": "test_property",
            "object_path": None,
            "property_name": "Value"
        }
        
        result = agent._test_property(task)
        
        assert result.status == TestStatus.ERROR
        assert "Missing required fields" in result.message
    
    def test_test_property_unexpected_error(self, agent):
        """Test property test handles unexpected exceptions."""
        task = {
            "name": "test_property",
            "object_path": "/Game/Test",
            "property_name": "Value"
        }
        
        agent.get_property = Mock(side_effect=TypeError("Unexpected error"))
        
        result = agent._test_property(task)
        
        assert result.status == TestStatus.ERROR
        assert "Unexpected error" in result.message
        assert result.details.get("error_type") == "TypeError"
    
    def test_test_function_success(self, agent):
        """Test function test passes."""
        task = {
            "name": "test_function",
            "object_path": "/Game/Test",
            "function_name": "DoSomething",
            "parameters": {"input": 10},
            "expected_result": {"output": 20}
        }
        
        agent.call_function = Mock(return_value={"output": 20})
        
        result = agent._test_function(task)
        
        assert result.status == TestStatus.PASSED
        assert result.details["expected"] == {"output": 20}
    
    def test_test_function_failure(self, agent):
        """Test function test fails when results don't match."""
        task = {
            "name": "test_function",
            "object_path": "/Game/Test",
            "function_name": "DoSomething",
            "expected_result": {"output": 20}
        }
        
        agent.call_function = Mock(return_value={"output": 30})
        
        result = agent._test_function(task)
        
        assert result.status == TestStatus.FAILED
    
    def test_test_function_no_expected_result(self, agent):
        """Test function test passes when no expected result provided."""
        task = {
            "name": "test_function",
            "object_path": "/Game/Test",
            "function_name": "DoSomething"
        }
        
        agent.call_function = Mock(return_value={"success": True})
        
        result = agent._test_function(task)
        
        assert result.status == TestStatus.PASSED
    
    def test_test_function_error(self, agent):
        """Test function test handles errors."""
        task = {
            "name": "test_function",
            "object_path": "/Game/Test",
            "function_name": "DoSomething"
        }
        
        agent.call_function = Mock(side_effect=RemoteControlError("Function not found"))
        
        result = agent._test_function(task)
        
        assert result.status == TestStatus.ERROR
    
    def test_test_function_missing_fields(self, agent):
        """Test function test handles missing required fields."""
        task = {
            "name": "test_function",
            "object_path": "/Game/Test",
            "function_name": None
        }
        
        result = agent._test_function(task)
        
        assert result.status == TestStatus.ERROR
        assert "Missing required fields" in result.message
    
    def test_test_function_unexpected_error(self, agent):
        """Test function test handles unexpected exceptions."""
        task = {
            "name": "test_function",
            "object_path": "/Game/Test",
            "function_name": "DoSomething"
        }
        
        agent.call_function = Mock(side_effect=AttributeError("Unexpected error"))
        
        result = agent._test_function(task)
        
        assert result.status == TestStatus.ERROR
        assert "Unexpected error" in result.message
        assert result.details.get("error_type") == "AttributeError"
    
    def test_test_command_success(self, agent):
        """Test command test passes."""
        task = {
            "name": "test_command",
            "command": "stat fps",
            "expected_output": "FPS"
        }
        
        agent.execute_command = Mock(return_value={"output": "FPS: 60"})
        
        result = agent._test_command(task)
        
        assert result.status == TestStatus.PASSED
    
    def test_test_command_failure(self, agent):
        """Test command test fails when expected output not found."""
        task = {
            "name": "test_command",
            "command": "stat fps",
            "expected_output": "GPU"
        }
        
        agent.execute_command = Mock(return_value={"output": "FPS: 60"})
        
        result = agent._test_command(task)
        
        assert result.status == TestStatus.FAILED
        assert "not found" in result.message
    
    def test_test_command_no_expected_output(self, agent):
        """Test command test passes when no expected output provided."""
        task = {
            "name": "test_command",
            "command": "stat fps"
        }
        
        agent.execute_command = Mock(return_value={"output": "FPS: 60"})
        
        result = agent._test_command(task)
        
        assert result.status == TestStatus.PASSED
    
    def test_test_command_error(self, agent):
        """Test command test handles errors."""
        task = {
            "name": "test_command",
            "command": "invalid command"
        }
        
        agent.execute_command = Mock(side_effect=RemoteControlError("Command failed"))
        
        result = agent._test_command(task)
        
        assert result.status == TestStatus.ERROR
    
    def test_test_command_missing_field(self, agent):
        """Test command test handles missing required field."""
        task = {
            "name": "test_command",
            "command": None
        }
        
        result = agent._test_command(task)
        
        assert result.status == TestStatus.ERROR
        assert "Missing required field" in result.message
    
    def test_test_command_unexpected_error(self, agent):
        """Test command test handles unexpected exceptions."""
        task = {
            "name": "test_command",
            "command": "stat fps"
        }
        
        agent.execute_command = Mock(side_effect=ValueError("Unexpected error"))
        
        result = agent._test_command(task)
        
        assert result.status == TestStatus.ERROR
        assert "Unexpected error" in result.message
        assert result.details.get("exception_type") == "ValueError"
    
    def test_run_test_suite(self, agent):
        """Test running a suite of tests."""
        tests = [
            {
                "name": "test1",
                "type": "property",
                "object_path": "/Game/Test",
                "property_name": "Value"
            },
            {
                "name": "test2",
                "type": "command",
                "command": "stat fps"
            }
        ]
        
        agent.get_property = Mock(return_value=42)
        agent.execute_command = Mock(return_value={"output": "FPS: 60"})
        
        results = agent.run_test_suite(tests)
        
        assert len(results) == 2
        assert all(isinstance(r, TestResult) for r in results)
        assert len(agent.test_results) == 2
    
    def test_get_test_results(self, agent):
        """Test getting test results."""
        # Add some test results
        agent.test_results = [
            TestResult("test1", TestStatus.PASSED),
            TestResult("test2", TestStatus.FAILED)
        ]
        
        results = agent.get_test_results()
        
        assert len(results) == 2
        assert results[0].test_name == "test1"
        assert results[1].test_name == "test2"
    
    def test_clear_test_results(self, agent):
        """Test clearing test results."""
        agent.test_results = [
            TestResult("test1", TestStatus.PASSED),
            TestResult("test2", TestStatus.FAILED)
        ]
        
        agent.clear_test_results()
        
        assert len(agent.test_results) == 0
    
    def test_print_test_summary_no_results(self, agent, capsys):
        """Test printing summary with no results."""
        agent.print_test_summary()
        
        captured = capsys.readouterr()
        assert "No test results available" in captured.out
    
    def test_print_test_summary_with_results(self, agent, capsys):
        """Test printing summary with results."""
        agent.test_results = [
            TestResult("test1", TestStatus.PASSED, duration=1.0),
            TestResult("test2", TestStatus.FAILED, duration=0.5),
            TestResult("test3", TestStatus.ERROR, duration=0.2)
        ]
        
        agent.print_test_summary()
        
        captured = capsys.readouterr()
        assert "TEST SUMMARY" in captured.out
        assert "Total Tests:  3" in captured.out
        assert "Passed:       1" in captured.out
        assert "Failed:       1" in captured.out
        assert "Errors:       1" in captured.out
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_export_test_results_json(self, mock_json_dump, mock_file, agent):
        """Test exporting test results to JSON."""
        agent.test_results = [
            TestResult("test1", TestStatus.PASSED),
            TestResult("test2", TestStatus.FAILED)
        ]
        
        result = agent.export_test_results("/tmp/results.json", format="json")
        
        assert result is True
        mock_file.assert_called_once_with("/tmp/results.json", 'w', encoding='utf-8')
        mock_json_dump.assert_called_once()
    
    def test_export_test_results_unsupported_format(self, agent):
        """Test exporting with unsupported format."""
        agent.test_results = [TestResult("test1", TestStatus.PASSED)]
        
        result = agent.export_test_results("/tmp/results.xml", format="xml")
        
        assert result is False
