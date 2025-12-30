#!/bin/bash
# Test installation script for updated dependencies
# This script tests that all packages can be installed and work together

set -e  # Exit on error

echo "=========================================="
echo "Testing Adastrea Director Requirements"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $PYTHON_VERSION"

MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 9 ]); then
    echo "ERROR: Python 3.9 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 12 ]; then
    echo "✓ Python $PYTHON_VERSION is compatible (3.12+ recommended)"
else
    echo "✓ Python $PYTHON_VERSION is supported (3.12+ recommended for best compatibility)"
fi
echo ""

# Create virtual environment
echo "Creating test virtual environment..."
if [ -d "venv_test" ]; then
    echo "Removing existing test environment..."
    rm -rf venv_test
fi

python3 -m venv venv_test
source venv_test/bin/activate

echo "✓ Virtual environment created"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"
echo ""

# Install requirements
echo "Installing requirements..."
echo "This may take several minutes..."
if pip install -r requirements.txt; then
    echo "✓ Requirements installed successfully"
else
    echo "✗ Failed to install requirements"
    deactivate
    exit 1
fi
echo ""

# Run validation script
echo "Running validation script..."
if python validate_requirements.py; then
    echo "✓ Validation passed"
else
    echo "✗ Validation failed"
    deactivate
    exit 1
fi
echo ""

# Test basic imports
echo "Testing basic imports..."
python3 << 'EOF'
import sys

# Test numpy
import numpy as np
print(f"  ✓ numpy {np.__version__}")
assert np.__version__.startswith('2.'), f"numpy version {np.__version__} does not start with 2.x"

# Test pandas
import pandas as pd
print(f"  ✓ pandas {pd.__version__}")
version_parts = pd.__version__.split('.')
assert int(version_parts[0]) >= 2 and int(version_parts[1]) >= 2, "pandas version must be >=2.2"

# Test langchain
import langchain
print(f"  ✓ langchain {langchain.__version__}")

# Test langchain components
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
print("  ✓ langchain_openai")

from langchain_chroma import Chroma
print("  ✓ langchain_chroma")

# Test chromadb
import chromadb
print("  ✓ chromadb")

# Test sentence transformers
import sentence_transformers
print(f"  ✓ sentence_transformers {sentence_transformers.__version__}")

# Test other imports
import openai
print("  ✓ openai")

from pypdf import PdfReader
print("  ✓ pypdf")

print("\nAll imports successful!")
EOF

if [ $? -eq 0 ]; then
    echo "✓ Import tests passed"
else
    echo "✗ Import tests failed"
    deactivate
    exit 1
fi
echo ""

# Cleanup
echo "Cleaning up test environment..."
deactivate
rm -rf venv_test
echo "✓ Test environment removed"
echo ""

echo "=========================================="
echo "ALL TESTS PASSED"
echo "=========================================="
echo ""
echo "The updated requirements.txt is compatible with your Python environment."
echo "You can now install the packages in your main environment with:"
echo "  pip install -r requirements.txt"
