#!/usr/bin/env python3
"""
Demonstration of Incremental Ingestion Feature

This script demonstrates the incremental ingestion feature without requiring
an OpenAI API key by using mocked components.

Run with: python3 demo_incremental.py
"""

import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from ingest import DocumentIngestionAgent


def demo_incremental_ingestion():
    """Demonstrate incremental ingestion capabilities."""
    
    print("=" * 70)
    print("Incremental Ingestion Feature Demo")
    print("=" * 70)
    
    # Create a temporary directory for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\n📁 Created temporary directory: {temp_dir}\n")
        
        # Create some sample files
        files = {
            "design.md": "# Game Design Document\n\nThis is our game design.",
            "player.py": "class Player:\n    def __init__(self):\n        self.health = 100",
            "config.json": '{"game": "Space Adventure", "version": "1.0"}'
        }
        
        print("Creating sample files:")
        for filename, content in files.items():
            filepath = Path(temp_dir) / filename
            filepath.write_text(content)
            print(f"  ✓ {filename}")
        
        # Mock OpenAI embeddings to avoid needing API key
        with patch('ingest.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value = Mock()
            agent = DocumentIngestionAgent(persist_directory=f"{temp_dir}/db")
            
            print(f"\n📊 Discovering files...")
            discovered_files = agent._get_file_list(temp_dir)
            print(f"  Found {len(discovered_files)} files")
            
            print(f"\n🔐 Calculating file hashes...")
            for file_path in discovered_files:
                file_hash = agent._calculate_file_hash(file_path)
                filename = Path(file_path).name
                print(f"  {filename}: {file_hash[:16]}...")
            
            print(f"\n🔍 Testing change detection...")
            
            # Simulate first ingestion (all files are new)
            print(f"\n  Scenario 1: First ingestion (all files are new)")
            with patch('ingest.Chroma') as mock_chroma:
                mock_collection = Mock()
                mock_collection.get.return_value = {"metadatas": []}
                mock_vectorstore = Mock()
                mock_vectorstore._collection = mock_collection
                mock_chroma.return_value = mock_vectorstore
                
                for file_path in discovered_files:
                    has_changed, old_hash = agent._check_file_changed(file_path)
                    filename = Path(file_path).name
                    status = "NEW" if old_hash is None else "CHANGED"
                    print(f"    {filename}: {status} (will be added)")
            
            # Simulate second ingestion (no changes)
            print(f"\n  Scenario 2: Re-ingestion without changes")
            with patch('ingest.Chroma') as mock_chroma:
                for file_path in discovered_files:
                    current_hash = agent._calculate_file_hash(file_path)
                    
                    mock_collection = Mock()
                    mock_collection.get.return_value = {
                        "metadatas": [{"file_hash": current_hash, "source": file_path}]
                    }
                    mock_vectorstore = Mock()
                    mock_vectorstore._collection = mock_collection
                    mock_chroma.return_value = mock_vectorstore
                    
                    has_changed, old_hash = agent._check_file_changed(file_path)
                    filename = Path(file_path).name
                    status = "UNCHANGED" if not has_changed else "CHANGED"
                    print(f"    {filename}: {status} (will be skipped)")
            
            # Modify one file and test again
            print(f"\n  Scenario 3: One file modified")
            modified_file = Path(temp_dir) / "player.py"
            modified_file.write_text("class Player:\n    def __init__(self):\n        self.health = 150  # Increased!")
            
            with patch('ingest.Chroma') as mock_chroma:
                for file_path in discovered_files:
                    current_hash = agent._calculate_file_hash(file_path)
                    
                    # For player.py, use old hash; for others, use current hash
                    if Path(file_path).name == "player.py":
                        stored_hash = "old_hash_different"
                    else:
                        stored_hash = current_hash
                    
                    mock_collection = Mock()
                    mock_collection.get.return_value = {
                        "metadatas": [{"file_hash": stored_hash, "source": file_path}]
                    }
                    mock_vectorstore = Mock()
                    mock_vectorstore._collection = mock_collection
                    mock_chroma.return_value = mock_vectorstore
                    
                    has_changed, old_hash = agent._check_file_changed(file_path)
                    filename = Path(file_path).name
                    if has_changed and old_hash is not None:
                        status = "CHANGED"
                        action = "(will be updated)"
                    elif has_changed:
                        status = "NEW"
                        action = "(will be added)"
                    else:
                        status = "UNCHANGED"
                        action = "(will be skipped)"
                    print(f"    {filename}: {status} {action}")
            
            # Test force re-ingest
            print(f"\n  Scenario 4: Force re-ingest (--reingest flag)")
            for file_path in discovered_files:
                has_changed, old_hash = agent._check_file_changed(file_path, force_reingest=True)
                filename = Path(file_path).name
                print(f"    {filename}: FORCED (will be re-ingested)")
            
            # Test metadata enrichment
            print(f"\n📋 Testing metadata enrichment with hash...")
            mock_doc = Mock()
            mock_doc.metadata = {"source": str(Path(temp_dir) / "design.md")}
            
            test_hash = agent._calculate_file_hash(str(Path(temp_dir) / "design.md"))
            docs = agent._enrich_document_metadata([mock_doc], file_hash=test_hash)
            
            print(f"  Metadata fields added:")
            for key, value in docs[0].metadata.items():
                if key == "file_hash":
                    print(f"    {key}: {value[:16]}...")
                else:
                    print(f"    {key}: {value}")
    
    print(f"\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
    print(f"\n📚 Key Features Demonstrated:")
    print(f"  ✓ Hash-based change detection")
    print(f"  ✓ Skip unchanged files")
    print(f"  ✓ Detect modified files")
    print(f"  ✓ Force re-ingestion option")
    print(f"  ✓ Metadata enrichment with file hash")
    print(f"\n💡 To use with real ingestion:")
    print(f"  python ingest.py --docs-dir /path/to/docs")
    print(f"  python ingest.py --docs-dir /path/to/docs --reingest")
    print()


if __name__ == "__main__":
    demo_incremental_ingestion()
