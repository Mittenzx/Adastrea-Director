#!/usr/bin/env python3
"""
Smart dependency installer for Adastrea Director.
Detects platform and provides guidance for installing dependencies.
"""

import os
import sys
import platform
import subprocess
from typing import Tuple, Optional

# Windows-specific imports
import ctypes

MB_ICONERROR = 0x10  # MessageBox icon constant


def check_console_available() -> bool:
    """
    Check if console/stdin/stdout is available.
    Returns False if running with pythonw.exe or no console attached.
    """
    # First check for Windows pythonw.exe (cheapest check)
    if platform.system() == "Windows":
        executable = sys.executable.lower()
        if "pythonw.exe" in executable:
            return False

    # Check if stdin/stdout exist
    if not sys.stdin or not sys.stdout:
        return False

    # Try to actually use stdout
    try:
        # Test if we can write to stdout
        sys.stdout.flush()
    except (AttributeError, OSError, ValueError):
        return False

    return True


def get_platform_info() -> Tuple[str, str, str]:
    """Get platform information."""
    system = platform.system()  # Linux, Darwin, Windows
    machine = platform.machine()  # x86_64, arm64, AMD64, etc.
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    return system, machine, python_version


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version < (3, 9):
        print(f"❌ Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    if version >= (3, 13):
        print(f"⚠️  Warning: Python {version.major}.{version.minor} detected")
        print("onnxruntime may not have wheels for Python 3.13+")
        print("Python 3.9-3.12 is recommended for best compatibility")
        print("\nYou may encounter installation errors. Consider:")
        print("1. Installing Python 3.12 from https://www.python.org/")
        print(
            "2. Using Docker with ChromaDB (see the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki))"
        )
        return True  # Allow to continue but with warning
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
        print(
            "\nFor detailed instructions, see: the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki)"
        )
        print(f"\n{'='*70}\n")

        response = input(
            "Would you like to:\n"
            "  [1] Try standard installation (may fail)\n"
            "  [2] Exit and follow the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki) guide\n"
            "Choice (1 or 2): "
        ).strip()

        if response == "2":
            print(
                "\nPlease follow the platform-specific guide in the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki)"
            )
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
        print(
            "\nFor detailed instructions, see: the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki)"
        )
        print(f"\n{'='*70}\n")

    elif is_windows_arm():
        print("\n⚠️  Windows ARM platform detected!")
        print("\nYou may encounter issues with onnxruntime.")
        print("Consider using Docker or x86 emulation.")
        print(
            "\nFor detailed instructions, see: the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki)"
        )
        print(f"\n{'='*70}\n")
    else:
        print("\n✅ Standard platform detected - installation should work smoothly.")

        # Additional check for Windows with Python 3.13+
        if platform.system() == "Windows" and sys.version_info >= (3, 13):
            print("\n⚠️  Warning: Python 3.13+ on Windows")
            print("    onnxruntime may not be available for Python 3.13+")
            print("    Recommended: Use Python 3.9-3.12 for best compatibility")
            print(
                "    See the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki) for Windows-specific instructions"
            )

        print(f"\n{'='*70}\n")

    return True


def install_requirements():
    """Install requirements using pip."""
    print("Installing dependencies from requirements.txt...")
    print("This may take several minutes...\n")

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
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
            print("   pip install chromadb>=1.4.0,<2.0.0")
            print(
                "\n2. Use Rosetta 2 (see the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki))"
            )
            print(
                "\n3. Use Docker (see the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki))"
            )
        elif is_linux_arm() or is_windows_arm():
            print("\n🔧 ARM platform solutions:")
            print("1. Build from source:")
            print("   pip install --no-binary onnxruntime onnxruntime>=1.14.1")
            print(
                "\n2. Use Docker (see the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki))"
            )
        else:
            print("\n🔍 General troubleshooting:")
            print("1. Check Python version: python --version")
            if sys.version_info >= (3, 13):
                print("   ⚠️  Python 3.13+ detected - onnxruntime may not be available")
                print("   → Install Python 3.12 from https://www.python.org/")
            elif platform.system() == "Windows":
                print("   ℹ️  Windows x86_64 detected")
                print("   → If Python 3.13+: Install Python 3.12")
                print(
                    "   → Upgrade pip: python -m pip install --upgrade pip setuptools wheel"
                )
                print("   → Test: pip install --verbose onnxruntime")
            print("2. Upgrade pip: pip install --upgrade pip setuptools wheel")
            print(
                "3. See the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki) for detailed troubleshooting"
            )

        print(
            "\nFor complete platform-specific guide, see: the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki)"
        )
        return False


def verify_installation():
    """Verify that key packages can be imported."""
    print("\n" + "=" * 70)
    print("Verifying installation...")
    print("=" * 70 + "\n")

    critical_packages = [
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("langchain", "LangChain"),
        ("langchain_google_genai", "LangChain Google Gemini"),
        ("openai", "OpenAI (Legacy)"),
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

    print("\n" + "=" * 70)
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
        print(
            "1. Check the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki) for platform-specific solutions"
        )
        print("2. Verify all dependencies installed: pip list")
        print("3. Try reinstalling: pip install -r requirements.txt")
    print("=" * 70 + "\n")

    return all_success


def _log_error_safely(log_path: Optional[str], message: str) -> None:
    """
    Helper function to log errors with fallback handling.
    Tries to write to log file, then stderr, silently failing if both fail.
    """
    if log_path:
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n{message}\n")
            return
        except Exception:
            pass
    # Fallback to stderr
    try:
        sys.stderr.write(f"\n{message}\n")
    except Exception:
        # Final fallback: swallow any logging errors
        pass


def main():
    """Main installation flow."""
    # First, check if we have a console available
    if not check_console_available():
        # We can't use print() reliably here, so write to a file
        error_msg = """
ERROR: This script cannot run with pythonw.exe (no console available).

This installer requires user interaction and must be run from a console.

How to fix:
1. Open Command Prompt (cmd.exe) or PowerShell
2. Navigate to the Adastrea-Director folder
3. Run: python install_dependencies.py
   (Use 'python' not 'pythonw')

Alternative: Double-click requires console
If you're double-clicking this script and seeing this error:
- Windows may be using pythonw.exe by default
- Solution: Right-click the file → Edit with IDLE → Run → Run Module
  OR open cmd.exe first, then run the command above

For more help, see: https://github.com/Mittenzx/Adastrea-Director/wiki
"""
        # Get absolute path for log file (define early to avoid NameError)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(script_dir, "install_dependencies_error.log")

        try:
            # Try to write error to a log file
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(error_msg)
            # Try to display a message box on Windows
            if platform.system() == "Windows":
                try:
                    ctypes.windll.user32.MessageBoxW(
                        0,
                        "This installer must be run from Command Prompt or PowerShell, not by double-clicking.\n\n"
                        "Please open Command Prompt and run:\n"
                        "python install_dependencies.py\n\n"
                        f"See error log for details:\n{log_path}",
                        "Adastrea Director - Installation Error",
                        MB_ICONERROR,
                    )
                except Exception as e:
                    # Best-effort logging if the message box fails
                    _log_error_safely(log_path, f"Failed to show message box: {e}")
        except Exception as e:
            # Best-effort logging if writing the error log fails
            # log_path is defined before try block, so it's safe to reference
            _log_error_safely(
                None, f"Failed to write installation error log to {log_path}: {e}"
            )
        return 1

    # Check Python version
    if not check_python_version():
        return 1

    # Print platform info and warnings
    if not print_platform_warning():
        return 0

    # Ask user if they want to proceed
    response = input("Proceed with installation? (y/n): ").strip().lower()
    if response not in ["y", "yes"]:
        print("\nInstallation cancelled.")
        print(
            "See the Wiki (https://github.com/Mittenzx/Adastrea-Director/wiki) for manual installation instructions."
        )
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
