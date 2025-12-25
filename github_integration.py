#!/usr/bin/env python3
"""
GitHub Integration Module for Adastrea Director

This module provides GitHub repository management and automatic ingestion:
1. GitHub API integration
2. Repository cloning with authentication
3. Automatic ingestion on clone
4. Update detection and synchronization
5. Branch switching support

Features:
- Clone public and private repositories
- Authenticate with personal access tokens
- Detect repository updates
- Automatically ingest on clone/update
- Switch between branches
- Track multiple repositories
"""

import os
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from dataclasses import dataclass, asdict

from logging_config import get_logger
from ingest import DocumentIngestionAgent

# Try to import requests for GitHub API (optional dependency)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = get_logger(__name__)


@dataclass
class Repository:
    """Represents a GitHub repository."""
    name: str
    url: str
    clone_path: Optional[Path] = None
    current_branch: str = "main"
    last_commit: Optional[str] = None
    last_ingestion: Optional[str] = None
    document_count: int = 0
    chunk_count: int = 0


class GitHubAPI:
    """GitHub API client for repository operations."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub API client.
        
        Args:
            token: GitHub personal access token (optional for public repos)
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.session = None
        
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            if self.token:
                self.session.headers.update({
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json",
                })
    
    def get_repository_info(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """
        Get repository information from GitHub API.
        
        Args:
            owner: Repository owner
            repo: Repository name
        
        Returns:
            Repository information dict or None if error
        """
        if not REQUESTS_AVAILABLE:
            logger.warning("requests library not available - API features disabled")
            return None
        
        try:
            url = f"{self.BASE_URL}/repos/{owner}/{repo}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get repository info: {e}")
            return None
    
    def get_latest_commit(self, owner: str, repo: str, branch: str = "main") -> Optional[str]:
        """
        Get the latest commit hash for a branch.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
        
        Returns:
            Commit hash or None if error
        """
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits/{branch}"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            return data["sha"]
        except Exception as e:
            logger.error(f"Failed to get latest commit: {e}")
            return None
    
    def list_branches(self, owner: str, repo: str) -> List[str]:
        """
        List all branches in a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
        
        Returns:
            List of branch names
        """
        if not REQUESTS_AVAILABLE:
            return []
        
        try:
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/branches"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            return [branch["name"] for branch in data]
        except Exception as e:
            logger.error(f"Failed to list branches: {e}")
            return []


class GitHubIntegration:
    """GitHub repository integration with automatic ingestion."""
    
    def __init__(
        self,
        repos_directory: str = "./repos",
        github_token: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """
        Initialize GitHub integration.
        
        Args:
            repos_directory: Directory to store cloned repositories
            github_token: GitHub personal access token
            progress_callback: Callback for progress updates
        """
        self.repos_directory = Path(repos_directory).resolve()
        self.repos_directory.mkdir(parents=True, exist_ok=True)
        
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        self.progress_callback = progress_callback
        
        # GitHub API client
        self.api = GitHubAPI(self.github_token)
        
        # Repository tracking
        self.tracking_file = self.repos_directory / ".repo_tracking.json"
        self.repositories: Dict[str, Repository] = self._load_tracking()
        
        logger.info(f"GitHubIntegration initialized (repos: {self.repos_directory})")
    
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
    
    def _load_tracking(self) -> Dict[str, Repository]:
        """
        Load repository tracking from file.
        
        Returns:
            Dictionary of repository name to Repository object
        """
        if not self.tracking_file.exists():
            return {}
        
        try:
            data = json.loads(self.tracking_file.read_text())
            repos = {}
            for name, repo_dict in data.items():
                # Convert clone_path string back to Path
                if repo_dict.get("clone_path"):
                    repo_dict["clone_path"] = Path(repo_dict["clone_path"])
                repos[name] = Repository(**repo_dict)
            return repos
        except Exception as e:
            logger.error(f"Failed to load tracking: {e}")
            return {}
    
    def _save_tracking(self):
        """Save repository tracking to file."""
        try:
            # Convert Repository objects to dicts for JSON serialization
            data = {}
            for name, repo in self.repositories.items():
                repo_dict = asdict(repo)
                # Convert Path to string
                if repo_dict.get("clone_path"):
                    repo_dict["clone_path"] = str(repo_dict["clone_path"])
                data[name] = repo_dict
            
            self.tracking_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Failed to save tracking: {e}")
    
    def _parse_repo_url(self, repo_url: str) -> Optional[tuple]:
        """
        Parse repository URL to extract owner and repo name.
        
        Args:
            repo_url: GitHub repository URL
        
        Returns:
            Tuple of (owner, repo) or None if invalid
        """
        # Handle different URL formats:
        # - https://github.com/owner/repo
        # - https://github.com/owner/repo.git
        # - git@github.com:owner/repo.git
        # - owner/repo
        
        repo_url = repo_url.strip()
        
        # Handle SSH URLs
        if repo_url.startswith("git@github.com:"):
            repo_url = repo_url.replace("git@github.com:", "")
        
        # Handle HTTPS URLs
        if repo_url.startswith("https://github.com/"):
            repo_url = repo_url.replace("https://github.com/", "")
        
        # Remove .git suffix
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]
        
        # Split into owner/repo
        parts = repo_url.split("/")
        if len(parts) == 2:
            return parts[0], parts[1]
        
        logger.error(f"Invalid repository URL: {repo_url}")
        return None
    
    def _get_current_commit(self, repo_path: Path) -> Optional[str]:
        """
        Get the current commit hash of a repository.
        
        Args:
            repo_path: Path to repository
        
        Returns:
            Commit hash or None
        """
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Failed to get commit hash: {e}")
            return None
    
    def clone_repository(
        self,
        repo_url: str,
        branch: Optional[str] = None,
        auto_ingest: bool = True,
    ) -> Optional[Repository]:
        """
        Clone a GitHub repository.
        
        Args:
            repo_url: Repository URL or owner/repo
            branch: Branch to clone (default: main/master)
            auto_ingest: Automatically ingest after cloning
        
        Returns:
            Repository object or None if failed
        """
        logger.info(f"Cloning repository: {repo_url}")
        self._notify_progress(f"Cloning {repo_url}...", 10)
        
        # Parse repository URL
        parsed = self._parse_repo_url(repo_url)
        if not parsed:
            self._notify_progress("Invalid repository URL", 0)
            return None
        
        owner, repo_name = parsed
        
        # Construct full URL without embedding token to avoid leaking credentials
        clone_url = f"https://github.com/{owner}/{repo_name}.git"
        
        # Determine clone path
        clone_path = self.repos_directory / f"{owner}_{repo_name}"
        
        # Remove existing directory if it exists
        if clone_path.exists():
            logger.info(f"Removing existing repository at {clone_path}")
            shutil.rmtree(clone_path)
        
        # Clone repository
        try:
            self._notify_progress(f"Cloning {repo_name}...", 30, "Running git clone")
            
            cmd = ["git", "clone"]
            if branch:
                cmd.extend(["-b", branch])
            cmd.extend([clone_url, str(clone_path)])
            
            # Set up environment for secure credential handling if token is available
            env = os.environ.copy()
            credential_helper_file = None
            
            if self.github_token:
                # Create a temporary credential helper script to avoid exposing token in command line
                credential_helper_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh')
                credential_helper_file.write('#!/bin/sh\n')
                credential_helper_file.write('echo username=x-access-token\n')
                credential_helper_file.write(f'echo password={self.github_token}\n')
                credential_helper_file.close()
                os.chmod(credential_helper_file.name, 0o700)
                
                # Configure git to use our credential helper
                cmd = ["git", "-c", f"credential.helper={credential_helper_file.name}", "clone"]
                if branch:
                    cmd.extend(["-b", branch])
                cmd.extend([clone_url, str(clone_path)])
                env["GIT_TERMINAL_PROMPT"] = "0"
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    env=env,
                )
            finally:
                # Clean up credential helper file
                if credential_helper_file:
                    try:
                        os.unlink(credential_helper_file.name)
                    except Exception:
                        pass
            
            if result.returncode != 0:
                logger.error(f"Clone failed: {result.stderr}")
                self._notify_progress(f"Clone failed: {result.stderr[:100]}", 0)
                return None
            
            self._notify_progress(f"Cloned {repo_name}", 50, "Getting commit info")
            
            # Get current commit and branch
            commit_hash = self._get_current_commit(clone_path)
            if not branch:
                # Detect default branch
                try:
                    result = subprocess.run(
                        ["git", "-C", str(clone_path), "branch", "--show-current"],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=10,
                    )
                    branch = result.stdout.strip() or "main"
                except Exception:
                    branch = "main"
            
            # Create repository object
            repo = Repository(
                name=f"{owner}/{repo_name}",
                url=f"https://github.com/{owner}/{repo_name}",
                clone_path=clone_path,
                current_branch=branch,
                last_commit=commit_hash,
            )
            
            # Save to tracking
            self.repositories[repo.name] = repo
            self._save_tracking()
            
            logger.info(f"Repository cloned successfully: {repo.name}")
            
            # Auto-ingest if requested
            if auto_ingest:
                self.ingest_repository(repo.name)
            else:
                self._notify_progress(f"Repository cloned: {repo_name}", 100)
            
            return repo
            
        except subprocess.TimeoutExpired:
            logger.error("Clone operation timed out")
            self._notify_progress("Clone timed out (5 minutes)", 0)
            # Clean up potentially incomplete clone directory
            if clone_path.exists():
                try:
                    shutil.rmtree(clone_path)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up incomplete clone at {clone_path}: {cleanup_error}")
            return None
        except Exception as e:
            logger.error(f"Failed to clone repository: {e}")
            self._notify_progress(f"Clone failed: {e}", 0)
            # Clean up potentially incomplete clone directory
            if clone_path.exists():
                try:
                    shutil.rmtree(clone_path)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up incomplete clone at {clone_path}: {cleanup_error}")
            return None
    
    def ingest_repository(self, repo_name: str) -> bool:
        """
        Ingest documents from a cloned repository.
        
        Args:
            repo_name: Repository name (owner/repo)
        
        Returns:
            True if successful
        """
        if repo_name not in self.repositories:
            logger.error(f"Repository not found: {repo_name}")
            return False
        
        repo = self.repositories[repo_name]
        
        if not repo.clone_path or not repo.clone_path.exists():
            logger.error(f"Repository not cloned: {repo_name}")
            return False
        
        logger.info(f"Ingesting repository: {repo_name}")
        self._notify_progress(f"Ingesting {repo_name}...", 60)
        
        try:
            # Create ingestion agent for this repository
            collection_name = f"repo_{repo_name.replace('/', '_')}"
            persist_dir = str(self.repos_directory / f".db_{repo_name.replace('/', '_')}")
            
            agent = DocumentIngestionAgent(
                collection_name=collection_name,
                persist_directory=persist_dir,
            )
            
            # Load documents
            self._notify_progress(f"Loading documents from {repo_name}...", 70)
            documents = agent.load_documents_from_directory(str(repo.clone_path))
            
            if not documents:
                logger.warning(f"No documents found in {repo_name}")
                self._notify_progress(f"No documents found in {repo_name}", 100)
                return False
            
            # Chunk documents
            self._notify_progress(f"Chunking {len(documents)} documents...", 80)
            chunks = agent.chunk_documents(documents)
            
            # Ingest documents
            self._notify_progress(f"Ingesting {len(chunks)} chunks...", 90)
            success = agent.ingest_documents_batch(
                chunks,
                batch_size=50,
                delay_between_batches=1.0,
            )
            
            if success:
                # Update repository tracking
                repo.last_ingestion = datetime.now().isoformat()
                repo.document_count = len(documents)
                repo.chunk_count = len(chunks)
                self._save_tracking()
                
                self._notify_progress(
                    f"Repository ingested: {repo_name}",
                    100,
                    f"{len(documents)} docs, {len(chunks)} chunks"
                )
                logger.info(f"Repository ingested successfully: {repo_name}")
                return True
            else:
                self._notify_progress(f"Ingestion failed for {repo_name}", 0)
                return False
                
        except Exception as e:
            logger.error(f"Failed to ingest repository: {e}")
            self._notify_progress(f"Ingestion failed: {e}", 0)
            return False
    
    def check_for_updates(self, repo_name: str) -> bool:
        """
        Check if a repository has updates.
        
        Args:
            repo_name: Repository name (owner/repo)
        
        Returns:
            True if updates are available
        """
        if repo_name not in self.repositories:
            return False
        
        repo = self.repositories[repo_name]
        
        if not repo.clone_path or not repo.clone_path.exists():
            return True  # Not cloned yet
        
        try:
            # Fetch latest from remote
            subprocess.run(
                ["git", "-C", str(repo.clone_path), "fetch"],
                capture_output=True,
                check=True,
                timeout=60,
            )
            
            # Get local and remote commit hashes
            local_commit = self._get_current_commit(repo.clone_path)
            
            result = subprocess.run(
                ["git", "-C", str(repo.clone_path), "rev-parse", f"origin/{repo.current_branch}"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            remote_commit = result.stdout.strip()
            
            return local_commit != remote_commit
            
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            return False
    
    def update_repository(self, repo_name: str, auto_ingest: bool = True) -> bool:
        """
        Update a repository to the latest version.
        
        Args:
            repo_name: Repository name (owner/repo)
            auto_ingest: Automatically re-ingest after update
        
        Returns:
            True if successful
        """
        if repo_name not in self.repositories:
            logger.error(f"Repository not found: {repo_name}")
            return False
        
        repo = self.repositories[repo_name]
        
        if not repo.clone_path or not repo.clone_path.exists():
            logger.error(f"Repository not cloned: {repo_name}")
            return False
        
        logger.info(f"Updating repository: {repo_name}")
        self._notify_progress(f"Updating {repo_name}...", 30)
        
        try:
            # Pull latest changes
            subprocess.run(
                ["git", "-C", str(repo.clone_path), "pull"],
                capture_output=True,
                text=True,
                check=True,
                timeout=60,
            )
            
            # Update commit hash
            repo.last_commit = self._get_current_commit(repo.clone_path)
            self._save_tracking()
            
            self._notify_progress(f"Repository updated: {repo_name}", 50)
            logger.info(f"Repository updated: {repo_name}")
            
            # Auto-ingest if requested
            if auto_ingest:
                return self.ingest_repository(repo_name)
            else:
                return True
                
        except Exception as e:
            logger.error(f"Failed to update repository: {e}")
            self._notify_progress(f"Update failed: {e}", 0)
            return False
    
    def switch_branch(self, repo_name: str, branch: str, auto_ingest: bool = True) -> bool:
        """
        Switch to a different branch.
        
        Args:
            repo_name: Repository name (owner/repo)
            branch: Branch name to switch to
            auto_ingest: Automatically re-ingest after switching
        
        Returns:
            True if successful
        """
        if repo_name not in self.repositories:
            logger.error(f"Repository not found: {repo_name}")
            return False
        
        repo = self.repositories[repo_name]
        
        if not repo.clone_path or not repo.clone_path.exists():
            logger.error(f"Repository not cloned: {repo_name}")
            return False
        
        logger.info(f"Switching branch: {repo_name} -> {branch}")
        self._notify_progress(f"Switching to {branch}...", 30)
        
        try:
            # Checkout branch
            subprocess.run(
                ["git", "-C", str(repo.clone_path), "checkout", branch],
                capture_output=True,
                text=True,
                check=True,
                timeout=60,
            )
            
            # Update repository info
            repo.current_branch = branch
            repo.last_commit = self._get_current_commit(repo.clone_path)
            self._save_tracking()
            
            self._notify_progress(f"Switched to {branch}", 50)
            logger.info(f"Switched to branch: {branch}")
            
            # Auto-ingest if requested
            if auto_ingest:
                return self.ingest_repository(repo_name)
            else:
                return True
                
        except Exception as e:
            logger.error(f"Failed to switch branch: {e}")
            self._notify_progress(f"Branch switch failed: {e}", 0)
            return False
    
    def list_repositories(self) -> List[Repository]:
        """
        List all tracked repositories.
        
        Returns:
            List of Repository objects
        """
        return list(self.repositories.values())
    
    def remove_repository(self, repo_name: str, delete_files: bool = False) -> bool:
        """
        Remove a repository from tracking.
        
        Args:
            repo_name: Repository name (owner/repo)
            delete_files: Also delete cloned files
        
        Returns:
            True if successful
        """
        if repo_name not in self.repositories:
            return False
        
        repo = self.repositories[repo_name]
        
        # Delete files if requested
        if delete_files and repo.clone_path and repo.clone_path.exists():
            shutil.rmtree(repo.clone_path)
        
        # Remove from tracking
        del self.repositories[repo_name]
        self._save_tracking()
        
        logger.info(f"Repository removed: {repo_name}")
        return True


def main():
    """Example usage of GitHub integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub repository integration")
    parser.add_argument("action", choices=["clone", "update", "list", "ingest"])
    parser.add_argument("--repo", help="Repository URL or owner/repo")
    parser.add_argument("--branch", help="Branch name")
    parser.add_argument("--token", help="GitHub personal access token")
    
    args = parser.parse_args()
    
    # Create integration instance
    def progress_callback(data):
        print(f"[{data['percent']:.0f}%] {data['message']}")
        if data['details']:
            print(f"  {data['details']}")
    
    integration = GitHubIntegration(
        github_token=args.token,
        progress_callback=progress_callback,
    )
    
    if args.action == "clone":
        if not args.repo:
            print("Error: --repo required for clone")
            return
        repo = integration.clone_repository(args.repo, branch=args.branch)
        if repo:
            print(f"\nCloned: {repo.name}")
            print(f"  Path: {repo.clone_path}")
            print(f"  Branch: {repo.current_branch}")
    
    elif args.action == "update":
        if not args.repo:
            print("Error: --repo required for update")
            return
        success = integration.update_repository(args.repo)
        print(f"\nUpdate {'successful' if success else 'failed'}")
    
    elif args.action == "list":
        repos = integration.list_repositories()
        print(f"\nTracked repositories: {len(repos)}")
        for repo in repos:
            print(f"\n  {repo.name}")
            print(f"    Branch: {repo.current_branch}")
            print(f"    Commit: {repo.last_commit[:8] if repo.last_commit else 'N/A'}")
            print(f"    Last ingestion: {repo.last_ingestion or 'Never'}")
            print(f"    Documents: {repo.document_count}")
    
    elif args.action == "ingest":
        if not args.repo:
            print("Error: --repo required for ingest")
            return
        success = integration.ingest_repository(args.repo)
        print(f"\nIngestion {'successful' if success else 'failed'}")


if __name__ == "__main__":
    main()
