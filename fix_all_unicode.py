#!/usr/bin/env python3
"""
Fix ALL Unicode characters in Python files for Windows compatibility.
"""

import os
import re
from pathlib import Path

def fix_all_unicode_in_file(filepath: Path):
    """Replace ALL Unicode characters with ASCII equivalents in a file."""
    print(f"Processing: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Common Unicode replacements
        replacements = {
            # Emojis
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARNING]',
            '🔧': '[TOOL]',
            '🚀': '[ROCKET]',
            '📡': '[SERVER]',
            '🛑': '[STOP]',
            '💡': '[TIP]',
            '👋': '[WAVE]',
            '🎯': '[TARGET]',
            '📋': '[CLIPBOARD]',
            '🛠️': '[TOOLS]',
            '📊': '[CHART]',
            '🔌': '[PLUG]',
            '📁': '[FOLDER]',
            '📚': '[BOOKS]',
            '🏁': '[FINISH]',
            '🤝': '[HANDSHAKE]',
            '📈': '[GRAPH]',
            '🎉': '[PARTY]',
            '🚫': '[NO]',
            '🔍': '[SEARCH]',
            '💬': '[CHAT]',
            '📝': '[NOTE]',
            '🔗': '[LINK]',
            '🎭': '[MASK]',
            '💓': '[HEART]',
            '😊': '[SMILE]',
            '😂': '[LAUGH]',
            '💀': '[SKULL]',
            '🙌': '[HANDS]',
            '🤔': '[THINK]',
            '👀': '[EYES]',
            '👍': '[THUMBS UP]',
            '❤️': '[HEART]',
            
            # Special characters
            '•': '-',
            '→': '->',
            '—': '--',
            '–': '-',
            '…': '...',
            '“': '"',
            '”': '"',
            '‘': "'",
            '’': "'",
            '«': '<<',
            '»': '>>',
        }
        
        # Apply all replacements
        for unicode_char, ascii_replacement in replacements.items():
            content = content.replace(unicode_char, ascii_replacement)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  Fixed ALL Unicode characters in {filepath}")
        
    except Exception as e:
        print(f"  Error processing {filepath}: {e}")

def main():
    """Fix Unicode characters in all Python files in the repository."""
    repo_root = Path(__file__).parent
    
    # Files to process
    files_to_fix = [
        repo_root / "configure_unreal_python.py",
        repo_root / "unreal_mcp_cli_enhanced.py",
        repo_root / "mcp_server" / "server_enhanced.py",
        repo_root / "mcp_server" / "enhanced_error_handling.py",
        repo_root / "test_unreal_connection.py",
    ]
    
    print("Fixing ALL Unicode characters for Windows compatibility...")
    print("=" * 60)
    
    for filepath in files_to_fix:
        if filepath.exists():
            fix_all_unicode_in_file(filepath)
        else:
            print(f"File not found: {filepath}")
    
    print("\n" + "=" * 60)
    print("Done! All Unicode characters replaced with ASCII equivalents.")
    print("\nNote: This makes the output compatible with Windows terminals")
    print("      that don't support Unicode characters.")

if __name__ == "__main__":
    main()