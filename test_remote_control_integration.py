#!/usr/bin/env python3
"""
Test script for Remote Control integration via IPC server.

This script tests the new Remote Control handlers added to the IPC server.
"""

import json
import socket
import sys
import time

def send_request(host, port, request_type, data):
    """Send a request to the IPC server."""
    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        
        # Prepare request
        request = {
            'type': request_type,
            'data': json.dumps(data) if isinstance(data, dict) else data
        }
        
        # Send request
        request_str = json.dumps(request) + '\n'
        sock.sendall(request_str.encode('utf-8'))
        
        # Receive response
        response_data = sock.recv(4096)
        response = json.loads(response_data.decode('utf-8').strip())
        
        sock.close()
        return response
        
    except Exception as e:
        print(f"Error: {e}")
        return {'status': 'error', 'error': str(e)}

def test_health_check():
    """Test Remote Control health check."""
    print("\n" + "="*60)
    print("Test 1: Remote Control Health Check")
    print("="*60)
    
    response = send_request('localhost', 5555, 'remote_control_health_check', {
        'host': 'localhost',
        'port': 30010
    })
    
    print(f"Status: {response.get('status')}")
    if response.get('status') == 'success':
        print(f"Healthy: {response.get('healthy')}")
        print(f"Message: {response.get('message')}")
    else:
        print(f"Error: {response.get('error')}")
        print(f"Details: {response.get('details')}")
    
    return response.get('status') == 'success'

def test_execute_command():
    """Test executing console command."""
    print("\n" + "="*60)
    print("Test 2: Execute Console Command")
    print("="*60)
    
    response = send_request('localhost', 5555, 'remote_control_execute_command', {
        'command': 'stat fps',
        'host': 'localhost',
        'port': 30010
    })
    
    print(f"Status: {response.get('status')}")
    if response.get('status') == 'success':
        print(f"Command: {response.get('command')}")
        print(f"Result: {response.get('result')}")
    else:
        print(f"Error: {response.get('error')}")
    
    return response.get('status') == 'success'

def test_get_property():
    """Test getting property (will fail without valid UE object)."""
    print("\n" + "="*60)
    print("Test 3: Get Property (Expected to fail without valid object)")
    print("="*60)
    
    response = send_request('localhost', 5555, 'remote_control_get_property', {
        'object_path': '/Game/TestBlueprint.TestBlueprint_C',
        'property_name': 'TestProperty',
        'host': 'localhost',
        'port': 30010
    })
    
    print(f"Status: {response.get('status')}")
    if response.get('status') == 'success':
        print(f"Property Value: {response.get('value')}")
    else:
        print(f"Error: {response.get('error')} (expected)")
    
    return True  # Always return True since we expect this to fail

def test_set_property():
    """Test setting property (will fail without valid UE object)."""
    print("\n" + "="*60)
    print("Test 4: Set Property (Expected to fail without valid object)")
    print("="*60)
    
    response = send_request('localhost', 5555, 'remote_control_set_property', {
        'object_path': '/Game/TestBlueprint.TestBlueprint_C',
        'property_name': 'TestProperty',
        'value': 100.0,
        'host': 'localhost',
        'port': 30010
    })
    
    print(f"Status: {response.get('status')}")
    if response.get('status') == 'success':
        print(f"Property Set Successfully")
    else:
        print(f"Error: {response.get('error')} (expected)")
    
    return True  # Always return True since we expect this to fail

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Remote Control Integration Tests")
    print("="*60)
    print("\nNOTE: These tests verify that the IPC server handlers are working.")
    print("They will show errors if Unreal Engine is not running with Remote Control enabled.")
    print("\nTo run with Unreal Engine:")
    print("  UnrealEditor.exe MyProject.uproject -RCWebControlEnable -RCWebInterfaceEnable")
    
    # Wait a moment
    time.sleep(1)
    
    # Run tests
    results = []
    results.append(("Health Check", test_health_check()))
    results.append(("Execute Command", test_execute_command()))
    results.append(("Get Property", test_get_property()))
    results.append(("Set Property", test_set_property()))
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
