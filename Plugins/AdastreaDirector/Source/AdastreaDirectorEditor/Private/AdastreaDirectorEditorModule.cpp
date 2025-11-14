// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "AdastreaDirectorEditorModule.h"
#include "Modules/ModuleManager.h"

#define LOCTEXT_NAMESPACE "FAdastreaDirectorEditorModule"

void FAdastreaDirectorEditorModule::StartupModule()
{
	// This code will execute after your module is loaded into memory; the exact timing is specified in the .uplugin file per-module
	UE_LOG(LogTemp, Log, TEXT("AdastreaDirector Editor Module: StartupModule"));
	
	RegisterMenuExtensions();
}

void FAdastreaDirectorEditorModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module. For modules that support dynamic reloading,
	// we call this function before unloading the module.
	UE_LOG(LogTemp, Log, TEXT("AdastreaDirector Editor Module: ShutdownModule"));
	
	UnregisterMenuExtensions();
}

void FAdastreaDirectorEditorModule::RegisterMenuExtensions()
{
	// Future: Register menu commands, toolbar buttons, and custom panels here
	// This will be implemented in subsequent weeks as part of the UI development
}

void FAdastreaDirectorEditorModule::UnregisterMenuExtensions()
{
	// Future: Unregister menu extensions here
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FAdastreaDirectorEditorModule, AdastreaDirectorEditor)
