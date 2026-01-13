# VibeUE Implementation Guide for Adastrea-Director

## Purpose

This document provides concrete, actionable implementation guidance for adopting VibeUE patterns in Adastrea-Director. Each section includes code examples, step-by-step instructions, and specific files to create or modify.

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
        float ExecutionTimeMs
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

    return ConvertResult(Command, ExecutionTimeMs);
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

    return ConvertResult(Command, ExecutionTimeMs);
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
    float ExecutionTimeMs)
{
    FAdastreaScriptResult Result;
    // Success if there are no errors and we have a result
    Result.bSuccess = (CommandEx.LogOutput.Num() == 0) && !CommandEx.CommandResult.IsEmpty();
    Result.Output = CommandEx.CommandResult;
    Result.ExecutionTimeMs = ExecutionTimeMs;

    // Extract error messages
    for (const FPythonLogOutputEntry& Entry : CommandEx.LogOutput)
    {
        if (Entry.Type == EPythonLogOutputType::Error || Entry.Type == EPythonLogOutputType::Warning)
        {
            Result.bSuccess = false;
            Result.ErrorMessage += Entry.Output + TEXT("\n");
        }
    }

    Result.ErrorMessage.TrimEndInline();
    return Result;
}
```

### Step 4: Test Python Execution

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/Private/AdastreaScriptService.cpp` (add test command)

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
 */
class ADASTREADIRECTOR_API FAdastreaLLMClient
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

    // Setup callbacks
    if (OnStreamChunk.IsBound())
    {
        // Streaming mode
        Request->OnRequestProgress().BindLambda(
            [this, OnStreamChunk](FHttpRequestPtr Req, int32 BytesSent, int32 BytesReceived)
            {
                OnStreamDataReceived(Req, BytesSent, BytesReceived, OnStreamChunk);
            }
        );
    }

    Request->OnProcessRequestComplete().BindLambda(
        [this, OnComplete](FHttpRequestPtr Req, FHttpResponsePtr Response, bool bWasSuccessful)
        {
            OnResponseReceived(Req, Response, bWasSuccessful, OnComplete);
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
        TSharedPtr<FJsonObject> ContentObj = Candidate->GetObjectField(TEXT("content"));
        
        const TArray<TSharedPtr<FJsonValue>>* Parts;
        if (ContentObj->TryGetArrayField(TEXT("parts"), Parts))
        {
            for (const TSharedPtr<FJsonValue>& PartValue : *Parts)
            {
                TSharedPtr<FJsonObject> Part = PartValue->AsObject();
                
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
                    ToolCall.Arguments = FunctionCall->GetObjectField(TEXT("args"));
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
    // Get current response content
    FString ResponseSoFar = Request->GetResponse()->GetContentAsString();
    
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

### Step 4: Test LLM Client

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
        Filter.ClassPaths.Add(FTopLevelAssetPath(FName(*ClassName)));
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

## 4. Quick Migration Checklist

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

## 5. Testing Strategy

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

## 6. Common Pitfalls & Solutions

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

## Next Steps

1. **Review** this implementation guide with your team
2. **Start** with Phase 1 (Python plugin integration)
3. **Test** each phase thoroughly before moving to next
4. **Document** any deviations or improvements
5. **Share** learnings with the community

Good luck with the migration! 🚀
