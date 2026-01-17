# Getting Started with Adastrea Director

Welcome! This guide will help you install and set up Adastrea Director on your system.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Quick Setup](#quick-setup)
- [Manual Installation](#manual-installation)
- [Configuration](#configuration)
- [Next Steps](#next-steps)

## System Requirements

### Minimum Requirements
- **Python:** 3.9 or higher (3.12+ recommended for best compatibility)
- **pip:** Package manager (included with Python)
- **RAM:** 4GB minimum, 8GB+ recommended
- **Storage:** 2GB free space (more for document databases)
- **OS:** Windows 10+, macOS 10.14+, Ubuntu 20.04+

### Optional Requirements
- **GitHub Token:** For private repository ingestion
- **API Keys:** For LLM providers (Gemini or OpenAI)
- **Unreal Engine:** 5.0+ (for plugin mode only)

## Installation Methods

### Method 1: Quick Setup (Recommended) ⭐

The automated setup script handles everything for you:

```bash
# Clone the repository
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director

# Run setup script (Linux/Mac)
./setup.sh

# Run setup script (Windows - use Git Bash or WSL)
bash setup.sh
```

The setup script will:
- ✅ Check system compatibility
- ✅ Create and activate virtual environment
- ✅ Install all dependencies with platform-specific handling
- ✅ Verify the installation
- ✅ Guide you through initial configuration

**💡 Tip:** The virtual environment is reusable. Simply activate it with:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Method 2: Smart Installer

If the quick setup doesn't work or you need more control:

```bash
# Clone the repository
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director

# Run the smart installer
python install_dependencies.py
```

The smart installer will:
- Detect your platform and architecture
- Handle platform-specific dependencies (especially for Apple Silicon)
- Guide you through any required manual steps
- Verify the installation

### Method 3: Manual Installation

For advanced users who want complete control:

```bash
# 1. Clone the repository
git clone https://github.com/Mittenzx/Adastrea-Director.git
cd Adastrea-Director

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python test_installation.sh
```

## Quick Setup

### 1. Install Adastrea Director

Choose one of the installation methods above. We recommend the **Quick Setup** for most users.

### 2. Configure LLM Provider

Adastrea Director supports multiple LLM providers. You have three options:

#### Option A: Save to Local Config (Recommended)

Keys are securely stored in `~/.adastrea/config.json`:

**Via CLI:**
```bash
python main.py --set-api-key gemini
# Follow the prompts and check "Save API key for future sessions"
```

#### Option B: Environment Variables

```bash
# For Gemini (recommended - free tier available)
export GEMINI_KEY="your-api-key-here"

# For OpenAI
export OPENAI_API_KEY="your-api-key-here"
```

#### Option C: .env File

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your keys
GEMINI_KEY=your-api-key-here
OPENAI_API_KEY=your-api-key-here
```

**Priority:** Local config → Environment variables → .env file

### 3. (Optional) Set Up GitHub Token

Only needed for private repository ingestion:

```bash
export GITHUB_TOKEN="your-github-token-here"
```

### 4. Verify Installation

Run a quick test to ensure everything is working:

```bash
# Test the CLI
python main.py --help
```

## Configuration

### Embeddings Configuration

**Default (No Setup Required):**
Adastrea Director uses **HuggingFace embeddings by default** (works offline, no API key needed).

**Optional - OpenAI Embeddings:**
For better quality embeddings:
1. Set `OPENAI_API_KEY` environment variable
2. Configure in settings to use OpenAI embeddings

### Document Ingestion

Before using Adastrea Director, you should populate the knowledge base:

```bash
# Ingest your project documentation
python ingest.py --docs-dir /path/to/your/docs

# For Mittenzx/Adastrea game developers
python ingest_game_repo.py
```

See the [Document Ingestion Guide](Document-Ingestion.md) for more details.

## Platform-Specific Notes

### macOS (Apple Silicon)

If you encounter issues with ARM-based dependencies:

1. Use the smart installer: `python install_dependencies.py`
2. It will guide you through any required steps for Apple Silicon compatibility

### Windows

- Use Git Bash or WSL for best compatibility with setup scripts
- tkinter is included with Python on Windows
- Some dependencies may require Visual C++ Build Tools

### Linux

**Ubuntu/Debian:**
```bash
# Install tkinter if needed
sudo apt-get install python3-tk

# Install build essentials if needed
sudo apt-get install build-essential python3-dev
```

**Fedora/CentOS:**
```bash
# Install tkinter if needed
sudo dnf install python3-tkinter
```

## Troubleshooting

### Common Issues

**Problem:** "No module named 'tkinter'"
- **Solution:** Install python3-tk package for your OS (see Platform-Specific Notes)

**Problem:** "Failed to load embeddings model"
- **Solution:** Ensure you have internet connection for first-time model download, or check your API key configuration

**Problem:** "Permission denied" when running setup.sh
- **Solution:** Make the script executable: `chmod +x setup.sh`

**Problem:** Dependencies fail to install on Apple Silicon
- **Solution:** Use the smart installer: `python install_dependencies.py`

For more troubleshooting help, see the [Troubleshooting Guide](Troubleshooting.md).

## Next Steps

Now that you have Adastrea Director installed:

1. **📚 [Quick Start Tutorial](Quick-Start.md)** - Learn the basics in 5 minutes
2. **🔍 [Context-Aware Assistant](../usage/Context-Aware-Assistant.md)** - Start asking questions about your project
3. **📋 [Planning System](../usage/Planning-System.md)** - Create implementation plans
4. **🤖 [Autonomous Agents](../usage/Autonomous-Agents.md)** - Set up proactive monitoring

## Getting Help

- **📖 [FAQ](FAQ.md)** - Frequently asked questions
- **🐛 [Report Issues](https://github.com/Mittenzx/Adastrea-Director/issues)** - Found a bug?
- **💬 [Discussions](https://github.com/Mittenzx/Adastrea-Director/discussions)** - Ask questions

---

**Next:** [Quick Start Tutorial](Quick-Start.md) →

[← Back to Home](../Home.md)
