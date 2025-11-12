# Documents to Ingest for Adastrea Director

This document provides a comprehensive list of files to ingest into the Adastrea Director knowledge base. These documents will enable the AI assistant to understand your project, answer questions about game design, and assist with development tasks.

## Quick Start

To ingest all recommended documents at once:

```bash
# From the repository root directory
python ingest.py --docs-dir .
```

This will automatically process all supported file types (`.md`, `.txt`, `.py`) in the repository.

---

## Document Categories

### 1. Core Project Documentation

Essential documents that describe the project's purpose, architecture, and roadmap.

| File | Purpose | Priority |
|------|---------|----------|
| `README.md` | Main project overview and getting started guide | **High** |
| `PROJECT_PLAN.md` | Four-phase development roadmap and timelines | **High** |
| `AGENTS.md` | Agent system architecture and design principles | **High** |
| `CONTRIBUTING.md` | Contribution guidelines and development workflow | Medium |
| `LICENSE` | Project license information | Low |

### 2. Installation & Setup Documentation

Documents that help with installation, configuration, and troubleshooting.

| File | Purpose | Priority |
|------|---------|----------|
| `INSTALLATION.md` | Platform-specific installation instructions | **High** |
| `TROUBLESHOOTING.md` | Common issues and solutions | **High** |
| `requirements.txt` | Python dependencies list | Medium |
| `UPGRADE_NOTES.md` | Version upgrade information and breaking changes | Medium |

### 3. Design System Documentation

Complete UI/UX design documentation for the project.

| File | Purpose | Priority |
|------|---------|----------|
| `DESIGN_INDEX.md` | Complete guide to all design documentation | **High** |
| `UI_UX_DESIGN_SYSTEM.md` | Design system with principles, colors, typography | **High** |
| `DESIGN_GUIDE.md` | Visual specifications and implementation examples | **High** |
| `COMPONENT_LIBRARY.md` | Reusable UI components with code examples | **High** |
| `DESIGN_SYSTEM_SUMMARY.md` | Summary of design system | Medium |

### 4. GUI Documentation

Documentation specific to the graphical user interface implementation.

| File | Purpose | Priority |
|------|---------|----------|
| `GUI_IMPROVEMENTS.md` | Comprehensive GUI feature documentation | **High** |
| `GUI_QUICK_START.md` | User quick start guide for GUI | **High** |
| `GUI_CHANGES_SUMMARY.md` | Complete summary of all GUI changes | Medium |
| `GUI_VISUAL_COMPARISON.md` | Before/after GUI comparison | Medium |
| `GUI_SCREENSHOT_DESCRIPTION.md` | Detailed interface description | Medium |
| `GUI_UPGRADE_SUMMARY.md` | GUI upgrade history | Low |
| `GUI_DESIGN_COMPLIANCE.md` | GUI design compliance documentation | Medium |
| `GUI_IMPROVEMENTS_VISUAL.md` | Visual improvements documentation | Low |

### 5. Unreal Engine UI Documentation

Documentation for Unreal Engine-specific UI implementations.

| File | Purpose | Priority |
|------|---------|----------|
| `UE5_COMPLETE_REFINEMENT.md` | Complete UE5 UI refinement guide | **High** |
| `UE5_STYLE_VISUAL_MOCKUP.md` | UE5 style visual mockups | **High** |
| `UNREAL_ENGINE_UI_PR_SUMMARY.md` | Unreal Engine UI PR summary | Medium |
| `UNREAL_ENGINE_UI_UPDATES.md` | Unreal Engine UI updates | Medium |
| `UI_IMPLEMENTATION_GUIDE.md` | UI implementation instructions | **High** |
| `UI_REFINEMENT_SUMMARY.md` | UI refinement summary | Medium |
| `UI_COLOR_COMPARISON.md` | UI color scheme comparison | Medium |
| `UI_SCREENSHOT_README.md` | UI screenshot documentation | Low |

### 6. Visual Design Documentation

Visual mockups and design refinements.

| File | Purpose | Priority |
|------|---------|----------|
| `VISUAL_MOCKUP.md` | Visual design mockups | Medium |
| `SCREENSHOT_DESCRIPTION.md` | Screenshot descriptions | Low |
| `REFINEMENT_COMPLETE.md` | Design refinement completion notes | Low |

### 7. Game Design Templates & Examples

Templates and sample documents for game design.

| File | Purpose | Priority |
|------|---------|----------|
| `GDD_TEMPLATE.md` | Game design document template | **High** |
| `SAMPLE_GDD.md` | Example game design document | **High** |

### 8. Technical Schema & Specifications

Technical specifications and schema definitions.

| File | Purpose | Priority |
|------|---------|----------|
| `ACTION_SCHEMA.md` | Phase 2 action schema definition | **High** |

### 9. Code Files

Python source code files that implement the system.

| File | Purpose | Priority |
|------|---------|----------|
| `main.py` | CLI entry point | **High** |
| `ingest.py` | Document ingestion script | **High** |
| `gui_director.py` | GUI application | **High** |
| `install_dependencies.py` | Smart dependency installer | Medium |
| `check_compatibility.py` | Compatibility checker | Medium |
| `validate_requirements.py` | Requirements validator | Medium |
| `test_unicode_support.py` | Unicode support testing | Low |

### 10. PR and Review Documentation

Pull request summaries and review findings (lower priority for general use).

| File | Purpose | Priority |
|------|---------|----------|
| `PR_SUMMARY.md` | Pull request summaries | Low |
| `PR_REVIEW_FINDINGS.md` | Code review findings | Low |

---

## Ingestion Methods

### Method 1: Ingest Everything (Recommended for First Setup)

Ingest all supported files from the repository:

```bash
python ingest.py --docs-dir .
```

This is the fastest way to get started and ensures comprehensive coverage.

### Method 2: Ingest by Category

Ingest specific categories based on your needs:

**Core Documentation Only:**
```bash
python ingest.py --file README.md
python ingest.py --file PROJECT_PLAN.md
python ingest.py --file AGENTS.md
```

**Design System Documentation:**
```bash
python ingest.py --file DESIGN_INDEX.md
python ingest.py --file UI_UX_DESIGN_SYSTEM.md
python ingest.py --file DESIGN_GUIDE.md
python ingest.py --file COMPONENT_LIBRARY.md
```

**Game Design Templates:**
```bash
python ingest.py --file GDD_TEMPLATE.md
python ingest.py --file SAMPLE_GDD.md
```

### Method 3: Custom Selection

Create a temporary directory with symlinks or copies of specific files you want to ingest:

```bash
mkdir -p /tmp/custom_docs
cp README.md PROJECT_PLAN.md AGENTS.md /tmp/custom_docs/
python ingest.py --docs-dir /tmp/custom_docs
```

---

## Priority Guidelines

### High Priority Documents
These are essential for basic functionality and should always be ingested:
- All **Core Project Documentation**
- `INSTALLATION.md` and `TROUBLESHOOTING.md`
- Main **Design System Documentation**
- **Game Design Templates**
- Core **Python code files** (`main.py`, `ingest.py`, `gui_director.py`)

### Medium Priority Documents
Include these for comprehensive understanding:
- GUI implementation details
- Unreal Engine specific documentation
- Technical schemas and specifications
- Development workflow documents

### Low Priority Documents
These can be ingested for completeness but may not be frequently queried:
- Historical PR summaries and review findings
- Visual mockups and screenshots
- Upgrade notes and changelog details

---

## Supported File Types

The current ingestion system supports:
- **Markdown files** (`.md`) - Documentation, guides, templates
- **Text files** (`.txt`) - Plain text documents
- **Python files** (`.py`) - Source code with docstrings

---

## Advanced Usage

### Custom Collection Names

Organize different document sets into separate collections:

```bash
# Project documentation
python ingest.py --docs-dir . --collection-name project_docs

# User game design documents
python ingest.py --docs-dir /path/to/your/game/docs --collection-name my_game
```

### Custom Chunk Sizes

Adjust chunk size for different document types:

```bash
# Larger chunks for narrative documents
python ingest.py --docs-dir ./docs --chunk-size 2000 --chunk-overlap 400

# Smaller chunks for code
python ingest.py --file main.py --chunk-size 500 --chunk-overlap 100
```

### Check Database Status

View what's already ingested:

```bash
python ingest.py --stats
```

---

## Tips for Best Results

1. **Start with High Priority**: Ingest high-priority documents first to get the most value immediately.

2. **Include Your Game Design Docs**: After ingesting the system documentation, add your own game design documents to enable project-specific assistance.

3. **Update Regularly**: Re-run ingestion when documentation is updated to keep the knowledge base current.

4. **Use Meaningful Collection Names**: If working on multiple projects, use distinct collection names to keep them separate.

5. **Monitor Token Usage**: Larger document sets will consume more API tokens during queries. Start with essential documents and expand as needed.

---

## Excluding Unwanted Files

The ingestion script will automatically skip:
- Files in `.git` directories
- Binary files
- Files that fail to parse

If you want more control, use Method 3 (Custom Selection) to explicitly choose files.

---

## Next Steps After Ingestion

Once documents are ingested:

1. **Start the CLI Assistant:**
   ```bash
   python main.py
   ```

2. **Or launch the GUI:**
   ```bash
   python gui_director.py
   ```

3. **Test with sample questions:**
   - "What is the Adastrea Director?"
   - "Explain the four project phases"
   - "How do I install on Apple Silicon?"
   - "What agents are planned for Phase 3?"

---

## Troubleshooting Ingestion

**Issue: "No documents loaded"**
- Check that the path exists and contains supported file types
- Verify file permissions

**Issue: "Error initializing OpenAI embeddings"**
- Ensure `OPENAI_API_KEY` is set in your environment
- Check API key validity

**Issue: "Chunking creates too many/few chunks"**
- Adjust `--chunk-size` and `--chunk-overlap` parameters
- Typical ranges: chunk-size 500-2000, overlap 100-400

For more help, see `TROUBLESHOOTING.md`.

---

**Last Updated:** 2025-11-10  
**Version:** 1.0  
**Compatible with:** Adastrea Director Phase 1
