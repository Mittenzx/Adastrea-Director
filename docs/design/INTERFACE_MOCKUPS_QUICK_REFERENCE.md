# Interface Mockups - Quick Reference

A condensed visual guide to Adastrea Director interfaces.

---

## 🎮 UE Plugin - Main Query Interface

```
┌─────────────────────────────────────────────────────┐
│ 🤖 Adastrea Director - AI Assistant                │
├─────────────────────────────────────────────────────┤
│ Query:                                              │
│ ┌─────────────────────────────────────────────────┐ │
│ │ How do I create a Blueprint for movement?       │ │
│ └─────────────────────────────────────────────────┘ │
│ [Send Query]  [Clear History]                       │
│                                                     │
│ Results:                                            │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 🔵 Q: How do I create a Blueprint for movement? │ │
│ │                                                 │ │
│ │ 🤖 A: To create a Blueprint:                    │ │
│ │ 1. Open Content Browser                         │ │
│ │ 2. Right-click > Blueprint Class                │ │
│ │ 3. Select "Character" as parent class           │ │
│ │ 4. Name it "BP_PlayerCharacter"...              │ │
│ │                                                 │ │
│ │ [Scrollable]                                    │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

**Key Features:**
- Single-line query input with Enter support
- Scrollable results with formatted responses
- Clear history button for conversation reset
- UE5 dark theme (#20232b background)

---

## 📁 UE Plugin - Ingestion Interface

```
┌─────────────────────────────────────────────────────┐
│ 🤖 Adastrea Director - Document Ingestion          │
├─────────────────────────────────────────────────────┤
│ Documentation Folder:                               │
│ [C:/Projects/MyGame/Docs          ] [Browse...]     │
│                                                     │
│ Database Path:                                      │
│ [C:/Projects/MyGame/chroma_db     ] [Browse...]     │
│                                                     │
│ [Start Ingestion]  [Stop]                           │
│                                                     │
│ Progress:                                           │
│ ⚡ Ingestion in progress...                         │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░  65%               │
│ Processing file 13 of 20                            │
│ Ingesting: GameplayMechanics.md (87 chunks)         │
│                                                     │
│ Files:                                              │
│ ✓ GameDesignDocument.md (125 chunks)                │
│ ✓ CharacterAbilities.md (67 chunks)                 │
│ ⏳ GameplayMechanics.md (processing...)             │
│ ⏹ EnemyAI.md (pending)                              │
└─────────────────────────────────────────────────────┘
```

**Key Features:**
- Path selection with browse dialogs
- Real-time progress bar (0-100%)
- File-by-file status tracking
- Status icons (✓ done, ⏳ processing, ⏹ pending)

---

## ⚙️ Settings Panel

```
┌─────────────────────────────────────────────────────┐
│ ⚙️ Settings                                         │
├─────────────────────────────────────────────────────┤
│ API Configuration:                                  │
│   ◉ Gemini (Recommended)    ○ OpenAI               │
│                                                     │
│ Gemini API Key:                                     │
│ [••••••••••••••••••••••••••••••]                    │
│                                                     │
│ OpenAI API Key:                                     │
│ [••••••••••••••••••••••••••••••]                    │
│                                                     │
│ Embedding Provider:                                 │
│   ◉ HuggingFace (Free)    ○ OpenAI                 │
│                                                     │
│ Display Options:                                    │
│ Font Size: [10] pt ▲▼                               │
│ ☑ Auto-save settings                                │
│ ☑ Show timestamps                                   │
│                                                     │
│ Backend Status: ✓ Running (PID: 12345)              │
│                                                     │
│            [Save]        [Cancel]                   │
└─────────────────────────────────────────────────────┘
```

**Key Features:**
- Provider selection with radio buttons
- Masked API key inputs (security)
- Display preferences (font size, checkboxes)
- Backend status monitoring
- Save/cancel actions

---

## 🖥️ Standalone Python GUI

```
┌─────────────────────────────────────────────────────┐
│ File  Edit  Help       Adastrea Director           │
├─────────────────────────────────────────────────────┤
│ 🤖 Adastrea Director                               │
│ AI-Powered Game Development Assistant               │
│ ● Ready                                             │
├─────────────────────────────────────────────────────┤
│ Quick Actions:                                      │
│ [📁 Ingest Folder] [🔑 Set API Key] [🗑️ Clear]    │
│                                                     │
│ Progress (when active):                             │
│ ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░  30%                 │
│ Ingesting: GameDesign.md (42 chunks)                │
├─────────────────────────────────────────────────────┤
│ 💬 Conversation    📋 Ingest List                   │
├─────────────────────────────────────────────────────┤
│ Conversation History                 3 messages     │
│                                                     │
│ [14:23] 🔵 You: What is the gameplay loop?         │
│ [14:23] 🤖 Assistant: The loop consists of...      │
│                                                     │
│ [14:25] 🔵 You: How do abilities work?             │
│ [14:25] 🤖 Assistant: Abilities are divided...     │
│                                                     │
│ [Scrollable]                                        │
├─────────────────────────────────────────────────────┤
│ Your Question:                                      │
│ [Tell me about the enemy AI system    ] [Ask ▶]    │
├─────────────────────────────────────────────────────┤
│ ✓ Ready.                                            │
└─────────────────────────────────────────────────────┘
```

**Key Features:**
- Menu bar (File, Edit, Help)
- Header with branding and status
- Quick action buttons
- Collapsible progress bar
- Tabbed interface (Conversation / Ingest List)
- Timestamp support
- Large input area
- Status bar

---

## 🎯 Integrated UE5 View (Compact)

```
┌────────────────────────────────────────────────────────────┐
│ 🎮 Unreal Engine 5.3                        [Window] [Help] │
├────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐  │
│ │ 📁 Content  │ │ 🎬 Viewport  │ │ 🤖 Adastrea         │  │
│ │   Browser   │ │              │ │                     │  │
│ │             │ │  [3D View]   │ │ Query:              │  │
│ │ Blueprints/ │ │              │ │ [How to optimize?]  │  │
│ │ Materials/  │ │  Camera of   │ │ [Send]              │  │
│ │ Maps/       │ │  game level  │ │                     │  │
│ │             │ │              │ │ Results:            │  │
│ │             │ │              │ │ 🤖 To optimize:     │  │
│ └─────────────┘ └──────────────┘ │ 1. Use LODs         │  │
│ ┌─────────────┐                  │ 2. Enable culling   │  │
│ │ 📊 Details  │                  │ 3. Optimize...      │  │
│ │             │                  └─────────────────────┘  │
│ │ Transform   │                                           │
│ │ Location... │                                           │
│ └─────────────┘                                           │
└────────────────────────────────────────────────────────────┘
```

**Key Features:**
- Dockable alongside standard UE panels
- Compact design for side-by-side use
- No context switching needed
- Matches UE5 editor theme

---

## 🎨 Color Reference

```
Background Dark:    #20232b  ████
Background Light:   #2a2d35  ████
Border:             #3e3e42  ████
Accent Blue:        #40a9ff  ████
Text Primary:       #e3e4e8  ████
Text Secondary:     #cccccc  ████
Success:            #4ec9b0  ████
Warning:            #ce9178  ████
Error:              #f48771  ████
```

---

## 📐 Layout Specs

**Minimum Sizes:**
- UE Plugin Panel: 400x600 pixels
- Standalone GUI: 800x600 pixels

**Spacing:**
- Standard padding: 10px
- Section gaps: 15px
- Button spacing: 5px

**Typography:**
- Headers: 12-16pt Bold
- Body: 10pt Regular
- Status: 9pt Regular

---

## 🔤 Icon Reference

**Status:**
- ✓ Done/Success
- ⚡ Active/Processing
- ⏳ Waiting/Queued
- ⏹ Pending/Stopped
- ❌ Error/Failed
- ⚠️ Warning

**Actions:**
- 🔵 User message
- 🤖 AI response
- 📁 Folder
- 📄 File
- 🔗 Link
- 🔑 API Key
- 🗑️ Clear/Delete
- 📋 Copy
- ⚙️ Settings

---

## 🚀 Future Phases Preview

**Phase 3 - Performance Monitoring:**
```
┌─ Performance ────────────────────────┐
│ FPS: 60 ████████████░░  (60 target) │
│ Memory: 2.3GB ███████░░  (4GB max)  │
│ Draw Calls: 1,245 ⚠️ High           │
│ [View Details] [Optimize]            │
└──────────────────────────────────────┘
```

**Phase 3 - Bug Detection:**
```
┌─ Bug Reports ─────────────────────────┐
│ ❌ Critical: Crash in BP_Enemy (L42)  │
│ ⚠️ Warning: Memory leak in transition │
│ ℹ️ Info: Unused asset SM_OldWeapon    │
│ [View All] [Generate Report]          │
└───────────────────────────────────────┘
```

**Phase 4 - Content Generation:**
```
┌─ Content Assistant ─────────────────┐
│ Generate: ● Character backstory     │
│ Character: [Warrior Hero]           │
│ Tone: [Serious] [Humorous]          │
│ [Generate] [Refine]                 │
└─────────────────────────────────────┘
```

---

## 📝 Notes

**Design Philosophy:**
- Dark theme for reduced eye strain
- High contrast for accessibility
- Clear visual hierarchy
- Consistent spacing and alignment
- Intuitive icon usage
- Professional UE5 aesthetic

**Interaction Patterns:**
- Enter key submits queries
- Hover states on all interactive elements
- Clear focus indicators
- Disabled states when appropriate
- Real-time feedback during operations

**Accessibility:**
- WCAG AA contrast compliance
- Keyboard navigation support
- Screen reader friendly
- Clear error messages
- Visual feedback for all actions

---

**Last Updated**: 2025-11-16
**See Also**: [Full Mockups](UE_INTERFACE_MOCKUPS.md) | [Design System](UI_UX_DESIGN_SYSTEM.md)
