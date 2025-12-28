# Landing Screen Guide

## Overview

The Landing Screen (Home tab) is the default startup screen in Adastrea Director. It provides a real-time "what's happening" view of your system's connection status and recent activity.

## Features

### Connection Status Diagram

The landing screen displays a visual diagram showing the connection status between three key components:

1. **VSCode Extension** (🔌)
   - Shows whether the VSCode extension is connected to the Director
   - Icon: Blue connector symbol
   - Status indicator: Green (connected) or Red (disconnected)

2. **IPC Server** (🔗)
   - Shows the status of the Inter-Process Communication server
   - Icon: Link symbol
   - Status indicator: Green (running) or Red (not running)

3. **Director Backend** (⚡)
   - Shows the status of the Adastrea Director backend (always running)
   - Icon: Lightning bolt
   - Status indicator: Green (running)

### Connection Lines

Lines between components indicate the communication paths:
- **Solid green lines**: Active connection
- **Dashed gray lines**: No connection

### Recent Activity Log

The bottom section displays recent system activity with timestamps, including:
- System initialization messages
- Connection status updates
- Service status changes
- Important system events

## Usage

### Viewing the Landing Screen

The Landing Screen is displayed by default when you start Adastrea Director. You can return to it at any time by clicking the **🏠 Home** tab.

### Refreshing Status

- **Manual Refresh**: Click the **🔄 Refresh** button in the top-right corner
- **Auto-Refresh**: The system automatically refreshes every 5 seconds when the Home tab is visible

### Understanding Status Indicators

| Color | Meaning |
|-------|---------|
| 🟢 Green | Connected/Running |
| 🔴 Red | Disconnected/Not Running |
| 🟡 Yellow | Connecting/Transitioning (future feature) |

## Technical Details

### Connection Checks

- **VSCode Connection**: Checks for active IPC connection from VSCode extension
- **IPC Server**: Attempts to connect to port 8765 (default IPC server port)
- **Director**: Always shows as running (this is the GUI itself)

### Auto-Refresh Behavior

- Refreshes every 5 seconds
- Only refreshes when the Home tab is active (saves resources)
- Can be manually stopped/started programmatically

## Benefits

1. **Quick Status Overview**: See system health at a glance
2. **Troubleshooting**: Quickly identify connection issues
3. **Activity Monitoring**: Track system events in real-time
4. **User-Friendly**: Visual representation makes complex connections easy to understand

## Future Enhancements

Planned improvements include:
- [ ] Additional component monitoring (Unreal Engine, databases, etc.)
- [ ] Connection quality indicators (latency, throughput)
- [ ] Historical connection data and graphs
- [ ] Custom refresh intervals
- [ ] More detailed component status information
- [ ] Alert notifications for connection issues

## Troubleshooting

### VSCode Extension Shows Disconnected

1. Ensure the Adastrea Director VSCode extension is installed
2. Check that the IPC server is running
3. Verify VSCode extension settings

### IPC Server Shows Not Running

1. Start the IPC server manually from the Servers tab
2. Check if port 8765 is available
3. Review server logs for errors

## Related Documentation

- [VSCode Extension Integration](VSCODE_EXTENSION_INTEGRATION.md)
- [IPC MCP Integration Guide](IPC_MCP_INTEGRATION_GUIDE.md)
- [GUI Visual Description](GUI_VISUAL_DESCRIPTION.md)

---

*For more information, see the main [README.md](README.md) or visit the [Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki)*
