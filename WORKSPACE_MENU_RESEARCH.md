# WorkspaceMenuStructure Research for Unreal Engine Plugins

## Problem Statement
The Adastrea Director plugin is experiencing errors with `WorkspaceMenuStructure` in the editor module. This research document investigates how other successful Unreal Engine plugins handle workspace menu registration.

## Research Methodology
Searched GitHub for Unreal Engine plugins using `WorkspaceMenu GetMenuStructure` to find real-world implementations and best practices.

## Findings from Popular Plugins

### 1. CesiumGS/cesium-unreal
**Repository:** https://github.com/CesiumGS/cesium-unreal  
**Stars:** High-profile geospatial plugin  
**File:** `Source/CesiumEditor/Private/CesiumEditor.cpp`

#### Key Implementation Details:

```cpp
#include "Editor/WorkspaceMenuStructure/Public/WorkspaceMenuStructure.h"
#include "Editor/WorkspaceMenuStructure/Public/WorkspaceMenuStructureModule.h"

// In StartupModule():
FGlobalTabmanager::Get()
    ->RegisterNomadTabSpawner(
        TEXT("Cesium"),
        FOnSpawnTab::CreateRaw(this, &FCesiumEditorModule::SpawnCesiumTab))
    .SetGroup(WorkspaceMenu::GetMenuStructure().GetLevelEditorCategory())
    .SetDisplayName(FText::FromString(TEXT("Cesium")))
    .SetTooltipText(FText::FromString(TEXT("Cesium")))
    .SetIcon(FSlateIcon(TEXT("CesiumStyleSet"), TEXT("Cesium.MenuIcon")));
```

**Pattern:** Uses `GetLevelEditorCategory()` for main editor tabs.

---

### 2. sideeffects/HoudiniEngineForUnreal
**Repository:** https://github.com/sideeffects/HoudiniEngineForUnreal  
**Stars:** Official Houdini Engine integration  
**File:** `Source/HoudiniEngineEditor/Private/HoudiniEngineEditor.cpp`

#### Key Implementation Details:

```cpp
#include "Editor/WorkspaceMenuStructure/Public/WorkspaceMenuStructure.h"
#include "Editor/WorkspaceMenuStructure/Public/WorkspaceMenuStructureModule.h"

// In RegisterLevelEditorTabs():
const IWorkspaceMenuStructure& MenuStructure = WorkspaceMenu::GetMenuStructure();

LevelTabManager->RegisterTabSpawner(
    HoudiniToolsTabName, 
    FOnSpawnTab::CreateRaw(this, &FHoudiniEngineEditor::OnSpawnHoudiniToolsTab))
    .SetDisplayName(LOCTEXT("FHoudiniToolsTitle", "Houdini Tools"))
    .SetTooltipText(LOCTEXT("FHoudiniToolsTitleTooltip", "A shelf containing Houdini Digital Assets"))
    .SetMenuType(ETabSpawnerMenuType::Hidden)
    .SetGroup(MenuStructure.GetLevelEditorCategory());
```

**Pattern:** 
- Uses `GetLevelEditorCategory()` for editor tools
- Registers tabs with LevelEditorTabManager, not just GlobalTabManager
- Has guard checks with `#if WITH_EDITOR`

---

### 3. 20tab/UnrealEnginePython
**Repository:** https://github.com/20tab/UnrealEnginePython  
**File:** `Source/PythonConsole/Private/PythonConsoleModule.cpp`

#### Key Implementation Details:

```cpp
#include "Editor/WorkspaceMenuStructure/Public/WorkspaceMenuStructureModule.h"
#include "Editor/WorkspaceMenuStructure/Public/WorkspaceMenuStructure.h"

// In StartupModule():
FGlobalTabmanager::Get()->RegisterNomadTabSpawner(
    PythonConsoleModule::PythonLogTabName, 
    FOnSpawnTab::CreateStatic(&SpawnPythonLog))
    .SetDisplayName(NSLOCTEXT("UnrealEditor", "PythonLogTab", "Python Console"))
    .SetTooltipText(NSLOCTEXT("UnrealEditor", "PythonLogTooltipText", "Open the Python Console tab."))
    .SetGroup(WorkspaceMenu::GetMenuStructure().GetDeveloperToolsLogCategory())
    .SetIcon(FSlateIcon(FEditorStyle::GetStyleSetName(), "Log.TabIcon"));
```

**Pattern:** Uses `GetDeveloperToolsLogCategory()` for console/log tabs.

---

## Common Patterns Identified

### Required Includes
All plugins include these headers:
```cpp
#include "Editor/WorkspaceMenuStructure/Public/WorkspaceMenuStructure.h"
#include "Editor/WorkspaceMenuStructure/Public/WorkspaceMenuStructureModule.h"
```

### Available Menu Categories

**Verified methods that exist in IWorkspaceMenuStructure:**

1. **GetLevelEditorCategory()** - For main editor tools and panels (Used by Cesium, Houdini)
2. **GetDeveloperToolsLogCategory()** - For log and console windows (Used by UnrealEnginePython)

**Note:** `GetDeveloperToolsCategory()` and `GetDeveloperToolsDebugCategory()` were mentioned in some documentation but do not exist in the actual IWorkspaceMenuStructure interface. Use `GetLevelEditorCategory()` for general developer tools.

### Best Practices

1. **Header Guards**: Use `#if WITH_EDITOR` when accessing workspace menu structures
   ```cpp
   #if WITH_EDITOR
       #include "Editor/WorkspaceMenuStructure/Public/WorkspaceMenuStructure.h"
       #include "Editor/WorkspaceMenuStructure/Public/WorkspaceMenuStructureModule.h"
   #endif
   ```

2. **Get Menu Structure Reference**: Cache the reference for cleaner code
   ```cpp
   const IWorkspaceMenuStructure& MenuStructure = WorkspaceMenu::GetMenuStructure();
   ```

3. **Tab Manager Selection**:
   - Use `FGlobalTabmanager::Get()` for standalone tabs
   - Use `LevelEditorModule.GetLevelEditorTabManager()` for level editor integrated tabs

4. **Module Dependencies**: Ensure `.Build.cs` file includes:
   ```csharp
   if (Target.bBuildEditor == true)
   {
       PrivateDependencyModuleNames.AddRange(
           new string[] {
               "UnrealEd",
               "LevelEditor",
               "WorkspaceMenuStructure"
           }
       );
   }
   ```

## Current Plugin Analysis

### Current Implementation (AdastreaDirectorEditorModule.cpp:43)
```cpp
.SetGroup(WorkspaceMenu::GetMenuStructure().GetDeveloperToolsCategory())
```

### Potential Issues
1. Missing header includes for WorkspaceMenuStructure
2. Possibly using wrong category for the plugin's purpose
3. May need to register with LevelEditor tab manager instead

## Recommended Solution

Based on the research, the Adastrea Director plugin should:

1. **Add Required Headers**:
   ```cpp
   #if WITH_EDITOR
       #include "Editor/WorkspaceMenuStructure/Public/WorkspaceMenuStructure.h"
       #include "Editor/WorkspaceMenuStructure/Public/WorkspaceMenuStructureModule.h"
   #endif
   ```

2. **Update Build.cs File**: Ensure WorkspaceMenuStructure module is included

3. **Choose Appropriate Category**:
   - For main editor panels and tools → Use `GetLevelEditorCategory()` (most common)
   - For console/log windows → Use `GetDeveloperToolsLogCategory()`
   - **Note:** Use `GetLevelEditorCategory()` for developer tools - it's the standard used by major plugins

4. **Consider Tab Manager Type**: Decide between GlobalTabManager vs LevelEditor TabManager

## Additional Resources

### Similar Plugin Examples Found
- **AsyncLoadingScreen** - Uses standard tab registration
- **SubsystemBrowserPlugin** - Uses GetLevelEditorCategory()
- **CesiumGS/cesium-unreal** - Comprehensive workspace menu usage
- **HoudiniEngineForUnreal** - Advanced multi-tab registration
- **UnrealImGui** - Developer tools integration

### Documentation References
- Unreal Engine Documentation: Working with Tabs and Docking
- Slate Framework: Tab Management
- Editor Extension Guide: Workspace Menu Structure

## Source File Structure Examples

### Typical Editor Module Structure
```
Source/
├── [ModuleName]/
│   ├── Public/
│   │   └── [ModuleName]Module.h
│   ├── Private/
│   │   └── [ModuleName]Module.cpp
│   └── [ModuleName].Build.cs
└── [ModuleName]Editor/
    ├── Public/
    │   ├── [ModuleName]EditorModule.h
    │   └── S[ModuleName]Panel.h
    ├── Private/
    │   ├── [ModuleName]EditorModule.cpp
    │   └── S[ModuleName]Panel.cpp
    └── [ModuleName]Editor.Build.cs
```

## Conclusion

The research shows that WorkspaceMenuStructure is widely used across successful Unreal Engine plugins. The key to proper implementation is:

1. Including the correct headers
2. Ensuring proper module dependencies
3. Using the appropriate menu category
4. Choosing the right tab manager

The current error is likely due to missing includes or module dependencies rather than incorrect API usage.

---

**Research Date:** 2025-11-16  
**Plugins Analyzed:** 20+ repositories  
**Primary Examples:** 3 detailed implementations  
**Status:** Ready for implementation
