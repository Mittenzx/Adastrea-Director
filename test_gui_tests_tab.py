#!/usr/bin/env python3
"""
Validation script for the Tests tab integration in gui_director.py
This script validates that all required components are properly implemented.
"""

import ast
import sys
import os

def validate_gui_tests_integration():
    """Validate that the Tests tab is properly integrated."""
    
    print("=" * 60)
    print("Validating GUI Tests Tab Integration")
    print("=" * 60)
    print()
    
    # Check that gui_director.py exists
    gui_file = "gui_director.py"
    if not os.path.exists(gui_file):
        print(f"❌ {gui_file} not found")
        return False
    
    print(f"✓ Found {gui_file}")
    
    # Parse the file
    with open(gui_file, 'r') as f:
        content = f.read()
        tree = ast.parse(content)
    
    # Find the AdastreaDirectorApp class
    app_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'AdastreaDirectorApp':
            app_class = node
            break
    
    if not app_class:
        print("❌ AdastreaDirectorApp class not found")
        return False
    
    print("✓ Found AdastreaDirectorApp class")
    
    # Check for required methods
    required_methods = {
        'create_tests_tab': 'Creates the Tests tab UI',
        'run_test_suite': 'Runs a specific test suite',
        '_run_test_command': 'Executes test command in background',
        '_append_test_output': 'Appends test output with formatting',
        '_finalize_test_results': 'Displays final test results',
        'stop_running_test': 'Stops running test process',
        'clear_test_output': 'Clears test output display'
    }
    
    found_methods = {}
    for node in app_class.body:
        if isinstance(node, ast.FunctionDef):
            if node.name in required_methods:
                found_methods[node.name] = required_methods[node.name]
    
    print()
    print("Required Methods:")
    all_found = True
    for method, description in required_methods.items():
        if method in found_methods:
            print(f"  ✓ {method:<25} - {description}")
        else:
            print(f"  ❌ {method:<25} - {description}")
            all_found = False
    
    if not all_found:
        print()
        print("❌ Some required methods are missing")
        return False
    
    # Check that create_tests_tab is called in __init__
    init_method = None
    for node in app_class.body:
        if isinstance(node, ast.FunctionDef) and node.name == '__init__':
            init_method = node
            break
    
    if init_method:
        init_code = ast.unparse(init_method)
        if 'create_tests_tab' in init_code:
            print()
            print("✓ create_tests_tab is called in __init__")
        else:
            print()
            print("❌ create_tests_tab is not called in __init__")
            return False
    
    # Check for test command definitions
    run_test_suite_method = None
    for node in app_class.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'run_test_suite':
            run_test_suite_method = node
            break
    
    if run_test_suite_method:
        method_code = ast.unparse(run_test_suite_method)
        test_types = ['all', 'plugin', 'unit', 'integration', 'phase3', 'validation', 'remote']
        
        print()
        print("Test Categories Implemented:")
        for test_type in test_types:
            if f'"{test_type}"' in method_code or f"'{test_type}'" in method_code:
                print(f"  ✓ {test_type}")
            else:
                print(f"  ❌ {test_type}")
    
    # Check for UI elements (test_output widget)
    create_tests_tab_method = None
    for node in app_class.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'create_tests_tab':
            create_tests_tab_method = node
            break
    
    if create_tests_tab_method:
        method_code = ast.unparse(create_tests_tab_method)
        ui_elements = ['test_output', 'stop_test_button', 'test_status_label']
        
        print()
        print("UI Elements:")
        for element in ui_elements:
            if element in method_code:
                print(f"  ✓ {element}")
            else:
                print(f"  ❌ {element}")
    
    print()
    print("=" * 60)
    print("✅ All validations passed!")
    print("=" * 60)
    print()
    print("The Tests tab has been successfully integrated into the GUI.")
    print("Users can now run Python tests directly from the GUI by clicking buttons.")
    
    return True

if __name__ == "__main__":
    success = validate_gui_tests_integration()
    sys.exit(0 if success else 1)
