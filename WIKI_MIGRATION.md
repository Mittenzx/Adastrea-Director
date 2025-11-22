# Wiki Migration Manifest

**Date:** 2025-11-22  
**Purpose:** Document the migration of all documentation from the main repository to the GitHub Wiki

## Overview

All documentation files have been moved from the main repository to the [Adastrea Director Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki) to:
- Reduce repository clutter
- Separate documentation from code
- Make documentation more accessible and easier to edit
- Follow GitHub best practices for project organization

## Files Kept in Repository

The following files remain in the main repository:

- **README.md** - Main project entry point and quick start guide
- **CONTRIBUTING.md** - Contribution guidelines for developers
- **LICENSE** - Project license
- **Plugins/AdastreaDirector/*.md** - Plugin-specific documentation (stays with code)

## Files Moved to Wiki

### Root Directory Documentation (46 files)

**Analysis & Reports:**
- ADASTREA_DIRECTOR_ANALYSIS.md
- API_COST_ANALYSIS.md
- ARCHITECTURE_ANALYSIS.md
- MARKETPLACE_SELLABILITY_REPORT.md
- MARKETPLACE_SELLABILITY_SUMMARY.md

**Architecture & Design:**
- AGENTS.md
- CHOOSING_DEPLOYMENT_MODE.md
- CODE_REFERENCE.md
- ARCHITECTURE_REVIEW_SUMMARY.md

**Phase Documentation:**
- PHASE3_COMPLETE.md
- PHASE3_COMPLETION_SUMMARY.md
- PHASE3_COMPLETION_VERIFICATION.md
- PHASE3_CONTINUATION_SUMMARY.md
- PHASE3_FINAL_SUMMARY.md
- PHASE3_FUNCTIONAL_COMPLETION.md
- PHASE3_GUIDE.md
- PHASE3_IMPLEMENTATION_SUMMARY.md
- PHASE3_ORCHESTRATION_SUMMARY.md
- PHASE3_PREREQUISITES_COMPLETION.md
- PHASE3_README.md
- PHASE3_UE_INTEGRATION_COMPLETE.md
- PHASE3_WORK_ORDER.md
- PHASE_STRUCTURE_VISUAL.md

**Guides & References:**
- INDEX.md
- START_HERE.md
- ROADMAP.md
- INTEGRATION_GUIDE.md
- DOCUMENTATION_QUICK_REFERENCE.md
- DOCUMENTATION_RESTRUCTURE_SUMMARY.md

**UI & Features:**
- PROGRESS_BAR_UI.md
- SETTINGS_DIALOG_VISUAL_GUIDE.md
- INGEST_LOG_FEATURE.md
- INGEST_UI_COMPARISON.md

**Implementation & Summaries:**
- CODE_QUALITY_REVIEW_SUMMARY.md
- EMBEDDING_PROVIDER_CHANGES.md
- IMPROVEMENTS.md
- PLUGIN_DEVELOPMENT_FEASIBILITY.md
- PR_SUMMARY.md

**Project Management:**
- SPRINT_CHECKLIST.md
- SPRINT_CHECKLIST_COPILOT.md
- SPRINT_CHECKLIST_MITTENZX.md
- START_SPRINT.md
- TASKS_2_WEEKS.md
- TASK_BOARD.md
- TESTING_NOTES.md
- WORKSPACE_MENU_RESEARCH.md

**Alternatives & Comparisons:**
- LLM_ALTERNATIVES.md

### docs/ Directory (108 files)

**docs/ Root:**
- INDEX.md
- INDEXING_SYSTEM.md
- TEST_SKIP_ANALYSIS.md

**docs/completed/ (14 files):**
- README.md
- ANALYSIS_IMPLEMENTATION_SUMMARY.md
- ARCHITECTURE_REVIEW_SUMMARY.md
- IMPLEMENTATION_SUMMARY.md
- IMPLEMENTATION_SUMMARY_WEEK_7_8.md
- PLUGIN_PHASE1_WEEK1_SUMMARY.md
- PLUGIN_PHASE1_WEEK2_SUMMARY.md
- PLUGIN_TESTING_SUMMARY.md
- PLUGIN_WEEKS_5_6_SUMMARY.md
- TASK_LIST_SUMMARY.md
- UE_PYTHON_INTEGRATION_SUMMARY.md
- UNREAL_PLUGIN_RESEARCH_SUMMARY.md
- VISUAL_MOCKUPS_SUMMARY.md
- WEEK1_ORCHESTRATION_COMPLETION.md
- WEEK_7_8_COMPLETION.md

**docs/design/ (16 files):**
- COMPONENT_LIBRARY.md
- DESIGN_GUIDE.md
- DESIGN_INDEX.md
- DESIGN_SYSTEM_SUMMARY.md
- INTERACTION_STATES_GUIDE.md
- INTERFACE_MOCKUPS_QUICK_REFERENCE.md
- MOCKUPS_README.md
- MOCKUP_IMPLEMENTATION_COMPARISON.md
- UE5_COMPLETE_REFINEMENT.md
- UE5_STYLE_VISUAL_MOCKUP.md
- UE_INTERFACE_MOCKUPS.md
- UI_COLOR_COMPARISON.md
- UI_IMPLEMENTATION_GUIDE.md
- UI_REFINEMENT_SUMMARY.md
- UI_UX_DESIGN_SYSTEM.md
- VISUAL_MOCKUP.md

**docs/gui/ (12 files):**
- GUI_CHANGES_SUMMARY.md
- GUI_DESIGN_COMPLIANCE.md
- GUI_IMPROVEMENTS.md
- GUI_IMPROVEMENTS_VISUAL.md
- GUI_QUICK_START.md
- GUI_SCREENSHOT_DESCRIPTION.md
- GUI_SETTINGS.md
- GUI_UPGRADE_SUMMARY.md
- GUI_VISUAL_COMPARISON.md
- INGEST_LIST_FEATURE.md
- INGEST_LIST_SCREENSHOT.md
- UI_SCREENSHOT_README.md

**docs/guides/ (24 files):**
- ACTION_SCHEMA.md
- AGENTS_UTILITY_ASSESSMENT.md
- API_KEY_MANAGEMENT.md
- DEPENDENCY_CACHING.md
- DOCS_TO_INGEST.md
- DOCUMENT_INGESTION.md
- ERROR_HANDLING.md
- GAME_REPO_FEATURE_SUMMARY.md
- GAME_REPO_INGESTION.md
- GDD_TEMPLATE.md
- INSTALLATION.md
- ISSUE_40_RESOLUTION.md
- OPENAI_EMBEDDINGS_SETUP.md
- OPTION1_NEXT_STEPS.md
- POPULATE_DATABASE.md
- PROJECT_PLAN.md
- QUERY_OPTIMIZATION.md
- QUICK_START_GAME_REPO.md
- REPOSITORY_STRUCTURE.md
- SAMPLE_GDD.md
- SETUP_GITHUB_SECRETS.md
- TRIGGER_DATABASE_POPULATION.md
- TROUBLESHOOTING.md
- UNREAL_MCP_ASSESSMENT.md

**docs/phases/ (8 files):**
- AGENT_ORCHESTRATION.md
- INTEGRATION_TESTING.md
- PHASE1_COMPLETION.md
- PHASE1_RAG_COMPLETION_SUMMARY.md
- PHASE2_COMPLETION.md
- PHASE2_GUIDE.md
- PHASE2_STATUS.md
- PHASE2_SUMMARY.md
- PHASE2_TO_PHASE3_CHECKLIST.md
- PHASE3_STATUS.md

**docs/remote-control/ (6 files):**
- IMPLEMENTATION_SUMMARY.md
- REMOTE_CONTROL_API.md
- REMOTE_CONTROL_IMPLEMENTATION_PLAN.md
- REMOTE_CONTROL_QUICKSTART.md
- REMOTE_CONTROL_REVIEW_SUMMARY.md
- REMOTE_CONTROL_VISUAL_SUMMARY.md

**docs/summaries/ (13 files):**
- README.md
- FILES_CREATED_SUMMARY.md
- IMPLEMENTATION_SUMMARY.md
- INGESTION_FIX_SUMMARY.md
- OPTIMIZATION_SUMMARY.md
- PR_REVIEW_FINDINGS.md
- PR_SUMMARY.md
- REFINEMENT_COMPLETE.md
- REVIEW_SUMMARY.md
- SCREENSHOT_DESCRIPTION.md
- UNICODE_ENCODING_FIX.md
- UNREAL_ENGINE_UI_PR_SUMMARY.md
- UNREAL_ENGINE_UI_UPDATES.md
- UPGRADE_NOTES.md

**docs/testing/ (9 files):**
- GAME_REPO_TEST_RESULTS.md
- GUI_TESTING_GUIDE.md
- PHASE3_INTEGRATION_TESTING.md
- RAG_SYSTEM_VERIFICATION.md
- RUN_INTEGRATION_TESTS.md
- TESTING.md
- TESTING_OPTIMIZATIONS.md
- TEST_SUMMARY.md

## Total Files Moved

- **Root Directory:** 46 documentation files
- **docs/ Directory:** 108 documentation files
- **Total:** 154 documentation files

## Accessing Documentation

All documentation is now available in the [Adastrea Director Wiki](https://github.com/Mittenzx/Adastrea-Director/wiki).

The wiki maintains the same organizational structure:
- **Home** - Getting started and quick links
- **Installation & Setup** - Installation guides and troubleshooting
- **Usage** - How to use different features
- **Phases** - Phase-specific documentation (P1-P4)
- **Architecture** - System architecture and design
- **Development** - Contributing, testing, and development guides
- **Design** - UI/UX design system
- **Remote Control** - Remote control API documentation

## Migration Notes

- All internal links have been updated to point to the wiki
- The README.md has been updated with wiki links
- Plugin documentation remains in the Plugins/ directory with the code
- This manifest file serves as a historical record of the migration

---

*Last Updated: 2025-11-22*
