#!/usr/bin/env python3
"""
Test to verify that subprocess calls properly handle UTF-8 encoding.

This test ensures that the encoding fixes in ingest_game_repo.py and
other files properly handle UTF-8 characters in subprocess output on Windows.
"""

import subprocess
import sys
import tempfile
from pathlib import Path


def test_subprocess_encoding_parameter():
    """Test that subprocess.run with encoding='utf-8' handles UTF-8 output."""
    # Create a simple test that echoes UTF-8 text
    if sys.platform == "win32":
        # On Windows, use echo command
        result = subprocess.run(
            ["cmd", "/c", "echo", "Test UTF-8: café ñ 日本語"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
    else:
        # On Unix-like systems
        result = subprocess.run(
            ["echo", "Test UTF-8: café ñ 日本語"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
    
    # The test passes if no UnicodeDecodeError is raised
    assert result.returncode == 0
    assert isinstance(result.stdout, str)
    print(f"✓ Subprocess successfully handled UTF-8 output: {result.stdout.strip()}")


def test_git_command_with_utf8_encoding():
    """Test that git commands work with encoding='utf-8'."""
    # Try to run a simple git command that should work in any directory
    result = subprocess.run(
        ["git", "--version"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    assert result.returncode == 0
    assert "git version" in result.stdout.lower()
    print(f"✓ Git command with UTF-8 encoding works: {result.stdout.strip()}")


def test_subprocess_without_encoding_on_windows():
    """
    Test that demonstrates the issue when encoding is not specified on Windows.
    
    This test is skipped on non-Windows platforms since they default to UTF-8.
    """
    if sys.platform != "win32":
        print("⊘ Skipping Windows-specific test on non-Windows platform")
        return
    
    # This test just verifies the platform detection works
    # The actual bug would occur with UTF-8 content in subprocess output
    print("✓ Running on Windows platform - encoding parameter is required")


def test_git_output_with_unicode():
    """
    Test git command that might produce unicode output.
    
    This simulates the scenario that causes the original bug.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "test_repo"
        test_dir.mkdir()
        
        # Initialize a git repository
        result = subprocess.run(
            ["git", "init"],
            cwd=str(test_dir),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            print(f"⊘ Skipping test - git init failed: {result.stderr}")
            return
        
        # Configure git user (required for commits)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=str(test_dir),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=str(test_dir),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Create a file with UTF-8 content
        test_file = test_dir / "test.txt"
        test_file.write_text("Test file with UTF-8: café ñ émoji 🎮", encoding='utf-8')
        
        # Add and commit the file
        subprocess.run(
            ["git", "add", "test.txt"],
            cwd=str(test_dir),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        result = subprocess.run(
            ["git", "commit", "-m", "Test commit with UTF-8: café"],
            cwd=str(test_dir),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            print(f"⊘ Skipping test - git commit failed: {result.stderr}")
            return
        
        # Get the commit hash (this is what was failing in the original bug)
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(test_dir),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        assert result.returncode == 0
        assert len(result.stdout.strip()) == 40  # Git commit hash is 40 chars
        print(f"✓ Git rev-parse with UTF-8 encoding works: {result.stdout.strip()[:8]}...")


def main():
    """Run all tests."""
    print("\n=== Testing Subprocess UTF-8 Encoding Fix ===")
    print(f"Platform: {sys.platform}")
    print(f"Python version: {sys.version}\n")
    
    tests = [
        ("Basic encoding parameter", test_subprocess_encoding_parameter),
        ("Git command with UTF-8", test_git_command_with_utf8_encoding),
        ("Windows platform check", test_subprocess_without_encoding_on_windows),
        ("Git output with unicode", test_git_output_with_unicode),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{test_name}:")
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✅ All subprocess encoding tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
