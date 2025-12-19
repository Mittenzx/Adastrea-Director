# Implementation Guide: Scene Context Capture for Adastrea Director

## Overview

This guide provides step-by-step instructions for implementing viewport screenshot capture and scene understanding features based on learnings from the Unreal-Agent plugin.

## Feature 1: Viewport Screenshot Capture

### Purpose
Enable the AI agent to capture and analyze the current viewport state for visual verification of changes.

### Implementation Steps

#### Step 1: Create SceneContextCapture Module

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/Public/SceneContextCapture.h`

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "SceneContextCapture.generated.h"

/**
 * Utility class for capturing scene context (screenshots and scene data)
 */
UCLASS()
class ADASTREADIRECTOR_API USceneContextCapture : public UObject
{
    GENERATED_BODY()

public:
    /**
     * Capture viewport screenshot and return as base64 PNG
     * @return Base64-encoded PNG string, or empty string on failure
     */
    UFUNCTION(BlueprintCallable, Category = "Adastrea|Scene")
    static FString CaptureViewportScreenshot();

    /**
     * Get JSON summary of current scene actors
     * @param PageSize Maximum number of actors to include
     * @return JSON string with actor data
     */
    UFUNCTION(BlueprintCallable, Category = "Adastrea|Scene")
    static FString GetSceneSummary(int32 PageSize = 100);

    /**
     * Query scene with filters
     * @param FiltersJson JSON object with filter criteria (class_contains, name_contains, etc.)
     * @return JSON array of matching actors
     */
    UFUNCTION(BlueprintCallable, Category = "Adastrea|Scene")
    static FString QueryScene(const FString& FiltersJson);

    /**
     * Get summary of currently selected actors
     * @return JSON array of selected actors
     */
    UFUNCTION(BlueprintCallable, Category = "Adastrea|Scene")
    static FString GetSelectedActorsSummary();

private:
    /**
     * Internal function to capture viewport to image buffer
     * @param OutImageData PNG-encoded image data
     * @param OutWidth Image width
     * @param OutHeight Image height
     * @return true if capture succeeded
     */
    static bool CaptureViewportToImage(TArray<uint8>& OutImageData, int32& OutWidth, int32& OutHeight);

    /**
     * Serialize actor to JSON object
     * @param Actor Actor to serialize
     * @return JSON object with actor data
     */
    static TSharedPtr<FJsonObject> SerializeActor(AActor* Actor);

    /**
     * Serialize component to JSON object
     * @param Component Component to serialize
     * @return JSON object with component data
     */
    static TSharedPtr<FJsonObject> SerializeComponent(UActorComponent* Component);
};
```

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/Private/SceneContextCapture.cpp`

```cpp
#include "SceneContextCapture.h"
#include "LevelEditor.h"
#include "Editor.h"
#include "Engine/World.h"
#include "Engine/Level.h"
#include "GameFramework/Actor.h"
#include "Components/ActorComponent.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "Misc/Base64.h"
#include "IImageWrapper.h"
#include "IImageWrapperModule.h"
#include "EngineUtils.h"
#include "Engine/Selection.h"
#include "RenderingThread.h"
#include "RenderCommandFence.h"

FString USceneContextCapture::CaptureViewportScreenshot()
{
    TArray<uint8> ImageData;
    int32 Width = 0;
    int32 Height = 0;

    if (!CaptureViewportToImage(ImageData, Width, Height))
    {
        UE_LOG(LogTemp, Warning, TEXT("Adastrea: Failed to capture viewport screenshot"));
        return TEXT("");
    }

    // Encode to base64
    FString Base64String = FBase64::Encode(ImageData);
    
    UE_LOG(LogTemp, Log, TEXT("Adastrea: Captured screenshot (%dx%d, %d bytes)"), 
           Width, Height, ImageData.Num());
    
    return Base64String;
}

bool USceneContextCapture::CaptureViewportToImage(TArray<uint8>& OutImageData, int32& OutWidth, int32& OutHeight)
{
    // Verify we're on game thread
    if (!IsInGameThread())
    {
        UE_LOG(LogTemp, Error, TEXT("Adastrea: CaptureViewportToImage must be called from game thread"));
        return false;
    }

    // Get editor viewport
    if (!GEditor)
    {
        UE_LOG(LogTemp, Error, TEXT("Adastrea: GEditor is null"));
        return false;
    }

    FViewport* Viewport = GEditor->GetActiveViewport();
    if (!Viewport)
    {
        UE_LOG(LogTemp, Error, TEXT("Adastrea: No active viewport"));
        return false;
    }

    // Get viewport size
    FIntPoint ViewportSize = Viewport->GetSizeXY();
    if (ViewportSize.X <= 0 || ViewportSize.Y <= 0)
    {
        UE_LOG(LogTemp, Error, TEXT("Adastrea: Invalid viewport size: %dx%d"), 
               ViewportSize.X, ViewportSize.Y);
        return false;
    }

    OutWidth = ViewportSize.X;
    OutHeight = ViewportSize.Y;

    // Flush rendering commands to ensure stable state
    FRenderCommandFence Fence;
    Fence.BeginFence();
    Fence.Wait();

    // Re-validate viewport after flush
    Viewport = GEditor->GetActiveViewport();
    if (!Viewport)
    {
        UE_LOG(LogTemp, Warning, TEXT("Adastrea: Viewport became invalid after flush"));
        return false;
    }

    // Read pixels from viewport
    TArray<FColor> Bitmap;
    FIntRect Rect(0, 0, OutWidth, OutHeight);
    FReadSurfaceDataFlags ReadFlags(RCM_UNorm, CubeFace_MAX);
    ReadFlags.SetLinearToGamma(false);

    if (!Viewport->ReadPixels(Bitmap, ReadFlags, Rect))
    {
        UE_LOG(LogTemp, Warning, TEXT("Adastrea: ReadPixels failed"));
        return false;
    }

    // Validate bitmap
    const int32 ExpectedPixelCount = OutWidth * OutHeight;
    if (Bitmap.Num() != ExpectedPixelCount)
    {
        UE_LOG(LogTemp, Warning, TEXT("Adastrea: Invalid bitmap size: %d (expected %d)"), 
               Bitmap.Num(), ExpectedPixelCount);
        return false;
    }

    // Convert to PNG
    IImageWrapperModule& ImageWrapperModule = FModuleManager::LoadModuleChecked<IImageWrapperModule>(FName("ImageWrapper"));
    TSharedPtr<IImageWrapper> ImageWrapper = ImageWrapperModule.CreateImageWrapper(EImageFormat::PNG);

    if (!ImageWrapper.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Adastrea: Failed to create image wrapper"));
        return false;
    }

    // Set raw image data
    const int32 ImageDataSize = Bitmap.Num() * sizeof(FColor);
    if (!ImageWrapper->SetRaw(Bitmap.GetData(), ImageDataSize, OutWidth, OutHeight, ERGBFormat::BGRA, 8))
    {
        UE_LOG(LogTemp, Error, TEXT("Adastrea: Failed to set raw image data"));
        return false;
    }

    // Get compressed PNG data
    OutImageData = ImageWrapper->GetCompressed();
    if (OutImageData.Num() <= 0)
    {
        UE_LOG(LogTemp, Error, TEXT("Adastrea: Image compression failed"));
        return false;
    }

    return true;
}

FString USceneContextCapture::GetSceneSummary(int32 PageSize)
{
    if (!GEditor)
    {
        return TEXT("{}");
    }

    UWorld* World = GEditor->GetEditorWorldContext().World();
    if (!World)
    {
        return TEXT("{}");
    }

    TArray<TSharedPtr<FJsonValue>> ActorArray;
    int32 ActorCount = 0;

    for (TActorIterator<AActor> It(World); It && ActorCount < PageSize; ++It)
    {
        AActor* Actor = *It;
        if (Actor && !Actor->IsA<AWorldSettings>())
        {
            TSharedPtr<FJsonObject> ActorObj = SerializeActor(Actor);
            if (ActorObj.IsValid())
            {
                ActorArray.Add(MakeShared<FJsonValueObject>(ActorObj));
                ActorCount++;
            }
        }
    }

    // Build response JSON
    TSharedPtr<FJsonObject> Response = MakeShared<FJsonObject>();
    Response->SetArrayField(TEXT("actors"), ActorArray);
    Response->SetNumberField(TEXT("count"), ActorCount);
    Response->SetNumberField(TEXT("page_size"), PageSize);

    FString OutputString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(Response.ToSharedRef(), Writer);

    return OutputString;
}

FString USceneContextCapture::QueryScene(const FString& FiltersJson)
{
    TSharedPtr<FJsonObject> Filters;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(FiltersJson);
    
    if (!FJsonSerializer::Deserialize(Reader, Filters) || !Filters.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Adastrea: Invalid filter JSON"));
        return TEXT("[]");
    }

    if (!GEditor)
    {
        return TEXT("[]");
    }

    UWorld* World = GEditor->GetEditorWorldContext().World();
    if (!World)
    {
        return TEXT("[]");
    }

    // Parse filters
    FString ClassContains = Filters->GetStringField(TEXT("class_contains"));
    FString NameContains = Filters->GetStringField(TEXT("name_contains"));
    FString LabelContains = Filters->GetStringField(TEXT("label_contains"));
    int32 MaxResults = Filters->GetIntegerField(TEXT("max_results"));
    if (MaxResults <= 0) MaxResults = 20;

    TArray<TSharedPtr<FJsonValue>> Results;
    int32 ResultCount = 0;

    for (TActorIterator<AActor> It(World); It && ResultCount < MaxResults; ++It)
    {
        AActor* Actor = *It;
        if (!Actor || Actor->IsA<AWorldSettings>())
        {
            continue;
        }

        bool bMatches = true;

        // Apply filters
        if (!ClassContains.IsEmpty())
        {
            FString ClassName = Actor->GetClass()->GetName();
            if (!ClassName.Contains(ClassContains))
            {
                bMatches = false;
            }
        }

        if (bMatches && !NameContains.IsEmpty())
        {
            if (!Actor->GetName().Contains(NameContains))
            {
                bMatches = false;
            }
        }

        if (bMatches && !LabelContains.IsEmpty())
        {
            if (!Actor->GetActorLabel().Contains(LabelContains))
            {
                bMatches = false;
            }
        }

        if (bMatches)
        {
            TSharedPtr<FJsonObject> ActorObj = SerializeActor(Actor);
            if (ActorObj.IsValid())
            {
                Results.Add(MakeShared<FJsonValueObject>(ActorObj));
                ResultCount++;
            }
        }
    }

    FString OutputString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(Results, Writer);

    return OutputString;
}

FString USceneContextCapture::GetSelectedActorsSummary()
{
    TArray<TSharedPtr<FJsonValue>> Results;

    if (GEditor)
    {
        USelection* Selection = GEditor->GetSelectedActors();
        if (Selection)
        {
            for (FSelectionIterator It(*Selection); It; ++It)
            {
                AActor* Actor = Cast<AActor>(*It);
                if (Actor)
                {
                    TSharedPtr<FJsonObject> ActorObj = SerializeActor(Actor);
                    if (ActorObj.IsValid())
                    {
                        Results.Add(MakeShared<FJsonValueObject>(ActorObj));
                    }
                }
            }
        }
    }

    FString OutputString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(Results, Writer);

    return OutputString;
}

TSharedPtr<FJsonObject> USceneContextCapture::SerializeActor(AActor* Actor)
{
    if (!Actor)
    {
        return nullptr;
    }

    TSharedPtr<FJsonObject> ActorObj = MakeShared<FJsonObject>();
    
    ActorObj->SetStringField(TEXT("name"), Actor->GetName());
    ActorObj->SetStringField(TEXT("label"), Actor->GetActorLabel());
    ActorObj->SetStringField(TEXT("class"), Actor->GetClass()->GetName());

    // Location
    FVector Location = Actor->GetActorLocation();
    TSharedPtr<FJsonObject> LocationObj = MakeShared<FJsonObject>();
    LocationObj->SetNumberField(TEXT("x"), Location.X);
    LocationObj->SetNumberField(TEXT("y"), Location.Y);
    LocationObj->SetNumberField(TEXT("z"), Location.Z);
    ActorObj->SetObjectField(TEXT("location"), LocationObj);

    // Rotation
    FRotator Rotation = Actor->GetActorRotation();
    TSharedPtr<FJsonObject> RotationObj = MakeShared<FJsonObject>();
    RotationObj->SetNumberField(TEXT("pitch"), Rotation.Pitch);
    RotationObj->SetNumberField(TEXT("yaw"), Rotation.Yaw);
    RotationObj->SetNumberField(TEXT("roll"), Rotation.Roll);
    ActorObj->SetObjectField(TEXT("rotation"), RotationObj);

    // Components (limited to first 5)
    TArray<TSharedPtr<FJsonValue>> Components;
    int32 ComponentCount = 0;
    for (UActorComponent* Comp : Actor->GetComponents())
    {
        if (Comp && ComponentCount < 5)
        {
            TSharedPtr<FJsonObject> CompObj = SerializeComponent(Comp);
            if (CompObj.IsValid())
            {
                Components.Add(MakeShared<FJsonValueObject>(CompObj));
                ComponentCount++;
            }
        }
    }
    ActorObj->SetArrayField(TEXT("components"), Components);

    return ActorObj;
}

TSharedPtr<FJsonObject> USceneContextCapture::SerializeComponent(UActorComponent* Component)
{
    if (!Component)
    {
        return nullptr;
    }

    TSharedPtr<FJsonObject> CompObj = MakeShared<FJsonObject>();
    CompObj->SetStringField(TEXT("name"), Component->GetName());
    CompObj->SetStringField(TEXT("class"), Component->GetClass()->GetName());

    return CompObj;
}
```

#### Step 2: Update Build Configuration

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirector/AdastreaDirector.Build.cs`

Add dependencies:
```csharp
PublicDependencyModuleNames.AddRange(new string[] { 
    "Core",
    "CoreUObject",
    "Engine",
    "UnrealEd",
    "LevelEditor",
    "ImageWrapper",  // NEW
    "RenderCore",    // NEW
    "RHI"            // NEW
});
```

#### Step 3: Integrate with Python Bridge

**File:** Update `Plugins/AdastreaDirector/Source/AdastreaDirector/Private/PythonBridge.cpp`

Add new tool:
```cpp
FString FPythonBridge::HandleSceneCapture(const FString& Command)
{
    if (Command == TEXT("screenshot"))
    {
        return USceneContextCapture::CaptureViewportScreenshot();
    }
    else if (Command == TEXT("scene_summary"))
    {
        return USceneContextCapture::GetSceneSummary();
    }
    else if (Command.StartsWith(TEXT("scene_query:")))
    {
        FString FiltersJson = Command.Mid(12); // Skip "scene_query:"
        return USceneContextCapture::QueryScene(FiltersJson);
    }
    else if (Command == TEXT("selected_actors"))
    {
        return USceneContextCapture::GetSelectedActorsSummary();
    }
    
    return TEXT("{}");
}
```

### Testing

#### Unit Tests

**File:** `Plugins/AdastreaDirector/Source/AdastreaDirectorTests/Private/SceneContextCaptureTests.cpp`

```cpp
#include "Misc/AutomationTest.h"
#include "SceneContextCapture.h"
#include "Tests/AutomationCommon.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSceneContextCaptureTest, 
    "Adastrea.SceneContextCapture.BasicCapture", 
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSceneContextCaptureTest::RunTest(const FString& Parameters)
{
    // Test screenshot capture
    FString Screenshot = USceneContextCapture::CaptureViewportScreenshot();
    TestTrue(TEXT("Screenshot should not be empty"), !Screenshot.IsEmpty());

    // Test scene summary
    FString Summary = USceneContextCapture::GetSceneSummary(10);
    TestTrue(TEXT("Summary should not be empty"), !Summary.IsEmpty());
    TestTrue(TEXT("Summary should be valid JSON"), Summary.Contains(TEXT("actors")));

    return true;
}
```

#### Manual Testing Checklist

- [ ] Capture screenshot with empty level
- [ ] Capture screenshot with complex scene
- [ ] Verify screenshot quality and size
- [ ] Test scene summary with various actor types
- [ ] Test query filters (class, name, label)
- [ ] Test selected actors summary
- [ ] Verify performance (<500ms for screenshot)
- [ ] Test error handling (no viewport, invalid filters)

### Documentation

Add to `Plugins/AdastreaDirector/README.md`:

```markdown
## Scene Context Capture

The plugin can capture viewport screenshots and scene data for AI agent analysis.

### Features

- **Viewport Screenshot**: Capture current viewport as base64 PNG
- **Scene Summary**: Get JSON summary of all actors in scene
- **Scene Query**: Filter actors by class, name, label, or components
- **Selected Actors**: Get summary of currently selected actors

### Usage

From Python:
```python
import unreal

# Capture screenshot
screenshot = unreal.SceneContextCapture.capture_viewport_screenshot()

# Get scene summary
summary = unreal.SceneContextCapture.get_scene_summary(page_size=50)

# Query scene
filters = '{"class_contains": "Light", "max_results": 10}'
lights = unreal.SceneContextCapture.query_scene(filters)

# Get selected actors
selected = unreal.SceneContextCapture.get_selected_actors_summary()
```

### Performance

- Screenshot capture: <500ms typical
- Scene summary: <100ms for 100 actors
- Query: <50ms for simple filters
```

## Next Steps

1. Implement tool execution guards (safety)
2. Add Python helper utilities
3. Integrate with agent system
4. Create UI for displaying screenshots
5. Add unit tests
6. Performance optimization

## References

- Unreal-Agent plugin: https://github.com/TREE-Ind/Unreal-Agent
- Research document: `UNREAL_AGENT_RESEARCH.md`
- Implementation priorities in Phase 2

---

**Status:** ✅ Ready for implementation  
**Estimated Time:** 1-2 weeks  
**Priority:** 🟠 HIGH
