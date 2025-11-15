#!/usr/bin/env python3
"""
Verify GUI Director can be instantiated and has all required methods.
This script validates the GUI without displaying it.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def verify_gui_structure():
    """Verify the GUI module structure and methods."""
    print("Verifying GUI Director structure...")
    
    # Import the module
    try:
        import gui_director
        print("✓ gui_director module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import gui_director: {e}")
        return False
    
    # Check for main class
    if not hasattr(gui_director, 'AdastreaDirectorApp'):
        print("✗ AdastreaDirectorApp class not found")
        return False
    print("✓ AdastreaDirectorApp class exists")
    
    # Check for required methods
    required_methods = [
        'set_api_key',
        'open_settings',  # New method
        'clear_conversation',
        'copy_response',
        'export_conversation',
        'run_query',
        'ingest_folder',
        'ingest_file',
        'ingest_github_repo',
        'update_status',
        'add_to_conversation',
        'show_shortcuts',
        'bind_shortcuts',
    ]
    
    for method_name in required_methods:
        if not hasattr(gui_director.AdastreaDirectorApp, method_name):
            print(f"✗ Method '{method_name}' not found")
            return False
    print(f"✓ All {len(required_methods)} required methods exist")
    
    # Verify main function exists
    if not hasattr(gui_director, 'main'):
        print("✗ main() function not found")
        return False
    print("✓ main() function exists")
    
    return True


def verify_test_structure():
    """Verify the test file structure."""
    print("\nVerifying test structure...")
    
    try:
        import tests.test_gui_director as test_module
        print("✓ test_gui_director module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import test module: {e}")
        return False
    
    # Check for test classes
    test_classes = [
        'TestGUIDirector',
        'TestSettingsDialog',
        'TestErrorHandling',
        'TestConversationManagement',
        'TestGUIIntegration',
        'TestModuleImports',
    ]
    
    for class_name in test_classes:
        if not hasattr(test_module, class_name):
            print(f"✗ Test class '{class_name}' not found")
            return False
    print(f"✓ All {len(test_classes)} test classes exist")
    
    return True


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("GUI Director Verification")
    print("=" * 60)
    
    gui_ok = verify_gui_structure()
    test_ok = verify_test_structure()
    
    print("\n" + "=" * 60)
    if gui_ok and test_ok:
        print("✅ All verifications passed!")
        print("=" * 60)
        return 0
    else:
        print("❌ Some verifications failed")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
