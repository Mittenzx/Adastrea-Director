# Migration Guide: Legacy IPC to VibeUE Architecture

**Last Updated:** January 2026  
**Status:** Phase 2 - Gradual Cutover

## Overview

This guide helps developers migrate from the legacy IPC-based architecture to the new VibeUE architecture. The VibeUE architecture provides native C++ integration with LLMs, eliminating the need for external Python processes and IPC communication.

## Why Migrate?

### Legacy Architecture Issues
- ❌ External Python process can fail to start
- ❌ IPC connections can drop unexpectedly
- ❌ Python dependency conflicts
- ❌ High latency (~200ms IPC overhead)
- ❌ Complex debugging (multiple processes)
- ❌ Process lifecycle management complexity

### VibeUE Architecture Benefits
- ✅ **Zero IPC latency** - Direct in-process calls
- ✅ **Simplified architecture** - No external processes
- ✅ **Better reliability** - No socket connections to fail
- ✅ **Native C++** - Full Unreal Engine integration
- ✅ **Built-in Python** - Uses Unreal's IPythonScriptPlugin
- ✅ **Runtime discovery** - No document ingestion needed
- ✅ **MCP protocol** - Standard protocol for AI clients

## Migration Timeline

### Phase 1: Completion (✅ Complete)
- VibeUE architecture implemented
- All new components available

### Phase 2: Gradual Cutover (🚧 Current)
- Deprecation warnings added to legacy components
- Both architectures working in parallel
- New features route through VibeUE components
- Documentation updated

### Phase 3: Complete Migration (📅 Future)
- Legacy components removed:
  - `FPythonProcessManager`
  - `FIPCClient`
  - `FPythonBridge`
  - Python IPC server (`ipc_server.py`)
- All code using VibeUE components
- Tests updated

## Component Migration Map

### Python Process Management
**Legacy:** `FPythonProcessManager`  
**VibeUE:** `FAdastreaScriptService`

#### Before (Legacy)
```cpp
// Start external Python process
FPythonProcessManager Manager;
Manager.StartPythonProcess(
    TEXT("python.exe"),
    TEXT("ipc_server.py"),
    5555
);
```

#### After (VibeUE)
```cpp
// Execute Python directly in-process
#include "AdastreaScriptService.h"

FAdastreaScriptResult Result = FAdastreaScriptService::ExecuteCode(
    TEXT("import unreal; print(unreal.SystemLibrary.get_project_directory())")
);

if (Result.bSuccess)
{
    UE_LOG(LogAdastreaDirector, Log, TEXT("Output: %s"), *Result.Output);
}
else
{
    UE_LOG(LogAdastreaDirector, Error, TEXT("Error: %s"), *Result.ErrorMessage);
}
```

### IPC Communication
**Legacy:** `FIPCClient`  
**VibeUE:** `FAdastreaLLMClient`

#### Before (Legacy)
```cpp
// Connect via IPC to Python backend
FIPCClient Client;
Client.Connect(TEXT("127.0.0.1"), 5555);

FString Request = TEXT("{\"type\":\"query\",\"data\":\"What is UE5?\"}");
FString Response;
Client.SendRequest(Request, Response);
```

#### After (VibeUE)
```cpp
// Direct LLM API calls
#include "AdastreaLLMClient.h"

TSharedPtr<FAdastreaLLMClient> Client = MakeShared<FAdastreaLLMClient>();
Client->SetProvider(ELLMProvider::Gemini, TEXT("YOUR_API_KEY"));
Client->SetModel(TEXT("gemini-1.5-flash"));

TArray<FChatMessage> Messages;
FChatMessage UserMsg;
UserMsg.Role = TEXT("user");
UserMsg.Content = TEXT("What is Unreal Engine 5?");
Messages.Add(UserMsg);

Client->SendChatRequest(
    Messages,
    TArray<FToolDefinition>(),
    [](const FString& Chunk) {
        UE_LOG(LogAdastreaDirector, Log, TEXT("Chunk: %s"), *Chunk);
    },
    [](bool bSuccess, const FString& FullResponse) {
        if (bSuccess)
        {
            UE_LOG(LogAdastreaDirector, Log, TEXT("Complete: %s"), *FullResponse);
        }
    }
);
```

### Python Bridge
**Legacy:** `FPythonBridge`  
**VibeUE:** Multiple components depending on use case

#### Before (Legacy)
```cpp
// High-level wrapper for process + IPC
FPythonBridge Bridge;
Bridge.Initialize(
    TEXT("python.exe"),
    TEXT("ipc_server.py"),
    5555
);

FString Response;
Bridge.SendRequest(TEXT("query"), TEXT("question"), Response);
```

#### After (VibeUE)
```cpp
// Use appropriate component for your needs:

// 1. For Python execution:
FAdastreaScriptService::ExecuteCode(TEXT("import unreal; ..."));

// 2. For LLM queries:
TSharedPtr<FAdastreaLLMClient> LLMClient = MakeShared<FAdastreaLLMClient>();
// ... (see LLM example above)

// 3. For asset queries:
TArray<FAssetInfo> Assets = FAdastreaAssetService::SearchAssets(
    TEXT("*Character*"),
    TEXT("Blueprint")
);

// 4. For tool-based AI interactions:
FAdastreaToolSystem::RegisterTool(/* ... */);
```

### Asset Discovery
**Legacy:** Document ingestion + RAG queries  
**VibeUE:** `FAdastreaAssetService`

#### Before (Legacy)
```python
# Python IPC server ingests assets into vector DB
# Then queries via RAG system - slow and complex
```

#### After (VibeUE)
```cpp
// Runtime queries - instant results
#include "AdastreaAssetService.h"

// Search for assets by pattern
TArray<FAssetInfo> Blueprints = FAdastreaAssetService::SearchAssets(
    TEXT("*Player*"),
    TEXT("Blueprint")
);

// Get all assets of a type
TArray<FAssetInfo> AllMaterials = FAdastreaAssetService::GetMaterials();

// Query specific asset
TOptional<FAssetInfo> Asset = FAdastreaAssetService::GetAssetByPath(
    TEXT("/Game/Characters/MyCharacter")
);

// Get as JSON for AI tools
FString JSON = FAdastreaAssetService::GetBlueprintsAsJSON();
```

## MCP Protocol Integration

The new `FAdastreaMCPServer` provides a standard Model Context Protocol server for external AI clients (VS Code, Claude Desktop, etc.).

```cpp
#include "AdastreaMCPServer.h"

// Start MCP server
TSharedPtr<FAdastreaMCPServer> MCPServer = MakeShared<FAdastreaMCPServer>();
MCPServer->Start(8080);

// External clients can now connect and use tools
// Tools are automatically registered from FAdastreaToolSystem
```

## Tool System

The new tool system allows registration of custom capabilities for AI agents.

```cpp
#include "AdastreaToolSystem.h"

// Define a tool
FToolDefinition MyTool;
MyTool.Name = TEXT("my_custom_tool");
MyTool.Description = TEXT("Does something useful");
MyTool.Category = TEXT("utility");

// Add parameters
FToolParameter Param;
Param.Name = TEXT("input");
Param.Type = TEXT("string");
Param.Description = TEXT("Input to process");
Param.bRequired = true;
MyTool.Parameters.Add(Param);

// Register execution handler
FAdastreaToolSystem::RegisterTool(
    MyTool,
    [](const TMap<FString, FString>& Params) -> FString {
        FString Input = Params.FindRef(TEXT("input"));
        // Process input and return JSON result
        return TEXT("{\"result\": \"processed\"}");
    }
);

// Tool is now available to LLM function calling and MCP clients
```

## Step-by-Step Migration Process

### Step 1: Identify Legacy Usage
Search your codebase for:
- `FPythonProcessManager`
- `FIPCClient`
- `FPythonBridge`
- References to `ipc_server.py`

### Step 2: Choose VibeUE Component
Based on what you're doing:
- **Python execution** → `FAdastreaScriptService`
- **LLM queries** → `FAdastreaLLMClient`
- **Asset discovery** → `FAdastreaAssetService`
- **Tool-based AI** → `FAdastreaToolSystem`
- **External AI clients** → `FAdastreaMCPServer`

### Step 3: Update Code
Replace legacy component with appropriate VibeUE component following the examples above.

### Step 4: Test Thoroughly
- Verify functionality matches or exceeds legacy behavior
- Test error handling
- Check performance (should be faster with no IPC)

### Step 5: Remove Legacy References
Once migrated and tested:
- Remove legacy includes
- Remove legacy initialization code
- Update any configuration files

## API Key Configuration

The VibeUE architecture requires direct API keys for LLM providers.

### Setting API Keys

**Option 1: Environment Variables (Recommended)**
```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

**Option 2: Code**
```cpp
Client->SetProvider(ELLMProvider::Gemini, TEXT("your_api_key"));
```

**Option 3: Project Settings**
Add to your project's `Config/DefaultEngine.ini`:
```ini
[/Script/AdastreaDirector.AdastreaDirectorSettings]
GeminiAPIKey=your_gemini_api_key
OpenAIAPIKey=your_openai_api_key
```

## Troubleshooting

### Issue: "Deprecated component warning"
**Solution:** This is expected during Phase 2. Follow this migration guide to switch to VibeUE components.

### Issue: "Python execution not working"
**Solution:** Ensure IPythonScriptPlugin is enabled in your project. Add to `.uproject`:
```json
"Plugins": [
    {
        "Name": "PythonScriptPlugin",
        "Enabled": true
    }
]
```

### Issue: "LLM API calls failing"
**Solution:** 
1. Verify API key is correctly set
2. Check internet connectivity
3. Verify API quota hasn't been exceeded
4. Check provider status page

### Issue: "Asset queries returning nothing"
**Solution:**
1. Ensure Asset Registry is loaded (happens automatically in editor)
2. Verify asset paths are correct (use `/Game/...` format)
3. Check asset class names match exactly

## Testing Checklist

Before removing legacy components:

- [ ] All Python execution migrated to `FAdastreaScriptService`
- [ ] All LLM queries migrated to `FAdastreaLLMClient`
- [ ] All asset queries migrated to `FAdastreaAssetService`
- [ ] No references to `FPythonBridge` remain
- [ ] No references to `FIPCClient` remain
- [ ] No references to `FPythonProcessManager` remain
- [ ] API keys configured and tested
- [ ] Functionality verified in both Editor and Runtime
- [ ] Performance benchmarks show improvement or no regression
- [ ] Error handling tested and robust

## Support Resources

### Documentation
- `VIBEUE_ARCHITECTURE_SUMMARY.md` - Complete architecture overview
- `ARCHITECTURE.md` - System architecture documentation
- `ROADMAP.md` - Project roadmap and phase tracking
- `AdastreaExamples.h` - Code examples for all VibeUE components

### Example Code
- `Plugins/AdastreaDirector/Source/AdastreaDirector/Public/AdastreaExamples.h`
- Contains complete working examples for:
  - Script execution
  - LLM integration
  - Asset discovery
  - Tool system
  - MCP server

### Getting Help
- Check the `TROUBLESHOOTING.md` guide
- Review examples in `AdastreaExamples.h`
- Search documentation for specific component usage
- Check GitHub issues for known problems

## Phase 3 Preparation

Phase 3 will remove all legacy components. To prepare:

1. **Complete Phase 2 Migration** - Migrate all code to VibeUE components
2. **Remove Legacy Initializations** - Clean up any remaining legacy init code
3. **Update Tests** - Ensure all tests use VibeUE components
4. **Update Documentation** - Remove any legacy component references
5. **Verify No Dependencies** - Ensure no external code depends on legacy components

## Migration Timeline

- **January 2026** - Phase 2: Gradual Cutover (Current)
- **Q1 2026** - Phase 2: Continue migration, validate VibeUE stability
- **Q2 2026** - Phase 3: Remove legacy components (Target)

## Feedback

If you encounter issues during migration or have suggestions for this guide:
- Open an issue on GitHub
- Tag with `migration` label
- Provide specific examples of migration challenges

---

**Need Help?** See `TROUBLESHOOTING.md` or open a GitHub issue.
