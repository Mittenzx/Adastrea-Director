# Ingest List Feature

## Overview

The **Ingest List** tab is a new feature in the Adastrea Director GUI that provides a visual checklist of documents that have been ingested into the vector database. This makes it easy to track which documents are available for the AI assistant to query.

## Features

### 1. Tabbed Interface

The GUI now includes a tabbed interface with two main tabs:
- **💬 Conversation**: The original conversation interface (unchanged functionality)
- **📋 Ingest List**: New tab showing document ingestion status

### 2. Ingested Documents Display

The Ingest List tab displays:
- ✅ **List of ingested documents** with full file paths
- 📦 **Number of chunks** per document (how many text chunks each document was split into)
- 📊 **Summary statistics** showing total documents and total chunks

### 3. Real-time Refresh

- **🔄 Refresh button** to update the list at any time
- Automatically loads when the tab is first opened
- Shows loading states and error messages when appropriate

### 4. Status Messages

The tab intelligently handles different states:
- **Success**: Shows all ingested documents with details
- **No Database**: Indicates no vector database exists yet
- **Empty Database**: Shows when database exists but is empty
- **Error**: Displays any errors encountered while accessing the database

## How to Use

### Step 1: Start the GUI

```bash
python gui_director.py
```

### Step 2: Ingest Documents

Before viewing the ingest list, you need to add documents to the vector database:

1. Click **📁 Ingest Folder** to add all documents from a folder
2. Click **📄 Ingest File** to add a single document
3. Click **🔗 Ingest Repo** to clone and ingest a GitHub repository

### Step 3: View Ingested Documents

1. Click on the **📋 Ingest List** tab
2. The list will automatically load and display all ingested documents
3. Click **🔄 Refresh** at any time to update the list

## Display Format

Each ingested document is displayed with:

```
✅ filename.md
   📍 /full/path/to/filename.md
   📦 5 chunks
```

- **Green checkmark (✅)**: Indicates successfully ingested document
- **Filename**: The name of the document
- **Path (📍)**: Full path to the document on your system
- **Chunks (📦)**: Number of text chunks the document was split into

## Statistics Bar

At the bottom of the Ingest List tab, you'll see summary statistics:

```
📊 Total: 12 documents • 87 chunks
```

This provides a quick overview of your entire knowledge base.

## Design

The Ingest List tab follows the same Unreal Engine 5-inspired design system as the rest of the application:

- **Dark theme** with professional colors
- **Card-based layout** with proper spacing
- **Consistent styling** with the rest of the application
- **Hover effects** on interactive elements
- **Tooltips** for better user experience

## Technical Details

### Database Query

The feature queries the ChromaDB vector database to retrieve:
- Total number of chunks (text segments)
- Metadata for each chunk (including source file path)
- Aggregated statistics per document

### Thread Safety

- Database queries run in a background thread to prevent UI freezing
- Results are updated on the main thread
- Error handling ensures the GUI remains responsive

### Error Handling

The feature gracefully handles:
- Missing dependencies (shows helpful installation message)
- Non-existent database directory
- Empty databases
- API key not set
- Connection errors

## Future Enhancements

Potential future improvements could include:

1. **Pending Documents List**: Show files in a selected folder that haven't been ingested yet
2. **Selective Deletion**: Remove specific documents from the database
3. **Re-ingestion**: Update already-ingested documents
4. **Search/Filter**: Find specific documents in the list
5. **Export List**: Export the ingestion status to a file
6. **Visual Progress**: Show ingestion progress in real-time
7. **File Type Filtering**: Filter by document type (.md, .py, .txt, etc.)

## Troubleshooting

### "No vector database found"

**Solution**: You need to ingest documents first. Use the ingest buttons in the Quick Actions section.

### "Required dependencies not installed"

**Solution**: Install the required Python packages:
```bash
pip install -r requirements.txt
```

### "Error accessing database"

**Possible causes**:
1. OPENAI_API_KEY not set
2. Database corruption
3. Permission issues

**Solution**: 
1. Set your API key using the 🔑 Set API Key button
2. Try re-ingesting documents
3. Check file permissions on the `chroma_db` directory

## Benefits

This feature provides several benefits:

1. **Visibility**: See exactly what the AI knows about
2. **Verification**: Confirm documents were successfully ingested
3. **Troubleshooting**: Quickly identify if documents are missing
4. **Organization**: Keep track of your knowledge base contents
5. **Confidence**: Know what information is available to query

## Related Files

- `gui_director.py`: Main GUI application with the Ingest List feature
- `ingest.py`: Script that performs document ingestion
- `test_ingest_list.py`: Test script to validate the feature
- `main.py`: CLI interface for querying the database

## Keyboard Shortcuts

While there are no specific keyboard shortcuts for the Ingest List tab, the existing shortcuts still work:

- `Ctrl+K`: Set API Key (needed for database access)
- `Ctrl+U`: Ingest Folder
- `Ctrl+L`: Clear conversation (on Conversation tab)

## Visual Example

When you open the Ingest List tab, you'll see something like:

```
📋 Document Ingestion Status                    [🔄 Refresh]
─────────────────────────────────────────────────────────

✅ Ingested Documents
┌──────────────────────────────────────────────────────┐
│                                                      │
│  ✅ README.md                                        │
│     📍 /path/to/project/README.md                   │
│     📦 12 chunks                                     │
│                                                      │
│  ✅ AGENTS.md                                        │
│     📍 /path/to/project/AGENTS.md                   │
│     📦 25 chunks                                     │
│                                                      │
│  ✅ ingest.py                                        │
│     📍 /path/to/project/ingest.py                   │
│     📦 8 chunks                                      │
│                                                      │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ 📊 Total: 3 documents • 45 chunks                   │
└──────────────────────────────────────────────────────┘
```

---

**Last Updated**: 2025-11-10
**Feature Version**: 1.0
**Part of**: Adastrea Director v1.0.0 (Phase 1)
