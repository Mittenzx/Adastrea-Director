#!/usr/bin/env python3
"""
Document Ingestion Script for Adastrea Director

This script handles loading, processing, and embedding project documents
into a vector database for RAG-based question answering.

Embedding Providers:
- By default, uses HuggingFace embeddings (local, no API key required)
- To use OpenAI embeddings: set EMBEDDING_PROVIDER=openai (requires OPENAI_API_KEY)
- To customize HuggingFace model: set HUGGINGFACE_MODEL_NAME (default: all-MiniLM-L6-v2)

Features:
- Incremental ingestion: Only processes changed or new files (default)
- Hash-based change detection: Uses SHA-256 to detect file modifications
- Sequential processing: Processes files one-by-one to avoid rate limits
- Legacy mode: Option to load all files at once (use --legacy-mode)

Usage:
    # Incremental ingestion (default, recommended, uses HuggingFace embeddings)
    python ingest.py --docs-dir /path/to/docs
    
    # Use OpenAI embeddings instead
    export EMBEDDING_PROVIDER=openai
    export OPENAI_API_KEY=your-key
    python ingest.py --docs-dir /path/to/docs
    
    # Use a different HuggingFace model
    export HUGGINGFACE_MODEL_NAME=sentence-transformers/all-mpnet-base-v2
    python ingest.py --docs-dir /path/to/docs
    
    # Force re-ingestion of all files
    python ingest.py --docs-dir /path/to/docs --reingest
    
    # Legacy mode (load all files at once)
    python ingest.py --docs-dir /path/to/docs --legacy-mode
    
    # Single file
    python ingest.py --file single_doc.md
    
    # Custom collection name
    python ingest.py --docs-dir /path/to/docs --collection-name my_project
"""

import os
import sys
import argparse
import time
import random
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from exceptions import (
    APIKeyError,
    DatabaseError,
    NetworkError,
    RateLimitError,
    ChunkingError,
    ValidationError,
    FileEncodingError,
    CorruptedFileError,
)

# Disable ChromaDB telemetry BEFORE any imports that might import chromadb
# This prevents "capture() takes 1 positional argument but 3 were given" errors
# Must be set before langchain_community imports which internally import chromadb
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Force UTF-8 encoding for stdout/stderr to handle Unicode characters (emojis)
# This prevents encoding errors on Windows systems with cp1252 encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from dotenv import load_dotenv
    # Load environment variables immediately after import
    load_dotenv()
    
    from langchain_community.document_loaders import (
        DirectoryLoader,
        TextLoader,
        PythonLoader,
        PyPDFLoader,
        Docx2txtLoader,
    )
    from langchain_text_splitters import (
        RecursiveCharacterTextSplitter,
        Language,
    )
    from langchain_community.vectorstores import Chroma
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
    
    # Try to import UnstructuredMarkdownLoader, but fall back to TextLoader if not available
    try:
        from langchain_community.document_loaders import UnstructuredMarkdownLoader
        MARKDOWN_LOADER = UnstructuredMarkdownLoader
    except ImportError:
        # If unstructured is not installed, fall back to TextLoader for markdown files
        MARKDOWN_LOADER = TextLoader
        console_fallback = Console(legacy_windows=False)
        console_fallback.print(
            "[yellow]Note: 'unstructured' package not found. "
            "Markdown files will be loaded as plain text.[/yellow]"
        )
        console_fallback.print(
            "[yellow]For better markdown parsing, install: pip install unstructured[/yellow]"
        )
    
except ImportError as e:
    print(f"Error: Missing required dependencies. Please install requirements.txt")
    print(f"Details: {e}")
    print(f"\nTo install dependencies, run:")
    print(f"  pip install -r requirements.txt")
    print(f"\nOr use the setup script:")
    print(f"  ./setup.sh")
    sys.exit(1)

console = Console(legacy_windows=False)


class DocumentIngestionAgent:
    """Agent responsible for ingesting documents into the vector database."""

    def __init__(
        self,
        collection_name: str = "adastrea_docs",
        persist_directory: str = "./chroma_db",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embeddings = None,
    ):
        """
        Initialize the document ingestion agent.

        Args:
            collection_name: Name of the collection in the vector database
            persist_directory: Directory to persist the vector database
            chunk_size: Size of text chunks for embedding
            chunk_overlap: Overlap between chunks
            embeddings: Optional embeddings instance. If not provided, will use
                       EMBEDDING_PROVIDER environment variable to select provider.
                       Defaults to HuggingFace embeddings ('all-MiniLM-L6-v2').
            
        Raises:
            ValidationError: If chunk_size or chunk_overlap are invalid
            APIKeyError: If OpenAI is selected and API key is missing or invalid
        """
        # Validate configuration
        if chunk_size <= 0:
            raise ValidationError("chunk_size", chunk_size, "Must be greater than 0")
        
        if chunk_overlap < 0:
            raise ValidationError("chunk_overlap", chunk_overlap, "Must be non-negative")
        
        if chunk_overlap >= chunk_size:
            raise ValidationError(
                "chunk_overlap", 
                chunk_overlap, 
                f"Must be less than chunk_size ({chunk_size})"
            )
        
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Initialize embeddings
        if embeddings is not None:
            # Use provided embeddings
            self.embeddings = embeddings
        else:
            # Determine which embedding provider to use
            embedding_provider = os.environ.get("EMBEDDING_PROVIDER", "hf").lower()
            
            if embedding_provider == "openai":
                # Use OpenAI embeddings
                try:
                    from langchain_openai import OpenAIEmbeddings
                    self.embeddings = OpenAIEmbeddings()
                except ImportError as e:
                    console.print(
                        "[red]Error: OpenAI embeddings require 'langchain-openai' package[/red]"
                    )
                    console.print(
                        "[yellow]Install it with: pip install langchain-openai[/yellow]"
                    )
                    sys.exit(1)
                except Exception as e:
                    error_msg = str(e).lower()
                    if "api" in error_msg and "key" in error_msg:
                        raise APIKeyError("OpenAI", str(e))
                    console.print(
                        f"[red]Error initializing OpenAI embeddings: {e}[/red]"
                    )
                    console.print(
                        "[yellow]Make sure OPENAI_API_KEY is set in your environment[/yellow]"
                    )
                    sys.exit(1)
            else:
                # Use HuggingFace embeddings (default)
                model_name = os.environ.get("HUGGINGFACE_MODEL_NAME", "all-MiniLM-L6-v2")
                try:
                    # Try the newer langchain-huggingface package first
                    try:
                        from langchain_huggingface import HuggingFaceEmbeddings
                    except ImportError:
                        # Fall back to langchain_community if the newer package isn't available
                        from langchain_community.embeddings import HuggingFaceEmbeddings
                    
                    self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
                    console.print(
                        f"[cyan]Using HuggingFace embeddings with model: {model_name}[/cyan]"
                    )
                except ImportError as e:
                    console.print(
                        "[red]Error: HuggingFace embeddings require 'sentence-transformers' package[/red]"
                    )
                    console.print(
                        "[yellow]Install it with: pip install sentence-transformers[/yellow]"
                    )
                    console.print(
                        "[yellow]Or install the langchain-huggingface package: pip install langchain-huggingface[/yellow]"
                    )
                    console.print(
                        "[yellow]Or to use OpenAI instead, set: EMBEDDING_PROVIDER=openai[/yellow]"
                    )
                    sys.exit(1)
                except Exception as e:
                    console.print(
                        f"[red]Error initializing HuggingFace embeddings: {e}[/red]"
                    )
                    console.print(
                        f"[yellow]Model: {model_name}[/yellow]"
                    )
                    console.print(
                        "[yellow]Try setting HUGGINGFACE_MODEL_NAME to a different model[/yellow]"
                    )
                    console.print(
                        "[yellow]Or use OpenAI instead: EMBEDDING_PROVIDER=openai[/yellow]"
                    )
                    sys.exit(1)

        # Initialize text splitter (default for markdown and text)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )
        
        # Initialize code-specific text splitters for different languages
        self.code_splitters = {
            Language.PYTHON: RecursiveCharacterTextSplitter.from_language(
                language=Language.PYTHON,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            ),
            Language.JS: RecursiveCharacterTextSplitter.from_language(
                language=Language.JS,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            ),
            Language.TS: RecursiveCharacterTextSplitter.from_language(
                language=Language.TS,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            ),
            Language.CPP: RecursiveCharacterTextSplitter.from_language(
                language=Language.CPP,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            ),
            Language.CSHARP: RecursiveCharacterTextSplitter.from_language(
                language=Language.CSHARP,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            ),
        }

    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of a file's content.
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA-256 hash as a hexadecimal string
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files efficiently
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            console.print(f"[yellow]Warning: Could not calculate hash for {file_path}: {e}[/yellow]")
            return ""

    def _check_file_changed(
        self, file_path: str, force_reingest: bool = False
    ) -> Tuple[bool, Optional[str], str]:
        """
        Check if a file has changed by comparing its hash with stored metadata.
        
        Args:
            file_path: Path to the file to check
            force_reingest: If True, always treat file as changed
            
        Returns:
            Tuple of (has_changed, old_hash, current_hash). 
            has_changed is True if file should be processed.
        """
        # Calculate current file hash
        current_hash = self._calculate_file_hash(file_path)
        
        if force_reingest:
            return True, None, current_hash
            
        if not current_hash:
            # If we can't calculate hash, process the file to be safe
            return True, None, ""
        
        try:
            # Query ChromaDB for existing documents with this source
            vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )
            
            # Get documents by source metadata
            collection = vectorstore._collection
            results = collection.get(
                where={"source": file_path},
                limit=1,
                include=["metadatas"]
            )
            
            if results and results.get("metadatas") and len(results["metadatas"]) > 0:
                # File exists in database, check hash
                stored_metadata = results["metadatas"][0]
                stored_hash = stored_metadata.get("file_hash", "")
                
                if stored_hash == current_hash:
                    # File unchanged
                    return False, stored_hash, current_hash
                else:
                    # File changed
                    return True, stored_hash, current_hash
            else:
                # File not in database, needs to be added
                return True, None, current_hash
                
        except Exception as e:
            # If database doesn't exist yet or there's an error, process the file
            return True, None, current_hash

    def _delete_document_by_source(self, source: str) -> bool:
        """
        Delete all document chunks for a given source file.
        
        Args:
            source: Source file path to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )
            
            collection = vectorstore._collection
            # Get all IDs for documents with this source
            results = collection.get(
                where={"source": source},
                include=["documents"]
            )
            
            if results and results.get("ids"):
                ids_to_delete = results["ids"]
                collection.delete(ids=ids_to_delete)
                console.print(f"[dim]  Deleted {len(ids_to_delete)} old chunks[/dim]")
                return True
            
            return False
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not delete old chunks for {source}: {e}[/yellow]")
            return False

    def _enrich_document_metadata(self, documents: List[Any], file_hash: Optional[str] = None) -> List[Any]:
        """
        Enrich document metadata with additional information.
        
        Args:
            documents: List of documents to enrich
            file_hash: Optional SHA-256 hash of the file content
            
        Returns:
            List of documents with enriched metadata
        """
        for doc in documents:
            try:
                source = doc.metadata.get("source", "")
                if source and isinstance(source, str):
                    source_path = Path(source)
                    
                    # Add file information
                    doc.metadata["filename"] = source_path.name
                    doc.metadata["extension"] = source_path.suffix.lower()
                    
                    # Add file hash if provided
                    if file_hash:
                        doc.metadata["file_hash"] = file_hash
                    else:
                        # Calculate hash if not provided
                        calculated_hash = self._calculate_file_hash(source)
                        if calculated_hash:
                            doc.metadata["file_hash"] = calculated_hash
                    
                    # Detect document type
                    extension = source_path.suffix.lower()
                    if extension in [".md", ".txt"]:
                        doc.metadata["doc_type"] = "documentation"
                    elif extension in [".pdf", ".docx"]:
                        doc.metadata["doc_type"] = "document"
                    elif extension in [".py", ".js", ".jsx", ".ts", ".tsx", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".cs"]:
                        doc.metadata["doc_type"] = "code"
                    elif extension in [".json", ".yaml", ".yml"]:
                        doc.metadata["doc_type"] = "config"
                    else:
                        doc.metadata["doc_type"] = "other"
                    
                    # Detect programming language for code files
                    language = self._detect_language(source)
                    if language:
                        doc.metadata["language"] = language.value
                    
                    # Add file size if available
                    try:
                        if source_path.exists():
                            doc.metadata["file_size"] = source_path.stat().st_size
                    except (OSError, IOError):
                        # Ignore file system errors when getting file size
                        pass
            except Exception as e:
                # Skip metadata enrichment if there's any error
                source = doc.metadata.get("source", "unknown")
                console.print(f"[yellow]Warning: Failed to enrich metadata for '{source}': {e}[/yellow]")
        
        return documents

    def _get_file_list(self, directory: str) -> List[str]:
        """
        Get a list of all supported files in a directory.
        
        Args:
            directory: Path to directory
            
        Returns:
            List of file paths
        """
        directory_path = Path(directory)
        supported_extensions = {
            ".md", ".txt", ".pdf", ".docx",
            ".py", ".js", ".jsx", ".ts", ".tsx",
            ".cpp", ".cc", ".cxx", ".h", ".hpp", ".cs",
            ".json", ".yaml", ".yml"
        }
        
        file_list = []
        for ext in supported_extensions:
            file_list.extend(directory_path.glob(f"**/*{ext}"))
        
        return [str(f) for f in file_list]

    def load_documents_from_directory(self, directory: str) -> List[Any]:
        """
        Load documents from a directory.

        Args:
            directory: Path to directory containing documents

        Returns:
            List of loaded documents
        """
        documents = []
        directory_path = Path(directory)

        if not directory_path.exists():
            console.print(f"[red]Error: Directory {directory} does not exist[/red]")
            return documents

        # Define loaders for different file types
        loader_mapping = {
            # Documentation files
            ".md": MARKDOWN_LOADER,  # Will be UnstructuredMarkdownLoader or TextLoader
            ".txt": TextLoader,
            ".pdf": PyPDFLoader,
            ".docx": Docx2txtLoader,
            # Code files - Python
            ".py": PythonLoader,
            # Code files - JavaScript/TypeScript (use TextLoader for now)
            ".js": TextLoader,
            ".jsx": TextLoader,
            ".ts": TextLoader,
            ".tsx": TextLoader,
            # Code files - C++
            ".cpp": TextLoader,
            ".cc": TextLoader,
            ".cxx": TextLoader,
            ".h": TextLoader,
            ".hpp": TextLoader,
            # Code files - C#
            ".cs": TextLoader,
            # Config files
            ".json": TextLoader,
            ".yaml": TextLoader,
            ".yml": TextLoader,
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading documents...", total=None)

            for extension, loader_class in loader_mapping.items():
                try:
                    loader = DirectoryLoader(
                        directory,
                        glob=f"**/*{extension}",
                        loader_cls=loader_class,
                        show_progress=False,
                        silent_errors=True,  # Continue loading even if some files fail
                    )
                    docs = loader.load()
                    documents.extend(docs)
                    if len(docs) > 0:
                        progress.update(
                            task,
                            description=f"✓ Loaded {len(docs)} {extension} files",
                        )
                except UnicodeDecodeError as e:
                    console.print(
                        f"[yellow]Warning: Encoding error in {extension} files. "
                        f"Some files may have been skipped due to encoding issues.[/yellow]"
                    )
                except ImportError as e:
                    console.print(
                        f"[yellow]Warning: Missing dependency for {extension} files: {e}[/yellow]"
                    )
                    console.print(
                        f"[yellow]Install the required package to load {extension} files.[/yellow]"
                    )
                except PermissionError as e:
                    console.print(
                        f"[yellow]Warning: Permission denied when loading {extension} files.[/yellow]"
                    )
                    console.print(
                        f"[yellow]Check file permissions in the directory.[/yellow]"
                    )
                except Exception as e:
                    console.print(
                        f"[yellow]Warning: Error loading {extension} files: {e}[/yellow]"
                    )

        # Enrich metadata for loaded documents
        documents = self._enrich_document_metadata(documents)
        
        return documents

    def load_single_file(self, file_path: str) -> List[Any]:
        """
        Load a single document file.

        Args:
            file_path: Path to the file

        Returns:
            List containing the loaded document
        """
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            console.print(f"[red]Error: File {file_path} does not exist[/red]")
            return []

        # Determine loader based on extension
        extension = file_path_obj.suffix.lower()
        loader_mapping = {
            # Documentation files
            ".md": MARKDOWN_LOADER,  # Will be UnstructuredMarkdownLoader or TextLoader
            ".txt": TextLoader,
            ".pdf": PyPDFLoader,
            ".docx": Docx2txtLoader,
            # Code files - Python
            ".py": PythonLoader,
            # Code files - JavaScript/TypeScript
            ".js": TextLoader,
            ".jsx": TextLoader,
            ".ts": TextLoader,
            ".tsx": TextLoader,
            # Code files - C++
            ".cpp": TextLoader,
            ".cc": TextLoader,
            ".cxx": TextLoader,
            ".h": TextLoader,
            ".hpp": TextLoader,
            # Code files - C#
            ".cs": TextLoader,
            # Config files
            ".json": TextLoader,
            ".yaml": TextLoader,
            ".yml": TextLoader,
        }

        loader_class = loader_mapping.get(extension, TextLoader)

        try:
            loader = loader_class(file_path)
            documents = loader.load()
            console.print(f"[green]Loaded {file_path}[/green]")
            # Enrich metadata for loaded document
            documents = self._enrich_document_metadata(documents)
            return documents
        except UnicodeDecodeError as e:
            error = FileEncodingError(file_path)
            console.print(f"[red]{error.message}[/red]")
            console.print(f"[yellow]{error.details}[/yellow]")
            return []
        except ImportError as e:
            # Map file extensions to correct package names
            package_mapping = {
                ".pdf": "pypdf",
                ".docx": "python-docx",
                ".md": "unstructured",
            }
            package_name = package_mapping.get(extension, extension.replace('.', ''))
            console.print(f"[red]Error: Missing required library to load {extension} files[/red]")
            console.print(f"[yellow]Details: {e}[/yellow]")
            console.print(f"[yellow]Install the required package using: pip install {package_name}[/yellow]")
            return []
        except PermissionError as e:
            console.print(f"[red]Error: Permission denied for file: {file_path}[/red]")
            console.print(f"[yellow]Check that you have read permissions for this file[/yellow]")
            return []
        except FileNotFoundError as e:
            console.print(f"[red]Error: File not found during loading: {file_path}[/red]")
            console.print(f"[yellow]The file may have been moved or deleted[/yellow]")
            return []
        except Exception as e:
            # Try to provide more specific error messages based on file type
            error_msg = str(e).lower()
            if extension == ".pdf" and ("pdf" in error_msg or "parse" in error_msg):
                error = CorruptedFileError(file_path, "PDF")
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
            elif extension == ".docx" and ("docx" in error_msg or "xml" in error_msg):
                error = CorruptedFileError(file_path, "DOCX")
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
            else:
                console.print(f"[red]Error loading file: {e}[/red]")
                console.print(f"[yellow]File: {file_path}[/yellow]")
            return []

    def ingest_directory_incremental(
        self,
        directory: str,
        force_reingest: bool = False,
        delay_between_files: float = 1.0
    ) -> Dict[str, Any]:
        """
        Ingest documents from a directory incrementally, processing one file at a time.
        
        This method:
        1. Discovers all files in the directory
        2. For each file, checks if it has changed (via hash comparison)
        3. Skips unchanged files
        4. Deletes old chunks and re-ingests changed files
        5. Adds new files
        
        Args:
            directory: Path to directory containing documents
            force_reingest: If True, re-ingest all files regardless of changes
            delay_between_files: Delay in seconds between processing files (default: 1.0)
            
        Returns:
            Dictionary with statistics about the ingestion process
        """
        stats = {
            "total_files": 0,
            "skipped": 0,
            "updated": 0,
            "added": 0,
            "errors": 0,
        }
        
        directory_path = Path(directory)
        if not directory_path.exists():
            console.print(f"[red]Error: Directory {directory} does not exist[/red]")
            return stats
        
        # Get list of all files
        file_list = self._get_file_list(directory)
        stats["total_files"] = len(file_list)
        
        if not file_list:
            console.print(f"[yellow]No supported files found in {directory}[/yellow]")
            return stats
        
        console.print(f"\n[cyan]Found {len(file_list)} files to process[/cyan]")
        if force_reingest:
            console.print(f"[yellow]Force re-ingestion enabled - all files will be processed[/yellow]\n")
        else:
            console.print(f"[cyan]Checking for changes...[/cyan]\n")
        
        from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Processing files...",
                total=len(file_list)
            )
            
            for file_path in file_list:
                try:
                    # Check if file has changed
                    has_changed, old_hash, current_hash = self._check_file_changed(file_path, force_reingest)
                    
                    if not has_changed:
                        # File unchanged, skip
                        stats["skipped"] += 1
                        progress.update(
                            task,
                            advance=1,
                            description=f"[dim]⊘ Skipped (unchanged): {Path(file_path).name}[/dim]"
                        )
                        continue
                    
                    # Load the file
                    documents = self.load_single_file(file_path)
                    
                    if not documents:
                        stats["errors"] += 1
                        progress.update(task, advance=1)
                        continue
                    
                    # Enrich metadata with hash
                    documents = self._enrich_document_metadata(documents, file_hash=current_hash)
                    
                    # Chunk the documents
                    chunks = self.chunk_documents(documents)
                    
                    if not chunks:
                        stats["errors"] += 1
                        progress.update(task, advance=1)
                        continue
                    
                    # If file exists in DB, delete old chunks first
                    if old_hash is not None:
                        self._delete_document_by_source(file_path)
                        stats["updated"] += 1
                        action = "↻ Updated"
                    else:
                        stats["added"] += 1
                        action = "+ Added"
                    
                    # Ingest the chunks
                    try:
                        # Check if database exists
                        if not Path(self.persist_directory).exists():
                            # Database doesn't exist, create it
                            vectorstore = Chroma.from_documents(
                                documents=chunks,
                                embedding=self.embeddings,
                                collection_name=self.collection_name,
                                persist_directory=self.persist_directory,
                            )
                        else:
                            # Add to existing database
                            vectorstore = Chroma(
                                collection_name=self.collection_name,
                                embedding_function=self.embeddings,
                                persist_directory=self.persist_directory,
                            )
                            vectorstore.add_documents(chunks)
                        
                        vectorstore.persist()
                        
                        progress.update(
                            task,
                            advance=1,
                            description=f"[green]{action}: {Path(file_path).name} ({len(chunks)} chunks)[/green]"
                        )
                        
                        # Add delay between files to avoid rate limiting
                        if delay_between_files > 0:
                            time.sleep(delay_between_files)
                            
                    except Exception as e:
                        stats["errors"] += 1
                        error_msg = str(e).lower()
                        if "rate" in error_msg and "limit" in error_msg:
                            console.print(f"[red]✗ Rate limit error for {Path(file_path).name}[/red]")
                            console.print(f"[yellow]Consider increasing --delay parameter[/yellow]")
                        else:
                            console.print(f"[red]✗ Error ingesting {Path(file_path).name}: {e}[/red]")
                        progress.update(task, advance=1)
                        
                except Exception as e:
                    stats["errors"] += 1
                    console.print(f"[red]✗ Error processing {Path(file_path).name}: {e}[/red]")
                    progress.update(task, advance=1)
        
        return stats

    def _detect_language(self, source: str) -> Language:
        """
        Detect the programming language based on file extension.
        
        Args:
            source: Source file path
            
        Returns:
            Language enum or None if not a code file
        """
        extension = Path(source).suffix.lower()
        language_map = {
            ".py": Language.PYTHON,
            ".js": Language.JS,
            ".jsx": Language.JS,
            ".ts": Language.TS,
            ".tsx": Language.TS,
            ".cpp": Language.CPP,
            ".cc": Language.CPP,
            ".cxx": Language.CPP,
            ".h": Language.CPP,
            ".hpp": Language.CPP,
            ".cs": Language.CSHARP,
        }
        return language_map.get(extension)

    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        """
        Split documents into chunks using document-type aware strategies.

        Args:
            documents: List of documents to chunk

        Returns:
            List of document chunks
            
        Raises:
            ChunkingError: If chunking fails
        """
        if not documents:
            return []

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Chunking documents...", total=None)
                
                # Separate documents by language for optimized chunking
                docs_by_language = {lang: [] for lang in self.code_splitters.keys()}
                text_docs = []
                
                for doc in documents:
                    source = doc.metadata.get("source", "")
                    language = self._detect_language(source)
                    
                    if language and language in self.code_splitters:
                        docs_by_language[language].append(doc)
                    else:
                        text_docs.append(doc)
                
                # Chunk with appropriate splitters
                chunks = []
                code_doc_count = 0
                
                # Process code documents with language-specific splitters
                for language, docs in docs_by_language.items():
                    if docs:
                        chunks.extend(self.code_splitters[language].split_documents(docs))
                        code_doc_count += len(docs)
                
                # Process text documents
                if text_docs:
                    chunks.extend(self.text_splitter.split_documents(text_docs))
                
                progress.update(
                    task,
                    description=f"Created {len(chunks)} chunks from {len(documents)} documents "
                               f"({code_doc_count} code, {len(text_docs)} text)",
                )

            return chunks
        except AttributeError as e:
            raise ChunkingError(
                "Invalid document format",
                "One or more documents are not in the expected format. "
                "Ensure all documents have 'page_content' and 'metadata' attributes."
            )
        except MemoryError as e:
            raise ChunkingError(
                "Out of memory",
                "The documents are too large to process. Try:\n"
                "  - Processing fewer documents at once\n"
                "  - Reducing the chunk_size parameter\n"
                "  - Increasing available system memory"
            )
        except Exception as e:
            raise ChunkingError(str(e))

    def _process_batch(self, batch: List[Any], is_first_batch: bool, max_retries: int = 8) -> Any:
        """
        Process a single batch of documents with retry logic for rate limits.
        
        Implements OpenAI's recommended retry strategy with exponential backoff and jitter:
        https://platform.openai.com/docs/guides/rate-limits/retrying-with-exponential-backoff
        
        Args:
            batch: Documents to process
            is_first_batch: Whether this is the first batch
            max_retries: Maximum number of retries for rate limit errors (default: 8)
            
        Returns:
            The vectorstore instance
            
        Raises:
            Exception: If all retries are exhausted
        """
        retry_count = 0
        last_error = None
        
        while retry_count <= max_retries:
            try:
                if is_first_batch:
                    vectorstore = Chroma.from_documents(
                        documents=batch,
                        embedding=self.embeddings,
                        collection_name=self.collection_name,
                        persist_directory=self.persist_directory,
                    )
                else:
                    vectorstore = Chroma(
                        collection_name=self.collection_name,
                        embedding_function=self.embeddings,
                        persist_directory=self.persist_directory,
                    )
                    vectorstore.add_documents(batch)
                
                # Persist after each batch
                vectorstore.persist()
                return vectorstore
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a quota exhaustion error (should NOT retry)
                # Quota errors won't resolve with retries - need to add credits or wait longer
                is_quota_exceeded = any(phrase in error_msg for phrase in [
                    "insufficient_quota", "quota exceeded", "exceeded your current quota"
                ])
                
                if is_quota_exceeded:
                    # Fail immediately on quota errors - retrying won't help
                    console.print(
                        f"[red]✗ OpenAI API quota exhausted. Retrying will not help.[/red]"
                    )
                    console.print(
                        f"[yellow]Recommendations:[/yellow]"
                    )
                    console.print(
                        f"[yellow]  1. Check your billing and add credits: https://platform.openai.com/account/billing[/yellow]"
                    )
                    console.print(
                        f"[yellow]  2. Check your usage limits: https://platform.openai.com/account/limits[/yellow]"
                    )
                    console.print(
                        f"[yellow]  3. Wait for quota reset (quotas reset monthly or per billing cycle)[/yellow]"
                    )
                    raise e
                
                # Check if it's a temporary rate limit error (should retry)
                is_rate_limit = any(phrase in error_msg for phrase in [
                    "rate limit", "rate_limit_exceeded", "429", "too many requests"
                ])
                
                if is_rate_limit:
                    retry_count += 1
                    if retry_count <= max_retries:
                        # Exponential backoff with jitter (OpenAI best practices)
                        # Base wait time: 1, 2, 4, 8, 16, 32, 64, 64 seconds (capped at 60)
                        # Add random jitter (0-100% of base wait) to prevent thundering herd
                        base_wait = min(2 ** (retry_count - 1), 60)
                        jitter = random.uniform(0, base_wait)
                        wait_time = base_wait + jitter
                        console.print(
                            f"[yellow]⚠ Rate limit hit. Waiting {wait_time:.1f} seconds before retry "
                            f"({retry_count}/{max_retries})...[/yellow]"
                        )
                        time.sleep(wait_time)
                        last_error = e
                    else:
                        # All retries exhausted
                        console.print(
                            f"[red]✗ Rate limit retries exhausted after {max_retries} attempts.[/red]"
                        )
                        console.print(
                            f"[yellow]Recommendations:[/yellow]"
                        )
                        console.print(
                            f"[yellow]  1. Use longer delays: --delay 5.0 or --delay 10.0[/yellow]"
                        )
                        console.print(
                            f"[yellow]  2. Use smaller batches: --batch-size 10 or --batch-size 5[/yellow]"
                        )
                        console.print(
                            f"[yellow]  3. Wait a few minutes and try again (API quotas reset over time)[/yellow]"
                        )
                        console.print(
                            f"[yellow]  4. Check OpenAI usage limits at: https://platform.openai.com/account/limits[/yellow]"
                        )
                        console.print(
                            f"[dim]Note: Using exponential backoff with jitter per OpenAI best practices[/dim]"
                        )
                        raise e
                else:
                    # Not a rate limit error, raise immediately
                    raise e
        
        # Should not reach here, but just in case
        if last_error:
            raise last_error
        else:
            raise RuntimeError("Unexpected: _process_batch completed without returning or raising an exception")

    def ingest_documents_batch(
        self, 
        documents: List[Any], 
        batch_size: int = 50,
        show_progress: bool = True,
        delay_between_batches: float = 2.0
    ) -> bool:
        """
        Ingest documents into the vector database in batches.
        
        This method is more memory efficient for large document sets
        and provides better progress tracking. It also includes rate limiting
        to avoid hitting OpenAI API rate limits.

        Args:
            documents: List of documents to ingest
            batch_size: Number of documents to process in each batch
            show_progress: Whether to show progress bar
            delay_between_batches: Seconds to wait between batches (default: 2.0)
                                   Helps avoid rate limiting. Use 3.0+ for very large batches.

        Returns:
            True if successful, False otherwise
        """
        if not documents:
            console.print("[yellow]No documents to ingest[/yellow]")
            return False

        try:
            total_batches = (len(documents) + batch_size - 1) // batch_size
            
            if show_progress:
                from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
                
                with Progress(
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeRemainingColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task(
                        f"Ingesting {len(documents)} documents in {total_batches} batches...",
                        total=len(documents)
                    )
                    
                    for i in range(0, len(documents), batch_size):
                        batch = documents[i:i + batch_size]
                        batch_num = (i // batch_size) + 1
                        
                        # Process the batch
                        self._process_batch(batch, is_first_batch=(i == 0))
                        progress.update(task, advance=len(batch))
                        
                        # Add delay between batches to avoid rate limiting (except after last batch)
                        if i + batch_size < len(documents):
                            time.sleep(delay_between_batches)
            else:
                # No progress bar
                for i in range(0, len(documents), batch_size):
                    batch = documents[i:i + batch_size]
                    batch_num = (i // batch_size) + 1
                    
                    self._process_batch(batch, is_first_batch=(i == 0))
                    
                    # Add delay between batches to avoid rate limiting (except after last batch)
                    if i + batch_size < len(documents):
                        time.sleep(delay_between_batches)

            console.print(
                f"[green]✓ Successfully ingested {len(documents)} documents![/green]"
            )
            console.print(
                f"[cyan]Collection: {self.collection_name}[/cyan]"
            )
            console.print(
                f"[cyan]Storage: {self.persist_directory}[/cyan]"
            )
            return True

        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for quota exceeded errors (429)
            if "quota" in error_msg or "insufficient_quota" in error_msg or "429" in str(e):
                console.print(f"[red]✗ OpenAI API Rate Limit or Quota Exceeded[/red]")
                console.print(f"[yellow]You have hit OpenAI API limits (rate limiting or quota).[/yellow]")
                console.print(f"[yellow]\nRecommended Solutions (in order):[/yellow]")
                console.print(f"[yellow]  1. Use smaller batches with longer delays:[/yellow]")
                console.print(f"[cyan]     python ingest.py --docs-dir <path> --batch-size 10 --delay 5.0[/cyan]")
                console.print(f"[yellow]  2. For very strict limits, use even smaller batches:[/yellow]")
                console.print(f"[cyan]     python ingest.py --docs-dir <path> --batch-size 5 --delay 10.0[/cyan]")
                console.print(f"[yellow]  3. Check your OpenAI usage and limits:[/yellow]")
                console.print(f"[cyan]     https://platform.openai.com/account/limits[/cyan]")
                console.print(f"[yellow]  4. Check your billing and add credits:[/yellow]")
                console.print(f"[cyan]     https://platform.openai.com/account/billing[/cyan]")
                console.print(f"[yellow]  5. Wait 5-10 minutes and try again with conservative settings[/yellow]")
                console.print(f"[yellow]\nNote: The system includes automatic retries (up to 8 attempts) with exponential backoff and jitter per OpenAI best practices.[/yellow]")
                console.print(f"[dim]Error details: {e}[/dim]")
            # Check for rate limit errors
            elif "rate" in error_msg and "limit" in error_msg:
                error = RateLimitError(service="OpenAI API")
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
            # Check for API key errors
            elif "api" in error_msg and "key" in error_msg:
                error = APIKeyError("OpenAI")
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
            # Check for network/connection errors
            elif any(word in error_msg for word in ["connection", "network", "timeout"]):
                error = NetworkError("batch ingestion")
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
            # Check for database errors
            elif any(word in error_msg for word in ["chroma", "database", "persist"]):
                error = DatabaseError("batch ingestion", str(e))
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
            else:
                console.print(f"[red]Error during batch ingestion: {e}[/red]")
            
            return False

    def ingest_documents(self, documents: List[Any]) -> bool:
        """
        Ingest documents into the vector database.

        Args:
            documents: List of documents to ingest

        Returns:
            True if successful, False otherwise
        """
        if not documents:
            console.print("[yellow]No documents to ingest[/yellow]")
            return False

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Creating embeddings and storing...", total=None)

                # Create vector store
                vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    collection_name=self.collection_name,
                    persist_directory=self.persist_directory,
                )

                # Persist the database
                vectorstore.persist()

                progress.update(
                    task,
                    description=f"Successfully ingested {len(documents)} chunks",
                )

            console.print(
                f"[green]✓ Documents ingested successfully![/green]"
            )
            console.print(
                f"[cyan]Collection: {self.collection_name}[/cyan]"
            )
            console.print(
                f"[cyan]Storage: {self.persist_directory}[/cyan]"
            )
            return True

        except TimeoutError as e:
            error = NetworkError("embedding generation", 
                "The OpenAI API request timed out. This usually means:\n"
                "  - The API is experiencing high load\n"
                "  - Your internet connection is slow\n"
                "Try again in a few moments."
            )
            console.print(f"[red]{error.message}[/red]")
            console.print(f"[yellow]{error.details}[/yellow]")
            return False
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for quota exceeded errors (429)
            if "quota" in error_msg or "insufficient_quota" in error_msg or "429" in str(e):
                console.print(f"[red]✗ OpenAI API Rate Limit or Quota Exceeded[/red]")
                console.print(f"[yellow]You have hit OpenAI API limits (rate limiting or quota).[/yellow]")
                console.print(f"[yellow]\nRecommended Solutions (in order):[/yellow]")
                console.print(f"[yellow]  1. Use batch processing with conservative settings:[/yellow]")
                console.print(f"[cyan]     python ingest.py --docs-dir <path> --use-batch --batch-size 25 --delay 5.0[/cyan]")
                console.print(f"[yellow]  2. For very strict limits:[/yellow]")
                console.print(f"[cyan]     python ingest.py --docs-dir <path> --use-batch --batch-size 10 --delay 10.0[/cyan]")
                console.print(f"[yellow]  3. Check your OpenAI usage and limits:[/yellow]")
                console.print(f"[cyan]     https://platform.openai.com/account/limits[/cyan]")
                console.print(f"[yellow]  4. Check your billing and add credits:[/yellow]")
                console.print(f"[cyan]     https://platform.openai.com/account/billing[/cyan]")
                console.print(f"[yellow]  5. Wait 5-10 minutes and try again[/yellow]")
                console.print(f"[yellow]\nNote: The system includes automatic retries (up to 5 attempts) with exponential backoff.[/yellow]")
                console.print(f"[dim]Error details: {e}[/dim]")
            # Check for rate limit errors
            elif "rate" in error_msg and "limit" in error_msg:
                error = RateLimitError(service="OpenAI API")
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
            # Check for API key errors
            elif "api" in error_msg and "key" in error_msg:
                error = APIKeyError("OpenAI")
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
            # Check for network/connection errors
            elif any(word in error_msg for word in ["connection", "network", "timeout"]):
                error = NetworkError("database ingestion")
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
            # Check for database errors
            elif any(word in error_msg for word in ["chroma", "database", "persist"]):
                error = DatabaseError("ingestion", str(e))
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
            else:
                console.print(f"[red]Error ingesting documents: {e}[/red]")
            
            return False

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current database.

        Returns:
            Dictionary with database statistics
        """
        try:
            vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )

            collection = vectorstore._collection
            count = collection.count()

            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory,
            }
        except Exception as e:
            console.print(f"[yellow]Could not retrieve stats: {e}[/yellow]")
            return {}


def main():
    """Main entry point for the ingestion script."""
    parser = argparse.ArgumentParser(
        description="Ingest documents into Adastrea Director knowledge base"
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        help="Directory containing documents to ingest",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Single file to ingest",
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="adastrea_docs",
        help="Name for the document collection (default: adastrea_docs)",
    )
    parser.add_argument(
        "--persist-dir",
        type=str,
        default="./chroma_db",
        help="Directory to persist the database (default: ./chroma_db)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Size of text chunks (default: 1000)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Overlap between chunks (default: 200)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show database statistics",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for processing large document sets (default: 50). "
             "Use 25 or lower if you encounter rate limits.",
    )
    parser.add_argument(
        "--use-batch",
        action="store_true",
        help="Use batch processing mode (recommended for large document sets)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay in seconds between batches to avoid rate limiting (default: 2.0). "
             "Use 3.0+ for very large document sets or if you hit rate limits.",
    )
    parser.add_argument(
        "--reingest",
        action="store_true",
        help="Force re-ingestion of all documents, ignoring change detection. "
             "Useful for clearing out old data or recovering from corrupted database.",
    )
    parser.add_argument(
        "--legacy-mode",
        action="store_true",
        help="Use legacy ingestion mode (load all files at once). "
             "By default, incremental mode is used.",
    )

    args = parser.parse_args()

    # Print banner
    console.print("\n[bold cyan]🤖 Adastrea Director - Document Ingestion[/bold cyan]\n")

    # Initialize agent
    agent = DocumentIngestionAgent(
        collection_name=args.collection_name,
        persist_directory=args.persist_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    # Show stats if requested
    if args.stats:
        stats = agent.get_database_stats()
        if stats:
            rprint("\n[bold]Database Statistics:[/bold]")
            rprint(f"  Collection: [cyan]{stats['collection_name']}[/cyan]")
            rprint(f"  Documents: [cyan]{stats['document_count']}[/cyan]")
            rprint(f"  Location: [cyan]{stats['persist_directory']}[/cyan]")
        return

    # Check if either docs-dir or file is provided
    if not args.docs_dir and not args.file:
        console.print(
            "[red]Error: Please provide either --docs-dir or --file[/red]"
        )
        parser.print_help()
        sys.exit(1)

    # Use incremental ingestion by default for directories (unless legacy mode is enabled)
    if args.docs_dir and not args.legacy_mode:
        console.print(f"[cyan]Processing directory: {args.docs_dir}[/cyan]")
        console.print(f"[cyan]Mode: Incremental (file-by-file)[/cyan]\n")
        
        stats = agent.ingest_directory_incremental(
            args.docs_dir,
            force_reingest=args.reingest,
            delay_between_files=args.delay
        )
        
        # Print summary
        console.print("\n[bold]Ingestion Summary:[/bold]")
        console.print(f"  Total files: [cyan]{stats['total_files']}[/cyan]")
        console.print(f"  Skipped (unchanged): [dim]{stats['skipped']}[/dim]")
        console.print(f"  Updated: [yellow]{stats['updated']}[/yellow]")
        console.print(f"  Added: [green]{stats['added']}[/green]")
        if stats['errors'] > 0:
            console.print(f"  Errors: [red]{stats['errors']}[/red]")
        
        if stats['added'] > 0 or stats['updated'] > 0:
            console.print("\n[bold green]✓ Ingestion complete![/bold green]")
            console.print(
                "\n[cyan]You can now run the main assistant with:[/cyan] python main.py\n"
            )
        elif stats['skipped'] > 0:
            console.print("\n[bold green]✓ All files up to date![/bold green]")
            console.print("[cyan]No changes detected. Database is current.\n")
        else:
            console.print("\n[bold yellow]⚠ No files were processed[/bold yellow]\n")
            sys.exit(1)
        
        return
    
    # Legacy mode or single file processing
    if args.legacy_mode and args.docs_dir:
        console.print(f"[yellow]Using legacy mode (load all files at once)[/yellow]\n")
    
    # Warn if --reingest or --legacy-mode used with --file
    if args.file and (args.reingest or args.legacy_mode):
        console.print(
            "[yellow]Note: --reingest and --legacy-mode flags have no effect "
            "when using --file for single file ingestion[/yellow]\n"
        )
    
    # Load documents
    documents = []
    if args.docs_dir:
        console.print(f"[cyan]Loading documents from: {args.docs_dir}[/cyan]\n")
        documents = agent.load_documents_from_directory(args.docs_dir)
    elif args.file:
        console.print(f"[cyan]Loading file: {args.file}[/cyan]\n")
        documents = agent.load_single_file(args.file)

    if not documents:
        console.print("[red]No documents loaded. Exiting.[/red]")
        sys.exit(1)

    console.print(f"\n[green]Loaded {len(documents)} documents[/green]\n")

    # Chunk documents
    chunks = agent.chunk_documents(documents)

    if not chunks:
        console.print("[red]No chunks created. Exiting.[/red]")
        sys.exit(1)

    console.print(f"\n[green]Created {len(chunks)} chunks[/green]\n")

    # Ingest documents (use batch mode for large sets or if explicitly requested)
    if args.use_batch or len(chunks) > 200:
        if not args.use_batch:
            console.print(
                f"[yellow]Detected {len(chunks)} chunks. Automatically using batch processing.[/yellow]\n"
            )
        
        # Recommend longer delay for very large document sets
        delay = args.delay
        if len(chunks) > 1000 and delay < 3.0:
            console.print(
                f"[yellow]Note: Processing {len(chunks)} chunks. Consider using --delay 3.0 or higher "
                f"to avoid rate limits.[/yellow]\n"
            )
        elif len(chunks) > 500 and delay < 2.0:
            console.print(
                f"[yellow]Note: Processing {len(chunks)} chunks. Current delay is {delay}s. "
                f"If you hit rate limits, try --delay 3.0[/yellow]\n"
            )
        
        success = agent.ingest_documents_batch(
            chunks, 
            batch_size=args.batch_size,
            delay_between_batches=delay
        )
    else:
        success = agent.ingest_documents(chunks)

    if success:
        console.print("\n[bold green]✓ Ingestion complete![/bold green]")
        console.print(
            "\n[cyan]You can now run the main assistant with:[/cyan] python main.py\n"
        )
    else:
        console.print("\n[bold red]✗ Ingestion failed[/bold red]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
