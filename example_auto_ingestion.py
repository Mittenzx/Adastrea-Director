#!/usr/bin/env python3
"""
Example usage of auto-ingestion and GitHub integration features.

This script demonstrates how to use the new features:
1. Auto-detect and ingest project codebase
2. Clone and ingest GitHub repositories
3. Enable file watching for real-time updates
4. Schedule periodic ingestion

Usage:
    # Auto-ingest current project
    python example_auto_ingestion.py --project .
    
    # Clone and ingest a GitHub repository
    python example_auto_ingestion.py --github owner/repo
    
    # Enable file watching
    python example_auto_ingestion.py --project . --watch
    
    # Schedule periodic ingestion
    python example_auto_ingestion.py --project . --schedule 2.0
"""

import argparse
import sys

# Import the new modules
from auto_ingestion import AutoIngestion
from github_integration import GitHubIntegration


def demo_auto_ingestion(project_root: str, watch: bool = False, schedule: float = 0):
    """
    Demonstrate auto-ingestion of project codebase.
    
    Args:
        project_root: Root directory of the project
        watch: Enable file watching
        schedule: Scheduled ingestion interval in hours (0 = disabled)
    """
    print("\n" + "=" * 60)
    print("AUTO-INGESTION DEMO")
    print("=" * 60)
    
    # Progress callback
    def progress_callback(data):
        percent = data.get('percent', 0)
        message = data.get('message', '')
        details = data.get('details', '')
        
        bar_width = 40
        filled = int(bar_width * percent / 100)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        print(f"\r[{bar}] {percent:3.0f}% | {message}", end='', flush=True)
        if details:
            print(f"\n  ℹ {details}")
    
    # Create auto-ingestion instance
    auto_ingest = AutoIngestion(
        project_root=project_root,
        collection_name="adastrea_project",
        persist_directory="./chroma_db_project",
        progress_callback=progress_callback,
    )
    
    # Detect project
    print(f"\nProject root: {project_root}")
    dirs = auto_ingest.detect_project()
    print(f"\nDetected {len(dirs)} project directories:")
    for dir_path in dirs:
        print(f"  • {dir_path.name}/")
    
    # Run full ingestion
    print("\nRunning full project ingestion...")
    stats = auto_ingest.run_full_ingestion()
    
    print(f"\n\n✓ Ingestion complete!")
    print(f"  Total files: {stats.get('total_files', 0)}")
    print(f"  Added: {stats.get('added', 0)}")
    print(f"  Updated: {stats.get('updated', 0)}")
    print(f"  Skipped: {stats.get('skipped', 0)}")
    if stats.get('errors', 0) > 0:
        print(f"  Errors: {stats.get('errors', 0)}")
    
    # Enable file watching if requested
    if watch:
        print("\n" + "-" * 60)
        print("Enabling file watching for real-time updates...")
        if auto_ingest.start_file_watching():
            print("✓ File watching active")
            print("  Changes will be automatically ingested")
        else:
            print("✗ File watching unavailable (install watchdog)")
    
    # Enable scheduled ingestion if requested
    if schedule > 0:
        print("\n" + "-" * 60)
        print(f"Enabling scheduled ingestion (every {schedule} hours)...")
        auto_ingest.start_scheduled_ingestion(interval_hours=schedule)
        print("✓ Scheduled ingestion active")
    
    # Keep running if watching or scheduling enabled
    if watch or schedule > 0:
        print("\nPress Ctrl+C to stop...")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping...")
            auto_ingest.stop_file_watching()
            auto_ingest.stop_scheduled_ingestion()
            print("✓ Stopped")


def demo_github_integration(repo_url: str, branch: str = None, token: str = None):
    """
    Demonstrate GitHub repository integration.
    
    Args:
        repo_url: GitHub repository URL or owner/repo
        branch: Branch name (optional)
        token: GitHub token (optional)
    """
    print("\n" + "=" * 60)
    print("GITHUB INTEGRATION DEMO")
    print("=" * 60)
    
    # Progress callback
    def progress_callback(data):
        percent = data.get('percent', 0)
        message = data.get('message', '')
        details = data.get('details', '')
        
        bar_width = 40
        filled = int(bar_width * percent / 100)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        print(f"\r[{bar}] {percent:3.0f}% | {message}", end='', flush=True)
        if details:
            print(f"\n  ℹ {details}")
    
    # Create GitHub integration instance
    integration = GitHubIntegration(
        repos_directory="./repos",
        github_token=token,
        progress_callback=progress_callback,
    )
    
    print(f"\nRepository: {repo_url}")
    if branch:
        print(f"Branch: {branch}")
    
    # Clone repository
    print("\nCloning and ingesting repository...")
    repo = integration.clone_repository(
        repo_url=repo_url,
        branch=branch,
        auto_ingest=True,
    )
    
    if repo:
        print(f"\n\n✓ Repository ready!")
        print(f"  Name: {repo.name}")
        print(f"  Branch: {repo.current_branch}")
        print(f"  Commit: {repo.last_commit[:8] if repo.last_commit else 'N/A'}")
        print(f"  Documents: {repo.document_count}")
        print(f"  Chunks: {repo.chunk_count}")
        print(f"  Path: {repo.clone_path}")
    else:
        print("\n\n✗ Failed to clone repository")
        return
    
    # List all tracked repositories
    print("\n" + "-" * 60)
    print("All tracked repositories:")
    repos = integration.list_repositories()
    for r in repos:
        print(f"\n  {r.name}")
        print(f"    Branch: {r.current_branch}")
        print(f"    Documents: {r.document_count}")
        print(f"    Last ingestion: {r.last_ingestion or 'Never'}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Demo of auto-ingestion and GitHub integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-ingest current project
  python example_auto_ingestion.py --project .
  
  # Auto-ingest with file watching
  python example_auto_ingestion.py --project . --watch
  
  # Auto-ingest with scheduled updates every 2 hours
  python example_auto_ingestion.py --project . --schedule 2.0
  
  # Clone and ingest GitHub repository
  python example_auto_ingestion.py --github owner/repo
  
  # Clone specific branch
  python example_auto_ingestion.py --github owner/repo --branch develop
  
  # Clone private repository (set GITHUB_TOKEN env var or use --token)
  export GITHUB_TOKEN=ghp_xxxxx
  python example_auto_ingestion.py --github owner/private-repo
"""
    )
    
    parser.add_argument(
        "--project",
        type=str,
        help="Project root directory for auto-ingestion",
    )
    parser.add_argument(
        "--github",
        type=str,
        help="GitHub repository URL or owner/repo",
    )
    parser.add_argument(
        "--branch",
        type=str,
        help="Branch name for GitHub repository",
    )
    parser.add_argument(
        "--token",
        type=str,
        help="GitHub personal access token",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Enable file watching for real-time updates",
    )
    parser.add_argument(
        "--schedule",
        type=float,
        default=0,
        help="Enable scheduled ingestion (hours between runs)",
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.project and not args.github:
        parser.print_help()
        print("\nError: Must specify either --project or --github")
        sys.exit(1)
    
    # Run demos
    if args.project:
        demo_auto_ingestion(
            project_root=args.project,
            watch=args.watch,
            schedule=args.schedule,
        )
    
    if args.github:
        demo_github_integration(
            repo_url=args.github,
            branch=args.branch,
            token=args.token,
        )


if __name__ == "__main__":
    main()
