# Adastrea Director - Unreal Editor Interface Mockups

## Overview

This document provides detailed visual mockups of the Adastrea Director plugin interface within Unreal Engine Editor. These mockups show how the AI assistant integrates seamlessly into the UE5 workflow.

---

## Mockup 1: Main Panel - Query Interface

This is the primary interface users interact with when asking questions to the AI assistant.

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🤖 Adastrea Director - AI Assistant                           [▢][○][✕] ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                            ┃
┃  ┌─ Query ────────────────────────────────────────────────────────────┐  ┃
┃  │                                                                      │  ┃
┃  │  ╔═══════════════════════════════════════════════════════════════╗ │  ┃
┃  │  ║ How do I create a Blueprint for player movement?             ║ │  ┃
┃  │  ╚═══════════════════════════════════════════════════════════════╝ │  ┃
┃  │                                                                      │  ┃
┃  │  [Send Query]  [Clear History]                                      │  ┃
┃  │                                                                      │  ┃
┃  └──────────────────────────────────────────────────────────────────────┘  ┃
┃                                                                            ┃
┃  ┌─ Results ───────────────────────────────────────────────────────────┐  ┃
┃  │                                                                      │  ┃
┃  │  Welcome to Adastrea Director!                                      │  ┃
┃  │                                                                      │  ┃
┃  │  Enter a query above and click 'Send Query' or press Enter to      │  ┃
┃  │  get started.                                                       │  ┃
┃  │                                                                      │  ┃
┃  │  Example: "What is Unreal Engine?"                                  │  ┃
┃  │                                                                      │  ┃
┃  │  ┌────────────────────────────────────────────────────────────────┐ │  ┃
┃  │  │  🔵 Query: How do I create a Blueprint for player movement?   │ │  ┃
┃  │  │                                                                 │ │  ┃
┃  │  │  🤖 Response:                                                  │ │  ┃
┃  │  │                                                                 │ │  ┃
┃  │  │  To create a Blueprint for player movement in Unreal Engine:  │ │  ┃
┃  │  │                                                                 │ │  ┃
┃  │  │  1. Open Content Browser                                       │ │  ┃
┃  │  │  2. Right-click > Blueprint Class                              │ │  ┃
┃  │  │  3. Select "Character" as parent class                         │ │  ┃
┃  │  │  4. Name it "BP_PlayerCharacter"                               │ │  ┃
┃  │  │  5. Open the Blueprint and add movement components...          │ │  ┃
┃  │  │                                                                 │ │  ┃
┃  │  │  [Processing time: 245ms]                                      │ │  ┃
┃  │  └────────────────────────────────────────────────────────────────┘ │  ┃
┃  │                                                                      │  ┃
┃  │                                                                      │  ┃
┃  │  [Scrollable conversation history]                                  │  ┃
┃  │                                                                      │  ┃
┃  └──────────────────────────────────────────────────────────────────────┘  ┃
┃                                                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Design Notes:
- **Theme**: Dark UE5 style with blue accents (#40a9ff)
- **Query Box**: Single-line input with focus highlight
- **Results Area**: Scrollable with formatted responses
- **Buttons**: UE5 standard button style
- **Response Cards**: Subtle border with light background for readability

---

## Mockup 2: Ingestion Tab - Document Management

This tab allows users to ingest documentation into the knowledge base.

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🤖 Adastrea Director - AI Assistant                           [▢][○][✕] ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                            ┃
┃  ┌─ Documentation Ingestion ────────────────────────────────────────────┐  ┃
┃  │                                                                      │  ┃
┃  │  Documentation Folder:                                              │  ┃
┃  │  ╔════════════════════════════════════════════════╗  [Browse...]    │  ┃
┃  │  ║ C:/Projects/MyGame/Docs                        ║                 │  ┃
┃  │  ╚════════════════════════════════════════════════╝                 │  ┃
┃  │                                                                      │  ┃
┃  │  Database Path:                                                     │  ┃
┃  │  ╔════════════════════════════════════════════════╗  [Browse...]    │  ┃
┃  │  ║ C:/Projects/MyGame/chroma_db                   ║                 │  ┃
┃  │  ╚════════════════════════════════════════════════╝                 │  ┃
┃  │                                                                      │  ┃
┃  │  [Start Ingestion]  [Stop]                                          │  ┃
┃  │                                                                      │  ┃
┃  └──────────────────────────────────────────────────────────────────────┘  ┃
┃                                                                            ┃
┃  ┌─ Progress ──────────────────────────────────────────────────────────┐  ┃
┃  │                                                                      │  ┃
┃  │  ⚡ Ingestion in progress...                                         │  ┃
┃  │                                                                      │  ┃
┃  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░  65%    │  ┃
┃  │                                                                      │  ┃
┃  │  Processing file 13 of 20                                           │  ┃
┃  │  Ingesting: GameplayMechanics.md (87 chunks)                        │  ┃
┃  │                                                                      │  ┃
┃  │  ┌────────────────────────────────────────────────────────────────┐ │  ┃
┃  │  │  ✓ GameDesignDocument.md       (125 chunks)                   │ │  ┃
┃  │  │  ✓ CharacterAbilities.md       (67 chunks)                    │ │  ┃
┃  │  │  ✓ LevelDesign.md              (43 chunks)                    │ │  ┃
┃  │  │  ⏳ GameplayMechanics.md       (processing...)                 │ │  ┃
┃  │  │  ⏹ EnemyAI.md                  (pending)                       │ │  ┃
┃  │  │  ⏹ Weapons.md                  (pending)                       │ │  ┃
┃  │  │  ⏹ PowerUps.md                 (pending)                       │ │  ┃
┃  │  └────────────────────────────────────────────────────────────────┘ │  ┃
┃  │                                                                      │  ┃
┃  └──────────────────────────────────────────────────────────────────────┘  ┃
┃                                                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Design Notes:
- **Path Inputs**: Text fields with browse buttons for easy navigation
- **Progress Bar**: Real-time visual feedback with percentage
- **File List**: Shows status of each document (✓ done, ⏳ processing, ⏹ pending)
- **Status Messages**: Clear indication of current operation
- **Buttons**: Enable/disable based on state (Start disabled during ingestion)

---

## Mockup 3: Settings Panel (Future)

Configuration panel for API keys and preferences.

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ⚙️ Settings                                                    [▢][○][✕] ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                            ┃
┃  ┌─ API Configuration ──────────────────────────────────────────────────┐  ┃
┃  │                                                                      │  ┃
┃  │  LLM Provider:                                                      │  ┃
┃  │    ◉ Gemini (Recommended)       ○ OpenAI                            │  ┃
┃  │                                                                      │  ┃
┃  │  Gemini API Key:                                                    │  ┃
┃  │  ╔════════════════════════════════════════════════════════════════╗ │  ┃
┃  │  ║ ••••••••••••••••••••••••••••••••                              ║ │  ┃
┃  │  ╚════════════════════════════════════════════════════════════════╝ │  ┃
┃  │                                                                      │  ┃
┃  │  OpenAI API Key:                                                    │  ┃
┃  │  ╔════════════════════════════════════════════════════════════════╗ │  ┃
┃  │  ║ ••••••••••••••••••••••••••••••••                              ║ │  ┃
┃  │  ╚════════════════════════════════════════════════════════════════╝ │  ┃
┃  │                                                                      │  ┃
┃  │  Embedding Provider:                                                │  ┃
┃  │    ◉ HuggingFace (Free, No API Key)       ○ OpenAI                 │  ┃
┃  │                                                                      │  ┃
┃  └──────────────────────────────────────────────────────────────────────┘  ┃
┃                                                                            ┃
┃  ┌─ Display Options ────────────────────────────────────────────────────┐  ┃
┃  │                                                                      │  ┃
┃  │  Font Size:  [10] pt  ▲▼                                            │  ┃
┃  │                                                                      │  ┃
┃  │  ☑ Auto-save settings                                               │  ┃
┃  │  ☑ Show timestamps in conversation                                  │  ┃
┃  │  ☑ Auto-scroll to latest message                                    │  ┃
┃  │                                                                      │  ┃
┃  └──────────────────────────────────────────────────────────────────────┘  ┃
┃                                                                            ┃
┃  ┌─ Backend Configuration ──────────────────────────────────────────────┐  ┃
┃  │                                                                      │  ┃
┃  │  Python Backend Status: ✓ Running (PID: 12345)                      │  ┃
┃  │                                                                      │  ┃
┃  │  IPC Port: [50051]                                                  │  ┃
┃  │                                                                      │  ┃
┃  │  [Restart Backend]  [View Logs]                                     │  ┃
┃  │                                                                      │  ┃
┃  └──────────────────────────────────────────────────────────────────────┘  ┃
┃                                                                            ┃
┃                                                                            ┃
┃                          [Save]        [Cancel]                            ┃
┃                                                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Design Notes:
- **Sections**: Grouped by functionality (API, Display, Backend)
- **Radio Buttons**: For provider selection with recommendations
- **Masked Inputs**: Security for API keys (show as bullets)
- **Checkboxes**: Boolean preferences
- **Status Indicators**: Real-time backend status with visual icons
- **Action Buttons**: Clear save/cancel actions at bottom

---

## Mockup 4: Integrated UE5 Editor View

Shows how Adastrea Director appears docked within the Unreal Engine Editor.

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File  Edit  Window  Help                    🎮 Unreal Engine 5.3                                   [▢][○][✕] ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                                                            ┃
┃  ┌──────────────────────────────────────────────┐  ┌───────────────────────────────────────────────────┐ ┃
┃  │  📁 Content Browser                         │  │  🎬 Viewport                                      │ ┃
┃  │  ┌──────────────────────────────────────┐   │  │                                                   │ ┃
┃  │  │ Content                              │   │  │       ┌─────────────────────┐                    │ ┃
┃  │  │  ├─ Blueprints/                      │   │  │       │                     │                    │ ┃
┃  │  │  │  ├─ BP_Player                     │   │  │       │   [3D Viewport]     │                    │ ┃
┃  │  │  │  ├─ BP_Enemy                      │   │  │       │                     │                    │ ┃
┃  │  │  │  └─ BP_Weapon                     │   │  │       │   Camera view of    │                    │ ┃
┃  │  │  ├─ Materials/                       │   │  │       │   game level        │                    │ ┃
┃  │  │  ├─ Maps/                            │   │  │       │                     │                    │ ┃
┃  │  │  └─ UI/                              │   │  │       └─────────────────────┘                    │ ┃
┃  │  │                                      │   │  │                                                   │ ┃
┃  │  └──────────────────────────────────────┘   │  └───────────────────────────────────────────────────┘ ┃
┃  │                                              │                                                        ┃
┃  │  [Grid View] 📄 123 items                   │                                                        ┃
┃  └──────────────────────────────────────────────┘                                                        ┃
┃                                                                                                            ┃
┃  ┌──────────────────────────────────────────────┐  ┌───────────────────────────────────────────────────┐ ┃
┃  │  📊 Details                                 │  │  🤖 Adastrea Director                             │ ┃
┃  │                                              │  │  ┌─ Query ─────────────────────────────────────┐  │ ┃
┃  │  Transform                                   │  │  │ ╔═══════════════════════════════════════╗  │  │ ┃
┃  │    Location: X:0 Y:0 Z:0                     │  │  │ ║ How do I optimize rendering?          ║  │  │ ┃
┃  │    Rotation: X:0 Y:0 Z:0                     │  │  │ ╚═══════════════════════════════════════╝  │  │ ┃
┃  │    Scale: X:1 Y:1 Z:1                        │  │  │ [Send Query] [Clear]                       │  │ ┃
┃  │                                              │  │  └─────────────────────────────────────────────┘  │ ┃
┃  │  Mesh                                        │  │  ┌─ Results ───────────────────────────────────┐  │ ┃
┃  │    Static Mesh: SM_Cube                      │  │  │ 🤖 To optimize rendering:                  │  │ ┃
┃  │    Materials: [M_Default]                    │  │  │                                            │  │ ┃
┃  │                                              │  │  │ 1. Use LODs for distant objects            │  │ ┃
┃  │  Physics                                     │  │  │ 2. Enable occlusion culling                │  │ ┃
┃  │    ☑ Simulate Physics                       │  │  │ 3. Optimize material complexity...         │  │ ┃
┃  │    Mass: 100.0                               │  │  │                                            │  │ ┃
┃  │                                              │  │  │ [See full response]                        │  │ ┃
┃  └──────────────────────────────────────────────┘  │  └─────────────────────────────────────────────┘  │ ┃
┃                                                     └───────────────────────────────────────────────────┘ ┃
┃                                                                                                            ┃
┃  [Output Log] Build successful. Ready to play.                                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Design Notes:
- **Dockable Panel**: Adastrea Director appears as a standard UE5 dockable window
- **Integration**: Sits alongside other editor panels (Content Browser, Details, Viewport)
- **Compact Design**: Optimized for side-by-side use with other tools
- **Seamless Workflow**: No context switching needed - ask questions while working
- **Standard UE5 Theme**: Matches editor appearance perfectly

---

## Mockup 5: Standalone Python GUI Application

The standalone GUI application that works outside of Unreal Engine.

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File  Edit  Help                  Adastrea Director - AI Game Development Assistant  ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                                       ┃
┃  ┌─────────────────────────────────────────────────────────────────────────────────┐ ┃
┃  │  🤖 Adastrea Director                                                          │ ┃
┃  │  AI-Powered Game Development Assistant                                         │ ┃
┃  │  ● Ready                                                                        │ ┃
┃  └─────────────────────────────────────────────────────────────────────────────────┘ ┃
┃                                                                                       ┃
┃  ┌─ Quick Actions ──────────────────────────────────────────────────────────────────┐ ┃
┃  │ [📁 Ingest Folder] [📄 Ingest File] [🔗 Ingest Repo]                           │ ┃
┃  │ [🔑 Set API Key] [🗑️ Clear] [📋 Copy]               Font: [A-] [A+]           │ ┃
┃  └─────────────────────────────────────────────────────────────────────────────────┘ ┃
┃                                                                                       ┃
┃  ┌─ Progress ────────────────────────────────────────────────────────────────────────┐ ┃
┃  │ Processing file 3 of 10                                                          │ ┃
┃  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  30%   │ ┃
┃  │ Ingesting: GameDesign.md (42 chunks)                                            │ ┃
┃  └─────────────────────────────────────────────────────────────────────────────────┘ ┃
┃                                                                                       ┃
┃  💬 Conversation    📋 Ingest List                                                   ┃
┃  ┌─────────────────────────────────────────────────────────────────────────────────┐ ┃
┃  │  💬 Conversation History                                        3 messages       │ ┃
┃  │  ───────────────────────────────────────────────────────────────────────────────  │ ┃
┃  │                                                                                  │ ┃
┃  │  [14:23:45] 🔵 You: What is the main gameplay loop?                             │ ┃
┃  │                                                                                  │ ┃
┃  │  [14:23:47] 🤖 Assistant: The main gameplay loop consists of three core         │ ┃
┃  │             phases: Exploration, Combat, and Progression. During exploration... │ ┃
┃  │                                                                                  │ ┃
┃  │  [14:25:12] 🔵 You: How do player abilities work?                               │ ┃
┃  │                                                                                  │ ┃
┃  │  [14:25:14] 🤖 Assistant: Player abilities are divided into three categories:   │ ┃
┃  │             1. Active abilities - triggered by player input                     │ ┃
┃  │             2. Passive abilities - always active effects                        │ ┃
┃  │             3. Ultimate abilities - high-impact skills with cooldowns...        │ ┃
┃  │                                                                                  │ ┃
┃  │  [Scrollable conversation history]                                              │ ┃
┃  │                                                                                  │ ┃
┃  └─────────────────────────────────────────────────────────────────────────────────┘ ┃
┃                                                                                       ┃
┃  ┌─ Your Question ──────────────────────────────────────────────────────────────────┐ ┃
┃  │ ╔═════════════════════════════════════════════════════════════════════════════╗  │ ┃
┃  │ ║ Tell me about the enemy AI system                                          ║  │ ┃
┃  │ ╚═════════════════════════════════════════════════════════════════════════════╝  │ ┃
┃  │                                                                        [Ask ▶]   │ ┃
┃  └─────────────────────────────────────────────────────────────────────────────────┘ ┃
┃                                                                                       ┃
┃  ✓ Ready.                                                                             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Design Notes:
- **Menu Bar**: Standard application menus (File, Edit, Help)
- **Header**: Branding with status indicator
- **Quick Actions**: Frequently used operations in one place
- **Progress Bar**: Shows during long operations (ingestion)
- **Tabs**: Switch between Conversation view and Ingest List
- **Conversation**: Scrollable history with timestamps and color coding
- **Input Area**: Large text input with prominent send button
- **Status Bar**: Current application state
- **Dark Theme**: Professional appearance, easy on eyes

---

## Color Palette

### Primary Colors
```
┌─────────────────────────────────────────────────────┐
│ Background (Dark):        #20232b  ████████████████ │
│ Background (Lighter):     #2a2d35  ████████████████ │
│ Border/Separator:         #3e3e42  ████████████████ │
│ Accent Blue:              #40a9ff  ████████████████ │
│ Text Primary:             #e3e4e8  ████████████████ │
│ Text Secondary:           #cccccc  ████████████████ │
│ Text Muted:               #858585  ████████████████ │
└─────────────────────────────────────────────────────┘
```

### Status Colors
```
┌─────────────────────────────────────────────────────┐
│ Success/Done:             #4ec9b0  ████████████████ │
│ Warning/Processing:       #ce9178  ████████████████ │
│ Error/Stop:               #f48771  ████████████████ │
│ Info/User:                #569cd6  ████████████████ │
└─────────────────────────────────────────────────────┘
```

---

## Typography

### Font Hierarchy
- **Title**: Segoe UI, 16pt, Bold
- **Section Headers**: Segoe UI, 12pt, Bold
- **Body Text**: Segoe UI, 10pt, Regular
- **Input Text**: Segoe UI, 10pt, Regular
- **Status/Details**: Segoe UI, 9pt, Regular
- **Monospace**: Consolas, 9pt (for code/paths)

---

## Interaction States

### Button States
```
Normal:     [ Button Text ]     (Gray background)
Hover:      [ Button Text ]     (Lighter gray + subtle highlight)
Pressed:    [ Button Text ]     (Darker, slightly inset)
Disabled:   [ Button Text ]     (Dimmed, gray text)
```

### Input Field States
```
Normal:     ╔═══════════╗        (Dark gray background)
Focus:      ╔═══════════╗        (Blue border highlight)
Error:      ╔═══════════╗        (Red border)
Disabled:   ╔═══════════╗        (Dimmed, gray)
```

### Progress Indicators
```
Idle:       ░░░░░░░░░░░░░░░░░░   0%
Loading:    ▓▓▓▓▓▓▓░░░░░░░░░░░   40%
Complete:   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   100%
```

---

## Icons & Symbols

### Status Icons
- ✓ Success/Done
- ⚡ Processing/Active
- ⏳ Waiting/Queued
- ⏹ Stopped/Pending
- ❌ Error/Failed
- ℹ️ Information
- ⚠️ Warning

### Action Icons
- 🔵 User message
- 🤖 AI response
- 📁 Folder/Directory
- 📄 File/Document
- 🔗 Link/Connection
- 🔑 API Key/Settings
- 🗑️ Delete/Clear
- 📋 Copy
- ⚙️ Settings/Configure
- 🎮 Unreal Engine

---

## Layout Principles

### 1. Visual Hierarchy
- Headers clearly separate sections
- Consistent padding and spacing (10px standard)
- Grouped related elements with borders

### 2. Information Density
- Balance between information and whitespace
- Scrollable areas for long content
- Collapsible sections (future enhancement)

### 3. Accessibility
- High contrast text (WCAG AA compliant)
- Clear focus indicators
- Keyboard navigation support
- Screen reader friendly labels

### 4. Responsiveness
- Minimum window size: 800x600
- Flexible layouts that adapt
- Scrollable content areas
- Dockable panels in UE Editor

---

## Use Cases Illustrated

### Use Case 1: First-Time User
```
User opens plugin → Sees welcome message → Clicks "Send Query" → 
Gets immediate feedback → Learns to use interface
```

### Use Case 2: Documentation Ingestion
```
User clicks "Browse" → Selects docs folder → Clicks "Start Ingestion" → 
Watches progress bar → Sees file-by-file progress → Gets completion notification
```

### Use Case 3: Asking Questions
```
User types question → Presses Enter → Sees "Processing..." → 
Response appears with formatting → Can scroll history → Can copy response
```

### Use Case 4: Configuration
```
User opens Settings → Selects API provider → Enters key → 
Adjusts display preferences → Saves → Settings persist
```

---

## Future Enhancements Visualization

### Phase 3: Performance Monitoring
```
┌─ Performance Metrics ────────────────────────────────┐
│ FPS: 60 ████████████████████░░  (Target: 60)       │
│ Memory: 2.3GB ███████░░░░░░░░░  (Max: 4GB)         │
│ Draw Calls: 1,245  ⚠️ High                          │
│                                                     │
│ [View Details] [Optimize Now]                       │
└─────────────────────────────────────────────────────┘
```

### Phase 3: Bug Detection
```
┌─ Bug Reports ────────────────────────────────────────┐
│ ❌ Critical: Crash in BP_Enemy::OnDeath (Line 42)  │
│ ⚠️ Warning: Memory leak in level transition         │
│ ℹ️ Info: Unused asset detected: SM_OldWeapon        │
│                                                     │
│ [View All] [Generate Report]                        │
└─────────────────────────────────────────────────────┘
```

### Phase 4: Content Generation
```
┌─ Content Assistant ──────────────────────────────────┐
│ Generate:                                           │
│ ○ Quest dialogue                                    │
│ ○ Item description                                  │
│ ● Character backstory                               │
│                                                     │
│ Character: [Warrior Hero]                           │
│ Tone: [Serious] [Humorous] [Mysterious]            │
│                                                     │
│ [Generate] [Refine]                                 │
└─────────────────────────────────────────────────────┘
```

---

## Technical Implementation Notes

### Slate Widget Structure (UE Plugin)
```
SAdastreaDirectorPanel (SCompoundWidget)
├─ SVerticalBox (Main Container)
│  ├─ STextBlock (Header)
│  ├─ SSeparator
│  ├─ SVerticalBox (Query Tab)
│  │  ├─ SEditableTextBox (Query Input)
│  │  ├─ SButton (Send)
│  │  └─ SMultiLineEditableTextBox (Results)
│  └─ SVerticalBox (Ingestion Tab)
│     ├─ SEditableTextBox (Docs Path)
│     ├─ SButton (Browse)
│     ├─ SProgressBar
│     └─ STextBlock (Status)
```

### Python GUI Structure
```
TkinterWindow
├─ Frame (Header)
│  └─ Label (Title + Status)
├─ Frame (Quick Actions)
│  └─ Multiple Buttons
├─ Frame (Progress - conditionally shown)
│  ├─ Progressbar
│  └─ Labels (Status text)
├─ Notebook (Tabs)
│  ├─ Frame (Conversation Tab)
│  │  ├─ ScrolledText (History)
│  │  └─ Entry + Button (Input)
│  └─ Frame (Ingest List Tab)
│     └─ Treeview (Document list)
└─ Label (Status Bar)
```

---

## Summary

These mockups provide a comprehensive visual reference for the Adastrea Director interface across both:
- **Unreal Engine Plugin**: Seamlessly integrated into UE5 Editor
- **Standalone Application**: Independent Python GUI for any workflow

Key features illustrated:
✓ Query interface with real-time responses
✓ Document ingestion with progress tracking
✓ Settings and configuration panels
✓ Status indicators and feedback
✓ Professional UE5-inspired dark theme
✓ Accessible, user-friendly design

---

**Last Updated**: 2025-11-16
**Status**: Visual mockups complete and ready for implementation reference
