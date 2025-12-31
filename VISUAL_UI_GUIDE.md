# Visual UI/UX Guide - Adastrea Director

This document provides visual representations of the new UI components using ASCII art and descriptions.

## 1. Main Window Layout

```
┌────────────────────────────────────────────────────────────────────────┐
│  ⚡ Adastrea Director                            [🔑 Set API Key]       │
│  AI-Powered Game Development Assistant                                 │
│  ● Ready                                                                │
├────────────────────────────────────────────────────────────────────────┤
│  [📁 Ingest Folder] [📄 Ingest File] [🔗 Ingest Repo] [🗑️ Clear]     │
│  Text Size: [A-] [A+]                                                   │
├────────────────────────────────────────────────────────────────────────┤
│  [🏠 Home] [💬 Conversation] [📋 Ingest] [🧪 Tests] [🤖 Agents] ◄NEW!│
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Tab Content Area (Dynamically Changes)                                │
│                                                                         │
│                                                                         │
├────────────────────────────────────────────────────────────────────────┤
│  💭 Ask a Question                                                      │
│  ┌─────────────────────────────────────────────────┐                   │
│  │ Enter your query here...                        │  [Send ▶]         │
│  └─────────────────────────────────────────────────┘                   │
├────────────────────────────────────────────────────────────────────────┤
│  ● Ready • Waiting for your question                        v1.0.0     │
└────────────────────────────────────────────────────────────────────────┘
```

## 2. Agent Dashboard Tab (NEW!)

```
┌────────────────────────────────────────────────────────────────────────┐
│  📊 Agent Dashboard                                           [🔄]      │
│  Monitor Phase 3 autonomous agents in real-time                        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  System Overview                                                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │ 🤖          │ │ ⚠️           │ │ ⏱️           │ │ 💚           │ │
│  │ Active      │ │ Active       │ │ Uptime       │ │ System       │ │
│  │ Agents      │ │ Alerts       │ │ 2h 34m       │ │ Health       │ │
│  │             │ │              │ │              │ │              │ │
│  │     2/3     │ │      3       │ │              │ │     Good     │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ │
│                                                                         │
│  🤖 Autonomous Agents                                          [🔄]     │
│                                                                         │
│  ┌─▼ ⚡ Performance Profiling ──────────────────────────────────────┐ │
│  │  Status: [✅ Running]                                            │ │
│  │                                                                   │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│ │
│  │  │ FPS         │ │ Memory      │ │ CPU         │ │ GPU         ││ │
│  │  │             │ │             │ │             │ │             ││ │
│  │  │     60      │ │   4.2 GB    │ │     45%     │ │     62%     ││ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌─▼ 🐛 Bug Detection ──────────────────────────────────────────────┐ │
│  │  Status: [ℹ️ Idle]                                               │ │
│  │                                                                   │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│ │
│  │  │ Critical    │ │ High        │ │ Medium      │ │ Low         ││ │
│  │  │             │ │             │ │             │ │             ││ │
│  │  │      0      │ │      2      │ │      5      │ │     12      ││ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌─▼ ✨ Code Quality ───────────────────────────────────────────────┐ │
│  │  Status: [✅ Running]                                            │ │
│  │                                                                   │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│ │
│  │  │ Issues      │ │ Warnings    │ │ Tech Debt   │ │ Score       ││ │
│  │  │             │ │             │ │             │ │             ││ │
│  │  │      8      │ │     23      │ │     Low     │ │   85/100    ││ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

## 3. Status Badge Component

```
Color-coded status indicators:

[✅ Running]    - Success (Green #4ec9b0)
[ℹ️ Idle]      - Info (Blue #40a9ff)
[⚠️ Warning]   - Warning (Orange #ce9178)
[❌ Error]     - Error (Red #f48771)
[❓ Unknown]   - Neutral (Gray #858585)
```

## 4. Info Card Component

```
┌──────────────────────┐
│ 🤖                  │
│ Active Agents        │
│                      │
│        2/3           │
└──────────────────────┘

Components:
- Large icon (top left)
- Small label (gray)
- Large value (white, bold)
- Card border and padding
```

## 5. Collapsible Section

```
Expanded:
┌─▼ Section Title ──────────────────┐
│                                    │
│  Content visible here              │
│  Multiple lines supported          │
│                                    │
└────────────────────────────────────┘

Collapsed:
┌─▶ Section Title ──────────────────┐
└────────────────────────────────────┘

Click header to toggle
```

## 6. Action Button Variants

```
Primary:    [🚀 Run Tests]     - Bright blue (#40a9ff)
Secondary:  [📁 Browse...]     - Dark gray (#343843)
Success:    [✅ Complete]      - Green (#4ec9b0)
Danger:     [❌ Delete]        - Red (#f48771)

All buttons:
- Icon + Text
- Hover effect (lighter color)
- Rounded corners
- Consistent padding
```

## 7. Progress Indicator

```
┌──────────────────────────────────────┐
│ Processing documents...              │
│ ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░ 45%      │
│ Scanned: 23/50 files                 │
└──────────────────────────────────────┘

Components:
- Label (top)
- Progress bar (middle)
- Details (bottom)
- Animated during operation
```

## 8. Metrics Panel

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ ⚡          │ │ 💾           │ │ 🔥           │ │ 🎮           │
│ FPS          │ │ Memory       │ │ CPU          │ │ GPU          │
│              │ │              │ │              │ │              │
│     60       │ │   4.2 GB     │ │     45%      │ │     62%      │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘

Grid layout:
- 2-4 columns (responsive)
- Equal spacing
- Consistent card size
```

## 9. Color Scheme Reference

### Background Colors
```
Primary:   #20232b  ████  Main background
Secondary: #252526  ████  Panel background
Tertiary:  #2d2d30  ████  Card background
```

### Text Colors
```
Primary:   #e3e4e8  ████  Main text
Secondary: #cccccc  ████  Secondary text
Muted:     #858585  ████  Disabled/subtle text
```

### Accent Colors
```
Blue:      #40a9ff  ████  Primary actions
Hover:     #5bb8ff  ████  Hover state
Active:    #005a9e  ████  Active/pressed
```

### Status Colors
```
Success:   #4ec9b0  ████  Green (running, ok)
Warning:   #ce9178  ████  Orange (attention)
Error:     #f48771  ████  Red (error, stopped)
Info:      #40a9ff  ████  Blue (info, idle)
```

### Border Colors
```
Border:    #3e3e42  ████  Default borders
Highlight: #094771  ████  Selection highlight
```

## 10. Typography

```
Font Family: Segoe UI (Windows), San Francisco (macOS), Roboto (Linux)

Sizes:
- Title:    16pt bold  (Headers, page titles)
- Subtitle: 11pt       (Section headers)
- Body:     10pt       (Main content)
- Small:     9pt       (Labels, details)
- Tiny:      8pt       (Timestamps, footnotes)

Metric Values: 14pt bold (Card values)
Icons: 20pt (Card icons), 10pt (Button icons)
```

## 11. Spacing System

```
Unit: 5px base

xxs:  2px   (Tight spacing)
xs:   5px   (Minimal spacing)
sm:  10px   (Small spacing)
md:  15px   (Standard spacing)
lg:  20px   (Large spacing)
xl:  30px   (Extra large spacing)

Padding (buttons): 18px horizontal, 9px vertical
Padding (cards):   15px all sides
Padding (sections): 10px-20px based on hierarchy
```

## 12. Interactive States

### Buttons
```
Default:  [  Button  ]  - Normal state
Hover:    [  Button  ]  - Lighter background
Active:   [  Button  ]  - Pressed state
Disabled: [  Button  ]  - Grayed out
```

### Input Fields
```
Default:  ┌───────────┐  - Border: #3e3e42
          │           │
          └───────────┘

Focus:    ┌───────────┐  - Border: #40a9ff (blue)
          │ █         │
          └───────────┘
```

## 13. Icons Used

```
System:
⚡ Performance/Speed
🤖 Agents/AI
💾 Storage/Memory
🔥 CPU/Heat
🎮 GPU/Graphics
⏱️ Time/Duration
💚 Health/Good

Actions:
🔄 Refresh/Reload
🔗 Link/Connect
📁 Folder/Browse
📄 File/Document
📋 List/Clipboard
🔑 Key/Security
🗑️ Delete/Clear
💾 Save/Export
▶ Play/Run
⏹ Stop
⏸ Pause

Status:
✅ Success/Complete
❌ Error/Failed
⚠️ Warning/Attention
ℹ️ Info/Idle
❓ Unknown/Question
🐛 Bug/Issue
✨ Quality/Clean
📊 Analytics/Charts
```

## 14. Animation & Transitions

```
Hover Effects:
- Duration: 150ms
- Easing: ease-in-out
- Properties: background-color

Collapse/Expand:
- Duration: 200ms
- Easing: ease-out
- Properties: height, opacity

Progress Bar:
- Smooth animation
- Update every 100ms
- No janky jumps
```

## 15. Accessibility Features

```
✓ High contrast ratios (4.5:1 minimum)
✓ Clear focus indicators
✓ Keyboard navigation support
✓ Screen reader friendly labels
✓ Consistent tab order
✓ Error messages clearly visible
✓ Large click targets (48px+)
```

## 16. Responsive Behavior

```
Window Size:
Minimum:  800x600px
Optimal: 1200x800px
Maximum: Unrestricted

Card Grid:
1200px+:  4 columns
900-1199: 3 columns
600-899:  2 columns
<600px:   1 column

Collapsible sections automatically collapse
at narrow widths to save space.
```

---

## Implementation Notes

1. **Widget Library**: All components in `gui_widgets.py`
2. **Agent Panel**: Full implementation in `gui_agent_panel.py`
3. **Test Suite**: Interactive demo in `test_ui_components.py`
4. **Integration**: Examples in `UIUX_IMPROVEMENTS.md`
5. **Plugin Guide**: C++ Slate examples in `PLUGIN_UI_ENHANCEMENT.md`

## Visual Consistency Checklist

- [ ] All buttons use ActionButton or consistent styling
- [ ] All metrics use InfoCard components
- [ ] All status indicators use StatusBadge
- [ ] All sections can collapse (where appropriate)
- [ ] All progress uses ProgressIndicator
- [ ] Color scheme consistent throughout
- [ ] Spacing follows the 5px base system
- [ ] Typography uses defined sizes
- [ ] Icons are consistent and meaningful
- [ ] Hover states on all interactive elements

---

**Last Updated**: December 2025  
**Maintainer**: Copilot + Mittenzx  
**Status**: Documentation Complete, Ready for Visual Testing
