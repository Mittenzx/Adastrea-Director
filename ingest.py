#!/usr/bin/env python3
"""
Document Ingestion Script for Adastrea Director

This script handles loading, processing, and embedding project documents
into a vector database for RAG-based question answering.

Usage:
    python ingest.py --docs-dir /path/to/docs
    python ingest.py --docs-dir /path/to/docs --collection-name my_project
    python ingest.py --file single_doc.md
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
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
        UnstructuredMarkdownLoader,
        PythonLoader,
        PyPDFLoader,
        Docx2txtLoader,
    )
    from langchain.text_splitter import (
        RecursiveCharacterTextSplitter,
        Language,
    )
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
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
    ):
        """
        Initialize the document ingestion agent.

        Args:
            collection_name: Name of the collection in the vector database
            persist_directory: Directory to persist the vector database
            chunk_size: Size of text chunks for embedding
            chunk_overlap: Overlap between chunks
            
        Raises:
            ValidationError: If chunk_size or chunk_overlap are invalid
            APIKeyError: If OpenAI API key is missing or invalid
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
        try:
            self.embeddings = OpenAIEmbeddings()
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

        # Initialize text splitter (default for markdown and text)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )
        
        # Initialize code-specific text splitter for Python files
        self.code_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

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
            ".md": UnstructuredMarkdownLoader,
            ".txt": TextLoader,
            ".py": PythonLoader,
            ".pdf": PyPDFLoader,
            ".docx": Docx2txtLoader,
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
                    )
                    docs = loader.load()
                    documents.extend(docs)
                    progress.update(
                        task,
                        description=f"Loaded {len(docs)} {extension} files",
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
            ".md": UnstructuredMarkdownLoader,
            ".txt": TextLoader,
            ".py": PythonLoader,
            ".pdf": PyPDFLoader,
            ".docx": Docx2txtLoader,
        }

        loader_class = loader_mapping.get(extension, TextLoader)

        try:
            loader = loader_class(file_path)
            documents = loader.load()
            console.print(f"[green]Loaded {file_path}[/green]")
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
                
                # Separate documents by type for optimized chunking
                code_docs = []
                text_docs = []
                
                for doc in documents:
                    source = doc.metadata.get("source", "")
                    if source.endswith(".py"):
                        code_docs.append(doc)
                    else:
                        text_docs.append(doc)
                
                # Chunk with appropriate splitters
                chunks = []
                if code_docs:
                    chunks.extend(self.code_splitter.split_documents(code_docs))
                if text_docs:
                    chunks.extend(self.text_splitter.split_documents(text_docs))
                
                progress.update(
                    task,
                    description=f"Created {len(chunks)} chunks from {len(documents)} documents "
                               f"({len(code_docs)} code, {len(text_docs)} text)",
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
            
            # Check for rate limit errors
            if "rate" in error_msg and "limit" in error_msg:
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

    # Ingest documents
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
