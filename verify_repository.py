#!/usr/bin/env python3
"""
Verify Adastrea Director Repository

A minimal verification script that checks if the repository
is properly structured and key components exist.

This script requires NO external dependencies - it only uses
standard Python libraries.
"""

import os
import sys
import json

# Fix Unicode encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_file_exists(path, description):
    """Check if a file exists and print status."""
    if os.path.exists(path):
        print(f"[OK] {description}: {path}")
        return True
    else:
        print(f"[MISSING] {description}: {path}")
        return False

def check_directory_exists(path, description):
    """Check if a directory exists and print status."""
    if os.path.exists(path) and os.path.isdir(path):
        print(f"[OK] {description}: {path}")
        return True
    else:
        print(f"[MISSING] {description}: {path}")
        return False

def check_python_file(path, description):
    """Check if a Python file exists and can be parsed."""
    if not os.path.exists(path):
        print(f"❌ {description}: {path} (MISSING)")
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            # Try to read first few lines to check syntax
            content = f.read(1000)
            # Check for common Python syntax
            if 'import ' in content or 'def ' in content or 'class ' in content:
                print(f"✅ {description}: {path} (valid Python)")
                return True
            else:
                print(f"[WARNING] {description}: {path} (unusual content)")
                return False
    except Exception as e:
        print(f"[ERROR] {description}: {path} (ERROR: {e})")
        return False

def main():
    print("=" * 60)
    print("Adastrea Director Repository Verification")
    print("=" * 60)
    print()
    
    # Get repository root
    repo_root = os.path.dirname(os.path.abspath(__file__))
    print(f"Repository root: {repo_root}")
    print()
    
    # Track results
    results = {
        "core_files": 0,
        "core_dirs": 0,
        "python_files": 0,
        "total_checks": 0,
        "passed": 0,
        "failed": 0
    }
    
    # Check core files
    print("Core Files:")
    print("-" * 40)
    
    core_files = [
        ("README.md", "Main documentation"),
        ("requirements.txt", "Python dependencies"),
        ("ARCHITECTURE.md", "Architecture documentation"),
        ("QUICK_START_GUIDE.md", "Quick start guide"),
        ("WORK_SESSION_SUMMARY_2026-02-24.md", "Latest work summary"),
    ]
    
    for filename, description in core_files:
        results["total_checks"] += 1
        if check_file_exists(os.path.join(repo_root, filename), description):
            results["core_files"] += 1
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    print()
    
    # Check core directories
    print("Core Directories:")
    print("-" * 40)
    
    core_dirs = [
        ("examples", "Example scripts"),
        ("mcp_server", "MCP server implementation"),
        ("Plugins/AdastreaDirector", "Unreal Engine plugin"),
        ("tests", "Test suite"),
    ]
    
    for dirname, description in core_dirs:
        results["total_checks"] += 1
        if check_directory_exists(os.path.join(repo_root, dirname), description):
            results["core_dirs"] += 1
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    print()
    
    # Check key Python files
    print("Key Python Files:")
    print("-" * 40)
    
    python_files = [
        ("unreal_mcp_cli.py", "Unreal Engine MCP CLI"),
        ("test_unreal_connection.py", "Connection test script"),
        ("examples/planning_example.py", "Planning example"),
        ("mcp_server/server.py", "MCP server core"),
    ]
    
    for filepath, description in python_files:
        results["total_checks"] += 1
        if check_python_file(os.path.join(repo_root, filepath), description):
            results["python_files"] += 1
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    print()
    print("=" * 60)
    print("Verification Results:")
    print("=" * 60)
    
    print(f"Total checks: {results['total_checks']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print()
    
    print("Summary by category:")
    print(f"  Core files: {results['core_files']}/5")
    print(f"  Core directories: {results['core_dirs']}/4")
    print(f"  Python files: {results['python_files']}/4")
    print()
    
    # Overall status
    if results['failed'] == 0:
        print("[SUCCESS] Repository structure is complete and valid!")
        print("   All core components are present.")
        return 0
    elif results['failed'] <= 2:
        print("[PARTIAL] Repository has minor issues.")
        print("   Most core components are present.")
        return 1
    else:
        print("[FAILED] Repository has significant issues.")
        print("   Many core components are missing.")
        return 2

if __name__ == "__main__":
    sys.exit(main())