// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "AdastreaToolSystem.h"
#include "AdastreaDirectorModule.h"
#include "Dom/JsonObject.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaToolSystemRegistrationTest,
	"Adastrea.VibeUE.Tools.Registration",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FAdastreaToolSystemRegistrationTest::RunTest(const FString& Parameters)
{
	FAdastreaToolSystem& ToolSystem = FAdastreaToolSystem::Get();
	
	// Create a test tool
	FAdastreaToolInfo TestTool;
	TestTool.Name = TEXT("test_tool");
	TestTool.Description = TEXT("A test tool for unit testing");
	TestTool.Category = TEXT("Test");
	
	// Create parameter schema
	TSharedPtr<FJsonObject> Schema = MakeShared<FJsonObject>();
	Schema->SetStringField(TEXT("type"), TEXT("object"));
	TestTool.ParameterSchema = Schema;
	
	// Create executor
	TestTool.Executor.BindLambda([](const TSharedPtr<FJsonObject>& Args) -> FToolExecutionResult
	{
		FToolExecutionResult Result;
		Result.bSuccess = true;
		Result.Output = TEXT("Test tool executed successfully");
		return Result;
	});
	
	// Register the tool
	ToolSystem.RegisterTool(TestTool);
	
	// Verify tool is registered
	bool bHasTool = ToolSystem.HasTool(TEXT("test_tool"));
	TestTrue(TEXT("Tool should be registered"), bHasTool);
	
	// Clean up
	ToolSystem.UnregisterTool(TEXT("test_tool"));
	
	// Verify tool is unregistered
	bHasTool = ToolSystem.HasTool(TEXT("test_tool"));
	TestFalse(TEXT("Tool should be unregistered"), bHasTool);
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaToolSystemExecutionTest,
	"Adastrea.VibeUE.Tools.Execution",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FAdastreaToolSystemExecutionTest::RunTest(const FString& Parameters)
{
	FAdastreaToolSystem& ToolSystem = FAdastreaToolSystem::Get();
	
	// Create a test tool
	FAdastreaToolInfo TestTool;
	TestTool.Name = TEXT("test_execution_tool");
	TestTool.Description = TEXT("Tool to test execution");
	TestTool.Category = TEXT("Test");
	
	TSharedPtr<FJsonObject> Schema = MakeShared<FJsonObject>();
	Schema->SetStringField(TEXT("type"), TEXT("object"));
	TestTool.ParameterSchema = Schema;
	
	// Create executor that uses arguments
	TestTool.Executor.BindLambda([](const TSharedPtr<FJsonObject>& Args) -> FToolExecutionResult
	{
		FToolExecutionResult Result;
		
		FString InputValue;
		if (Args->TryGetStringField(TEXT("input"), InputValue))
		{
			Result.bSuccess = true;
			Result.Output = FString::Printf(TEXT("Received: %s"), *InputValue);
		}
		else
		{
			Result.bSuccess = false;
			Result.ErrorMessage = TEXT("Missing 'input' parameter");
		}
		
		return Result;
	});
	
	// Register the tool
	ToolSystem.RegisterTool(TestTool);
	
	// Test 1: Execute with valid arguments
	TSharedPtr<FJsonObject> Args1 = MakeShared<FJsonObject>();
	Args1->SetStringField(TEXT("input"), TEXT("Hello World"));
	
	FToolExecutionResult Result1 = ToolSystem.ExecuteTool(TEXT("test_execution_tool"), Args1);
	TestTrue(TEXT("Execution with valid args should succeed"), Result1.bSuccess);
	TestTrue(TEXT("Output should contain input"), Result1.Output.Contains(TEXT("Hello World")));
	
	// Test 2: Execute with missing arguments
	TSharedPtr<FJsonObject> Args2 = MakeShared<FJsonObject>();
	FToolExecutionResult Result2 = ToolSystem.ExecuteTool(TEXT("test_execution_tool"), Args2);
	TestFalse(TEXT("Execution with missing args should fail"), Result2.bSuccess);
	TestFalse(TEXT("Error message should not be empty"), Result2.ErrorMessage.IsEmpty());
	
	// Clean up
	ToolSystem.UnregisterTool(TEXT("test_execution_tool"));
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaToolSystemNotFoundTest,
	"Adastrea.VibeUE.Tools.NotFound",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FAdastreaToolSystemNotFoundTest::RunTest(const FString& Parameters)
{
	FAdastreaToolSystem& ToolSystem = FAdastreaToolSystem::Get();
	
	// Try to execute non-existent tool
	TSharedPtr<FJsonObject> Args = MakeShared<FJsonObject>();
	FToolExecutionResult Result = ToolSystem.ExecuteTool(TEXT("non_existent_tool"), Args);
	
	TestFalse(TEXT("Non-existent tool should fail"), Result.bSuccess);
	TestTrue(TEXT("Error message should mention 'not found'"), Result.ErrorMessage.Contains(TEXT("not found")));
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaToolSystemCategoryFilterTest,
	"Adastrea.VibeUE.Tools.CategoryFilter",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FAdastreaToolSystemCategoryFilterTest::RunTest(const FString& Parameters)
{
	FAdastreaToolSystem& ToolSystem = FAdastreaToolSystem::Get();
	
	// Create tools in different categories
	FAdastreaToolInfo Tool1;
	Tool1.Name = TEXT("test_asset_tool");
	Tool1.Description = TEXT("Test asset tool");
	Tool1.Category = TEXT("Asset");
	Tool1.ParameterSchema = MakeShared<FJsonObject>();
	Tool1.Executor.BindLambda([](const TSharedPtr<FJsonObject>&) -> FToolExecutionResult
	{
		FToolExecutionResult Result;
		Result.bSuccess = true;
		return Result;
	});
	
	FAdastreaToolInfo Tool2;
	Tool2.Name = TEXT("test_python_tool");
	Tool2.Description = TEXT("Test python tool");
	Tool2.Category = TEXT("Python");
	Tool2.ParameterSchema = MakeShared<FJsonObject>();
	Tool2.Executor.BindLambda([](const TSharedPtr<FJsonObject>&) -> FToolExecutionResult
	{
		FToolExecutionResult Result;
		Result.bSuccess = true;
		return Result;
	});
	
	// Register tools
	ToolSystem.RegisterTool(Tool1);
	ToolSystem.RegisterTool(Tool2);
	
	// Get tools by category
	TArray<FToolDefinition> AssetTools = ToolSystem.GetToolsByCategory(TEXT("Asset"));
	TArray<FToolDefinition> PythonTools = ToolSystem.GetToolsByCategory(TEXT("Python"));
	
	TestTrue(TEXT("Should find at least one asset tool"), AssetTools.Num() >= 1);
	TestTrue(TEXT("Should find at least one python tool"), PythonTools.Num() >= 1);
	
	// Verify asset tools contain our test tool
	bool bFoundAssetTool = false;
	for (const FToolDefinition& Tool : AssetTools)
	{
		if (Tool.Name == TEXT("test_asset_tool"))
		{
			bFoundAssetTool = true;
			break;
		}
	}
	TestTrue(TEXT("Asset category should contain test_asset_tool"), bFoundAssetTool);
	
	// Clean up
	ToolSystem.UnregisterTool(TEXT("test_asset_tool"));
	ToolSystem.UnregisterTool(TEXT("test_python_tool"));
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaToolSystemGetAllToolsTest,
	"Adastrea.VibeUE.Tools.GetAllTools",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FAdastreaToolSystemGetAllToolsTest::RunTest(const FString& Parameters)
{
	FAdastreaToolSystem& ToolSystem = FAdastreaToolSystem::Get();
	
	// Get all registered tools
	TArray<FToolDefinition> AllTools = ToolSystem.GetAllToolDefinitions();
	AddInfo(FString::Printf(TEXT("Found %d registered tools"), AllTools.Num()));
	
	// Verify each tool has required fields
	for (const FToolDefinition& Tool : AllTools)
	{
		TestFalse(TEXT("Tool name should not be empty"), Tool.Name.IsEmpty());
		TestFalse(TEXT("Tool description should not be empty"), Tool.Description.IsEmpty());
		TestTrue(TEXT("Tool should have parameter schema"), Tool.Parameters.IsValid());
		
		AddInfo(FString::Printf(TEXT("  Tool: %s - %s"), *Tool.Name, *Tool.Description));
		
		// Only log first few to avoid spam
		const int32 MaxToolsToLog = 5;
		if (AllTools.Find(Tool) >= MaxToolsToLog)
		{
			AddInfo(TEXT("  ... and more"));
			break;
		}
	}
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaToolSystemResultSerializationTest,
	"Adastrea.VibeUE.Tools.ResultSerialization",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FAdastreaToolSystemResultSerializationTest::RunTest(const FString& Parameters)
{
	// Create a test result
	FToolExecutionResult Result;
	Result.bSuccess = true;
	Result.Output = TEXT("Test output");
	Result.ErrorMessage = TEXT("");
	
	// Add some data
	TSharedPtr<FJsonObject> Data = MakeShared<FJsonObject>();
	Data->SetStringField(TEXT("key1"), TEXT("value1"));
	Data->SetNumberField(TEXT("key2"), 42);
	Result.Data = Data;
	
	// Serialize to JSON
	TSharedPtr<FJsonObject> JsonObj = Result.ToJson();
	TestTrue(TEXT("JSON object should be valid"), JsonObj.IsValid());
	
	// Verify fields
	bool bSuccess;
	TestTrue(TEXT("JSON should have success field"), JsonObj->TryGetBoolField(TEXT("success"), bSuccess));
	TestTrue(TEXT("Success should be true"), bSuccess);
	
	FString Output;
	TestTrue(TEXT("JSON should have output field"), JsonObj->TryGetStringField(TEXT("output"), Output));
	TestEqual(TEXT("Output should match"), Output, TEXT("Test output"));
	
	const TSharedPtr<FJsonObject>* DataObj;
	TestTrue(TEXT("JSON should have data field"), JsonObj->TryGetObjectField(TEXT("data"), DataObj));
	TestTrue(TEXT("Data object should be valid"), DataObj && (*DataObj).IsValid());
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaToolSystemOverwriteTest,
	"Adastrea.VibeUE.Tools.OverwriteTool",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FAdastreaToolSystemOverwriteTest::RunTest(const FString& Parameters)
{
	FAdastreaToolSystem& ToolSystem = FAdastreaToolSystem::Get();
	
	// Create first version of tool
	FAdastreaToolInfo Tool1;
	Tool1.Name = TEXT("test_overwrite_tool");
	Tool1.Description = TEXT("Version 1");
	Tool1.Category = TEXT("Test");
	Tool1.ParameterSchema = MakeShared<FJsonObject>();
	Tool1.Executor.BindLambda([](const TSharedPtr<FJsonObject>&) -> FToolExecutionResult
	{
		FToolExecutionResult Result;
		Result.bSuccess = true;
		Result.Output = TEXT("Version 1");
		return Result;
	});
	
	ToolSystem.RegisterTool(Tool1);
	
	// Execute first version
	TSharedPtr<FJsonObject> Args = MakeShared<FJsonObject>();
	FToolExecutionResult Result1 = ToolSystem.ExecuteTool(TEXT("test_overwrite_tool"), Args);
	TestEqual(TEXT("Should execute version 1"), Result1.Output, TEXT("Version 1"));
	
	// Create second version (overwrite)
	FAdastreaToolInfo Tool2;
	Tool2.Name = TEXT("test_overwrite_tool"); // Same name
	Tool2.Description = TEXT("Version 2");
	Tool2.Category = TEXT("Test");
	Tool2.ParameterSchema = MakeShared<FJsonObject>();
	Tool2.Executor.BindLambda([](const TSharedPtr<FJsonObject>&) -> FToolExecutionResult
	{
		FToolExecutionResult Result;
		Result.bSuccess = true;
		Result.Output = TEXT("Version 2");
		return Result;
	});
	
	// This should log a warning about overwriting
	ToolSystem.RegisterTool(Tool2);
	
	// Execute should now use version 2
	FToolExecutionResult Result2 = ToolSystem.ExecuteTool(TEXT("test_overwrite_tool"), Args);
	TestEqual(TEXT("Should execute version 2 after overwrite"), Result2.Output, TEXT("Version 2"));
	
	// Clean up
	ToolSystem.UnregisterTool(TEXT("test_overwrite_tool"));
	
	return true;
}
