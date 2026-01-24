#!/usr/bin/env python3
"""
Script to ingest documents from the Mittenzx/Adastrea game repository.

This script handles cloning and ingesting documents from the game repository
that Adastrea Director is designed to help build.

NOTE: The Mittenzx/Adastrea repository is private. You need a GitHub token
with 'repo' scope and access to the repository.

Embedding Configuration:
- By default, uses HuggingFace embeddings (local, no API key required)
- To use OpenAI embeddings instead, set: EMBEDDING_PROVIDER=openai
- To customize HuggingFace model: HUGGINGFACE_MODEL_NAME=your-model-name
- Default HuggingFace model: 'all-MiniLM-L6-v2'
- OPENAI_API_KEY is only required when EMBEDDING_PROVIDER=openai

Features:
1. Cloning the private repository (requires GitHub token)
2. Selective ingestion of relevant directories
3. Tracking of last ingestion for auto-update detection
4. Scheduled updates via cron or GitHub Actions

Usage:
    # With GitHub token in environment (uses HuggingFace embeddings by default)
    export GITHUB_TOKEN="your_token_here"
    python ingest_game_repo.py
    
    # To use OpenAI embeddings instead
    export EMBEDDING_PROVIDER=openai
    export OPENAI_API_KEY="your_openai_key"
    python ingest_game_repo.py --token YOUR_TOKEN
    
    # To use a different HuggingFace model
    export HUGGINGFACE_MODEL_NAME="sentence-transformers/all-mpnet-base-v2"
    python ingest_game_repo.py
    
    # Check if update is needed
    python ingest_game_repo.py --check-updates
    
    # Force re-ingestion
    python ingest_game_repo.py --force
"""

import os
import sys

# Disable ChromaDB telemetry BEFORE any imports that might import chromadb
# This prevents "capture() takes 1 positional argument but 3 were given" errors
# Must be set before importing the ingest module which imports langchain_community/chromadb
# ChromaDB checks for this variable and disables telemetry when set to "1"
os.environ["ANONYMIZED_TELEMETRY"] = "1"

import argparse
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List

from ingest import DocumentIngestionAgent
from rich.console import Console
from logging_config import get_logger

logger = get_logger(__name__)
console = Console(legacy_windows=False)

# Configuration
# NOTE: This is a private repository. A GitHub token with 'repo' scope is required.
GAME_REPO_URL = "https://github.com/Mittenzx/Adastrea.git"
GAME_REPO_NAME = "Adastrea"
DEFAULT_CLONE_DIR = Path("/tmp") / f"adastrea_game_repo"
TRACKING_FILE = Path(".adastrea_ingestion_tracking.json")

# Directories to ingest from the game repository
# Customize these based on the actual structure of Mittenzx/Adastrea
INGEST_DIRS = [
    "docs",
    "Documentation",
    "Source",
    "Content",
    "Config",
]


class GameRepoIngestionTracker:
    """Track ingestion state for the game repository."""
    
    def __init__(self, tracking_file: Path = TRACKING_FILE):
        self.tracking_file = tracking_file
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load tracking state from file."""
        if self.tracking_file.exists():
            try:
                state = json.loads(self.tracking_file.read_text())
                logger.debug(f"Loaded ingestion tracking state from: {self.tracking_file}")
                return state
            except Exception as e:
                logger.warning(f"Could not load tracking state from {self.tracking_file}: {e}")
                console.print(f"[yellow]Warning: Could not load tracking state: {e}[/yellow]")
                return {}
        logger.debug(f"No tracking file found at: {self.tracking_file}")
        return {}
    
    def _save_state(self):
        """Save tracking state to file."""
        try:
            self.tracking_file.write_text(json.dumps(self.state, indent=2))
            logger.info(f"Saved ingestion tracking state to: {self.tracking_file}")
        except Exception as e:
            logger.error(f"Could not save tracking state to {self.tracking_file}: {e}")
            console.print(f"[yellow]Warning: Could not save tracking state: {e}[/yellow]")
    
    def get_last_commit(self) -> Optional[str]:
        """Get the last ingested commit hash."""
        return self.state.get("last_commit")
    
    def get_last_ingestion_time(self) -> Optional[str]:
        """Get the timestamp of last ingestion."""
        return self.state.get("last_ingestion_time")
    
    def update_ingestion(self, commit_hash: str, document_count: int, chunk_count: int):
        """Update tracking information after successful ingestion."""
        self.state.update({
            "last_commit": commit_hash,
            "last_ingestion_time": datetime.now().isoformat(),
            "document_count": document_count,
            "chunk_count": chunk_count,
        })
        self._save_state()
        logger.info(f"Updated ingestion tracking - Commit: {commit_hash}, Docs: {document_count}, Chunks: {chunk_count}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        return {
            "last_commit": self.state.get("last_commit", "Never"),
            "last_ingestion_time": self.state.get("last_ingestion_time", "Never"),
            "document_count": self.state.get("document_count", 0),
            "chunk_count": self.state.get("chunk_count", 0),
        }


def get_current_commit_hash(repo_dir: Path) -> Optional[str]:
    """Get the current commit hash of a git repository."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True,
        )
        commit_hash = result.stdout.strip()
        logger.debug(f"Current commit hash for {repo_dir}: {commit_hash}")
        return commit_hash
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get commit hash for {repo_dir}: {e}")
        return None


def clone_repository(repo_url: str, clone_dir: Path, github_token: Optional[str] = None) -> bool:
    """
    Clone the game repository.
    
    Args:
        repo_url: URL of the repository
        clone_dir: Directory to clone into
        github_token: GitHub personal access token for private repos
    
    Returns:
        bool: True if successful
    """
    logger.info(f"Starting repository clone - URL: {repo_url}, Destination: {clone_dir}")
    console.print(f"\n[cyan]Cloning repository...[/cyan]")
    console.print(f"  URL: {repo_url}")
    console.print(f"  Destination: {clone_dir}")
    
    # Add token to URL if provided
    if github_token:
        repo_url = repo_url.replace("https://", f"https://{github_token}@")
        logger.debug("Using GitHub token for authentication")
    
    # Remove existing directory if it exists
    if clone_dir.exists():
        console.print(f"  [yellow]Removing existing directory...[/yellow]")
        logger.debug(f"Removing existing directory: {clone_dir}")
        shutil.rmtree(clone_dir)
    
    # Clone the repository
    start_time = datetime.now()
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(clone_dir)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # Replace invalid UTF-8 sequences instead of failing
            timeout=300,  # 5 minute timeout
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        if result.returncode != 0:
            logger.error(f"Repository clone failed (took {duration:.2f}s): {result.stderr}")
            console.print(f"[red]Failed to clone repository:[/red]")
            console.print(f"[red]{result.stderr}[/red]")
            return False
        
        logger.info(f"Repository cloned successfully in {duration:.2f}s")
        console.print(f"[green]✓ Repository cloned successfully[/green]")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Repository clone timed out after 5 minutes")
        console.print(f"[red]Clone operation timed out after 5 minutes[/red]")
        return False
    except Exception as e:
        logger.error(f"Error during repository clone: {e}", exc_info=True)
        console.print(f"[red]Error cloning repository: {e}[/red]")
        return False


def check_for_updates(clone_dir: Path, tracker: GameRepoIngestionTracker) -> bool:
    """
    Check if the game repository has updates.
    
    Args:
        clone_dir: Directory where repository is cloned
        tracker: Ingestion tracker
    
    Returns:
        bool: True if updates are available
    """
    if not clone_dir.exists():
        console.print("[yellow]Repository not cloned yet. Updates needed.[/yellow]")
        return True
    
    current_commit = get_current_commit_hash(clone_dir)
    last_commit = tracker.get_last_commit()
    
    if not last_commit:
        console.print("[yellow]No previous ingestion found. Updates needed.[/yellow]")
        return True
    
    if current_commit != last_commit:
        console.print(f"[yellow]New commits available:[/yellow]")
        console.print(f"  Last ingested: {last_commit}")
        console.print(f"  Current: {current_commit}")
        return True
    
    console.print("[green]Repository is up to date[/green]")
    return False


def ingest_game_repository(
    clone_dir: Path,
    collection_name: str = "adastrea_game_docs",
    persist_directory: str = "./chroma_db_adastrea",
    ingest_dirs: Optional[List[str]] = None,
) -> Tuple[bool, int, int]:
    """
    Ingest documents from the cloned game repository.
    
    Args:
        clone_dir: Directory where repository is cloned
        collection_name: Name for the vector database collection
        persist_directory: Directory to store the vector database
        ingest_dirs: List of directories to ingest (relative to repo root)
    
    Returns:
        tuple: (success, document_count, chunk_count)
    """
    if ingest_dirs is None:
        ingest_dirs = INGEST_DIRS
    
    logger.info(f"Starting game repository ingestion - Collection: {collection_name}, Persist: {persist_directory}")
    console.print(f"\n[cyan]Ingesting documents from game repository...[/cyan]")
    
    start_time = datetime.now()
    
    # Create agent
    agent = DocumentIngestionAgent(
        collection_name=collection_name,
        persist_directory=persist_directory,
        chunk_size=1000,
        chunk_overlap=200,
    )
    
    # Collect all documents from specified directories
    all_documents = []
    
    for dir_name in ingest_dirs:
        dir_path = clone_dir / dir_name
        if dir_path.exists():
            logger.debug(f"Loading documents from: {dir_path}")
            console.print(f"  Loading from: {dir_name}/")
            docs = agent.load_documents_from_directory(str(dir_path))
            all_documents.extend(docs)
            logger.info(f"Loaded {len(docs)} documents from {dir_name}/")
            console.print(f"    [green]✓ Loaded {len(docs)} documents[/green]")
        else:
            logger.debug(f"Directory not found, skipping: {dir_path}")
            console.print(f"    [dim]  Skipping {dir_name}/ (not found)[/dim]")
    
    if not all_documents:
        logger.warning("No documents found to ingest")
        console.print("[yellow]No documents found to ingest[/yellow]")
        return False, 0, 0
    
    logger.info(f"Total documents loaded: {len(all_documents)}")
    console.print(f"\n[green]Total documents loaded: {len(all_documents)}[/green]")
    
    # Chunk documents
    console.print("\n[cyan]Chunking documents...[/cyan]")
    chunks = agent.chunk_documents(all_documents)
    logger.info(f"Created {len(chunks)} chunks from {len(all_documents)} documents")
    console.print(f"[green]Created {len(chunks)} chunks[/green]")
    
    # Ingest documents
    console.print("\n[cyan]Ingesting into vector database...[/cyan]")
    success = agent.ingest_documents_batch(
        chunks,
        batch_size=50,
        delay_between_batches=2.0
    )
    
    duration = (datetime.now() - start_time).total_seconds()
    
    if success:
        logger.info(f"Successfully ingested game repository in {duration:.2f}s - Docs: {len(all_documents)}, Chunks: {len(chunks)}")
        console.print(f"\n[bold green]✓ Successfully ingested game repository (took {duration:.2f}s)![/bold green]")
        console.print(f"  Documents: {len(all_documents)}")
        console.print(f"  Chunks: {len(chunks)}")
        console.print(f"  Collection: {collection_name}")
        console.print(f"  Storage: {persist_directory}")
        return True, len(all_documents), len(chunks)
    else:
        logger.error(f"Failed to ingest game repository after {duration:.2f}s")
        console.print(f"\n[bold red]✗ Failed to ingest game repository[/bold red]")
        return False, 0, 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest documents from the Mittenzx/Adastrea game repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest with GitHub token from environment
  export GITHUB_TOKEN="ghp_xxxxx"
  python ingest_game_repo.py
  
  # Ingest with token as argument
  python ingest_game_repo.py --token ghp_xxxxx
  
  # Check if updates are available
  python ingest_game_repo.py --check-updates
  
  # Force re-ingestion even if no updates
  python ingest_game_repo.py --force
  
  # Show ingestion statistics
  python ingest_game_repo.py --stats
"""
    )
    
    parser.add_argument(
        "--token",
        type=str,
        help="GitHub personal access token (or set GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--clone-dir",
        type=str,
        default=str(DEFAULT_CLONE_DIR),
        help=f"Directory to clone repository to (default: {DEFAULT_CLONE_DIR})",
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="adastrea_game_docs",
        help="Vector database collection name (default: adastrea_game_docs)",
    )
    parser.add_argument(
        "--persist-dir",
        type=str,
        default="./chroma_db_adastrea",
        help="Vector database storage directory (default: ./chroma_db_adastrea)",
    )
    parser.add_argument(
        "--check-updates",
        action="store_true",
        help="Check if updates are available without ingesting",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-ingestion even if no updates",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show ingestion statistics",
    )
    
    args = parser.parse_args()
    
    logger.info("Starting game repository ingestion script")
    
    # Print banner
    console.print("\n[bold cyan]🎮 Adastrea Director - Game Repository Ingestion[/bold cyan]\n")
    
    # Initialize tracker
    tracker = GameRepoIngestionTracker()
    
    # Show stats if requested
    if args.stats:
        stats = tracker.get_stats()
        console.print("[bold]Ingestion Statistics:[/bold]")
        console.print(f"  Last commit: [cyan]{stats['last_commit']}[/cyan]")
        console.print(f"  Last ingestion: [cyan]{stats['last_ingestion_time']}[/cyan]")
        console.print(f"  Documents: [cyan]{stats['document_count']}[/cyan]")
        console.print(f"  Chunks: [cyan]{stats['chunk_count']}[/cyan]")
        return
    
    # Get GitHub token
    github_token = args.token or os.environ.get("GITHUB_TOKEN")
    
    if not github_token:
        console.print("[yellow]⚠ No GitHub token provided.[/yellow]")
        console.print("[yellow]  If the repository is private, set GITHUB_TOKEN environment variable[/yellow]")
        console.print("[yellow]  or use --token argument[/yellow]\n")
    
    clone_dir = Path(args.clone_dir)
    
    # Clone repository
    if not clone_repository(GAME_REPO_URL, clone_dir, github_token):
        console.print("\n[red]Failed to clone repository. Exiting.[/red]")
        sys.exit(1)
    
    # Check for updates if requested
    if args.check_updates:
        has_updates = check_for_updates(clone_dir, tracker)
        sys.exit(0 if not has_updates else 1)
    
    # Check if ingestion is needed
    if not args.force:
        current_commit = get_current_commit_hash(clone_dir)
        last_commit = tracker.get_last_commit()
        
        if current_commit and current_commit == last_commit:
            console.print("\n[green]Repository is already up to date. Use --force to re-ingest.[/green]")
            sys.exit(0)
    
    # Ingest documents
    success, doc_count, chunk_count = ingest_game_repository(
        clone_dir,
        collection_name=args.collection_name,
        persist_directory=args.persist_dir,
    )
    
    if success:
        # Update tracking
        current_commit = get_current_commit_hash(clone_dir)
        if current_commit:
            tracker.update_ingestion(current_commit, doc_count, chunk_count)
            console.print(f"\n[cyan]Tracking updated with commit: {current_commit}[/cyan]")
        
        console.print("\n[bold green]✓ Game repository ingestion complete![/bold green]")
        console.print("\n[cyan]You can now use the assistant with game repository knowledge:[/cyan]")
        console.print(f"  python main.py")
        sys.exit(0)
    else:
        console.print("\n[bold red]✗ Game repository ingestion failed[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
