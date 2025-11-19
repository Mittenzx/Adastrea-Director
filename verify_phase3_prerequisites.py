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
            try:
                if module == "remote_control.client":
                    if not hasattr(mod, "UnrealRemoteControlClient"):
                        print(f"  ✗ UnrealRemoteControlClient class not found")
                        results.append(False)
                    else:
                        print(f"  └─ UnrealRemoteControlClient class found")
                elif module == "remote_control.websocket_client":
                    if not hasattr(mod, "WebSocketEventClient"):
                        print(f"  ✗ WebSocketEventClient class not found")
                        results.append(False)
                    else:
                        print(f"  └─ WebSocketEventClient class found")
                elif module == "remote_control.base_agent":
                    if not hasattr(mod, "RemoteControlAgent"):
                        print(f"  ✗ RemoteControlAgent class not found")
                        results.append(False)
                    else:
                        print(f"  └─ RemoteControlAgent class found")
            except Exception as e:
                print(f"  ✗ Error checking module attributes: {e}")
                results.append(False)
    
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
        try:
            if not hasattr(mod, "EventBus"):
                print(f"  ✗ EventBus class not found")
                return False
            if not hasattr(mod, "Event"):
                print(f"  ✗ Event class not found")
                return False
            if not hasattr(mod, "EventType"):
                print(f"  ✗ EventType enum not found")
                return False
            print(f"  └─ EventBus class found")
            print(f"  └─ Event class found")
            print(f"  └─ EventType enum found")
            
            # Try to create an instance
            event_bus = mod.EventBus()
            print(f"  └─ EventBus instance created successfully")
            
            # Check key methods
            if not hasattr(event_bus, "publish"):
                print(f"  ✗ publish method not found")
                return False
            if not hasattr(event_bus, "subscribe"):
                print(f"  ✗ subscribe method not found")
                return False
            if not hasattr(event_bus, "unsubscribe"):
                print(f"  ✗ unsubscribe method not found")
                return False
            if not hasattr(event_bus, "get_history"):
                print(f"  ✗ get_history method not found")
                return False
            print(f"  └─ All key methods present")
            
        except Exception as e:
            print(f"  ✗ Failed to verify EventBus: {e}")
            return False
    
    return success


def verify_shared_state():
    """Verify Shared State Management implementation."""
    print("\n3. Shared State Management")
    print("=" * 60)
    
    success, mod = check_module("agents.phase3.shared_state", "Shared State module")
    
    if success and mod:
        # Check key classes exist
        try:
            if not hasattr(mod, "SharedContext"):
                print(f"  ✗ SharedContext class not found")
                return False
            if not hasattr(mod, "AgentState"):
                print(f"  ✗ AgentState class not found")
                return False
            if not hasattr(mod, "AgentMetrics"):
                print(f"  ✗ AgentMetrics class not found")
                return False
            if not hasattr(mod, "AgentStatus"):
                print(f"  ✗ AgentStatus enum not found")
                return False
            if not hasattr(mod, "ProjectInfo"):
                print(f"  ✗ ProjectInfo class not found")
                return False
            if not hasattr(mod, "CodeStructure"):
                print(f"  ✗ CodeStructure class not found")
                return False
            if not hasattr(mod, "Change"):
                print(f"  ✗ Change class not found")
                return False
            print(f"  └─ SharedContext class found")
            print(f"  └─ AgentState class found")
            print(f"  └─ AgentMetrics class found")
            print(f"  └─ Data model classes found")
            
            # Try to create an instance
            shared_context = mod.SharedContext()
            print(f"  └─ SharedContext instance created successfully")
            
            # Check key methods
            if not hasattr(shared_context, "register_agent"):
                print(f"  ✗ register_agent method not found")
                return False
            if not hasattr(shared_context, "get_agent_state"):
                print(f"  ✗ get_agent_state method not found")
                return False
            if not hasattr(shared_context, "set_project_info"):
                print(f"  ✗ set_project_info method not found")
                return False
            if not hasattr(shared_context, "get_project_info"):
                print(f"  ✗ get_project_info method not found")
                return False
            print(f"  └─ All key methods present")
            
        except Exception as e:
            print(f"  ✗ Failed to verify SharedContext: {e}")
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
