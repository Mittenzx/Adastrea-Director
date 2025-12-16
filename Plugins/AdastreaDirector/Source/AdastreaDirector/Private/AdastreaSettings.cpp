// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "AdastreaSettings.h"
#include "AdastreaDirectorModule.h"

FAdastreaSettings& FAdastreaSettings::Get()
{
	static FAdastreaSettings Instance;
	return Instance;
}

FAdastreaSettings::FAdastreaSettings()
	: DefaultFontSize(10)
	, bAutoSaveSettings(true)
	, bShowTimestamps(true)
{
	LoadSettings();
}

void FAdastreaSettings::LoadSettings()
{
	LLMProvider = LoadConfigValue(TEXT("LLMProvider"), TEXT("gemini"));
	EmbeddingProvider = LoadConfigValue(TEXT("EmbeddingProvider"), TEXT("huggingface"));
	GeminiAPIKey = LoadConfigValue(TEXT("GeminiAPIKey"), TEXT(""));
	OpenAIAPIKey = LoadConfigValue(TEXT("OpenAIAPIKey"), TEXT(""));
	
	FString FontSizeStr = LoadConfigValue(TEXT("DefaultFontSize"), TEXT("10"));
	DefaultFontSize = FCString::Atoi(*FontSizeStr);
	if (DefaultFontSize < 8 || DefaultFontSize > 20)
	{
		DefaultFontSize = 10;
	}
	
	FString AutoSaveStr = LoadConfigValue(TEXT("AutoSaveSettings"), TEXT("true"));
	bAutoSaveSettings = AutoSaveStr == TEXT("true");
	
	FString ShowTimestampsStr = LoadConfigValue(TEXT("ShowTimestamps"), TEXT("true"));
	bShowTimestamps = ShowTimestampsStr == TEXT("true");
}

void FAdastreaSettings::SaveSettings()
{
	SaveConfigValue(TEXT("LLMProvider"), LLMProvider);
	SaveConfigValue(TEXT("EmbeddingProvider"), EmbeddingProvider);
	SaveConfigValue(TEXT("GeminiAPIKey"), GeminiAPIKey);
	SaveConfigValue(TEXT("OpenAIAPIKey"), OpenAIAPIKey);
	SaveConfigValue(TEXT("DefaultFontSize"), FString::FromInt(DefaultFontSize));
	SaveConfigValue(TEXT("AutoSaveSettings"), bAutoSaveSettings ? TEXT("true") : TEXT("false"));
	SaveConfigValue(TEXT("ShowTimestamps"), bShowTimestamps ? TEXT("true") : TEXT("false"));
}

bool FAdastreaSettings::ValidateSettings(FString& OutErrorMessage) const
{
	// Check if an API key is configured
	if (!HasAPIKey())
	{
		if (LLMProvider == TEXT("gemini"))
		{
			OutErrorMessage = TEXT("Gemini API key is not configured. Please configure it in Settings.");
		}
		else if (LLMProvider == TEXT("openai"))
		{
			OutErrorMessage = TEXT("OpenAI API key is not configured. Please configure it in Settings.");
		}
		else
		{
			OutErrorMessage = FString::Printf(TEXT("API key for provider '%s' is not configured."), *LLMProvider);
		}
		return false;
	}

	// Validate API key format (basic check)
	const FString* APIKey = nullptr;
	if (LLMProvider == TEXT("gemini"))
	{
		APIKey = &GeminiAPIKey;
	}
	else if (LLMProvider == TEXT("openai"))
	{
		APIKey = &OpenAIAPIKey;
	}

	if (APIKey && APIKey->Len() < 10)
	{
		OutErrorMessage = TEXT("API key appears to be invalid (too short). Please verify your API key in Settings.");
		return false;
	}

	return true;
}

bool FAdastreaSettings::HasAPIKey() const
{
	if (LLMProvider == TEXT("gemini"))
	{
		return !GeminiAPIKey.IsEmpty();
	}
	else if (LLMProvider == TEXT("openai"))
	{
		return !OpenAIAPIKey.IsEmpty();
	}
	return false;
}

FString FAdastreaSettings::GetConfigFilePath()
{
	return FPaths::ProjectSavedDir() / TEXT("AdastreaDirector") / TEXT("config.ini");
}

TMap<FString, FString> FAdastreaSettings::LoadConfigMap(const FString& ConfigPath)
{
	TMap<FString, FString> ConfigMap;
	
	if (!FPaths::FileExists(ConfigPath))
	{
		return ConfigMap;
	}
	
	FString FileContent;
	if (!FFileHelper::LoadFileToString(FileContent, *ConfigPath))
	{
		return ConfigMap;
	}
	
	TArray<FString> Lines;
	FileContent.ParseIntoArrayLines(Lines);
	
	for (const FString& Line : Lines)
	{
		FString TrimmedLine = Line.TrimStartAndEnd();
		if (TrimmedLine.IsEmpty() || TrimmedLine.StartsWith(TEXT("#")))
		{
			continue;
		}
		
		FString LineKey, LineValue;
		if (TrimmedLine.Split(TEXT("="), &LineKey, &LineValue))
		{
			ConfigMap.Add(LineKey.TrimStartAndEnd(), LineValue.TrimStartAndEnd());
		}
	}
	
	return ConfigMap;
}

FString FAdastreaSettings::LoadConfigValue(const FString& Key, const FString& DefaultValue)
{
	FString ConfigPath = GetConfigFilePath();
	TMap<FString, FString> ConfigMap = LoadConfigMap(ConfigPath);
	
	const FString* Value = ConfigMap.Find(Key);
	return Value ? *Value : DefaultValue;
}

void FAdastreaSettings::SaveConfigValue(const FString& Key, const FString& Value)
{
	FString ConfigPath = GetConfigFilePath();
	FString ConfigDir = FPaths::GetPath(ConfigPath);
	
	// Create directory if it doesn't exist
	IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();
	if (!PlatformFile.DirectoryExists(*ConfigDir))
	{
		PlatformFile.CreateDirectoryTree(*ConfigDir);
	}
	
	// Load existing content
	TMap<FString, FString> ConfigMap = LoadConfigMap(ConfigPath);
	
	// Update or add the key
	ConfigMap.FindOrAdd(Key) = Value;
	
	// Write back to file
	FString NewContent;
	NewContent += TEXT("# Adastrea Director Configuration\n");
	NewContent += TEXT("# Auto-generated file\n\n");
	
	// Sort keys for deterministic output
	TArray<FString> SortedKeys;
	ConfigMap.GetKeys(SortedKeys);
	SortedKeys.Sort();
	for (const FString& SortedKey : SortedKeys)
	{
		NewContent += FString::Printf(TEXT("%s=%s\n"), *SortedKey, *ConfigMap[SortedKey]);
	}
	
	if (!FFileHelper::SaveStringToFile(NewContent, *ConfigPath))
	{
		UE_LOG(LogAdastreaDirector, Error, TEXT("Failed to save settings to: %s"), *ConfigPath);
	}
}
