# Ingest List Tab - Visual Description

## Overview
This document provides a detailed visual description of the new Ingest List tab in the Adastrea Director GUI.

## Interface Layout

### Tab Bar
Located at the top of the main content area, the tab bar contains two tabs:
- **💬 Conversation** (left tab) - The original conversation interface
- **📋 Ingest List** (right tab) - The new ingestion status tab

**Tab Styling:**
- Background: Dark gray (#343843) for inactive tabs
- Selected tab: Darker gray (#2d2d30) with blue text (#40a9ff)
- Font: Segoe UI, 10pt
- Padding: 20px horizontal, 10px vertical

### Ingest List Tab Content

#### Header Section
```
┌────────────────────────────────────────────────────────────────┐
│ 📋 Document Ingestion Status              [🔄 Refresh]        │
└────────────────────────────────────────────────────────────────┘
```

**Header Components:**
- Title: "📋 Document Ingestion Status" in light gray (#e3e4e8), bold, 11pt
- Refresh Button: 
  - Text: "🔄 Refresh"
  - Style: Dark button background (#343843)
  - On hover: Lighter gray (#4a4e5a)
  - Position: Right-aligned

#### Main Content Area

##### Ingested Documents Section
```
┌────────────────────────────────────────────────────────────────┐
│ ✅ Ingested Documents                                         │
│                                                                │
│ ┌────────────────────────────────────────────────────────┐   │
│ │                                                          │   │
│ │  ✅ README.md                                            │   │
│ │     📍 /home/user/project/README.md                     │   │
│ │     📦 12 chunks                                         │   │
│ │                                                          │   │
│ │  ✅ PROJECT_PLAN.md                                      │   │
│ │     📍 /home/user/project/PROJECT_PLAN.md               │   │
│ │     📦 25 chunks                                         │   │
│ │                                                          │   │
│ │  ✅ AGENTS.md                                            │   │
│ │     📍 /home/user/project/AGENTS.md                     │   │
│ │     📦 18 chunks                                         │   │
│ │                                                          │   │
│ │  ✅ ingest.py                                            │   │
│ │     📍 /home/user/project/ingest.py                     │   │
│ │     📦 8 chunks                                          │   │
│ │                                                          │   │
│ │  ✅ main.py                                              │   │
│ │     📍 /home/user/project/main.py                       │   │
│ │     📦 7 chunks                                          │   │
│ │                                                          │   │
│ └────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

**Document List Styling:**
- Section Header: "✅ Ingested Documents" in success green (#4ec9b0), bold
- Scrollable area with dark background (#2a2d35)
- Each document entry shows:
  - **Filename**: Green checkmark + filename in green (#4ec9b0), bold, Consolas 9pt
  - **Path**: 📍 icon + full path in muted gray (#858585), Consolas 8pt, indented
  - **Chunks**: 📦 icon + chunk count in secondary gray (#cccccc), Consolas 8pt, indented
- Spacing: Empty line between documents

##### Statistics Bar
```
┌────────────────────────────────────────────────────────────────┐
│ 📊 Total: 5 documents • 70 chunks                             │
└────────────────────────────────────────────────────────────────┘
```

**Statistics Styling:**
- Background: Secondary dark (#252526)
- Border: Subtle border (#3e3e42)
- Text: Secondary gray (#cccccc), Segoe UI 9pt
- Padding: 15px horizontal, 10px vertical

## Color Scheme

The Ingest List tab follows the UE5-inspired dark theme:

| Element | Color Code | Usage |
|---------|-----------|--------|
| Background | `#20232b` | Main background |
| Secondary BG | `#252526` | Statistics bar |
| Tertiary BG | `#2d2d30` | Cards and selected tab |
| Text BG | `#2a2d35` | Document list area |
| Text | `#e3e4e8` | Primary text |
| Secondary Text | `#cccccc` | Metadata text |
| Muted Text | `#858585` | Paths and dim text |
| Accent | `#40a9ff` | Selected tab text |
| Success | `#4ec9b0` | Checkmarks and filenames |
| Border | `#3e3e42` | Borders and dividers |
| Button BG | `#343843` | Button background |
| Button Hover | `#4a4e5a` | Button on hover |

## States and Messages

### Empty Database State
```
┌────────────────────────────────────────────────────────────────┐
│ ✅ Ingested Documents                                         │
│                                                                │
│ ┌────────────────────────────────────────────────────────┐   │
│ │                                                          │   │
│ │  ℹ️ Database is empty                                   │   │
│ │                                                          │   │
│ │  Vector database is empty. Please ingest documents.     │   │
│ │                                                          │   │
│ └────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ 0 documents • 0 chunks                                         │
└────────────────────────────────────────────────────────────────┘
```

**Empty State Styling:**
- Info icon + header in accent blue (#40a9ff), bold
- Message in secondary gray (#cccccc)

### No Database State
```
┌────────────────────────────────────────────────────────────────┐
│ ✅ Ingested Documents                                         │
│                                                                │
│ ┌────────────────────────────────────────────────────────┐   │
│ │                                                          │   │
│ │  ⚠️ No vector database found                            │   │
│ │                                                          │   │
│ │  No vector database found. Please ingest documents      │   │
│ │  first.                                                  │   │
│ │                                                          │   │
│ └────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ No database found                                              │
└────────────────────────────────────────────────────────────────┘
```

**Warning State Styling:**
- Warning icon + header in warning orange (#ce9178), bold
- Message in secondary gray (#cccccc)

### Error State
```
┌────────────────────────────────────────────────────────────────┐
│ ✅ Ingested Documents                                         │
│                                                                │
│ ┌────────────────────────────────────────────────────────┐   │
│ │                                                          │   │
│ │  ❌ Error                                                │   │
│ │                                                          │   │
│ │  Error accessing database: [error message]              │   │
│ │                                                          │   │
│ └────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ Error loading data                                             │
└────────────────────────────────────────────────────────────────┘
```

**Error State Styling:**
- Error icon + header in error red (#f48771), bold
- Error message in error red (#f48771)

## Interactions

### Refresh Button
- **Hover**: Background changes from #343843 to #4a4e5a
- **Click**: Triggers refresh, queries database in background thread
- **Tooltip**: "Refresh the ingestion status" (appears after 500ms hover)

### Document List
- **Scrollable**: Vertical scrollbar appears when content exceeds height
- **Selectable**: Text can be selected and copied
- **Read-only**: Cannot be edited

### Tab Switching
- **Click Conversation tab**: Switches to conversation view
- **Click Ingest List tab**: Switches to ingest list view
- Tab state persists during session

## Responsiveness

The Ingest List tab is fully responsive:
- Minimum window size: 800x600 pixels
- Scales with window resizing
- Document list scrolls vertically when needed
- Statistics bar remains fixed at bottom

## Accessibility

- **High contrast**: Dark theme with sufficient contrast ratios
- **Clear icons**: Visual indicators (✅, 📍, 📦) for quick scanning
- **Readable fonts**: Segoe UI and Consolas with appropriate sizes
- **Tooltips**: Helpful text on interactive elements
- **Keyboard navigation**: Can be navigated with Tab key

## Integration with Existing UI

The Ingest List tab integrates seamlessly with the existing interface:
- Uses same color scheme and styling as conversation tab
- Maintains consistent spacing and padding
- Follows same card-based design pattern
- Shares the same status bar at bottom
- Respects the same window constraints

## Technical Notes

- **Thread Safety**: Database queries run in background threads
- **Non-blocking**: UI remains responsive during queries
- **Error Recovery**: Gracefully handles missing dependencies
- **Auto-refresh**: Can be manually refreshed at any time
- **Memory Efficient**: Only loads document metadata, not full content

---

**Note**: This is a textual description of the interface. The actual implementation uses tkinter with the described styling and layout. To see the live interface, run `python gui_director.py` after installing dependencies.

**Last Updated**: 2025-11-10
