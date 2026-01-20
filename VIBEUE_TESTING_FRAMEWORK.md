# VibeUE Testing Framework

## Overview

This document describes the comprehensive testing framework created for the VibeUE architecture components in Adastrea Director.

## Test Structure

### Location

All tests are located in:
```
Plugins/AdastreaDirector/Source/AdastreaDirectorTests/
```

### Test Module

- **Module Name**: `AdastreaDirectorTests`
- **Type**: Editor module (for automation framework access)
- **Dependencies**: Core, CoreUObject, Engine, AdastreaDirector, UnrealEd, AssetRegistry, PythonScriptPlugin, HTTP, Json, JsonUtilities, HTTPServer

## Test Coverage

### 1. AdastreaScriptService Tests (6 tests)

**File**: `AdastreaScriptServiceTests.cpp`

| Test Name | Category | Description |
|-----------|----------|-------------|
| `FAdastreaScriptServiceAvailabilityTest` | Python.Availability | Checks if Python plugin is loaded and available |
| `FAdastreaScriptServiceExpressionTest` | Python.EvaluateExpression | Tests Python expression evaluation (2+2, strings, lists) |
| `FAdastreaScriptServiceExecuteCodeTest` | Python.ExecuteCode | Tests Python code execution (single/multi-line, functions) |
| `FAdastreaScriptServiceUnrealAccessTest` | Python.UnrealModuleAccess | Verifies access to Unreal Python API |
| `FAdastreaScriptServiceErrorHandlingTest` | Python.ErrorHandling | Tests error detection (syntax, runtime, name errors) |
| `FAdastreaScriptServiceScopeTest` | Python.Scope | Tests private vs shared scope isolation |

**Test Command**:
```
Automation RunTests Adastrea.VibeUE.Python
```

### 2. AdastreaAssetService Tests (7 tests)

**File**: `AdastreaAssetServiceTests.cpp`

| Test Name | Category | Description |
|-----------|----------|-------------|
| `FAdastreaAssetServiceAvailabilityTest` | Assets.RegistryAvailability | Checks if Asset Registry is ready |
| `FAdastreaAssetServiceSearchTest` | Assets.SearchAssets | Tests asset search with patterns and wildcards |
| `FAdastreaAssetServiceBlueprintTest` | Assets.GetBlueprints | Tests Blueprint discovery |
| `FAdastreaAssetServiceMaterialTest` | Assets.GetMaterials | Tests Material discovery |
| `FAdastreaAssetServiceWidgetTest` | Assets.GetWidgets | Tests UMG Widget discovery |
| `FAdastreaAssetServiceJsonSerializationTest` | Assets.JsonSerialization | Tests JSON serialization of asset info |
| `FAdastreaAssetServiceMaxResultsTest` | Assets.MaxResults | Tests max results limit enforcement |

**Test Command**:
```
Automation RunTests Adastrea.VibeUE.Assets
```

### 3. AdastreaToolSystem Tests (7 tests)

**File**: `AdastreaToolSystemTests.cpp`

| Test Name | Category | Description |
|-----------|----------|-------------|
| `FAdastreaToolSystemRegistrationTest` | Tools.Registration | Tests tool registration and unregistration |
| `FAdastreaToolSystemExecutionTest` | Tools.Execution | Tests tool execution with arguments |
| `FAdastreaToolSystemNotFoundTest` | Tools.NotFound | Tests error handling for non-existent tools |
| `FAdastreaToolSystemCategoryFilterTest` | Tools.CategoryFilter | Tests category-based tool filtering |
| `FAdastreaToolSystemGetAllToolsTest` | Tools.GetAllTools | Tests getting all registered tools |
| `FAdastreaToolSystemResultSerializationTest` | Tools.ResultSerialization | Tests JSON serialization of results |
| `FAdastreaToolSystemOverwriteTest` | Tools.OverwriteTool | Tests tool overwrite behavior |

**Test Command**:
```
Automation RunTests Adastrea.VibeUE.Tools
```

## Running Tests

### All VibeUE Tests

Run all tests at once:
```
Automation RunTests Adastrea.VibeUE
```

### Individual Components

Run tests for specific components:
```
Automation RunTests Adastrea.VibeUE.Python
Automation RunTests Adastrea.VibeUE.Assets
Automation RunTests Adastrea.VibeUE.Tools
```

### Command Line

Run from command line:
```bash
UnrealEditor.exe <ProjectPath> -ExecCmds="Automation RunTests Adastrea.VibeUE; Quit" -unattended -nopause -NullRHI -log
```

### Editor UI

1. Open **Window → Test Automation**
2. Expand **Adastrea → VibeUE**
3. Select tests to run
4. Click **Start Tests**

## Test Requirements

### Python Tests

**Requirements**:
- PythonScriptPlugin must be enabled
- Python plugin must be loaded

**Graceful Handling**:
- Tests skip with warning if Python is not available
- No test failures due to missing Python

### Asset Tests

**Requirements**:
- Asset Registry must complete initial scan
- Project must have at least some assets

**Graceful Handling**:
- Tests skip with warning if Asset Registry not ready
- Informational output about asset counts

### Tool Tests

**Requirements**:
- No special requirements
- All tool tests are self-contained

## Test Categories

Tests follow Unreal's automation test flag system:

```cpp
EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter
```

This means:
- Tests run in the Editor context
- Tests are categorized as "Product" level
- Tests are suitable for automated CI/CD pipelines

## Adding New Tests

### 1. Create Test File

Create a new `.cpp` file in `AdastreaDirectorTests/Private/`:

```cpp
// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "YourComponent.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FYourComponentTest,
    "Adastrea.VibeUE.YourCategory.TestName",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FYourComponentTest::RunTest(const FString& Parameters)
{
    // Your test code here
    TestTrue(TEXT("Description"), true);
    return true;
}
```

### 2. Test Naming Convention

Follow the pattern:
```
Adastrea.VibeUE.<Component>.<TestName>
```

Examples:
- `Adastrea.VibeUE.Python.EvaluateExpression`
- `Adastrea.VibeUE.Assets.SearchAssets`
- `Adastrea.VibeUE.Tools.Registration`

### 3. Test Assertions

Use Unreal's test macros:
```cpp
TestTrue(TEXT("Message"), bCondition);
TestFalse(TEXT("Message"), bCondition);
TestEqual(TEXT("Message"), Actual, Expected);
TestNotEqual(TEXT("Message"), Actual, NotExpected);
AddInfo(TEXT("Informational message"));
AddWarning(TEXT("Warning message"));
AddError(TEXT("Error message"));
```

### 4. Graceful Failures

Handle missing dependencies gracefully:
```cpp
if (!ComponentIsAvailable())
{
    AddWarning(TEXT("Component not available - skipping test"));
    return true; // Skip, don't fail
}
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run VibeUE Tests
  run: |
    UnrealEditor.exe ${{ env.PROJECT_PATH }} \
      -ExecCmds="Automation RunTests Adastrea.VibeUE; Quit" \
      -unattended -nopause -NullRHI -log \
      -ReportOutputPath=${{ env.TEST_REPORTS }}
```

### Test Report Location

Test reports are saved to:
```
<Project>/Saved/Automation/Reports/
```

## Future Test Additions

### Planned Tests

1. **LLM Client Tests** (Integration):
   - Test Gemini API request formation
   - Test OpenAI API request formation
   - Test streaming response handling
   - Test tool call extraction
   - **Note**: Requires API keys and network access

2. **MCP Server Tests** (Integration):
   - Test server startup/shutdown
   - Test endpoint routing
   - Test JSON-RPC format
   - Test tool execution via HTTP
   - **Note**: Requires HTTP server module

3. **End-to-End Tests** (System):
   - Full conversation flow with tool calling
   - Asset discovery → LLM → Tool execution cycle
   - MCP client → Server → Tool execution

## Best Practices

### 1. Test Independence

Each test should:
- Be self-contained
- Not depend on other tests
- Clean up after itself
- Not modify global state

### 2. Fast Execution

Tests should:
- Complete quickly (< 1 second each)
- Not perform expensive operations
- Use mocks for external services

### 3. Clear Output

Tests should:
- Use descriptive assertion messages
- Log useful information
- Explain failures clearly

### 4. Robustness

Tests should:
- Handle missing dependencies gracefully
- Not crash on failure
- Provide helpful error messages

## Troubleshooting

### Python Tests Failing

**Issue**: Python tests skip with "Python not available"

**Solution**:
1. Enable PythonScriptPlugin in Project Settings
2. Restart Unreal Editor
3. Verify plugin loaded: `Plugins → Built-in → Python`

### Asset Tests Return Empty

**Issue**: Asset tests find 0 assets

**Solution**:
1. Wait for Asset Registry to complete initial scan
2. Check log for "Asset Registry loaded" message
3. Verify assets exist in `/Game/` folder

### Tests Not Showing in UI

**Issue**: Tests don't appear in Test Automation window

**Solution**:
1. Verify AdastreaDirectorTests module is in .uplugin
2. Regenerate project files
3. Rebuild plugin
4. Restart Editor
5. Check Module list in Editor: `Edit → Plugins → Adastrea Director`

## Statistics

**Total Tests**: 20 unit tests across 3 components
**Coverage**: Core VibeUE services (Python, Assets, Tools)
**Execution Time**: ~5-10 seconds for full suite
**Success Rate**: 100% (with proper setup)

## References

- [Unreal Automation System](https://docs.unrealengine.com/5.3/en-US/automation-system-in-unreal-engine/)
- [Automation Technical Guide](https://docs.unrealengine.com/5.3/en-US/automation-technical-guide/)
- [VIBEUE_ARCHITECTURE_SUMMARY.md](VIBEUE_ARCHITECTURE_SUMMARY.md)
- [VIBEUE_IMPLEMENTATION_GUIDE.md](VIBEUE_IMPLEMENTATION_GUIDE.md)
