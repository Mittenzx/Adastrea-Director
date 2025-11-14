// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "AdastreaDirectorModule.h"

// Define custom log category for AdastreaDirector
DEFINE_LOG_CATEGORY(LogAdastreaDirector);

#define LOCTEXT_NAMESPACE "FAdastreaDirectorModule"

void FAdastreaDirectorModule::StartupModule()
{
	// This code will execute after your module is loaded into memory; the exact timing is specified in the .uplugin file per-module
	UE_LOG(LogAdastreaDirector, Log, TEXT("AdastreaDirector Runtime Module: StartupModule"));
}

void FAdastreaDirectorModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module. For modules that support dynamic reloading,
	// we call this function before unloading the module.
	UE_LOG(LogAdastreaDirector, Log, TEXT("AdastreaDirector Runtime Module: ShutdownModule"));
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FAdastreaDirectorModule, AdastreaDirector)
