// Copyright (c) 2025 Mittenzx. All Rights Reserved.

using UnrealBuildTool;

public class AdastreaDirectorTests : ModuleRules
{
	public AdastreaDirectorTests(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
		
		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
				"CoreUObject",
				"Engine",
				"AdastreaDirector"
			}
		);

		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"UnrealEd",
				"AssetRegistry",
				"PythonScriptPlugin",
				"HTTP",
				"Json",
				"JsonUtilities",
				"HTTPServer"
			}
		);

		// Required for automation testing
		if (Target.bBuildEditor)
		{
			PrivateDependencyModuleNames.Add("UnrealEd");
		}
	}
}
