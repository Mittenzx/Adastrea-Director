// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

// Custom log category for Adastrea Director Editor
DECLARE_LOG_CATEGORY_EXTERN(LogAdastreaDirectorEditor, Log, All);

/**
 * Editor module for Adastrea Director plugin.
 * Provides Unreal Editor integration including UI panels, toolbar buttons, and menu commands.
 */
class FAdastreaDirectorEditorModule : public IModuleInterface
{
public:

	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

private:
	// Future: UI registration, menu extensions, and toolbar commands will be added here
	
	/** Registers menu extensions and toolbar buttons */
	void RegisterMenuExtensions();
	
	/** Unregisters menu extensions */
	void UnregisterMenuExtensions();
};
