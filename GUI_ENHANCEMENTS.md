# GUI Enhancements - Status Dashboard & Server Management

## Overview
This update adds two powerful new tabs to the Adastrea Director GUI, addressing the user's request to:
1. Integrate all test and server run commands into GUI buttons (no terminal needed)
2. Show VS Code extension connection status
3. Show plugin connection status

## New Features

### 📊 Status Dashboard Tab

A comprehensive system status overview showing real-time connection and health information.

#### Features:
- **VS Code Extension Status**
  - Connection status (checking IPC port 5555)
  - Extension version
  - IPC port configuration
  - Auto-connect settings

- **Unreal Engine Plugin Status**
  - Plugin connection status (via MCP)
  - Remote Execution status
  - Python Plugin status
  - MCP Server status

- **Backend Services Status**
  - Agent Orchestrator (running/stopped)
  - Agent Dashboard (running/stopped)
  - MCP Server (running/stopped)
  - RAG System (database present/absent)

- **API Configuration**
  - LLM Provider (Gemini/OpenAI)
  - Gemini API Key status
  - OpenAI API Key status
  - Embedding Provider

- **System Health**
  - CPU Usage (with color-coded warnings)
  - Memory Usage (with color-coded warnings)
  - Disk Space
  - Python Version

#### UI Elements:
- 🔄 **Refresh All** button - Updates all status indicators
- Color-coded status indicators:
  - 🟢 Green: Connected/Running/Healthy
  - �� Yellow: Warning/Partial
  - 🔴 Red: Disconnected/Error
  - ⚪ Gray: Inactive/Not Set

### 🖥️ Servers Tab

Manage backend servers and services directly from the GUI - no terminal commands needed!

#### Available Services:
1. **Agent Orchestrator**
   - Start: `python agent_orchestrator_cli.py start --all`
   - Individual stop button
   - Manages all Phase 3 autonomous agents

2. **Agent Dashboard**
   - Start: `python agent_dashboard.py --auto-start`
   - Individual stop button
   - Real-time agent monitoring UI

3. **MCP Server**
   - Start: `python -m mcp_server.server`
   - Individual stop button
   - Enables Unreal Engine integration

4. **Demo Scripts Section**
   - Phase 3 Demo: `python phase3_demo.py`
   - Runs orchestrator demo with all agents

#### Features:
- ▶️ **Start buttons** for each service
- ⏹️ **Individual stop buttons** for each service
- ⏹️ **Stop All** button - Terminates all running servers
- 🗑️ **Clear** button - Clears output display
- **Real-time output streaming** - See server logs as they happen
- **Color-coded output**:
  - Success messages in green
  - Errors in red
  - Warnings in yellow
  - Info in gray
- **Thread-safe process management** - Prevents conflicts
- **Graceful shutdown** - Attempts SIGTERM before SIGKILL

### 🧪 Enhanced Tests Tab

Added more test command buttons to the existing Tests tab:

#### New Test Buttons:
- **🎮 MCP Tests** - Run MCP server tests
- **🖥️ GUI Tests** - Run GUI component tests
- **🔍 Check Compatibility** - Run `check_compatibility.py`
- **📦 Install Dependencies** - Run `install_dependencies.py`

#### Existing Test Buttons:
- 🚀 Run All Tests (pytest)
- 🔌 Plugin Tests
- ⚙️ Unit Tests
- 🔗 Integration Tests
- 🎯 Phase 3 Tests
- ✅ Validation Scripts
- 🌐 Remote Control Tests

All test buttons:
- Display real-time output
- Show pass/fail with color coding
- Can be stopped mid-execution
- Support parallel test discovery

## Usage Examples

### Checking System Status
1. Open GUI: `python gui_director.py`
2. Click on the **📊 Status** tab
3. Click **🔄 Refresh All** to update all indicators
4. Review connection status for:
   - VS Code Extension (port 5555)
   - Unreal Plugin (MCP connection)
   - Backend services
   - API keys
   - System health

### Starting Backend Services
1. Click on the **🖥️ Servers** tab
2. Click **▶ Agent Orchestrator** to start agent management
3. Click **▶ MCP Server** to enable Unreal Engine integration
4. Watch real-time output in the display area
5. Use individual ⏹️ buttons to stop specific services
6. Or use **⏹ Stop All** to terminate everything

### Running Tests
1. Click on the **🧪 Tests** tab
2. Select a test category:
   - For quick validation: **✅ Validation Scripts**
   - For MCP features: **🎮 MCP Tests**
   - For full suite: **🚀 Run All Tests**
3. Watch test output in real-time
4. Use **⏹ Stop** if needed to cancel
5. Results are color-coded (green=pass, red=fail)

## Technical Details

### Status Checking Implementation
- **IPC Connection**: Attempts socket connection to localhost:5555
- **Process Detection**: Uses `psutil` to find running processes
- **Database Check**: Verifies ChromaDB directory exists
- **API Keys**: Checks environment variables
- **System Metrics**: Uses `psutil` for CPU, memory, disk
- **Thread-safe Updates**: All UI updates use `root.after(0, ...)`

### Server Management Implementation
- **Process Spawning**: Uses `subprocess.Popen` with output streaming
- **Output Streaming**: Line-buffered real-time display
- **Process Tracking**: Thread-safe dictionary of running processes
- **Graceful Shutdown**: 3-second SIGTERM before SIGKILL
- **Error Handling**: Catches and displays all exceptions
- **Cross-platform**: Works on Windows (CREATE_NO_WINDOW), Linux, Mac

### Design Philosophy
- **No Terminal Required**: All commands accessible via GUI buttons
- **Real-time Feedback**: Immediate status updates and output streaming
- **Color-coded**: Intuitive visual indicators for all states
- **Thread-safe**: Prevents race conditions and UI freezing
- **Graceful Degradation**: Features work even if optional deps missing

## Benefits

### For Users
- ✅ No need to remember terminal commands
- ✅ Visual confirmation of all connections and services
- ✅ One-click server start/stop
- ✅ Real-time status monitoring
- ✅ Easy troubleshooting with status dashboard
- ✅ Centralized control of all backend services

### For Developers
- ✅ Faster testing workflow (click instead of type)
- ✅ Quick service management during development
- ✅ System health monitoring at a glance
- ✅ No context switching to terminal
- ✅ All tools in one interface

## Future Enhancements (Potential)
- [ ] Add auto-start option for servers on GUI launch
- [ ] Save server preferences (which to auto-start)
- [ ] Add more demo script options
- [ ] Log rotation for server output
- [ ] Export server logs to file
- [ ] Service restart buttons
- [ ] Health check polling intervals
- [ ] Notification on status changes
