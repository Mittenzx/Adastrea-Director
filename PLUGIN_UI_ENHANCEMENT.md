# Plugin UI Enhancement Guide

## Overview
This document outlines improvements for the Adastrea Director Unreal Engine plugin UI to match the enhanced Python GUI.

## Current State (SAdastreaDirectorPanel.cpp)
- 4 tabs: Query, Ingestion, Dashboard, Tests
- Basic button layouts
- Simple text displays
- Limited visual feedback
- No agent integration

## Proposed Enhancements

### 1. Enhanced Visual Hierarchy

#### Header Section
```cpp
// Before: Simple text header
SNew(STextBlock)
    .Text(LOCTEXT("PanelTitle", "Adastrea Director - AI Assistant"))
    .Font(FCoreStyle::GetDefaultFontStyle("Bold", 16))

// After: Card-based header with status indicator
SNew(SBorder)
    .BorderImage(FAppStyle::GetBrush("ToolPanel.GroupBorder"))
    .Padding(15.0f)
    [
        SNew(SHorizontalBox)
        
        // Icon
        + SHorizontalBox::Slot()
        .AutoWidth()
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("⚡")))
            .Font(FCoreStyle::GetDefaultFontStyle("Regular", 20))
        ]
        
        // Title and subtitle
        + SHorizontalBox::Slot()
        .FillWidth(1.0f)
        .Padding(10.0f, 0.0f)
        [
            SNew(SVerticalBox)
            + SVerticalBox::Slot()
            .AutoHeight()
            [
                SNew(STextBlock)
                .Text(LOCTEXT("PanelTitle", "Adastrea Director"))
                .Font(FCoreStyle::GetDefaultFontStyle("Bold", 16))
            ]
            + SVerticalBox::Slot()
            .AutoHeight()
            [
                SNew(STextBlock)
                .Text(LOCTEXT("Subtitle", "AI-Powered Game Development Assistant"))
                .Font(FCoreStyle::GetDefaultFontStyle("Regular", 9))
                .ColorAndOpacity(FSlateColor(FLinearColor(0.7f, 0.7f, 0.7f)))
            ]
        ]
        
        // Status badge
        + SHorizontalBox::Slot()
        .AutoWidth()
        [
            CreateStatusBadge()
        ]
    ]
```

### 2. Modern Button Styles

```cpp
// Enhanced button factory method
TSharedRef<SWidget> CreateModernButton(
    const FText& Text,
    FOnClicked OnClicked,
    const FText& Icon = FText::GetEmpty(),
    bool bIsPrimary = false)
{
    FLinearColor ButtonColor = bIsPrimary 
        ? FLinearColor(0.25f, 0.66f, 1.0f)  // Primary blue
        : FLinearColor(0.2f, 0.22f, 0.26f); // Secondary gray
    
    FLinearColor HoverColor = bIsPrimary
        ? FLinearColor(0.36f, 0.72f, 1.0f)  // Lighter blue
        : FLinearColor(0.29f, 0.30f, 0.35f); // Lighter gray
    
    return SNew(SButton)
        .ButtonStyle(FAppStyle::Get(), "FlatButton")
        .ButtonColorAndOpacity(ButtonColor)
        .OnClicked(OnClicked)
        .ContentPadding(FMargin(18.0f, 9.0f))
        .HAlign(HAlign_Center)
        [
            SNew(SHorizontalBox)
            
            // Icon (if provided)
            + SHorizontalBox::Slot()
            .AutoWidth()
            .Padding(0.0f, 0.0f, Icon.IsEmpty() ? 0.0f : 8.0f, 0.0f)
            [
                SNew(STextBlock)
                .Text(Icon)
                .Visibility(Icon.IsEmpty() ? EVisibility::Collapsed : EVisibility::Visible)
                .Font(FCoreStyle::GetDefaultFontStyle("Regular", 10))
            ]
            
            // Text
            + SHorizontalBox::Slot()
            .AutoWidth()
            [
                SNew(STextBlock)
                .Text(Text)
                .Font(FCoreStyle::GetDefaultFontStyle("Bold", 10))
            ]
        ];
}
```

### 3. Collapsible Sections

```cpp
// Factory for collapsible sections
TSharedRef<SWidget> CreateCollapsibleSection(
    const FText& Title,
    TSharedRef<SWidget> Content,
    bool bStartExpanded = true)
{
    return SNew(SBorder)
        .BorderImage(FAppStyle::GetBrush("ToolPanel.GroupBorder"))
        .Padding(0.0f)
        [
            SNew(SVerticalBox)
            
            // Header (clickable)
            + SVerticalBox::Slot()
            .AutoHeight()
            [
                SNew(SButton)
                .ButtonStyle(FAppStyle::Get(), "FlatButton")
                .ContentPadding(FMargin(15.0f, 10.0f))
                .OnClicked_Lambda([this, &bExpanded]() {
                    bExpanded = !bExpanded;
                    // Toggle content visibility
                    return FReply::Handled();
                })
                [
                    SNew(SHorizontalBox)
                    
                    // Expand/collapse icon
                    + SHorizontalBox::Slot()
                    .AutoWidth()
                    .Padding(0.0f, 0.0f, 10.0f, 0.0f)
                    [
                        SNew(STextBlock)
                        .Text_Lambda([&bExpanded]() {
                            return bExpanded ? FText::FromString(TEXT("▼")) : FText::FromString(TEXT("▶"));
                        })
                        .Font(FCoreStyle::GetDefaultFontStyle("Regular", 10))
                        .ColorAndOpacity(FLinearColor(0.25f, 0.66f, 1.0f))
                    ]
                    
                    // Title
                    + SHorizontalBox::Slot()
                    .FillWidth(1.0f)
                    [
                        SNew(STextBlock)
                        .Text(Title)
                        .Font(FCoreStyle::GetDefaultFontStyle("Bold", 11))
                    ]
                ]
            ]
            
            // Content (with visibility control)
            + SVerticalBox::Slot()
            .AutoHeight()
            [
                SNew(SBox)
                .Visibility_Lambda([&bExpanded]() {
                    return bExpanded ? EVisibility::Visible : EVisibility::Collapsed;
                })
                [
                    Content
                ]
            ]
        ];
}
```

### 4. Info Card Widget

```cpp
// Info card for displaying metrics
TSharedRef<SWidget> CreateInfoCard(
    const FText& Title,
    const FText& Value,
    const FText& Icon = FText::GetEmpty())
{
    return SNew(SBorder)
        .BorderImage(FAppStyle::GetBrush("ToolPanel.GroupBorder"))
        .Padding(15.0f, 12.0f)
        [
            SNew(SHorizontalBox)
            
            // Icon
            + SHorizontalBox::Slot()
            .AutoWidth()
            .Padding(0.0f, 0.0f, 15.0f, 0.0f)
            [
                SNew(STextBlock)
                .Text(Icon)
                .Font(FCoreStyle::GetDefaultFontStyle("Regular", 20))
                .Visibility(Icon.IsEmpty() ? EVisibility::Collapsed : EVisibility::Visible)
            ]
            
            // Text container
            + SHorizontalBox::Slot()
            .FillWidth(1.0f)
            [
                SNew(SVerticalBox)
                
                // Title
                + SVerticalBox::Slot()
                .AutoHeight()
                [
                    SNew(STextBlock)
                    .Text(Title)
                    .Font(FCoreStyle::GetDefaultFontStyle("Regular", 9))
                    .ColorAndOpacity(FSlateColor(FLinearColor(0.52f, 0.52f, 0.52f)))
                ]
                
                // Value
                + SVerticalBox::Slot()
                .AutoHeight()
                [
                    SNew(STextBlock)
                    .Text(Value)
                    .Font(FCoreStyle::GetDefaultFontStyle("Bold", 14))
                ]
            ]
        ];
}
```

### 5. Agent Monitoring Panel

```cpp
// Create agent monitoring section for Dashboard tab
TSharedRef<SWidget> CreateAgentMonitoringSection()
{
    return SNew(SVerticalBox)
        
        // Header
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(10.0f, 10.0f, 10.0f, 5.0f)
        [
            SNew(STextBlock)
            .Text(LOCTEXT("AgentsHeader", "🤖 Autonomous Agents"))
            .Font(FCoreStyle::GetDefaultFontStyle("Bold", 12))
        ]
        
        // Agent grid
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(10.0f, 5.0f)
        [
            SNew(SGridPanel)
            .FillColumn(0, 1.0f)
            .FillColumn(1, 1.0f)
            
            // Performance Agent
            + SGridPanel::Slot(0, 0)
            .Padding(5.0f)
            [
                CreateAgentCard(
                    LOCTEXT("PerfAgent", "Performance Profiling"),
                    LOCTEXT("PerfStatus", "Running"),
                    FText::FromString(TEXT("⚡"))
                )
            ]
            
            // Bug Detection Agent
            + SGridPanel::Slot(1, 0)
            .Padding(5.0f)
            [
                CreateAgentCard(
                    LOCTEXT("BugAgent", "Bug Detection"),
                    LOCTEXT("BugStatus", "Idle"),
                    FText::FromString(TEXT("🐛"))
                )
            ]
            
            // Code Quality Agent
            + SGridPanel::Slot(0, 1)
            .Padding(5.0f)
            [
                CreateAgentCard(
                    LOCTEXT("QualityAgent", "Code Quality"),
                    LOCTEXT("QualityStatus", "Running"),
                    FText::FromString(TEXT("✨"))
                )
            ]
        ];
}

TSharedRef<SWidget> CreateAgentCard(
    const FText& Name,
    const FText& Status,
    const FText& Icon)
{
    // Determine status color
    FLinearColor StatusColor = FLinearColor(0.3f, 0.79f, 0.69f); // Green
    if (Status.ToString().Contains(TEXT("Idle")))
    {
        StatusColor = FLinearColor(0.25f, 0.66f, 1.0f); // Blue
    }
    else if (Status.ToString().Contains(TEXT("Error")))
    {
        StatusColor = FLinearColor(0.96f, 0.53f, 0.44f); // Red
    }
    
    return CreateCollapsibleSection(
        FText::Format(LOCTEXT("AgentTitle", "{0} {1}"), Icon, Name),
        SNew(SVerticalBox)
        
        // Status row
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(10.0f, 5.0f)
        [
            SNew(SHorizontalBox)
            
            + SHorizontalBox::Slot()
            .AutoWidth()
            [
                SNew(STextBlock)
                .Text(LOCTEXT("StatusLabel", "Status:"))
                .Font(FCoreStyle::GetDefaultFontStyle("Bold", 9))
                .ColorAndOpacity(FSlateColor(FLinearColor(0.52f, 0.52f, 0.52f)))
            ]
            
            + SHorizontalBox::Slot()
            .AutoWidth()
            .Padding(10.0f, 0.0f)
            [
                SNew(SBorder)
                .BorderImage(FAppStyle::GetBrush("ToolPanel.GroupBorder"))
                .Padding(8.0f, 4.0f)
                .BorderBackgroundColor(StatusColor)
                [
                    SNew(STextBlock)
                    .Text(Status)
                    .Font(FCoreStyle::GetDefaultFontStyle("Bold", 9))
                ]
            ]
        ]
        
        // Metrics would go here
        ,
        true // Start expanded
    );
}
```

## Implementation Plan

### Phase 1: Foundation (Week 1)
1. Create new widget factory methods (CreateModernButton, CreateInfoCard, etc.)
2. Update color scheme constants to match Python GUI
3. Refactor header section with card-based design

### Phase 2: Enhanced Visuals (Week 2)
1. Update all buttons to use new modern style
2. Add icon support throughout
3. Implement collapsible sections
4. Add hover states and animations

### Phase 3: Agent Integration (Week 3)
1. Create agent monitoring section
2. Add status indicators for each agent
3. Display real-time metrics
4. Implement refresh mechanism

### Phase 4: Polish (Week 4)
1. Add tooltips to all interactive elements
2. Implement keyboard shortcuts
3. Add loading states for async operations
4. Create transition animations
5. Final testing and bug fixes

## Testing Checklist

- [ ] All widgets render correctly at different window sizes
- [ ] Button hover states work properly
- [ ] Collapsible sections expand/collapse smoothly
- [ ] Status indicators update in real-time
- [ ] Tooltips display correctly
- [ ] Keyboard shortcuts function as expected
- [ ] No performance degradation
- [ ] Matches Python GUI visual style
- [ ] Accessible via keyboard navigation

## Color Reference

### Primary Colors
```cpp
static const FLinearColor PrimaryBlue = FLinearColor(0.25f, 0.66f, 1.0f);    // #40a9ff
static const FLinearColor DarkBg = FLinearColor(0.13f, 0.14f, 0.17f);        // #20232b
static const FLinearColor SecondaryBg = FLinearColor(0.15f, 0.15f, 0.15f);   // #252526
static const FLinearColor TertiaryBg = FLinearColor(0.18f, 0.18f, 0.19f);    // #2d2d30
static const FLinearColor TextPrimary = FLinearColor(0.89f, 0.89f, 0.91f);   // #e3e4e8
static const FLinearColor TextSecondary = FLinearColor(0.52f, 0.52f, 0.52f); // #858585
static const FLinearColor BorderColor = FLinearColor(0.24f, 0.24f, 0.26f);   // #3e3e42
```

### Status Colors
```cpp
static const FLinearColor SuccessGreen = FLinearColor(0.3f, 0.79f, 0.69f);  // #4ec9b0
static const FLinearColor WarningOrange = FLinearColor(0.81f, 0.57f, 0.47f); // #ce9178
static const FLinearColor ErrorRed = FLinearColor(0.96f, 0.53f, 0.44f);      // #f48771
static const FLinearColor InfoBlue = FLinearColor(0.25f, 0.66f, 1.0f);       // #40a9ff
```

## Notes

- All changes should maintain backward compatibility
- Focus on incremental improvements
- Test each change independently
- Keep performance impact minimal
- Document all new widget types
- Follow UE5 Slate best practices
