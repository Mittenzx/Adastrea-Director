// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "SSettingsDialog.h"
#include "AdastreaDirectorEditorModule.h"
#include "Widgets/Input/SEditableTextBox.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Input/SCheckBox.h"
#include "Widgets/Input/SSpinBox.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SSeparator.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SUniformGridPanel.h"
#include "Styling/AppStyle.h"
#include "Framework/Application/SlateApplication.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/SecureHash.h"
#include "Misc/MessageDialog.h"
#include "HAL/PlatformFileManager.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformProcess.h"

#define LOCTEXT_NAMESPACE "SettingsDialog"

void SSettingsDialog::Construct(const FArguments& InArgs, TSharedPtr<SWindow> InParentWindow)
{
	ParentWindow = InParentWindow;
	
	// Load existing settings
	LoadSettings();

	ChildSlot
	[
		SNew(SBorder)
		.BorderImage(FAppStyle::GetBrush("ToolPanel.GroupBorder"))
		.Padding(20.0f)
		[
			SNew(SVerticalBox)

			// Title
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 20.0f)
			[
				SNew(STextBlock)
				.Text(LOCTEXT("SettingsTitle", "Settings"))
				.Font(FCoreStyle::GetDefaultFontStyle("Bold", 14))
			]

			// Content (scrollable)
			+ SVerticalBox::Slot()
			.FillHeight(1.0f)
			[
				SNew(SScrollBox)
				.Orientation(Orient_Vertical)

				+ SScrollBox::Slot()
				[
					SNew(SVerticalBox)

					// API Keys Section
					+ SVerticalBox::Slot()
					.AutoHeight()
					.Padding(0.0f, 0.0f, 0.0f, 15.0f)
					[
						CreateAPIKeysSection()
					]

					// LLM Settings Section
					+ SVerticalBox::Slot()
					.AutoHeight()
					.Padding(0.0f, 0.0f, 0.0f, 15.0f)
					[
						CreateLLMSettingsSection()
					]

					// Display Settings Section
					+ SVerticalBox::Slot()
					.AutoHeight()
					[
						CreateDisplaySettingsSection()
					]
				]
			]

			// Buttons
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 20.0f, 0.0f, 0.0f)
			[
				CreateButtonSection()
			]
		]
	];
}

void SSettingsDialog::OpenDialog()
{
	TSharedRef<SWindow> SettingsWindow = SNew(SWindow)
		.Title(LOCTEXT("SettingsWindowTitle", "Settings"))
		.ClientSize(FVector2D(550.0f, 600.0f))
		.SupportsMaximize(false)
		.SupportsMinimize(false)
		.SizingRule(ESizingRule::FixedSize);

	TSharedRef<SSettingsDialog> SettingsDialog = SNew(SSettingsDialog, SettingsWindow);
	SettingsWindow->SetContent(SettingsDialog);

	FSlateApplication::Get().AddModalWindow(SettingsWindow, FSlateApplication::Get().GetActiveTopLevelWindow());
}

TSharedRef<SWidget> SSettingsDialog::CreateAPIKeysSection()
{
	// Get the .env file path
	FString EnvFilePath = FPaths::Combine(FPaths::ProjectDir(), TEXT(".env"));
	FString EnvExamplePath = FPaths::Combine(FPaths::ProjectDir(), TEXT(".env.example"));
	bool bEnvFileExists = FPaths::FileExists(EnvFilePath);
	
	return SNew(SBorder)
		.BorderImage(FAppStyle::GetBrush("ToolPanel.GroupBorder"))
		.Padding(15.0f)
		[
			SNew(SVerticalBox)

			// Section Title
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 10.0f)
			[
				SNew(STextBlock)
				.Text(LOCTEXT("APIKeysSection", "API Configuration (.env)"))
				.Font(FCoreStyle::GetDefaultFontStyle("Bold", 10))
			]

			// Instructions
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 15.0f)
			[
				SNew(SBorder)
				.BorderImage(FAppStyle::GetBrush("ToolPanel.DarkGroupBorder"))
				.Padding(10.0f)
				[
					SNew(SVerticalBox)
					
					+ SVerticalBox::Slot()
					.AutoHeight()
					.Padding(0.0f, 0.0f, 0.0f, 5.0f)
					[
						SNew(STextBlock)
						.Text(LOCTEXT("EnvInstructions", "📝 API keys are configured via .env file"))
						.Font(FCoreStyle::GetDefaultFontStyle("Bold", 9))
					]
					
					+ SVerticalBox::Slot()
					.AutoHeight()
					[
						SNew(STextBlock)
						.Text(FText::FromString(FString::Printf(
							TEXT("1. Copy .env.example to .env in your project root\n")
							TEXT("2. Edit .env and add your API key:\n")
							TEXT("   GEMINI_KEY=your-api-key-here\n")
							TEXT("   (or GOOGLE_API_KEY for compatibility)\n")
							TEXT("   OPENAI_API_KEY=your-key (if using OpenAI)\n")
							TEXT("3. Restart Unreal Engine\n\n")
							TEXT(".env location: %s\n")
							TEXT("Status: %s"),
							*EnvFilePath,
							bEnvFileExists ? TEXT("✓ File exists") : TEXT("⚠ File not found")
						)))
						.AutoWrapText(true)
					]
				]
			]

			// LLM Provider Selection
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 10.0f)
			[
				SNew(SHorizontalBox)

				+ SHorizontalBox::Slot()
				.AutoWidth()
				.Padding(0.0f, 0.0f, 10.0f, 0.0f)
				[
					SNew(STextBlock)
					.Text(LOCTEXT("LLMProvider", "LLM Provider:"))
				]

				+ SHorizontalBox::Slot()
				.AutoWidth()
				.Padding(0.0f, 0.0f, 10.0f, 0.0f)
				[
					SNew(SCheckBox)
					.Style(FAppStyle::Get(), "RadioButton")
					.IsChecked(LLMProvider == TEXT("gemini") ? ECheckBoxState::Checked : ECheckBoxState::Unchecked)
					.OnCheckStateChanged_Lambda([this](ECheckBoxState NewState) {
						if (NewState == ECheckBoxState::Checked && LLMProvider != TEXT("gemini"))
						{
							OnLLMProviderChanged(TEXT("gemini"));
						}
					})
					[
						SNew(STextBlock)
						.Text(LOCTEXT("GeminiRecommended", "Gemini (Recommended)"))
					]
				]

				+ SHorizontalBox::Slot()
				.AutoWidth()
				[
					SNew(SCheckBox)
					.Style(FAppStyle::Get(), "RadioButton")
					.IsChecked(LLMProvider == TEXT("openai") ? ECheckBoxState::Checked : ECheckBoxState::Unchecked)
					.OnCheckStateChanged_Lambda([this](ECheckBoxState NewState) {
						if (NewState == ECheckBoxState::Checked && LLMProvider != TEXT("openai"))
						{
							OnLLMProviderChanged(TEXT("openai"));
						}
					})
					[
						SNew(STextBlock)
						.Text(LOCTEXT("OpenAI", "OpenAI"))
					]
				]
			]

			// Embedding Provider Selection
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 15.0f)
			[
				SNew(SHorizontalBox)

				+ SHorizontalBox::Slot()
				.AutoWidth()
				.Padding(0.0f, 0.0f, 10.0f, 0.0f)
				[
					SNew(STextBlock)
					.Text(LOCTEXT("EmbeddingProvider", "Embedding Provider:"))
				]

				+ SHorizontalBox::Slot()
				.AutoWidth()
				.Padding(0.0f, 0.0f, 10.0f, 0.0f)
				[
					SNew(SCheckBox)
					.Style(FAppStyle::Get(), "RadioButton")
					.IsChecked(EmbeddingProvider == TEXT("huggingface") ? ECheckBoxState::Checked : ECheckBoxState::Unchecked)
					.OnCheckStateChanged_Lambda([this](ECheckBoxState NewState) {
						if (NewState == ECheckBoxState::Checked && EmbeddingProvider != TEXT("huggingface"))
						{
							OnEmbeddingProviderChanged(TEXT("huggingface"));
						}
					})
					[
						SNew(STextBlock)
						.Text(LOCTEXT("HuggingFaceFree", "HuggingFace (Free)"))
					]
				]

				+ SHorizontalBox::Slot()
				.AutoWidth()
				[
					SNew(SCheckBox)
					.Style(FAppStyle::Get(), "RadioButton")
					.IsChecked(EmbeddingProvider == TEXT("openai") ? ECheckBoxState::Checked : ECheckBoxState::Unchecked)
					.OnCheckStateChanged_Lambda([this](ECheckBoxState NewState) {
						if (NewState == ECheckBoxState::Checked && EmbeddingProvider != TEXT("openai"))
						{
							OnEmbeddingProviderChanged(TEXT("openai"));
						}
					})
					[
						SNew(STextBlock)
						.Text(LOCTEXT("OpenAIEmbedding", "OpenAI"))
					]
				]
			]

			// Helper Buttons
			+ SVerticalBox::Slot()
			.AutoHeight()
			[
				SNew(SHorizontalBox)

				+ SHorizontalBox::Slot()
				.AutoWidth()
				.Padding(0.0f, 0.0f, 5.0f, 0.0f)
				[
					SNew(SButton)
					.Text(LOCTEXT("OpenEnvFileButton", "Open .env File"))
					.ToolTipText(LOCTEXT("OpenEnvFileTooltip", "Open the .env file in your default text editor"))
					.OnClicked_Lambda([EnvFilePath]() -> FReply {
						if (FPaths::FileExists(EnvFilePath))
						{
							FPlatformProcess::LaunchFileInDefaultExternalApplication(*EnvFilePath);
						}
						else
						{
							FMessageDialog::Open(EAppMsgType::Ok, 
								FText::FromString(TEXT(".env file not found. Please copy .env.example to .env first.")));
						}
						return FReply::Handled();
					})
				]

				+ SHorizontalBox::Slot()
				.AutoWidth()
				.Padding(0.0f, 0.0f, 5.0f, 0.0f)
				[
					SNew(SButton)
					.Text(LOCTEXT("OpenProjectFolderButton", "Open Project Folder"))
					.ToolTipText(LOCTEXT("OpenProjectFolderTooltip", "Open the project folder in file explorer"))
					.OnClicked_Lambda([]() -> FReply {
						FPlatformProcess::ExploreFolder(*FPaths::ProjectDir());
						return FReply::Handled();
					})
				]

				+ SHorizontalBox::Slot()
				.AutoWidth()
				[
					SNew(SButton)
					.Text(LOCTEXT("CreateEnvButton", "Create .env from Template"))
					.ToolTipText(LOCTEXT("CreateEnvTooltip", "Copy .env.example to .env"))
					.IsEnabled_Lambda([EnvFilePath]() { return !FPaths::FileExists(EnvFilePath); })
					.OnClicked_Lambda([EnvFilePath, EnvExamplePath]() -> FReply {
						if (FPaths::FileExists(EnvExamplePath))
						{
							if (IFileManager::Get().Copy(*EnvFilePath, *EnvExamplePath) == COPY_OK)
							{
								FMessageDialog::Open(EAppMsgType::Ok,
									FText::FromString(TEXT(".env file created successfully! Please edit it to add your API key, then restart Unreal Engine.")));
							}
							else
							{
								FMessageDialog::Open(EAppMsgType::Ok,
									FText::FromString(TEXT("Failed to create .env file. Please create it manually.")));
							}
						}
						else
						{
							FMessageDialog::Open(EAppMsgType::Ok,
								FText::FromString(TEXT(".env.example not found in project root.")));
						}
						return FReply::Handled();
					})
				]
			]
		];
}

TSharedRef<SWidget> SSettingsDialog::CreateLLMSettingsSection()
{
	return SNew(SBorder)
		.BorderImage(FAppStyle::GetBrush("ToolPanel.GroupBorder"))
		.Padding(15.0f)
		[
			SNew(SVerticalBox)

			// Section Header
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 10.0f)
			[
				SNew(STextBlock)
				.Text(LOCTEXT("LLMSettingsHeader", "LLM Configuration"))
				.Font(FCoreStyle::GetDefaultFontStyle("Bold", 12))
			]

			// Model Selection
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 5.0f)
			[
				SNew(STextBlock)
				.Text(LOCTEXT("ModelNameLabel", "Model:"))
			]

			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 15.0f)
			[
				SNew(SHorizontalBox)

				+ SHorizontalBox::Slot()
				.AutoWidth()
				.Padding(0.0f, 0.0f, 5.0f, 0.0f)
				[
					SNew(SButton)
					.Text(LOCTEXT("GeminiFlashButton", "Gemini 1.5 Flash"))
					.ToolTipText(LOCTEXT("GeminiFlashTooltip", "Fast and cost-effective model"))
					.OnClicked_Lambda([this]() {
						OnModelNameChanged(TEXT("gemini-1.5-flash"));
						return FReply::Handled();
					})
				]

				+ SHorizontalBox::Slot()
				.AutoWidth()
				.Padding(0.0f, 0.0f, 5.0f, 0.0f)
				[
					SNew(SButton)
					.Text(LOCTEXT("GeminiProButton", "Gemini 1.5 Pro"))
					.ToolTipText(LOCTEXT("GeminiProTooltip", "More capable for complex tasks"))
					.OnClicked_Lambda([this]() {
						OnModelNameChanged(TEXT("gemini-1.5-pro"));
						return FReply::Handled();
					})
				]

				+ SHorizontalBox::Slot()
				.AutoWidth()
				.Padding(0.0f, 0.0f, 5.0f, 0.0f)
				[
					SNew(SButton)
					.Text(LOCTEXT("GPT4Button", "GPT-4"))
					.ToolTipText(LOCTEXT("GPT4Tooltip", "OpenAI's most capable model"))
					.OnClicked_Lambda([this]() {
						OnModelNameChanged(TEXT("gpt-4"));
						return FReply::Handled();
					})
				]

				+ SHorizontalBox::Slot()
				.AutoWidth()
				[
					SNew(SButton)
					.Text(LOCTEXT("GPT4TurboButton", "GPT-4 Turbo"))
					.ToolTipText(LOCTEXT("GPT4TurboTooltip", "Faster and more cost-effective"))
					.OnClicked_Lambda([this]() {
						OnModelNameChanged(TEXT("gpt-4-turbo"));
						return FReply::Handled();
					})
				]
			]

			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 10.0f)
			[
				SNew(STextBlock)
				.Text_Lambda([this]() {
					return FText::Format(LOCTEXT("CurrentModelText", "Current: {0}"), FText::FromString(ModelName));
				})
				.Font(FCoreStyle::GetDefaultFontStyle("Italic", 9))
			]

			// Temperature Slider
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 5.0f)
			[
				SNew(STextBlock)
				.Text(LOCTEXT("TemperatureLabel", "Temperature (Creativity):"))
			]

			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 5.0f)
			[
				SNew(SHorizontalBox)

				+ SHorizontalBox::Slot()
				.FillWidth(1.0f)
				[
					SNew(SSpinBox<float>)
					.MinValue(0.0f)
					.MaxValue(2.0f)
					.Delta(0.1f)
					.Value_Lambda([this]() { return Temperature; })
					.OnValueChanged_Lambda([this](float NewValue) {
						OnTemperatureChanged(NewValue);
					})
				]

				+ SHorizontalBox::Slot()
				.AutoWidth()
				.Padding(10.0f, 0.0f, 0.0f, 0.0f)
				[
					SNew(STextBlock)
					.Text_Lambda([this]() {
						return FText::AsNumber(Temperature, &FNumberFormattingOptions::DefaultNoGrouping());
					})
					.MinDesiredWidth(40.0f)
				]
			]

			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 15.0f)
			[
				SNew(STextBlock)
				.Text(LOCTEXT("TemperatureHint", "Lower values = more focused, higher values = more creative. Maximum depends on provider (OpenAI: 0.0-1.0, Gemini: 0.0-2.0)"))
				.Font(FCoreStyle::GetDefaultFontStyle("Italic", 8))
			]

			// Max Tokens
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 5.0f)
			[
				SNew(STextBlock)
				.Text(LOCTEXT("MaxTokensLabel", "Max Response Length (Tokens):"))
			]

			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 5.0f)
			[
				SNew(SSpinBox<int32>)
				.MinValue(100)
				.MaxValue(8000)
				.Value_Lambda([this]() { return MaxTokens; })
				.OnValueChanged_Lambda([this](int32 NewValue) {
					OnMaxTokensChanged(NewValue);
				})
			]

			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 15.0f)
			[
				SNew(STextBlock)
				.Text(LOCTEXT("MaxTokensHint", "Higher values allow longer responses but may cost more"))
				.Font(FCoreStyle::GetDefaultFontStyle("Italic", 8))
			]

			// Test API Key Button
			+ SVerticalBox::Slot()
			.AutoHeight()
			[
				SNew(SHorizontalBox)

				+ SHorizontalBox::Slot()
				.AutoWidth()
				[
					SNew(SButton)
					.Text(LOCTEXT("TestAPIKeyButton", "Test API Key"))
					.ToolTipText(LOCTEXT("TestAPIKeyTooltip", "Send a test request to verify your API key works"))
					.OnClicked(this, &SSettingsDialog::OnTestAPIKeyClicked)
				]

				+ SHorizontalBox::Slot()
				.FillWidth(1.0f)
				.Padding(10.0f, 0.0f, 0.0f, 0.0f)
				[
					SAssignNew(TestStatusText, STextBlock)
					.Text(LOCTEXT("TestStatusIdle", "Click to test"))
				]
			]
		];
}

TSharedRef<SWidget> SSettingsDialog::CreateDisplaySettingsSection()
{
	return SNew(SBorder)
		.BorderImage(FAppStyle::GetBrush("ToolPanel.GroupBorder"))
		.Padding(15.0f)
		[
			SNew(SVerticalBox)

			// Section Title
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 10.0f)
			[
				SNew(STextBlock)
				.Text(LOCTEXT("DisplaySection", "Display"))
				.Font(FCoreStyle::GetDefaultFontStyle("Bold", 10))
			]

			// Font Size
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 5.0f, 0.0f, 10.0f)
			[
				SNew(SHorizontalBox)

				+ SHorizontalBox::Slot()
				.AutoWidth()
				.Padding(0.0f, 0.0f, 10.0f, 0.0f)
				[
					SNew(STextBlock)
					.Text(LOCTEXT("DefaultFontSize", "Default Font Size:"))
				]

				+ SHorizontalBox::Slot()
				.AutoWidth()
				[
					SNew(SSpinBox<int32>)
					.MinValue(8)
					.MaxValue(20)
					.Value(DefaultFontSize)
					.OnValueChanged_Lambda([this](int32 NewValue) {
						OnFontSizeChanged(NewValue);
					})
				]

				+ SHorizontalBox::Slot()
				.AutoWidth()
				.Padding(5.0f, 0.0f, 0.0f, 0.0f)
				[
					SNew(STextBlock)
					.Text(LOCTEXT("FontSizeUnit", "pt"))
				]
			]

			// Auto-save Settings
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0.0f, 0.0f, 0.0f, 10.0f)
			[
				SNew(SCheckBox)
				.IsChecked(bAutoSaveSettings ? ECheckBoxState::Checked : ECheckBoxState::Unchecked)
				.OnCheckStateChanged_Lambda([this](ECheckBoxState NewState) {
					OnAutoSaveChanged(NewState);
				})
				[
					SNew(STextBlock)
					.Text(LOCTEXT("AutoSaveSettings", "Auto-save settings"))
				]
			]

			// Show Timestamps
			+ SVerticalBox::Slot()
			.AutoHeight()
			[
				SNew(SCheckBox)
				.IsChecked(bShowTimestamps ? ECheckBoxState::Checked : ECheckBoxState::Unchecked)
				.OnCheckStateChanged_Lambda([this](ECheckBoxState NewState) {
					OnShowTimestampsChanged(NewState);
				})
				[
					SNew(STextBlock)
					.Text(LOCTEXT("ShowTimestamps", "Show timestamps in conversation"))
				]
			]
		];
}

TSharedRef<SWidget> SSettingsDialog::CreateButtonSection()
{
	return SNew(SHorizontalBox)

		+ SHorizontalBox::Slot()
		.FillWidth(1.0f)
		[
			SNew(SSpacer)
		]

		+ SHorizontalBox::Slot()
		.AutoWidth()
		.Padding(0.0f, 0.0f, 10.0f, 0.0f)
		[
			SNew(SButton)
			.Text(LOCTEXT("SaveButton", "Save"))
			.OnClicked(this, &SSettingsDialog::OnSaveClicked)
		]

		+ SHorizontalBox::Slot()
		.AutoWidth()
		[
			SNew(SButton)
			.Text(LOCTEXT("CancelButton", "Cancel"))
			.OnClicked(this, &SSettingsDialog::OnCancelClicked)
		];
}

FReply SSettingsDialog::OnSaveClicked()
{
	SaveSettings();
	
	if (TSharedPtr<SWindow> Window = ParentWindow.Pin())
	{
		Window->RequestDestroyWindow();
	}
	
	return FReply::Handled();
}

FReply SSettingsDialog::OnCancelClicked()
{
	if (TSharedPtr<SWindow> Window = ParentWindow.Pin())
	{
		Window->RequestDestroyWindow();
	}
	
	return FReply::Handled();
}

void SSettingsDialog::OnLLMProviderChanged(FString NewProvider)
{
	LLMProvider = NewProvider;
}

void SSettingsDialog::OnEmbeddingProviderChanged(FString NewProvider)
{
	EmbeddingProvider = NewProvider;
}

void SSettingsDialog::OnModelNameChanged(FString NewModel)
{
	ModelName = NewModel;
}

void SSettingsDialog::OnTemperatureChanged(float NewTemperature)
{
	Temperature = NewTemperature;
}

void SSettingsDialog::OnMaxTokensChanged(int32 NewMaxTokens)
{
	MaxTokens = NewMaxTokens;
}

void SSettingsDialog::OnFontSizeChanged(int32 NewSize)
{
	DefaultFontSize = NewSize;
}

void SSettingsDialog::OnAutoSaveChanged(ECheckBoxState NewState)
{
	bAutoSaveSettings = (NewState == ECheckBoxState::Checked);
}

void SSettingsDialog::OnShowTimestampsChanged(ECheckBoxState NewState)
{
	bShowTimestamps = (NewState == ECheckBoxState::Checked);
}

FReply SSettingsDialog::OnTestAPIKeyClicked()
{
	// Update status to show testing
	if (TestStatusText.IsValid())
	{
		TestStatusText->SetText(LOCTEXT("TestStatusTesting", "Testing..."));
	}

	// Reload settings to get latest .env values
	FAdastreaSettings::Get().LoadSettings();
	
	// Test the API key by checking if it's present in the loaded settings
	FString APIKey;
	FString Provider = LLMProvider.ToLower();
	
	if (Provider == TEXT("gemini"))
	{
		APIKey = FAdastreaSettings::Get().GetGeminiAPIKey();
	}
	else if (Provider == TEXT("openai"))
	{
		APIKey = FAdastreaSettings::Get().GetOpenAIAPIKey();
	}
	else
	{
		if (TestStatusText.IsValid())
		{
			TestStatusText->SetText(FText::FromString(
				FString::Printf(TEXT("⚠️ Unknown provider: %s"), *LLMProvider)
			));
		}
		return FReply::Handled();
	}

	if (APIKey.IsEmpty())
	{
		if (TestStatusText.IsValid())
		{
			TestStatusText->SetText(FText::FromString(
				FString::Printf(
					TEXT("❌ No API key found for %s\n\n")
					TEXT("Please add %s to your .env file\n")
					TEXT("and restart Unreal Engine."),
					*Provider.ToUpper(),
					Provider == TEXT("gemini") ? TEXT("GEMINI_API_KEY") : TEXT("OPENAI_API_KEY")
				)
			));
		}
	}
	else
	{
		// API key is present - show partial key for verification
		FString MaskedKey = APIKey.Left(8) + TEXT("...") + APIKey.Right(4);
		if (TestStatusText.IsValid())
		{
			TestStatusText->SetText(FText::FromString(
				FString::Printf(
					TEXT("✓ API key loaded: %s\n\n")
					TEXT("Key format appears valid.\n")
					TEXT("Test with a query to verify it works with the API."),
					*MaskedKey
				)
			));
		}
	}

	return FReply::Handled();
}

void SSettingsDialog::LoadSettings()
{
	// Load from config file
	// Note: API keys are now configured via .env file, not stored in config.ini
	LLMProvider = LoadConfigValue(TEXT("LLMProvider"), TEXT("gemini"));
	EmbeddingProvider = LoadConfigValue(TEXT("EmbeddingProvider"), TEXT("huggingface"));
	ModelName = LoadConfigValue(TEXT("ModelName"), TEXT("gemini-1.5-flash"));
	
	FString TemperatureStr = LoadConfigValue(TEXT("Temperature"), TEXT("0.7"));
	Temperature = FCString::Atof(*TemperatureStr);
	if (Temperature < 0.0f || Temperature > 2.0f)
	{
		Temperature = 0.7f; // Reset to default if out of bounds
	}
	
	FString MaxTokensStr = LoadConfigValue(TEXT("MaxTokens"), TEXT("2000"));
	MaxTokens = FCString::Atoi(*MaxTokensStr);
	if (MaxTokens < 100 || MaxTokens > 8000)
	{
		MaxTokens = 2000; // Reset to default if out of bounds
	}
	
	FString FontSizeStr = LoadConfigValue(TEXT("DefaultFontSize"), TEXT("10"));
	DefaultFontSize = FCString::Atoi(*FontSizeStr);
	// Validate font size is within allowed range
	if (DefaultFontSize < 8 || DefaultFontSize > 20)
	{
		DefaultFontSize = 10; // Reset to default if out of bounds or invalid
	}
	
	FString AutoSaveStr = LoadConfigValue(TEXT("AutoSaveSettings"), TEXT("true"));
	bAutoSaveSettings = AutoSaveStr == TEXT("true");
	
	FString ShowTimestampsStr = LoadConfigValue(TEXT("ShowTimestamps"), TEXT("true"));
	bShowTimestamps = ShowTimestampsStr == TEXT("true");
	
	// Initialize API key strings as empty (they're read from .env by Python backend)
	GeminiAPIKey = TEXT("");
	OpenAIAPIKey = TEXT("");
}

void SSettingsDialog::SaveSettings()
{
	// Save provider preferences, LLM settings, and display settings
	// Note: API keys are configured via .env file and not saved here
	SaveConfigValue(TEXT("LLMProvider"), LLMProvider);
	SaveConfigValue(TEXT("EmbeddingProvider"), EmbeddingProvider);
	SaveConfigValue(TEXT("ModelName"), ModelName);
	SaveConfigValue(TEXT("Temperature"), FString::SanitizeFloat(Temperature));
	SaveConfigValue(TEXT("MaxTokens"), FString::FromInt(MaxTokens));
	SaveConfigValue(TEXT("DefaultFontSize"), FString::FromInt(DefaultFontSize));
	SaveConfigValue(TEXT("AutoSaveSettings"), bAutoSaveSettings ? TEXT("true") : TEXT("false"));
	SaveConfigValue(TEXT("ShowTimestamps"), bShowTimestamps ? TEXT("true") : TEXT("false"));
}

TMap<FString, FString> SSettingsDialog::LoadConfigMap(const FString& ConfigPath)
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

FString SSettingsDialog::LoadConfigValue(const FString& Key, const FString& DefaultValue)
{
	FString ConfigPath = FPaths::ProjectSavedDir() / TEXT("AdastreaDirector") / TEXT("config.ini");
	TMap<FString, FString> ConfigMap = LoadConfigMap(ConfigPath);
	
	const FString* Value = ConfigMap.Find(Key);
	return Value ? *Value : DefaultValue;
}

void SSettingsDialog::SaveConfigValue(const FString& Key, const FString& Value)
{
	// Get config file path
	FString ConfigPath = FPaths::ProjectSavedDir() / TEXT("AdastreaDirector") / TEXT("config.ini");
	FString ConfigDir = FPaths::GetPath(ConfigPath);
	
	// Create directory if it doesn't exist
	IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();
	if (!PlatformFile.DirectoryExists(*ConfigDir))
	{
		PlatformFile.CreateDirectoryTree(*ConfigDir);
	}
	
	// Load existing content using helper
	TMap<FString, FString> ConfigMap = LoadConfigMap(ConfigPath);
	
	// Update or add the key
	ConfigMap.FindOrAdd(Key) = Value;
	
	// Write back to file
	FString NewContent;
	NewContent += TEXT("# Adastrea Director Configuration\n");
	NewContent += TEXT("# Auto-generated file\n");
	NewContent += TEXT("# Note: Manual edits to this file may be overwritten when saving from the UI\n\n");
	
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
		UE_LOG(LogAdastreaDirectorEditor, Error, TEXT("Failed to save settings to: %s"), *ConfigPath);
	}
}

#undef LOCTEXT_NAMESPACE
