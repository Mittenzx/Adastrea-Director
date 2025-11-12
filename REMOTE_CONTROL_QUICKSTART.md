# Remote Control API Quick Start Guide

**For:** Adastrea Director Phase 3  
**Target Audience:** Developers implementing or using Remote Control integration  
**Prerequisites:** Phase 2 completion, Unreal Engine 5.6+  
**Est. Time:** 15-30 minutes

---

## Overview

This guide will help you quickly set up and test the Remote Control API integration between Adastrea Director and Unreal Engine. By the end, you'll have:

✅ Remote Control API enabled in Unreal Engine  
✅ Python client configured and connected  
✅ First successful API call executed  
✅ Basic agent workflow tested

---

## Table of Contents

1. [Unreal Engine Setup](#unreal-engine-setup)
2. [Adastrea Director Setup](#adastrea-director-setup)
3. [Testing the Connection](#testing-the-connection)
4. [First Agent Workflow](#first-agent-workflow)
5. [Troubleshooting](#troubleshooting)
6. [Next Steps](#next-steps)

---

## Unreal Engine Setup

### Step 1: Enable Remote Control Plugins

1. Open your Unreal Engine project (or create a test project)
2. Go to **Edit → Plugins**
3. Search for "Remote Control"
4. Enable the following plugins:
   - ✅ **Remote Control API**
   - ✅ **Remote Control Web Interface**
   - ✅ **Python Editor Script Plugin** (if not already enabled)
5. Click **Restart Now**

### Step 2: Create a Remote Control Preset

A preset defines which properties and functions are exposed to the Remote Control API.

1. Go to **Window → Remote Control → Remote Control Panel**
2. Click **+ Preset** button
3. Name it: `Adastrea_Automation`
4. The Remote Control panel will open

### Step 3: Expose Some Properties (Optional for Testing)

Let's expose a few things to test with:

**Option A: Quick Test with Level Actor**
1. Place any actor in your level (e.g., a Cube)
2. Select the actor
3. In Details panel, find a property (e.g., "Location")
4. Drag the property name into the Remote Control panel
5. The property is now exposed!

**Option B: Create a Test Blueprint**
1. Create a new Blueprint (Actor or Object)
2. Add some variables (e.g., `TestSpeed`, `TestHealth`)
3. Make them "Instance Editable" and "BlueprintReadWrite"
4. Save and close Blueprint
5. Place instance in level or reference in preset
6. Drag variables into Remote Control panel

### Step 4: Start the Remote Control Web Server

**Method 1: Manual Start**
1. In Remote Control panel, click **Start Server**
2. Default URL: `http://localhost:30010`
3. Server status indicator should turn green

**Method 2: Auto-Start on Launch**
1. Go to **Edit → Project Settings**
2. Search for "Remote Control"
3. Find **Plugins → Remote Control Web Interface**
4. Enable **Start Server on Launch**
5. Set **Remote Control HTTP Server Port** to `30010`
6. Restart editor

### Step 5: Verify Server is Running

Open a web browser and navigate to:
```
http://localhost:30010/remote/health
```

You should see:
```json
{
  "status": "ok"
}
```

✅ **Unreal Engine setup complete!**

---

## Adastrea Director Setup

### Step 1: Install Required Dependencies

If not already installed from Phase 2, add Remote Control dependencies:

```bash
# Navigate to Adastrea-Director directory
cd /path/to/Adastrea-Director

# Install/update dependencies
pip install -r requirements.txt
```

The following packages will be installed (if not already present):
- `requests>=2.31.0` - HTTP client
- `websocket-client>=1.6.0` - WebSocket support
- `websockets>=12.0` - Async WebSocket (for future enhancements)
- `GitPython>=3.1.0` - Git operations (for version control integration)

### Step 2: Configure Remote Control Settings

Edit the configuration file:

```bash
# Open configuration file
nano config/remote_control_config.yaml
# or use your preferred editor
```

Minimal required configuration:
```yaml
remote_control:
  default_host: "localhost"
  default_port: 30010

version_control:
  auto_sync: true
  create_feature_branches: true
```

For initial testing, the default values are fine. You can customize later.

### Step 3: Set Up Environment Variables (Optional)

Create or update `.env` file in project root:

```bash
# Remote Control API
REMOTE_CONTROL_HOST=localhost
REMOTE_CONTROL_PORT=30010

# Version Control (if using GitHub integration)
GITHUB_TOKEN=your_github_token_here
```

---

## Testing the Connection

### Test 1: Basic Health Check

Create a test script or use Python REPL:

```python
# test_connection.py
from remote_control.client import UnrealRemoteControlClient

# Create client
client = UnrealRemoteControlClient(host="localhost", port=30010)

# Test connection
if client.health_check():
    print("✅ Connected to Unreal Engine successfully!")
    
    # Get server info
    info = client.get_server_info()
    print(f"Engine Version: {info.engine_version}")
    print(f"Project Name: {info.project_name}")
else:
    print("❌ Connection failed. Check if UE Remote Control server is running.")
```

Run it:
```bash
python test_connection.py
```

Expected output:
```
✅ Connected to Unreal Engine successfully!
Engine Version: 5.6.0
Project Name: YourProjectName
```

### Test 2: List Available Presets

```python
# List all Remote Control presets
presets = client.list_presets()

print(f"Found {len(presets)} preset(s):")
for preset in presets:
    print(f"  - {preset.name}")
```

Expected output:
```
Found 1 preset(s):
  - Adastrea_Automation
```

### Test 3: Execute a Console Command

```python
# Execute a simple console command
result = client.execute_command("stat fps")
print(f"Command output: {result}")
```

This should enable the FPS counter in the Unreal Editor viewport.

### Test 4: Property Operations (if you exposed properties)

```python
# Get a property value
try:
    value = client.get_property(
        "/Game/YourLevel.YourLevel:PersistentLevel.Cube_0",
        "K2Node_GetActorLocation_ReturnValue"
    )
    print(f"Current location: {value}")
    
    # Set a property value
    success = client.set_property(
        "/Game/YourLevel.YourLevel:PersistentLevel.Cube_0",
        "RelativeLocation",
        {"X": 100.0, "Y": 200.0, "Z": 300.0}
    )
    
    if success:
        print("✅ Property updated successfully!")
except Exception as e:
    print(f"Property operation failed: {e}")
    print("Note: Ensure the object path is correct and property is exposed.")
```

---

## First Agent Workflow

Let's test a simple agent workflow that uses Remote Control API.

### Create a Test Agent Script

```python
# test_agent_workflow.py
import sys
sys.path.append('/path/to/Adastrea-Director')

from remote_control.client import UnrealRemoteControlClient
from version_control.agent import VersionControlAgent
from agents.remote_control_agent import RemoteControlAgent

class TestAgent(RemoteControlAgent):
    """Simple test agent to verify workflow."""
    
    def run_test_workflow(self):
        """Execute a simple test workflow."""
        print("Starting test agent workflow...")
        
        # Step 1: Check connection
        if not self.remote_control.health_check():
            print("❌ Cannot connect to Unreal Engine")
            return False
        print("✅ Connected to Unreal Engine")
        
        # Step 2: Execute a console command
        print("\nExecuting console command: stat fps")
        result = self.remote_control.execute_command("stat fps")
        print(f"✅ Command executed: {result[:50]}...")
        
        # Step 3: List presets
        presets = self.remote_control.list_presets()
        print(f"\n✅ Found {len(presets)} preset(s)")
        
        # Step 4: Create a branch (if version control enabled)
        if self.version_control:
            branch = self.version_control.before_agent_action(
                "TestAgent",
                "test_workflow"
            )
            print(f"\n✅ Created branch: {branch}")
            
            # Simulate some work...
            import time
            time.sleep(2)
            
            # Commit changes
            commit = self.version_control.after_agent_action(
                "TestAgent",
                branch,
                ["test_agent_workflow.log"]
            )
            print(f"✅ Created commit: {commit.commit_hash[:8]}")
        
        print("\n✨ Test workflow completed successfully!")
        return True

# Run the test
if __name__ == "__main__":
    # Initialize components
    rc_client = UnrealRemoteControlClient()
    vc_agent = VersionControlAgent(".")
    
    # Create and run test agent
    agent = TestAgent(rc_client, vc_agent)
    success = agent.run_test_workflow()
    
    if success:
        print("\n🎉 All systems operational!")
    else:
        print("\n❌ Test workflow failed")
```

Run it:
```bash
python test_agent_workflow.py
```

Expected output:
```
Starting test agent workflow...
✅ Connected to Unreal Engine

Executing console command: stat fps
✅ Command executed: FPS counter enabled...

✅ Found 1 preset(s)

✅ Created branch: agent/TestAgent/test_workflow/1699876543

✅ Created commit: a1b2c3d4

✨ Test workflow completed successfully!

🎉 All systems operational!
```

---

## Troubleshooting

### Issue: "Connection refused" or "Cannot connect"

**Cause:** Remote Control server is not running in Unreal Engine.

**Solution:**
1. Open Unreal Engine project
2. Go to **Window → Remote Control → Remote Control Panel**
3. Click **Start Server**
4. Verify server started at `http://localhost:30010`

### Issue: "Port already in use"

**Cause:** Another application is using port 30010.

**Solution:**
1. Change port in Unreal Engine:
   - **Edit → Project Settings → Plugins → Remote Control Web Interface**
   - Change **Remote Control HTTP Server Port** to `30011` or another free port
2. Update `config/remote_control_config.yaml`:
   ```yaml
   remote_control:
     default_port: 30011
   ```

### Issue: "Property not found" or "Object not found"

**Cause:** Object path is incorrect or property not exposed in Remote Control preset.

**Solution:**
1. In Unreal Engine, verify object exists in level
2. Get correct object path:
   - Select actor in level
   - Copy "Reference" from Details panel
3. Ensure property is dragged into Remote Control preset
4. Use exact object path in API calls

### Issue: "Permission denied" errors

**Cause:** Property or function is protected or not whitelisted.

**Solution:**
1. Check `config/remote_control_config.yaml` security settings
2. Ensure property/function is in allowed list
3. For testing, you can temporarily disable whitelisting:
   ```yaml
   security:
     whitelist_enabled: false
   ```

### Issue: WebSocket connection fails

**Cause:** WebSocket not enabled or port blocked.

**Solution:**
1. Check if WebSocket is enabled in config:
   ```yaml
   websocket:
     enable: true
   ```
2. Verify firewall allows WebSocket connections
3. Try disabling WebSocket for now:
   ```yaml
   websocket:
     enable: false
   ```

### Issue: Version control errors

**Cause:** Git repository not initialized or configured.

**Solution:**
1. Ensure you're in a git repository: `git status`
2. Initialize if needed: `git init`
3. Configure git user:
   ```bash
   git config user.name "Adastrea Director"
   git config user.email "adastrea@automated.agent"
   ```
4. Or disable version control for testing:
   ```python
   agent = TestAgent(rc_client, version_control=None)
   ```

---

## Next Steps

### 1. Explore More Examples

Check the `examples/remote_control/` directory for more example scripts:
- `basic_property_update.py` - Simple property get/set
- `automated_profiling.py` - Performance profiling workflow
- `batch_asset_optimization.py` - Batch asset operations

### 2. Set Up Specific Agents

Configure and test individual agents:
- **Performance Profiling Agent**: `agents/performance_profiling_agent.py`
- **Bug Detection Agent**: `agents/bug_detection_agent.py`
- **Asset Management Agent**: `agents/asset_management_agent.py`

### 3. Configure for Your Project

Customize `config/remote_control_config.yaml` for your specific needs:
- Add your Unreal Engine project paths
- Configure security settings
- Set up monitoring and alerts
- Customize agent behaviors

### 4. Integrate with Existing Workflows

- Update planning CLI to include Remote Control tasks
- Configure CI/CD integration
- Set up automated testing pipelines

### 5. Read Full Documentation

- **Implementation Plan**: `REMOTE_CONTROL_IMPLEMENTATION_PLAN.md`
- **API Reference**: `docs/remote_control_api_reference.md`
- **Agent Documentation**: `AGENTS.md`
- **Configuration Guide**: `docs/configuration_guide.md`

---

## Quick Reference

### Useful Commands

**Health Check:**
```python
client.health_check()  # Returns True/False
```

**Get Server Info:**
```python
info = client.get_server_info()
```

**List Presets:**
```python
presets = client.list_presets()
```

**Execute Console Command:**
```python
output = client.execute_command("stat fps")
```

**Get Property:**
```python
value = client.get_property(object_path, property_name)
```

**Set Property:**
```python
success = client.set_property(object_path, property_name, new_value)
```

**Call Function:**
```python
result = client.call_function(object_path, function_name, parameters)
```

**Load Level:**
```python
client.load_level("/Game/Maps/YourLevel")
```

**Start PIE:**
```python
client.start_play_in_editor()
```

**Stop PIE:**
```python
client.stop_play_in_editor()
```

### Common Object Paths

**Level Actor:**
```
/Game/YourLevel.YourLevel:PersistentLevel.ActorName
```

**Blueprint Class:**
```
/Game/Blueprints/BP_YourBlueprint.BP_YourBlueprint_C
```

**Data Asset:**
```
/Game/DataAssets/DA_YourAsset.DA_YourAsset
```

**Material:**
```
/Game/Materials/M_YourMaterial.M_YourMaterial
```

### Configuration File Locations

- Remote Control config: `config/remote_control_config.yaml`
- Agent config: `config/agent_config.yaml`
- Environment variables: `.env`
- Logs: `logs/remote_control.log`

---

## Getting Help

### Resources

- **Documentation**: `/docs/` directory
- **Examples**: `/examples/remote_control/` directory
- **Tests**: `/tests/` directory for reference implementations

### Support

- **GitHub Issues**: Report bugs or request features
- **Discussion Board**: Ask questions and share experiences
- **Documentation**: Full implementation details in `REMOTE_CONTROL_IMPLEMENTATION_PLAN.md`

---

## Success! What Now?

If you've completed all the tests successfully, you're ready to:

✅ Use Remote Control API in your workflows  
✅ Develop and test custom agents  
✅ Automate Unreal Engine tasks  
✅ Integrate with CI/CD pipelines  
✅ Move forward with Phase 3 implementation

**Congratulations! You've successfully set up Remote Control API integration.**

---

*Last Updated: 2025-11-12*  
*Version: 1.0.0*  
*Part of: Adastrea Director Phase 3*
