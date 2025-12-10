# VS Code Extension Integration - Quick Start

## Overview

This guide shows how to integrate the new IPC MCP handlers into the VS Code extension to enable Copilot interaction with Unreal Engine.

## Step 1: Update IPC Client

Add helper methods to `vscode-extension/src/ipcClient.ts`:

```typescript
// Add these methods to the IPCClient class

/**
 * Connect to Unreal Engine via MCP
 */
async connectToUnreal(): Promise<{connected: boolean, projectInfo?: any}> {
  const response = await this.sendRequest({
    type: 'mcp_connect',
    data: ''
  });
  
  return {
    connected: response.connected,
    projectInfo: response.project_info
  };
}

/**
 * Disconnect from Unreal Engine
 */
async disconnectFromUnreal(): Promise<void> {
  await this.sendRequest({
    type: 'mcp_disconnect',
    data: ''
  });
}

/**
 * Check MCP connection status
 */
async getMCPStatus(): Promise<{connected: boolean, serverInfo?: any}> {
  const response = await this.sendRequest({
    type: 'mcp_status',
    data: ''
  });
  
  return {
    connected: response.connected,
    serverInfo: response.server_info
  };
}

/**
 * Execute Python code in Unreal Engine
 */
async executeUEPython(code: string): Promise<any> {
  const response = await this.sendRequest({
    type: 'mcp_execute_python',
    data: JSON.stringify({ code })
  });
  
  if (response.status === 'error') {
    throw new Error(response.error);
  }
  
  return response.result;
}

/**
 * Execute console command in Unreal Engine
 */
async executeUEConsoleCommand(command: string): Promise<any> {
  const response = await this.sendRequest({
    type: 'mcp_console_command',
    data: JSON.stringify({ command })
  });
  
  if (response.status === 'error') {
    throw new Error(response.error);
  }
  
  return response.result;
}

/**
 * List available MCP tools
 */
async listMCPTools(): Promise<any[]> {
  const response = await this.sendRequest({
    type: 'mcp_list_tools',
    data: ''
  });
  
  return response.tools || [];
}

/**
 * Call an MCP tool
 */
async callMCPTool(toolName: string, arguments: any = {}): Promise<any> {
  const response = await this.sendRequest({
    type: 'mcp_call_tool',
    data: JSON.stringify({ tool: toolName, arguments })
  });
  
  if (response.status === 'error') {
    throw new Error(response.error);
  }
  
  return response.result;
}

/**
 * Get list of recent UE log files
 */
async getUELogs(limit: number = 10): Promise<any[]> {
  const response = await this.sendRequest({
    type: 'get_ue_logs',
    data: JSON.stringify({ limit })
  });
  
  return response.logs || [];
}

/**
 * Read a specific UE log file
 */
async readUELog(filename: string, maxLines: number = 1000): Promise<string> {
  const response = await this.sendRequest({
    type: 'read_ue_log',
    data: JSON.stringify({ filename, max_lines: maxLines })
  });
  
  if (response.status === 'error') {
    throw new Error(response.error);
  }
  
  return response.content;
}
```

## Step 2: Add New Commands

Update `vscode-extension/package.json`:

```json
{
  "contributes": {
    "commands": [
      // ... existing commands ...
      {
        "command": "director.connectUnreal",
        "title": "Director: Connect to Unreal Engine (MCP)"
      },
      {
        "command": "director.disconnectUnreal",
        "title": "Director: Disconnect from Unreal Engine"
      },
      {
        "command": "director.executeUEPython",
        "title": "Director: Execute Python in Unreal Engine"
      },
      {
        "command": "director.executeUEConsole",
        "title": "Director: Execute Console Command in UE"
      },
      {
        "command": "director.viewUELogs",
        "title": "Director: View UE Logs"
      }
    ]
  }
}
```

## Step 3: Implement Commands

In `vscode-extension/src/extension.ts`:

```typescript
// Register MCP commands
context.subscriptions.push(
  vscode.commands.registerCommand('director.connectUnreal', async () => {
    try {
      const result = await client.connectToUnreal();
      if (result.connected) {
        vscode.window.showInformationMessage('✅ Connected to Unreal Engine');
        outputChannel.appendLine('Connected to Unreal Engine');
        if (result.projectInfo) {
          outputChannel.appendLine(JSON.stringify(result.projectInfo, null, 2));
        }
      } else {
        vscode.window.showErrorMessage('Failed to connect to Unreal Engine');
      }
    } catch (error) {
      vscode.window.showErrorMessage(`Connection error: ${error}`);
    }
  })
);

context.subscriptions.push(
  vscode.commands.registerCommand('director.executeUEPython', async () => {
    const code = await vscode.window.showInputBox({
      prompt: 'Enter Python code to execute in Unreal Engine',
      placeHolder: 'import unreal; print(unreal.SystemLibrary.get_engine_version())'
    });
    
    if (code) {
      try {
        const result = await client.executeUEPython(code);
        outputChannel.appendLine('Python Execution Result:');
        outputChannel.appendLine(JSON.stringify(result, null, 2));
        outputChannel.show();
      } catch (error) {
        vscode.window.showErrorMessage(`Execution error: ${error}`);
      }
    }
  })
);

context.subscriptions.push(
  vscode.commands.registerCommand('director.viewUELogs', async () => {
    try {
      const logs = await client.getUELogs(10);
      
      if (logs.length === 0) {
        vscode.window.showInformationMessage('No UE logs found');
        return;
      }
      
      // Show quick pick to select a log
      const items = logs.map(log => ({
        label: log.filename,
        description: `${(log.size / 1024).toFixed(2)} KB`,
        detail: new Date(log.modified * 1000).toLocaleString(),
        log: log
      }));
      
      const selected = await vscode.window.showQuickPick(items, {
        placeHolder: 'Select a log file to view'
      });
      
      if (selected) {
        // Read and display the log
        const content = await client.readUELog(selected.log.filename);
        const doc = await vscode.workspace.openTextDocument({
          content: content,
          language: 'log'
        });
        await vscode.window.showTextDocument(doc);
      }
    } catch (error) {
      vscode.window.showErrorMessage(`Error viewing logs: ${error}`);
    }
  })
);
```

## Step 4: Update Chat Participant

Update `vscode-extension/src/chatParticipant.ts`:

```typescript
export function registerChatParticipant(context: vscode.ExtensionContext, client: IPCClient) {
  const handler: vscode.ChatRequestHandler = async (
    request: vscode.ChatRequest,
    context: vscode.ChatContext,
    stream: vscode.ChatResponseStream,
    token: vscode.CancellationToken
  ) => {
    // Handle new slash commands
    if (request.command === 'connect-ue') {
      try {
        const result = await client.connectToUnreal();
        if (result.connected) {
          stream.markdown('✅ **Connected to Unreal Engine**\n\n');
          if (result.projectInfo?.info) {
            stream.markdown('```\n' + result.projectInfo.info + '\n```\n');
          }
        } else {
          stream.markdown('❌ Failed to connect to Unreal Engine\n\n');
          stream.markdown('Make sure Unreal Engine is running with Python Remote Execution enabled.\n');
        }
      } catch (error) {
        stream.markdown(`❌ Connection error: ${error}\n`);
      }
      return;
    }
    
    if (request.command === 'exec') {
      // Execute Python in UE
      const code = request.prompt.trim();
      if (!code) {
        stream.markdown('❌ Please provide Python code to execute\n\n');
        stream.markdown('Example: `@director /exec import unreal; print(unreal.SystemLibrary.get_engine_version())`\n');
        return;
      }
      
      try {
        stream.markdown('🔄 Executing Python in Unreal Engine...\n\n');
        const result = await client.executeUEPython(code);
        
        if (result.isError) {
          stream.markdown('❌ **Execution Error**\n\n');
          stream.markdown('```\n' + result.content[0].text + '\n```\n');
        } else {
          stream.markdown('✅ **Result**\n\n');
          stream.markdown('```\n' + result.content[0].text + '\n```\n');
        }
      } catch (error) {
        stream.markdown(`❌ Error: ${error}\n`);
      }
      return;
    }
    
    if (request.command === 'console') {
      // Execute console command
      const command = request.prompt.trim();
      if (!command) {
        stream.markdown('❌ Please provide a console command\n\n');
        stream.markdown('Example: `@director /console stat fps`\n');
        return;
      }
      
      try {
        stream.markdown('🔄 Executing console command...\n\n');
        const result = await client.executeUEConsoleCommand(command);
        
        if (result.isError) {
          stream.markdown('❌ **Error**\n\n');
          stream.markdown('```\n' + result.content[0].text + '\n```\n');
        } else {
          stream.markdown('✅ **Output**\n\n');
          stream.markdown('```\n' + result.content[0].text + '\n```\n');
        }
      } catch (error) {
        stream.markdown(`❌ Error: ${error}\n`);
      }
      return;
    }
    
    if (request.command === 'analyze-logs') {
      // Analyze recent UE logs
      try {
        stream.markdown('🔍 Analyzing recent UE logs...\n\n');
        
        const logs = await client.getUELogs(1);
        if (logs.length === 0) {
          stream.markdown('No logs found. Connect to Unreal Engine and perform some operations first.\n');
          return;
        }
        
        const latestLog = logs[0];
        stream.markdown(`Reading latest log: **${latestLog.filename}**\n\n`);
        
        const content = await client.readUELog(latestLog.filename, 500);
        
        // Use Copilot to analyze the log
        stream.markdown('**Analysis**\n\n');
        
        // Here you would send the log content to an LLM for analysis
        // For now, show basic statistics
        const lines = content.split('\n');
        const errors = lines.filter(l => l.includes('[ERROR]')).length;
        const warnings = lines.filter(l => l.includes('[WARNING]')).length;
        
        stream.markdown(`- Total lines: ${lines.length}\n`);
        stream.markdown(`- Errors: ${errors}\n`);
        stream.markdown(`- Warnings: ${warnings}\n\n`);
        
        if (errors > 0) {
          stream.markdown('**Recent Errors:**\n\n');
          const errorLines = lines.filter(l => l.includes('[ERROR]')).slice(-3);
          stream.markdown('```\n' + errorLines.join('\n') + '\n```\n');
        }
      } catch (error) {
        stream.markdown(`❌ Error: ${error}\n`);
      }
      return;
    }
    
    // ... existing command handling ...
  };
  
  const participant = vscode.chat.createChatParticipant('director', handler);
  participant.iconPath = vscode.Uri.file(
    path.join(context.extensionPath, 'resources', 'icon.png')
  );
  
  // Add new slash commands
  participant.commands = [
    {
      name: 'connect-ue',
      description: 'Connect to Unreal Engine via MCP'
    },
    {
      name: 'exec',
      description: 'Execute Python code in Unreal Engine'
    },
    {
      name: 'console',
      description: 'Execute console command in Unreal Engine'
    },
    {
      name: 'analyze-logs',
      description: 'Analyze recent UE logs for errors and issues'
    },
    // ... existing commands ...
  ];
  
  context.subscriptions.push(participant);
}
```

## Step 5: Test the Integration

### Test MCP Connection

1. Start the IPC server from the repository root:
   ```bash
   python Plugins/AdastreaDirector/Python/ipc_server.py --port 5555
   ```

2. In VS Code, run command:
   ```
   Director: Connect to Unreal Engine (MCP)
   ```

3. Or use Copilot Chat:
   ```
   @director /connect-ue
   ```

### Test Python Execution

In Copilot Chat:
```
@director /exec import unreal; print(unreal.SystemLibrary.get_engine_version())
```

### Test Log Analysis

In Copilot Chat:
```
@director /analyze-logs
```

## Step 6: Update README

Add to `vscode-extension/README.md`:

```markdown
### GitHub Copilot + Unreal Engine Integration

The `@director` chat participant now supports direct interaction with Unreal Engine:

**New Slash Commands:**
- `@director /connect-ue` - Connect to Unreal Engine
- `@director /exec <code>` - Execute Python in UE
- `@director /console <command>` - Run console command
- `@director /analyze-logs` - Analyze recent UE logs

**Example Usage:**
```
@director /connect-ue

@director /exec import unreal
actor_count = len(unreal.EditorLevelLibrary.get_all_level_actors())
print(f"Found {actor_count} actors")

@director /console stat fps

@director /analyze-logs
```

**Requirements:**
- IPC server must be running (`python ipc_server.py --port 5555`)
- Unreal Engine with Python Remote Execution enabled
- GUI log capture creates log files for analysis
```

## Complete Example: UE Log Debugging with Copilot

User workflow:

1. **User runs game in UE, encounters error**

2. **User asks Copilot for help:**
   ```
   @director /analyze-logs
   ```

3. **Copilot reads latest log and responds:**
   ```
   Found 3 errors in the latest log:
   
   1. Blueprint compilation error in BP_PlayerCharacter
   2. Missing texture reference in M_Character_Material
   3. Null pointer access in CustomMovementComponent
   
   Would you like me to help fix these issues?
   ```

4. **User asks for more details:**
   ```
   @director /exec import unreal
   actor = unreal.EditorAssetLibrary.load_asset('/Game/Blueprints/BP_PlayerCharacter')
   print(actor.get_class().get_name())
   ```

5. **Copilot suggests fixes based on log analysis and code inspection**

This creates a seamless debugging workflow where Copilot has access to UE runtime information!

## Troubleshooting

### "Not connected to Unreal Engine"

Make sure:
1. Unreal Engine is running
2. Python Editor Script Plugin is enabled
3. Remote Execution is enabled in Project Settings
4. IPC server is running

### "MCP server not available"

The IPC server couldn't import the mcp_server module. Make sure:
1. You're running from the correct directory
2. The mcp_server module is in the Python path
3. Dependencies are installed

### Logs not found

Make sure:
1. The GUI has been used to connect to UE at least once
2. The logs directory exists
3. Log files have `.log` extension

## Next Steps

- Add more MCP tools to the IPC server
- Implement real-time log streaming
- Add code actions for UE Python snippets
- Create dedicated log viewer UI in VS Code
- Add performance profiling integration
