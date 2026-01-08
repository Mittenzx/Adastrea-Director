# Remote Control API - Quick Integration Guide

**Quick answer**: Remote Control API is NOT integrated yet, but here's how to do it.

## 5-Minute Integration: GUI Director

### Step 1: Import the Client

Add to imports in `gui_director.py` (around line 42):

```python
from remote_control import UnrealRemoteControlClient
```

### Step 2: Initialize in `__init__`

Add to `AdastreaDirectorApp.__init__` (around line 640):

```python
# Initialize Remote Control client
self.remote_control_client = None
self.remote_control_connected = False
```

### Step 3: Update Connect Method

Replace the `connect_to_unreal` method (around line 1379):

```python
def connect_to_unreal(self):
    """Connect to Unreal Engine via Remote Control API."""
    try:
        self.remote_control_client = UnrealRemoteControlClient(
            host="localhost",
            port=30010,
            timeout=30
        )
        
        if self.remote_control_client.health_check():
            self.remote_control_connected = True
            self.unreal_status_indicator.config(fg=self.success_color)
            self.unreal_status_label.config(text="Connected", fg=self.success_color)
            self.unreal_connect_button.config(state=tk.DISABLED)
            self.unreal_disconnect_button.config(state=tk.NORMAL)
            self.log_to_landing("✅ Connected to Unreal Engine Remote Control API", "success")
            messagebox.showinfo("Connected", "Successfully connected to Unreal Engine!")
        else:
            raise Exception("Health check failed")
            
    except Exception as e:
        self.remote_control_connected = False
        messagebox.showerror("Connection Failed", 
            f"Failed to connect to Unreal Engine:\n{e}\n\n"
            "Make sure:\n"
            "1. Unreal Engine is running\n"
            "2. Remote Control plugins are enabled\n"
            "3. UE launched with -RCWebControlEnable -RCWebInterfaceEnable")
```

### Step 4: Update Disconnect Method

Replace the `disconnect_from_unreal` method (around line 1394):

```python
def disconnect_from_unreal(self):
    """Disconnect from Unreal Engine."""
    if self.remote_control_client:
        try:
            self.remote_control_client.close()
        except:
            pass
        self.remote_control_client = None
    
    self.remote_control_connected = False
    self.unreal_status_indicator.config(fg=self.fg_muted)
    self.unreal_status_label.config(text="Disconnected", fg=self.fg_muted)
    self.unreal_connect_button.config(state=tk.NORMAL)
    self.unreal_disconnect_button.config(state=tk.DISABLED)
    self.log_to_landing("Disconnected from Unreal Engine", "info")
    messagebox.showinfo("Disconnected", "Disconnected from Unreal Engine")
```

### Step 5: Update Tool Execution

Replace the `run_mcp_tool` method (around line 1419):

```python
def run_mcp_tool(self, tool_name):
    """Execute an MCP tool using Remote Control API."""
    if not self.remote_control_connected:
        messagebox.showwarning("Not Connected", "Please connect to Unreal Engine first")
        return
    
    try:
        self.append_mcp_output(f"\n▶ Running: {tool_name}\n")
        
        if tool_name == "editor_project_info":
            response = self.remote_control_client.execute_command("stat namedevents")
            self.append_mcp_output(f"✓ Command executed successfully\n")
            if response.data:
                self.append_mcp_output(f"Output: {response.data}\n")
            
        elif tool_name == "map_info":
            response = self.remote_control_client.execute_command("stat levels")
            self.append_mcp_output(f"✓ Command executed successfully\n")
            if response.data:
                self.append_mcp_output(f"Output: {response.data}\n")
            
        elif tool_name == "actor_list":
            response = self.remote_control_client.execute_command("listactors")
            self.append_mcp_output(f"✓ Command executed successfully\n")
            if response.data:
                self.append_mcp_output(f"Output: {response.data}\n")
        
        elif tool_name == "stat_fps":
            response = self.remote_control_client.execute_command("stat fps")
            self.append_mcp_output(f"✓ FPS stats enabled in viewport\n")
            
        elif tool_name == "stat_unit":
            response = self.remote_control_client.execute_command("stat unit")
            self.append_mcp_output(f"✓ Unit stats enabled in viewport\n")
            
        elif tool_name == "stat_memory":
            response = self.remote_control_client.execute_command("stat memory")
            self.append_mcp_output(f"✓ Memory stats enabled in viewport\n")
        
        else:
            self.append_mcp_output(f"❌ Unknown tool: {tool_name}\n")
    
    except Exception as e:
        self.append_mcp_output(f"❌ Error: {e}\n")
        messagebox.showerror("Tool Error", f"Failed to execute tool:\n{e}")
```

### Step 6: Update Console Command Execution

Update the `execute_mcp_console_command` method (around line 1581):

```python
def execute_mcp_console_command(self):
    """Execute a console command via Remote Control API."""
    if not self.remote_control_connected:
        messagebox.showwarning("Not Connected", "Please connect to Unreal Engine first")
        return
    
    command = self.mcp_console_entry.get().strip()
    if not command:
        messagebox.showwarning("Empty Command", "Please enter a console command")
        return
    
    try:
        self.append_mcp_output(f"\n▶ Executing: {command}\n")
        response = self.remote_control_client.execute_command(command)
        
        if response.success:
            self.append_mcp_output(f"✓ Command executed successfully\n")
            if response.data:
                self.append_mcp_output(f"Output: {response.data}\n")
            else:
                self.append_mcp_output(f"(No output - check UE viewport/console)\n")
        else:
            self.append_mcp_output(f"✗ Command failed: {response.error}\n")
    
    except Exception as e:
        self.append_mcp_output(f"❌ Error: {e}\n")
        messagebox.showerror("Execution Error", f"Failed to execute command:\n{e}")
    
    # Clear the entry
    self.mcp_console_entry.delete(0, tk.END)
```

### Step 7: Test It!

1. **Start Unreal Engine** with Remote Control flags:
   ```bash
   UnrealEditor.exe MyProject.uproject -RCWebControlEnable -RCWebInterfaceEnable
   ```

2. **Run GUI Director**:
   ```bash
   python gui_director.py
   ```

3. **Click the "Unreal MCP" tab**

4. **Click "Connect"** - should see "Successfully connected to Unreal Engine!"

5. **Try tools**:
   - Click "📊 Project Info"
   - Click "🎮 FPS Stats"
   - Type `stat fps` in console and click Execute

**Done!** You now have working Remote Control integration.

---

## VSCode Extension Integration (Option A: Python Proxy)

### Step 1: Add Handler to IPC Server

Add to your Python IPC server (wherever it handles requests):

```python
from remote_control import UnrealRemoteControlClient

# Initialize client once
_remote_control_client = None

def get_remote_control_client():
    """Get or create Remote Control client."""
    global _remote_control_client
    if _remote_control_client is None:
        _remote_control_client = UnrealRemoteControlClient()
    return _remote_control_client

def handle_remote_control_request(request_data):
    """Handle Remote Control requests from VSCode."""
    client = get_remote_control_client()
    action = request_data.get('action')
    
    try:
        if action == 'health_check':
            return {'success': client.health_check()}
        
        elif action == 'execute_command':
            response = client.execute_command(request_data['command'])
            return response.to_dict()
        
        elif action == 'get_property':
            response = client.get_property(
                request_data['object_path'],
                request_data['property_name']
            )
            return response.to_dict()
        
        elif action == 'set_property':
            response = client.set_property(
                request_data['object_path'],
                request_data['property_name'],
                request_data['value']
            )
            return response.to_dict()
        
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

### Step 2: Add Commands to VSCode Extension

Add to `vscode-extension/src/extension.ts`:

```typescript
// Register Remote Control commands
context.subscriptions.push(
    vscode.commands.registerCommand('adastrea-director.unreal.executeCommand', async () => {
        const command = await vscode.window.showInputBox({
            prompt: 'Enter Unreal Engine console command',
            placeHolder: 'stat fps'
        });
        
        if (!command) return;
        
        try {
            const response = await ipcClient.sendRequest({
                type: 'remote_control',
                action: 'execute_command',
                command: command
            });
            
            if (response.success) {
                vscode.window.showInformationMessage(`✓ Executed: ${command}`);
            } else {
                vscode.window.showErrorMessage(`✗ Failed: ${response.error}`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error}`);
        }
    })
);

context.subscriptions.push(
    vscode.commands.registerCommand('adastrea-director.unreal.checkConnection', async () => {
        try {
            const response = await ipcClient.sendRequest({
                type: 'remote_control',
                action: 'health_check'
            });
            
            if (response.success) {
                vscode.window.showInformationMessage('✓ Connected to Unreal Engine');
            } else {
                vscode.window.showWarningMessage('✗ Not connected to Unreal Engine');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Connection check failed: ${error}`);
        }
    })
);
```

### Step 3: Add Commands to package.json

Add to `vscode-extension/package.json` under `contributes.commands`:

```json
{
    "command": "adastrea-director.unreal.executeCommand",
    "title": "Adastrea: Execute Unreal Command",
    "category": "Adastrea Director"
},
{
    "command": "adastrea-director.unreal.checkConnection",
    "title": "Adastrea: Check Unreal Connection",
    "category": "Adastrea Director"
}
```

### Step 4: Test It!

1. **Reload VSCode extension** (F5 in extension development host)
2. **Open Command Palette** (Ctrl+Shift+P)
3. **Run**: "Adastrea: Check Unreal Connection"
4. **Run**: "Adastrea: Execute Unreal Command" → Enter "stat fps"

**Done!** VSCode can now control Unreal Engine.

---

## Troubleshooting

### "Failed to connect"
- Ensure UE is running
- Check Remote Control plugins are enabled (Project Settings → Plugins)
- Verify launch flags: `-RCWebControlEnable -RCWebInterfaceEnable`
- Test in browser: `http://localhost:30010/remote/info`

### "Command returns no output"
- Some commands don't return text (e.g., `stat fps` just shows in viewport)
- Check UE console for errors
- Try simpler commands: `stat fps`, `stat unit`

### "Connection works but commands fail"
- Check command whitelist in `config/remote_control_config.yaml`
- Verify command syntax in UE console first
- Check UE output log for errors

---

## Full Documentation

For complete details, see:
- **[REMOTE_CONTROL_INTEGRATION_STATUS.md](REMOTE_CONTROL_INTEGRATION_STATUS.md)** - Complete integration status and options
- **[remote_control/README.md](remote_control/README.md)** - Remote Control module documentation
- **[examples/remote_control_demo.py](examples/remote_control_demo.py)** - Working examples
- **[config/remote_control_config.yaml](config/remote_control_config.yaml)** - Configuration reference

---

*Quick Integration Guide | Last Updated: 2026-01-05*
