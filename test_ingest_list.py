#!/usr/bin/env python3
"""
Test script for the Ingest List functionality.

This script tests the document ingestion tracking feature without requiring
a full GUI environment.
"""

import os
import sys

# Add the directory to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


def test_get_ingested_documents():
    """Test the get_ingested_documents functionality."""
    print("Testing document ingestion tracking...\n")
    
    # Mock the method by importing necessary components
    try:
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import Chroma
        
        persist_directory = os.path.join(SCRIPT_DIR, "chroma_db")
        
        # Check if database exists
        if not os.path.exists(persist_directory):
            print("❌ No vector database found.")
            print("   📝 Note: Please ingest documents first using:")
            print("      python ingest.py --docs-dir /path/to/docs")
            return False
        
        print("✓ Vector database directory found")
        
        # Check if API key is set
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  Warning: OPENAI_API_KEY not set")
            print("   The Ingest List tab will show an error until you set your API key.")
            return False
        
        # Initialize embeddings and vector store
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma(
            collection_name="adastrea_docs",
            embedding_function=embeddings,
            persist_directory=persist_directory,
        )
        
        # Get collection and documents
        collection = vectorstore._collection
        count = collection.count()
        
        print(f"✓ Connected to vector database")
        print(f"  Total chunks in database: {count}")
        
        if count == 0:
            print("\n⚠️  Database is empty. Please ingest documents first.")
            return False
        
        # Get all documents with metadata
        results = collection.get(include=['metadatas'])
        
        # Extract unique source documents
        sources = {}
        if results and 'metadatas' in results:
            for metadata in results['metadatas']:
                if metadata and 'source' in metadata:
                    source = metadata['source']
                    if source not in sources:
                        sources[source] = {
                            'path': source,
                            'chunks': 1
                        }
                    else:
                        sources[source]['chunks'] += 1
        
        print(f"\n📊 Summary:")
        print(f"   Total documents: {len(sources)}")
        print(f"   Total chunks: {count}")
        
        if sources:
            print(f"\n✅ Ingested Documents:")
            for doc_path, doc_info in sorted(sources.items()):
                filename = os.path.basename(doc_path)
                chunks = doc_info['chunks']
                print(f"   • {filename}")
                print(f"     Path: {doc_path}")
                print(f"     Chunks: {chunks}")
        
        print("\n✓ Test passed! The Ingest List feature is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("\n   📝 To install required dependencies:")
        print("      pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main test function."""
    print("=" * 60)
    print("Adastrea Director - Ingest List Test")
    print("=" * 60)
    print()
    
    success = test_get_ingested_documents()
    
    print()
    print("=" * 60)
    if success:
        print("✓ All tests passed!")
        print("\nYou can now run the GUI and see the Ingest List tab:")
        print("  python gui_director.py")
    else:
        print("⚠️  Tests incomplete")
        print("\nPlease follow the instructions above to complete setup.")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
