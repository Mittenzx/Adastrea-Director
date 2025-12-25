#!/usr/bin/env python3
"""
Auto-Ingestion Module for Adastrea Director

This module provides automatic codebase ingestion capabilities:
1. Project source directory detection
2. Scheduled background ingestion
3. Incremental updates on file save (file watching)
4. Configurable file type filters
5. Progress notifications

Features:
- Auto-detect project directories (Source, Content, Config, etc.)
- Background ingestion without blocking UI
- File watcher for incremental updates
- Configurable file patterns and exclusions
- Progress callbacks for GUI integration
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any, Set
from datetime import datetime, timedelta
import json

from logging_config import get_logger

# Try to import watchdog for file watching (optional dependency)
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

# Import existing ingestion infrastructure
from ingest import DocumentIngestionAgent, ProgressWriter

logger = get_logger(__name__)


class ProjectDetector:
    """Detects project directories and relevant source files."""
    
    # Common project directory patterns
    PROJECT_DIRS = [
        "Source",
        "Content",
        "Config",
        "Plugins",
        "Documentation",
        "Docs",
        "Scripts",
        "Shaders",
    ]
    
    # Default file extensions to ingest
    DEFAULT_EXTENSIONS = {
        ".cpp", ".h", ".hpp", ".cc", ".cxx",  # C++
        ".cs",  # C#
        ".py",  # Python
        ".js", ".jsx", ".ts", ".tsx",  # JavaScript/TypeScript
        ".md", ".txt", ".rst",  # Documentation
        ".json", ".yaml", ".yml", ".ini", ".cfg",  # Config
        ".uasset", ".umap",  # Unreal assets (metadata only)
    }
    
    # Directories to exclude
    EXCLUDE_DIRS = {
        ".git", ".svn", ".hg",  # Version control
        "node_modules", "__pycache__", ".pytest_cache",  # Dependencies/cache
        "Binaries", "Intermediate", "Build",  # Build artifacts
        "Saved",  # Unreal temp files
        ".vs", ".vscode", ".idea",  # IDE files
    }
    
    def __init__(self, root_path: str):
        """
        Initialize project detector.
        
        Args:
            root_path: Root directory of the project
        """
        self.root_path = Path(root_path).resolve()
        self.detected_dirs: List[Path] = []
    
    def detect_project_dirs(self) -> List[Path]:
        """
        Detect project directories in the root path.
        
        Returns:
            List of detected project directories
        """
        logger.info(f"Detecting project directories in: {self.root_path}")
        detected = []
        
        # Check for each project directory pattern
        for dir_name in self.PROJECT_DIRS:
            dir_path = self.root_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                detected.append(dir_path)
                logger.info(f"  Found: {dir_name}/")
        
        self.detected_dirs = detected
        return detected
    
    def should_include_file(self, file_path: Path, extensions: Optional[Set[str]] = None) -> bool:
        """
        Check if a file should be included in ingestion.
        
        Args:
            file_path: Path to the file
            extensions: Set of allowed extensions (defaults to DEFAULT_EXTENSIONS)
        
        Returns:
            True if file should be included
        """
        if extensions is None:
            extensions = self.DEFAULT_EXTENSIONS
        
        # Check if file has allowed extension
        if file_path.suffix.lower() not in extensions:
            return False
        
        # Check if file is in excluded directory
        for parent in file_path.parents:
            if parent.name in self.EXCLUDE_DIRS:
                return False
        
        return True
    
    def scan_project_files(self, extensions: Optional[Set[str]] = None) -> List[Path]:
        """
        Scan all project files that should be ingested.
        
        Args:
            extensions: Set of allowed extensions (defaults to DEFAULT_EXTENSIONS)
        
        Returns:
            List of file paths to ingest
        """
        if not self.detected_dirs:
            self.detect_project_dirs()
        
        logger.info("Scanning project files...")
        files = []
        
        for dir_path in self.detected_dirs:
            for file_path in dir_path.rglob("*"):
                if file_path.is_file() and self.should_include_file(file_path, extensions):
                    files.append(file_path)
        
        logger.info(f"Found {len(files)} files to ingest")
        return files


class FileWatchHandler(FileSystemEventHandler):
    """File system event handler for incremental updates."""
    
    def __init__(self, auto_ingestion: 'AutoIngestion'):
        """
        Initialize file watch handler.
        
        Args:
            auto_ingestion: AutoIngestion instance to notify
        """
        self.auto_ingestion = auto_ingestion
        self.logger = get_logger(__name__)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if self.auto_ingestion.detector.should_include_file(file_path):
                self.logger.info(f"File modified: {file_path}")
                self.auto_ingestion.queue_file_for_ingestion(file_path)
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if self.auto_ingestion.detector.should_include_file(file_path):
                self.logger.info(f"File created: {file_path}")
                self.auto_ingestion.queue_file_for_ingestion(file_path)


class AutoIngestion:
    """Automatic project codebase ingestion."""
    
    def __init__(
        self,
        project_root: str,
        collection_name: str = "adastrea_project",
        persist_directory: str = "./chroma_db_project",
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """
        Initialize auto-ingestion.
        
        Args:
            project_root: Root directory of the project
            collection_name: Vector database collection name
            persist_directory: Vector database storage directory
            progress_callback: Callback for progress updates
        """
        self.project_root = Path(project_root).resolve()
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.progress_callback = progress_callback
        
        # Project detection
        self.detector = ProjectDetector(str(self.project_root))
        
        # File watching
        self.file_watch_enabled = False
        self.observer: Optional[Observer] = None
        self.file_queue: Set[Path] = set()
        self.queue_lock = threading.Lock()
        
        # Scheduled ingestion
        self.scheduled_ingestion_enabled = False
        self.ingestion_interval = timedelta(hours=1)  # Default: every hour
        self.last_ingestion_time: Optional[datetime] = None
        self.schedule_thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()
        
        # Ingestion agent
        self.agent: Optional[DocumentIngestionAgent] = None
        
        logger.info(f"AutoIngestion initialized for: {self.project_root}")
    
    def _notify_progress(self, message: str, percent: float = 0, details: str = ""):
        """
        Notify progress callback.
        
        Args:
            message: Progress message
            percent: Progress percentage (0-100)
            details: Additional details
        """
        if self.progress_callback:
            self.progress_callback({
                "message": message,
                "percent": percent,
                "details": details,
                "timestamp": datetime.now().isoformat(),
            })
    
    def detect_project(self) -> List[Path]:
        """
        Detect project directories.
        
        Returns:
            List of detected project directories
        """
        self._notify_progress("Detecting project directories...", 10)
        dirs = self.detector.detect_project_dirs()
        self._notify_progress(f"Detected {len(dirs)} project directories", 20)
        return dirs
    
    def start_file_watching(self) -> bool:
        """
        Start file system watching for incremental updates.
        
        Returns:
            True if successful
        """
        if not WATCHDOG_AVAILABLE:
            logger.warning("watchdog not available - file watching disabled")
            self._notify_progress("File watching unavailable (install watchdog)", 0)
            return False
        
        if self.file_watch_enabled:
            logger.info("File watching already enabled")
            return True
        
        try:
            self._notify_progress("Starting file watching...", 0)
            
            # Create observer and handler
            self.observer = Observer()
            handler = FileWatchHandler(self)
            
            # Watch all detected project directories
            dirs = self.detector.detected_dirs
            if not dirs:
                dirs = self.detect_project()
            
            for dir_path in dirs:
                self.observer.schedule(handler, str(dir_path), recursive=True)
                logger.info(f"Watching directory: {dir_path}")
            
            self.observer.start()
            self.file_watch_enabled = True
            
            self._notify_progress(f"File watching active for {len(dirs)} directories", 100)
            logger.info("File watching started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start file watching: {e}")
            self._notify_progress(f"File watching failed: {e}", 0)
            return False
    
    def stop_file_watching(self):
        """Stop file system watching."""
        if self.observer and self.file_watch_enabled:
            self._notify_progress("Stopping file watching...", 0)
            self.observer.stop()
            self.observer.join(timeout=5)
            self.file_watch_enabled = False
            self._notify_progress("File watching stopped", 100)
            logger.info("File watching stopped")
    
    def queue_file_for_ingestion(self, file_path: Path):
        """
        Queue a file for ingestion.
        
        Args:
            file_path: Path to the file
        """
        with self.queue_lock:
            self.file_queue.add(file_path)
            logger.debug(f"Queued file for ingestion: {file_path}")
    
    def process_file_queue(self):
        """Process queued files for ingestion."""
        with self.queue_lock:
            if not self.file_queue:
                return
            
            files_to_process = list(self.file_queue)
            self.file_queue.clear()
        
        logger.info(f"Processing {len(files_to_process)} queued files")
        self._notify_progress(f"Processing {len(files_to_process)} changed files", 50)
        
        # Initialize agent if needed
        if self.agent is None:
            self.agent = DocumentIngestionAgent(
                collection_name=self.collection_name,
                persist_directory=self.persist_directory,
            )
        
        # Process each file
        for file_path in files_to_process:
            try:
                # Load and ingest single file
                documents = self.agent.load_single_file(str(file_path))
                if documents:
                    chunks = self.agent.chunk_documents(documents)
                    if chunks:
                        # Delete old chunks for this file
                        self.agent._delete_document_by_source(str(file_path))
                        # Add new chunks
                        self.agent.ingest_documents(chunks)
                        logger.info(f"Updated: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
        
        self._notify_progress(f"Processed {len(files_to_process)} files", 100)
    
    def start_scheduled_ingestion(self, interval_hours: float = 1.0):
        """
        Start scheduled background ingestion.
        
        Args:
            interval_hours: Hours between ingestions
        """
        if self.scheduled_ingestion_enabled:
            logger.info("Scheduled ingestion already enabled")
            return
        
        self.ingestion_interval = timedelta(hours=interval_hours)
        self.scheduled_ingestion_enabled = True
        self.stop_flag.clear()
        
        # Start background thread
        self.schedule_thread = threading.Thread(
            target=self._scheduled_ingestion_loop,
            daemon=True,
        )
        self.schedule_thread.start()
        
        self._notify_progress(f"Scheduled ingestion active (every {interval_hours}h)", 100)
        logger.info(f"Scheduled ingestion started (interval: {interval_hours}h)")
    
    def stop_scheduled_ingestion(self):
        """Stop scheduled background ingestion."""
        if self.schedule_thread:
            self.stop_flag.set()
            self.scheduled_ingestion_enabled = False
            self.schedule_thread.join(timeout=5)
            self._notify_progress("Scheduled ingestion stopped", 100)
            logger.info("Scheduled ingestion stopped")
    
    def _scheduled_ingestion_loop(self):
        """Background thread for scheduled ingestion."""
        while not self.stop_flag.is_set():
            # Check if ingestion is due
            now = datetime.now()
            if (self.last_ingestion_time is None or 
                (now - self.last_ingestion_time) >= self.ingestion_interval):
                
                logger.info("Scheduled ingestion starting")
                self.run_full_ingestion()
                self.last_ingestion_time = now
            
            # Sleep in small intervals to allow quick stopping
            for _ in range(60):  # Check every second for a minute
                if self.stop_flag.is_set():
                    break
                time.sleep(1)
    
    def run_full_ingestion(self) -> Dict[str, Any]:
        """
        Run full project ingestion.
        
        Returns:
            Statistics about the ingestion
        """
        logger.info("Starting full project ingestion")
        self._notify_progress("Starting project ingestion...", 0)
        
        # Detect project directories
        dirs = self.detect_project()
        
        if not dirs:
            logger.warning("No project directories detected")
            self._notify_progress("No project directories found", 0)
            return {"error": "No project directories detected"}
        
        # Initialize agent if needed
        if self.agent is None:
            self.agent = DocumentIngestionAgent(
                collection_name=self.collection_name,
                persist_directory=self.persist_directory,
            )
        
        # Use incremental ingestion for each directory
        all_stats = {
            "total_files": 0,
            "skipped": 0,
            "updated": 0,
            "added": 0,
            "errors": 0,
        }
        
        for i, dir_path in enumerate(dirs):
            progress = ((i + 1) / len(dirs)) * 100
            self._notify_progress(
                f"Ingesting {dir_path.name}... ({i + 1}/{len(dirs)})",
                progress,
                f"Processing directory {i + 1} of {len(dirs)}"
            )
            
            try:
                stats = self.agent.ingest_directory_incremental(
                    str(dir_path),
                    force_reingest=False,
                    delay_between_files=0.5
                )
                
                # Accumulate stats
                for key in all_stats:
                    all_stats[key] += stats.get(key, 0)
                    
            except Exception as e:
                logger.error(f"Failed to ingest {dir_path}: {e}")
                all_stats["errors"] += 1
        
        self._notify_progress("Project ingestion complete", 100, 
                            f"Added: {all_stats['added']}, Updated: {all_stats['updated']}")
        logger.info(f"Project ingestion complete: {all_stats}")
        
        return all_stats


def main():
    """Example usage of auto-ingestion."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-ingest project codebase")
    parser.add_argument("project_root", help="Root directory of the project")
    parser.add_argument("--watch", action="store_true", help="Enable file watching")
    parser.add_argument("--schedule", type=float, help="Enable scheduled ingestion (hours)")
    parser.add_argument("--run-now", action="store_true", help="Run full ingestion immediately")
    
    args = parser.parse_args()
    
    # Create auto-ingestion instance
    def progress_callback(data):
        print(f"[{data['percent']:.0f}%] {data['message']}")
        if data['details']:
            print(f"  {data['details']}")
    
    auto_ingest = AutoIngestion(
        args.project_root,
        progress_callback=progress_callback,
    )
    
    # Run immediate ingestion if requested
    if args.run_now:
        stats = auto_ingest.run_full_ingestion()
        print(f"\nIngestion complete: {stats}")
    
    # Enable file watching if requested
    if args.watch:
        if auto_ingest.start_file_watching():
            print("File watching enabled")
    
    # Enable scheduled ingestion if requested
    if args.schedule:
        auto_ingest.start_scheduled_ingestion(args.schedule)
        print(f"Scheduled ingestion enabled (every {args.schedule} hours)")
    
    # Keep running if watching or scheduling is enabled
    if args.watch or args.schedule:
        try:
            print("\nPress Ctrl+C to stop...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
            auto_ingest.stop_file_watching()
            auto_ingest.stop_scheduled_ingestion()


if __name__ == "__main__":
    main()
