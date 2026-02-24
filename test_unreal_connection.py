#!/usr/bin/env python3
"""
Simple test to check if we can connect to Unreal Engine's Python Remote Execution.
"""

import socket
import json
import struct
import time
import sys

# Fix Unicode encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_unreal_connection():
    """Test connection to Unreal Engine's Python Remote Execution."""
    
    print("Testing Unreal Engine Python Remote Execution connection...")
    
    # Unreal Engine uses multicast discovery on 239.0.0.1:6766
    multicast_group = "239.0.0.1"
    multicast_port = 6766
    
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        
        # Allow multiple sockets to use the same PORT number
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind to the server address
        sock.bind(("", multicast_port))
        
        # Tell the operating system to add the socket to the multicast group
        # on all interfaces.
        group = socket.inet_aton(multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        # Set timeout
        sock.settimeout(5.0)
        
        print(f"Listening for Unreal Engine multicast announcements on {multicast_group}:{multicast_port}...")
        
        try:
            # Try to receive data
            data, address = sock.recvfrom(1024)
            print(f"Received data from {address}:")
            print(f"  Raw data: {data}")
            
            # Try to parse as JSON
            try:
                message = json.loads(data.decode('utf-8'))
                print(f"  Parsed JSON: {json.dumps(message, indent=2)}")
                print("\n[SUCCESS] Unreal Engine is broadcasting on the multicast group!")
                print(f"   Project: {message.get('project_name', 'Unknown')}")
                print(f"   Engine: {message.get('engine_version', 'Unknown')}")
                return True
            except json.JSONDecodeError:
                print(f"  Could not parse as JSON (might be binary data)")
                print("\n[WARNING] Received data but couldn't parse as JSON")
                return False
                
        except socket.timeout:
            print("\n[FAILED] No Unreal Engine multicast announcements received within 5 seconds.")
            print("   Possible reasons:")
            print("   1. Unreal Engine is not running")
            print("   2. Python Remote Execution is not enabled")
            print("   3. Firewall is blocking multicast traffic")
            print("   4. Unreal Engine is using a different multicast address/port")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False
    finally:
        try:
            sock.close()
        except:
            pass

def test_direct_connection():
    """Test direct connection to Unreal Engine's command endpoint."""
    
    print("\n\nTesting direct connection to Unreal Engine command endpoint...")
    
    # Unreal Engine's command endpoint is typically on 127.0.0.1:6776
    command_host = "127.0.0.1"
    command_port = 6776
    
    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        
        print(f"Attempting to connect to {command_host}:{command_port}...")
        sock.connect((command_host, command_port))
        
        print(f"[SUCCESS] Connected to Unreal Engine command endpoint!")
        
        # Send a simple ping message
        ping_message = json.dumps({
            "type": "ping",
            "id": "test_ping"
        })
        
        # Send message length first (4 bytes, big-endian)
        message_len = len(ping_message)
        sock.send(struct.pack('>I', message_len))
        
        # Send the message
        sock.send(ping_message.encode('utf-8'))
        
        print("Sent ping message, waiting for response...")
        
        # Try to receive response
        try:
            # Read response length
            response_len_bytes = sock.recv(4)
            if len(response_len_bytes) == 4:
                response_len = struct.unpack('>I', response_len_bytes)[0]
                print(f"Response length: {response_len} bytes")
                
                # Read response data
                response_data = sock.recv(response_len)
                if response_data:
                    try:
                        response = json.loads(response_data.decode('utf-8'))
                        print(f"Response: {json.dumps(response, indent=2)}")
                    except:
                        print(f"Raw response: {response_data}")
            else:
                print("No response received")
                
        except socket.timeout:
            print("No response received (timeout)")
            
        sock.close()
        return True
        
    except ConnectionRefusedError:
        print(f"[FAILED] Connection refused. Unreal Engine command endpoint is not listening.")
        return False
    except socket.timeout:
        print(f"[FAILED] Connection timeout.")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Unreal Engine Python Remote Execution Test")
    print("=" * 60)
    
    # Test multicast discovery
    multicast_success = test_unreal_connection()
    
    # Test direct connection
    direct_success = test_direct_connection()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    
    if multicast_success:
        print("[SUCCESS] Multicast discovery: SUCCESS")
    else:
        print("[FAILED] Multicast discovery: FAILED")
        
    if direct_success:
        print("[SUCCESS] Direct connection: SUCCESS")
    else:
        print("[FAILED] Direct connection: FAILED")
    
    print("\nRecommendations:")
    if not multicast_success and not direct_success:
        print("1. Ensure Unreal Engine is running")
        print("2. Enable Python Editor Script Plugin in Unreal Engine")
        print("3. Enable Remote Execution in Project Settings -> Python")
        print("4. Check firewall settings for multicast traffic")
    elif multicast_success and not direct_success:
        print("1. Unreal Engine is discoverable but command endpoint not accessible")
        print("2. Check if another application is using port 6776")
        print("3. Try restarting Unreal Engine")
    else:
        print("[SUCCESS] Both connections successful! MCP server should work.")
    
    print("=" * 60)