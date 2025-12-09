# Copilot Agent Instructions for Adastrea Director

This document provides comprehensive instructions for GitHub Copilot agents and AI assistants working with the Adastrea Director plugin from VS Code. It covers all available connection methods, capabilities, and verification procedures.

## Table of Contents

- [Overview](#overview)
- [Quick Start for Copilot Agents](#quick-start-for-copilot-agents)
- [Connection Methods](#connection-methods)
- [Available Capabilities](#available-capabilities)
- [How to Connect](#how-to-connect)
- [How to Send Instructions](#how-to-send-instructions)
- [How to Verify Instructions](#how-to-verify-instructions)
- [Common Workflows](#common-workflows)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Overview

**Adastrea Director** is an AI-powered game development assistant system for Unreal Engine. As a Copilot agent, you can interact with it through multiple connection types to:

- Query documentation and project context (RAG system)
- Generate development plans and task breakdowns
- Execute code and commands in Unreal Engine
- Manage assets and actors in the editor
- Monitor system health and performance
- Retrieve information about the current project

The system provides **5 different connection methods**, each with specific capabilities:

1. **MCP Server** (Recommended for Copilot) - Direct integration via Model Context Protocol
2. **HTTP Remote Control API** - REST API for synchronous UE operations
3. **WebSocket Event Client** - Real-time event streaming
4. **Python IPC Server** - Communication with the AI backend
5. **UE Python API** - Direct Python execution in Unreal Editor

---

## Quick Start for Copilot Agents

### Prerequisites Check

Before you begin, verify these prerequisites are met:

1. ✅ **Unreal Engine Editor** is running
2. ✅ **Python Editor Script Plugin** is enabled in UE
3. ✅ **Remote Execution** is enabled (Edit → Project Settings → Python)
4. ✅ **Adastrea Director** Python environment is set up

### Fastest Way to Connect: MCP Server

The **Model Context Protocol (MCP) Server** is the recommended connection method for GitHub Copilot agents working from VS Code.

**Why MCP?**
- Native integration with VS Code and GitHub Copilot
- Automatic tool discovery
- Type-safe operation calls
- Built-in error handling
- No manual configuration needed in your code

**Setup:**

Add to your VS Code workspace settings (`.vscode/settings.json`):

```json
{
  "github.copilot.chat.experimental.mcpServers": {
    "adastrea-unreal": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/Adastrea-Director"
    }
  }
}
```

**Testing Connection:**

In Copilot Chat, you can now use natural language:
- "Get project information from Unreal Engine"
- "List all assets in the project"
- "Execute this Python code in Unreal: `import unreal; print(unreal.SystemLibrary.get_engine_version())`"

---

## Connection Methods

### 1. MCP Server (Recommended for Copilot)

**Best for:** Direct integration from VS Code with GitHub Copilot

**Available Tools:** 13 editor tools including:
- `editor_run_python` - Execute Python in Unreal Editor
- `editor_list_assets` - List all project assets
- `editor_get_asset_info` - Get asset details
- `editor_search_assets` - Search for assets
- `editor_console_command` - Run console commands
- `editor_project_info` - Get project information
- `editor_get_map_info` - Get current map details
- `editor_get_world_outliner` - List all actors
- `editor_create_object` - Create actors
- `editor_update_object` - Update actor properties
- `editor_delete_object` - Delete actors
- `editor_take_screenshot` - Capture viewport
- `editor_move_camera` - Position viewport camera

**How to Use:**

Once configured, Copilot can automatically invoke these tools based on your requests. You don't need to manually call them - just ask in natural language.

**Example:**
```
User: "What version of Unreal Engine is running?"
Copilot: *automatically uses editor_run_python tool*
Result: "5.3.2"
```

**Documentation:** See `mcp_server/MCP_SERVER_GUIDE.md` for complete details.

---

### 2. HTTP Remote Control API

**Best for:** Synchronous property manipulation and function calls

**Protocol:** HTTP/REST over TCP
**Default Port:** 30010
**Latency:** 10-50ms

**Key Capabilities:**
- Get/set object properties
- Call functions on UE objects
- Execute console commands
- Manage Remote Control presets

**Python Example:**

```python
from remote_control import UnrealRemoteControlClient

client = UnrealRemoteControlClient(host="localhost", port=30010)

# Check connection
if client.health_check():
    # Execute console command
    response = client.execute_command("stat fps")
    print(f"Command output: {response.data}")
    
    # Set property
    client.set_property(
        object_path="/Game/MyActor.MyActor_C",
        property_name="Health",
        value=100.0
    )
    
    # Call function
    result = client.call_function(
        object_path="/Game/MyActor.MyActor_C",
        function_name="TakeDamage",
        parameters={"Amount": 10.0}
    )

client.close()
```

**Verification:**
```python
# Verify property was set
response = client.get_property("/Game/MyActor.MyActor_C", "Health")
assert response.data == 100.0, "Property not set correctly"
```

---

### 3. WebSocket Event Client

**Best for:** Real-time monitoring and event streaming

**Protocol:** WebSocket over TCP
**Default Port:** 30010 (different endpoint than HTTP)
**Latency:** 1-5ms

**Key Capabilities:**
- Receive property change notifications
- Monitor function calls
- Track preset changes
- Monitor connection status

**Python Example:**

```python
from remote_control import WebSocketEventClient

client = WebSocketEventClient(host="localhost", port=30010)

# Define event handler
def on_property_changed(event):
    print(f"Property changed: {event['property_name']} = {event['value']}")

# Subscribe to events
client.on("property_changed", on_property_changed)
client.connect()

# Subscribe to specific property
client.subscribe_to_property("/Game/MyActor.MyActor_C", "Health")

# Keep listening
client.start_listening()
```

**Verification:**
Events are received in real-time. Check the console output or event handler logs to verify subscriptions are working.

---

### 4. Python IPC Server

**Best for:** AI/RAG queries, task planning, backend integration

**Protocol:** TCP Socket with JSON
**Default Port:** 5555
**Latency:** < 1ms

**Key Capabilities:**
- Documentation queries (RAG system)
- Task planning and goal analysis
- Document ingestion
- Code generation assistance
- Performance metrics
- Conversation history management

**Python Example:**

```python
import socket
import json

def send_ipc_request(request_type, data):
    """Send request to Director IPC server."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 5555))
    
    request = {
        "type": request_type,
        "data": data
    }
    
    sock.sendall(json.dumps(request).encode('utf-8') + b'\n')
    response = json.loads(sock.recv(4096).decode('utf-8'))
    sock.close()
    
    return response

# Query documentation
response = send_ipc_request("query", "How do I create a Blueprint in Unreal Engine?")
print(f"Answer: {response['result']}")
print(f"Sources: {response['sources']}")

# Generate a plan
response = send_ipc_request("plan", "Add a health bar UI to the player character")
print(f"Plan: {response['plan']}")

# Get metrics
response = send_ipc_request("metrics", "")
print(f"Performance: {response}")
```

**Request Types:**
- `ping` - Health check (returns "pong")
- `query` - Ask documentation questions
- `plan` - Generate development plans
- `analyze` - Analyze development goals
- `ingest` - Add documents to knowledge base
- `metrics` - Get performance metrics
- `clear_history` - Clear conversation history

**Verification:**

```python
# Verify connection
response = send_ipc_request("ping", "")
assert response["status"] == "success", "IPC server not responding"
assert response["message"] == "pong", "Unexpected ping response"
```

---

### 5. UE Python API Integration

**Best for:** Direct editor automation and asset operations

**Protocol:** Direct Python API (in-process)
**Latency:** < 0.1ms

**Key Capabilities:**
- Asset operations (create, modify, delete, query)
- Actor spawning and manipulation
- Editor commands and notifications
- Level operations
- Blueprint interactions

**Python Example (executed in Unreal Editor):**

```python
import unreal

# Get project information
project_name = unreal.SystemLibrary.get_game_name()
engine_version = unreal.SystemLibrary.get_engine_version()
print(f"Project: {project_name}, Engine: {engine_version}")

# List all assets
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
all_assets = asset_registry.get_all_assets()
print(f"Total assets: {len(all_assets)}")

# Spawn an actor
world = unreal.EditorLevelLibrary.get_editor_world()
location = unreal.Vector(0, 0, 100)
rotation = unreal.Rotator(0, 0, 0)
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.StaticMeshActor,
    location,
    rotation
)
actor.set_actor_label("MyNewActor")

# Get all actors in world
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
print(f"Actors in world: {len(all_actors)}")
```

**How to Execute via MCP:**

Use the `editor_run_python` tool:

```python
# This code runs in the MCP server, which sends it to UE
result = mcp_client.call_tool("editor_run_python", {
    "code": """
import unreal
print(unreal.SystemLibrary.get_engine_version())
"""
})
print(result)
```

**Verification:**

```python
# Verify actor was created
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
actor_labels = [actor.get_actor_label() for actor in all_actors]
assert "MyNewActor" in actor_labels, "Actor not created"
```

---

## Available Capabilities

### Documentation & Knowledge Base (via IPC)

**What you can do:**
- Query project documentation
- Get context-aware answers about Unreal Engine
- Search through ingested documents
- Access historical conversations

**Example Queries:**
- "How do I implement a health system in Unreal Engine?"
- "What is the recommended way to handle player input?"
- "Explain the Actor Component architecture"

**How to verify:**
Check the `sources` field in the response to see which documents were used to generate the answer.

---

### Task Planning & Goal Decomposition (via IPC)

**What you can do:**
- Break down high-level goals into actionable tasks
- Generate implementation plans
- Assess feasibility and complexity
- Get effort estimates

**Example Goals:**
- "Add a multiplayer lobby system"
- "Implement procedural terrain generation"
- "Create a dialogue system with branching choices"

**How to verify:**
Review the generated plan for:
- Clear task descriptions
- Logical dependencies
- Reasonable effort estimates
- Implementation suggestions

---

### Unreal Engine Control (via MCP/HTTP/Python API)

**What you can do:**
- Execute console commands
- Get/set object properties
- Call Blueprint functions
- Spawn and manipulate actors
- Query project and level information
- Take screenshots
- Control viewport camera

**Example Operations:**
```python
# Via MCP (from Copilot Chat)
"Set the player character's health to 100"
"Spawn a cube at position (0, 0, 100)"
"Take a screenshot of the current viewport"
"List all actors with 'Player' in the name"

# Via HTTP API (Python code)
client.execute_command("stat fps")
client.set_property("/Game/Player.Player_C", "MaxHealth", 100)

# Via Python API (executed in UE)
unreal.EditorLevelLibrary.spawn_actor_from_class(...)
```

**How to verify:**
- Use `editor_get_world_outliner` to list all actors
- Use `get_property` to read back set values
- Use `editor_take_screenshot` to visually verify changes
- Check console output for command results

---

### Asset Management (via MCP/Python API)

**What you can do:**
- List all project assets
- Search for assets by name or type
- Get detailed asset information
- Query asset metadata

**Example Operations:**
```python
# List all assets
assets = mcp_client.call_tool("editor_list_assets", {})

# Search for character assets
results = mcp_client.call_tool("editor_search_assets", {
    "search_term": "character",
    "asset_class": "SkeletalMesh"
})

# Get asset details
info = mcp_client.call_tool("editor_get_asset_info", {
    "asset_path": "/Game/Characters/Hero/SK_Hero"
})
```

**How to verify:**
- Check returned asset counts match expected values
- Verify asset paths are valid
- Confirm asset metadata is correct

---

### Real-time Monitoring (via WebSocket)

**What you can do:**
- Monitor property changes in real-time
- Track function calls
- Receive connection status updates
- Stream events from Unreal Engine

**Example Monitoring:**
```python
# Subscribe to health changes
client.subscribe_to_property("/Game/Player.Player_C", "Health")

# Monitor all property changes
client.subscribe_to_all_properties()

# Track specific events
client.on("property_changed", lambda e: print(f"Changed: {e}"))
```

**How to verify:**
- Make changes in Unreal Engine manually
- Verify events are received in your client
- Check event timestamps are recent
- Confirm event data is accurate

---

## How to Connect

### Method 1: Using MCP Server (Recommended for Copilot)

**Step 1: Ensure Unreal Engine is ready**

```python
# Check if UE Python plugin is enabled
import unreal
print(unreal.SystemLibrary.get_engine_version())
# If this works, you're ready!
```

**Step 2: Start MCP Server (if not auto-started)**

```bash
cd /path/to/Adastrea-Director
python -m mcp_server.server
```

**Step 3: Verify connection from Copilot Chat**

In VS Code Copilot Chat:
```
"Get project information from Unreal Engine"
```

If you receive project details, you're connected!

---

### Method 2: Using Python IPC Server

**Step 1: Start IPC Server**

```bash
cd /path/to/Adastrea-Director/Plugins/AdastreaDirector/Python
python ipc_server.py --port 5555
```

**Step 2: Test connection**

```python
import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 5555))
request = {"type": "ping", "data": ""}
sock.sendall(json.dumps(request).encode('utf-8') + b'\n')
response = json.loads(sock.recv(4096).decode('utf-8'))
print(response)  # Should print: {"status": "success", "message": "pong"}
sock.close()
```

---

### Method 3: Using HTTP Remote Control API

**Step 1: Enable Remote Control in Unreal Engine**

1. Launch Unreal Engine Editor with flags:
   ```bash
   UnrealEditor.exe <ProjectPath> -RCWebControlEnable -RCWebInterfaceEnable
   ```

2. Or enable in Project Settings:
   - Edit → Project Settings → Plugins → Remote Control API
   - Check "Enable Remote Control API"

**Step 2: Test connection**

```python
from remote_control import UnrealRemoteControlClient

client = UnrealRemoteControlClient(host="localhost", port=30010)
if client.health_check():
    print("Connected successfully!")
else:
    print("Connection failed")
```

---

### Method 4: Using WebSocket Client

**Step 1: Ensure Remote Control is enabled (same as HTTP)**

**Step 2: Connect to WebSocket endpoint**

```python
from remote_control import WebSocketEventClient

client = WebSocketEventClient(host="localhost", port=30010)
if client.connect():
    print("WebSocket connected!")
    client.start_listening()
```

---

## How to Send Instructions

### Via MCP Server (Natural Language)

**Recommended for Copilot agents:**

Simply ask in natural language in Copilot Chat:

```
"Create a StaticMeshActor at position (100, 200, 50)"
"Get the current map name"
"List all Blueprint actors in the world"
"Execute console command 'stat unit'"
"Search for assets containing 'character'"
```

Copilot will automatically translate your request into the appropriate MCP tool call.

---

### Via HTTP API (Programmatic)

**For precise control:**

```python
from remote_control import UnrealRemoteControlClient

client = UnrealRemoteControlClient(host="localhost", port=30010)

# Execute console command
response = client.execute_command("stat fps")
print(response.data)

# Set property
client.set_property(
    object_path="/Game/Player.Player_C",
    property_name="MaxHealth",
    value=150.0
)

# Call function
result = client.call_function(
    object_path="/Game/GameMode.GameMode_C",
    function_name="RestartGame",
    parameters={}
)

client.close()
```

---

### Via Python IPC (AI Backend)

**For RAG queries and planning:**

```python
import socket
import json

def ask_director(question):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 5555))
    
    request = {
        "type": "query",
        "data": question
    }
    
    sock.sendall(json.dumps(request).encode('utf-8') + b'\n')
    response = json.loads(sock.recv(8192).decode('utf-8'))
    sock.close()
    
    return response

# Ask a question
result = ask_director("How do I implement player movement in Unreal Engine?")
print(f"Answer: {result['result']}")
print(f"Sources: {result['sources']}")
```

---

### Via UE Python API (Direct Execution)

**For in-editor automation:**

```python
# This code runs inside Unreal Engine
import unreal

# Get editor subsystem
editor_subsystem = unreal.UnrealEditorSubsystem()

# Execute editor command
editor_subsystem.editor_exec_command("stat fps")

# Spawn actor
world = unreal.EditorLevelLibrary.get_editor_world()
location = unreal.Vector(0, 0, 100)
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.StaticMeshActor,
    location,
    unreal.Rotator(0, 0, 0)
)

# Modify actor
actor.set_actor_label("MyActor")
actor.set_actor_location(unreal.Vector(100, 100, 100), False, False)
```

**To execute from outside UE (via MCP):**

```python
code = """
import unreal
world = unreal.EditorLevelLibrary.get_editor_world()
print(f"Current world: {world.get_name()}")
"""

result = mcp_client.call_tool("editor_run_python", {"code": code})
print(result)
```

---

## How to Verify Instructions

### 1. Verify Connection Health

**MCP Server:**
```python
# Ask Copilot: "Is Unreal Engine connected?"
# Or use editor_project_info tool
```

**IPC Server:**
```python
response = send_ipc_request("ping", "")
assert response["status"] == "success"
assert response["message"] == "pong"
```

**HTTP API:**
```python
client = UnrealRemoteControlClient(host="localhost", port=30010)
assert client.health_check() == True
```

---

### 2. Verify Property Changes

**After setting a property:**

```python
# Set property
client.set_property("/Game/Player.Player_C", "Health", 100.0)

# Verify it was set
response = client.get_property("/Game/Player.Player_C", "Health")
assert response.data == 100.0, f"Expected 100.0, got {response.data}"
```

**Via MCP:**
```python
# Set via natural language
"Set player health to 100"

# Verify via Python
code = """
import unreal
player = unreal.GameplayStatics.get_player_character(unreal.EditorLevelLibrary.get_editor_world(), 0)
health = player.get_editor_property('Health')
print(f'Health: {health}')
"""
result = mcp_client.call_tool("editor_run_python", {"code": code})
# Check result contains "Health: 100"
```

---

### 3. Verify Actor Creation

**After spawning an actor:**

```python
# Spawn actor
mcp_client.call_tool("editor_create_object", {
    "object_class": "StaticMeshActor",
    "object_name": "TestCube",
    "location": {"x": 0, "y": 0, "z": 100}
})

# Verify it exists
result = mcp_client.call_tool("editor_get_world_outliner", {})
actor_names = [actor['name'] for actor in result['actors']]
assert "TestCube" in actor_names, "Actor not found in world"
```

**Alternative verification via Python:**

```python
code = """
import unreal
actors = unreal.EditorLevelLibrary.get_all_level_actors()
actor_labels = [a.get_actor_label() for a in actors]
print('TestCube' in actor_labels)
"""
result = mcp_client.call_tool("editor_run_python", {"code": code})
assert "True" in result, "Actor not found"
```

---

### 4. Verify Console Commands

**After executing a command:**

```python
# Execute command
response = client.execute_command("stat fps")

# Check response
assert response.success == True, "Command failed"
assert response.data is not None, "No command output"
print(f"Command output: {response.data}")
```

---

### 5. Verify RAG Queries

**After querying documentation:**

```python
response = send_ipc_request("query", "How do I create a Blueprint?")

# Verify response structure
assert response["status"] == "success", "Query failed"
assert "result" in response, "No result in response"
assert "sources" in response, "No sources in response"
assert len(response["sources"]) > 0, "No sources found"

# Verify answer quality
assert len(response["result"]) > 50, "Answer too short"
print(f"Answer uses {len(response['sources'])} sources")
```

---

### 6. Verify Screenshot Capture

**After taking a screenshot:**

```python
import os

result = mcp_client.call_tool("editor_take_screenshot", {})

# Verify file was created
screenshot_path = result['path']
assert os.path.exists(screenshot_path), "Screenshot not saved"
assert os.path.getsize(screenshot_path) > 0, "Screenshot is empty"
print(f"Screenshot saved: {screenshot_path}")
```

---

### 7. Verify Asset Operations

**After searching for assets:**

```python
result = mcp_client.call_tool("editor_search_assets", {
    "search_term": "character",
    "asset_class": "SkeletalMesh"
})

# Verify results
assert len(result['assets']) > 0, "No assets found"
assert all('character' in a.lower() for a in result['assets']), "Invalid search results"
print(f"Found {len(result['assets'])} character assets")
```

---

### 8. Verify Plan Generation

**After generating a plan:**

```python
response = send_ipc_request("plan", "Add a health bar UI")

# Verify plan structure
assert response["status"] == "success", "Plan generation failed"
assert "plan" in response, "No plan in response"

plan = response["plan"]
assert "tasks" in plan, "No tasks in plan"
assert len(plan["tasks"]) > 0, "Plan has no tasks"
assert "dependencies" in plan, "No dependencies in plan"

print(f"Generated plan with {len(plan['tasks'])} tasks")
```

---

## Common Workflows

### Workflow 1: Query Documentation → Generate Code → Execute in UE

```python
# Step 1: Query documentation via IPC
question = "How do I spawn a particle effect in Unreal Engine?"
response = send_ipc_request("query", question)
print(f"Documentation says: {response['result']}")

# Step 2: Generate code based on the answer
code = """
import unreal

# Spawn particle system
world = unreal.EditorLevelLibrary.get_editor_world()
location = unreal.Vector(0, 0, 100)
particle_system = unreal.EditorAssetLibrary.load_asset('/Game/Effects/P_Explosion')

if particle_system:
    unreal.GameplayStatics.spawn_emitter_at_location(
        world,
        particle_system,
        location
    )
    print('Particle effect spawned successfully')
else:
    print('Failed to load particle system')
"""

# Step 3: Execute in UE via MCP
result = mcp_client.call_tool("editor_run_python", {"code": code})
print(f"Execution result: {result}")

# Step 4: Verify
assert "successfully" in result.lower(), "Particle spawn failed"
```

---

### Workflow 2: Create Actor → Set Properties → Verify

```python
# Step 1: Create actor via MCP
mcp_client.call_tool("editor_create_object", {
    "object_class": "StaticMeshActor",
    "object_name": "HealthPickup",
    "location": {"x": 100, "y": 200, "z": 50},
    "scale": {"x": 2.0, "y": 2.0, "z": 2.0}
})

# Step 2: Set custom properties via HTTP API
client = UnrealRemoteControlClient(host="localhost", port=30010)
client.set_property(
    object_path="/Game/HealthPickup.HealthPickup",
    property_name="HealAmount",
    value=25.0
)

# Step 3: Verify actor exists and has correct properties
outliner = mcp_client.call_tool("editor_get_world_outliner", {})
health_pickup = next((a for a in outliner['actors'] if a['name'] == 'HealthPickup'), None)

assert health_pickup is not None, "Actor not found"
assert health_pickup['scale']['x'] == 2.0, "Scale not set correctly"

# Verify property via HTTP
prop_response = client.get_property(
    "/Game/HealthPickup.HealthPickup",
    "HealAmount"
)
assert prop_response.data == 25.0, "Property not set correctly"

print("✓ Actor created and configured successfully")
```

---

### Workflow 3: Monitor Changes → React to Events

```python
from remote_control import WebSocketEventClient

# Step 1: Connect to WebSocket
ws_client = WebSocketEventClient(host="localhost", port=30010)
ws_client.connect()

# Step 2: Define event handlers
def on_health_changed(event):
    new_health = event['value']
    print(f"Player health changed to: {new_health}")
    
    # React to low health
    if new_health < 20:
        print("⚠️ Warning: Health is critical!")
        # Send notification via IPC
        send_ipc_request("query", "How do I heal the player?")

def on_death(event):
    print("💀 Player died!")
    # Generate respawn plan
    send_ipc_request("plan", "Implement player respawn system")

# Step 3: Subscribe to events
ws_client.on("property_changed", on_health_changed)
ws_client.subscribe_to_property("/Game/Player.Player_C", "Health")

# Step 4: Start listening
ws_client.start_listening()

# Step 5: Make changes in UE to trigger events
# The event handlers will be called automatically
```

---

### Workflow 4: Generate Plan → Execute Tasks → Verify Results

```python
# Step 1: Generate implementation plan
goal = "Add a simple inventory system to the player"
plan_response = send_ipc_request("plan", goal)
plan = plan_response["plan"]

print(f"Generated plan with {len(plan['tasks'])} tasks:")
for i, task in enumerate(plan['tasks'], 1):
    print(f"{i}. {task['description']}")

# Step 2: Execute each task
for task in plan['tasks']:
    print(f"\nExecuting: {task['description']}")
    
    # Generate code for the task
    code_prompt = f"Generate Unreal Engine Python code to: {task['description']}"
    code_response = send_ipc_request("query", code_prompt)
    
    # Execute the generated code
    result = mcp_client.call_tool("editor_run_python", {
        "code": code_response["result"]
    })
    
    print(f"Result: {result}")
    
    # Wait for user confirmation or automated checks
    task_success = "error" not in result.lower()
    
    if not task_success:
        print(f"⚠️ Task failed: {task['description']}")
        break
    else:
        print(f"✓ Task completed: {task['description']}")

# Step 3: Verify the entire implementation
print("\nVerifying implementation...")

verification_code = """
import unreal

# Check if inventory component exists
player = unreal.GameplayStatics.get_player_character(
    unreal.EditorLevelLibrary.get_editor_world(), 0
)

components = player.get_components_by_class(unreal.ActorComponent)
component_names = [c.get_name() for c in components]

has_inventory = any('inventory' in name.lower() for name in component_names)
print(f'Has inventory component: {has_inventory}')
"""

verify_result = mcp_client.call_tool("editor_run_python", {"code": verification_code})

if "True" in verify_result:
    print("✓ Implementation verified successfully!")
else:
    print("⚠️ Implementation verification failed")
```

---

### Workflow 5: Asset Search → Batch Operations

```python
# Step 1: Search for all texture assets
search_result = mcp_client.call_tool("editor_search_assets", {
    "search_term": "",
    "asset_class": "Texture2D"
})

textures = search_result['assets']
print(f"Found {len(textures)} texture assets")

# Step 2: Get detailed info for each texture
texture_info = []
for texture_path in textures[:10]:  # Limit to first 10 for demo
    info = mcp_client.call_tool("editor_get_asset_info", {
        "asset_path": texture_path
    })
    texture_info.append(info)

# Step 3: Analyze and report
print("\nTexture Analysis:")
for info in texture_info:
    print(f"  {info['name']}: {info['class']}")

# Step 4: Batch operation example - generate material instances
for texture_path in textures[:5]:  # Create materials for first 5
    material_code = f"""
import unreal

# Load texture
texture = unreal.EditorAssetLibrary.load_asset('{texture_path}')

# Create material
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
material_factory = unreal.MaterialFactoryNew()

material = asset_tools.create_asset(
    'M_' + texture.get_name(),
    '/Game/Materials',
    unreal.Material,
    material_factory
)

print(f'Created material: {{material.get_name()}}')
"""
    
    result = mcp_client.call_tool("editor_run_python", {"code": material_code})
    print(f"Material creation result: {result}")

print("✓ Batch operation completed")
```

---

## Troubleshooting

### Issue: "Connection refused" when connecting to IPC server

**Diagnosis:**
```python
import socket

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 5555))
    print("✓ IPC server is running")
    sock.close()
except ConnectionRefusedError:
    print("✗ IPC server is not running")
```

**Solutions:**
1. Start the IPC server:
   ```bash
   cd /path/to/Adastrea-Director/Plugins/AdastreaDirector/Python
   python ipc_server.py --port 5555
   ```

2. Check if port is already in use:
   ```bash
   # Linux/Mac
   lsof -i :5555
   
   # Windows
   netstat -ano | findstr :5555
   ```

3. Try a different port:
   ```python
   python ipc_server.py --port 5556
   ```

---

### Issue: "Not connected to Unreal Engine" with MCP server

**Diagnosis:**
```python
# Check if UE Python plugin is enabled
code = "import unreal; print(unreal.SystemLibrary.get_engine_version())"
result = mcp_client.call_tool("editor_run_python", {"code": code})
```

**Solutions:**
1. Enable Python Editor Script Plugin in UE:
   - Edit → Plugins → Search "Python"
   - Enable "Python Editor Script Plugin"
   - Restart UE

2. Enable Remote Execution:
   - Edit → Project Settings → Plugins → Python
   - Check "Enable Remote Execution"

3. Check firewall settings:
   - Allow Python on port 6766 (multicast)
   - Allow Unreal Engine Editor

4. Verify multicast settings:
   ```python
   # In Project Settings → Python → Remote Execution
   # Set "Multicast Bind Address" to "0.0.0.0"
   ```

---

### Issue: HTTP API returns errors

**Diagnosis:**
```python
client = UnrealRemoteControlClient(host="localhost", port=30010)
try:
    if client.health_check():
        print("✓ HTTP API is accessible")
    else:
        print("✗ HTTP API health check failed")
except Exception as e:
    print(f"✗ Error: {e}")
```

**Solutions:**
1. Launch UE with Remote Control flags:
   ```bash
   UnrealEditor.exe <Project> -RCWebControlEnable -RCWebInterfaceEnable
   ```

2. Enable in Project Settings:
   - Edit → Project Settings → Plugins → Remote Control API
   - Check "Enable Remote Control API"
   - Check "Enable Remote Control Web Interface"

3. Verify port 30010 is accessible:
   ```bash
   curl http://localhost:30010/remote/object/call
   ```

---

### Issue: WebSocket not receiving events

**Diagnosis:**
```python
ws_client = WebSocketEventClient(host="localhost", port=30010)
if ws_client.connect():
    print("✓ WebSocket connected")
    # Try subscribing to any property
    ws_client.subscribe_to_all_properties()
    print("Waiting for events... (make changes in UE)")
else:
    print("✗ WebSocket connection failed")
```

**Solutions:**
1. Ensure HTTP API is enabled (WebSocket uses same endpoint)
2. Check WebSocket endpoint is accessible:
   ```bash
   wscat -c ws://localhost:30010/remote/events
   ```

3. Verify subscriptions are active:
   ```python
   # Subscribe to specific property first
   ws_client.subscribe_to_property("/Game/Player.Player_C", "Health")
   # Then make changes to that property in UE
   ```

---

### Issue: Queries return no results

**Diagnosis:**
```python
response = send_ipc_request("query", "test")
if response["status"] == "success":
    if len(response.get("sources", [])) == 0:
        print("✗ No documents in knowledge base")
    else:
        print(f"✓ Knowledge base has {len(response['sources'])} relevant docs")
```

**Solutions:**
1. Ingest documentation:
   ```bash
   cd /path/to/Adastrea-Director
   python ingest.py --docs-dir /path/to/docs
   ```

2. Check if database exists:
   ```python
   import os
   db_path = "./chroma_db"
   if os.path.exists(db_path):
       print(f"✓ Database exists at {db_path}")
   else:
       print(f"✗ Database not found at {db_path}")
   ```

3. Verify API key is configured:
   ```bash
   # For queries, you need an LLM API key
   export GEMINI_KEY="your-key"
   # or
   python main.py --set-api-key gemini
   ```

---

### Issue: Python code fails to execute in UE

**Diagnosis:**
```python
# Test basic Python execution
code = "print('Hello from Unreal Engine')"
result = mcp_client.call_tool("editor_run_python", {"code": code})
print(result)
```

**Solutions:**
1. Check Python syntax:
   ```python
   # Ensure code is valid Python
   import ast
   try:
       ast.parse(your_code)
       print("✓ Code syntax is valid")
   except SyntaxError as e:
       print(f"✗ Syntax error: {e}")
   ```

2. Verify imports are available:
   ```python
   # Test if unreal module is available
   code = """
try:
    import unreal
    print('unreal module available')
except ImportError:
    print('unreal module not available')
"""
   result = mcp_client.call_tool("editor_run_python", {"code": code})
   ```

3. Check for runtime errors:
   ```python
   # Wrap code in try-except for debugging
   code = """
try:
    import unreal
    # Your code here
    result = unreal.EditorLevelLibrary.get_editor_world()
    print(f'Success: {result}')
except Exception as e:
    print(f'Error: {str(e)}')
    import traceback
    traceback.print_exc()
"""
   ```

---

## Best Practices

### 1. Always Verify Connections First

Before sending instructions, verify the connection:

```python
# Quick connection check
def verify_all_connections():
    results = {}
    
    # Check IPC
    try:
        response = send_ipc_request("ping", "")
        results['IPC'] = response["message"] == "pong"
    except:
        results['IPC'] = False
    
    # Check HTTP
    try:
        client = UnrealRemoteControlClient(host="localhost", port=30010)
        results['HTTP'] = client.health_check()
        client.close()
    except:
        results['HTTP'] = False
    
    # Check MCP
    try:
        result = mcp_client.call_tool("editor_project_info", {})
        results['MCP'] = 'project_name' in result
    except:
        results['MCP'] = False
    
    return results

# Use before operations
connections = verify_all_connections()
print(f"Connection Status: {connections}")
```

---

### 2. Use Appropriate Connection for the Task

**Choose the right tool:**

- **MCP Server**: Best for Copilot-driven workflows, natural language requests
- **HTTP API**: Best for property manipulation, function calls, console commands
- **WebSocket**: Best for monitoring and real-time updates
- **IPC Server**: Best for RAG queries, planning, knowledge base
- **Python API**: Best for complex editor automation

**Example decision tree:**

```python
task_type = "create_actor"  # Example task

if task_type in ["create_actor", "modify_actor", "query_scene"]:
    # Use MCP Server
    use_mcp_server()
elif task_type in ["monitor_property", "track_events"]:
    # Use WebSocket
    use_websocket()
elif task_type in ["query_docs", "generate_plan"]:
    # Use IPC Server
    use_ipc_server()
elif task_type in ["batch_operations", "complex_automation"]:
    # Use Python API directly
    use_python_api()
```

---

### 3. Handle Errors Gracefully

**Always include error handling:**

```python
def safe_api_call(client_method, *args, **kwargs):
    """Wrapper for safe API calls with error handling."""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            result = client_method(*args, **kwargs)
            return result
        except ConnectionError as e:
            if attempt < max_retries - 1:
                print(f"Connection error, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Failed after {max_retries} attempts: {e}")
                raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    
    return None

# Usage
result = safe_api_call(
    client.set_property,
    "/Game/Player.Player_C",
    "Health",
    100.0
)
```

---

### 4. Verify Critical Operations

**Always verify important changes:**

```python
def set_and_verify_property(client, object_path, property_name, value):
    """Set property and verify it was set correctly."""
    # Set property
    client.set_property(object_path, property_name, value)
    
    # Wait briefly for propagation
    time.sleep(0.1)
    
    # Verify
    response = client.get_property(object_path, property_name)
    
    if response.data == value:
        print(f"✓ Property {property_name} set to {value}")
        return True
    else:
        print(f"✗ Property {property_name} mismatch: expected {value}, got {response.data}")
        return False

# Usage
success = set_and_verify_property(
    client,
    "/Game/Player.Player_C",
    "MaxHealth",
    150.0
)
```

---

### 5. Use Context from RAG System

**Leverage the knowledge base:**

```python
def informed_action(task_description):
    """Perform action informed by documentation."""
    # Step 1: Query knowledge base
    response = send_ipc_request("query", 
        f"Best practices for: {task_description}")
    
    best_practices = response["result"]
    print(f"Documentation suggests: {best_practices}")
    
    # Step 2: Generate plan based on documentation
    plan_response = send_ipc_request("plan", task_description)
    plan = plan_response["plan"]
    
    # Step 3: Execute plan
    for task in plan["tasks"]:
        print(f"Executing: {task['description']}")
        # Execute task...
    
    return plan

# Usage
informed_action("Create a damage system for the player")
```

---

### 6. Log All Operations

**Maintain audit trail:**

```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename=f'director_operations_{datetime.now().strftime("%Y%m%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def logged_operation(operation_name, operation_func, *args, **kwargs):
    """Execute operation with logging."""
    logging.info(f"Starting: {operation_name}")
    logging.debug(f"Args: {args}, Kwargs: {kwargs}")
    
    try:
        result = operation_func(*args, **kwargs)
        logging.info(f"Completed: {operation_name}")
        logging.debug(f"Result: {result}")
        return result
    except Exception as e:
        logging.error(f"Failed: {operation_name} - {str(e)}")
        raise

# Usage
result = logged_operation(
    "Set player health",
    client.set_property,
    "/Game/Player.Player_C",
    "Health",
    100.0
)
```

---

### 7. Use Batch Operations When Possible

**Optimize multiple operations:**

```python
def batch_property_update(client, object_path, properties):
    """Update multiple properties efficiently."""
    results = {}
    
    for prop_name, value in properties.items():
        try:
            client.set_property(object_path, prop_name, value)
            results[prop_name] = "success"
        except Exception as e:
            results[prop_name] = f"failed: {str(e)}"
    
    # Verify all at once
    for prop_name in properties.keys():
        try:
            response = client.get_property(object_path, prop_name)
            if response.data != properties[prop_name]:
                results[prop_name] = "verification_failed"
        except Exception as e:
            results[prop_name] = f"verification_error: {str(e)}"
    
    return results

# Usage
properties = {
    "Health": 100.0,
    "MaxHealth": 150.0,
    "Speed": 600.0,
    "JumpHeight": 420.0
}

results = batch_property_update(
    client,
    "/Game/Player.Player_C",
    properties
)

print(f"Batch update results: {results}")
```

---

### 8. Document Your Workflows

**Create reusable patterns:**

```python
def standard_actor_creation_workflow(
    actor_class,
    actor_name,
    location,
    custom_properties=None
):
    """
    Standard workflow for creating and configuring actors.
    
    Args:
        actor_class: Unreal Engine actor class name
        actor_name: Label for the actor
        location: Dict with x, y, z coordinates
        custom_properties: Optional dict of properties to set
    
    Returns:
        Dict with creation results and verification status
    """
    workflow_result = {
        "created": False,
        "properties_set": False,
        "verified": False
    }
    
    try:
        # Step 1: Create actor
        mcp_client.call_tool("editor_create_object", {
            "object_class": actor_class,
            "object_name": actor_name,
            "location": location
        })
        workflow_result["created"] = True
        
        # Step 2: Set custom properties
        if custom_properties:
            client = UnrealRemoteControlClient(host="localhost", port=30010)
            for prop_name, value in custom_properties.items():
                client.set_property(
                    f"/Game/{actor_name}.{actor_name}",
                    prop_name,
                    value
                )
            workflow_result["properties_set"] = True
        
        # Step 3: Verify
        outliner = mcp_client.call_tool("editor_get_world_outliner", {})
        actor_exists = any(a['name'] == actor_name for a in outliner['actors'])
        workflow_result["verified"] = actor_exists
        
    except Exception as e:
        workflow_result["error"] = str(e)
    
    return workflow_result

# Usage
result = standard_actor_creation_workflow(
    actor_class="StaticMeshActor",
    actor_name="HealthPickup",
    location={"x": 100, "y": 200, "z": 50},
    custom_properties={"HealAmount": 25.0}
)

print(f"Workflow result: {result}")
```

---

## Summary

This document provides comprehensive instructions for Copilot agents to:

1. ✅ **Connect** to Adastrea Director via 5 different methods (MCP recommended)
2. ✅ **Query** documentation and get context-aware answers
3. ✅ **Control** Unreal Engine (properties, functions, console commands)
4. ✅ **Create** and manipulate actors and assets
5. ✅ **Monitor** real-time events and changes
6. ✅ **Generate** implementation plans and task breakdowns
7. ✅ **Verify** that instructions were carried out correctly
8. ✅ **Troubleshoot** common issues
9. ✅ **Follow** best practices for robust automation

### Quick Reference Card

| Task | Best Method | Example |
|------|-------------|---------|
| Ask documentation questions | IPC Server | `send_ipc_request("query", "How to...")` |
| Execute Python in UE | MCP Server | `"Run Python code in Unreal Engine"` |
| Set object properties | HTTP API | `client.set_property(path, prop, value)` |
| Monitor property changes | WebSocket | `ws_client.subscribe_to_property(...)` |
| Generate plans | IPC Server | `send_ipc_request("plan", "Add feature")` |
| List assets | MCP Server | `"List all assets in the project"` |
| Create actors | MCP Server | `"Create a StaticMeshActor at (0,0,100)"` |
| Take screenshot | MCP Server | `"Take a screenshot of the viewport"` |

### Next Steps

1. **Test your connection** using the Quick Start section
2. **Try example workflows** to understand the patterns
3. **Verify operations** using the provided verification methods
4. **Build custom workflows** for your specific needs
5. **Refer to detailed docs** for advanced features:
   - `mcp_server/MCP_SERVER_GUIDE.md` - Complete MCP documentation
   - `wiki/Remote-Connection-Types-and-Actions.md` - All connection types
   - `Plugins/AdastreaDirector/README.md` - Plugin documentation
   - `vscode-extension/README.md` - VS Code extension guide

---

**For issues or questions, refer to:**
- [GitHub Issues](https://github.com/Mittenzx/Adastrea-Director/issues)
- [Project Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki)
- Main project README.md

**Version:** 1.0.0  
**Last Updated:** December 2024  
**Project:** Adastrea Director - AI Game Development Assistant
