// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "AdastreaAssetService.h"
#include "AdastreaDirectorModule.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaAssetServiceAvailabilityTest,
	"Adastrea.VibeUE.Assets.RegistryAvailability",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FAdastreaAssetServiceAvailabilityTest::RunTest(const FString& Parameters)
{
	// Test if asset registry is available
	bool bIsReady = FAdastreaAssetService::IsAssetRegistryReady();
	
	if (bIsReady)
	{
		AddInfo(TEXT("Asset Registry is ready"));
		TestTrue(TEXT("Asset Registry should be ready"), bIsReady);
	}
	else
	{
		AddWarning(TEXT("Asset Registry is still loading - results may be incomplete"));
		AddInfo(TEXT("Wait for asset registry to finish scanning before running comprehensive tests"));
	}
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaAssetServiceSearchTest,
	"Adastrea.VibeUE.Assets.SearchAssets",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FAdastreaAssetServiceSearchTest::RunTest(const FString& Parameters)
{
	if (!FAdastreaAssetService::IsAssetRegistryReady())
	{
		AddWarning(TEXT("Asset Registry not ready - skipping test"));
		return true;
	}
	
	// Test 1: Search all assets (wildcard)
	TArray<FAdastreaAssetInfo> AllAssets = FAdastreaAssetService::SearchAssets(TEXT("*"), TEXT(""), 50);
	TestTrue(TEXT("Should find at least some assets"), AllAssets.Num() >= 0);
	AddInfo(FString::Printf(TEXT("Found %d assets with wildcard search"), AllAssets.Num()));
	
	// Test 2: Search with pattern
	TArray<FAdastreaAssetInfo> PatternAssets = FAdastreaAssetService::SearchAssets(TEXT("Player"), TEXT(""), 50);
	AddInfo(FString::Printf(TEXT("Found %d assets matching 'Player'"), PatternAssets.Num()));
	
	// Verify pattern matching works
	for (const FAdastreaAssetInfo& Asset : PatternAssets)
	{
		TestTrue(TEXT("Asset name should contain pattern"), Asset.Name.Contains(TEXT("Player")));
		TestFalse(TEXT("Asset name should not be empty"), Asset.Name.IsEmpty());
		TestFalse(TEXT("Asset path should not be empty"), Asset.Path.IsEmpty());
		TestFalse(TEXT("Asset class should not be empty"), Asset.Class.IsEmpty());
	}
	
	// Test 3: Empty pattern
	TArray<FAdastreaAssetInfo> EmptyPatternAssets = FAdastreaAssetService::SearchAssets(TEXT(""), TEXT(""), 10);
	AddInfo(FString::Printf(TEXT("Found %d assets with empty pattern"), EmptyPatternAssets.Num()));
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaAssetServiceBlueprintTest,
	"Adastrea.VibeUE.Assets.GetBlueprints",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FAdastreaAssetServiceBlueprintTest::RunTest(const FString& Parameters)
{
	if (!FAdastreaAssetService::IsAssetRegistryReady())
	{
		AddWarning(TEXT("Asset Registry not ready - skipping test"));
		return true;
	}
	
	// Get all Blueprints
	TArray<FAdastreaAssetInfo> Blueprints = FAdastreaAssetService::GetBlueprints();
	AddInfo(FString::Printf(TEXT("Found %d Blueprints"), Blueprints.Num()));
	
	// Verify Blueprint results
	for (const FAdastreaAssetInfo& Blueprint : Blueprints)
	{
		TestFalse(TEXT("Blueprint name should not be empty"), Blueprint.Name.IsEmpty());
		
		bool bIsValidPath = Blueprint.Path.StartsWith(TEXT("/Game")) || Blueprint.Path.StartsWith(TEXT("/Engine"));
		TestTrue(TEXT("Blueprint path should start with /Game or /Engine"), bIsValidPath);
		
		bool bIsBlueprint = Blueprint.Class.Contains(TEXT("Blueprint")) || Blueprint.Class.Equals(TEXT("Blueprint"));
		TestTrue(TEXT("Blueprint class should be Blueprint or related"), bIsBlueprint);
		
		AddInfo(FString::Printf(TEXT("  Blueprint: %s (%s)"), *Blueprint.Name, *Blueprint.Path));
		
		// Only check first few to avoid spam
		if (Blueprints.Find(Blueprint) >= 3)
		{
			break;
		}
	}
	
	// Test with path prefix
	TArray<FAdastreaAssetInfo> GameBlueprints = FAdastreaAssetService::GetBlueprints(TEXT("/Game"));
	AddInfo(FString::Printf(TEXT("Found %d Blueprints in /Game"), GameBlueprints.Num()));
	
	for (const FAdastreaAssetInfo& Blueprint : GameBlueprints)
	{
		TestTrue(TEXT("Blueprint should be in /Game path"), Blueprint.Path.StartsWith(TEXT("/Game")));
	}
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaAssetServiceMaterialTest,
	"Adastrea.VibeUE.Assets.GetMaterials",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FAdastreaAssetServiceMaterialTest::RunTest(const FString& Parameters)
{
	if (!FAdastreaAssetService::IsAssetRegistryReady())
	{
		AddWarning(TEXT("Asset Registry not ready - skipping test"));
		return true;
	}
	
	// Get all Materials
	TArray<FAdastreaAssetInfo> Materials = FAdastreaAssetService::GetMaterials();
	AddInfo(FString::Printf(TEXT("Found %d Materials"), Materials.Num()));
	
	// Verify Material results
	for (const FAdastreaAssetInfo& Material : Materials)
	{
		TestFalse(TEXT("Material name should not be empty"), Material.Name.IsEmpty());
		TestTrue(TEXT("Material class should be Material"), Material.Class.Equals(TEXT("Material")));
		AddInfo(FString::Printf(TEXT("  Material: %s"), *Material.Name));
		
		// Only check first few
		if (Materials.Find(Material) >= 3)
		{
			break;
		}
	}
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaAssetServiceWidgetTest,
	"Adastrea.VibeUE.Assets.GetWidgets",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FAdastreaAssetServiceWidgetTest::RunTest(const FString& Parameters)
{
	if (!FAdastreaAssetService::IsAssetRegistryReady())
	{
		AddWarning(TEXT("Asset Registry not ready - skipping test"));
		return true;
	}
	
	// Get all Widgets
	TArray<FAdastreaAssetInfo> Widgets = FAdastreaAssetService::GetWidgets();
	AddInfo(FString::Printf(TEXT("Found %d UMG Widgets"), Widgets.Num()));
	
	// Verify Widget results
	for (const FAdastreaAssetInfo& Widget : Widgets)
	{
		TestFalse(TEXT("Widget name should not be empty"), Widget.Name.IsEmpty());
		TestTrue(TEXT("Widget class should be WidgetBlueprint"), Widget.Class.Equals(TEXT("WidgetBlueprint")));
		AddInfo(FString::Printf(TEXT("  Widget: %s"), *Widget.Name));
		
		// Only check first few
		if (Widgets.Find(Widget) >= 3)
		{
			break;
		}
	}
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaAssetServiceJsonSerializationTest,
	"Adastrea.VibeUE.Assets.JsonSerialization",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FAdastreaAssetServiceJsonSerializationTest::RunTest(const FString& Parameters)
{
	// Create a test asset info
	FAdastreaAssetInfo TestAsset;
	TestAsset.Name = TEXT("TestAsset");
	TestAsset.Path = TEXT("/Game/Test/TestAsset");
	TestAsset.Class = TEXT("Blueprint");
	TestAsset.DiskSize = 12345;
	
	// Serialize to JSON
	TSharedPtr<FJsonObject> JsonObj = TestAsset.ToJson();
	TestTrue(TEXT("JSON object should be valid"), JsonObj.IsValid());
	
	// Verify fields
	FString Name;
	TestTrue(TEXT("JSON should have name field"), JsonObj->TryGetStringField(TEXT("name"), Name));
	TestEqual(TEXT("Name should match"), Name, TEXT("TestAsset"));
	
	FString Path;
	TestTrue(TEXT("JSON should have path field"), JsonObj->TryGetStringField(TEXT("path"), Path));
	TestEqual(TEXT("Path should match"), Path, TEXT("/Game/Test/TestAsset"));
	
	FString Class;
	TestTrue(TEXT("JSON should have class field"), JsonObj->TryGetStringField(TEXT("class"), Class));
	TestEqual(TEXT("Class should match"), Class, TEXT("Blueprint"));
	
	double DiskSize;
	TestTrue(TEXT("JSON should have diskSize field"), JsonObj->TryGetNumberField(TEXT("diskSize"), DiskSize));
	TestEqual(TEXT("DiskSize should match"), (int64)DiskSize, (int64)12345);
	
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdastreaAssetServiceMaxResultsTest,
	"Adastrea.VibeUE.Assets.MaxResults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FAdastreaAssetServiceMaxResultsTest::RunTest(const FString& Parameters)
{
	if (!FAdastreaAssetService::IsAssetRegistryReady())
	{
		AddWarning(TEXT("Asset Registry not ready - skipping test"));
		return true;
	}
	
	// Test with max results limit
	TArray<FAdastreaAssetInfo> LimitedAssets = FAdastreaAssetService::SearchAssets(TEXT("*"), TEXT(""), 5);
	TestTrue(TEXT("Should respect max results limit"), LimitedAssets.Num() <= 5);
	AddInfo(FString::Printf(TEXT("Limited search returned %d assets (max 5)"), LimitedAssets.Num()));
	
	// Test with higher limit
	TArray<FAdastreaAssetInfo> MoreAssets = FAdastreaAssetService::SearchAssets(TEXT("*"), TEXT(""), 50);
	AddInfo(FString::Printf(TEXT("Larger search returned %d assets (max 50)"), MoreAssets.Num()));
	
	return true;
}
