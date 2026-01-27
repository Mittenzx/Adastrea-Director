// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

/**
 * Test module for Adastrea Director plugin.
 * Provides a minimal module implementation to allow automation tests to load correctly.
 */
class FAdastreaDirectorTestsModule : public IModuleInterface
{
public:
	/** IModuleInterface implementation */
	virtual void StartupModule() override
	{
		// Minimal startup - automation tests will initialize themselves
	}

	virtual void ShutdownModule() override
	{
		// Minimal shutdown
	}
};

IMPLEMENT_MODULE(FAdastreaDirectorTestsModule, AdastreaDirectorTests)
