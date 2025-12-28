# Unreal-Agent Plugin Research and Implementation Recommendations

**Date:** December 19, 2024  
**Source Repository:** https://github.com/TREE-Ind/Unreal-Agent.git  
**Target Repository:** Adastrea Director Plugin

## Executive Summary

This document analyzes the Unreal-Agent (UnrealGPT) plugin to identify valuable features and implementation patterns that can enhance the Adastrea Director plugin. The UnrealGPT plugin is an AI-powered editor copilot for Unreal Engine 5.6 that integrates GPT models with editor capabilities including Python execution, scene understanding, and viewport screenshot capture.

## Key Features Analyzed

### 1. **Scene Understanding & Context Capture**

**What They Do:**
- Capture viewport screenshots and convert to base64 PNG
- Generate JSON scene summaries of actors/components in the current level
- Implement `scene_query` tool for searching actors by class/name/label/component types
- `GetSelectedActorsSummary` for focused summaries of current selection

**Implementation Highlights:**
- Robust viewport screenshot capture with proper error handling (`UnrealGPTSceneContext.cpp`)
- Rendering thread synchronization using `FRenderCommandFence`
- Viewport validation checks before and after rendering flush
- Base64 encoding for easy transmission
- JSON serialization of actor/component data

**Value to Adastrea Director:**
⭐⭐⭐⭐⭐ **CRITICAL** - This enables the AI to "see" and understand the current level state

**Recommendation:**
✅ **IMPLEMENT** - Add scene context capture capabilities to Adastrea Director plugin

### 2. **Voice Input with Whisper API**

**What They Do:**
- Record audio from default input device using `AudioCaptureCore`
- Send audio to OpenAI Whisper API for transcription
- Insert transcribed text into chat input for review before sending
- Visual feedback for recording state (microphone button turns red)

**Implementation Highlights:**
- Custom audio capture using `Audio::FAudioCaptureSynth` (`UnrealGPTVoiceInput.cpp`)
- WAV format conversion for API compatibility
- HTTP request to Whisper transcription endpoint
- Delegates for recording state changes (started/stopped/complete)

**Value to Adastrea Director:**
⭐⭐⭐ **MEDIUM** - Nice-to-have feature for hands-free interaction

**Recommendation:**
🔄 **CONSIDER LATER** - Implement in a future phase after core features are complete

### 3. **Python Helper Utilities for Asset Import**

**What They Do:**
- Helper module `unrealgpt_mcp_import.py` for importing generated content
- Functions to import textures, static meshes, and audio files
- Standardized JSON result format with status, message, and details
- Automatic asset naming from filenames

**Implementation Highlights:**
```python
# Standard result format
result = {
    "status": "ok",
    "message": "Success message",
    "details": {
        "asset_path": "/Game/Path/To/Asset",
        "local_path": "C:/path/to/file"
    }
}
```
- Uses `unreal.AssetImportTask` for batch imports
- Proper error handling with traceback capture
- Support for multiple file formats per content type

**Value to Adastrea Director:**
⭐⭐⭐⭐ **HIGH** - Standardizes asset import workflows

**Recommendation:**
✅ **IMPLEMENT** - Create similar helper utilities in Adastrea Director's Python folder

### 4. **Agent Tool Architecture**

**What They Do:**
- Structured tool definition system with JSON schemas
- Tool execution with result size limits (10KB max)
- Tool call iteration protection (max 25 iterations)
- Tool call signature tracking to prevent duplicate executions
- Sequential tool execution tracking (prevents `python_execute` loops)

**Implementation Highlights:**
```cpp
// Tool result size limiting (UnrealGPTAgentClient.h)
static constexpr int32 MaxToolResultSize = 10000; // ~10KB

// Tool iteration protection
static constexpr int32 MaxToolCallIterations = 25;

// Prevent duplicate tool execution
TSet<FString> ExecutedToolCallSignatures;

// Sequential tool tracking
bool bLastToolWasPythonExecute;
bool bLastSceneQueryFoundResults;
```

**Value to Adastrea Director:**
⭐⭐⭐⭐⭐ **CRITICAL** - Prevents runaway agent loops and excessive API costs

**Recommendation:**
✅ **IMPLEMENT IMMEDIATELY** - Add similar safety guardrails to Adastrea Director

### 5. **Reflection Query Tool**

**What They Do:**
- `reflection_query` tool inspects UClass properties and functions
- Returns JSON schema with:
  - Property names, C++/UE types, and flags
  - Function parameters, return types, and flags
- Helps the model write correct Python against Unreal types

**Value to Adastrea Director:**
⭐⭐⭐⭐ **HIGH** - Enables self-documenting API exploration

**Recommendation:**
✅ **IMPLEMENT** - Add reflection capabilities for better Python code generation

### 6. **Documentation Integration with Vector Store**

**What They Do:**
- `file_search` tool against UE 5.6 Python API vector store
- OpenAI file_search integration
- Local UE Python docs shipped for reference
- `web_search` tool for broader documentation queries

**Value to Adastrea Director:**
⭐⭐⭐ **MEDIUM** - Already have RAG system but could enhance with UE-specific docs

**Recommendation:**
🔄 **ENHANCE EXISTING** - Add UE Python API documentation to existing RAG system

### 7. **Replicate Integration for Content Generation**

**What They Do:**
- Optional `replicate_generate` tool for AI content generation
- Support for images, 3D models, audio, music, speech, and video
- Direct HTTP integration with Replicate API
- Python helpers to import generated content as UE assets

**Value to Adastrea Director:**
⭐⭐ **LOW** - Interesting but not core to current roadmap

**Recommendation:**
❌ **SKIP FOR NOW** - Focus on core agent capabilities first

### 8. **Safety and Guardrails**

**What They Do:**
- Execution timeout for risky/long-running Python code
- Tool result size limits to prevent context overflow
- Tool loop protection with iteration counting
- Detection of task completion to stop unnecessary iterations
- API error handling and retry logic

**Implementation Highlights:**
```cpp
// Safety settings (UUnrealGPTSettings)
- Execution Timeout (seconds)
- Max Context Tokens
- Tool iteration limits
- Result size caps

// Task completion detection
bool DetectTaskCompletion(const TArray<FString>& ToolNames, 
                         const TArray<FString>& ToolResults) const;
```

**Value to Adastrea Director:**
⭐⭐⭐⭐⭐ **CRITICAL** - Essential for production use

**Recommendation:**
✅ **IMPLEMENT IMMEDIATELY** - Add comprehensive safety measures

### 9. **Viewport Screenshot Tool**

**What They Do:**
- Dedicated `viewport_screenshot` tool
- Returns base64 PNG of active viewport
- UI displays screenshot inline in chat history
- Enables visual verification of changes

**Implementation Details:**
- Proper thread synchronization
- Error handling for invalid viewports
- Bitmap validation before encoding
- PNG compression using IImageWrapper

**Value to Adastrea Director:**
⭐⭐⭐⭐⭐ **CRITICAL** - Essential for agent verification

**Recommendation:**
✅ **IMPLEMENT** - Add viewport screenshot capabilities

### 10. **Modern UI/UX Patterns**

**What They Do:**
- Dockable tab interface (`Window → UnrealGPT`)
- Modern AAA-style layout with toolbar
- Color-coded tool call cards in chat history
- Reasoning strip showing agent thinking
- Image attachment support with paperclip icon
- Keyboard shortcuts (`Ctrl+Enter` to send)

**Implementation Highlights:**
- Custom Slate widgets (`SUnrealGPTWidget`)
- Bundled Geist and Geist Mono fonts
- Status indicators with visual feedback
- Clear conversation history button
- Settings access from toolbar

**Value to Adastrea Director:**
⭐⭐⭐⭐ **HIGH** - Professional UX matters for user adoption

**Recommendation:**
✅ **ENHANCE EXISTING** - Adopt UI patterns in Adastrea Director plugin

## Features Already Present in Adastrea Director

### ✅ **Already Implemented**
1. **Python Execution** - Already have Python backend integration
2. **RAG System** - Comprehensive document understanding
3. **Planning System** - Goal decomposition and task planning
4. **Remote Control API** - HTTP/WebSocket/IPC integration
5. **Agent Orchestration** - Multi-agent system with event bus
6. **MCP Server** - AI agent access to Unreal Engine
7. **Settings Dialog** - Configuration UI in plugin
8. **IPC Client** - Communication with Python backend

### 🔄 **Partially Implemented (Can Be Enhanced)**
1. **Scene Queries** - Have basic actor queries, can add screenshot
2. **Python Helpers** - Have some helpers, can standardize format
3. **Documentation Search** - Have RAG, can add UE-specific docs
4. **UI/UX** - Have basic UI, can add more polish

## Priority Implementation Recommendations

### **Phase 1: Critical Safety Features** (Week 1-2)

**Priority:** 🔴 **CRITICAL**

1. **Add Tool Execution Guardrails**
   - Implement tool iteration counter (max 25)
   - Add tool result size limiting (10KB)
   - Track executed tool signatures
   - Prevent python_execute loops
   - Add execution timeouts

**Files to Create/Modify:**
- `Plugins/AdastreaDirector/Source/AdastreaDirector/Public/ToolExecutionGuard.h`
- `Plugins/AdastreaDirector/Source/AdastreaDirector/Private/ToolExecutionGuard.cpp`
- Update `PythonBridge.cpp` to use guards

2. **Task Completion Detection**
   - Detect when agent has completed task
   - Stop unnecessary tool iterations
   - Save API costs

**Implementation:**
```cpp
bool DetectTaskCompletion(const TArray<FString>& ToolNames, 
                         const TArray<FString>& ToolResults);
```

### **Phase 2: Scene Understanding** (Week 3-4)

**Priority:** 🟠 **HIGH**

1. **Viewport Screenshot Capture**
   - Implement safe viewport capture with FRenderCommandFence
   - Base64 encoding
   - Add to tool list
   - Display in UI

**Files to Create:**
- `Plugins/AdastreaDirector/Source/AdastreaDirector/Public/SceneContextCapture.h`
- `Plugins/AdastreaDirector/Source/AdastreaDirector/Private/SceneContextCapture.cpp`

2. **Scene Query Tool**
   - Filter actors by class/name/label/components
   - JSON serialization of actor data
   - Pagination support

3. **Selected Actors Summary**
   - Quick context for current selection
   - Useful for focused operations

### **Phase 3: Python Utilities** (Week 5)

**Priority:** 🟡 **MEDIUM-HIGH**

1. **Standardized Asset Import Helpers**
   - Create `Plugins/AdastreaDirector/Python/adastrea_helpers.py`
   - Functions for texture, mesh, audio import
   - Standard result format (status, message, details)
   - Error handling with tracebacks

2. **Reflection Query Utility**
   - UClass property/function inspection
   - JSON schema generation
   - Help AI generate correct code

**Example:**
```python
def import_texture(file_path, target_folder, asset_name=None):
    """Import texture with standardized result format."""
    result = {
        "status": "ok",
        "message": "",
        "details": {}
    }
    try:
        # Import logic
        result["details"]["asset_path"] = asset_path
    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
        result["details"]["traceback"] = traceback.format_exc()
    return result
```

### **Phase 4: UI Enhancements** (Week 6)

**Priority:** 🟢 **MEDIUM**

1. **Tool Call Visualization**
   - Color-coded cards for different tool types
   - Inline screenshot display
   - Reasoning strip

2. **Keyboard Shortcuts**
   - `Ctrl+Enter` to send
   - Quick access to common functions

3. **Status Indicators**
   - Visual feedback for operations
   - Recording state (for future voice input)

### **Phase 5: Future Enhancements** (Later)

**Priority:** 🔵 **LOW**

1. **Voice Input** (Phase 3.5+)
   - Audio capture
   - Whisper API integration
   - Transcription UI

2. **UE Python API Documentation** (Enhancement)
   - Add to RAG system
   - Vector store integration

3. **Web Search Tool** (Optional)
   - For broader queries
   - External documentation

## Implementation Strategy

### **Minimal Change Approach**

For each feature, we'll:
1. Create focused, single-purpose modules
2. Add tests for new functionality
3. Update existing code minimally
4. Maintain backward compatibility

### **File Organization**

```
Plugins/AdastreaDirector/
├── Source/AdastreaDirector/
│   ├── Public/
│   │   ├── ToolExecutionGuard.h        [NEW]
│   │   ├── SceneContextCapture.h       [NEW]
│   │   └── ReflectionQuery.h           [NEW]
│   └── Private/
│       ├── ToolExecutionGuard.cpp      [NEW]
│       ├── SceneContextCapture.cpp     [NEW]
│       └── ReflectionQuery.cpp         [NEW]
├── Python/
│   └── adastrea_helpers.py             [NEW]
└── Content/
    └── UI/
        └── Icons/                       [NEW]
```

### **Testing Approach**

Each feature will include:
1. Unit tests for core functionality
2. Integration tests with existing systems
3. Manual testing checklist
4. Performance benchmarks (especially for screenshot capture)

## Code Examples

### **Example 1: Tool Execution Guard**

```cpp
// ToolExecutionGuard.h
#pragma once

#include "CoreMinimal.h"

class ADASTREADIRECTOR_API FToolExecutionGuard
{
public:
    FToolExecutionGuard();

    // Check if tool can be executed
    bool CanExecuteTool(const FString& ToolName, const FString& Arguments);

    // Record tool execution
    void RecordExecution(const FString& ToolName, const FString& Arguments, const FString& Result);

    // Reset for new conversation
    void Reset();

    // Check if iteration limit reached
    bool HasReachedIterationLimit() const;

    // Truncate large results
    FString TruncateResult(const FString& Result) const;

private:
    static constexpr int32 MaxIterations = 25;
    static constexpr int32 MaxResultSize = 10000;

    int32 IterationCount;
    TSet<FString> ExecutedSignatures;
    bool bLastToolWasPython;
    bool bTaskCompleted;
};
```

### **Example 2: Scene Context Capture**

```cpp
// SceneContextCapture.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "SceneContextCapture.generated.h"

UCLASS()
class ADASTREADIRECTOR_API USceneContextCapture : public UObject
{
    GENERATED_BODY()

public:
    // Capture viewport screenshot as base64 PNG
    static FString CaptureViewportScreenshot();

    // Get JSON scene summary
    static FString GetSceneSummary(int32 PageSize = 100);

    // Query scene with filters
    static FString QueryScene(const FString& FiltersJson);

    // Get selected actors summary
    static FString GetSelectedActorsSummary();

private:
    static bool CaptureViewportToImage(TArray<uint8>& OutImageData, 
                                      int32& OutWidth, 
                                      int32& OutHeight);
    
    static TSharedPtr<FJsonObject> SerializeActor(AActor* Actor);
};
```

### **Example 3: Python Helper**

```python
# adastrea_helpers.py
import unreal
import json
import os
import traceback

def standardized_result(status="ok", message="", **details):
    """Create standardized result dictionary."""
    return {
        "status": status,
        "message": message,
        "details": details
    }

def import_texture(file_path, target_folder="/Game/Textures", asset_name=None):
    """Import texture file as Texture2D asset."""
    try:
        if not os.path.exists(file_path):
            return standardized_result("error", f"File not found: {file_path}")
        
        if not asset_name:
            asset_name = os.path.splitext(os.path.basename(file_path))[0]
        
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        import_task = unreal.AssetImportTask()
        import_task.filename = file_path
        import_task.destination_path = target_folder
        import_task.destination_name = asset_name
        import_task.replace_existing = True
        import_task.automated = True
        import_task.save = True
        
        asset_tools.import_asset_tasks([import_task])
        
        if import_task.imported_object_paths:
            asset_path = import_task.imported_object_paths[0]
            return standardized_result(
                "ok",
                f"Successfully imported texture: {asset_path}",
                asset_path=asset_path,
                local_path=file_path
            )
        else:
            return standardized_result("error", "Import task completed but no asset was created")
    
    except Exception as e:
        return standardized_result(
            "error",
            str(e),
            traceback=traceback.format_exc()
        )

def reflect_class(class_name):
    """Inspect UClass properties and functions."""
    try:
        uclass = unreal.load_class(None, class_name)
        if not uclass:
            return standardized_result("error", f"Class not found: {class_name}")
        
        properties = []
        for prop in uclass.get_properties():
            properties.append({
                "name": prop.get_name(),
                "type": prop.get_class().get_name(),
                "flags": str(prop.get_editor_property("property_flags"))
            })
        
        functions = []
        for func in uclass.get_functions():
            functions.append({
                "name": func.get_name(),
                "return_type": func.get_return_property().get_class().get_name() if func.get_return_property() else "void"
            })
        
        return standardized_result(
            "ok",
            f"Reflected class: {class_name}",
            class_name=class_name,
            properties=properties,
            functions=functions
        )
    
    except Exception as e:
        return standardized_result(
            "error",
            str(e),
            traceback=traceback.format_exc()
        )
```

## Success Metrics

### **Phase 1 Success Criteria**
- ✅ Tool execution guards prevent infinite loops
- ✅ API costs reduced by 50% through early termination
- ✅ No crashes from runaway agents
- ✅ All safety tests passing

### **Phase 2 Success Criteria**
- ✅ Screenshot capture works reliably (99% success rate)
- ✅ Scene queries return accurate data
- ✅ Agent can verify its own work
- ✅ Performance: Screenshot capture <500ms

### **Phase 3 Success Criteria**
- ✅ Asset import success rate >95%
- ✅ Standardized error reporting
- ✅ Reflection tool helps AI write correct code
- ✅ Python helper tests all passing

### **Phase 4 Success Criteria**
- ✅ UI feels responsive and professional
- ✅ Tool calls clearly visualized
- ✅ User satisfaction improved

## Risk Assessment

### **High Risk Items**
1. **Viewport Screenshot Capture**
   - **Risk:** Crashes during rendering thread access
   - **Mitigation:** Use FRenderCommandFence, extensive validation
   - **Testing:** Stress test with multiple rapid captures

2. **Tool Execution Loops**
   - **Risk:** Agent gets stuck in infinite loops
   - **Mitigation:** Multiple layers of protection (iteration count, signatures, task completion detection)
   - **Testing:** Simulate problematic scenarios

### **Medium Risk Items**
1. **Performance Impact**
   - **Risk:** Screenshot capture slows editor
   - **Mitigation:** Async operations where possible
   - **Testing:** Performance benchmarks

2. **Memory Usage**
   - **Risk:** Large screenshots consume memory
   - **Mitigation:** Result size limits, compression
   - **Testing:** Memory profiling

### **Low Risk Items**
1. **Python Helpers**
   - **Risk:** Import failures
   - **Mitigation:** Comprehensive error handling
   - **Testing:** Test with various file types

## Conclusion

The Unreal-Agent plugin provides excellent examples of:
1. **Safety-first design** - Multiple layers of protection
2. **Scene understanding** - Critical for agent autonomy
3. **Standardization** - Consistent patterns across features
4. **Professional UX** - Modern, polished interface

### **Key Takeaways**

1. **Safety is paramount** - Implement guardrails before adding powerful features
2. **Visual feedback matters** - Screenshot capture enables agent verification
3. **Standardization helps** - Consistent result formats reduce errors
4. **Start simple** - Focus on high-value features first

### **Recommended Next Steps**

1. ✅ Implement Phase 1 (Safety guardrails) immediately
2. ✅ Add Phase 2 (Scene understanding) for agent verification
3. ✅ Create Phase 3 (Python utilities) for better integration
4. 🔄 Enhance Phase 4 (UI/UX) gradually
5. 🔵 Consider Phase 5 (Future features) after core is solid

This research provides a solid foundation for enhancing Adastrea Director with proven patterns from a production-quality AI agent plugin.

---

**Document Version:** 1.0  
**Last Updated:** December 19, 2024  
**Author:** GitHub Copilot  
**Status:** ✅ Complete
