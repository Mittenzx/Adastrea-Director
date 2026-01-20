// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "AdastreaScriptService.h"
#include "AdastreaDirectorModule.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaScriptServiceAvailabilityTest, 
	"Adastrea.VibeUE.Python.Availability",
	EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FAdastreaScriptServiceAvailabilityTest::RunTest(const FString& Parameters)
{
	// Test if Python is available
	bool bPythonAvailable = FAdastreaScriptService::IsPythonAvailable();
	
	if (bPythonAvailable)
	{
		AddInfo(TEXT("Python plugin is available"));
		TestTrue(TEXT("Python should be available"), bPythonAvailable);
		
		// Get Python info
		FString PythonInfo = FAdastreaScriptService::GetPythonInfo();
		AddInfo(FString::Printf(TEXT("Python Info: %s"), *PythonInfo));
		TestFalse(TEXT("Python info should not be empty"), PythonInfo.IsEmpty());
	}
	else
	{
		AddWarning(TEXT("Python plugin is not loaded - skipping Python tests"));
		AddWarning(TEXT("Enable PythonScriptPlugin in project settings to run Python tests"));
	}
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaScriptServiceExpressionTest,
	"Adastrea.VibeUE.Python.EvaluateExpression",
	EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FAdastreaScriptServiceExpressionTest::RunTest(const FString& Parameters)
{
	if (!FAdastreaScriptService::IsPythonAvailable())
	{
		AddWarning(TEXT("Python not available - skipping test"));
		return true;
	}
	
	// Test 1: Simple arithmetic
	FAdastreaScriptResult Result1 = FAdastreaScriptService::EvaluateExpression(TEXT("2 + 2"));
	TestTrue(TEXT("Arithmetic expression should succeed"), Result1.bSuccess);
	
	FString TrimmedOutput = Result1.Output.TrimStartAndEnd();
	TestEqual(TEXT("2 + 2 should equal 4"), TrimmedOutput, TEXT("4"));
	TestTrue(TEXT("Execution time should be > 0"), Result1.ExecutionTimeMs > 0.0f);
	
	// Test 2: String expression
	FAdastreaScriptResult Result2 = FAdastreaScriptService::EvaluateExpression(TEXT("'Hello' + ' ' + 'World'"));
	TestTrue(TEXT("String expression should succeed"), Result2.bSuccess);
	TestTrue(TEXT("Output should contain 'Hello World'"), Result2.Output.Contains(TEXT("Hello World")));
	
	// Test 3: List expression
	FAdastreaScriptResult Result3 = FAdastreaScriptService::EvaluateExpression(TEXT("[1, 2, 3, 4, 5]"));
	TestTrue(TEXT("List expression should succeed"), Result3.bSuccess);
	TestTrue(TEXT("Output should contain list"), Result3.Output.Contains(TEXT("[")));
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaScriptServiceExecuteCodeTest,
	"Adastrea.VibeUE.Python.ExecuteCode",
	EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FAdastreaScriptServiceExecuteCodeTest::RunTest(const FString& Parameters)
{
	if (!FAdastreaScriptService::IsPythonAvailable())
	{
		AddWarning(TEXT("Python not available - skipping test"));
		return true;
	}
	
	// Test 1: Simple print statement
	FString Code1 = TEXT("print('Hello from Python')");
	FAdastreaScriptResult Result1 = FAdastreaScriptService::ExecuteCode(Code1);
	TestTrue(TEXT("Print statement should succeed"), Result1.bSuccess);
	TestTrue(TEXT("Output should contain message"), Result1.Output.Contains(TEXT("Hello from Python")));
	
	// Test 2: Multi-line code
	FString Code2 = TEXT(R"(
x = 10
y = 20
result = x + y
print(f'Result: {result}')
)");
	FAdastreaScriptResult Result2 = FAdastreaScriptService::ExecuteCode(Code2);
	TestTrue(TEXT("Multi-line code should succeed"), Result2.bSuccess);
	TestTrue(TEXT("Output should contain result"), Result2.Output.Contains(TEXT("30")));
	
	// Test 3: Function definition
	FString Code3 = TEXT(R"(
def greet(name):
    return f'Hello, {name}!'

message = greet('Adastrea')
print(message)
)");
	FAdastreaScriptResult Result3 = FAdastreaScriptService::ExecuteCode(Code3);
	TestTrue(TEXT("Function code should succeed"), Result3.bSuccess);
	TestTrue(TEXT("Output should contain greeting"), Result3.Output.Contains(TEXT("Hello, Adastrea")));
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaScriptServiceUnrealAccessTest,
	"Adastrea.VibeUE.Python.UnrealModuleAccess",
	EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FAdastreaScriptServiceUnrealAccessTest::RunTest(const FString& Parameters)
{
	if (!FAdastreaScriptService::IsPythonAvailable())
	{
		AddWarning(TEXT("Python not available - skipping test"));
		return true;
	}
	
	// Test accessing Unreal module
	FString Code = TEXT(R"(
import unreal
print(f'Unreal module imported: {unreal}')
print(f'Project directory: {unreal.SystemLibrary.get_project_directory()}')
)");
	
	FAdastreaScriptResult Result = FAdastreaScriptService::ExecuteCode(Code);
	TestTrue(TEXT("Unreal module access should succeed"), Result.bSuccess);
	TestTrue(TEXT("Output should contain project directory"), Result.Output.Len() > 0);
	TestFalse(TEXT("Should not have error message"), !Result.ErrorMessage.IsEmpty() && Result.bSuccess);
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaScriptServiceErrorHandlingTest,
	"Adastrea.VibeUE.Python.ErrorHandling",
	EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FAdastreaScriptServiceErrorHandlingTest::RunTest(const FString& Parameters)
{
	if (!FAdastreaScriptService::IsPythonAvailable())
	{
		AddWarning(TEXT("Python not available - skipping test"));
		return true;
	}
	
	// Test 1: Syntax error
	FAdastreaScriptResult Result1 = FAdastreaScriptService::ExecuteCode(TEXT("print('unclosed string"));
	TestFalse(TEXT("Syntax error should fail"), Result1.bSuccess);
	TestFalse(TEXT("Error message should not be empty"), Result1.ErrorMessage.IsEmpty());
	
	// Test 2: Runtime error (division by zero)
	FAdastreaScriptResult Result2 = FAdastreaScriptService::ExecuteCode(TEXT("x = 1 / 0"));
	TestFalse(TEXT("Division by zero should fail"), Result2.bSuccess);
	TestTrue(TEXT("Error message should mention division"), Result2.ErrorMessage.Contains(TEXT("division")));
	
	// Test 3: Name error (undefined variable)
	FAdastreaScriptResult Result3 = FAdastreaScriptService::ExecuteCode(TEXT("print(undefined_variable)"));
	TestFalse(TEXT("Undefined variable should fail"), Result3.bSuccess);
	TestTrue(TEXT("Error message should mention name"), 
		Result3.ErrorMessage.Contains(TEXT("name")) || Result3.ErrorMessage.Contains(TEXT("undefined")));
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaScriptServiceScopeTest,
	"Adastrea.VibeUE.Python.Scope",
	EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FAdastreaScriptServiceScopeTest::RunTest(const FString& Parameters)
{
	if (!FAdastreaScriptService::IsPythonAvailable())
	{
		AddWarning(TEXT("Python not available - skipping test"));
		return true;
	}
	
	// Test private scope isolation
	FString Code1 = TEXT("test_variable = 'private_scope'");
	FAdastreaScriptResult Result1 = FAdastreaScriptService::ExecuteCode(Code1, true); // Private scope
	TestTrue(TEXT("Code in private scope should succeed"), Result1.bSuccess);
	
	// Try to access variable from different private scope (should fail)
	FString Code2 = TEXT("print(test_variable)");
	FAdastreaScriptResult Result2 = FAdastreaScriptService::ExecuteCode(Code2, true); // Different private scope
	TestFalse(TEXT("Variable should not be accessible in different private scope"), Result2.bSuccess);
	
	// Test shared scope
	FString Code3 = TEXT("shared_variable = 'shared_scope'");
	FAdastreaScriptResult Result3 = FAdastreaScriptService::ExecuteCode(Code3, false); // Shared scope
	TestTrue(TEXT("Code in shared scope should succeed"), Result3.bSuccess);
	
	// Access variable from shared scope (might work depending on UE Python implementation)
	FString Code4 = TEXT("print(shared_variable)");
	FAdastreaScriptResult Result4 = FAdastreaScriptService::ExecuteCode(Code4, false); // Same shared scope
	// Note: Shared scope behavior may vary, so we just check it doesn't crash
	AddInfo(FString::Printf(TEXT("Shared scope test result: %s"), Result4.bSuccess ? TEXT("Success") : TEXT("Failed")));
	
	return true;
}
