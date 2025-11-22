"""
Test Agent for automated testing via Remote Control API.

This module provides a specialized agent that can connect to Unreal Engine
and perform automated tests through the Remote Control API.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from .base_agent import RemoteControlAgent
from .models import RemoteControlError

logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Status of a test execution."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class TestResult:
    """
    Result of a test execution.
    
    Attributes:
        test_name: Name of the test
        status: Test execution status
        duration: Execution time in seconds
        message: Status message or error details
        timestamp: When the test was executed
        details: Additional test-specific details
    """
    
    def __init__(
        self,
        test_name: str,
        status: TestStatus,
        duration: float = 0.0,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.test_name = test_name
        self.status = status
        self.duration = duration
        self.message = message
        self.timestamp = datetime.now()
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert test result to dictionary."""
        return {
            "test_name": self.test_name,
            "status": self.status.value,
            "duration": self.duration,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }
    
    def __str__(self) -> str:
        """String representation of test result."""
        status_symbol = {
            TestStatus.PASSED: "✓",
            TestStatus.FAILED: "✗",
            TestStatus.ERROR: "⚠",
            TestStatus.SKIPPED: "○",
            TestStatus.RUNNING: "→",
            TestStatus.PENDING: "·",
        }
        symbol = status_symbol.get(self.status, "?")
        return f"{symbol} {self.test_name} ({self.duration:.2f}s): {self.message}"


class TestAgent(RemoteControlAgent):
    """
    Agent for automated testing through Unreal Engine Remote Control API.
    
    This agent can connect to the UE plugin and execute automated tests,
    including property validation, function calls, and console commands.
    
    Example:
        ```python
        from remote_control import TestAgent, TestStatus
        
        # Create test agent
        agent = TestAgent(
            agent_id="automated_tester",
            ue_host="localhost",
            ue_port=30010
        )
        
        # Start agent and run tests
        with agent:
            # Define test suite
            tests = [
                {
                    "name": "test_player_health",
                    "type": "property",
                    "object_path": "/Game/Player.Player_C",
                    "property_name": "Health",
                    "expected_value": 100.0
                },
                {
                    "name": "test_fps_command",
                    "type": "command",
                    "command": "stat fps"
                }
            ]
            
            # Execute tests
            results = agent.run_test_suite(tests)
            
            # Print results
            agent.print_test_summary(results)
        ```
    """
    
    def __init__(
        self,
        agent_id: str = "test_agent",
        ue_host: str = "localhost",
        ue_port: int = 30010,
        enable_websocket: bool = False,
        timeout: int = 30,
    ):
        """
        Initialize the test agent.
        
        Args:
            agent_id: Unique identifier for this agent
            ue_host: Unreal Engine host address
            ue_port: Remote Control API port
            enable_websocket: Whether to enable WebSocket events
            timeout: Request timeout in seconds
        """
        super().__init__(
            agent_id=agent_id,
            ue_host=ue_host,
            ue_port=ue_port,
            enable_websocket=enable_websocket,
            timeout=timeout,
        )
        
        self.test_results: List[TestResult] = []
        logger.info(f"Initialized TestAgent: {agent_id}")
    
    def execute_task(self, task: Any) -> Any:
        """
        Execute a test task.
        
        Args:
            task: Test task definition (dict with test parameters)
            
        Returns:
            TestResult object
        """
        if not isinstance(task, dict):
            return TestResult(
                test_name="unknown",
                status=TestStatus.ERROR,
                message="Invalid task format: expected dictionary"
            )
        
        test_type = task.get("type", "unknown")
        
        if test_type == "property":
            return self._test_property(task)
        elif test_type == "function":
            return self._test_function(task)
        elif test_type == "command":
            return self._test_command(task)
        else:
            return TestResult(
                test_name=task.get("name", "unknown"),
                status=TestStatus.ERROR,
                message=f"Unknown test type: {test_type}"
            )
    
    def _test_property(self, task: Dict[str, Any]) -> TestResult:
        """
        Test property value.
        
        Args:
            task: Test task with property details
            
        Returns:
            TestResult object
        """
        test_name = task.get("name", "property_test")
        object_path = task.get("object_path")
        property_name = task.get("property_name")
        expected_value = task.get("expected_value")
        
        start_time = time.time()
        
        try:
            # Get property value
            actual_value = self.get_property(object_path, property_name)
            duration = time.time() - start_time
            
            # Compare with expected value if provided
            if expected_value is not None:
                if actual_value == expected_value:
                    return TestResult(
                        test_name=test_name,
                        status=TestStatus.PASSED,
                        duration=duration,
                        message=f"Property value matches expected: {actual_value}",
                        details={
                            "object_path": object_path,
                            "property_name": property_name,
                            "expected": expected_value,
                            "actual": actual_value,
                        }
                    )
                else:
                    return TestResult(
                        test_name=test_name,
                        status=TestStatus.FAILED,
                        duration=duration,
                        message=f"Expected {expected_value}, got {actual_value}",
                        details={
                            "object_path": object_path,
                            "property_name": property_name,
                            "expected": expected_value,
                            "actual": actual_value,
                        }
                    )
            else:
                # No expected value, just verify property exists
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.PASSED,
                    duration=duration,
                    message=f"Property retrieved successfully: {actual_value}",
                    details={
                        "object_path": object_path,
                        "property_name": property_name,
                        "value": actual_value,
                    }
                )
                
        except RemoteControlError as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                duration=duration,
                message=f"Error getting property: {str(e)}",
                details={
                    "object_path": object_path,
                    "property_name": property_name,
                    "error": str(e),
                }
            )
    
    def _test_function(self, task: Dict[str, Any]) -> TestResult:
        """
        Test function call.
        
        Args:
            task: Test task with function details
            
        Returns:
            TestResult object
        """
        test_name = task.get("name", "function_test")
        object_path = task.get("object_path")
        function_name = task.get("function_name")
        parameters = task.get("parameters", {})
        expected_result = task.get("expected_result")
        
        start_time = time.time()
        
        try:
            # Call function
            result = self.call_function(object_path, function_name, parameters)
            duration = time.time() - start_time
            
            # Compare with expected result if provided
            if expected_result is not None:
                if result == expected_result:
                    return TestResult(
                        test_name=test_name,
                        status=TestStatus.PASSED,
                        duration=duration,
                        message=f"Function result matches expected: {result}",
                        details={
                            "object_path": object_path,
                            "function_name": function_name,
                            "parameters": parameters,
                            "expected": expected_result,
                            "actual": result,
                        }
                    )
                else:
                    return TestResult(
                        test_name=test_name,
                        status=TestStatus.FAILED,
                        duration=duration,
                        message=f"Expected {expected_result}, got {result}",
                        details={
                            "object_path": object_path,
                            "function_name": function_name,
                            "parameters": parameters,
                            "expected": expected_result,
                            "actual": result,
                        }
                    )
            else:
                # No expected result, just verify function executed
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.PASSED,
                    duration=duration,
                    message=f"Function executed successfully",
                    details={
                        "object_path": object_path,
                        "function_name": function_name,
                        "parameters": parameters,
                        "result": result,
                    }
                )
                
        except RemoteControlError as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                duration=duration,
                message=f"Error calling function: {str(e)}",
                details={
                    "object_path": object_path,
                    "function_name": function_name,
                    "parameters": parameters,
                    "error": str(e),
                }
            )
    
    def _test_command(self, task: Dict[str, Any]) -> TestResult:
        """
        Test console command execution.
        
        Args:
            task: Test task with command details
            
        Returns:
            TestResult object
        """
        test_name = task.get("name", "command_test")
        command = task.get("command")
        expected_output = task.get("expected_output")
        
        start_time = time.time()
        
        try:
            # Execute command
            result = self.execute_command(command)
            duration = time.time() - start_time
            
            # Check if command contains expected output
            if expected_output is not None:
                output_str = str(result)
                if expected_output in output_str:
                    return TestResult(
                        test_name=test_name,
                        status=TestStatus.PASSED,
                        duration=duration,
                        message=f"Command output contains expected string",
                        details={
                            "command": command,
                            "expected": expected_output,
                            "output": result,
                        }
                    )
                else:
                    return TestResult(
                        test_name=test_name,
                        status=TestStatus.FAILED,
                        duration=duration,
                        message=f"Expected output '{expected_output}' not found",
                        details={
                            "command": command,
                            "expected": expected_output,
                            "output": result,
                        }
                    )
            else:
                # No expected output, just verify command executed
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.PASSED,
                    duration=duration,
                    message=f"Command executed successfully",
                    details={
                        "command": command,
                        "output": result,
                    }
                )
                
        except RemoteControlError as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                duration=duration,
                message=f"Error executing command: {str(e)}",
                details={
                    "command": command,
                    "error": str(e),
                }
            )
    
    def run_test_suite(self, tests: List[Dict[str, Any]]) -> List[TestResult]:
        """
        Run a suite of tests.
        
        Args:
            tests: List of test task definitions
            
        Returns:
            List of TestResult objects
        """
        logger.info(f"Running test suite with {len(tests)} tests")
        results = []
        
        for test in tests:
            logger.info(f"Executing test: {test.get('name', 'unknown')}")
            result = self.execute_task(test)
            results.append(result)
            self.test_results.append(result)
            logger.info(str(result))
        
        return results
    
    def get_test_results(self) -> List[TestResult]:
        """
        Get all test results from this session.
        
        Returns:
            List of TestResult objects
        """
        return self.test_results
    
    def clear_test_results(self):
        """Clear all test results."""
        self.test_results.clear()
        logger.info("Test results cleared")
    
    def print_test_summary(self, results: Optional[List[TestResult]] = None):
        """
        Print a summary of test results.
        
        Args:
            results: List of TestResult objects (uses self.test_results if None)
        """
        if results is None:
            results = self.test_results
        
        if not results:
            print("No test results available")
            return
        
        # Count results by status
        status_counts = {status: 0 for status in TestStatus}
        total_duration = 0.0
        
        for result in results:
            status_counts[result.status] += 1
            total_duration += result.duration
        
        # Print summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        for result in results:
            print(str(result))
        
        print("-" * 70)
        print(f"Total Tests:  {len(results)}")
        print(f"Passed:       {status_counts[TestStatus.PASSED]}")
        print(f"Failed:       {status_counts[TestStatus.FAILED]}")
        print(f"Errors:       {status_counts[TestStatus.ERROR]}")
        print(f"Skipped:      {status_counts[TestStatus.SKIPPED]}")
        print(f"Duration:     {total_duration:.2f}s")
        print("=" * 70 + "\n")
    
    def export_test_results(
        self,
        filepath: str,
        format: str = "json"
    ) -> bool:
        """
        Export test results to a file.
        
        Args:
            filepath: Path to output file
            format: Output format ("json" or "xml")
            
        Returns:
            True if export succeeded
        """
        try:
            results_data = [result.to_dict() for result in self.test_results]
            
            if format == "json":
                with open(filepath, 'w') as f:
                    json.dump({
                        "agent_id": self.agent_id,
                        "timestamp": datetime.now().isoformat(),
                        "total_tests": len(self.test_results),
                        "results": results_data,
                    }, f, indent=2)
                logger.info(f"Test results exported to {filepath}")
                return True
            else:
                logger.error(f"Unsupported export format: {format}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to export test results: {e}")
            return False
