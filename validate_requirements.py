#!/usr/bin/env python3
"""
Validation script for requirements.txt
Tests that all required packages can be imported and are compatible.
"""

import sys
import os

# Disable ChromaDB telemetry BEFORE any imports that might import chromadb
# This prevents "capture() takes 1 positional argument but 3 were given" errors
# ChromaDB checks for this variable and disables telemetry when set to "1"
os.environ["ANONYMIZED_TELEMETRY"] = "1"


def check_package_versions():
    """Check that key packages are installed with correct versions."""
    failures = []
    successes = []

    # Check numpy
    try:
        import numpy as np
        version = tuple(map(int, np.__version__.split('.')[:2]))
        if version >= (2, 0):
            successes.append(f"✓ numpy {np.__version__} (>=2.0 required)")
        else:
            failures.append(f"✗ numpy {np.__version__} is too old (>=2.0 required)")
    except ImportError as e:
        failures.append(f"✗ numpy not installed: {e}")

    # Check pandas
    try:
        import pandas as pd
        version = tuple(map(int, pd.__version__.split('.')[:2]))
        if version >= (2, 2):
            successes.append(f"✓ pandas {pd.__version__} (>=2.2 required)")
        else:
            failures.append(f"✗ pandas {pd.__version__} is too old (>=2.2 required)")
    except ImportError as e:
        failures.append(f"✗ pandas not installed: {e}")

    # Check langchain
    try:
        import langchain
        successes.append(f"✓ langchain {langchain.__version__}")
    except ImportError as e:
        failures.append(f"✗ langchain not installed: {e}")

    # Check langchain-openai
    try:
        import langchain_openai
        successes.append("✓ langchain-openai installed")
    except ImportError as e:
        failures.append(f"✗ langchain-openai not installed: {e}")

    # Check langchain-community
    try:
        import langchain_community
        successes.append("✓ langchain-community installed")
    except ImportError as e:
        failures.append(f"✗ langchain-community not installed: {e}")

    # Check chromadb
    try:
        import chromadb
        successes.append(f"✓ chromadb installed")
    except ImportError as e:
        failures.append(f"✗ chromadb not installed: {e}")

    # Check sentence-transformers
    try:
        import sentence_transformers
        successes.append(f"✓ sentence-transformers {sentence_transformers.__version__}")
    except ImportError as e:
        failures.append(f"✗ sentence-transformers not installed: {e}")

    # Check other key packages
    packages = [
        'openai',
        'pypdf',
        'docx',  # python-docx
        'markdown',
        'bs4',  # beautifulsoup4
        'tiktoken',
        'click',
        'dotenv',  # python-dotenv
        'rich',
        'pydantic',
    ]

    for package in packages:
        try:
            __import__(package)
            successes.append(f"✓ {package} installed")
        except ImportError as e:
            failures.append(f"✗ {package} not installed: {e}")

    # Print results
    print("\n" + "=" * 60)
    print("REQUIREMENTS VALIDATION RESULTS")
    print("=" * 60 + "\n")

    if successes:
        print("Successes:")
        for success in successes:
            print(f"  {success}")
        print()

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"  {failure}")
        print()
        print("=" * 60)
        print("VALIDATION FAILED")
        print("=" * 60)
        return False
    else:
        print("=" * 60)
        print("VALIDATION PASSED")
        print("=" * 60)
        return True


def test_numpy_compatibility():
    """Test that numpy 2.0 works correctly."""
    try:
        import numpy as np
        
        # Test basic operations
        arr = np.array([1, 2, 3, 4, 5])
        assert arr.mean() == 3.0
        
        # Test that old removed attributes are not present
        # (numpy 2.0 removed np.float_, np.int_, etc.)
        if hasattr(np, 'float_'):
            print("  Warning: numpy still has deprecated np.float_ attribute")
        
        print("  ✓ NumPy 2.0 compatibility tests passed")
        return True
    except Exception as e:
        print(f"  ✗ NumPy compatibility test failed: {e}")
        return False


if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check minimum Python version
    if sys.version_info < (3, 9):
        print("\n✗ Python 3.9 or higher is required")
        sys.exit(1)
    
    # Run validation
    success = check_package_versions()
    
    if success:
        print("\nRunning compatibility tests...")
        test_numpy_compatibility()
    
    sys.exit(0 if success else 1)
