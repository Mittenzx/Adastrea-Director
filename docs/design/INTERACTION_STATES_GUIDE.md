# Interaction States Guide

Visual guide showing how UI elements respond to user interactions.

---

## Button States

### Primary Button (Send Query, Start Ingestion)

#### Normal State
```
┌────────────────┐
│  Send Query    │  ← Blue background (#40a9ff)
└────────────────┘     Dark text (#1e1e1e)
```

#### Hover State
```
┌────────────────┐
│  Send Query    │  ← Lighter blue (#5bb8ff)
└────────────────┘     Subtle glow effect
                       Cursor: pointer
```

#### Pressed State
```
┌────────────────┐
│  Send Query    │  ← Darker blue (#3090cc)
└────────────────┘     Slight inset appearance
                       Visual feedback
```

#### Disabled State
```
┌────────────────┐
│  Send Query    │  ← Gray background (#3e3e42)
└────────────────┘     Dimmed text (#858585)
                       Cursor: not-allowed
```

#### Loading State
```
┌────────────────┐
│  ⏳ Sending...  │  ← Blue background
└────────────────┘     Animated spinner
                       Disabled interaction
```

---

## Input Field States

### Text Input (Query Box, Path Fields)

#### Normal State
```
╔════════════════════════════════════╗
║ Enter your query here...           ║  ← Dark background (#2a2d35)
╚════════════════════════════════════╝     Subtle border (#3e3e42)
                                           Placeholder text dimmed
```

#### Focus State
```
╔════════════════════════════════════╗
║ How do I create a Blueprint?▌      ║  ← Blue border (#40a9ff)
╚════════════════════════════════════╝     2px border width
                                           Cursor blinking
                                           Placeholder hidden
```

#### Filled State
```
╔════════════════════════════════════╗
║ How do I create a Blueprint?       ║  ← Normal border
╚════════════════════════════════════╝     Full text color
                                           Ready to edit
```

#### Error State
```
╔════════════════════════════════════╗
║ Invalid path                        ║  ← Red border (#f48771)
╚════════════════════════════════════╝     Red background tint
❌ Error: Path does not exist              Error message below
```

#### Disabled State
```
╔════════════════════════════════════╗
║ [Input disabled]                    ║  ← Dark gray (#3e3e42)
╚════════════════════════════════════╝     Dimmed text
                                           Cursor: not-allowed
```

---

## Progress Bar States

### Document Ingestion Progress

#### Idle (0%)
```
Processing file 0 of 10
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0%
Ready to start ingestion
```

#### Starting (5%)
```
Preparing to ingest documents...
▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  5%
Initializing...
```

#### Processing (40%)
```
Processing file 4 of 10
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░  40%
Ingesting: GameDesign.md (42 chunks)
```

#### Near Complete (90%)
```
Processing file 9 of 10
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░  90%
Ingesting: FinalDocument.md (23 chunks)
```

#### Complete (100%)
```
✓ Ingestion complete!
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  100%
Successfully processed 10 files
```

#### Error State
```
❌ Ingestion failed
▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░  35%
Error: Unable to read file
```

---

## Dialog/Panel States

### Settings Dialog

#### Normal State
```
┌─────────────────────────────────────┐
│ ⚙️ Settings                          │
├─────────────────────────────────────┤
│                                     │
│ API Configuration:                  │
│ [Configuration fields]              │
│                                     │
│          [Save]    [Cancel]         │
└─────────────────────────────────────┘
```

#### Saving State
```
┌─────────────────────────────────────┐
│ ⚙️ Settings                          │
├─────────────────────────────────────┤
│                                     │
│ API Configuration:                  │
│ [Configuration fields - disabled]   │
│                                     │
│      ⏳ Saving settings...          │
│                                     │
└─────────────────────────────────────┘
```

#### Success State
```
┌─────────────────────────────────────┐
│ ⚙️ Settings                          │
├─────────────────────────────────────┤
│                                     │
│ ✓ Settings saved successfully!      │
│                                     │
│ [Auto-closes in 2 seconds]          │
│                                     │
└─────────────────────────────────────┘
```

#### Error State
```
┌─────────────────────────────────────┐
│ ⚙️ Settings                          │
├─────────────────────────────────────┤
│                                     │
│ ❌ Failed to save settings           │
│                                     │
│ Error: Unable to write config file  │
│                                     │
│              [OK]                   │
└─────────────────────────────────────┘
```

---

## Status Indicator States

### Connection Status

#### Connected
```
● Connected to Python backend
```

#### Connecting
```
⏳ Connecting to Python backend...
```

#### Disconnected
```
○ Disconnected
```

#### Error
```
❌ Connection failed
```

---

## File Status Icons

### In Document List

#### Completed
```
✓ GameDesignDocument.md       (125 chunks)  [Green text]
```

#### Processing
```
⏳ GameplayMechanics.md       (processing...)  [Orange text]
```

#### Pending
```
⏹ EnemyAI.md                  (pending)  [Gray text]
```

#### Error
```
❌ BrokenFile.md               (error)  [Red text]
```

---

## Conversation Message States

### User Message

#### Normal
```
[14:23:45] 🔵 You: What is the main gameplay loop?
```

#### With Selection
```
[14:23:45] 🔵 You: What is ▓▓▓ main gameplay loop?
                              └─ Selected text highlighted
```

### AI Response

#### Loading
```
[14:23:46] 🤖 Assistant: ⏳ Thinking...
```

#### Streaming (partial response)
```
[14:23:46] 🤖 Assistant: The main gameplay loop consists of
                        three core phases: Exploration, Combat...▌
                                                     └─ Cursor indicates streaming
```

#### Complete
```
[14:23:47] 🤖 Assistant: The main gameplay loop consists of
                        three core phases: Exploration, Combat, 
                        and Progression. During exploration...
                        
                        [Processing time: 245ms]
```

#### Error
```
[14:23:47] ❌ Error: Failed to get response
                   Unable to connect to LLM provider.
                   Please check your API key.
```

---

## Tab States

### Tab Bar

#### Active Tab
```
┌──────────────┬──────────────┐
│ 💬 Conversation  │  📋 Ingest List  │  ← Active: darker, bold
└──────────────┴──────────────┘        Inactive: lighter, regular
```

#### Hover on Inactive Tab
```
┌──────────────┬──────────────┐
│ 💬 Conversation  │  📋 Ingest List  │  ← Slight highlight
└──────────────┴──────────────┘
```

---

## Tooltip States

### Button Tooltip

#### Before Hover
```
[Send Query]  ← No tooltip
```

#### On Hover (after 0.5s delay)
```
[Send Query]
    ↑
┌─────────────────────────────────────┐
│ Send query to Python backend        │
│ Shortcut: Enter or Ctrl+Enter       │
└─────────────────────────────────────┘
```

---

## Scrollbar States

### Results Display Scrollbar

#### Normal
```
┌─────────────────────────────────┐│
│ [Conversation content]          │▓  ← Scrollbar (dimmed)
│                                 │▓
│                                 │░
│                                 │░
└─────────────────────────────────┘│
```

#### Hover
```
┌─────────────────────────────────┐│
│ [Conversation content]          │█  ← Scrollbar (highlighted)
│                                 │█
│                                 │░
│                                 │░
└─────────────────────────────────┘│
```

#### Dragging
```
┌─────────────────────────────────┐│
│ [Conversation content]          │░
│                                 │█  ← Scrollbar (brighter)
│                                 │█  ← Active drag
│                                 │░
└─────────────────────────────────┘│
```

---

## Focus Indicators

### Keyboard Navigation

#### No Focus
```
[Query Input]  [Send Query]  [Clear History]
```

#### First Element Focused (Tab)
```
[Query Input]◄ [Send Query]  [Clear History]
  └─ Blue outline, 2px
```

#### Second Element Focused (Tab again)
```
[Query Input]  [Send Query]◄ [Clear History]
                  └─ Blue outline, 2px
```

#### Shift+Tab (Previous)
```
[Query Input]◄ [Send Query]  [Clear History]
  └─ Returns to previous element
```

---

## Loading Overlays

### Full Panel Loading

#### Normal View
```
┌─────────────────────────────────────┐
│ 🤖 Adastrea Director                │
├─────────────────────────────────────┤
│ [Panel content]                     │
└─────────────────────────────────────┘
```

#### Loading Overlay
```
┌─────────────────────────────────────┐
│ 🤖 Adastrea Director                │
├─────────────────────────────────────┤
│ ╔═══════════════════════════════╗   │
│ ║                               ║   │
│ ║      ⏳ Loading...            ║   │
│ ║                               ║   │
│ ║  Please wait while we         ║   │
│ ║  initialize the backend       ║   │
│ ║                               ║   │
│ ╚═══════════════════════════════╝   │
└─────────────────────────────────────┘
     └─ Semi-transparent overlay
```

---

## Context Menus

### Right-Click on Message

#### Before Right-Click
```
[14:23:47] 🤖 Assistant: The main gameplay loop...
```

#### After Right-Click
```
[14:23:47] 🤖 Assistant: The main gameplay loop...
                ↑
           ┌──────────────┐
           │ Copy         │
           │ Select All   │
           │ Export...    │
           └──────────────┘
```

---

## Notification States

### In-App Notifications

#### Success Notification
```
┌─────────────────────────────────────────┐
│ ✓ Settings saved successfully!          │
└─────────────────────────────────────────┘
  └─ Green background, auto-dismisses 3s
```

#### Warning Notification
```
┌─────────────────────────────────────────┐
│ ⚠️ API key not set. Some features       │
│    may not work correctly.              │
│                            [Dismiss]    │
└─────────────────────────────────────────┘
  └─ Orange background, manual dismiss
```

#### Error Notification
```
┌─────────────────────────────────────────┐
│ ❌ Failed to connect to backend          │
│    Please check the connection.         │
│                            [Retry]      │
└─────────────────────────────────────────┘
  └─ Red background, action button
```

#### Info Notification
```
┌─────────────────────────────────────────┐
│ ℹ️ Python backend started successfully   │
└─────────────────────────────────────────┘
  └─ Blue background, auto-dismisses 3s
```

---

## Transition Animations

### Panel Appearing
```
Frame 1 (0ms):    [Empty space]
Frame 2 (50ms):   [Panel 20% visible, fading in]
Frame 3 (100ms):  [Panel 60% visible]
Frame 4 (150ms):  [Panel 100% visible]
```

### Progress Bar Update
```
Frame 1:  ▓▓▓▓▓▓▓▓░░░░░░░░  40%
          [Smooth transition 200ms]
Frame 2:  ▓▓▓▓▓▓▓▓▓░░░░░░░  45%
```

### Button Press
```
Frame 1:  [Normal]
Frame 2:  [Pressed - 50ms]
Frame 3:  [Release - returns to normal or hover]
```

---

## Dark/Light Mode Comparison (Future)

### Current (Dark Only)
```
Background: #20232b (very dark)
Text: #e3e4e8 (light)
Accent: #40a9ff (bright blue)
```

### Future Light Mode
```
Background: #ffffff (white)
Text: #1e1e1e (dark)
Accent: #0078d4 (medium blue)
```

---

## Accessibility Indicators

### High Contrast Mode

#### Normal
```
[Send Query]  ← Standard colors
```

#### High Contrast
```
[Send Query]  ← Black text on yellow background
              ← Bold border
              ← Increased contrast ratio
```

### Screen Reader Announcements

#### Button Click
```
User clicks [Send Query]
Screen reader announces: "Send Query button pressed. Sending query..."
```

#### Progress Update
```
Progress changes from 40% to 50%
Screen reader announces: "Ingestion progress: 50 percent complete"
```

---

## Summary

All interaction states follow these principles:

1. **Visual Feedback**: Every interaction has visible feedback
2. **Timing**: Hover delays 0.5s, animations 150-300ms
3. **Accessibility**: All states keyboard-accessible and screen-reader friendly
4. **Consistency**: Same patterns across all components
5. **Clarity**: States are distinct and easy to understand

---

**Last Updated**: 2025-11-16
**See Also**: [Interface Mockups](UE_INTERFACE_MOCKUPS.md) | [Design System](UI_UX_DESIGN_SYSTEM.md)
