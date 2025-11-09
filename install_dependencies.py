#!/usr/bin/env python3
"""
Smart dependency installer for Adastrea Director.
Detects platform and provides guidance for installing dependencies.
"""

import sys
import platform
import subprocess
from typing import Tuple, List


def get_platform_info() -> Tuple[str, str, str]:
    """Get platform information."""
    system = platform.system()  # Linux, Darwin, Windows
    machine = platform.machine()  # x86_64, arm64, AMD64, etc.
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    return system, machine, python_version


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    if sys.version_info < (3, 9):
        print(f"❌ Python 3.9+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        return False
    return True


def is_apple_silicon() -> bool:
    """Check if running on Apple Silicon."""
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def is_linux_arm() -> bool:
    """Check if running on Linux ARM."""
    return platform.system() == "Linux" and "arm" in platform.machine().lower()


def is_windows_arm() -> bool:
    """Check if running on Windows ARM."""
    return platform.system() == "Windows" and "arm" in platform.machine().lower()


def print_platform_warning():
    """Print platform-specific warnings and recommendations."""
    system, machine, python_version = get_platform_info()
    
    print(f"\n{'='*70}")
    print("Adastrea Director - Dependency Installer")
    print(f"{'='*70}\n")
    print(f"Platform: {system} {machine}")
    print(f"Python: {python_version}")
    
    if is_apple_silicon():
        print("\n⚠️  Apple Silicon (M1/M2/M3/M4) detected!")
        print("\nYou may encounter issues with onnxruntime (required by ChromaDB).")
        print("\nRecommended solutions:")
        print("1. Use Rosetta 2 with x86_64 Python (most compatible)")
        print("2. Use onnxruntime-silicon package")
        print("3. Use Docker with ChromaDB server")
        print("\nFor detailed instructions, see: INSTALLATION.md")
        print(f"\n{'='*70}\n")
        
        response = input("Would you like to:\n"
                        "  [1] Try standard installation (may fail)\n"
                        "  [2] Exit and follow INSTALLATION.md guide\n"
                        "Choice (1 or 2): ").strip()
        
        if response == "2":
            print("\nPlease follow the platform-specific guide in INSTALLATION.md")
            print("Summary for Apple Silicon:")
            print("  Option 1: arch -x86_64 /usr/local/bin/python3.12 -m venv venv")
            print("  Option 2: pip install onnxruntime-silicon, then chromadb")
            print("  Option 3: docker run -p 8000:8000 chromadb/chroma")
            return False
            
    elif is_linux_arm():
        print("\n⚠️  Linux ARM platform detected!")
        print("\nYou may need to build onnxruntime from source.")
        print("Install build tools first:")
        print("  sudo apt-get install -y python3-dev build-essential cmake")
        print("\nFor detailed instructions, see: INSTALLATION.md")
        print(f"\n{'='*70}\n")
        
    elif is_windows_arm():
        print("\n⚠️  Windows ARM platform detected!")
        print("\nYou may encounter issues with onnxruntime.")
        print("Consider using Docker or x86 emulation.")
        print("\nFor detailed instructions, see: INSTALLATION.md")
        print(f"\n{'='*70}\n")
    else:
        print("\n✅ Standard platform detected - installation should work smoothly.")
        print(f"\n{'='*70}\n")
    
    return True


def install_requirements():
    """Install requirements using pip."""
    print("Installing dependencies from requirements.txt...")
    print("This may take several minutes...\n")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("\n✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed with error code {e.returncode}")
        print("\nTroubleshooting steps:")
        
        system, machine, _ = get_platform_info()
        
        if is_apple_silicon():
            print("\n🍎 Apple Silicon specific solutions:")
            print("1. Install onnxruntime-silicon:")
            print("   pip install onnxruntime-silicon>=1.14.0")
            print("   pip install chromadb>=0.5.23,<0.6.0")
            print("\n2. Use Rosetta 2 (see INSTALLATION.md)")
            print("\n3. Use Docker (see INSTALLATION.md)")
        elif is_linux_arm() or is_windows_arm():
            print("\n🔧 ARM platform solutions:")
            print("1. Build from source:")
            print("   pip install --no-binary onnxruntime onnxruntime>=1.14.1")
            print("\n2. Use Docker (see INSTALLATION.md)")
        else:
            print("\n🔍 General troubleshooting:")
            print("1. Upgrade pip: pip install --upgrade pip")
            print("2. Check Python version: python --version (need 3.9+)")
            print("3. See INSTALLATION.md for detailed troubleshooting")
        
        print(f"\nFor complete platform-specific guide, see: INSTALLATION.md")
        return False


def verify_installation():
    """Verify that key packages can be imported."""
    print("\n" + "="*70)
    print("Verifying installation...")
    print("="*70 + "\n")
    
    critical_packages = [
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("langchain", "LangChain"),
        ("openai", "OpenAI"),
        ("chromadb", "ChromaDB"),
    ]
    
    all_success = True
    
    for module_name, display_name in critical_packages:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
        except ImportError as e:
            print(f"❌ {display_name}: {e}")
            all_success = False
    
    print("\n" + "="*70)
    if all_success:
        print("✅ All critical packages verified successfully!")
        print("\nYou can now run:")
        print("  python check_compatibility.py    # Run compatibility checks")
        print("  python validate_requirements.py  # Detailed validation")
        print("  python main.py                   # Start the CLI")
        print("  python gui_director.py           # Start the GUI")
    else:
        print("❌ Some packages failed to import")
        print("\nPlease review the errors above and:")
        print("1. Check INSTALLATION.md for platform-specific solutions")
        print("2. Verify all dependencies installed: pip list")
        print("3. Try reinstalling: pip install -r requirements.txt")
    print("="*70 + "\n")
    
    return all_success


def main():
    """Main installation flow."""
    # Check Python version
    if not check_python_version():
        return 1
    
    # Print platform info and warnings
    if not print_platform_warning():
        return 0
    
    # Ask user if they want to proceed
    response = input("Proceed with installation? (y/n): ").strip().lower()
    if response not in ['y', 'yes']:
        print("\nInstallation cancelled.")
        print("See INSTALLATION.md for manual installation instructions.")
        return 0
    
    print()
    
    # Install requirements
    if not install_requirements():
        return 1
    
    # Verify installation
    if not verify_installation():
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
