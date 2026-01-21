// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Engine/Blueprint.h"
#include "Materials/Material.h"
#include "Dom/JsonObject.h"

struct FAdastreaAssetInfo
{
	FString Name;
	FString Path;
	FString Class;
	int64 DiskSize;
	
	TSharedPtr<FJsonObject> ToJson() const;
};

/**
 * Service for discovering and querying project assets at runtime
 */
class ADASTREADIRECTOR_API FAdastreaAssetService
{
public:
	/**
	 * Search for assets by name pattern and/or class
	 * @param SearchPattern Name pattern (supports wildcards)
	 * @param ClassName Optional class filter (e.g., "Blueprint", "Material")
	 * @param MaxResults Maximum number of results
	 * @return Array of matching assets
	 */
	static TArray<FAdastreaAssetInfo> SearchAssets(
		const FString& SearchPattern = TEXT("*"),
		const FString& ClassName = TEXT(""),
		int32 MaxResults = 100
	);

	/**
	 * Get all Blueprints in the project
	 * @param PathPrefix Optional path filter (e.g., "/Game/Characters/")
	 * @return Array of Blueprint assets
	 */
	static TArray<FAdastreaAssetInfo> GetBlueprints(const FString& PathPrefix = TEXT(""));

	/**
	 * Get all Materials in the project
	 * @param PathPrefix Optional path filter
	 * @return Array of Material assets
	 */
	static TArray<FAdastreaAssetInfo> GetMaterials(const FString& PathPrefix = TEXT(""));

	/**
	 * Get all UMG Widgets in the project
	 * @param PathPrefix Optional path filter
	 * @return Array of Widget Blueprint assets
	 */
	static TArray<FAdastreaAssetInfo> GetWidgets(const FString& PathPrefix = TEXT(""));

	/**
	 * Get asset information by path
	 * @param AssetPath Full asset path
	 * @return Asset info or empty if not found
	 */
	static TOptional<FAdastreaAssetInfo> GetAssetByPath(const FString& AssetPath);

	/**
	 * Check if asset registry is ready
	 * @return True if asset registry has finished initial scan
	 */
	static bool IsAssetRegistryReady();

private:
	static IAssetRegistry& GetAssetRegistry();
	static FAdastreaAssetInfo ConvertAssetData(const FAssetData& AssetData);
};
