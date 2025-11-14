// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "Widgets/DeclarativeSyntaxSupport.h"

class SMultiLineEditableTextBox;
class SEditableTextBox;

/**
 * Main Slate panel widget for Adastrea Director.
 * Provides UI for querying the Python backend and displaying results.
 */
class SAdastreaDirectorPanel : public SCompoundWidget
{
public:
	SLATE_BEGIN_ARGS(SAdastreaDirectorPanel) {}
	SLATE_END_ARGS()

	/** Constructs this widget with InArgs */
	void Construct(const FArguments& InArgs);

	/** Called when the widget is destroyed */
	virtual ~SAdastreaDirectorPanel();

private:
	/** Query input text box */
	TSharedPtr<SEditableTextBox> QueryInputBox;

	/** Results display text box */
	TSharedPtr<SMultiLineEditableTextBox> ResultsDisplay;

	/** Current query text */
	FText CurrentQuery;

	/** Current results text */
	FText CurrentResults;

	/** Is a query currently being processed */
	bool bIsProcessing;

	/** Called when the Send Query button is clicked */
	FReply OnSendQueryClicked();

	/** Called when query text is changed */
	void OnQueryTextChanged(const FText& NewText);

	/** Called when query text is committed (Enter pressed) */
	void OnQueryTextCommitted(const FText& NewText, ETextCommit::Type CommitType);

	/** Helper to send query to Python backend */
	void SendQueryToPython(const FString& Query);

	/** Helper to update results display */
	void UpdateResults(const FString& Results);

	/** Helper to check if query can be sent */
	bool CanSendQuery() const;

	/** Get the enabled state of the send button */
	bool IsSendButtonEnabled() const;
};
