"""
Verification script for Phase 3 Prerequisites.

This script verifies that all four Phase 3 prerequisites are properly
implemented and accessible.

Usage:
    python verify_phase3_prerequisites.py
"""

import sys
import importlib
from pathlib import Path


def check_module(module_name, description):
    """Check if a module can be imported."""
    try:
        mod = importlib.import_module(module_name)
        print(f"✓ {description}: {module_name}")
        return True, mod
    except ImportError as e:
        print(f"✗ {description}: {module_name} - {e}")
        return False, None


def verify_remote_control_api():
    """Verify Unreal Engine Remote Control API setup."""
    print("\n1. Unreal Engine Remote Control API Setup")
    print("=" * 60)
    
    checks = [
        ("remote_control", "Remote Control module"),
        ("remote_control.client", "HTTP/REST Client"),
        ("remote_control.websocket_client", "WebSocket Client"),
        ("remote_control.base_agent", "Base Agent Class"),
        ("remote_control.models", "Data Models"),
    ]
    
    results = []
    for module, desc in checks:
        success, mod = check_module(module, desc)
        results.append(success)
        
        # Check key classes/functions exist
        if success and mod:
            if module == "remote_control.client":
                assert hasattr(mod, "UnrealRemoteControlClient")
                print(f"  └─ UnrealRemoteControlClient class found")
            elif module == "remote_control.websocket_client":
                assert hasattr(mod, "WebSocketEventClient")
                print(f"  └─ WebSocketEventClient class found")
            elif module == "remote_control.base_agent":
                assert hasattr(mod, "RemoteControlAgent")
                print(f"  └─ RemoteControlAgent class found")
    
    # Check config file exists
    config_path = Path("config/remote_control_config.yaml")
    if config_path.exists():
        print(f"✓ Configuration file: {config_path}")
        results.append(True)
    else:
        print(f"✗ Configuration file not found: {config_path}")
        results.append(False)
    
    # Check README exists
    readme_path = Path("remote_control/README.md")
    if readme_path.exists():
        print(f"✓ Documentation: {readme_path}")
        results.append(True)
    else:
        print(f"✗ Documentation not found: {readme_path}")
        results.append(False)
    
    return all(results)


def verify_event_bus():
    """Verify Event Bus implementation."""
    print("\n2. Event Bus Implementation")
    print("=" * 60)
    
    success, mod = check_module("agents.phase3.event_bus", "Event Bus module")
    
    if success and mod:
        # Check key classes exist
        assert hasattr(mod, "EventBus")
        assert hasattr(mod, "Event")
        assert hasattr(mod, "EventType")
        print(f"  └─ EventBus class found")
        print(f"  └─ Event class found")
        print(f"  └─ EventType enum found")
        
        # Try to create an instance
        try:
            event_bus = mod.EventBus()
            print(f"  └─ EventBus instance created successfully")
            
            # Check key methods
            assert hasattr(event_bus, "publish")
            assert hasattr(event_bus, "subscribe")
            assert hasattr(event_bus, "unsubscribe")
            assert hasattr(event_bus, "get_history")
            print(f"  └─ All key methods present")
            
        except Exception as e:
            print(f"  ✗ Failed to create EventBus instance: {e}")
            return False
    
    return success


def verify_shared_state():
    """Verify Shared State Management implementation."""
    print("\n3. Shared State Management")
    print("=" * 60)
    
    success, mod = check_module("agents.phase3.shared_state", "Shared State module")
    
    if success and mod:
        # Check key classes exist
        assert hasattr(mod, "SharedContext")
        assert hasattr(mod, "AgentState")
        assert hasattr(mod, "AgentMetrics")
        assert hasattr(mod, "AgentStatus")
        assert hasattr(mod, "ProjectInfo")
        assert hasattr(mod, "CodeStructure")
        assert hasattr(mod, "Change")
        print(f"  └─ SharedContext class found")
        print(f"  └─ AgentState class found")
        print(f"  └─ AgentMetrics class found")
        print(f"  └─ Data model classes found")
        
        # Try to create an instance
        try:
            shared_context = mod.SharedContext()
            print(f"  └─ SharedContext instance created successfully")
            
            # Check key methods
            assert hasattr(shared_context, "register_agent")
            assert hasattr(shared_context, "get_agent_state")
            assert hasattr(shared_context, "set_project_info")
            assert hasattr(shared_context, "get_project_info")
            print(f"  └─ All key methods present")
            
        except Exception as e:
            print(f"  ✗ Failed to create SharedContext instance: {e}")
            return False
    
    return success


def verify_mcp_integration():
    """Verify Unreal MCP Server integration documentation."""
    print("\n4. Unreal MCP Server Integration")
    print("=" * 60)
    
    assessment_path = Path("docs/guides/UNREAL_MCP_ASSESSMENT.md")
    if assessment_path.exists():
        print(f"✓ MCP Assessment documentation: {assessment_path}")
        print(f"  └─ Decision: Use direct Remote Control API")
        print(f"  └─ Status: Architecture decision documented")
        return True
    else:
        print(f"✗ MCP Assessment not found: {assessment_path}")
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("Phase 3 Prerequisites Verification")
    print("=" * 60)
    
    results = {
        "Remote Control API": verify_remote_control_api(),
        "Event Bus": verify_event_bus(),
        "Shared State": verify_shared_state(),
        "MCP Integration": verify_mcp_integration(),
    }
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All Phase 3 prerequisites verified successfully!")
        print("Phase 3 is ready to proceed with agent implementation.")
        return 0
    else:
        print("✗ Some prerequisites failed verification.")
        print("Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
