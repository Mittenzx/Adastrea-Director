// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "SAdastreaDirectorPanel.h"
#include "SSettingsDialog.h"
#include "SStatusIndicator.h"
#include "AdastreaDirectorEditorModule.h"
#include "AdastreaDirectorModule.h"
#include "AdastreaSettings.h"
#include "AdastreaStartupValidator.h"
// VibeUE components
#include "AdastreaLLMClient.h"
#include "AdastreaScriptService.h"
#include "AdastreaAssetService.h"
#include "Widgets/Input/SEditableTextBox.h"
#include "Widgets/Input/SMultiLineEditableTextBox.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SSeparator.h"
#include "Widgets/Docking/SDockTab.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SGridPanel.h"
#include "Widgets/Notifications/SProgressBar.h"
#include "Widgets/Layout/SWidgetSwitcher.h"
#include "Widgets/Input/SCheckBox.h"
#include "Styling/AppStyle.h"
#include "Styling/SlateTypes.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonReader.h"
#include "DesktopPlatformModule.h"
#include "IDesktopPlatform.h"
#include "Framework/Application/SlateApplication.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/MessageDialog.h"
#include "Interfaces/IPluginManager.h"

#define LOCTEXT_NAMESPACE "AdastreaDirectorPanel"

// Plugin name constant for consistency
static const FString PluginName(TEXT("AdastreaDirector"));

SAdastreaDirectorPanel::~SAdastreaDirectorPanel()
{
	// Cleanup
}

FString SAdastreaDirectorPanel::GetPluginVersion()
{
	// Cache the version string to avoid repeated plugin manager lookups
	static FString CachedVersion;
	static bool bVersionCached = false;
	
	if (!bVersionCached)
	{
		// Get the plugin descriptor to read the version
		TSharedPtr<IPlugin> Plugin = IPluginManager::Get().FindPlugin(PluginName);
		if (Plugin.IsValid())
		{
			const FPluginDescriptor& Descriptor = Plugin->GetDescriptor();
			CachedVersion = Descriptor.VersionName;
		}
		else
		{
			CachedVersion = TEXT("Unknown");
		}
		bVersionCached = true;
	}
	
	return CachedVersion;
}

void SAdastreaDirectorPanel::Construct(const FArguments& InArgs)
{
	// Initialize state
	bIsProcessing = false;
	CurrentResults = LOCTEXT("WelcomeMessage", "Welcome to Adastrea Director!\n\nEnter a query above and click 'Send Query' or press Enter to get started.\n\nExample: \"What is Unreal Engine?\"");
	CurrentTabIndex = 0; // Start with Query tab
	LastDashboardRefreshTime = 0.0;
	LastConnectionStatusUpdateTime = 0.0;
	CurrentLogContent = TEXT("Dashboard logs will appear here...");
	CachedLogContentText = FText::FromString(CurrentLogContent);
	CachedConnectionStatus = FText::FromString(TEXT("Loading VibeUE architecture..."));
	LastStatusLightsUpdateTime = 0.0;
	
	// Initialize Tests tab state
	bIsTestRunning = false;
	TestProgress = 0.0f;
	TestStatusMessage = LOCTEXT("TestsIdle", "Ready to run tests");
	CurrentTestOutput = TEXT("🧪 Plugin Self-Test Suite\n\nClick a test button above to run tests.\nResults will appear here.\n");
	CachedTestOutputText = FText::FromString(CurrentTestOutput);
	LastTestOutputUpdateTime = 0.0;

	ChildSlot
	[
		SNew(SVerticalBox)
		
		// Header
		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 10.0f, 10.0f, 5.0f)
		[
			SNew(SHorizontalBox)
			
			+ SHorizontalBox::Slot()
			.FillWidth(1.0f)
			[
				SNew(SVerticalBox)
				
				+ SVerticalBox::Slot()
				.AutoHeight()
				[
					SNew(STextBlock)
					.Text(LOCTEXT("PanelTitle", "Adastrea Director - AI Assistant"))
					.Font(FCoreStyle::GetDefaultFontStyle("Bold", 16))
				]
				
				+ SVerticalBox::Slot()
				.AutoHeight()
				.Padding(0.0f, 2.0f, 0.0f, 0.0f)
				[
					SNew(STextBlock)
					.Text(FText::FromString(FString::Printf(TEXT("Version %s"), *GetPluginVersion())))
					.Font(FCoreStyle::GetDefaultFontStyle("Regular", 9))
					.ColorAndOpacity(FSlateColor(FLinearColor(0.7f, 0.7f, 0.7f, 1.0f)))
				]
			]
			
			+ SHorizontalBox::Slot()
			.AutoWidth()
			[
				SNew(SButton)
				.Text(LOCTEXT("SettingsButton", "Settings"))
				.ToolTipText(LOCTEXT("SettingsTooltip", "Open Settings (Ctrl+, - requires panel focus)"))
				.OnClicked(this, &SAdastreaDirectorPanel::OnSettingsClicked)
			]
		]

		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 0.0f, 10.0f, 10.0f)
		[
			SNew(SSeparator)
			.Orientation(Orient_Horizontal)
		]

		// Tab buttons
		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 5.0f, 10.0f, 5.0f)
		[
			SNew(SHorizontalBox)
			
			// Query Tab Button
			+ SHorizontalBox::Slot()
			.AutoWidth()
			.Padding(0.0f, 0.0f, 5.0f, 0.0f)
			[
				SNew(SCheckBox)
				.Style(FAppStyle::Get(), "RadioButton")
				.IsChecked(this, &SAdastreaDirectorPanel::GetTabButtonCheckedState, 0)
				.OnCheckStateChanged_Lambda([this](ECheckBoxState NewState) {
					if (NewState == ECheckBoxState::Checked)
					{
						OnTabButtonClicked(0);
					}
				})
				[
					SNew(STextBlock)
					.Text(LOCTEXT("QueryTabButton", "Query"))
					.Font(FCoreStyle::GetDefaultFontStyle("Bold", 10))
				]
			]

			// Dashboard Tab Button
			+ SHorizontalBox::Slot()
			.AutoWidth()
			.Padding(0.0f, 0.0f, 5.0f, 0.0f)
			[
				SNew(SCheckBox)
				.Style(FAppStyle::Get(), "RadioButton")
				.IsChecked(this, &SAdastreaDirectorPanel::GetTabButtonCheckedState, 1)
				.OnCheckStateChanged_Lambda([this](ECheckBoxState NewState) {
					if (NewState == ECheckBoxState::Checked)
					{
						OnTabButtonClicked(1);
					}
				})
				[
					SNew(STextBlock)
					.Text(LOCTEXT("DashboardTabButton", "Dashboard"))
					.Font(FCoreStyle::GetDefaultFontStyle("Bold", 10))
				]
			]

			// Tests Tab Button
			+ SHorizontalBox::Slot()
			.AutoWidth()
			.Padding(0.0f, 0.0f, 5.0f, 0.0f)
			[
				SNew(SCheckBox)
				.Style(FAppStyle::Get(), "RadioButton")
				.IsChecked(this, &SAdastreaDirectorPanel::GetTabButtonCheckedState, 2)
				.OnCheckStateChanged_Lambda([this](ECheckBoxState NewState) {
					if (NewState == ECheckBoxState::Checked)
					{
						OnTabButtonClicked(2);
					}
				})
				[
					SNew(STextBlock)
					.Text(LOCTEXT("TestsTabButton", "Tests"))
					.Font(FCoreStyle::GetDefaultFontStyle("Bold", 10))
				]
			]
		]

		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 0.0f, 10.0f, 5.0f)
		[
			SNew(SSeparator)
			.Orientation(Orient_Horizontal)
		]

		// Tab content area with widget switcher
		+ SVerticalBox::Slot()
		.FillHeight(1.0f)
		[
			SAssignNew(TabContentSwitcher, SWidgetSwitcher)
			.WidgetIndex_Lambda([this]() { return CurrentTabIndex; })
			
			// Query Tab (index 0)
			+ SWidgetSwitcher::Slot()
			[
				CreateQueryTab()
			]
			
			// Dashboard Tab (index 1)
			+ SWidgetSwitcher::Slot()
			[
				CreateDashboardTab()
			]
			
			// Tests Tab (index 2)
			+ SWidgetSwitcher::Slot()
			[
				CreateTestsTab()
			]
		]
	];
}

TSharedRef<SWidget> SAdastreaDirectorPanel::CreateQueryTab()
{
	return SNew(SVerticalBox)
		
		// Query Input Section
		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 5.0f, 10.0f, 5.0f)
		[
			SNew(STextBlock)
			.Text(LOCTEXT("QueryLabel", "Query:"))
			.Font(FCoreStyle::GetDefaultFontStyle("Bold", 10))
		]

		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 0.0f, 10.0f, 5.0f)
		[
			SNew(SHorizontalBox)
			
			// Query Input Box
			+ SHorizontalBox::Slot()
			.FillWidth(1.0f)
			.Padding(0.0f, 0.0f, 5.0f, 0.0f)
			[
				SAssignNew(QueryInputBox, SEditableTextBox)
				.HintText(LOCTEXT("QueryHint", "Enter your query here..."))
				.OnTextChanged(this, &SAdastreaDirectorPanel::OnQueryTextChanged)
				.OnTextCommitted(this, &SAdastreaDirectorPanel::OnQueryTextCommitted)
			]

			// Send Button
			+ SHorizontalBox::Slot()
			.AutoWidth()
			.Padding(0.0f, 0.0f, 5.0f, 0.0f)
			[
				SNew(SButton)
				.Text(LOCTEXT("SendButton", "Send Query"))
				.ToolTipText(LOCTEXT("SendButtonTooltip", "Send query to Python backend"))
				.OnClicked(this, &SAdastreaDirectorPanel::OnSendQueryClicked)
				.IsEnabled(this, &SAdastreaDirectorPanel::IsSendButtonEnabled)
			]

			// Clear Results Button
			+ SHorizontalBox::Slot()
			.AutoWidth()
			[
				SNew(SButton)
				.Text(LOCTEXT("ClearResultsButton", "Clear Results"))
				.ToolTipText(LOCTEXT("ClearResultsTooltip", "Clear the results display"))
				.OnClicked(this, &SAdastreaDirectorPanel::OnClearHistoryClicked)
			]
		]

		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 5.0f, 10.0f, 10.0f)
		[
			SNew(SSeparator)
			.Orientation(Orient_Horizontal)
		]

		// Results Section
		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 5.0f, 10.0f, 5.0f)
		[
			SNew(STextBlock)
			.Text(LOCTEXT("ResultsLabel", "Results:"))
			.Font(FCoreStyle::GetDefaultFontStyle("Bold", 10))
		]

		+ SVerticalBox::Slot()
		.FillHeight(1.0f)
		.Padding(10.0f, 0.0f, 10.0f, 10.0f)
		[
			SNew(SBox)
			.MinDesiredHeight(200.0f)
			[
				SNew(SScrollBox)
				.Orientation(Orient_Vertical)
				
				+ SScrollBox::Slot()
				[
					SAssignNew(ResultsDisplay, SMultiLineEditableTextBox)
					.Text_Lambda([this]() { return CurrentResults; })
					.IsReadOnly(true)
					.AutoWrapText(true)
				]
			]
		];
}

TSharedRef<SWidget> SAdastreaDirectorPanel::CreateDashboardTab()
{
	return SNew(SVerticalBox)
		
		// Status Indicators Section
		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 10.0f, 10.0f, 5.0f)
		[
			SNew(STextBlock)
			.Text(LOCTEXT("StatusIndicatorsLabel", "VibeUE Component Status:"))
			.Font(FCoreStyle::GetDefaultFontStyle("Bold", 12))
		]

		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 0.0f, 10.0f, 10.0f)
		[
			SNew(SBorder)
			.BorderImage(FAppStyle::GetBrush("ToolPanel.GroupBorder"))
			.Padding(10.0f)
			[
				SNew(SGridPanel)
				.FillColumn(0, 1.0f)
				.FillColumn(1, 1.0f)
				
				// Row 0: API Key & LLM Client
				+ SGridPanel::Slot(0, 0)
				.Padding(5.0f)
				[
					SAssignNew(APIKeyStatusLight, SStatusIndicator)
					.StatusText(LOCTEXT("APIKeyStatus", "API Key Configuration"))
					.InitialStatus(SStatusIndicator::EStatus::Unknown)
				]
				
				+ SGridPanel::Slot(1, 0)
				.Padding(5.0f)
				[
					SAssignNew(LLMClientStatusLight, SStatusIndicator)
					.StatusText(LOCTEXT("LLMClientStatus", "LLM Client"))
					.InitialStatus(SStatusIndicator::EStatus::Unknown)
				]
				
				// Row 1: Script Service & Asset Service
				+ SGridPanel::Slot(0, 1)
				.Padding(5.0f)
				[
					SAssignNew(ScriptServiceStatusLight, SStatusIndicator)
					.StatusText(LOCTEXT("ScriptServiceStatus", "Python Script Service"))
					.InitialStatus(SStatusIndicator::EStatus::Unknown)
				]
				
				+ SGridPanel::Slot(1, 1)
				.Padding(5.0f)
				[
					SAssignNew(AssetServiceStatusLight, SStatusIndicator)
					.StatusText(LOCTEXT("AssetServiceStatus", "Asset Discovery Service"))
					.InitialStatus(SStatusIndicator::EStatus::Unknown)
				]
			]
		]

		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 5.0f, 10.0f, 10.0f)
		[
			SNew(SSeparator)
			.Orientation(Orient_Horizontal)
		]

		// Connection Status Section
		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 5.0f, 10.0f, 5.0f)
		[
			SNew(STextBlock)
			.Text(LOCTEXT("ConnectionStatusLabel", "Detailed Status:"))
			.Font(FCoreStyle::GetDefaultFontStyle("Bold", 12))
		]

		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 0.0f, 10.0f, 10.0f)
		[
			SNew(SBorder)
			.BorderImage(FAppStyle::GetBrush("ToolPanel.GroupBorder"))
			.Padding(10.0f)
			[
				SNew(SVerticalBox)
				
				+ SVerticalBox::Slot()
				.AutoHeight()
				.Padding(0.0f, 0.0f, 0.0f, 10.0f)
				[
					SAssignNew(ConnectionStatusText, STextBlock)
					.Text_Lambda([this]() { return CachedConnectionStatus; })
					.AutoWrapText(true)
				]

				+ SVerticalBox::Slot()
				.AutoHeight()
				[
					SNew(SHorizontalBox)
					
					+ SHorizontalBox::Slot()
					.AutoWidth()
					.Padding(0.0f, 0.0f, 5.0f, 0.0f)
					[
						SNew(SButton)
						.Text(LOCTEXT("RefreshStatusButton", "Refresh Status"))
						.ToolTipText(LOCTEXT("RefreshStatusTooltip", "Update component status and indicators"))
						.OnClicked(this, &SAdastreaDirectorPanel::OnRefreshDashboardClicked)
					]
				]
			]
		]

		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 5.0f, 10.0f, 10.0f)
		[
			SNew(SSeparator)
			.Orientation(Orient_Horizontal)
		]

		// Logs Section
		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 5.0f, 10.0f, 5.0f)
		[
			SNew(SHorizontalBox)
			
			+ SHorizontalBox::Slot()
			.FillWidth(1.0f)
			[
				SNew(STextBlock)
				.Text(LOCTEXT("LogsLabel", "System Logs:"))
				.Font(FCoreStyle::GetDefaultFontStyle("Bold", 12))
			]

			+ SHorizontalBox::Slot()
			.AutoWidth()
			[
				SNew(SButton)
				.Text(LOCTEXT("ClearLogsButton", "Clear Logs"))
				.ToolTipText(LOCTEXT("ClearLogsTooltip", "Clear the log display"))
				.OnClicked(this, &SAdastreaDirectorPanel::OnClearLogsClicked)
			]
		]

		+ SVerticalBox::Slot()
		.FillHeight(1.0f)
		.Padding(10.0f, 0.0f, 10.0f, 10.0f)
		[
			SNew(SBox)
			.MinDesiredHeight(300.0f)
			[
				SNew(SScrollBox)
				.Orientation(Orient_Vertical)
				
				+ SScrollBox::Slot()
				[
					SAssignNew(LogDisplay, SMultiLineEditableTextBox)
					.Text_Lambda([this]() { return CachedLogContentText; })
					.IsReadOnly(true)
					.AutoWrapText(true)
				]
			]
		];
}

void SAdastreaDirectorPanel::OnQueryTextChanged(const FText& NewText)
{
	CurrentQuery = NewText;
}

void SAdastreaDirectorPanel::OnQueryTextCommitted(const FText& NewText, ETextCommit::Type CommitType)
{
	// If user pressed Enter, send the query
	if (CommitType == ETextCommit::OnEnter)
	{
		CurrentQuery = NewText;
		OnSendQueryClicked();
	}
}

FReply SAdastreaDirectorPanel::OnSendQueryClicked()
{
	if (!CanSendQuery())
	{
		return FReply::Handled();
	}

	FString QueryString = CurrentQuery.ToString().TrimStartAndEnd();
	
	if (QueryString.IsEmpty())
	{
		UpdateResults(TEXT("Error: Query cannot be empty."));
		return FReply::Handled();
	}

	// Set processing state with RAII guard to ensure it's reset
	struct FProcessingGuard
	{
		bool& Flag;
		FProcessingGuard(bool& InFlag) : Flag(InFlag) { Flag = true; }
		~FProcessingGuard() { Flag = false; }
	} ProcessingGuard(bIsProcessing);
	
	UpdateResults(TEXT("Processing query..."));

	// Send query to Python backend
	SendQueryToPython(QueryString);

	return FReply::Handled();
}

void SAdastreaDirectorPanel::SendQueryToPython(const FString& Query)
{
	// Get settings for API configuration
	FAdastreaSettings& Settings = FAdastreaSettings::Get();
	
	// Validate settings
	FString ErrorMessage;
	if (!Settings.ValidateSettings(ErrorMessage))
	{
		UpdateResults(FString::Printf(TEXT("❌ Configuration Error\n\n%s\n\nPlease configure your API key in Settings."), *ErrorMessage));
		bIsProcessing = false;
		return;
	}
	
	// Create LLM client
	TSharedPtr<FAdastreaLLMClient> LLMClient = MakeShared<FAdastreaLLMClient>();
	
	// Configure client from settings
	FString Provider = Settings.GetLLMProvider();
	FString APIKey = Settings.GetAPIKey();
	
	if (Provider == TEXT("Gemini"))
	{
		LLMClient->SetProvider(ELLMProvider::Gemini, APIKey);
		LLMClient->SetModel(TEXT("gemini-1.5-flash"));
	}
	else if (Provider == TEXT("OpenAI"))
	{
		LLMClient->SetProvider(ELLMProvider::OpenAI, APIKey);
		LLMClient->SetModel(TEXT("gpt-4"));
	}
	else
	{
		UpdateResults(FString::Printf(TEXT("❌ Unknown provider: %s\n\nSupported providers: Gemini, OpenAI"), *Provider));
		bIsProcessing = false;
		return;
	}
	
	// Prepare messages
	TArray<FChatMessage> Messages;
	
	// System message
	FChatMessage SystemMsg;
	SystemMsg.Role = TEXT("system");
	SystemMsg.Content = TEXT("You are an AI assistant integrated into Unreal Engine. Help developers with their questions about Unreal Engine, game development, and project-specific queries. Be concise and practical.");
	Messages.Add(SystemMsg);
	
	// User query
	FChatMessage UserMsg;
	UserMsg.Role = TEXT("user");
	UserMsg.Content = Query;
	Messages.Add(UserMsg);
	
	// Send request with callbacks
	FOnStreamChunk OnStreamChunk;
	OnStreamChunk.BindLambda([this](const FString& Chunk) {
		// For now, we'll collect chunks and display them all at once
		// In the future, we could implement progressive display
	});
	
	FOnLLMComplete OnComplete;
	OnComplete.BindLambda([this, Query](bool bSuccess, const FString& Content, const TArray<FToolCall>& ToolCalls) {
		bIsProcessing = false;
		
		if (bSuccess)
		{
			FString FormattedResponse = FString::Printf(
				TEXT("═══════════════════════════════════════════\n")
				TEXT("🤖 AI Response\n")
				TEXT("═══════════════════════════════════════════\n\n")
				TEXT("%s\n\n")
				TEXT("═══════════════════════════════════════════\n")
				TEXT("Query: %s\n")
				TEXT("═══════════════════════════════════════════"),
				*Content,
				*Query
			);
			UpdateResults(FormattedResponse);
		}
		else
		{
			FString ErrorResponse = FString::Printf(
				TEXT("❌ Error\n\n%s\n\n")
				TEXT("Please check:\n")
				TEXT("• Your API key is valid\n")
				TEXT("• You have an internet connection\n")
				TEXT("• The selected provider is available"),
				*Content
			);
			UpdateResults(ErrorResponse);
		}
	});
	
	// Send the request
	LLMClient->SendChatRequest(Messages, TArray<FToolDefinition>(), OnStreamChunk, OnComplete);
	
	UE_LOG(LogAdastreaDirectorEditor, Log, TEXT("Sending query to LLM: %s"), *Query);
}


void SAdastreaDirectorPanel::UpdateResults(const FString& Results)
{
	CurrentResults = FText::FromString(Results);
}

bool SAdastreaDirectorPanel::CanSendQuery() const
{
	return !bIsProcessing && !CurrentQuery.IsEmpty();
}

bool SAdastreaDirectorPanel::IsSendButtonEnabled() const
{
	return CanSendQuery();
}

FReply SAdastreaDirectorPanel::OnClearHistoryClicked()
{
	// Clear the results display
	CurrentResults = LOCTEXT("WelcomeMessage", "Welcome to Adastrea Director!\n\nEnter a query above and click 'Send Query' or press Enter to get started.\n\nExample: \"What is Unreal Engine?\"");
	return FReply::Handled();
}

FReply SAdastreaDirectorPanel::OnSettingsClicked()
{
	SSettingsDialog::OpenDialog();
	return FReply::Handled();
}




















FReply SAdastreaDirectorPanel::OnRefreshDashboardClicked()
{
	UpdateDashboardLogs();
	UpdateConnectionStatus();
	UpdateStatusLights();
	LastDashboardRefreshTime = RefreshTimerReset; // Reset timer to prevent immediate auto-refresh
	return FReply::Handled();
}

FReply SAdastreaDirectorPanel::OnClearLogsClicked()
{
	CurrentLogContent = TEXT("Logs cleared.\n");
	CachedLogContentText = FText::FromString(CurrentLogContent);
	return FReply::Handled();
}

void SAdastreaDirectorPanel::AppendLogEntry(const FString& Entry)
{
	// Prepend new entry to existing logs (newest first)
	CurrentLogContent = Entry + CurrentLogContent;
	
	// Keep only last MaxLogCharacters characters to prevent unbounded growth
	if (CurrentLogContent.Len() > MaxLogCharacters)
	{
		CurrentLogContent = CurrentLogContent.Left(MaxLogCharacters);
	}
	
	// Update cached FText version
	CachedLogContentText = FText::FromString(CurrentLogContent);
}



void SAdastreaDirectorPanel::UpdateConnectionStatus()
{
	// Build status message based on VibeUE component states
	FString StatusMessage;
	
	FAdastreaSettings& Settings = FAdastreaSettings::Get();
	FString ErrorMessage;
	bool bSettingsValid = Settings.ValidateSettings(ErrorMessage);
	
	if (bSettingsValid)
	{
		StatusMessage = FString::Printf(
			TEXT("✅ VibeUE Architecture Ready\n")
			TEXT("• LLM Provider: %s\n")
			TEXT("• Python: %s\n")
			TEXT("• Asset Registry: %s"),
			*Settings.GetLLMProvider(),
			FAdastreaScriptService::IsPythonAvailable() ? TEXT("Available") : TEXT("Not Available"),
			FAdastreaAssetService::IsAssetRegistryReady() ? TEXT("Ready") : TEXT("Loading...")
		);
	}
	else
	{
		StatusMessage = FString::Printf(
			TEXT("⚠️ Configuration Required\n")
			TEXT("• %s\n\n")
			TEXT("Please configure your API key in Settings."),
			*ErrorMessage
		);
	}
	
	CachedConnectionStatus = FText::FromString(StatusMessage);
}

void SAdastreaDirectorPanel::UpdateDashboardLogs()
{
	FString NewLogEntry = FString::Printf(
		TEXT("=== Dashboard Status Update ===\n")
		TEXT("Timestamp: %s\n")
		TEXT("Architecture: VibeUE (Native C++)\n")
		TEXT("LLM Provider: %s\n")
		TEXT("Python Service: %s\n")
		TEXT("Asset Service: %s\n")
		TEXT("===============================\n\n"),
		*FDateTime::Now().ToString(TEXT("%Y-%m-%d %H:%M:%S")),
		*FAdastreaSettings::Get().GetLLMProvider(),
		FAdastreaScriptService::IsPythonAvailable() ? TEXT("Available") : TEXT("Not Available"),
		FAdastreaAssetService::IsAssetRegistryReady() ? TEXT("Ready") : TEXT("Loading...")
	);
	
	AppendLogEntry(NewLogEntry);
}

void SAdastreaDirectorPanel::UpdateStatusLights()
{
	FAdastreaDirectorModule* RuntimeModule = FModuleManager::GetModulePtr<FAdastreaDirectorModule>("AdastreaDirector");
	
	if (!RuntimeModule)
	{
		// Runtime module not available - all systems down
		if (APIKeyStatusLight.IsValid())
			APIKeyStatusLight->SetStatus(SStatusIndicator::EStatus::Error, LOCTEXT("RuntimeModuleNotAvailable", "Runtime module not available"));
		if (LLMClientStatusLight.IsValid())
			LLMClientStatusLight->SetStatus(SStatusIndicator::EStatus::Error, LOCTEXT("RuntimeModuleNotAvailable", "Runtime module not available"));
		if (ScriptServiceStatusLight.IsValid())
			ScriptServiceStatusLight->SetStatus(SStatusIndicator::EStatus::Error, LOCTEXT("RuntimeModuleNotAvailable", "Runtime module not available"));
		if (AssetServiceStatusLight.IsValid())
			AssetServiceStatusLight->SetStatus(SStatusIndicator::EStatus::Error, LOCTEXT("RuntimeModuleNotAvailable", "Runtime module not available"));
		return;
	}

	// Check API key configuration
	if (APIKeyStatusLight.IsValid())
	{
		FStartupValidationResult SettingsResult = FAdastreaStartupValidator::ValidateSettings();
		if (SettingsResult.bSuccess)
		{
			FAdastreaSettings& Settings = FAdastreaSettings::Get();
			FString Provider = Settings.GetLLMProvider();
			
			APIKeyStatusLight->SetStatus(
				SStatusIndicator::EStatus::Good,
				FText::Format(LOCTEXT("APIKeyConfigured", "{0} configured"), FText::FromString(Provider))
			);
		}
		else
		{
			FString ErrorMsg = SettingsResult.ErrorMessage;
			if (ErrorMsg.Len() > 40)
			{
				ErrorMsg = ErrorMsg.Left(37) + TEXT("...");
			}
			APIKeyStatusLight->SetStatus(
				SStatusIndicator::EStatus::Error,
				FText::FromString(ErrorMsg)
			);
		}
	}

	// Check LLM Client
	if (LLMClientStatusLight.IsValid())
	{
		FAdastreaSettings& Settings = FAdastreaSettings::Get();
		FString ErrorMessage;
		if (Settings.ValidateSettings(ErrorMessage))
		{
			LLMClientStatusLight->SetStatus(
				SStatusIndicator::EStatus::Good,
				LOCTEXT("LLMClientReady", "Ready for queries")
			);
		}
		else
		{
			LLMClientStatusLight->SetStatus(
				SStatusIndicator::EStatus::Error,
				LOCTEXT("LLMClientNotConfigured", "Not configured")
			);
		}
	}

	// Check Python Script Service
	if (ScriptServiceStatusLight.IsValid())
	{
		if (FAdastreaScriptService::IsPythonAvailable())
		{
			FString PythonInfo = FAdastreaScriptService::GetPythonInfo();
			ScriptServiceStatusLight->SetStatus(
				SStatusIndicator::EStatus::Good,
				FText::FromString(PythonInfo)
			);
		}
		else
		{
			ScriptServiceStatusLight->SetStatus(
				SStatusIndicator::EStatus::Error,
				LOCTEXT("PythonNotAvailable", "Python plugin not available")
			);
		}
	}

	// Check Asset Service
	if (AssetServiceStatusLight.IsValid())
	{
		if (FAdastreaAssetService::IsAssetRegistryReady())
		{
			AssetServiceStatusLight->SetStatus(
				SStatusIndicator::EStatus::Good,
				LOCTEXT("AssetServiceReady", "Asset registry ready")
			);
		}
		else
		{
			AssetServiceStatusLight->SetStatus(
				SStatusIndicator::EStatus::Warning,
				LOCTEXT("AssetServiceLoading", "Loading assets...")
			);
		}
	}
}


void SAdastreaDirectorPanel::Tick(const FGeometry& AllottedGeometry, const double InCurrentTime, const float InDeltaTime)
{
	SCompoundWidget::Tick(AllottedGeometry, InCurrentTime, InDeltaTime);

	// Update dashboard if on dashboard tab (throttled intervals)
	if (CurrentTabIndex == 1) // Dashboard is now index 1
	{
		const double TimeSinceLastRefresh = InCurrentTime - LastDashboardRefreshTime;
		if (TimeSinceLastRefresh >= DashboardRefreshInterval)
		{
			UpdateDashboardLogs();
			UpdateConnectionStatus();
			LastDashboardRefreshTime = InCurrentTime;
		}
		
		// Update connection status more frequently
		const double TimeSinceLastStatusUpdate = InCurrentTime - LastConnectionStatusUpdateTime;
		if (TimeSinceLastStatusUpdate >= ConnectionStatusUpdateInterval)
		{
			UpdateConnectionStatus();
			LastConnectionStatusUpdateTime = InCurrentTime;
		}

		// Update status lights
		const double TimeSinceLastLightsUpdate = InCurrentTime - LastStatusLightsUpdateTime;
		if (TimeSinceLastLightsUpdate >= StatusLightsUpdateInterval)
		{
			UpdateStatusLights();
			LastStatusLightsUpdateTime = InCurrentTime;
		}
	}
}

FReply SAdastreaDirectorPanel::OnKeyDown(const FGeometry& MyGeometry, const FKeyEvent& InKeyEvent)
{
	// Handle Ctrl+, (Ctrl+Comma) for Settings
	if (InKeyEvent.GetKey() == EKeys::Comma && InKeyEvent.IsControlDown())
	{
		SSettingsDialog::OpenDialog();
		return FReply::Handled();
	}

	return SCompoundWidget::OnKeyDown(MyGeometry, InKeyEvent);
}

FReply SAdastreaDirectorPanel::OnTabButtonClicked(int32 TabIndex)
{
	if (TabIndex >= 0 && TabIndex <= 2) // Only 3 tabs now: Query(0), Dashboard(1), Tests(2)
	{
		CurrentTabIndex = TabIndex;
		
		// If switching to dashboard, refresh it immediately
		if (TabIndex == 1) // Dashboard is now index 1
		{
			UpdateDashboardLogs();
			UpdateConnectionStatus();
			UpdateStatusLights();
			LastDashboardRefreshTime = RefreshTimerReset; // Reset timer to prevent immediate auto-refresh
		}
		// If switching to tests tab, update test output
		else if (TabIndex == 2) // Tests is now index 2
		{
			UpdateTestOutput();
		}
	}
	return FReply::Handled();
}

ECheckBoxState SAdastreaDirectorPanel::GetTabButtonCheckedState(int32 TabIndex) const
{
	return (CurrentTabIndex == TabIndex) ? ECheckBoxState::Checked : ECheckBoxState::Unchecked;
}

TSharedRef<SWidget> SAdastreaDirectorPanel::CreateTestsTab()
{
	return SNew(SVerticalBox)
		
		// Tests Section Header
		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 10.0f, 10.0f, 5.0f)
		[
			SNew(STextBlock)
			.Text(LOCTEXT("TestsLabel", "🧪 Plugin Self-Test Suite:"))
			.Font(FCoreStyle::GetDefaultFontStyle("Bold", 12))
		]

		// Test Buttons Row 1
		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 5.0f, 10.0f, 5.0f)
		[
			SNew(SHorizontalBox)
			
			+ SHorizontalBox::Slot()
			.AutoWidth()
			.Padding(0.0f, 0.0f, 5.0f, 0.0f)
			[
				SNew(SButton)
				.Text(LOCTEXT("SelfCheckButton", "🔍 Self-Check"))
				.ToolTipText(LOCTEXT("SelfCheckTooltip", "Run quick self-check of all plugin components"))
				.OnClicked(this, &SAdastreaDirectorPanel::OnRunSelfCheckClicked)
				.IsEnabled_Lambda([this]() { return CanRunTests(); })
			]

			+ SHorizontalBox::Slot()
			.AutoWidth()
			.Padding(0.0f, 0.0f, 5.0f, 0.0f)
			[
				SNew(SButton)
				.Text(LOCTEXT("IPCTestsButton", "📡 IPC Tests"))
				.ToolTipText(LOCTEXT("IPCTestsTooltip", "Test IPC connection and communication"))
				.OnClicked(this, &SAdastreaDirectorPanel::OnRunIPCTestsClicked)
				.IsEnabled_Lambda([this]() { return CanRunTests(); })
			]

			+ SHorizontalBox::Slot()
			.AutoWidth()
			.Padding(0.0f, 0.0f, 5.0f, 0.0f)
			[
				SNew(SButton)
				.Text(LOCTEXT("PluginTestsButton", "🔌 Plugin Tests"))
				.ToolTipText(LOCTEXT("PluginTestsTooltip", "Run plugin-specific unit tests"))
				.OnClicked(this, &SAdastreaDirectorPanel::OnRunPluginTestsClicked)
				.IsEnabled_Lambda([this]() { return CanRunTests(); })
			]

			+ SHorizontalBox::Slot()
			.AutoWidth()
			.Padding(0.0f, 0.0f, 5.0f, 0.0f)
			[
				SNew(SButton)
				.Text(LOCTEXT("AllTestsButton", "🚀 All Tests"))
				.ToolTipText(LOCTEXT("AllTestsTooltip", "Run all available tests via Python backend"))
				.OnClicked(this, &SAdastreaDirectorPanel::OnRunAllTestsClicked)
				.IsEnabled_Lambda([this]() { return CanRunTests(); })
			]

			+ SHorizontalBox::Slot()
			.AutoWidth()
			.Padding(0.0f, 0.0f, 5.0f, 0.0f)
			[
				SNew(SButton)
				.Text(LOCTEXT("ClearTestOutputButton", "🗑️ Clear"))
				.ToolTipText(LOCTEXT("ClearTestOutputTooltip", "Clear test output display"))
				.OnClicked(this, &SAdastreaDirectorPanel::OnClearTestOutputClicked)
			]

			+ SHorizontalBox::Slot()
			.AutoWidth()
			[
				SNew(SButton)
				.Text(LOCTEXT("SaveLogButton", "💾 Save Log"))
				.ToolTipText(LOCTEXT("SaveLogTooltip", "Save test output to a log file"))
				.OnClicked(this, &SAdastreaDirectorPanel::OnSaveTestLogClicked)
			]
		]

		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 5.0f, 10.0f, 5.0f)
		[
			SNew(SSeparator)
			.Orientation(Orient_Horizontal)
		]

		// Test Status
		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 5.0f, 10.0f, 5.0f)
		[
			SAssignNew(TestStatusText, STextBlock)
			.Text_Lambda([this]() { return TestStatusMessage; })
			.Font(FCoreStyle::GetDefaultFontStyle("Bold", 10))
		]

		// Test Progress Bar
		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 0.0f, 10.0f, 5.0f)
		[
			SAssignNew(TestProgressBar, SProgressBar)
			.Percent_Lambda([this]() { return TestProgress; })
		]

		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 5.0f, 10.0f, 5.0f)
		[
			SNew(STextBlock)
			.Text(LOCTEXT("TestOutputLabel", "Test Output:"))
			.Font(FCoreStyle::GetDefaultFontStyle("Bold", 10))
		]

		// Test Output Display
		+ SVerticalBox::Slot()
		.FillHeight(1.0f)
		.Padding(10.0f, 0.0f, 10.0f, 10.0f)
		[
			SNew(SBox)
			.MinDesiredHeight(300.0f)
			[
				SNew(SScrollBox)
				.Orientation(Orient_Vertical)
				
				+ SScrollBox::Slot()
				[
					SAssignNew(TestOutputDisplay, SMultiLineEditableTextBox)
					.Text_Lambda([this]() { return CachedTestOutputText; })
					.IsReadOnly(true)
					.AutoWrapText(true)
				]
			]
		];
}

FReply SAdastreaDirectorPanel::OnRunSelfCheckClicked()
{
	if (!CanRunTests())
	{
		return FReply::Handled();
	}

	bIsTestRunning = true;
	TestProgress = 0.0f;
	TestStatusMessage = LOCTEXT("SelfCheckRunning", "Running self-check...");
	CurrentTestOutput = TEXT("");
	CachedTestOutputText = FText::FromString(CurrentTestOutput);

	// Perform self-check
	PerformSelfCheck();

	return FReply::Handled();
}

FReply SAdastreaDirectorPanel::OnRunIPCTestsClicked()
{
	RunTests(TEXT("ipc"));
	return FReply::Handled();
}

FReply SAdastreaDirectorPanel::OnRunPluginTestsClicked()
{
	RunTests(TEXT("plugin"));
	return FReply::Handled();
}

FReply SAdastreaDirectorPanel::OnRunAllTestsClicked()
{
	RunTests(TEXT("all"));
	return FReply::Handled();
}

FReply SAdastreaDirectorPanel::OnClearTestOutputClicked()
{
	CurrentTestOutput = TEXT("🧪 Test output cleared.\n\nClick a test button to run tests.\n");
	CachedTestOutputText = FText::FromString(CurrentTestOutput);
	TestProgress = 0.0f;
	TestStatusMessage = LOCTEXT("TestsIdle", "Ready to run tests");
	return FReply::Handled();
}

void SAdastreaDirectorPanel::RunTests(const FString& TestType)
{
	if (!CanRunTests())
	{
		return;
	}

	bIsTestRunning = true;
	TestProgress = 0.0f;
	CurrentTestOutput = TEXT("");
	CachedTestOutputText = FText::FromString(CurrentTestOutput);

	// Get the Python bridge
	FAdastreaDirectorModule* RuntimeModule = FModuleManager::GetModulePtr<FAdastreaDirectorModule>("AdastreaDirector");
	
	if (!RuntimeModule)
	{
		AppendTestOutput(TEXT("❌ Error: Runtime module not available\n"));
		bIsTestRunning = false;
		TestStatusMessage = LOCTEXT("TestsFailed", "Tests failed - module not available");
		return;
	}

	// Legacy IPC tests are no longer available
	AppendTestOutput(TEXT("❌ Error: Legacy IPC test system has been removed\n"));
	AppendTestOutput(TEXT("The plugin has migrated to VibeUE architecture which does not use IPC.\n"));
	AppendTestOutput(TEXT("See MIGRATION_GUIDE.md for information about the new architecture.\n"));
	bIsTestRunning = false;
	TestStatusMessage = LOCTEXT("TestsNotAvailable", "Legacy tests not available");
	return;
}


void SAdastreaDirectorPanel::PerformSelfCheck()
{
	FString Timestamp = FDateTime::Now().ToString(TEXT("%Y-%m-%d %H:%M:%S"));
	FString PluginVersion = GetPluginVersion();
	AppendTestOutput(FString::Printf(TEXT("═══════════════════════════════════════════════════════════════\n")));
	AppendTestOutput(FString::Printf(TEXT("🔍 ADASTREA DIRECTOR SELF-CHECK\n")));
	AppendTestOutput(FString::Printf(TEXT("Timestamp: %s\n"), *Timestamp));
	AppendTestOutput(FString::Printf(TEXT("Plugin Version: %s (UE5.6+)\n"), *PluginVersion));
	AppendTestOutput(FString::Printf(TEXT("═══════════════════════════════════════════════════════════════\n\n")));

	int32 PassCount = 0;
	int32 FailCount = 0;
	int32 SkippedCount = 0;
	int32 WarningCount = 0;
	int32 TotalChecks = 8; // Increased to include new checks
	int32 CurrentCheck = 0;

	// Check 1: Runtime Module
	CurrentCheck++;
	TestProgress = static_cast<float>(CurrentCheck) / TotalChecks;
	FAdastreaDirectorModule* RuntimeModule = FModuleManager::GetModulePtr<FAdastreaDirectorModule>("AdastreaDirector");
	if (RuntimeModule)
	{
		AppendTestOutput(TEXT("✅ [1/8] Runtime Module: Loaded successfully\n"));
		PassCount++;
		
		// Check if fully initialized
		if (RuntimeModule->IsFullyInitialized())
		{
			AppendTestOutput(TEXT("    → Startup validation passed\n"));
		}
		else
		{
			FString InitError = RuntimeModule->GetInitializationError();
			AppendTestOutput(FString::Printf(TEXT("    ⚠️ Initialization incomplete: %s\n"), *InitError));
			WarningCount++;
		}
	}
	else
	{
		AppendTestOutput(TEXT("❌ [1/8] Runtime Module: NOT LOADED\n"));
		FailCount++;
		// Cannot continue without runtime module
		TestStatusMessage = LOCTEXT("SelfCheckFailed", "Self-check failed - runtime module not loaded");
		bIsTestRunning = false;
		return;
	}

	// Check 2: Settings Configuration
	CurrentCheck++;
	TestProgress = static_cast<float>(CurrentCheck) / TotalChecks;
	{
		FAdastreaSettings& Settings = FAdastreaSettings::Get();
		FString ErrorMessage;
		if (Settings.ValidateSettings(ErrorMessage))
		{
			AppendTestOutput(TEXT("✅ [2/8] Settings Configuration: Valid\n"));
			AppendTestOutput(FString::Printf(TEXT("    → LLM Provider: %s\n"), *Settings.GetLLMProvider()));
			AppendTestOutput(FString::Printf(TEXT("    → Embedding Provider: %s\n"), *Settings.GetEmbeddingProvider()));
			AppendTestOutput(FString::Printf(TEXT("    → API Key: %s\n"), Settings.HasAPIKey() ? TEXT("Configured") : TEXT("Not configured")));
			PassCount++;
		}
		else
		{
			AppendTestOutput(TEXT("❌ [2/8] Settings Configuration: INVALID\n"));
			AppendTestOutput(FString::Printf(TEXT("    → Error: %s\n"), *ErrorMessage));
			FailCount++;
		}
	}

	// Check 3: Python Bridge (Legacy - No longer used)
	CurrentCheck++;
	TestProgress = static_cast<float>(CurrentCheck) / TotalChecks;
	AppendTestOutput(TEXT("ℹ️  [3/8] Python Bridge: N/A (Removed in Phase 3)\n"));
	SkippedCount++;

	// Check 4: Python Process (Legacy - No longer used)
	CurrentCheck++;
	TestProgress = static_cast<float>(CurrentCheck) / TotalChecks;
	AppendTestOutput(TEXT("ℹ️  [4/8] Python Process: N/A (VibeUE uses native C++)\n"));
	SkippedCount++;

	// Check 5: IPC Connection (Legacy - No longer used)
	CurrentCheck++;
	TestProgress = static_cast<float>(CurrentCheck) / TotalChecks;
	AppendTestOutput(TEXT("ℹ️  [5/8] IPC Connection: N/A (VibeUE architecture)\n"));
	SkippedCount++;
	// Removed legacy code - previously checked FPythonBridge initialization and status

	// Check 6: Backend Health (Legacy - No longer used)
	CurrentCheck++;
	TestProgress = static_cast<float>(CurrentCheck) / TotalChecks;
	AppendTestOutput(TEXT("ℹ️  [6/8] Backend Health: N/A (VibeUE native)\n"));
	SkippedCount++;

	// Check 7: API Key Configuration (VibeUE Phase 3 - settings only, no backend validation)
	CurrentCheck++;
	TestProgress = static_cast<float>(CurrentCheck) / TotalChecks;
	{
		FStartupValidationResult SettingsResult = FAdastreaStartupValidator::ValidateSettings();
		if (SettingsResult.bSuccess)
		{
			FAdastreaSettings& Settings = FAdastreaSettings::Get();
			FString Provider = Settings.GetLLMProvider();
			AppendTestOutput(TEXT("✅ [7/8] API Key Configuration: CONFIGURED\n"));
			AppendTestOutput(FString::Printf(TEXT("    → LLM Provider: %s\n"), *Provider));
			PassCount++;
		}
		else
		{
			AppendTestOutput(TEXT("❌ [7/8] API Key Configuration: NOT CONFIGURED\n"));
			AppendTestOutput(FString::Printf(TEXT("    → %s\n"), *SettingsResult.ErrorMessage));
			FailCount++;
		}
	}

	// Check 8: Query Processing (Legacy - No longer used)
	CurrentCheck++;
	TestProgress = static_cast<float>(CurrentCheck) / TotalChecks;
	AppendTestOutput(TEXT("ℹ️  [8/8] Query Processing: N/A (use VibeUE components)\n"));
	SkippedCount++;

	// Summary
	AppendTestOutput(TEXT("\n═══════════════════════════════════════════════════════════════\n"));
	AppendTestOutput(TEXT("SELF-CHECK SUMMARY\n"));
	AppendTestOutput(TEXT("───────────────────────────────────────────────────────────────\n"));
	AppendTestOutput(FString::Printf(TEXT("✅ Passed:  %d/%d\n"), PassCount, TotalChecks));
	AppendTestOutput(FString::Printf(TEXT("❌ Failed:  %d/%d\n"), FailCount, TotalChecks));
	if (SkippedCount > 0)
	{
		AppendTestOutput(FString::Printf(TEXT("⚠️  Skipped: %d/%d\n"), SkippedCount, TotalChecks));
	}
	if (WarningCount > 0)
	{
		AppendTestOutput(FString::Printf(TEXT("⚠️  Warnings: %d\n"), WarningCount));
	}
	AppendTestOutput(TEXT("───────────────────────────────────────────────────────────────\n"));
	
	// Determine overall status
	if (FailCount == 0 && SkippedCount == 0 && WarningCount == 0)
	{
		AppendTestOutput(TEXT("\n✅ ALL CHECKS PASSED\n"));
		AppendTestOutput(TEXT("Plugin is fully functional and ready for production use.\n"));
		TestStatusMessage = LOCTEXT("SelfCheckPassed", "✅ All self-checks passed!");
	}
	else if (FailCount == 0 && WarningCount > 0 && SkippedCount == 0)
	{
		AppendTestOutput(TEXT("\n⚠️  CHECKS PASSED WITH WARNINGS\n"));
		AppendTestOutput(TEXT("All checks passed but some warnings were raised.\n"));
		AppendTestOutput(TEXT("Plugin is functional but review warnings above.\n"));
		TestStatusMessage = FText::Format(LOCTEXT("SelfCheckWarnings", "⚠️ {0} passed, {1} warnings"), FText::AsNumber(PassCount), FText::AsNumber(WarningCount));
	}
	else if (FailCount == 0 && SkippedCount > 0 && WarningCount == 0)
	{
		AppendTestOutput(TEXT("\n⚠️  CHECKS INCOMPLETE\n"));
		AppendTestOutput(TEXT("Some checks were skipped due to missing dependencies.\n"));
		AppendTestOutput(TEXT("Plugin may have limited functionality.\n"));
		TestStatusMessage = FText::Format(LOCTEXT("SelfCheckSkipped", "⚠️ {0} passed, {1} skipped"), FText::AsNumber(PassCount), FText::AsNumber(SkippedCount));
	}
	else if (FailCount == 0 && SkippedCount > 0 && WarningCount > 0)
	{
		AppendTestOutput(TEXT("\n⚠️  CHECKS INCOMPLETE WITH WARNINGS\n"));
		AppendTestOutput(TEXT("Some checks were skipped and warnings were raised.\n"));
		AppendTestOutput(TEXT("Plugin may have limited functionality.\n"));
		TestStatusMessage = FText::Format(LOCTEXT("SelfCheckSkippedWarnings", "⚠️ {0} passed, {1} skipped, {2} warnings"), 
			FText::AsNumber(PassCount), FText::AsNumber(SkippedCount), FText::AsNumber(WarningCount));
	}
	else if (FailCount > 0)
	{
		AppendTestOutput(TEXT("\n❌ CHECKS FAILED\n"));
		AppendTestOutput(TEXT("Critical issues detected. Please review failures above.\n"));
		if (FailCount > 3)
		{
			AppendTestOutput(TEXT("\nRecommended Actions:\n"));
			AppendTestOutput(TEXT("1. Check Python installation and dependencies\n"));
			AppendTestOutput(TEXT("2. Verify API key configuration in .env file\n"));
			AppendTestOutput(TEXT("3. Review Output Log for detailed error messages\n"));
			AppendTestOutput(TEXT("4. Restart Unreal Engine if issues persist\n"));
		}
		TestStatusMessage = FText::Format(LOCTEXT("SelfCheckPartialFail", "❌ {0}/{1} checks failed"), FText::AsNumber(FailCount), FText::AsNumber(TotalChecks));
	}
	AppendTestOutput(TEXT("═══════════════════════════════════════════════════════════════\n"));

	TestProgress = 1.0f;
	bIsTestRunning = false;
}

void SAdastreaDirectorPanel::UpdateTestOutput()
{
	// Update cached test output text
	CachedTestOutputText = FText::FromString(CurrentTestOutput);
}

void SAdastreaDirectorPanel::AppendTestOutput(const FString& Entry)
{
	CurrentTestOutput += Entry;
	
	// Keep only last MaxTestOutputCharacters characters, preserving line boundaries
	if (CurrentTestOutput.Len() > MaxTestOutputCharacters)
	{
		// Find a newline near the truncation point to avoid cutting mid-line
		int32 TruncateIndex = CurrentTestOutput.Len() - MaxTestOutputCharacters;
		
		// Search for a newline within the next 100 characters after TruncateIndex
		int32 WindowLength = FMath::Min(100, CurrentTestOutput.Len() - TruncateIndex);
		int32 RelativeNewlineIndex = CurrentTestOutput.Mid(TruncateIndex, WindowLength).Find(TEXT("\n"));
		
		if (RelativeNewlineIndex != INDEX_NONE)
		{
			// Found a newline close to truncation point
			CurrentTestOutput = TEXT("[...truncated...]\n") + CurrentTestOutput.Mid(TruncateIndex + RelativeNewlineIndex + 1);
		}
		else
		{
			// No suitable newline found, just truncate with indicator
			CurrentTestOutput = TEXT("[...truncated...]\n") + CurrentTestOutput.Right(MaxTestOutputCharacters);
		}
	}
	
	// Update cached FText version
	CachedTestOutputText = FText::FromString(CurrentTestOutput);
}

bool SAdastreaDirectorPanel::CanRunTests() const
{
	return !bIsTestRunning;
}

FReply SAdastreaDirectorPanel::OnSaveTestLogClicked()
{
	// Create timestamp for filename
	FString Timestamp = FDateTime::Now().ToString(TEXT("%Y%m%d_%H%M%S"));
	FString DefaultFilename = FString::Printf(TEXT("adastrea_test_log_%s.txt"), *Timestamp);
	
	// Open save file dialog
	IDesktopPlatform* DesktopPlatform = FDesktopPlatformModule::Get();
	if (!DesktopPlatform)
	{
		AppendTestOutput(TEXT("\n❌ Failed to open save dialog - desktop platform not available.\n"));
		return FReply::Handled();
	}
	
	TArray<FString> OutFiles;
	const void* ParentWindowHandle = FSlateApplication::Get().FindBestParentWindowHandleForDialogs(nullptr);
	
	bool bOpened = DesktopPlatform->SaveFileDialog(
		ParentWindowHandle,
		TEXT("Save Test Log"),
		FPaths::ProjectLogDir(),
		DefaultFilename,
		TEXT("Text Files (*.txt)|*.txt|Log Files (*.log)|*.log|All Files (*.*)|*.*"),
		EFileDialogFlags::None,
		OutFiles
	);
	
	if (bOpened && OutFiles.Num() > 0)
	{
		if (SaveTestLogToFile(OutFiles[0]))
		{
			AppendTestOutput(FString::Printf(TEXT("\n✅ Log saved to: %s\n"), *OutFiles[0]));
		}
		else
		{
			AppendTestOutput(TEXT("\n❌ Failed to save log file.\n"));
		}
	}
	
	return FReply::Handled();
}

bool SAdastreaDirectorPanel::SaveTestLogToFile(const FString& FilePath)
{
	// Add header with metadata
	FString LogContent;
	LogContent += TEXT("═══════════════════════════════════════════════════════════════\n");
	LogContent += TEXT("ADASTREA DIRECTOR TEST LOG\n");
	LogContent += FString::Printf(TEXT("Generated: %s\n"), *FDateTime::Now().ToString(TEXT("%Y-%m-%d %H:%M:%S")));
	LogContent += FString::Printf(TEXT("Project: %s\n"), *FPaths::GetProjectFilePath());
	LogContent += TEXT("═══════════════════════════════════════════════════════════════\n\n");
	
	// Add the test output content
	LogContent += CurrentTestOutput;
	
	// Write to file
	return FFileHelper::SaveStringToFile(LogContent, *FilePath, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
}

#undef LOCTEXT_NAMESPACE
