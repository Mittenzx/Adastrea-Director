#!/usr/bin/env python3
"""
Validation script for Adastrea game repository ingestion setup.

This script checks:
1. Python version compatibility
2. Required dependencies installation
3. Internet connectivity (for first-time model download)
4. HuggingFace cache status
5. Database existence and accessibility
6. Ingestion tracking file
7. Plugin configuration guidance (informational)

Usage:
    python3 validate_game_ingestion.py
"""

import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def check_python_version():
    """Check if Python version is compatible."""
    print_header("1. Checking Python Version")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and 9 <= version.minor <= 12:
        print_success(f"Python {version_str} is compatible")
        return True
    elif version.major == 3 and version.minor >= 13:
        print_error(f"Python {version_str} is NOT supported (3.13+ not compatible with onnxruntime)")
        print_warning("Please use Python 3.9-3.12")
        return False
    else:
        print_error(f"Python {version_str} is NOT supported")
        print_warning("Please use Python 3.9-3.12")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print_header("2. Checking Dependencies")
    
    required_packages = [
        ('langchain', 'langchain'),
        ('langchain_community', 'langchain-community'),
        ('chromadb', 'chromadb'),
        ('sentence_transformers', 'sentence-transformers'),
        ('dotenv', 'python-dotenv'),
        ('rich', 'rich'),
    ]
    
    all_installed = True
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print_success(f"{package_name} installed")
        except ImportError:
            print_error(f"{package_name} NOT installed")
            all_installed = False
    
    if not all_installed:
        print_warning("\nInstall missing dependencies:")
        print_warning("  pip install -r requirements.txt")
        return False
    
    return True

def check_internet_connectivity():
    """Check if HuggingFace is accessible."""
    print_header("3. Checking Internet Connectivity")
    
    try:
        import socket
        socket.create_connection(("huggingface.co", 443), timeout=5)
        print_success("Can reach huggingface.co (required for first-time model download)")
        return True
    except (socket.error, socket.timeout):
        print_warning("Cannot reach huggingface.co")
        print_warning("First-time ingestion requires internet access to download embedding model")
        print_warning("Alternative: Use OpenAI embeddings (see Documentation/guides/GAME_REPO_INGESTION_GUIDE.md)")
        return False

def check_huggingface_cache():
    """Check if HuggingFace model is already cached."""
    print_header("4. Checking HuggingFace Cache")
    
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    
    if not cache_dir.exists():
        print_warning("No HuggingFace cache found")
        print_warning("First ingestion will download ~90MB model from huggingface.co")
        return False
    
    # Look for any cached models
    cached_models = list(cache_dir.glob("models--*"))
    if cached_models:
        print_success(f"Found {len(cached_models)} cached model(s)")
        for model in cached_models:
            print(f"  - {model.name}")
        return True
    else:
        print_warning("HuggingFace cache directory exists but no models cached")
        print_warning("First ingestion will download model")
        return False

def check_database():
    """Check if database exists and is accessible."""
    print_header("5. Checking Database")
    
    db_path = Path("./chroma_db_adastrea")
    
    if not db_path.exists():
        print_warning("Database not found at: ./chroma_db_adastrea")
        print_warning("Run ingestion to create database:")
        print_warning("  ./quick_ingest_game.sh")
        print_warning("  OR: python3 ingest_game_repo.py")
        return False
    
    # Check if database has content
    if not any(db_path.iterdir()):
        print_warning("Database directory exists but is empty")
        return False
    
    print_success(f"Database found at: {db_path.absolute()}")
    
    # Try to check database size (non-fatal if this fails)
    try:
        size_bytes = sum(f.stat().st_size for f in db_path.rglob('*') if f.is_file())
        size_mb = size_bytes / (1024 * 1024)
        print(f"  Size: {size_mb:.1f} MB")
    except Exception as e:
        print_warning(f"Could not determine database size: {e}")
    
    return True

def check_tracking_file():
    """Check if ingestion tracking file exists."""
    print_header("6. Checking Ingestion Tracking")
    
    tracking_file = Path(".adastrea_ingestion_tracking.json")
    
    if not tracking_file.exists():
        print_warning("Tracking file not found")
        print_warning("This is normal if ingestion hasn't been run yet")
        return False
    
    try:
        import json
        with open(tracking_file) as f:
            data = json.load(f)
        
        print_success("Tracking file found")
        print(f"  Last commit: {data.get('last_commit', 'N/A')}")
        print(f"  Last ingestion: {data.get('last_ingestion_time', 'N/A')}")
        print(f"  Documents: {data.get('document_count', 0)}")
        print(f"  Chunks: {data.get('chunk_count', 0)}")
        return True
    except Exception as e:
        print_warning(f"Tracking file exists but couldn't read it: {e}")
        return False

def check_plugin_config():
    """Provide plugin configuration guidance."""
    print_header("7. Plugin Configuration")
    
    print("For plugin integration, use these settings:")
    print(f"  Database Path: {Colors.GREEN}./chroma_db_adastrea{Colors.END}")
    print(f"  Collection Name: {Colors.GREEN}adastrea_game_docs{Colors.END}")
    print("")
    print("To test queries:")
    print(f"  1. Open Adastrea Director panel in Unreal Editor")
    print(f"  2. Configure the above paths")
    print(f"  3. Try query: 'What is the Adastrea game about?'")

def main():
    """Run all validation checks."""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" * 60)
    print("  Adastrea Game Repository Ingestion - Setup Validation")
    print("=" * 60)
    print(f"{Colors.END}")
    
    results = {
        'python': check_python_version(),
        'deps': check_dependencies(),
        'internet': check_internet_connectivity(),
        'cache': check_huggingface_cache(),
        'database': check_database(),
        'tracking': check_tracking_file(),
    }
    
    check_plugin_config()
    
    # Summary
    print_header("Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    if passed == total:
        print_success(f"All checks passed ({passed}/{total})! System is ready.")
    elif results['python'] and results['deps']:
        print_warning(f"Basic requirements met ({passed}/{total} checks passed)")
        
        if not results['database']:
            print_warning("\nNext step: Run ingestion to create database")
            # Check if quick_ingest_game.sh exists
            if Path("quick_ingest_game.sh").exists():
                print_warning("  ./quick_ingest_game.sh")
            else:
                print_warning("  python3 ingest_game_repo.py")
        
        if not results['internet'] and not results['cache']:
            print_warning("\nNote: First ingestion requires internet access")
            print_warning("See Documentation/guides/GAME_REPO_INGESTION_GUIDE.md for alternatives")
    else:
        print_error(f"Some critical checks failed ({passed}/{total} passed)")
        print_error("Fix the errors above before proceeding")
    
    print("")
    print("For detailed help, see:")
    print("  - Documentation/guides/GAME_REPO_INGESTION_GUIDE.md (comprehensive guide)")
    print("  - Plugins/AdastreaDirector/Documentation/guides/QUICK_INGESTION_GUIDE.md (quick reference)")
    print("")
    
    sys.exit(0 if passed >= 4 else 1)

if __name__ == "__main__":
    main()
