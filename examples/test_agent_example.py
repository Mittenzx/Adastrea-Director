"""
Example: Using TestAgent for automated UE testing.

This example demonstrates how to use the TestAgent to perform
automated testing of an Unreal Engine project via Remote Control API.

Requirements:
1. Unreal Engine running with Remote Control API enabled
2. Launch UE with: -RCWebControlEnable -RCWebInterfaceEnable
3. Remote Control API available at http://localhost:30010

Usage:
    python examples/test_agent_example.py
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from remote_control import TestAgent, TestStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_basic_test():
    """Example: Basic test agent usage."""
    print("\n" + "=" * 70)
    print("Example 1: Basic Test Agent Usage")
    print("=" * 70 + "\n")
    
    # Create test agent
    agent = TestAgent(
        agent_id="basic_test_agent",
        ue_host="localhost",
        ue_port=30010
    )
    
    try:
        # Start agent (connects to UE)
        print("Starting test agent...")
        agent.start()
        print("✓ Connected to Unreal Engine\n")
        
        # Run a simple command test
        print("Running command test...")
        result = agent.execute_task({
            "name": "test_fps_command",
            "type": "command",
            "command": "stat fps"
        })
        print(f"Result: {result}\n")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Stop agent
        agent.stop()
        print("Test agent stopped\n")


def example_test_suite():
    """Example: Running a test suite."""
    print("\n" + "=" * 70)
    print("Example 2: Test Suite Execution")
    print("=" * 70 + "\n")
    
    # Define test suite
    tests = [
        # Test 1: Console command
        {
            "name": "test_fps_display",
            "type": "command",
            "command": "stat fps",
            "expected_output": None  # Just verify it executes
        },
        
        # Test 2: Property read (example - adjust paths for your project)
        {
            "name": "test_player_health",
            "type": "property",
            "object_path": "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter",
            "property_name": "MaxWalkSpeed",
            # "expected_value": 600.0  # Uncomment to validate specific value
        },
        
        # Test 3: Another command test
        {
            "name": "test_memory_stats",
            "type": "command",
            "command": "stat memory"
        },
    ]
    
    # Create and use test agent
    with TestAgent(agent_id="suite_test_agent") as agent:
        print("Running test suite...")
        print(f"Total tests: {len(tests)}\n")
        
        # Run all tests
        results = agent.run_test_suite(tests)
        
        # Print summary
        print()
        agent.print_test_summary(results)
        
        # Export results
        output_file = "/tmp/test_results.json"
        if agent.export_test_results(output_file):
            print(f"✓ Results exported to: {output_file}")


def example_property_validation():
    """Example: Property validation testing."""
    print("\n" + "=" * 70)
    print("Example 3: Property Validation")
    print("=" * 70 + "\n")
    
    with TestAgent(agent_id="property_validator") as agent:
        # Test property exists and has expected value
        test = {
            "name": "validate_character_speed",
            "type": "property",
            "object_path": "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter",
            "property_name": "MaxWalkSpeed",
            "expected_value": 600.0  # Default UE character speed
        }
        
        print("Validating character property...")
        result = agent.execute_task(test)
        
        print(f"\nResult: {result}")
        print(f"Status: {result.status.value}")
        print(f"Message: {result.message}")
        
        if result.status == TestStatus.PASSED:
            print("\n✓ Property validation passed!")
        else:
            print("\n✗ Property validation failed!")
            if result.details:
                print(f"Details: {result.details}")


def example_function_testing():
    """Example: Function call testing."""
    print("\n" + "=" * 70)
    print("Example 4: Function Call Testing")
    print("=" * 70 + "\n")
    
    with TestAgent(agent_id="function_tester") as agent:
        # Test function call (example - adjust for your project)
        test = {
            "name": "test_actor_function",
            "type": "function",
            "object_path": "/Game/MyActor.MyActor_C",
            "function_name": "GetHealth",
            "parameters": {},
            # "expected_result": {"health": 100.0}  # Uncomment to validate result
        }
        
        print("Testing actor function...")
        result = agent.execute_task(test)
        
        print(f"\nResult: {result}")


def example_continuous_testing():
    """Example: Continuous testing with multiple iterations."""
    print("\n" + "=" * 70)
    print("Example 5: Continuous Testing")
    print("=" * 70 + "\n")
    
    import time
    
    with TestAgent(agent_id="continuous_tester") as agent:
        iterations = 3
        
        for i in range(iterations):
            print(f"\n--- Iteration {i + 1}/{iterations} ---")
            
            # Simple health check test
            test = {
                "name": f"iteration_{i+1}_health_check",
                "type": "command",
                "command": "stat fps"
            }
            
            result = agent.execute_task(test)
            print(f"Status: {result.status.value} - {result.message}")
            
            # Wait between iterations
            if i < iterations - 1:
                time.sleep(2)
        
        print("\n" + "=" * 70)
        print("All iterations complete!")
        agent.print_test_summary()


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("UNREAL ENGINE TEST AGENT EXAMPLES")
    print("=" * 70)
    
    print("\nNOTE: These examples require Unreal Engine to be running with")
    print("Remote Control API enabled. Launch UE with:")
    print("  -RCWebControlEnable -RCWebInterfaceEnable")
    print("\nPress Ctrl+C to exit at any time.")
    
    try:
        # Example 1: Basic usage
        example_basic_test()
        
        # Example 2: Test suite
        example_test_suite()
        
        # Example 3: Property validation
        # Uncomment if you have a valid object path
        # example_property_validation()
        
        # Example 4: Function testing
        # Uncomment if you have a valid function to test
        # example_function_testing()
        
        # Example 5: Continuous testing
        # example_continuous_testing()
        
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
    
    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
