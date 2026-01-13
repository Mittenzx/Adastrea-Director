# VibeUE Implementation Guide for Adastrea-Director

## Purpose

This document provides concrete, actionable implementation guidance for adopting VibeUE patterns in Adastrea-Director. Each section includes code examples, step-by-step instructions, and specific files to create or modify.

**🎯 What's New in This Guide:**

This comprehensive guide has been enhanced with:
- ✅ **Complete OpenAI API Implementation** - Full GPT model support alongside Gemini
- ✅ **Tool System Architecture** - Complete tool registration, execution, and management system
- ✅ **MCP Protocol Integration** - Standard protocol support for external AI clients
- ✅ **Performance Optimization** - HTTP pooling, caching, and streaming best practices
- ✅ **Detailed Migration Path** - Week-by-week roadmap with backwards compatibility
- ✅ **Best Practices & Patterns** - TResult<T>, async operations, RAII resource management
- ✅ **Extensive References** - VibeUE source files, UE docs, LLM APIs, and design patterns
- ✅ **Extended Troubleshooting** - Solutions for common HTTP, asset, and Python issues

**📊 Guide Statistics:**
- **2,929 lines** of comprehensive implementation guidance
- **13 major sections** covering all aspects of migration
- **50+ code examples** ready to use in your project
- **6 troubleshooting solutions** for common issues

**⏱️ Estimated Implementation Time:**
- **Phase 1 (Python):** 1 week
- **Phase 2 (LLM Client):** 2-3 weeks  
- **Phase 3 (Asset Discovery):** 1 week
- **Phase 4 (Cleanup):** 1 week
- **Total:** 5-6 weeks for full migration

**🎓 Who Should Read This:**
- C++ developers working on Adastrea-Director
- Engineers planning the VibeUE migration
- Anyone implementing LLM integration in Unreal Engine
- Teams wanting to learn from VibeUE's proven patterns

**🚀 Quick Start:**
- **New to the guide?** Start with [Section 1: Setting Up IPythonScriptPlugin](#1-setting-up-ipythonscriptplugin)
- **Need LLM integration?** Jump to [Section 2: Direct C++ LLM Client](#2-direct-c-llm-client)
- **Building tools?** See [Section 4: Tool System Architecture](#4-tool-system-architecture)
- **Planning migration?** Check [Section 10: Migration from Current Architecture](#10-migration-from-current-architecture)
- **Troubleshooting?** Go to [Section 8: Common Pitfalls](#8-common-pitfalls--solutions) or [Section 13: Extended Troubleshooting](#13-troubleshooting-extended)

## Table of Contents

1. [Setting Up IPythonScriptPlugin](#1-setting-up-ipythonscriptplugin)
   - [Overview](#overview)
   - [Step 1: Update Plugin Dependencies](#step-1-update-plugin-dependencies)
   - [Step 2: Add Module Dependency](#step-2-add-module-dependency)
   - [Step 3: Create Python Execution Service](#step-3-create-python-execution-service)
   - [Step 4: Test Python Execution](#step-4-test-python-execution)
   - [Step 5: Security Considerations](#step-5-security-considerations-for-python-execution)

2. [Direct C++ LLM Client](#2-direct-c-llm-client)
   - [Overview](#overview-1)
   - [Step 1: Add HTTP Module Dependency](#step-1-add-http-module-dependency)
   - [Step 2: Create LLM Client Interface](#step-2-create-llm-client-interface)
   - [Step 3: Implement Gemini API Client](#step-3-implement-gemini-api-client)
   - [Step 4: Implement OpenAI API Client](#step-4-implement-openai-api-client)
   - [Step 5: Test LLM Client](#step-5-test-llm-client)

3. [Runtime Asset Discovery](#3-runtime-asset-discovery)
   - [Overview](#overview-2)
   - [Step 1: Create Asset Discovery Service](#step-1-create-asset-discovery-service)
   - [Step 2: Expose as Tool](#step-2-expose-as-tool)

4. [Tool System Architecture](#4-tool-system-architecture)
   - [Overview](#overview-3)
   - [Tool Definition Structure](#tool-definition-structure)
   - [Tool Execution System](#tool-execution-system)
   - [Built-in Tools](#built-in-tools)

5. [MCP Protocol Integration](#5-mcp-protocol-integration)
   - [Overview](#overview-4)
   - [MCP Server Implementation](#mcp-server-implementation)
   - [External Client Support](#external-client-support)

6. [Quick Migration Checklist](#6-quick-migration-checklist)
   - [Phase 1: Remove Python Process](#phase-1-remove-python-process-week-1)
   - [Phase 2: Direct LLM Integration](#phase-2-direct-llm-integration-weeks-2-3)
   - [Phase 3: Runtime Discovery](#phase-3-runtime-discovery-week-4)
   - [Phase 4: Clean Up](#phase-4-clean-up-week-5)

7. [Testing Strategy](#7-testing-strategy)
   - [Unit Tests](#unit-tests)
   - [Integration Tests](#integration-tests)

8. [Common Pitfalls & Solutions](#8-common-pitfalls--solutions)
   - [Pitfall 1: Python Plugin Not Loaded](#pitfall-1-python-plugin-not-loaded)
   - [Pitfall 2: Asset Registry Not Ready](#pitfall-2-asset-registry-not-ready)
   - [Pitfall 3: JSON Parsing Errors](#pitfall-3-json-parsing-errors)

9. [Performance Optimization](#9-performance-optimization)
   - [HTTP Request Pooling](#http-request-pooling)
   - [Asset Registry Caching](#asset-registry-caching)
   - [Streaming Response Handling](#streaming-response-handling)

10. [Migration from Current Architecture](#10-migration-from-current-architecture)
    - [Step-by-Step Migration Path](#step-by-step-migration-path)
    - [Backwards Compatibility](#backwards-compatibility)
    - [Testing During Migration](#testing-during-migration)

11. [Best Practices & Design Patterns](#11-best-practices--design-patterns)
    - [Error Handling](#error-handling)
    - [Async Operations](#async-operations)
    - [Resource Management](#resource-management)

12. [Reference Materials](#12-reference-materials)
    - [VibeUE Source Files](#vibeue-source-files)
    - [Unreal Engine Documentation](#unreal-engine-documentation)
    - [Additional Resources](#additional-resources)

13. [Troubleshooting Extended](#13-troubleshooting-extended)
    - [HTTP Requests Timing Out](#issue-http-requests-timing-out)
    - [Asset Registry Returns Stale Data](#issue-asset-registry-returns-stale-data)
    - [Python Execution Fails Silently](#issue-python-execution-fails-silently)

---

## 1. Setting Up IPythonScriptPlugin

### Overview

Replace the external Python process with Unreal's built-in Python plugin.

### Step 1: Update Plugin Dependencies

**File:** `Plugins/AdastreaDirector/AdastreaDirector.uplugin`

```json
{
  "FileVersion": 3,
  "Version": 1,
  "VersionName": "1.0",
  "FriendlyName": "Adastrea Director",
  "Plugins": [
    {
      "Name": "PythonScriptPlugin",
      "Enabled": true
    }
  ]
}
```

### Step 2: Add Module Dependency

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/AdastreaDirector.Build.cs`

```csharp
PublicDependencyModuleNames.AddRange(
    new string[]
    {
        "Core",
        "CoreUObject",
        "Engine",
        "Slate",
        "SlateCore",
        "PythonScriptPlugin"  // ADD THIS
    }
);
```

### Step 3: Create Python Execution Service

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/Public/AdastreaScriptService.h`

```cpp
// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "IPythonScriptPlugin.h"
#include "PythonScriptTypes.h"

struct FAdastreaScriptResult
{
    bool bSuccess = false;
    FString Output;
    FString ErrorMessage;
    float ExecutionTimeMs = 0.0f;
};

/**
 * Service for executing Python code in Unreal Engine using IPythonScriptPlugin
 * 
 * ⚠️ SECURITY WARNING:
 * This service executes arbitrary Python code directly in the Unreal Editor process.
 * Never execute untrusted code, including LLM-generated code, without human review.
 * 
 * Recommended safety measures:
 * 1. Require explicit user confirmation before executing any LLM-generated Python
 * 2. Implement a whitelist of allowed operations/modules
 * 3. Display the code to the user for review before execution
 * 4. Consider sandboxing or running in a restricted environment
 * 5. Validate and sanitize all inputs
 * 
 * See "Security Considerations" section below for detailed mitigation strategies.
 */
class ADASTREADIRECTOR_API FAdastreaScriptService
{
public:
    /**
     * Execute Python code
     * @param Code Python code to execute
     * @param bPrivateScope If true, uses isolated scope. If false, uses shared console state
     * @return Execution result with output and errors
     */
    static FAdastreaScriptResult ExecuteCode(
        const FString& Code,
        bool bPrivateScope = true
    );

    /**
     * Evaluate a Python expression and return the result
     * @param Expression Single Python expression (e.g., "2 + 2")
     * @return Execution result with expression value
     */
    static FAdastreaScriptResult EvaluateExpression(const FString& Expression);

    /**
     * Check if Python is available
     * @return True if Python plugin is initialized and ready
     */
    static bool IsPythonAvailable();

    /**
     * Get Python version and information
     * @return Python version string
     */
    static FString GetPythonInfo();

private:
    static FAdastreaScriptResult ConvertResult(
        const FPythonCommandEx& CommandEx,
        float ExecutionTimeMs,
        bool bExecutionSuccess
    );
};
```

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/Private/AdastreaScriptService.cpp`

```cpp
// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "AdastreaScriptService.h"
#include "AdastreaDirectorModule.h"
#include "Misc/DateTime.h"

FAdastreaScriptResult FAdastreaScriptService::ExecuteCode(
    const FString& Code,
    bool bPrivateScope)
{
    if (!IsPythonAvailable())
    {
        FAdastreaScriptResult Result;
        Result.bSuccess = false;
        Result.ErrorMessage = TEXT("Python plugin is not available");
        return Result;
    }

    IPythonScriptPlugin* PythonPlugin = IPythonScriptPlugin::Get();
    
    // Setup command
    FPythonCommandEx Command;
    Command.Command = Code;
    Command.ExecutionMode = EPythonCommandExecutionMode::ExecuteFile;
    Command.FileExecutionScope = bPrivateScope 
        ? EPythonFileExecutionScope::Private 
        : EPythonFileExecutionScope::Public;

    // Execute with timing
    double StartTime = FPlatformTime::Seconds();
    bool bSuccess = PythonPlugin->ExecPythonCommandEx(Command);
    double ExecutionTimeMs = (FPlatformTime::Seconds() - StartTime) * 1000.0;

    return ConvertResult(Command, ExecutionTimeMs, bSuccess);
}

FAdastreaScriptResult FAdastreaScriptService::EvaluateExpression(const FString& Expression)
{
    if (!IsPythonAvailable())
    {
        FAdastreaScriptResult Result;
        Result.bSuccess = false;
        Result.ErrorMessage = TEXT("Python plugin is not available");
        return Result;
    }

    IPythonScriptPlugin* PythonPlugin = IPythonScriptPlugin::Get();
    
    FPythonCommandEx Command;
    Command.Command = Expression;
    Command.ExecutionMode = EPythonCommandExecutionMode::EvaluateStatement;

    double StartTime = FPlatformTime::Seconds();
    bool bSuccess = PythonPlugin->ExecPythonCommandEx(Command);
    double ExecutionTimeMs = (FPlatformTime::Seconds() - StartTime) * 1000.0;

    return ConvertResult(Command, ExecutionTimeMs, bSuccess);
}

bool FAdastreaScriptService::IsPythonAvailable()
{
    return IPythonScriptPlugin::Get() != nullptr;
}

FString FAdastreaScriptService::GetPythonInfo()
{
    if (!IsPythonAvailable())
    {
        return TEXT("Python not available");
    }

    IPythonScriptPlugin* PythonPlugin = IPythonScriptPlugin::Get();
    
    // Execute version check
    FPythonCommandEx Command;
    Command.Command = TEXT("import sys; print(f'Python {sys.version}')");
    Command.ExecutionMode = EPythonCommandExecutionMode::ExecuteFile;
    
    if (PythonPlugin->ExecPythonCommandEx(Command))
    {
        FString Output = Command.CommandResult;
        Output.TrimStartAndEndInline();
        return Output;
    }
    
    return TEXT("Unable to get Python version");
}

FAdastreaScriptResult FAdastreaScriptService::ConvertResult(
    const FPythonCommandEx& CommandEx,
    float ExecutionTimeMs,
    bool bExecutionSuccess)
{
    FAdastreaScriptResult Result;
    Result.Output = CommandEx.CommandResult;
    Result.ExecutionTimeMs = ExecutionTimeMs;

    // Extract error messages and detect error entries
    bool bHasError = false;
    for (const FPythonLogOutputEntry& Entry : CommandEx.LogOutput)
    {
        if (Entry.Type == EPythonLogOutputType::Error)
        {
            bHasError = true;
            Result.ErrorMessage += Entry.Output + TEXT("\n");
        }
    }

    Result.ErrorMessage.TrimEndInline();

    // Success if the Python command executed successfully and there are no error log entries,
    // regardless of whether any output was produced.
    Result.bSuccess = bExecutionSuccess && !bHasError;

    return Result;
}
```

### Step 4: Test Python Execution

Create a test function to verify the Python execution service works correctly.

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/Private/AdastreaScriptService.cpp` (add test function)

```cpp
// Test command to verify Python works
#include "EditorUtilitySubsystem.h"

void TestPythonExecution()
{
    // Test 1: Simple expression
    FAdastreaScriptResult Result1 = FAdastreaScriptService::EvaluateExpression(TEXT("2 + 2"));
    UE_LOG(LogAdastreaDirector, Log, TEXT("2 + 2 = %s"), *Result1.Output);

    // Test 2: Access Unreal module
    FString Code = TEXT(R"(
import unreal
editor_util = unreal.EditorUtilityLibrary()
assets = editor_util.get_selected_assets()
print(f'Selected {len(assets)} assets')
for asset in assets:
    print(f'  - {asset.get_name()}')
)");
    
    FAdastreaScriptResult Result2 = FAdastreaScriptService::ExecuteCode(Code);
    UE_LOG(LogAdastreaDirector, Log, TEXT("Unreal access result:\n%s"), *Result2.Output);

    // Test 3: Error handling
    FAdastreaScriptResult Result3 = FAdastreaScriptService::ExecuteCode(TEXT("1 / 0"));
    if (!Result3.bSuccess)
    {
        UE_LOG(LogAdastreaDirector, Warning, TEXT("Expected error: %s"), *Result3.ErrorMessage);
    }
}
```

**To test from Blueprint or Editor:**

Create an Editor Utility Widget or Blueprint function that calls this test:

```cpp
// In a Blueprint-callable function library
UFUNCTION(BlueprintCallable, Category = "Adastrea|Testing")
static void RunPythonTests()
{
    TestPythonExecution();
}
```

### Step 5: Security Considerations for Python Execution

**⚠️ CRITICAL SECURITY WARNING**

Executing arbitrary Python code (especially LLM-generated code) poses significant security risks:

**Risks:**
- Arbitrary code execution in the Unreal Editor process
- Access to local files, environment variables, and network
- Ability to modify or delete project assets
- Potential for lateral movement on developer machine

**Mitigation Strategies:**

1. **Never Auto-Execute LLM-Generated Code**
   ```cpp
   // ❌ DANGEROUS - Don't do this
   FString LLMCode = GetCodeFromLLM();
   FAdastreaScriptService::ExecuteCode(LLMCode);
   
   // ✅ SAFE - Require human confirmation
   FString LLMCode = GetCodeFromLLM();
   if (ShowCodeReviewDialog(LLMCode) == EUserChoice::Approve)
   {
       FAdastreaScriptService::ExecuteCode(LLMCode);
   }
   ```

2. **Implement Whitelist System**
   ```cpp
   class FPythonWhitelist
   {
   public:
       static bool IsOperationAllowed(const FString& Code)
       {
           // Only allow specific safe operations
           static const TArray<FString> AllowedModules = {
               TEXT("unreal"),
               TEXT("math"),
               TEXT("json")
           };
           
           // Block dangerous operations
           static const TArray<FString> BlockedPatterns = {
               TEXT("os.system"),
               TEXT("subprocess"),
               TEXT("open("),
               TEXT("__import__"),
               TEXT("eval("),
               TEXT("exec(")
           };
           
           for (const FString& Blocked : BlockedPatterns)
           {
               if (Code.Contains(Blocked))
               {
                   return false;
               }
           }
           
           return true;
       }
   };
   ```

3. **Constrained API Surface**
   ```cpp
   // Instead of free-form Python, provide parameterized operations
   class FSafeAssetOperations
   {
   public:
       static TArray<FString> GetAssetNames(const FString& ClassFilter);
       static bool RenameAsset(const FString& OldPath, const FString& NewPath);
       // ... other safe, validated operations
   };
   ```

4. **Display Code Before Execution**
   - Show the Python code in a UI dialog
   - Highlight potentially dangerous operations
   - Require explicit user approval
   - Log all executed code for audit

5. **Sandboxing (Advanced)**
   - Consider running Python in a restricted environment
   - Limit file system access
   - Restrict network operations
   - Use Python's `RestrictedPython` module

**Recommended Implementation:**
```cpp
FAdastreaScriptResult SafeExecuteCode(const FString& Code, bool bRequireApproval = true)
{
    // 1. Validate code
    if (!FPythonWhitelist::IsOperationAllowed(Code))
    {
        FAdastreaScriptResult Result;
        Result.bSuccess = false;
        Result.ErrorMessage = TEXT("Code contains blocked operations");
        return Result;
    }
    
    // 2. Get user approval if required
    if (bRequireApproval)
    {
        if (!ShowPythonExecutionDialog(Code))
        {
            FAdastreaScriptResult Result;
            Result.bSuccess = false;
            Result.ErrorMessage = TEXT("User rejected code execution");
            return Result;
        }
    }
    
    // 3. Log execution for audit
    UE_LOG(LogAdastreaDirector, Warning, TEXT("Executing Python code: %s"), *Code);
    
    // 4. Execute
    return FAdastreaScriptService::ExecuteCode(Code);
}
```

**Best Practice:** Design your system to use parameterized operations instead of free-form code execution wherever possible.

---

## 2. Direct C++ LLM Client

### Overview

Create a C++ HTTP client for direct LLM API communication without Python intermediary.

### Step 1: Add HTTP Module Dependency

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/AdastreaDirector.Build.cs`

```csharp
PublicDependencyModuleNames.AddRange(
    new string[]
    {
        "Core",
        "CoreUObject",
        "Engine",
        "HTTP",            // ADD THIS
        "Json",            // ADD THIS
        "JsonUtilities"    // ADD THIS
    }
);
```

### Step 2: Create LLM Client Interface

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/Public/AdastreaLLMClient.h`

```cpp
// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Interfaces/IHttpRequest.h"
#include "Interfaces/IHttpResponse.h"

/**
 * Chat message structure
 */
struct FChatMessage
{
    FString Role;      // "system", "user", "assistant", "tool"
    FString Content;
    FString ToolCallId; // For tool responses
    
    TSharedPtr<FJsonObject> ToJson() const;
    static FChatMessage FromJson(const TSharedPtr<FJsonObject>& Json);
};

/**
 * Tool call from LLM
 */
struct FToolCall
{
    FString Id;
    FString ToolName;
    TSharedPtr<FJsonObject> Arguments;
    
    static FToolCall FromJson(const TSharedPtr<FJsonObject>& Json);
};

/**
 * Tool definition
 */
struct FToolDefinition
{
    FString Name;
    FString Description;
    TSharedPtr<FJsonObject> Parameters;
    
    TSharedPtr<FJsonObject> ToJson() const;
};

/**
 * Streaming callback for incremental responses
 */
DECLARE_DELEGATE_OneParam(FOnStreamChunk, const FString& /* Chunk */);

/**
 * Completion callback
 */
DECLARE_DELEGATE_ThreeParams(FOnLLMComplete, bool /* bSuccess */, const FString& /* Content */, const TArray<FToolCall>& /* ToolCalls */);

/**
 * LLM Provider types
 */
enum class ELLMProvider : uint8
{
    Gemini,
    OpenAI
};

/**
 * Direct C++ client for LLM APIs (Gemini, OpenAI)
 * 
 * Note: This class should inherit from TSharedFromThis<FAdastreaLLMClient>
 * to safely use weak pointers in async callbacks.
 */
class ADASTREADIRECTOR_API FAdastreaLLMClient : public TSharedFromThis<FAdastreaLLMClient>
{
public:
    FAdastreaLLMClient();
    ~FAdastreaLLMClient();

    /**
     * Send a chat completion request
     * @param Messages Conversation history
     * @param Tools Available tools
     * @param OnStreamChunk Called for each streamed chunk (optional)
     * @param OnComplete Called when request completes
     */
    void SendChatRequest(
        const TArray<FChatMessage>& Messages,
        const TArray<FToolDefinition>& Tools,
        FOnStreamChunk OnStreamChunk,
        FOnLLMComplete OnComplete
    );

    /**
     * Set API provider and key
     */
    void SetProvider(ELLMProvider Provider, const FString& ApiKey);

    /**
     * Set model name (e.g., "gemini-1.5-flash", "gpt-4")
     */
    void SetModel(const FString& ModelName);

    /**
     * Set temperature (0.0 - 1.0)
     */
    void SetTemperature(float Temperature);

    /**
     * Cancel any in-progress request
     */
    void CancelRequest();

private:
    ELLMProvider Provider;
    FString ApiKey;
    FString ModelName;
    float Temperature;
    
    TSharedPtr<IHttpRequest> CurrentRequest;
    FString StreamBuffer;
    
    // Provider-specific implementations
    void SendGeminiRequest(
        const TArray<FChatMessage>& Messages,
        const TArray<FToolDefinition>& Tools,
        FOnStreamChunk OnStreamChunk,
        FOnLLMComplete OnComplete
    );
    
    void SendOpenAIRequest(
        const TArray<FChatMessage>& Messages,
        const TArray<FToolDefinition>& Tools,
        FOnStreamChunk OnStreamChunk,
        FOnLLMComplete OnComplete
    );
    
    // HTTP callbacks
    void OnResponseReceived(
        FHttpRequestPtr Request,
        FHttpResponsePtr Response,
        bool bWasSuccessful,
        FOnLLMComplete OnComplete
    );
    
    void OnStreamDataReceived(
        FHttpRequestPtr Request,
        int32 BytesSent,
        int32 BytesReceived,
        FOnStreamChunk OnStreamChunk
    );
    
    // Parsing helpers
    void ParseSSEChunk(const FString& Chunk, FOnStreamChunk OnStreamChunk);
    TArray<FToolCall> ExtractToolCalls(const TSharedPtr<FJsonObject>& Response);
};
```

### Step 3: Implement Gemini API Client

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/Private/AdastreaLLMClient.cpp`

```cpp
// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "AdastreaLLMClient.h"
#include "AdastreaDirectorModule.h"
#include "HttpModule.h"
#include "JsonObjectConverter.h"

FAdastreaLLMClient::FAdastreaLLMClient()
    : Provider(ELLMProvider::Gemini)
    , ModelName(TEXT("gemini-1.5-flash"))
    , Temperature(0.7f)
{
}

FAdastreaLLMClient::~FAdastreaLLMClient()
{
    CancelRequest();
}

void FAdastreaLLMClient::SetProvider(ELLMProvider InProvider, const FString& InApiKey)
{
    Provider = InProvider;
    ApiKey = InApiKey;
}

void FAdastreaLLMClient::SetModel(const FString& InModelName)
{
    ModelName = InModelName;
}

void FAdastreaLLMClient::SetTemperature(float InTemperature)
{
    Temperature = FMath::Clamp(InTemperature, 0.0f, 1.0f);
}

void FAdastreaLLMClient::SendChatRequest(
    const TArray<FChatMessage>& Messages,
    const TArray<FToolDefinition>& Tools,
    FOnStreamChunk OnStreamChunk,
    FOnLLMComplete OnComplete)
{
    // Cancel any existing request
    CancelRequest();

    // Route to provider-specific implementation
    switch (Provider)
    {
        case ELLMProvider::Gemini:
            SendGeminiRequest(Messages, Tools, OnStreamChunk, OnComplete);
            break;
        case ELLMProvider::OpenAI:
            SendOpenAIRequest(Messages, Tools, OnStreamChunk, OnComplete);
            break;
    }
}

void FAdastreaLLMClient::SendGeminiRequest(
    const TArray<FChatMessage>& Messages,
    const TArray<FToolDefinition>& Tools,
    FOnStreamChunk OnStreamChunk,
    FOnLLMComplete OnComplete)
{
    // Create HTTP request
    TSharedRef<IHttpRequest> Request = FHttpModule::Get().CreateRequest();
    
    // Gemini API endpoint (streaming)
    FString Endpoint = FString::Printf(
        TEXT("https://generativelanguage.googleapis.com/v1beta/models/%s:streamGenerateContent?key=%s"),
        *ModelName,
        *ApiKey
    );
    
    Request->SetURL(Endpoint);
    Request->SetVerb(TEXT("POST"));
    Request->SetHeader(TEXT("Content-Type"), TEXT("application/json"));

    // Build JSON payload
    TSharedPtr<FJsonObject> Payload = MakeShared<FJsonObject>();
    
    // Convert messages to Gemini format
    TArray<TSharedPtr<FJsonValue>> ContentsArray;
    for (const FChatMessage& Message : Messages)
    {
        TSharedPtr<FJsonObject> ContentObj = MakeShared<FJsonObject>();
        
        // Gemini uses "user" and "model" roles
        FString Role = Message.Role == TEXT("assistant") ? TEXT("model") : TEXT("user");
        ContentObj->SetStringField(TEXT("role"), Role);
        
        // Parts array with text
        TArray<TSharedPtr<FJsonValue>> PartsArray;
        TSharedPtr<FJsonObject> Part = MakeShared<FJsonObject>();
        Part->SetStringField(TEXT("text"), Message.Content);
        PartsArray.Add(MakeShared<FJsonValueObject>(Part));
        
        ContentObj->SetArrayField(TEXT("parts"), PartsArray);
        ContentsArray.Add(MakeShared<FJsonValueObject>(ContentObj));
    }
    Payload->SetArrayField(TEXT("contents"), ContentsArray);

    // Generation config
    TSharedPtr<FJsonObject> GenerationConfig = MakeShared<FJsonObject>();
    GenerationConfig->SetNumberField(TEXT("temperature"), Temperature);
    Payload->SetObjectField(TEXT("generationConfig"), GenerationConfig);

    // Tools (if any)
    if (Tools.Num() > 0)
    {
        TArray<TSharedPtr<FJsonValue>> ToolsArray;
        TSharedPtr<FJsonObject> ToolsWrapper = MakeShared<FJsonObject>();
        
        TArray<TSharedPtr<FJsonValue>> FunctionDeclarations;
        for (const FToolDefinition& Tool : Tools)
        {
            FunctionDeclarations.Add(MakeShared<FJsonValueObject>(Tool.ToJson()));
        }
        
        ToolsWrapper->SetArrayField(TEXT("functionDeclarations"), FunctionDeclarations);
        ToolsArray.Add(MakeShared<FJsonValueObject>(ToolsWrapper));
        Payload->SetArrayField(TEXT("tools"), ToolsArray);
    }

    // Serialize to JSON string
    FString JsonString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonString);
    FJsonSerializer::Serialize(Payload.ToSharedRef(), Writer);
    
    Request->SetContentAsString(JsonString);

    // Setup callbacks with weak pointer to prevent dangling pointer if object is destroyed
    TWeakPtr<FAdastreaLLMClient> WeakThis = AsShared();
    
    if (OnStreamChunk.IsBound())
    {
        // Streaming mode
        Request->OnRequestProgress().BindLambda(
            [WeakThis, OnStreamChunk](FHttpRequestPtr Req, int32 BytesSent, int32 BytesReceived)
            {
                TSharedPtr<FAdastreaLLMClient> Pinned = WeakThis.Pin();
                if (!Pinned.IsValid())
                {
                    return;
                }
                
                Pinned->OnStreamDataReceived(Req, BytesSent, BytesReceived, OnStreamChunk);
            }
        );
    }

    Request->OnProcessRequestComplete().BindLambda(
        [WeakThis, OnComplete](FHttpRequestPtr Req, FHttpResponsePtr Response, bool bWasSuccessful)
        {
            TSharedPtr<FAdastreaLLMClient> Pinned = WeakThis.Pin();
            if (!Pinned.IsValid())
            {
                return;
            }
            
            Pinned->OnResponseReceived(Req, Response, bWasSuccessful, OnComplete);
        }
    );

    // Send request
    CurrentRequest = Request;
    Request->ProcessRequest();

    UE_LOG(LogAdastreaDirector, Log, TEXT("Sent Gemini API request"));
}

void FAdastreaLLMClient::OnResponseReceived(
    FHttpRequestPtr Request,
    FHttpResponsePtr Response,
    bool bWasSuccessful,
    FOnLLMComplete OnComplete)
{
    CurrentRequest.Reset();

    if (!bWasSuccessful || !Response.IsValid())
    {
        UE_LOG(LogAdastreaDirector, Error, TEXT("LLM request failed"));
        OnComplete.ExecuteIfBound(false, TEXT("Request failed"), TArray<FToolCall>());
        return;
    }

    int32 StatusCode = Response->GetResponseCode();
    FString ResponseBody = Response->GetContentAsString();

    UE_LOG(LogAdastreaDirector, Log, TEXT("LLM response: %d, Body length: %d"), 
        StatusCode, ResponseBody.Len());

    if (StatusCode != 200)
    {
        UE_LOG(LogAdastreaDirector, Error, TEXT("LLM API error: %s"), *ResponseBody);
        OnComplete.ExecuteIfBound(false, FString::Printf(TEXT("API error: %d"), StatusCode), 
            TArray<FToolCall>());
        return;
    }

    // Parse JSON response
    TSharedPtr<FJsonObject> JsonResponse;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(ResponseBody);
    
    if (!FJsonSerializer::Deserialize(Reader, JsonResponse) || !JsonResponse.IsValid())
    {
        UE_LOG(LogAdastreaDirector, Error, TEXT("Failed to parse JSON response"));
        OnComplete.ExecuteIfBound(false, TEXT("Invalid JSON response"), TArray<FToolCall>());
        return;
    }

    // Extract content and tool calls
    FString Content;
    TArray<FToolCall> ToolCalls;

    // Gemini format: candidates[0].content.parts[]
    const TArray<TSharedPtr<FJsonValue>>* Candidates;
    if (JsonResponse->TryGetArrayField(TEXT("candidates"), Candidates) && Candidates->Num() > 0)
    {
        TSharedPtr<FJsonObject> Candidate = (*Candidates)[0]->AsObject();
        if (!Candidate.IsValid())
        {
            UE_LOG(LogAdastreaDirector, Warning, TEXT("Invalid candidate object in response"));
            OnComplete.ExecuteIfBound(false, TEXT("Invalid candidate format"), TArray<FToolCall>());
            return;
        }
        
        TSharedPtr<FJsonObject> ContentObj;
        if (!Candidate->TryGetObjectField(TEXT("content"), ContentObj) || !ContentObj.IsValid())
        {
            UE_LOG(LogAdastreaDirector, Warning, TEXT("No content field in candidate"));
            OnComplete.ExecuteIfBound(false, TEXT("No content in response"), TArray<FToolCall>());
            return;
        }
        
        const TArray<TSharedPtr<FJsonValue>>* Parts;
        if (ContentObj->TryGetArrayField(TEXT("parts"), Parts))
        {
            for (const TSharedPtr<FJsonValue>& PartValue : *Parts)
            {
                TSharedPtr<FJsonObject> Part = PartValue->AsObject();
                if (!Part.IsValid())
                {
                    continue;
                }
                
                // Text part
                FString Text;
                if (Part->TryGetStringField(TEXT("text"), Text))
                {
                    Content += Text;
                }
                
                // Function call part
                TSharedPtr<FJsonObject> FunctionCall;
                if (Part->TryGetObjectField(TEXT("functionCall"), FunctionCall))
                {
                    FToolCall ToolCall;
                    ToolCall.Id = FGuid::NewGuid().ToString();
                    FunctionCall->TryGetStringField(TEXT("name"), ToolCall.ToolName);
                    
                    // Safely get args object
                    TSharedPtr<FJsonObject> ArgsObject;
                    if (FunctionCall->TryGetObjectField(TEXT("args"), ArgsObject))
                    {
                        ToolCall.Arguments = ArgsObject;
                    }
                    else
                    {
                        ToolCall.Arguments = nullptr;
                    }
                    
                    ToolCalls.Add(ToolCall);
                }
            }
        }
    }

    UE_LOG(LogAdastreaDirector, Log, TEXT("Extracted content: %s, Tool calls: %d"), 
        *Content, ToolCalls.Num());

    OnComplete.ExecuteIfBound(true, Content, ToolCalls);
}

void FAdastreaLLMClient::OnStreamDataReceived(
    FHttpRequestPtr Request,
    int32 BytesSent,
    int32 BytesReceived,
    FOnStreamChunk OnStreamChunk)
{
    // Ensure the request and response are valid before accessing content
    if (!Request.IsValid())
    {
        UE_LOG(LogAdastreaDirector, Warning, TEXT("OnStreamDataReceived called with invalid Request"));
        return;
    }

    FHttpResponsePtr Response = Request->GetResponse();
    if (!Response.IsValid())
    {
        UE_LOG(LogAdastreaDirector, Warning, TEXT("OnStreamDataReceived: Request has no valid response yet"));
        return;
    }

    // Get current response content
    FString ResponseSoFar = Response->GetContentAsString();
    
    // Process only new data since last call (incremental parsing)
    if (ResponseSoFar.Len() > StreamBuffer.Len())
    {
        // Extract only the new portion to avoid reprocessing
        FString NewData = ResponseSoFar.Mid(StreamBuffer.Len());
        
        // Update buffer to current position
        StreamBuffer = ResponseSoFar;
        
        // Parse only the new SSE chunks
        ParseSSEChunk(NewData, OnStreamChunk);
    }
}

void FAdastreaLLMClient::ParseSSEChunk(const FString& Chunk, FOnStreamChunk OnStreamChunk)
{
    // SSE format: data: {...}\n\n
    // Parse JSON from each data: line
    
    TArray<FString> Lines;
    Chunk.ParseIntoArray(Lines, TEXT("\n"), true);
    
    for (const FString& Line : Lines)
    {
        if (Line.StartsWith(TEXT("data: ")))
        {
            FString JsonStr = Line.Mid(6).TrimStartAndEnd();
            
            // Skip [DONE] marker
            if (JsonStr == TEXT("[DONE]"))
            {
                continue;
            }
            
            // Parse JSON
            TSharedPtr<FJsonObject> JsonObj;
            TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonStr);
            
            if (FJsonSerializer::Deserialize(Reader, JsonObj) && JsonObj.IsValid())
            {
                // Extract text content from chunk
                // (Format varies by provider - this is simplified)
                FString Text;
                if (JsonObj->TryGetStringField(TEXT("text"), Text))
                {
                    OnStreamChunk.ExecuteIfBound(Text);
                }
            }
        }
    }
}

void FAdastreaLLMClient::CancelRequest()
{
    if (CurrentRequest.IsValid())
    {
        CurrentRequest->CancelRequest();
        CurrentRequest.Reset();
    }
    StreamBuffer.Empty();
}

// Tool definition serialization
TSharedPtr<FJsonObject> FToolDefinition::ToJson() const
{
    TSharedPtr<FJsonObject> Json = MakeShared<FJsonObject>();
    Json->SetStringField(TEXT("name"), Name);
    Json->SetStringField(TEXT("description"), Description);
    Json->SetObjectField(TEXT("parameters"), Parameters);
    return Json;
}
```

### Step 4: Implement OpenAI API Client

Add the OpenAI-specific implementation to support GPT models.

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/Private/AdastreaLLMClient.cpp` (add to existing file)

```cpp
void FAdastreaLLMClient::SendOpenAIRequest(
    const TArray<FChatMessage>& Messages,
    const TArray<FToolDefinition>& Tools,
    FOnStreamChunk OnStreamChunk,
    FOnLLMComplete OnComplete)
{
    // Create HTTP request
    TSharedRef<IHttpRequest> Request = FHttpModule::Get().CreateRequest();
    
    // OpenAI API endpoint
    Request->SetURL(TEXT("https://api.openai.com/v1/chat/completions"));
    Request->SetVerb(TEXT("POST"));
    Request->SetHeader(TEXT("Content-Type"), TEXT("application/json"));
    Request->SetHeader(TEXT("Authorization"), FString::Printf(TEXT("Bearer %s"), *ApiKey));

    // Build JSON payload
    TSharedPtr<FJsonObject> Payload = MakeShared<FJsonObject>();
    Payload->SetStringField(TEXT("model"), ModelName);
    
    // Convert messages to OpenAI format
    TArray<TSharedPtr<FJsonValue>> MessagesArray;
    for (const FChatMessage& Message : Messages)
    {
        MessagesArray.Add(MakeShared<FJsonValueObject>(Message.ToJson()));
    }
    Payload->SetArrayField(TEXT("messages"), MessagesArray);

    // Generation config
    Payload->SetNumberField(TEXT("temperature"), Temperature);
    Payload->SetBoolField(TEXT("stream"), OnStreamChunk.IsBound());

    // Tools (if any)
    if (Tools.Num() > 0)
    {
        TArray<TSharedPtr<FJsonValue>> ToolsArray;
        for (const FToolDefinition& Tool : Tools)
        {
            TSharedPtr<FJsonObject> ToolObj = MakeShared<FJsonObject>();
            ToolObj->SetStringField(TEXT("type"), TEXT("function"));
            
            TSharedPtr<FJsonObject> FunctionObj = MakeShared<FJsonObject>();
            FunctionObj->SetStringField(TEXT("name"), Tool.Name);
            FunctionObj->SetStringField(TEXT("description"), Tool.Description);
            FunctionObj->SetObjectField(TEXT("parameters"), Tool.Parameters);
            
            ToolObj->SetObjectField(TEXT("function"), FunctionObj);
            ToolsArray.Add(MakeShared<FJsonValueObject>(ToolObj));
        }
        Payload->SetArrayField(TEXT("tools"), ToolsArray);
        Payload->SetStringField(TEXT("tool_choice"), TEXT("auto"));
    }

    // Serialize to JSON string
    FString JsonString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonString);
    FJsonSerializer::Serialize(Payload.ToSharedRef(), Writer);
    
    Request->SetContentAsString(JsonString);

    // Setup callbacks with weak pointer
    TWeakPtr<FAdastreaLLMClient> WeakThis = AsShared();
    
    if (OnStreamChunk.IsBound())
    {
        // Streaming mode
        Request->OnRequestProgress().BindLambda(
            [WeakThis, OnStreamChunk](FHttpRequestPtr Req, int32 BytesSent, int32 BytesReceived)
            {
                TSharedPtr<FAdastreaLLMClient> Pinned = WeakThis.Pin();
                if (!Pinned.IsValid())
                {
                    return;
                }
                
                Pinned->OnStreamDataReceived(Req, BytesSent, BytesReceived, OnStreamChunk);
            }
        );
    }

    Request->OnProcessRequestComplete().BindLambda(
        [WeakThis, OnComplete](FHttpRequestPtr Req, FHttpResponsePtr Response, bool bWasSuccessful)
        {
            TSharedPtr<FAdastreaLLMClient> Pinned = WeakThis.Pin();
            if (!Pinned.IsValid())
            {
                return;
            }
            
            Pinned->OnResponseReceived(Req, Response, bWasSuccessful, OnComplete);
        }
    );

    // Send request
    CurrentRequest = Request;
    Request->ProcessRequest();

    UE_LOG(LogAdastreaDirector, Log, TEXT("Sent OpenAI API request"));
}
```

**Add message serialization helpers:**

```cpp
// In AdastreaLLMClient.cpp - Add these implementations

TSharedPtr<FJsonObject> FChatMessage::ToJson() const
{
    TSharedPtr<FJsonObject> Json = MakeShared<FJsonObject>();
    Json->SetStringField(TEXT("role"), Role);
    Json->SetStringField(TEXT("content"), Content);
    
    if (!ToolCallId.IsEmpty())
    {
        Json->SetStringField(TEXT("tool_call_id"), ToolCallId);
    }
    
    return Json;
}

FChatMessage FChatMessage::FromJson(const TSharedPtr<FJsonObject>& Json)
{
    FChatMessage Message;
    Json->TryGetStringField(TEXT("role"), Message.Role);
    Json->TryGetStringField(TEXT("content"), Message.Content);
    Json->TryGetStringField(TEXT("tool_call_id"), Message.ToolCallId);
    return Message;
}

FToolCall FToolCall::FromJson(const TSharedPtr<FJsonObject>& Json)
{
    FToolCall ToolCall;
    Json->TryGetStringField(TEXT("id"), ToolCall.Id);
    
    TSharedPtr<FJsonObject> FunctionObj;
    if (Json->TryGetObjectField(TEXT("function"), FunctionObj))
    {
        FunctionObj->TryGetStringField(TEXT("name"), ToolCall.ToolName);
        
        FString ArgsString;
        if (FunctionObj->TryGetStringField(TEXT("arguments"), ArgsString))
        {
            // Parse arguments JSON string
            TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(ArgsString);
            FJsonSerializer::Deserialize(Reader, ToolCall.Arguments);
        }
    }
    
    return ToolCall;
}
```

### Step 5: Test LLM Client

**Example usage in Blueprint library or test:**

```cpp
void TestLLMClient()
{
    FAdastreaLLMClient Client;
    Client.SetProvider(ELLMProvider::Gemini, TEXT("YOUR_API_KEY"));
    Client.SetModel(TEXT("gemini-1.5-flash"));

    // Create messages
    TArray<FChatMessage> Messages;
    
    FChatMessage SystemMsg;
    SystemMsg.Role = TEXT("system");
    SystemMsg.Content = TEXT("You are a helpful Unreal Engine assistant.");
    Messages.Add(SystemMsg);
    
    FChatMessage UserMsg;
    UserMsg.Role = TEXT("user");
    UserMsg.Content = TEXT("What is a Blueprint in Unreal Engine?");
    Messages.Add(UserMsg);

    // Create tools (empty for now)
    TArray<FToolDefinition> Tools;

    // Send request
    Client.SendChatRequest(
        Messages,
        Tools,
        FOnStreamChunk::CreateLambda([](const FString& Chunk) {
            UE_LOG(LogAdastreaDirector, Log, TEXT("Stream: %s"), *Chunk);
        }),
        FOnLLMComplete::CreateLambda([](bool bSuccess, const FString& Content, const TArray<FToolCall>& ToolCalls) {
            if (bSuccess)
            {
                UE_LOG(LogAdastreaDirector, Log, TEXT("Complete: %s"), *Content);
                UE_LOG(LogAdastreaDirector, Log, TEXT("Tool calls: %d"), ToolCalls.Num());
            }
            else
            {
                UE_LOG(LogAdastreaDirector, Error, TEXT("Failed: %s"), *Content);
            }
        })
    );
}
```

---

## 3. Runtime Asset Discovery

### Overview

Replace document ingestion with runtime queries using Asset Registry.

### Step 1: Create Asset Discovery Service

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/Public/AdastreaAssetService.h`

```cpp
// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Engine/Blueprint.h"
#include "Materials/Material.h"
#include "Blueprint/WidgetBlueprint.h"

struct FAssetInfo
{
    FString Name;
    FString Path;
    FString Class;
    int64 DiskSize;
    
    TSharedPtr<FJsonObject> ToJson() const;
};

/**
 * Service for discovering and querying project assets at runtime
 */
class ADASTREADIRECTOR_API FAdastreaAssetService
{
public:
    /**
     * Search for assets by name pattern and/or class
     * @param SearchPattern Name pattern (supports wildcards)
     * @param ClassName Optional class filter (e.g., "Blueprint", "Material")
     * @param MaxResults Maximum number of results
     * @return Array of matching assets
     */
    static TArray<FAssetInfo> SearchAssets(
        const FString& SearchPattern = TEXT("*"),
        const FString& ClassName = TEXT(""),
        int32 MaxResults = 100
    );

    /**
     * Get all Blueprints in the project
     * @param PathPrefix Optional path filter (e.g., "/Game/Characters/")
     * @return Array of Blueprint assets
     */
    static TArray<FAssetInfo> GetBlueprints(const FString& PathPrefix = TEXT(""));

    /**
     * Get all Materials in the project
     * @param PathPrefix Optional path filter
     * @return Array of Material assets
     */
    static TArray<FAssetInfo> GetMaterials(const FString& PathPrefix = TEXT(""));

    /**
     * Get all UMG Widgets in the project
     * @param PathPrefix Optional path filter
     * @return Array of Widget Blueprint assets
     */
    static TArray<FAssetInfo> GetWidgets(const FString& PathPrefix = TEXT(""));

    /**
     * Get asset information by path
     * @param AssetPath Full asset path
     * @return Asset info or empty if not found
     */
    static TOptional<FAssetInfo> GetAssetByPath(const FString& AssetPath);

    /**
     * Check if asset registry is ready
     * @return True if asset registry has finished initial scan
     */
    static bool IsAssetRegistryReady();

private:
    static IAssetRegistry& GetAssetRegistry();
    static FAssetInfo ConvertAssetData(const FAssetData& AssetData);
};
```

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/Private/AdastreaAssetService.cpp`

```cpp
// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "AdastreaAssetService.h"
#include "AdastreaDirectorModule.h"
#include "AssetRegistry/AssetRegistryModule.h"

IAssetRegistry& FAdastreaAssetService::GetAssetRegistry()
{
    FAssetRegistryModule& AssetRegistryModule = 
        FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
    return AssetRegistryModule.Get();
}

bool FAdastreaAssetService::IsAssetRegistryReady()
{
    return !GetAssetRegistry().IsLoadingAssets();
}

TArray<FAssetInfo> FAdastreaAssetService::SearchAssets(
    const FString& SearchPattern,
    const FString& ClassName,
    int32 MaxResults)
{
    TArray<FAssetInfo> Results;
    IAssetRegistry& AssetRegistry = GetAssetRegistry();

    // Build filter
    FARFilter Filter;
    
    if (!ClassName.IsEmpty())
    {
        // Use full class path string for FTopLevelAssetPath
        Filter.ClassPaths.Add(FTopLevelAssetPath(*ClassName));
    }

    // Search all game content
    Filter.PackagePaths.Add(FName("/Game"));
    Filter.bRecursivePaths = true;

    // Get assets
    TArray<FAssetData> AssetDataList;
    AssetRegistry.GetAssets(Filter, AssetDataList);

    // Filter by name pattern
    for (const FAssetData& AssetData : AssetDataList)
    {
        FString AssetName = AssetData.AssetName.ToString();
        
        if (SearchPattern == TEXT("*") || AssetName.Contains(SearchPattern))
        {
            Results.Add(ConvertAssetData(AssetData));
            
            if (Results.Num() >= MaxResults)
            {
                break;
            }
        }
    }

    UE_LOG(LogAdastreaDirector, Log, TEXT("Asset search: '%s' class '%s' -> %d results"),
        *SearchPattern, *ClassName, Results.Num());

    return Results;
}

TArray<FAssetInfo> FAdastreaAssetService::GetBlueprints(const FString& PathPrefix)
{
    IAssetRegistry& AssetRegistry = GetAssetRegistry();
    
    FARFilter Filter;
    Filter.ClassPaths.Add(UBlueprint::StaticClass()->GetClassPathName());
    Filter.PackagePaths.Add(PathPrefix.IsEmpty() ? FName("/Game") : FName(*PathPrefix));
    Filter.bRecursivePaths = true;

    TArray<FAssetData> AssetDataList;
    AssetRegistry.GetAssets(Filter, AssetDataList);

    TArray<FAssetInfo> Results;
    for (const FAssetData& AssetData : AssetDataList)
    {
        Results.Add(ConvertAssetData(AssetData));
    }

    return Results;
}

TArray<FAssetInfo> FAdastreaAssetService::GetMaterials(const FString& PathPrefix)
{
    IAssetRegistry& AssetRegistry = GetAssetRegistry();
    
    FARFilter Filter;
    Filter.ClassPaths.Add(UMaterial::StaticClass()->GetClassPathName());
    Filter.PackagePaths.Add(PathPrefix.IsEmpty() ? FName("/Game") : FName(*PathPrefix));
    Filter.bRecursivePaths = true;

    TArray<FAssetData> AssetDataList;
    AssetRegistry.GetAssets(Filter, AssetDataList);

    TArray<FAssetInfo> Results;
    for (const FAssetData& AssetData : AssetDataList)
    {
        Results.Add(ConvertAssetData(AssetData));
    }

    return Results;
}

TArray<FAssetInfo> FAdastreaAssetService::GetWidgets(const FString& PathPrefix)
{
    IAssetRegistry& AssetRegistry = GetAssetRegistry();
    
    FARFilter Filter;
    Filter.ClassPaths.Add(UWidgetBlueprint::StaticClass()->GetClassPathName());
    Filter.PackagePaths.Add(PathPrefix.IsEmpty() ? FName("/Game") : FName(*PathPrefix));
    Filter.bRecursivePaths = true;

    TArray<FAssetData> AssetDataList;
    AssetRegistry.GetAssets(Filter, AssetDataList);

    TArray<FAssetInfo> Results;
    for (const FAssetData& AssetData : AssetDataList)
    {
        Results.Add(ConvertAssetData(AssetData));
    }

    return Results;
}

TOptional<FAssetInfo> FAdastreaAssetService::GetAssetByPath(const FString& AssetPath)
{
    IAssetRegistry& AssetRegistry = GetAssetRegistry();
    
    // Use newer UE5 API with FTopLevelAssetPath for compatibility
    FSoftObjectPath ObjectPath(AssetPath);
    FAssetData AssetData = AssetRegistry.GetAssetByObjectPath(ObjectPath);
    
    if (AssetData.IsValid())
    {
        return ConvertAssetData(AssetData);
    }
    
    return TOptional<FAssetInfo>();
}

FAssetInfo FAdastreaAssetService::ConvertAssetData(const FAssetData& AssetData)
{
    FAssetInfo Info;
    Info.Name = AssetData.AssetName.ToString();
    Info.Path = AssetData.GetObjectPathString();
    Info.Class = AssetData.AssetClassPath.GetAssetName().ToString();
    
    // Get disk size
    const FAssetPackageData* PackageData = AssetData.GetPackageData();
    if (PackageData)
    {
        Info.DiskSize = PackageData->DiskSize;
    }
    
    return Info;
}

TSharedPtr<FJsonObject> FAssetInfo::ToJson() const
{
    TSharedPtr<FJsonObject> Json = MakeShared<FJsonObject>();
    Json->SetStringField(TEXT("name"), Name);
    Json->SetStringField(TEXT("path"), Path);
    Json->SetStringField(TEXT("class"), Class);
    Json->SetNumberField(TEXT("diskSize"), DiskSize);
    return Json;
}
```

### Step 2: Expose as Tool

Create a tool that the LLM can call to search assets:

```cpp
// In tool execution
FString ExecuteSearchAssetsTool(const TSharedPtr<FJsonObject>& Args)
{
    FString SearchPattern;
    Args->TryGetStringField(TEXT("pattern"), SearchPattern);
    
    FString ClassName;
    Args->TryGetStringField(TEXT("class"), ClassName);
    
    int32 MaxResults = 50;
    Args->TryGetNumberField(TEXT("maxResults"), MaxResults);
    
    TArray<FAssetInfo> Results = FAdastreaAssetService::SearchAssets(
        SearchPattern, ClassName, MaxResults
    );
    
    // Build JSON response
    TSharedPtr<FJsonObject> Response = MakeShared<FJsonObject>();
    Response->SetNumberField(TEXT("count"), Results.Num());
    
    TArray<TSharedPtr<FJsonValue>> AssetsArray;
    for (const FAssetInfo& Asset : Results)
    {
        AssetsArray.Add(MakeShared<FJsonValueObject>(Asset.ToJson()));
    }
    Response->SetArrayField(TEXT("assets"), AssetsArray);
    
    FString JsonString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonString);
    FJsonSerializer::Serialize(Response.ToSharedRef(), Writer);
    
    return JsonString;
}
```

---

## 4. Tool System Architecture

### Overview

The tool system is the core of how the LLM interacts with Unreal Engine. Tools are C++ functions that the LLM can call to perform actions like querying assets, executing Python, or modifying the project.

### Tool Definition Structure

Each tool needs:
1. **Name** - Unique identifier for the tool
2. **Description** - Clear explanation of what the tool does
3. **Parameters** - JSON schema defining input parameters
4. **Execution Handler** - C++ function that implements the tool

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/Public/AdastreaToolSystem.h`

```cpp
// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Dom/JsonObject.h"

/**
 * Tool execution result
 */
struct FToolExecutionResult
{
    bool bSuccess = false;
    FString Output;
    FString ErrorMessage;
    TSharedPtr<FJsonObject> Data;
    
    TSharedPtr<FJsonObject> ToJson() const;
};

/**
 * Delegate for tool execution
 * @param Arguments Tool arguments as JSON
 * @return Execution result
 */
DECLARE_DELEGATE_RetVal_OneParam(FToolExecutionResult, FToolExecutor, const TSharedPtr<FJsonObject>& /* Arguments */);

/**
 * Tool registration information
 */
struct FAdastreaToolInfo
{
    FString Name;
    FString Description;
    TSharedPtr<FJsonObject> ParameterSchema;
    FToolExecutor Executor;
    FString Category; // e.g., "Asset", "Python", "Debug"
};

/**
 * Central tool registry and execution system
 */
class ADASTREADIRECTOR_API FAdastreaToolSystem
{
public:
    static FAdastreaToolSystem& Get();
    
    /**
     * Register a new tool
     */
    void RegisterTool(const FAdastreaToolInfo& ToolInfo);
    
    /**
     * Unregister a tool
     */
    void UnregisterTool(const FString& ToolName);
    
    /**
     * Execute a tool by name
     */
    FToolExecutionResult ExecuteTool(const FString& ToolName, const TSharedPtr<FJsonObject>& Arguments);
    
    /**
     * Get all registered tools (for LLM context)
     */
    TArray<FToolDefinition> GetAllToolDefinitions() const;
    
    /**
     * Get tools by category
     */
    TArray<FToolDefinition> GetToolsByCategory(const FString& Category) const;
    
    /**
     * Check if tool exists
     */
    bool HasTool(const FString& ToolName) const;

private:
    FAdastreaToolSystem() = default;
    
    TMap<FString, FAdastreaToolInfo> RegisteredTools;
};
```

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/Private/AdastreaToolSystem.cpp`

```cpp
// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "AdastreaToolSystem.h"
#include "AdastreaDirectorModule.h"

FAdastreaToolSystem& FAdastreaToolSystem::Get()
{
    static FAdastreaToolSystem Instance;
    return Instance;
}

void FAdastreaToolSystem::RegisterTool(const FAdastreaToolInfo& ToolInfo)
{
    if (ToolInfo.Name.IsEmpty())
    {
        UE_LOG(LogAdastreaDirector, Error, TEXT("Cannot register tool with empty name"));
        return;
    }
    
    if (RegisteredTools.Contains(ToolInfo.Name))
    {
        UE_LOG(LogAdastreaDirector, Warning, TEXT("Overwriting existing tool: %s"), *ToolInfo.Name);
    }
    
    RegisteredTools.Add(ToolInfo.Name, ToolInfo);
    UE_LOG(LogAdastreaDirector, Log, TEXT("Registered tool: %s"), *ToolInfo.Name);
}

void FAdastreaToolSystem::UnregisterTool(const FString& ToolName)
{
    RegisteredTools.Remove(ToolName);
}

FToolExecutionResult FAdastreaToolSystem::ExecuteTool(
    const FString& ToolName,
    const TSharedPtr<FJsonObject>& Arguments)
{
    FToolExecutionResult Result;
    
    if (!RegisteredTools.Contains(ToolName))
    {
        Result.bSuccess = false;
        Result.ErrorMessage = FString::Printf(TEXT("Tool not found: %s"), *ToolName);
        return Result;
    }
    
    const FAdastreaToolInfo& ToolInfo = RegisteredTools[ToolName];
    
    if (!ToolInfo.Executor.IsBound())
    {
        Result.bSuccess = false;
        Result.ErrorMessage = FString::Printf(TEXT("Tool has no executor: %s"), *ToolName);
        return Result;
    }
    
    UE_LOG(LogAdastreaDirector, Log, TEXT("Executing tool: %s"), *ToolName);
    
    // Execute the tool
    Result = ToolInfo.Executor.Execute(Arguments);
    
    return Result;
}

TArray<FToolDefinition> FAdastreaToolSystem::GetAllToolDefinitions() const
{
    TArray<FToolDefinition> Definitions;
    
    for (const auto& Pair : RegisteredTools)
    {
        FToolDefinition Def;
        Def.Name = Pair.Value.Name;
        Def.Description = Pair.Value.Description;
        Def.Parameters = Pair.Value.ParameterSchema;
        Definitions.Add(Def);
    }
    
    return Definitions;
}

TArray<FToolDefinition> FAdastreaToolSystem::GetToolsByCategory(const FString& Category) const
{
    TArray<FToolDefinition> Definitions;
    
    for (const auto& Pair : RegisteredTools)
    {
        if (Pair.Value.Category == Category)
        {
            FToolDefinition Def;
            Def.Name = Pair.Value.Name;
            Def.Description = Pair.Value.Description;
            Def.Parameters = Pair.Value.ParameterSchema;
            Definitions.Add(Def);
        }
    }
    
    return Definitions;
}

bool FAdastreaToolSystem::HasTool(const FString& ToolName) const
{
    return RegisteredTools.Contains(ToolName);
}

TSharedPtr<FJsonObject> FToolExecutionResult::ToJson() const
{
    TSharedPtr<FJsonObject> Json = MakeShared<FJsonObject>();
    Json->SetBoolField(TEXT("success"), bSuccess);
    Json->SetStringField(TEXT("output"), Output);
    
    if (!ErrorMessage.IsEmpty())
    {
        Json->SetStringField(TEXT("error"), ErrorMessage);
    }
    
    if (Data.IsValid())
    {
        Json->SetObjectField(TEXT("data"), Data);
    }
    
    return Json;
}
```

### Tool Execution System

Create a conversation loop that handles tool calls:

```cpp
// Example: Chat loop with tool execution
void RunChatLoop()
{
    TSharedPtr<FAdastreaLLMClient> LLMClient = MakeShared<FAdastreaLLMClient>();
    LLMClient->SetProvider(ELLMProvider::Gemini, ApiKey);
    
    TArray<FChatMessage> ConversationHistory;
    
    // System message
    FChatMessage SystemMsg;
    SystemMsg.Role = TEXT("system");
    SystemMsg.Content = TEXT("You are an Unreal Engine assistant. Use tools to help the user.");
    ConversationHistory.Add(SystemMsg);
    
    // User message
    FChatMessage UserMsg;
    UserMsg.Role = TEXT("user");
    UserMsg.Content = TEXT("List all blueprints in the project");
    ConversationHistory.Add(UserMsg);
    
    // Get available tools
    TArray<FToolDefinition> Tools = FAdastreaToolSystem::Get().GetAllToolDefinitions();
    
    // Send to LLM
    LLMClient->SendChatRequest(
        ConversationHistory,
        Tools,
        FOnStreamChunk(), // No streaming for this example
        FOnLLMComplete::CreateLambda([&](bool bSuccess, const FString& Content, const TArray<FToolCall>& ToolCalls)
        {
            if (!bSuccess)
            {
                UE_LOG(LogAdastreaDirector, Error, TEXT("LLM request failed: %s"), *Content);
                return;
            }
            
            // Add assistant response to history
            FChatMessage AssistantMsg;
            AssistantMsg.Role = TEXT("assistant");
            AssistantMsg.Content = Content;
            ConversationHistory.Add(AssistantMsg);
            
            // Execute any tool calls
            if (ToolCalls.Num() > 0)
            {
                for (const FToolCall& ToolCall : ToolCalls)
                {
                    FToolExecutionResult Result = FAdastreaToolSystem::Get().ExecuteTool(
                        ToolCall.ToolName,
                        ToolCall.Arguments
                    );
                    
                    // Add tool result to history
                    FChatMessage ToolResultMsg;
                    ToolResultMsg.Role = TEXT("tool");
                    ToolResultMsg.ToolCallId = ToolCall.Id;
                    
                    FString JsonString;
                    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonString);
                    FJsonSerializer::Serialize(Result.ToJson().ToSharedRef(), Writer);
                    ToolResultMsg.Content = JsonString;
                    
                    ConversationHistory.Add(ToolResultMsg);
                }
                
                // Continue conversation with tool results
                // (Recursive call or loop back to send again)
            }
            else
            {
                // No more tool calls - conversation complete
                UE_LOG(LogAdastreaDirector, Log, TEXT("Assistant: %s"), *Content);
            }
        })
    );
}
```

### Built-in Tools

Register essential tools during module startup:

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/Private/AdastreaDirectorModule.cpp`

```cpp
void FAdastreaDirectorModule::StartupModule()
{
    // Register built-in tools
    RegisterAssetTools();
    RegisterPythonTools();
    RegisterDebugTools();
}

void FAdastreaDirectorModule::RegisterAssetTools()
{
    // search_assets tool
    FAdastreaToolInfo SearchAssetsTool;
    SearchAssetsTool.Name = TEXT("search_assets");
    SearchAssetsTool.Description = TEXT("Search for assets in the project by name pattern and/or class type");
    SearchAssetsTool.Category = TEXT("Asset");
    
    // Parameter schema
    TSharedPtr<FJsonObject> Schema = MakeShared<FJsonObject>();
    Schema->SetStringField(TEXT("type"), TEXT("object"));
    
    TSharedPtr<FJsonObject> Properties = MakeShared<FJsonObject>();
    
    TSharedPtr<FJsonObject> PatternProp = MakeShared<FJsonObject>();
    PatternProp->SetStringField(TEXT("type"), TEXT("string"));
    PatternProp->SetStringField(TEXT("description"), TEXT("Name pattern to search for (supports wildcards)"));
    Properties->SetObjectField(TEXT("pattern"), PatternProp);
    
    TSharedPtr<FJsonObject> ClassProp = MakeShared<FJsonObject>();
    ClassProp->SetStringField(TEXT("type"), TEXT("string"));
    ClassProp->SetStringField(TEXT("description"), TEXT("Asset class filter (e.g., Blueprint, Material)"));
    Properties->SetObjectField(TEXT("class"), ClassProp);
    
    Schema->SetObjectField(TEXT("properties"), Properties);
    SearchAssetsTool.ParameterSchema = Schema;
    
    // Executor
    SearchAssetsTool.Executor.BindLambda([](const TSharedPtr<FJsonObject>& Args) -> FToolExecutionResult
    {
        FToolExecutionResult Result;
        
        FString Pattern = TEXT("*");
        Args->TryGetStringField(TEXT("pattern"), Pattern);
        
        FString ClassName;
        Args->TryGetStringField(TEXT("class"), ClassName);
        
        TArray<FAssetInfo> Assets = FAdastreaAssetService::SearchAssets(Pattern, ClassName, 100);
        
        // Build JSON response
        TSharedPtr<FJsonObject> Data = MakeShared<FJsonObject>();
        Data->SetNumberField(TEXT("count"), Assets.Num());
        
        TArray<TSharedPtr<FJsonValue>> AssetsArray;
        for (const FAssetInfo& Asset : Assets)
        {
            AssetsArray.Add(MakeShared<FJsonValueObject>(Asset.ToJson()));
        }
        Data->SetArrayField(TEXT("assets"), AssetsArray);
        
        Result.bSuccess = true;
        Result.Output = FString::Printf(TEXT("Found %d assets"), Assets.Num());
        Result.Data = Data;
        
        return Result;
    });
    
    FAdastreaToolSystem::Get().RegisterTool(SearchAssetsTool);
}

void FAdastreaDirectorModule::RegisterPythonTools()
{
    // execute_python tool
    FAdastreaToolInfo ExecutePythonTool;
    ExecutePythonTool.Name = TEXT("execute_python");
    ExecutePythonTool.Description = TEXT("Execute Python code in the Unreal Editor. SECURITY: Only execute trusted, reviewed code.");
    ExecutePythonTool.Category = TEXT("Python");
    
    TSharedPtr<FJsonObject> Schema = MakeShared<FJsonObject>();
    Schema->SetStringField(TEXT("type"), TEXT("object"));
    
    TSharedPtr<FJsonObject> Properties = MakeShared<FJsonObject>();
    
    TSharedPtr<FJsonObject> CodeProp = MakeShared<FJsonObject>();
    CodeProp->SetStringField(TEXT("type"), TEXT("string"));
    CodeProp->SetStringField(TEXT("description"), TEXT("Python code to execute"));
    Properties->SetObjectField(TEXT("code"), CodeProp);
    
    Schema->SetObjectField(TEXT("properties"), Properties);
    
    TArray<TSharedPtr<FJsonValue>> Required;
    Required.Add(MakeShared<FJsonValueString>(TEXT("code")));
    Schema->SetArrayField(TEXT("required"), Required);
    
    ExecutePythonTool.ParameterSchema = Schema;
    
    // ⚠️ CRITICAL SECURITY WARNING:
    // This tool is DISABLED by default because it executes arbitrary Python code.
    // An attacker controlling tool inputs (e.g., via MCP or compromised client) can run
    // arbitrary Python in the Unreal Editor process, leading to full project compromise.
    // 
    // DO NOT ENABLE unless you implement:
    // 1. Strict allowlist of permitted operations/modules
    // 2. Interactive user confirmation in the editor
    // 3. Code review and approval workflow
    // 4. Audit logging of all executed code
    // 5. Sandboxing or restricted execution environment
    //
    // See Section 1, Step 5 "Security Considerations" for detailed mitigation strategies.
    
    // Executor is DISABLED for security - do not execute arbitrary Python from untrusted inputs
    ExecutePythonTool.Executor.BindLambda([](const TSharedPtr<FJsonObject>& Args) -> FToolExecutionResult
    {
        FToolExecutionResult Result;
        Result.bSuccess = false;
        Result.ErrorMessage = TEXT(
            "SECURITY: The 'execute_python' tool is DISABLED by default. "
            "This tool executes arbitrary Python code which poses severe security risks. "
            "Do NOT enable without implementing proper security controls:\n"
            "1. Allowlist permitted operations/modules\n"
            "2. Require explicit user approval in editor UI\n"
            "3. Implement code review workflow\n"
            "4. Add comprehensive audit logging\n"
            "5. Use sandboxed execution environment\n\n"
            "See VIBEUE_IMPLEMENTATION_GUIDE.md Section 1, Step 5 for security guidance.\n\n"
            "If you understand the risks and have implemented proper controls, "
            "replace this lambda with a hardened execution wrapper."
        );
        
        return Result;
    });
    
    // ORIGINAL UNSAFE IMPLEMENTATION (DO NOT USE):
    // ExecutePythonTool.Executor.BindLambda([](const TSharedPtr<FJsonObject>& Args) -> FToolExecutionResult
    // {
    //     FToolExecutionResult Result;
    //     
    //     FString Code;
    //     if (!Args->TryGetStringField(TEXT("code"), Code))
    //     {
    //         Result.bSuccess = false;
    //         Result.ErrorMessage = TEXT("Missing 'code' parameter");
    //         return Result;
    //     }
    //     
    //     // UNSAFE: Executes arbitrary code without validation
    //     FAdastreaScriptResult ScriptResult = FAdastreaScriptService::ExecuteCode(Code);
    //     
    //     Result.bSuccess = ScriptResult.bSuccess;
    //     Result.Output = ScriptResult.Output;
    //     Result.ErrorMessage = ScriptResult.ErrorMessage;
    //     
    //     TSharedPtr<FJsonObject> Data = MakeShared<FJsonObject>();
    //     Data->SetNumberField(TEXT("executionTimeMs"), ScriptResult.ExecutionTimeMs);
    //     Result.Data = Data;
    //     
    //     return Result;
    // });
    
    FAdastreaToolSystem::Get().RegisterTool(ExecutePythonTool);
}
```

---

## 5. MCP Protocol Integration

### Overview

The Model Context Protocol (MCP) is a standardized way to expose tools to external AI clients. By implementing an MCP server, Adastrea-Director can be controlled by VS Code, Claude Desktop, or other MCP-compatible clients.

### MCP Server Implementation

**Note:** The complete MCP server implementation code shown in this section is provided as a reference architecture. For a working implementation, refer to VibeUE's `Source/VibeUE/Private/MCP/MCPServer.cpp` and `MCPTransport.cpp` as practical examples.

The MCP server implementation should include:

- HTTP server setup using FHttpServerModule
- Tool list endpoint (`/mcp/tools/list`)
- Tool execution endpoint (`/mcp/tools/call`)
- Resource endpoint (`/mcp/resources`)
- JSON request/response handling
- Error handling and validation

**Reference Implementation Structure:**

```cpp
// File: Plugins/AdastreaDirector/Source/AdastreaDirector/Public/AdastreaMCPServer.h
// See VibeUE's MCPServer.h for complete implementation example

class ADASTREADIRECTOR_API FAdastreaMCPServer
{
public:
    bool Start(int32 Port = 8088);
    void Stop();
    bool IsRunning() const;
    
private:
    TSharedPtr<IHttpRouter> HttpRouter;
    bool HandleListTools(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete);
    bool HandleExecuteTool(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete);
    bool HandleGetResources(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete);
};
```

For the complete implementation with HTTP routing, JSON serialization, and error handling, refer to Section 5 in the earlier code examples or study VibeUE's MCP implementation.

### External Client Support

With the MCP server running, external clients can connect and use Adastrea tools. Example configuration for VS Code:

**`.vscode/mcp-settings.json`**

```json
{
  "mcpServers": {
    "adastrea-director": {
      "url": "http://localhost:8088/mcp",
      "apiKey": ""
    }
  }
}
```

---

## 6. Quick Migration Checklist

### Phase 1: Remove Python Process (Week 1)

- [ ] Add `PythonScriptPlugin` to .uplugin dependencies
- [ ] Create `FAdastreaScriptService` class
- [ ] Test basic Python execution
- [ ] Test `unreal` module access
- [ ] Document Python API patterns

### Phase 2: Direct LLM Integration (Weeks 2-3)

- [ ] Add HTTP/JSON module dependencies
- [ ] Create `FAdastreaLLMClient` class
- [ ] Implement Gemini API client
- [ ] Implement OpenAI API client (optional)
- [ ] Add streaming support
- [ ] Test conversation flow
- [ ] Test tool calling
- [ ] Remove Python LLM code

### Phase 3: Runtime Discovery (Week 4)

- [ ] Create `FAdastreaAssetService` class
- [ ] Implement Blueprint discovery
- [ ] Implement Material discovery
- [ ] Implement Widget discovery
- [ ] Create search tools
- [ ] Test with LLM
- [ ] Deprecate ingest.py

### Phase 4: Clean Up (Week 5)

- [ ] Remove `FPythonProcessManager`
- [ ] Remove `FIPCClient`
- [ ] Remove Python IPC server (`main.py` IPC parts)
- [ ] Update documentation
- [ ] Update user guides
- [ ] Test end-to-end

---

## 7. Testing Strategy

### Unit Tests

```cpp
// Test Python execution
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTestPythonExecution, "Adastrea.Python.BasicExecution", 
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FTestPythonExecution::RunTest(const FString& Parameters)
{
    FAdastreaScriptResult Result = FAdastreaScriptService::EvaluateExpression(TEXT("2 + 2"));
    TestTrue(TEXT("Python execution succeeded"), Result.bSuccess);
    TestEqual(TEXT("Python result is 4"), Result.Output.TrimStartAndEnd(), TEXT("4"));
    return true;
}

// Test Asset discovery
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTestAssetDiscovery, "Adastrea.Assets.Discovery",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FTestAssetDiscovery::RunTest(const FString& Parameters)
{
    TArray<FAssetInfo> Blueprints = FAdastreaAssetService::GetBlueprints();
    TestTrue(TEXT("Found blueprints"), Blueprints.Num() > 0);
    return true;
}
```

### Integration Tests

1. **LLM Chat Test:**
   - Send message to LLM
   - Verify response received
   - Check streaming works
   - Verify tool calling

2. **Asset Query Test:**
   - Ask LLM "what blueprints exist?"
   - LLM calls search_assets tool
   - Tool returns asset list
   - LLM provides summary

3. **Python Execution Test:**
   - Ask LLM to "list selected assets"
   - LLM generates Python code
   - Execute via FAdastreaScriptService
   - Return results to LLM

---

## 8. Common Pitfalls & Solutions

### Pitfall 1: Python Plugin Not Loaded

**Problem:** `IPythonScriptPlugin::Get()` returns nullptr

**Solution:**
```cpp
// In module startup
void FAdastreaDirectorModule::StartupModule()
{
    // Ensure Python plugin is loaded
    if (FModuleManager::Get().IsModuleLoaded("PythonScriptPlugin"))
    {
        UE_LOG(LogAdastreaDirector, Log, TEXT("Python plugin is loaded"));
    }
    else
    {
        UE_LOG(LogAdastreaDirector, Warning, TEXT("Python plugin not loaded - some features disabled"));
    }
}
```

### Pitfall 2: Asset Registry Not Ready

**Problem:** Asset searches return empty even though assets exist

**Solution:**
```cpp
void SearchAssetsWhenReady()
{
    IAssetRegistry& Registry = GetAssetRegistry();
    
    if (Registry.IsLoadingAssets())
    {
        // Wait for loading to complete
        Registry.OnFilesLoaded().AddLambda([this]() {
            // Retry search now
            PerformSearch();
        });
    }
    else
    {
        PerformSearch();
    }
}
```

### Pitfall 3: JSON Parsing Errors

**Problem:** LLM responses fail to parse

**Solution:**
```cpp
void ParseResponseSafely(const FString& Response)
{
    TSharedPtr<FJsonObject> JsonObj;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Response);
    
    if (!FJsonSerializer::Deserialize(Reader, JsonObj))
    {
        UE_LOG(LogAdastreaDirector, Error, TEXT("JSON parse error: %s"), 
            *Reader->GetErrorMessage());
        // Handle error gracefully
        return;
    }
    
    // Proceed with valid JSON
}
```

---

## 9. Performance Optimization

### HTTP Request Pooling

Reuse HTTP connections to improve LLM request performance:

```cpp
class FAdastreaHTTPPool
{
public:
    static TSharedRef<IHttpRequest> GetRequest()
    {
        if (AvailableRequests.Num() > 0)
        {
            return AvailableRequests.Pop();
        }
        
        return FHttpModule::Get().CreateRequest();
    }
    
    static void ReturnRequest(TSharedRef<IHttpRequest> Request)
    {
        // Reset request
        Request->CancelRequest();
        Request->SetURL(TEXT(""));
        Request->SetHeader(TEXT("Authorization"), TEXT(""));
        
        // Return to pool (max 10 cached)
        if (AvailableRequests.Num() < 10)
        {
            AvailableRequests.Add(Request);
        }
    }

private:
    static TArray<TSharedRef<IHttpRequest>> AvailableRequests;
};
```

### Asset Registry Caching

Cache asset registry queries to avoid repeated searches:

```cpp
class FAdastreaAssetCache
{
public:
    struct FCacheEntry
    {
        TArray<FAssetInfo> Assets;
        double Timestamp;
        bool IsValid() const { return FPlatformTime::Seconds() - Timestamp < 60.0; }
    };
    
    TOptional<TArray<FAssetInfo>> GetCached(const FString& Query)
    {
        if (Cache.Contains(Query))
        {
            FCacheEntry& Entry = Cache[Query];
            if (Entry.IsValid())
            {
                return Entry.Assets;
            }
        }
        return TOptional<TArray<FAssetInfo>>();
    }
    
    void SetCached(const FString& Query, const TArray<FAssetInfo>& Assets)
    {
        FCacheEntry Entry;
        Entry.Assets = Assets;
        Entry.Timestamp = FPlatformTime::Seconds();
        Cache.Add(Query, Entry);
    }

private:
    TMap<FString, FCacheEntry> Cache;
};
```

### Streaming Response Handling

Optimize streaming for better UX:

```cpp
// Buffer chunks to avoid too many UI updates
class FStreamBuffer
{
public:
    void AddChunk(const FString& Chunk)
    {
        Buffer += Chunk;
        LastChunkTime = FPlatformTime::Seconds();
        
        // Flush if buffer is large enough or enough time has passed
        if (Buffer.Len() > 100 || (FPlatformTime::Seconds() - LastFlushTime) > 0.1)
        {
            Flush();
        }
    }
    
    void Flush()
    {
        if (!Buffer.IsEmpty() && OnFlush.IsBound())
        {
            OnFlush.Execute(Buffer);
            Buffer.Empty();
            LastFlushTime = FPlatformTime::Seconds();
        }
    }
    
    FOnStreamChunk OnFlush;

private:
    FString Buffer;
    double LastChunkTime = 0.0;
    double LastFlushTime = 0.0;
};
```

---

## 10. Migration from Current Architecture

### Step-by-Step Migration Path

**Phase 0: Preparation (Week 0)**
1. Create feature branch: `feature/vibeue-migration`
2. Set up parallel implementation (keep old code working)
3. Add feature flags for gradual rollout
4. Create comprehensive test suite

```cpp
// Feature flag system
class FAdastreaFeatureFlags
{
public:
    static bool UseBuiltInPython() { return CVarUseBuiltInPython.GetValueOnAnyThread(); }
    static bool UseDirectLLM() { return CVarUseDirectLLM.GetValueOnAnyThread(); }
    static bool UseRuntimeDiscovery() { return CVarUseRuntimeDiscovery.GetValueOnAnyThread(); }

private:
    static TAutoConsoleVariable<bool> CVarUseBuiltInPython;
    static TAutoConsoleVariable<bool> CVarUseDirectLLM;
    static TAutoConsoleVariable<bool> CVarUseRuntimeDiscovery;
};
```

**Phase 1: Python Integration (Week 1)**

Day 1-2: Setup
- Add PythonScriptPlugin dependency
- Create FAdastreaScriptService
- Write unit tests

Day 3-4: Implementation
- Implement ExecuteCode and EvaluateExpression
- Add error handling
- Test with sample scripts

Day 5: Integration
- Update existing code paths to use new service
- Keep old external process as fallback (feature flag)
- Integration testing

**Phase 2: Direct LLM Client (Weeks 2-3)**

Week 2: Gemini Implementation
- Create FAdastreaLLMClient
- Implement Gemini API support
- Add streaming
- Unit tests

Week 3: OpenAI + Polish
- Add OpenAI support
- Tool calling implementation
- Error handling improvements
- Performance testing

**Phase 3: Runtime Discovery (Week 4)**

Day 1-2: Asset Service
- Create FAdastreaAssetService
- Implement Blueprint/Material/Widget discovery
- Caching implementation

Day 3-4: Tool Integration
- Register asset tools
- Test with LLM
- Performance optimization

Day 5: Deprecation
- Mark old ingestion code as deprecated
- Update documentation
- Migration guide for users

**Phase 4: Cleanup (Week 5)**

Day 1-2: Remove Old Code
- Remove FPythonProcessManager
- Remove FIPCClient
- Remove Python IPC server parts

Day 3-4: Documentation
- Update all documentation
- Create migration guide
- Record demo video

Day 5: Release
- Final testing
- Code review
- Merge to main

### Backwards Compatibility

Maintain compatibility during migration:

```cpp
// Adapter pattern for gradual migration
class FAdastreaLLMAdapter
{
public:
    static void SendMessage(const FString& Message, FOnComplete OnComplete)
    {
        if (FAdastreaFeatureFlags::UseDirectLLM())
        {
            // New path: Direct C++ LLM
            UseNewLLMClient(Message, OnComplete);
        }
        else
        {
            // Old path: Python IPC
            UseOldIPCClient(Message, OnComplete);
        }
    }

private:
    static void UseNewLLMClient(const FString& Message, FOnComplete OnComplete);
    static void UseOldIPCClient(const FString& Message, FOnComplete OnComplete);
};
```

### Testing During Migration

**Create parallel test suites:**

```cpp
// Test both old and new implementations
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTestLLMCompatibility, 
    "Adastrea.Migration.LLMCompatibility",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FTestLLMCompatibility::RunTest(const FString& Parameters)
{
    FString TestMessage = TEXT("What is Unreal Engine?");
    
    // Test old implementation
    FString OldResult;
    {
        // ... use old IPC client
    }
    
    // Test new implementation  
    FString NewResult;
    {
        // ... use new direct LLM
    }
    
    // Results should be similar quality
    TestTrue(TEXT("Both implementations return non-empty results"), 
        !OldResult.IsEmpty() && !NewResult.IsEmpty());
    
    return true;
}
```

---

## 11. Best Practices & Design Patterns

### Error Handling

Use TResult<T> pattern for better error handling:

```cpp
template<typename T>
struct TResult
{
    bool bSuccess = false;
    T Value;
    FString ErrorMessage;
    
    static TResult<T> Success(const T& InValue)
    {
        TResult<T> Result;
        Result.bSuccess = true;
        Result.Value = InValue;
        return Result;
    }
    
    static TResult<T> Failure(const FString& Error)
    {
        TResult<T> Result;
        Result.bSuccess = false;
        Result.ErrorMessage = Error;
        return Result;
    }
    
    bool IsSuccess() const { return bSuccess; }
    bool IsFailure() const { return !bSuccess; }
};

// Usage example
TResult<TArray<FAssetInfo>> SearchAssets(const FString& Pattern)
{
    if (Pattern.IsEmpty())
    {
        return TResult<TArray<FAssetInfo>>::Failure(TEXT("Pattern cannot be empty"));
    }
    
    TArray<FAssetInfo> Assets = PerformSearch(Pattern);
    return TResult<TArray<FAssetInfo>>::Success(Assets);
}
```

### Async Operations

Use promises for async operations:

```cpp
// Async asset loading
TSharedRef<TPromise<TArray<FAssetInfo>>> LoadAssetsAsync(const FString& Path)
{
    TSharedRef<TPromise<TArray<FAssetInfo>>> Promise = 
        MakeShared<TPromise<TArray<FAssetInfo>>>();
    
    // Start async operation
    AsyncTask(ENamedThreads::AnyBackgroundThreadNormalTask, [Promise, Path]()
    {
        TArray<FAssetInfo> Assets = FAdastreaAssetService::SearchAssets(Path);
        
        // Complete on game thread
        AsyncTask(ENamedThreads::GameThread, [Promise, Assets]()
        {
            Promise->SetValue(Assets);
        });
    });
    
    return Promise;
}

// Usage
TSharedRef<TPromise<TArray<FAssetInfo>>> Promise = LoadAssetsAsync(TEXT("/Game/Characters"));
Promise->GetFuture().Then([](const TArray<FAssetInfo>& Assets)
{
    UE_LOG(LogAdastreaDirector, Log, TEXT("Loaded %d assets"), Assets.Num());
});
```

### Resource Management

Use RAII for resource cleanup:

```cpp
// Scope guard for Python execution context
class FPythonExecutionScope
{
public:
    FPythonExecutionScope()
    {
        // Setup execution context
        IPythonScriptPlugin::Get()->BeginPythonExecution();
    }
    
    ~FPythonExecutionScope()
    {
        // Cleanup
        IPythonScriptPlugin::Get()->EndPythonExecution();
    }
    
    FPythonExecutionScope(const FPythonExecutionScope&) = delete;
    FPythonExecutionScope& operator=(const FPythonExecutionScope&) = delete;
};

// Usage
void SafeExecutePython()
{
    FPythonExecutionScope Scope; // Automatic cleanup
    // ... execute Python code
} // Scope ends, cleanup happens
```

---

## 12. Reference Materials

### VibeUE Source Files

Study these key files from the VibeUE repository for implementation reference:

**Core Architecture:**
- `Source/VibeUE/Private/Chat/ChatSession.cpp` - Main chat session management
- `Source/VibeUE/Private/Chat/VibeUEAPIClient.cpp` - Direct LLM API calls
- `Source/VibeUE/Public/Core/Result.h` - TResult<T> error handling pattern

**Python Integration:**
- `Source/VibeUE/Private/Services/Python/PythonExecutionService.cpp` - IPythonScriptPlugin usage
- `Source/VibeUE/Private/Tools/ExecutePythonTool.cpp` - Python tool implementation

**Asset Discovery:**
- `Source/VibeUE/Private/Services/Blueprint/BlueprintDiscoveryService.cpp` - Runtime asset queries
- `Source/VibeUE/Private/Services/Material/MaterialDiscoveryService.cpp` - Material discovery
- `Source/VibeUE/Private/Services/UMG/UMGDiscoveryService.cpp` - Widget discovery

**Tool System:**
- `Source/VibeUE/Private/Tools/ToolRegistry.cpp` - Tool registration system
- `Source/VibeUE/Private/Tools/ToolDefinition.cpp` - Tool definition structure
- `Source/VibeUE/Private/Tools/*Tool.cpp` - 27+ built-in tool implementations

**MCP Protocol:**
- `Source/VibeUE/Private/MCP/MCPServer.cpp` - MCP server implementation
- `Source/VibeUE/Private/MCP/MCPTransport.cpp` - HTTP transport layer

### Unreal Engine Documentation

**Python Plugin:**
- [Scripting the Editor using Python](https://docs.unrealengine.com/5.3/en-US/scripting-the-unreal-editor-using-python/)
- [Python API Reference](https://docs.unrealengine.com/5.3/en-US/PythonAPI/)
- [IPythonScriptPlugin Interface](https://docs.unrealengine.com/5.3/en-US/API/Plugins/PythonScriptPlugin/IPythonScriptPlugin/)

**HTTP Module:**
- [HTTP Module Documentation](https://docs.unrealengine.com/5.3/en-US/API/Runtime/HTTP/)
- [IHttpRequest Interface](https://docs.unrealengine.com/5.3/en-US/API/Runtime/HTTP/Interfaces/IHttpRequest/)
- [FHttpModule](https://docs.unrealengine.com/5.3/en-US/API/Runtime/HTTP/FHttpModule/)

**Asset Registry:**
- [Asset Registry](https://docs.unrealengine.com/5.3/en-US/asset-management-in-unreal-engine/)
- [IAssetRegistry Interface](https://docs.unrealengine.com/5.3/en-US/API/Runtime/AssetRegistry/IAssetRegistry/)
- [FAssetData](https://docs.unrealengine.com/5.3/en-US/API/Runtime/AssetRegistry/FAssetData/)

**JSON:**
- [JSON in Unreal Engine](https://docs.unrealengine.com/5.3/en-US/API/Runtime/Json/)
- [FJsonObject](https://docs.unrealengine.com/5.3/en-US/API/Runtime/Json/Dom/FJsonObject/)
- [FJsonSerializer](https://docs.unrealengine.com/5.3/en-US/API/Runtime/Json/Serialization/FJsonSerializer/)

### Additional Resources

**LLM API Documentation:**
- [Google Gemini API](https://ai.google.dev/docs)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)

**MCP Protocol:**
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Examples](https://github.com/modelcontextprotocol/servers)

**Design Patterns:**
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
- [Unreal Engine Coding Standard](https://docs.unrealengine.com/5.3/en-US/epic-cplusplus-coding-standard-for-unreal-engine/)
- [RAII in Modern C++](https://en.cppreference.com/w/cpp/language/raii)

---

## 13. Troubleshooting Extended

### Issue: HTTP Requests Timing Out

**Symptoms:** LLM requests fail with timeout errors

**Solutions:**
1. Increase timeout value:
```cpp
Request->SetTimeout(120.0f); // 2 minutes
```

2. Check network connectivity:
```cpp
bool TestConnection()
{
    TSharedRef<IHttpRequest> Request = FHttpModule::Get().CreateRequest();
    Request->SetURL(TEXT("https://www.google.com"));
    Request->SetVerb(TEXT("GET"));
    Request->SetTimeout(5.0f);
    
    bool bCompleted = false;
    Request->OnProcessRequestComplete().BindLambda(
        [&bCompleted](FHttpRequestPtr Req, FHttpResponsePtr Response, bool bSuccess)
        {
            bCompleted = true;
            UE_LOG(LogAdastreaDirector, Log, TEXT("Connection test: %s"), 
                bSuccess ? TEXT("Success") : TEXT("Failed"));
        }
    );
    
    Request->ProcessRequest();
    
    // Wait for completion (with timeout)
    double StartTime = FPlatformTime::Seconds();
    while (!bCompleted && (FPlatformTime::Seconds() - StartTime) < 10.0)
    {
        FPlatformProcess::Sleep(0.1f);
    }
    
    return bCompleted;
}
```

3. Use proxy if behind firewall:
```cpp
Request->SetHeader(TEXT("Proxy-Authorization"), ProxyAuth);
```

### Issue: Asset Registry Returns Stale Data

**Symptoms:** Asset searches don't reflect recent changes

**Solutions:**
1. Force registry update:
```cpp
IAssetRegistry& Registry = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry").Get();
Registry.SearchAllAssets(true); // Force rescan
```

2. Listen for asset changes:
```cpp
void WatchAssetChanges()
{
    IAssetRegistry& Registry = GetAssetRegistry();
    
    Registry.OnAssetAdded().AddLambda([](const FAssetData& Asset)
    {
        UE_LOG(LogAdastreaDirector, Log, TEXT("Asset added: %s"), *Asset.AssetName.ToString());
        // Invalidate cache
    });
    
    Registry.OnAssetRemoved().AddLambda([](const FAssetData& Asset)
    {
        UE_LOG(LogAdastreaDirector, Log, TEXT("Asset removed: %s"), *Asset.AssetName.ToString());
        // Invalidate cache
    });
}
```

### Issue: Python Execution Fails Silently

**Symptoms:** Python code runs but produces no output or errors

**Solutions:**
1. Check log output mode:
```cpp
FPythonCommandEx Command;
Command.Command = Code;
Command.ExecutionMode = EPythonCommandExecutionMode::ExecuteFile;
Command.LogOutput.Empty(); // Clear before execution

bool bSuccess = PythonPlugin->ExecPythonCommandEx(Command);

// Check log output
for (const FPythonLogOutputEntry& Entry : Command.LogOutput)
{
    UE_LOG(LogAdastreaDirector, Log, TEXT("[Python %s] %s"), 
        *UEnum::GetValueAsString(Entry.Type),
        *Entry.Output);
}
```

2. Redirect Python stdout:
```cpp
FString PythonCode = TEXT(R"(
import sys
import io

# Redirect stdout to capture prints
output = io.StringIO()
sys.stdout = output

# Your code here
print("Hello from Python")

# Get output
result = output.getvalue()
sys.stdout = sys.__stdout__  # Restore
result
)");
```

---

## Next Steps

1. **Review** this implementation guide with your team
2. **Start** with Phase 1 (Python plugin integration)
3. **Test** each phase thoroughly before moving to next
4. **Document** any deviations or improvements
5. **Share** learnings with the community

Good luck with the migration! 🚀
