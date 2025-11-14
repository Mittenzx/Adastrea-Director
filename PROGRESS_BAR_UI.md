# Progress Bar UI Feature

## Visual Overview

The progress bar appears between the "Quick Actions" buttons and the main tabbed interface during document ingestion operations.

```
┌────────────────────────────────────────────────────────────────┐
│ ⚡ Adastrea Director                                           │
│ AI-Powered Game Development Assistant                         │
│ ● Ready                                                        │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ Quick Actions                                                  │
│ [📁 Ingest Folder] [📄 Ingest File] [🔗 Ingest Repo]         │
│ [🔑 Set API Key] [🗑️ Clear] [📋 Copy]                         │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ Processing file 3 of 10                                        │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │ 30%
│ Ingesting: game_design.md (42 chunks)                          │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ 💬 Conversation    📋 Ingest List                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ 💬 Conversation History                      0 messages        │
│ ─────────────────────────────────────────────────────────────  │
│                                                                │
│ [Conversation content appears here]                            │
│                                                                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Features

### 1. Real-Time Progress Updates
- **Progress Percentage**: Visual bar showing completion (0-100%)
- **Main Label**: Current operation description (e.g., "Processing file 3 of 10")
- **Details**: Specific information about the current step
  - File checking: "Checking: filename.md"
  - File loading: "Loading: filename.md"
  - Chunking: "Chunking: filename.md"
  - Ingesting: "Ingesting: filename.md (N chunks)"

### 2. Visual Design
- **Theme Integration**: Matches the UE5-inspired dark theme
- **Colors**:
  - Background: `#2d2d30` (dark gray)
  - Border: `#3e3e42` (slightly lighter gray)
  - Progress Bar: `#40a9ff` (blue accent)
  - Text: `#e3e4e8` (light gray)
  - Details: `#cccccc` (medium gray)
- **Style**: Card-based design with subtle border
- **Height**: 20px progress bar for good visibility

### 3. Behavior
- **Appears**: When any ingestion operation starts (folder, file, or repo)
- **Updates**: Every 100ms by polling a temporary JSON file
- **Hides**: Automatically when ingestion completes or fails
- **Cleanup**: Removes temporary progress file after completion

## User Experience

### During Ingestion
1. User clicks "📁 Ingest Folder" and selects a directory
2. Progress bar card appears immediately with "Preparing to ingest documents..."
3. Progress updates show:
   - Which file is being processed (1 of N)
   - What operation is happening (checking, loading, chunking, ingesting)
   - Chunk count for each file
4. Progress bar fills from 0% to 100% as files are processed
5. When complete, progress bar disappears and success message appears

### Example Progress Sequence
```
[0%]   Preparing to ingest documents...
       Initializing...

[10%]  Processing file 1 of 10
       Checking: player_abilities.md

[15%]  Processing file 1 of 10
       Loading: player_abilities.md

[18%]  Processing file 1 of 10
       Chunking: player_abilities.md

[20%]  Processing file 1 of 10
       Ingesting: player_abilities.md (15 chunks)

[30%]  Processing file 2 of 10
       Checking: game_mechanics.md

...

[100%] Ingestion complete!
       Processed 10 files
```

## Technical Implementation

### GUI Side (gui_director.py)
- **Progress Card Widget**: ttk.Progressbar with custom styling
- **Labels**: Two labels for main text and details
- **Polling**: Checks progress file every 100ms using `root.after()`
- **Methods**:
  - `show_progress_bar()`: Shows the progress card
  - `hide_progress_bar()`: Hides and cleans up
  - `update_progress()`: Updates bar value and text
  - `poll_progress_file()`: Reads JSON and updates UI

### Ingestion Side (ingest.py)
- **ProgressWriter Class**: Handles writing progress updates
- **JSON Format**:
  ```json
  {
    "percent": 30,
    "label": "Processing file 3 of 10",
    "details": "Ingesting: game_design.md (42 chunks)"
  }
  ```
- **Integration Points**:
  - File checking phase
  - Document loading phase
  - Chunking phase
  - Ingestion/embedding phase

### Communication Protocol
1. GUI creates temporary JSON file path
2. GUI passes file path to ingest.py via `--progress-file` argument
3. Ingest.py writes progress updates to file at key points
4. GUI polls file every 100ms and updates UI
5. GUI deletes file when process completes

## Benefits

1. **User Feedback**: Clear visibility into long-running operations
2. **Progress Indication**: Know how much work remains
3. **Operation Transparency**: See exactly what's happening at each step
4. **Professional Feel**: Polished, modern interface
5. **Error Context**: If something fails, users know which file caused the issue

## Future Enhancements (Optional)

- Time remaining estimate
- Processing speed (files/second)
- Cancel button to stop ingestion mid-process
- Detailed log expansion for power users
- Progress history for multiple ingestion sessions
