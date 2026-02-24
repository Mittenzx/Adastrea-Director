#!/usr/bin/env python3
"""
Adastrea Director - Installation Script

This script provides a one-click installation and setup experience
for the Adastrea Director plugin.

Features:
1. Checks system requirements
2. Installs Python dependencies
3. Configures Unreal Engine
4. Tests the installation
5. Provides next steps

Usage:
    python install.py          # Interactive installation
    python install.py --quick  # Quick installation with defaults
    python install.py --check  # Check system only
"""

import sys
import os
import subprocess
import platform
import argparse
from pathlib import Path
from typing import Dict, List, Tuple


class AdastreaInstaller:
    """Installation manager for Adastrea Director."""
    
    def __init__(self, quick_mode: bool = False):
        """Initialize the installer."""
        self.quick_mode = quick_mode
        self.repo_root = Path(__file__).parent
        self.results = {
            "system_check": False,
            "python_check": False,
            "dependencies": False,
            "unreal_check": False,
            "configuration": False,
            "test": False,
        }
        self.errors = []
        
        print("\n" + "=" * 60)
        print("Adastrea Director - Installation Wizard")
        print("=" * 60)
    
    def run(self) -> bool:
        """Run the complete installation process."""
        try:
            self.check_system()
            self.check_python()
            self.install_dependencies()
            self.check_unreal_engine()
            self.configure_unreal()
            self.test_installation()
            self.show_summary()
            
            # Check if installation was successful
            success_count = sum(1 for v in self.results.values() if v)
            return success_count >= 4  # At least 4 out of 6 steps successful
            
        except KeyboardInterrupt:
            print("\n[INFO] Installation interrupted by user.")
            return False
        except Exception as e:
            print(f"\n[ERROR] Installation failed: {e}")
            self.errors.append(str(e))
            return False
    
    def check_system(self) -> bool:
        """Check system requirements."""
        print("\n[STEP 1] Checking system requirements...")
        
        checks = []
        
        # Check OS
        system = platform.system()
        checks.append(("Operating System", system in ["Windows", "Darwin", "Linux"], system))
        
        # Check Python version
        python_version = platform.python_version()
        major, minor, _ = map(int, python_version.split('.'))
        checks.append(("Python Version", major >= 3 and minor >= 8, python_version))
        
        # Check disk space (approximate)
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.repo_root)
            free_gb = free // (2**30)
            checks.append(("Disk Space", free_gb >= 1, f"{free_gb} GB free"))
        except:
            checks.append(("Disk Space", True, "Could not check"))
        
        # Display results
        all_passed = True
        for name, passed, value in checks:
            status = "[OK]" if passed else "[ERROR]"
            print(f"  {status} {name}: {value}")
            if not passed:
                all_passed = False
                self.errors.append(f"System check failed: {name}")
        
        self.results["system_check"] = all_passed
        return all_passed
    
    def check_python(self) -> bool:
        """Check Python installation and modules."""
        print("\n[STEP 2] Checking Python installation...")
        
        checks = []
        
        # Check if pip is available
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         capture_output=True, check=True)
            checks.append(("pip", True, "Available"))
        except:
            checks.append(("pip", False, "Not found"))
        
        # Check for required modules
        required_modules = ["json", "pathlib", "subprocess", "platform", "argparse"]
        for module in required_modules:
            try:
                __import__(module)
                checks.append((f"Module: {module}", True, "Available"))
            except ImportError:
                checks.append((f"Module: {module}", False, "Not found"))
        
        # Display results
        all_passed = True
        for name, passed, value in checks:
            status = "[OK]" if passed else "[ERROR]"
            print(f"  {status} {name}: {value}")
            if not passed:
                all_passed = False
                self.errors.append(f"Python check failed: {name}")
        
        self.results["python_check"] = all_passed
        return all_passed
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies."""
        print("\n[STEP 3] Installing Python dependencies...")
        
        requirements_file = self.repo_root / "requirements.txt"
        
        if not requirements_file.exists():
            print(f"  [INFO] No requirements.txt found at {requirements_file}")
            print("  [INFO] Creating minimal requirements...")
            
            # Create minimal requirements
            minimal_requirements = """# Adastrea Director - Minimal Requirements
# Core dependencies for MCP server and Unreal Engine integration

# Web framework for MCP server
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
websockets>=12.0

# HTTP client for Unreal Engine communication
httpx>=0.25.0

# Utilities
pydantic>=2.0.0
typing-extensions>=4.8.0
"""
            
            try:
                requirements_file.write_text(minimal_requirements, encoding="utf-8")
                print(f"  [OK] Created requirements.txt")
            except Exception as e:
                print(f"  [ERROR] Failed to create requirements.txt: {e}")
                self.results["dependencies"] = False
                return False
        
        # Ask user if they want to install dependencies
        if not self.quick_mode:
            response = input("\n  Install Python dependencies? (y/n): ").strip().lower()
            if response not in ['y', 'yes']:
                print("  [INFO] Skipping dependency installation")
                self.results["dependencies"] = True  # Mark as successful (user choice)
                return True
        
        # Install dependencies
        print(f"  Installing from {requirements_file}...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("  [OK] Dependencies installed successfully")
                self.results["dependencies"] = True
                return True
            else:
                print(f"  [ERROR] Failed to install dependencies:")
                print(f"  {result.stderr[:500]}")
                self.errors.append("Dependency installation failed")
                self.results["dependencies"] = False
                return False
                
        except Exception as e:
            print(f"  [ERROR] Exception during installation: {e}")
            self.errors.append(f"Dependency installation exception: {e}")
            self.results["dependencies"] = False
            return False
    
    def check_unreal_engine(self) -> bool:
        """Check if Unreal Engine is installed."""
        print("\n[STEP 4] Checking Unreal Engine installation...")
        
        # Try to use the configuration helper
        config_script = self.repo_root / "configure_unreal_python.py"
        
        if not config_script.exists():
            print(f"  [ERROR] Configuration script not found: {config_script}")
            self.errors.append("Configuration script missing")
            self.results["unreal_check"] = False
            return False
        
        try:
            # Run the check command
            result = subprocess.run(
                [sys.executable, str(config_script), "--check"],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            
            if result.returncode == 0:
                print("  [OK] Unreal Engine check completed")
                # Parse output to see if UE was found
                if "Found Unreal Engine at:" in result.stdout:
                    self.results["unreal_check"] = True
                    return True
                else:
                    print("  [WARNING] Unreal Engine not found in standard locations")
                    print("  [INFO] You may need to install Unreal Engine 5.0+")
                    self.results["unreal_check"] = False
                    return False
            else:
                print(f"  [ERROR] Unreal Engine check failed:")
                print(f"  {result.stderr[:500]}")
                self.errors.append("Unreal Engine check failed")
                self.results["unreal_check"] = False
                return False
                
        except Exception as e:
            print(f"  [ERROR] Exception during Unreal Engine check: {e}")
            self.errors.append(f"Unreal Engine check exception: {e}")
            self.results["unreal_check"] = False
            return False
    
    def configure_unreal(self) -> bool:
        """Configure Unreal Engine for Python Remote Execution."""
        print("\n[STEP 5] Configuring Unreal Engine...")
        
        # Ask user if they want to configure
        if not self.quick_mode:
            print("\n  Unreal Engine needs Python Remote Execution to be enabled.")
            print("  This can be done automatically or manually.")
            response = input("\n  Configure Unreal Engine automatically? (y/n): ").strip().lower()
            
            if response not in ['y', 'yes']:
                print("  [INFO] Skipping automatic configuration")
                print("  [INFO] Manual configuration instructions:")
                print("    1. Run: python configure_unreal_python.py --instructions")
                print("    2. Follow the step-by-step guide")
                self.results["configuration"] = True  # User choice
                return True
        
        # Run automatic configuration
        config_script = self.repo_root / "configure_unreal_python.py"
        
        try:
            print("  Running automatic configuration...")
            result = subprocess.run(
                [sys.executable, str(config_script), "--create-config"],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            
            if result.returncode == 0:
                print("  [OK] Unreal Engine configuration created")
                print("  [INFO] Launch Unreal Engine Editor to apply the configuration")
                self.results["configuration"] = True
                return True
            else:
                print(f"  [ERROR] Automatic configuration failed:")
                print(f"  {result.stderr[:500]}")
                print("  [INFO] Try manual configuration:")
                print("    python configure_unreal_python.py --instructions")
                self.errors.append("Automatic configuration failed")
                self.results["configuration"] = False
                return False
                
        except Exception as e:
            print(f"  [ERROR] Exception during configuration: {e}")
            self.errors.append(f"Configuration exception: {e}")
            self.results["configuration"] = False
            return False
    
    def test_installation(self) -> bool:
        """Test the installation."""
        print("\n[STEP 6] Testing installation...")
        
        # Test 1: Verify repository
        verify_script = self.repo_root / "verify_repository.py"
        if verify_script.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(verify_script)],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_root
                )
                
                if result.returncode == 0 and "[SUCCESS]" in result.stdout:
                    print("  [OK] Repository verification passed")
                else:
                    print("  [WARNING] Repository verification issues")
                    print(f"  {result.stdout[:300]}")
            except:
                print("  [INFO] Repository verification skipped")
        
        # Test 2: Test connection (optional)
        if not self.quick_mode:
            response = input("\n  Test Unreal Engine connection? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                test_script = self.repo_root / "test_unreal_connection.py"
                if test_script.exists():
                    try:
                        print("  Testing connection to Unreal Engine...")
                        result = subprocess.run(
                            [sys.executable, str(test_script)],
                            capture_output=True,
                            text=True,
                            cwd=self.repo_root
                        )
                        
                        if result.returncode == 0:
                            print("  [OK] Connection test completed")
                            if "[SUCCESS]" in result.stdout:
                                print("  [OK] Connected to Unreal Engine!")
                                self.results["test"] = True
                            else:
                                print("  [WARNING] Not connected to Unreal Engine")
                                print("  [INFO] Make sure Unreal Engine is running")
                                self.results["test"] = False
                        else:
                            print("  [ERROR] Connection test failed")
                            self.results["test"] = False
                    except Exception as e:
                        print(f"  [ERROR] Connection test exception: {e}")
                        self.results["test"] = False
                else:
                    print("  [INFO] Connection test script not found")
                    self.results["test"] = False
            else:
                print("  [INFO] Connection test skipped")
                self.results["test"] = True  # User choice
        else:
            # In quick mode, skip interactive test
            self.results["test"] = True
        
        return self.results["test"]
    
    def show_summary(self):
        """Show installation summary."""
        print("\n" + "=" * 60)
        print("INSTALLATION SUMMARY")
        print("=" * 60)
        
        # Show results
        steps = [
            ("System Requirements", "system_check"),
            ("Python Installation", "python_check"),
            ("Dependencies", "dependencies"),
            ("Unreal Engine", "unreal_check"),
            ("Configuration", "configuration"),
            ("Tests", "test"),
        ]
        
        for name, key in steps:
            status = "[OK]" if self.results[key] else "[ERROR]"
            print(f"{status} {name}")
        
        # Show errors if any
        if self.errors:
            print("\n" + "=" * 60)
            print("ERRORS ENCOUNTERED")
            print("=" * 60)
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
        
        # Show next steps
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)
        
        success_count = sum(1 for v in self.results.values() if v)
        
        if success_count >= 4:
            print("[SUCCESS] Installation mostly successful!")
            print("\nTo get started:")
            print("1. Launch Unreal Engine Editor")
            print("2. Enable Python Remote Execution if not already done")
            print("3. Test the connection:")
            print("   python test_unreal_connection.py")
            print("4. Run the comprehensive example:")
            print("   python examples/comprehensive_example.py")
            print("5. Use the enhanced CLI:")
            print("   python unreal_mcp_cli_enhanced.py")
        else:
            print("[WARNING] Installation had issues.")
            print("\nTroubleshooting steps:")
            print("1. Check Unreal Engine installation")
            print("2. Run manual configuration:")
            print("   python configure_unreal_python.py --instructions")
            print("3. Check Python dependencies:")
            print("   pip install -r requirements.txt")
            print("4. Verify repository structure:")
            print("   python verify_repository.py")
        
        print("\nDocumentation:")
        print("  - Quick Start: QUICK_START_GUIDE.md")
        print("  - Enhanced Tools: ENHANCED_PLUGIN_TOOLS.md")
        print("  - Setup Guide: UNREAL_PYTHON_SETUP.md")
        
        print("\n" + "=" * 60)
        print("Thank you for installing Adastrea Director!")
        print("=" * 60)


def main():
    """Main installation function."""
    parser = argparse.ArgumentParser(
        description="Adastrea Director Installation Wizard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python install.py           # Interactive installation
  python install.py --quick   # Quick installation with defaults
  python install.py --check   # Check system only
        
For manual setup:
  python configure_unreal_python.py --instructions
  python test_unreal_connection.py
        """
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick installation with default choices"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check system only (no installation)"
    )
    
    args = parser.parse_args()
    
    # Create installer
    installer = AdastreaInstaller(quick_mode=args.quick)
    
    if args.check:
        # System check only
        print("Running system check only...")
        installer.check_system()
        installer.check_python()
        return
    
    # Run full installation
    success = installer.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()