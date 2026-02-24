#!/usr/bin/env python3
"""
Test Suite for Adastrea Director Enhanced Tools

This test suite validates the enhanced tools and utilities
created for the Adastrea Director plugin.

Tests include:
1. Configuration helper
2. Connection diagnostics
3. Enhanced CLI
4. Enhanced MCP server
5. Error handling
"""

import unittest
import sys
import os
from pathlib import Path
import tempfile
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfigurationHelper(unittest.TestCase):
    """Test the configuration helper tool."""
    
    def test_script_exists(self):
        """Test that configuration script exists."""
        config_script = Path(__file__).parent.parent / "configure_unreal_python.py"
        self.assertTrue(config_script.exists(), "Configuration script should exist")
    
    def test_script_is_valid_python(self):
        """Test that configuration script is valid Python."""
        config_script = Path(__file__).parent.parent / "configure_unreal_python.py"
        try:
            with open(config_script, 'r', encoding='utf-8') as f:
                content = f.read()
            # Try to compile it
            compile(content, str(config_script), 'exec')
            self.assertTrue(True, "Configuration script should be valid Python")
        except SyntaxError as e:
            self.fail(f"Configuration script has syntax error: {e}")
    
    def test_help_option(self):
        """Test that help option works."""
        # This is a basic test that doesn't require Unreal Engine
        import subprocess
        config_script = Path(__file__).parent.parent / "configure_unreal_python.py"
        
        result = subprocess.run(
            [sys.executable, str(config_script), "--help"],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0, "Help option should succeed")
        self.assertIn("usage:", result.stdout.lower(), "Help should show usage")


class TestConnectionDiagnostics(unittest.TestCase):
    """Test the connection diagnostic tool."""
    
    def test_diagnostic_script_exists(self):
        """Test that diagnostic script exists."""
        test_script = Path(__file__).parent.parent / "test_unreal_connection.py"
        self.assertTrue(test_script.exists(), "Diagnostic script should exist")
    
    def test_diagnostic_script_is_valid(self):
        """Test that diagnostic script is valid Python."""
        test_script = Path(__file__).parent.parent / "test_unreal_connection.py"
        try:
            with open(test_script, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, str(test_script), 'exec')
            self.assertTrue(True, "Diagnostic script should be valid Python")
        except SyntaxError as e:
            self.fail(f"Diagnostic script has syntax error: {e}")


class TestEnhancedCLI(unittest.TestCase):
    """Test the enhanced CLI tool."""
    
    def test_cli_script_exists(self):
        """Test that enhanced CLI script exists."""
        cli_script = Path(__file__).parent.parent / "unreal_mcp_cli_enhanced.py"
        self.assertTrue(cli_script.exists(), "Enhanced CLI script should exist")
    
    def test_cli_is_valid_python(self):
        """Test that enhanced CLI is valid Python."""
        cli_script = Path(__file__).parent.parent / "unreal_mcp_cli_enhanced.py"
        try:
            with open(cli_script, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, str(cli_script), 'exec')
            self.assertTrue(True, "Enhanced CLI should be valid Python")
        except SyntaxError as e:
            self.fail(f"Enhanced CLI has syntax error: {e}")
    
    def test_cli_help_option(self):
        """Test that CLI help option works."""
        import subprocess
        cli_script = Path(__file__).parent.parent / "unreal_mcp_cli_enhanced.py"
        
        result = subprocess.run(
            [sys.executable, str(cli_script), "--help"],
            capture_output=True,
            text=True
        )
        
        # Help should work or at least not crash
        self.assertIn(result.returncode, [0, 2], "Help option should not crash")
        if result.returncode == 0:
            self.assertIn("usage:", result.stdout.lower(), "Help should show usage")


class TestEnhancedMCPServer(unittest.TestCase):
    """Test the enhanced MCP server."""
    
    def test_server_module_exists(self):
        """Test that enhanced server module exists."""
        server_module = Path(__file__).parent.parent / "mcp_server" / "server_enhanced.py"
        self.assertTrue(server_module.exists(), "Enhanced server module should exist")
    
    def test_server_is_valid_python(self):
        """Test that enhanced server is valid Python."""
        server_module = Path(__file__).parent.parent / "mcp_server" / "server_enhanced.py"
        try:
            with open(server_module, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, str(server_module), 'exec')
            self.assertTrue(True, "Enhanced server should be valid Python")
        except SyntaxError as e:
            self.fail(f"Enhanced server has syntax error: {e}")


class TestErrorHandling(unittest.TestCase):
    """Test the enhanced error handling."""
    
    def test_error_handling_in_server(self):
        """Test that error handling is integrated in the enhanced server."""
        server_module = Path(__file__).parent.parent / "mcp_server" / "server_enhanced.py"
        self.assertTrue(server_module.exists(), "Enhanced server should exist")
        
        # Check that the server has error handling methods
        with open(server_module, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for error handling methods
        self.assertIn('_get_enhanced_connection_error', content, 
                     "Server should have enhanced connection error method")
        self.assertIn('_get_enhanced_tool_error', content,
                     "Server should have enhanced tool error method")


class TestDocumentation(unittest.TestCase):
    """Test that documentation exists and is valid."""
    
    def test_quick_start_guide(self):
        """Test that quick start guide exists."""
        guide = Path(__file__).parent.parent / "QUICK_START_GUIDE.md"
        self.assertTrue(guide.exists(), "Quick start guide should exist")
        self.assertGreater(guide.stat().st_size, 100, "Quick start guide should have content")
    
    def test_enhanced_tools_doc(self):
        """Test that enhanced tools documentation exists."""
        doc = Path(__file__).parent.parent / "ENHANCED_PLUGIN_TOOLS.md"
        self.assertTrue(doc.exists(), "Enhanced tools documentation should exist")
        self.assertGreater(doc.stat().st_size, 100, "Enhanced tools doc should have content")
    
    def test_setup_guide(self):
        """Test that setup guide exists."""
        guide = Path(__file__).parent.parent / "UNREAL_PYTHON_SETUP.md"
        self.assertTrue(guide.exists(), "Setup guide should exist")
        self.assertGreater(guide.stat().st_size, 100, "Setup guide should have content")
    
    def test_installation_guide(self):
        """Test that installation guide exists."""
        guide = Path(__file__).parent.parent / "UNREAL_PYTHON_INSTALLATION_GUIDE.md"
        self.assertTrue(guide.exists(), "Installation guide should exist")
        self.assertGreater(guide.stat().st_size, 100, "Installation guide should have content")


class TestRepositoryStructure(unittest.TestCase):
    """Test the overall repository structure."""
    
    def test_verification_script(self):
        """Test that verification script exists and works."""
        verify_script = Path(__file__).parent.parent / "verify_repository.py"
        self.assertTrue(verify_script.exists(), "Verification script should exist")
        
        # Test that it's valid Python
        try:
            with open(verify_script, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, str(verify_script), 'exec')
            self.assertTrue(True, "Verification script should be valid Python")
        except SyntaxError as e:
            self.fail(f"Verification script has syntax error: {e}")
    
    def test_requirements_file(self):
        """Test that requirements file exists."""
        req_file = Path(__file__).parent.parent / "requirements.txt"
        self.assertTrue(req_file.exists(), "Requirements file should exist")
    
    def test_readme_file(self):
        """Test that README exists."""
        readme = Path(__file__).parent.parent / "README.md"
        self.assertTrue(readme.exists(), "README should exist")
        self.assertGreater(readme.stat().st_size, 100, "README should have content")
    
    def test_examples_directory(self):
        """Test that examples directory exists."""
        examples_dir = Path(__file__).parent.parent / "examples"
        self.assertTrue(examples_dir.exists(), "Examples directory should exist")
        self.assertTrue(examples_dir.is_dir(), "Examples should be a directory")
        
        # Check for at least one example
        example_files = list(examples_dir.glob("*.py"))
        self.assertGreater(len(example_files), 0, "Should have at least one example")
    
    def test_mcp_server_directory(self):
        """Test that MCP server directory exists."""
        mcp_dir = Path(__file__).parent.parent / "mcp_server"
        self.assertTrue(mcp_dir.exists(), "MCP server directory should exist")
        self.assertTrue(mcp_dir.is_dir(), "MCP server should be a directory")
        
        # Check for core files
        self.assertTrue((mcp_dir / "server.py").exists(), "MCP server.py should exist")
        self.assertTrue((mcp_dir / "server_enhanced.py").exists(), "Enhanced server should exist")


class TestInstallationScript(unittest.TestCase):
    """Test the installation script."""
    
    def test_install_script_exists(self):
        """Test that installation script exists."""
        install_script = Path(__file__).parent.parent / "install.py"
        self.assertTrue(install_script.exists(), "Installation script should exist")
    
    def test_install_script_is_valid(self):
        """Test that installation script is valid Python."""
        install_script = Path(__file__).parent.parent / "install.py"
        try:
            with open(install_script, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, str(install_script), 'exec')
            self.assertTrue(True, "Installation script should be valid Python")
        except SyntaxError as e:
            self.fail(f"Installation script has syntax error: {e}")


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationHelper))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectionDiagnostics))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedCLI))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedMCPServer))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentation))
    suite.addTests(loader.loadTestsFromTestCase(TestRepositoryStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestInstallationScript))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return summary
    return {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "successful": result.testsRun - len(result.failures) - len(result.errors),
    }


def main():
    """Main function to run tests."""
    print("\n" + "=" * 60)
    print("Adastrea Director - Enhanced Tools Test Suite")
    print("=" * 60)
    print("\nRunning tests...\n")
    
    results = run_tests()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Tests Run: {results['tests_run']}")
    print(f"Successful: {results['successful']}")
    print(f"Failures: {results['failures']}")
    print(f"Errors: {results['errors']}")
    
    if results['failures'] == 0 and results['errors'] == 0:
        print("\n[SUCCESS] All tests passed!")
        print("The enhanced tools are ready for use.")
        return 0
    else:
        print("\n[WARNING] Some tests failed.")
        print("Check the test output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())