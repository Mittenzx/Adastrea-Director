#!/bin/bash
# Quick setup script for Adastrea Director
# This script checks your system and guides you through installation

set -e

echo "=================================================="
echo "  Adastrea Director - Quick Setup"
echo "=================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.9+ from https://www.python.org/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "✅ Python $PYTHON_VERSION found"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "❌ Python 3.9+ required (found $PYTHON_VERSION)"
    echo "Please upgrade Python from https://www.python.org/"
    exit 1
fi

echo "✅ Python version is compatible"
echo ""

# Check platform
PLATFORM=$(uname -s)
ARCH=$(uname -m)

echo "Platform: $PLATFORM"
echo "Architecture: $ARCH"
echo ""

# Detect potential issues
POTENTIAL_ISSUES=false

if [ "$PLATFORM" = "Darwin" ] && [ "$ARCH" = "arm64" ]; then
    echo "⚠️  Apple Silicon (M1/M2/M3/M4) detected"
    echo "    You may need special installation steps"
    POTENTIAL_ISSUES=true
fi

if [ "$PLATFORM" = "Linux" ] && [[ "$ARCH" == arm* ]]; then
    echo "⚠️  Linux ARM detected"
    echo "    You may need to build some packages from source"
    POTENTIAL_ISSUES=true
fi

if [ "$POTENTIAL_ISSUES" = true ]; then
    echo ""
    echo "IMPORTANT: Please use the smart installer:"
    echo "  python3 install_dependencies.py"
    echo ""
    echo "Or see INSTALLATION.md for detailed platform-specific instructions"
    echo ""
    read -p "Continue with automatic setup? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Please follow INSTALLATION.md"
        exit 0
    fi
fi

echo ""
echo "=================================================="
echo "  Step 1: Create Virtual Environment"
echo "=================================================="
echo ""

if [ -d "venv" ]; then
    echo "Virtual environment already exists"
    read -p "Recreate it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing old virtual environment..."
        rm -rf venv
    fi
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

echo ""
echo "=================================================="
echo "  Step 2: Activate Virtual Environment"
echo "=================================================="
echo ""

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    echo "To activate the virtual environment, run:"
    echo "  source venv/bin/activate"
    echo ""
    echo "Activating now..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
elif [ -f "venv/Scripts/activate" ]; then
    echo "To activate the virtual environment, run:"
    echo "  source venv/Scripts/activate"
    echo ""
    echo "Activating now..."
    source venv/Scripts/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Could not find activation script"
    exit 1
fi

echo ""
echo "=================================================="
echo "  Step 3: Upgrade pip"
echo "=================================================="
echo ""

pip install --upgrade pip
echo "✅ pip upgraded"

echo ""
echo "=================================================="
echo "  Step 4: Install Dependencies"
echo "=================================================="
echo ""

if [ "$POTENTIAL_ISSUES" = true ]; then
    echo "Using smart installer for platform-specific handling..."
    python install_dependencies.py
else
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
fi

echo ""
echo "=================================================="
echo "  Step 5: Verify Installation"
echo "=================================================="
echo ""

echo "Running compatibility check..."
python check_compatibility.py

echo ""
echo "=================================================="
echo "  Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Set up your OpenAI API key:"
echo "   export OPENAI_API_KEY=\"your-api-key-here\""
echo "   # Or create a .env file with OPENAI_API_KEY=your-key"
echo ""
echo "2. Ingest your project documents:"
echo "   python ingest.py --docs-dir /path/to/your/docs"
echo ""
echo "3. Start using Adastrea Director:"
echo "   python main.py           # Command-line interface"
echo ""
echo "For troubleshooting, see TROUBLESHOOTING.md"
echo "=================================================="
