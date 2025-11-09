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

try:
    from dotenv import load_dotenv
    # Load environment variables immediately after import
    load_dotenv()
    
    from langchain_community.document_loaders import (
        DirectoryLoader,
        TextLoader,
        UnstructuredMarkdownLoader,
        PythonLoader,
    )
    from langchain.text_splitter import RecursiveCharacterTextSplitter
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

console = Console()


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
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Initialize embeddings
        try:
            self.embeddings = OpenAIEmbeddings()
        except Exception as e:
            console.print(
                f"[red]Error initializing OpenAI embeddings: {e}[/red]"
            )
            console.print(
                "[yellow]Make sure OPENAI_API_KEY is set in your environment[/yellow]"
            )
            sys.exit(1)

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
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
        }

        loader_class = loader_mapping.get(extension, TextLoader)

        try:
            loader = loader_class(file_path)
            documents = loader.load()
            console.print(f"[green]Loaded {file_path}[/green]")
            return documents
        except Exception as e:
            console.print(f"[red]Error loading file: {e}[/red]")
            return []

    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        """
        Split documents into chunks.

        Args:
            documents: List of documents to chunk

        Returns:
            List of document chunks
        """
        if not documents:
            return []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Chunking documents...", total=None)
            chunks = self.text_splitter.split_documents(documents)
            progress.update(
                task,
                description=f"Created {len(chunks)} chunks from {len(documents)} documents",
            )

        return chunks

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

        except Exception as e:
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
