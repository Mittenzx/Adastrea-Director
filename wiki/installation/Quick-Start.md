# Quick Start Tutorial

Get started with Adastrea Director in just a few minutes!

## 🎯 What You'll Learn

In this tutorial, you'll:
- ✅ Run your first query
- ✅ Ingest documentation
- ✅ Create an implementation plan
- ✅ Use the GUI application

**Time Required:** 5-10 minutes

## Prerequisites

✅ You've completed [Installation & Setup](Getting-Started.md)

## Step 1: Your First Query (CLI)

Let's start with a simple query using the command-line interface:

```bash
# Activate your virtual environment (if not already active)
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Start the interactive assistant
python main.py
```

You'll see a prompt like this:
```
Adastrea Director - Context-Aware Assistant
Type 'quit' or 'exit' to end the session.

> 
```

Try asking a question:
```
> What is Adastrea Director?
```

**Note:** The first query may be slow as it loads the embeddings model. Subsequent queries will be much faster!

## Step 2: Ingest Documentation

To get meaningful answers about your project, you need to populate the knowledge base:

### Option A: Sample Documentation

Start with the project's own documentation:

```bash
# Ingest the README and core documentation
python ingest.py --docs-dir .
```

This will:
- ✅ Scan for markdown files
- ✅ Process and chunk documents
- ✅ Create vector embeddings
- ✅ Store in the database

### Option B: Your Project Documentation

Ingest your own documentation:

```bash
# Ingest from a specific directory
python ingest.py --docs-dir /path/to/your/docs

# Ingest multiple types of files
python ingest.py --docs-dir /path/to/your/docs --file-types .md .txt .rst
```

### Option C: Adastrea Game Repository (For Team Members)

```bash
# Set your GitHub token
export GITHUB_TOKEN="ghp_your_token_here"

# Populate with game repository
python ingest_game_repo.py
```

See the [Document Ingestion Guide](Document-Ingestion.md) for advanced options.

## Step 3: Use the Planning System (P2)

Now let's create an implementation plan:

```bash
# Start interactive planning mode
python planner.py --interactive
```

Try this example goal:
```
> Add a player inventory system with drag-and-drop UI
```

The planner will:
- 📊 Analyze your goal
- 📋 Break it down into prioritized tasks
- 🔗 Identify dependencies
- 💻 Suggest code implementations
- ⏱️ Estimate effort required

### Export Your Plan

```bash
# Plan a specific goal and export to markdown
python planner.py "Optimize rendering pipeline" --export markdown --output plan.md

# Export to JSON for programmatic use
python planner.py "Add multiplayer support" --export json --output plan.json
```

## Step 4: Explore Advanced Features

### Agent Orchestration (P3)

```bash
# Start the agent orchestrator CLI
python agent_orchestrator_cli.py start --all

# Check agent status
python agent_orchestrator_cli.py status

# View the real-time dashboard
python agent_dashboard.py --auto-start
```

### Unreal Engine Plugin

If you're working in Unreal Engine:

1. Copy `Plugins/AdastreaDirector` to your UE project's `Plugins` folder
2. Regenerate project files
3. Build your project
4. Open **Window → Developer Tools → Adastrea Director**

See the [Plugin Guide](Plugin-Setup.md) for detailed instructions.

## Common Workflows

### Workflow 1: Documentation Q&A

```bash
# 1. Ingest your docs
python ingest.py --docs-dir /path/to/docs

# 2. Start asking questions
python main.py
> How do I implement feature X?
> What are the requirements for Y?
> Explain the architecture of Z
```

### Workflow 2: Planning & Implementation

```bash
# 1. Define your goal
python planner.py --interactive
> Add user authentication with OAuth2

# 2. Review the generated plan
# 3. Export for your team
python planner.py "Add authentication" --export markdown --output auth_plan.md

# 4. Follow the implementation steps
```

### Workflow 3: Continuous Development

```bash
# 1. Keep knowledge base updated
python ingest.py --docs-dir . --update

# 2. Generate plans as needed
python planner.py "Refactor module X"
```

## Tips for Success

### 🎯 Getting Better Answers

1. **Be Specific:** Instead of "How do I code this?", ask "How do I implement a singleton pattern for a game manager in C++?"

2. **Provide Context:** The more documents you ingest, the better the answers

3. **Use Natural Language:** Write questions as you would ask a colleague

### 📚 Maintaining Your Knowledge Base

1. **Regular Updates:** Re-run ingestion when documentation changes
   ```bash
   python ingest.py --docs-dir . --update
   ```

2. **Check What's Ingested:** Use the Ingest List tab in the GUI to see all documents

3. **Organize Documents:** Keep documentation in a structured directory for easier ingestion

### ⚡ Performance Tips

1. **First Query is Slow:** The initial query loads models - this is normal
2. **Use Local Config:** Save API keys to avoid re-entering them
3. **GPU Acceleration:** If you have a GPU, embeddings will be faster

## Troubleshooting Quick Fixes

**No/Poor Responses:**
- ✅ Ensure you've ingested relevant documentation
- ✅ Check your API key is set correctly
- ✅ Verify internet connection (for API-based LLMs)

**Slow Performance:**
- ✅ First query is always slow (loading models)
- ✅ Subsequent queries should be fast
- ✅ Consider using GPU acceleration

**GUI Won't Start:**
- ✅ Ensure tkinter is installed (see [Installation Guide](Getting-Started.md))
- ✅ Try running `python -m tkinter` to test

## Next Steps

Now that you're familiar with the basics:

- **📖 [Context-Aware Assistant Guide](../usage/Context-Aware-Assistant.md)** - Deep dive into P1 features
- **📋 [Planning System Guide](../usage/Planning-System.md)** - Master P2 planning capabilities
- **🤖 [Autonomous Agents Guide](../usage/Autonomous-Agents.md)** - Set up P3 proactive monitoring
- **🎨 [GUI Application Guide](../usage/GUI-Application.md)** - Explore all GUI features

## Example Queries to Try

Here are some example queries to get you started:

```
> What is the main purpose of this project?
> How do I contribute to this project?
> What are the system requirements?
> Explain the RAG architecture
> How do I add a new agent?
> What testing framework is used?
> How do I troubleshoot installation issues?
```

## Getting Help

- **📖 [FAQ](FAQ.md)** - Common questions and answers
- **🔧 [Troubleshooting](Troubleshooting.md)** - Solve common issues
- **🐛 [Report Issues](https://github.com/Mittenzx/Adastrea-Director/issues)** - Found a bug?
- **💬 [Discussions](https://github.com/Mittenzx/Adastrea-Director/discussions)** - Ask questions

---

**Congratulations! You're now ready to use Adastrea Director!** 🎉

[← Back to Getting Started](Getting-Started.md) | [Explore Usage Guides →](../usage/Context-Aware-Assistant.md)
