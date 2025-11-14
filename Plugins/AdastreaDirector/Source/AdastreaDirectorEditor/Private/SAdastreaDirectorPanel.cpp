// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#include "SAdastreaDirectorPanel.h"
#include "AdastreaDirectorEditorModule.h"
#include "AdastreaDirectorModule.h"
#include "PythonBridge.h"
#include "Widgets/Input/SEditableTextBox.h"
#include "Widgets/Input/SMultiLineEditableTextBox.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SSeparator.h"
#include "EditorStyleSet.h"
#include "Styling/SlateTypes.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonReader.h"

#define LOCTEXT_NAMESPACE "AdastreaDirectorPanel"

SAdastreaDirectorPanel::~SAdastreaDirectorPanel()
{
}

void SAdastreaDirectorPanel::Construct(const FArguments& InArgs)
{
	bIsProcessing = false;
	CurrentResults = LOCTEXT("WelcomeMessage", "Welcome to Adastrea Director!\n\nEnter a query above and click 'Send Query' or press Enter to get started.\n\nExample: \"What is Unreal Engine?\"");

	ChildSlot
	[
		SNew(SVerticalBox)
		
		// Header
		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 10.0f, 10.0f, 5.0f)
		[
			SNew(STextBlock)
			.Text(LOCTEXT("PanelTitle", "Adastrea Director - AI Assistant"))
			.Font(FCoreStyle::GetDefaultFontStyle("Bold", 16))
		]

		+ SVerticalBox::Slot()
		.AutoHeight()
		.Padding(10.0f, 0.0f, 10.0f, 10.0f)
		[
			SNew(SSeparator)
			.Orientation(Orient_Horizontal)
		]

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
			[
				SNew(SButton)
				.Text(LOCTEXT("SendButton", "Send Query"))
				.ToolTipText(LOCTEXT("SendButtonTooltip", "Send query to Python backend"))
				.OnClicked(this, &SAdastreaDirectorPanel::OnSendQueryClicked)
				.IsEnabled(this, &SAdastreaDirectorPanel::IsSendButtonEnabled)
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
					.Text(this, &SAdastreaDirectorPanel::CurrentResults)
					.IsReadOnly(true)
					.AutoWrapText(true)
				]
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

	// Set processing state
	bIsProcessing = true;
	UpdateResults(TEXT("Processing query..."));

	// Send query to Python backend
	SendQueryToPython(QueryString);

	// Reset processing state
	bIsProcessing = false;

	return FReply::Handled();
}

void SAdastreaDirectorPanel::SendQueryToPython(const FString& Query)
{
	// Get the Python bridge from the runtime module
	FAdastreaDirectorModule* RuntimeModule = FModuleManager::GetModulePtr<FAdastreaDirectorModule>("AdastreaDirector");
	
	if (!RuntimeModule)
	{
		UE_LOG(LogAdastreaDirectorEditor, Error, TEXT("Failed to get AdastreaDirector runtime module"));
		UpdateResults(TEXT("Error: AdastreaDirector runtime module not available."));
		return;
	}

	FPythonBridge* PythonBridge = RuntimeModule->GetPythonBridge();
	
	if (!PythonBridge)
	{
		UE_LOG(LogAdastreaDirectorEditor, Error, TEXT("Python bridge not available"));
		UpdateResults(TEXT("Error: Python backend is not initialized.\n\nPlease ensure the Python backend is running."));
		return;
	}

	if (!PythonBridge->IsReady())
	{
		UE_LOG(LogAdastreaDirectorEditor, Warning, TEXT("Python bridge not ready"));
		UpdateResults(TEXT("Error: Python backend is not ready.\n\nPlease check that the Python backend is running and connected."));
		return;
	}

	// Send query request
	FString Response;
	bool bSuccess = PythonBridge->SendRequest(TEXT("query"), Query, Response);

	if (bSuccess)
	{
		// Parse the JSON response
		TSharedPtr<FJsonObject> JsonObject;
		TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Response);
		
		if (FJsonSerializer::Deserialize(Reader, JsonObject) && JsonObject.IsValid())
		{
			FString Status = JsonObject->GetStringField(TEXT("status"));
			
			if (Status == TEXT("success"))
			{
				FString Result = JsonObject->GetStringField(TEXT("result"));
				UpdateResults(FString::Printf(TEXT("Query: %s\n\nResponse:\n%s"), *Query, *Result));
			}
			else
			{
				FString Error = JsonObject->GetStringField(TEXT("error"));
				UpdateResults(FString::Printf(TEXT("Error: %s"), *Error));
			}
		}
		else
		{
			UE_LOG(LogAdastreaDirectorEditor, Error, TEXT("Failed to parse response JSON: %s"), *Response);
			UpdateResults(FString::Printf(TEXT("Error: Failed to parse response.\n\nRaw response: %s"), *Response));
		}
	}
	else
	{
		UE_LOG(LogAdastreaDirectorEditor, Error, TEXT("Failed to send query to Python backend"));
		UpdateResults(TEXT("Error: Failed to communicate with Python backend.\n\nPlease check the connection and try again."));
	}
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

#undef LOCTEXT_NAMESPACE
