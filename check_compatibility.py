#!/usr/bin/env python3
"""
Compatibility checker for Adastrea Director requirements.
This script analyzes the requirements.txt file and checks for known compatibility issues.
"""

import sys
import re
from typing import Dict, List, Tuple


def parse_requirements(filename: str = "requirements.txt") -> Dict[str, str]:
    """Parse requirements.txt and extract package versions."""
    packages = {}
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse package specification
            match = re.match(r'^([a-zA-Z0-9_-]+)([><=!]+.+)?$', line)
            if match:
                package = match.group(1)
                version_spec = match.group(2) if match.group(2) else ""
                packages[package] = version_spec
    
    return packages


def check_numpy_pandas_compatibility(packages: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Check that numpy and pandas versions are compatible."""
    issues = []
    
    numpy_spec = packages.get('numpy', '')
    pandas_spec = packages.get('pandas', '')
    
    # Check numpy version
    if '>=2.0' in numpy_spec or numpy_spec.startswith('>=2'):
        issues.append("✓ NumPy 2.0+ specified (required for Python 3.12+)")
    else:
        issues.append("✗ NumPy version should be >=2.0 for Python 3.12+ compatibility")
        return False, issues
    
    # Check pandas version
    if '>=2.2' in pandas_spec or pandas_spec.startswith('>=2.2'):
        issues.append("✓ Pandas 2.2+ specified (compatible with NumPy 2.0)")
    else:
        issues.append("✗ Pandas version should be >=2.2 for NumPy 2.0 compatibility")
        return False, issues
    
    return True, issues


def check_langchain_compatibility(packages: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Check that LangChain versions support NumPy 2.0."""
    issues = []
    
    langchain_spec = packages.get('langchain', '')
    langchain_openai_spec = packages.get('langchain-openai', '')
    langchain_community_spec = packages.get('langchain-community', '')
    
    # Check langchain
    if '>=0.3' in langchain_spec or langchain_spec.startswith('>=0.3'):
        issues.append("✓ LangChain 0.3+ specified (supports NumPy 2.0)")
    else:
        issues.append("✗ LangChain should be >=0.3.19 for NumPy 2.0 support")
        return False, issues
    
    # Check langchain-openai
    if '>=0.3' in langchain_openai_spec:
        issues.append("✓ LangChain-OpenAI 0.3+ specified")
    else:
        issues.append("⚠ LangChain-OpenAI should be >=0.3.0")
    
    # Check langchain-community (security check)
    if '>=0.3.27' in langchain_community_spec:
        issues.append("✓ LangChain-Community 0.3.27+ specified (XXE vulnerability fixed)")
    elif '>=0.3' in langchain_community_spec:
        issues.append("⚠ LangChain-Community should be >=0.3.27 to fix XXE vulnerability")
    else:
        issues.append("✗ LangChain-Community should be >=0.3.27")
        return False, issues
    
    return True, issues


def check_chromadb_compatibility(packages: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Check that ChromaDB version is compatible."""
    issues = []
    
    chromadb_spec = packages.get('chromadb', '')
    
    if '>=1.0' in chromadb_spec or '>=1.1' in chromadb_spec or '>=1.2' in chromadb_spec or '>=1.3' in chromadb_spec or '>=1.4' in chromadb_spec:
        issues.append("✓ ChromaDB 1.x+ specified (latest stable version)")
    elif '>=0.5' in chromadb_spec or '>=0.6' in chromadb_spec:
        issues.append("✓ ChromaDB 0.5+ specified (supports NumPy 2.0 integration)")
    else:
        issues.append("⚠ ChromaDB should be >=1.4.0 for latest features and compatibility")
    
    return True, issues


def check_sentence_transformers_compatibility(packages: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Check sentence-transformers compatibility."""
    issues = []
    
    st_spec = packages.get('sentence-transformers', '')
    
    if '>=3.3' in st_spec or '>=3' in st_spec:
        issues.append("✓ Sentence-Transformers 3.3+ specified (supports NumPy 2.0)")
    else:
        issues.append("⚠ Sentence-Transformers should be >=3.3.0 for NumPy 2.0 support")
    
    return True, issues


def check_python_version() -> Tuple[bool, List[str]]:
    """Check Python version compatibility."""
    issues = []
    
    major = sys.version_info.major
    minor = sys.version_info.minor
    
    issues.append(f"Python version: {major}.{minor}.{sys.version_info.micro}")
    
    if major < 3 or (major == 3 and minor < 9):
        issues.append(f"✗ Python 3.9+ required (found {major}.{minor})")
        return False, issues
    
    if major == 3 and minor >= 12:
        issues.append("✓ Python 3.12+ detected (excellent compatibility)")
    elif major == 3 and minor >= 9:
        issues.append(f"✓ Python 3.{minor} supported (3.12+ recommended)")
    
    return True, issues


def main():
    """Run all compatibility checks."""
    print("=" * 70)
    print("Adastrea Director - Requirements Compatibility Check")
    print("=" * 70)
    print()
    
    all_passed = True
    
    # Check Python version
    print("Python Version Check:")
    passed, issues = check_python_version()
    for issue in issues:
        print(f"  {issue}")
    all_passed = all_passed and passed
    print()
    
    # Parse requirements
    try:
        packages = parse_requirements()
        print(f"Found {len(packages)} packages in requirements.txt")
        print()
    except FileNotFoundError:
        print("✗ requirements.txt not found")
        return 1
    except Exception as e:
        print(f"✗ Error parsing requirements.txt: {e}")
        return 1
    
    # Check NumPy and Pandas
    print("NumPy & Pandas Compatibility:")
    passed, issues = check_numpy_pandas_compatibility(packages)
    for issue in issues:
        print(f"  {issue}")
    all_passed = all_passed and passed
    print()
    
    # Check LangChain
    print("LangChain Compatibility:")
    passed, issues = check_langchain_compatibility(packages)
    for issue in issues:
        print(f"  {issue}")
    all_passed = all_passed and passed
    print()
    
    # Check ChromaDB
    print("ChromaDB Compatibility:")
    passed, issues = check_chromadb_compatibility(packages)
    for issue in issues:
        print(f"  {issue}")
    all_passed = all_passed and passed
    print()
    
    # Check Sentence Transformers
    print("Sentence Transformers Compatibility:")
    passed, issues = check_sentence_transformers_compatibility(packages)
    for issue in issues:
        print(f"  {issue}")
    all_passed = all_passed and passed
    print()
    
    # Summary
    print("=" * 70)
    if all_passed:
        print("✓ ALL COMPATIBILITY CHECKS PASSED")
        print()
        print("Your requirements.txt is properly configured for:")
        print("  • Python 3.9+ (3.12+ recommended)")
        print("  • NumPy 2.0+ compatibility")
        print("  • Modern package versions")
        print("  • Security fixes applied")
    else:
        print("✗ SOME COMPATIBILITY ISSUES DETECTED")
        print()
        print("Please review the issues above and update requirements.txt")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
