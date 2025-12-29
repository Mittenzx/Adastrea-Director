#!/usr/bin/env python3
"""
Test script to verify game repository ingestion infrastructure is ready.

This script checks that all necessary components for game repository ingestion
are in place and working correctly.

Usage:
    python3 test_ingestion_infrastructure.py
"""

import os
import sys
from pathlib import Path


def print_test(name, passed, details=""):
    """Print test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"        {details}")


def test_python_version():
    """Check Python version is compatible."""
    version = sys.version_info
    is_compatible = version.major == 3 and 9 <= version.minor <= 13
    print_test(
        "Python version compatibility",
        is_compatible,
        f"Python {version.major}.{version.minor}.{version.micro}"
    )
    return is_compatible


def test_script_files_exist():
    """Check that ingestion scripts exist."""
    scripts = [
        "ingest_game_repo.py",
        "ingest.py",
        "quick_ingest_game.sh",
        "validate_game_ingestion.py"
    ]
    
    missing_scripts = []
    for script in scripts:
        exists = Path(script).exists()
        print_test(f"Script exists: {script}", exists)
        if not exists:
            missing_scripts.append(script)
    
    all_scripts_exist = not missing_scripts
    return all_scripts_exist


def test_documentation_exists():
    """Check that documentation files exist."""
    docs = [
        "Documentation/guides/GAME_REPO_INGESTION_GUIDE.md",
        "Documentation/guides/START_HERE_INGESTION.md",
        "Documentation/development/INGESTION_STATUS.md",
        "Documentation/implementation/INGESTION_IMPLEMENTATION_SUMMARY.md"
    ]
    
    missing_docs = []
    for doc in docs:
        exists = Path(doc).exists()
        print_test(f"Documentation exists: {doc}", exists)
        if not exists:
            missing_docs.append(doc)
    
    all_docs_exist = not missing_docs
    return all_docs_exist


def test_dependencies_installed():
    """Check that required dependencies are installed."""
    dependencies = [
        ("langchain", "langchain"),
        ("langchain_community", "langchain-community"),
        ("chromadb", "chromadb"),
        ("sentence_transformers", "sentence-transformers"),
        ("rich", "rich"),
        ("python-dotenv", "dotenv"),
    ]
    
    all_installed = True
    for package_name, import_name in dependencies:
        try:
            if package_name == "python-dotenv":
                __import__("dotenv")
            else:
                __import__(import_name.replace("-", "_"))
            print_test(f"Dependency installed: {package_name}", True)
        except ImportError:
            print_test(f"Dependency installed: {package_name}", False, "Not installed")
            all_installed = False
    
    return all_installed


def test_script_is_executable():
    """Check that shell scripts are executable."""
    script = Path("quick_ingest_game.sh")
    if not script.exists():
        print_test("quick_ingest_game.sh is executable", False, "File not found")
        return False
    
    is_executable = os.access(script, os.X_OK)
    print_test("quick_ingest_game.sh is executable", is_executable)
    return is_executable


def test_imports_work():
    """Check that key imports from the ingestion script work."""
    try:
        # Disable ChromaDB telemetry before import
        # ChromaDB checks for this variable and any truthy value disables telemetry
        os.environ["ANONYMIZED_TELEMETRY"] = "1"
        
        # Try importing the DocumentIngestionAgent
        from ingest import DocumentIngestionAgent
        print_test("Can import DocumentIngestionAgent", True)
        return True
    except Exception as e:
        print_test("Can import DocumentIngestionAgent", False, str(e))
        return False


def test_environment_file_exists():
    """Check that environment example file exists and contains required configuration."""
    env_file = Path(".env.example")
    exists = env_file.exists()
    print_test(".env.example exists", exists)
    
    if not exists:
        return False
    
    content = env_file.read_text()
    has_embedding = "EMBEDDING_PROVIDER" in content
    has_huggingface = "HUGGINGFACE" in content
    has_config = has_embedding and has_huggingface
    print_test("Contains embedding configuration", has_config)
    
    return has_config


def main():
    """Run all infrastructure tests."""
    print("=" * 70)
    print("Game Repository Ingestion Infrastructure Test")
    print("=" * 70)
    print()
    
    results = []
    
    print("1. Python Environment")
    print("-" * 70)
    results.append(test_python_version())
    print()
    
    print("2. Core Script Files")
    print("-" * 70)
    results.append(test_script_files_exist())
    print()
    
    print("3. Documentation Files")
    print("-" * 70)
    results.append(test_documentation_exists())
    print()
    
    print("4. Dependencies")
    print("-" * 70)
    results.append(test_dependencies_installed())
    print()
    
    print("5. Script Permissions")
    print("-" * 70)
    results.append(test_script_is_executable())
    print()
    
    print("6. Code Imports")
    print("-" * 70)
    results.append(test_imports_work())
    print()
    
    print("7. Configuration")
    print("-" * 70)
    results.append(test_environment_file_exists())
    print()
    
    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - Infrastructure is ready!")
        print("\nNext steps:")
        print("1. Ensure you have internet access to HuggingFace")
        print("2. Run: ./quick_ingest_game.sh")
        print("3. Or run: python3 ingest_game_repo.py")
        print("\nSee INGESTION_STATUS.md for detailed usage instructions.")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        print("\nPlease address the failed tests before running ingestion.")
        print("See the test output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
