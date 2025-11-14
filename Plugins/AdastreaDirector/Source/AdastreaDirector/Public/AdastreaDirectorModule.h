// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

// Custom log category for Adastrea Director
DECLARE_LOG_CATEGORY_EXTERN(LogAdastreaDirector, Log, All);

/**
 * Runtime module for Adastrea Director plugin.
 * Provides core functionality for AI-powered development assistance.
 */
class FAdastreaDirectorModule : public IModuleInterface
{
public:

	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

private:
	// Future: Python bridge initialization and management will be added here
};
