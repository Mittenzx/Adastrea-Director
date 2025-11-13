"""
Demonstration of Unreal Engine Remote Control API integration.

This example shows how to use the Remote Control client to interact with
Unreal Engine projects in real-time.

Requirements:
    1. Unreal Engine 5.6+ running with Remote Control API enabled
    2. Remote Control plugin enabled in Unreal Engine
    3. Remote Control Web Interface plugin enabled
    4. Unreal Engine launched with: -RCWebControlEnable -RCWebInterfaceEnable

Usage:
    python examples/remote_control_demo.py
"""

import time
import logging
from remote_control import (
    UnrealRemoteControlClient,
    WebSocketEventClient,
    EventType,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def basic_client_demo():
    """Demonstrate basic HTTP client operations."""
    logger.info("=== Basic Remote Control Client Demo ===")
    
    # Create client
    client = UnrealRemoteControlClient(
        host="localhost",
        port=30010,
        timeout=30,
    )
    
    # Check connection
    logger.info("Checking connection to Unreal Engine...")
    if not client.health_check():
        logger.error("Failed to connect to Unreal Engine")
        logger.error("Please ensure:")
        logger.error("  1. Unreal Engine is running")
        logger.error("  2. Remote Control API is enabled")
        logger.error("  3. Port 30010 is accessible")
        return
    
    logger.info("✓ Connection successful!")
    
    try:
        # Example 1: Execute console command
        logger.info("\n--- Example 1: Execute Console Command ---")
        response = client.execute_command("stat fps")
        if response.success:
            logger.info(f"✓ Executed 'stat fps' command")
            logger.info(f"Response: {response.data}")
        else:
            logger.error(f"✗ Failed to execute command: {response.error}")
        
        # Example 2: List available presets
        logger.info("\n--- Example 2: List Remote Control Presets ---")
        response = client.list_presets()
        if response.success:
            presets = response.data.get('presets', [])
            logger.info(f"✓ Found {len(presets)} preset(s)")
            for preset in presets:
                logger.info(f"  - {preset}")
        else:
            logger.info("No presets found (this is normal for first run)")
        
        # Example 3: Get property (requires valid object path)
        logger.info("\n--- Example 3: Get Property ---")
        logger.info("Note: This example requires a valid object in your Unreal project")
        logger.info("Skipping property get/set demo (would require specific game objects)")
        
        # Example 4: More console commands
        logger.info("\n--- Example 4: Additional Console Commands ---")
        commands = [
            "stat unit",
            "stat gpu", 
            "stat memory",
        ]
        
        for cmd in commands:
            response = client.execute_command(cmd)
            if response.success:
                logger.info(f"✓ Executed '{cmd}'")
            else:
                logger.info(f"✗ Failed to execute '{cmd}'")
                
    finally:
        client.close()
        logger.info("\n✓ Client closed")


def websocket_demo():
    """Demonstrate WebSocket event client."""
    logger.info("\n=== WebSocket Event Client Demo ===")
    
    # Event handlers
    def on_property_changed(event):
        """Handle property change events."""
        logger.info(f"Property changed: {event}")
    
    def on_connection_status(event):
        """Handle connection status events."""
        status = event.get('status', 'unknown')
        logger.info(f"Connection status: {status}")
    
    def on_error(event):
        """Handle error events."""
        logger.error(f"WebSocket error: {event.get('message', 'Unknown error')}")
    
    # Create WebSocket client
    ws_client = WebSocketEventClient(
        host="localhost",
        port=30010,
        reconnect_attempts=3,
    )
    
    # Add event handlers
    ws_client.add_event_handler(EventType.PROPERTY_CHANGED, on_property_changed)
    ws_client.add_event_handler(EventType.CONNECTION_STATUS, on_connection_status)
    ws_client.add_event_handler(EventType.ERROR, on_error)
    
    try:
        # Connect
        logger.info("Connecting to Unreal Engine WebSocket...")
        ws_client.connect()
        logger.info("✓ WebSocket connected! Listening for events...")
        
        # Listen for events for 10 seconds
        logger.info("Listening for events (10 seconds)...")
        logger.info("(Make changes in Unreal Engine to see events)")
        time.sleep(10)
        
    except Exception as e:
        logger.error(f"WebSocket demo failed: {e}")
        logger.error("Note: WebSocket requires Unreal Engine to be running")
    finally:
        ws_client.disconnect()
        logger.info("✓ WebSocket disconnected")


def context_manager_demo():
    """Demonstrate using clients as context managers."""
    logger.info("\n=== Context Manager Demo ===")
    
    # Using HTTP client as context manager
    with UnrealRemoteControlClient() as client:
        if client.health_check():
            logger.info("✓ Connected via context manager")
            response = client.execute_command("stat fps")
            if response.success:
                logger.info("✓ Command executed successfully")
    
    logger.info("✓ Client automatically closed")


def practical_example():
    """Practical example: Performance monitoring."""
    logger.info("\n=== Practical Example: Performance Monitoring ===")
    
    with UnrealRemoteControlClient() as client:
        if not client.health_check():
            logger.error("Cannot connect to Unreal Engine")
            return
        
        logger.info("Monitoring performance metrics...")
        
        # Collect metrics
        metrics = []
        commands = ["stat fps", "stat unit", "stat memory"]
        
        for cmd in commands:
            response = client.execute_command(cmd)
            if response.success:
                metrics.append({
                    'command': cmd,
                    'output': response.data
                })
        
        # Display results
        logger.info("\n--- Performance Metrics ---")
        for metric in metrics:
            logger.info(f"{metric['command']}: Enabled")
        
        logger.info("\nMetrics are now displayed in Unreal Engine viewport")
        logger.info("Open Unreal Engine to see the statistics overlay")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("Unreal Engine Remote Control API - Demonstration")
    print("=" * 70)
    
    print("\nThis demo requires:")
    print("  • Unreal Engine 5.6+ running")
    print("  • Remote Control API plugin enabled")
    print("  • Unreal Engine launched with remote control flags")
    print("\nStarting demos in 3 seconds...")
    print("=" * 70 + "\n")
    
    time.sleep(3)
    
    # Run demos
    basic_client_demo()
    context_manager_demo()
    practical_example()
    
    # WebSocket demo (optional, might not work without proper setup)
    try:
        websocket_demo()
    except Exception as e:
        logger.warning(f"WebSocket demo skipped: {e}")
    
    print("\n" + "=" * 70)
    print("Demo completed!")
    print("=" * 70 + "\n")
    
    print("Next steps:")
    print("  1. Review the code in examples/remote_control_demo.py")
    print("  2. Read docs/remote-control/REMOTE_CONTROL_API.md")
    print("  3. Check config/remote_control_config.yaml for configuration")
    print("  4. Try creating your own automation scripts!")


if __name__ == "__main__":
    main()
