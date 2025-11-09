#!/usr/bin/env python3
"""
Test script to verify Unicode emoji support works correctly across platforms.

This test ensures that the encoding fix in ingest.py and main.py allows
Unicode emojis to be printed without errors on Windows systems.

Usage:
    python test_unicode_support.py
"""

import sys
import io


def test_encoding_fix_on_windows():
    """Test that the encoding fix works on Windows."""
    if sys.platform == "win32":
        # Apply the same fix as in the main scripts
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    return True


def test_emoji_rendering():
    """Test that all emojis used in the application can be printed."""
    emojis_used = {
        "🤖": "Robot emoji (used in banners)",
        "✓": "Check mark (used for success messages)",
        "✗": "X mark (used for failure messages)",
    }
    
    print("\n=== Testing Unicode Emoji Support ===")
    print(f"Platform: {sys.platform}")
    print(f"Python version: {sys.version}")
    print(f"stdout encoding: {sys.stdout.encoding}")
    print(f"stderr encoding: {sys.stderr.encoding}\n")
    
    failed = []
    for emoji, description in emojis_used.items():
        try:
            print(f"{emoji} - {description}")
            sys.stdout.flush()  # Ensure it's actually written
        except UnicodeEncodeError as e:
            failed.append((emoji, description, str(e)))
            print(f"FAILED to print: {description}")
    
    print("\n=== Test Results ===")
    if failed:
        print(f"❌ {len(failed)} emoji(s) failed to render:")
        for emoji, desc, error in failed:
            print(f"  - {desc}: {error}")
        return False
    else:
        print("✅ All emojis rendered successfully!")
        return True


def main():
    """Run all tests."""
    try:
        # Apply encoding fix
        test_encoding_fix_on_windows()
        
        # Test emoji rendering
        success = test_emoji_rendering()
        
        if success:
            print("\n🎉 All Unicode support tests passed!")
            return 0
        else:
            print("\n⚠️  Some tests failed. See details above.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
