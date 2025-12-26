#!/usr/bin/env python3
"""
Tests for GitHub integration module.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from github_integration import GitHubAPI, GitHubIntegration, Repository


class TestGitHubAPI:
    """Tests for GitHubAPI class."""
    
    def test_init_without_token(self):
        """Test initialization without token."""
        api = GitHubAPI()
        assert api.token is None or api.token == ""
    
    def test_init_with_token(self):
        """Test initialization with token."""
        api = GitHubAPI(token="test_token")
        assert api.token == "test_token"
    
    @patch('github_integration.REQUESTS_AVAILABLE', False)
    def test_api_unavailable(self):
        """Test API when requests is unavailable."""
        api = GitHubAPI()
        result = api.get_repository_info("owner", "repo")
        assert result is None


class TestGitHubIntegration:
    """Tests for GitHubIntegration class."""
    
    def test_init(self, tmp_path):
        """Test initialization."""
        integration = GitHubIntegration(
            repos_directory=str(tmp_path),
            github_token="test_token",
        )
        
        assert integration.repos_directory == tmp_path
        assert integration.github_token == "test_token"
        assert integration.tracking_file.exists()
    
    def test_parse_repo_url(self, tmp_path):
        """Test repository URL parsing."""
        integration = GitHubIntegration(str(tmp_path))
        
        # Test HTTPS URL
        result = integration._parse_repo_url("https://github.com/owner/repo")
        assert result == ("owner", "repo")
        
        # Test HTTPS URL with .git
        result = integration._parse_repo_url("https://github.com/owner/repo.git")
        assert result == ("owner", "repo")
        
        # Test SSH URL
        result = integration._parse_repo_url("git@github.com:owner/repo.git")
        assert result == ("owner", "repo")
        
        # Test owner/repo format
        result = integration._parse_repo_url("owner/repo")
        assert result == ("owner", "repo")
        
        # Test invalid URL
        result = integration._parse_repo_url("invalid")
        assert result is None
    
    def test_load_save_tracking(self, tmp_path):
        """Test loading and saving repository tracking."""
        integration = GitHubIntegration(str(tmp_path))
        
        # Add a repository
        repo = Repository(
            name="owner/repo",
            url="https://github.com/owner/repo",
            clone_path=tmp_path / "owner_repo",
            current_branch="main",
            last_commit="abc123",
            document_count=10,
            chunk_count=100,
        )
        integration.repositories["owner/repo"] = repo
        integration._save_tracking()
        
        # Create new integration and load tracking
        integration2 = GitHubIntegration(str(tmp_path))
        
        assert "owner/repo" in integration2.repositories
        loaded_repo = integration2.repositories["owner/repo"]
        assert loaded_repo.name == "owner/repo"
        assert loaded_repo.current_branch == "main"
        assert loaded_repo.last_commit == "abc123"
        assert loaded_repo.document_count == 10
    
    def test_list_repositories(self, tmp_path):
        """Test listing repositories."""
        integration = GitHubIntegration(str(tmp_path))
        
        # Add repositories
        repo1 = Repository(name="owner/repo1", url="https://github.com/owner/repo1")
        repo2 = Repository(name="owner/repo2", url="https://github.com/owner/repo2")
        
        integration.repositories["owner/repo1"] = repo1
        integration.repositories["owner/repo2"] = repo2
        
        repos = integration.list_repositories()
        
        assert len(repos) == 2
        names = [r.name for r in repos]
        assert "owner/repo1" in names
        assert "owner/repo2" in names
    
    def test_remove_repository(self, tmp_path):
        """Test removing a repository."""
        integration = GitHubIntegration(str(tmp_path))
        
        # Add repository
        repo = Repository(
            name="owner/repo",
            url="https://github.com/owner/repo",
            clone_path=tmp_path / "owner_repo",
        )
        integration.repositories["owner/repo"] = repo
        
        # Remove repository
        result = integration.remove_repository("owner/repo")
        
        assert result
        assert "owner/repo" not in integration.repositories
    
    def test_progress_callback(self, tmp_path):
        """Test progress callback."""
        callback_data = []
        
        def callback(data):
            callback_data.append(data)
        
        integration = GitHubIntegration(
            str(tmp_path),
            progress_callback=callback,
        )
        
        integration._notify_progress("Test message", 50, "Test details")
        
        assert len(callback_data) == 1
        assert callback_data[0]["message"] == "Test message"
        assert callback_data[0]["percent"] == 50
        assert callback_data[0]["details"] == "Test details"
    
    @patch('subprocess.run')
    def test_get_current_commit(self, mock_run, tmp_path):
        """Test getting current commit hash."""
        mock_run.return_value = Mock(
            stdout="abc123def456\n",
            returncode=0,
        )
        
        integration = GitHubIntegration(str(tmp_path))
        commit = integration._get_current_commit(tmp_path / "repo")
        
        assert commit == "abc123def456"
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_clone_repository_invalid_url(self, mock_run, tmp_path):
        """Test cloning with invalid URL."""
        integration = GitHubIntegration(str(tmp_path))
        
        result = integration.clone_repository("invalid_url")
        
        assert result is None
        # subprocess should not be called for invalid URL
        mock_run.assert_not_called()
    
    @patch('subprocess.run')
    def test_clone_repository_success(self, mock_run, tmp_path):
        """Test successful repository cloning."""
        # Mock subprocess calls
        mock_run.side_effect = [
            # git clone
            Mock(returncode=0, stdout="", stderr=""),
            # git rev-parse HEAD
            Mock(returncode=0, stdout="abc123\n", stderr=""),
            # git branch --show-current
            Mock(returncode=0, stdout="main\n", stderr=""),
        ]
        
        integration = GitHubIntegration(str(tmp_path))
        
        # Mock the auto-ingest to avoid actually ingesting
        with patch.object(integration, 'ingest_repository', return_value=True):
            repo = integration.clone_repository("owner/repo", auto_ingest=False)
        
        assert repo is not None
        assert repo.name == "owner/repo"
        assert repo.current_branch == "main"
        assert repo.last_commit == "abc123"


class TestRepository:
    """Tests for Repository dataclass."""
    
    def test_repository_creation(self):
        """Test creating a Repository instance."""
        repo = Repository(
            name="owner/repo",
            url="https://github.com/owner/repo",
            clone_path=Path("/tmp/repo"),
            current_branch="main",
            last_commit="abc123",
            document_count=10,
            chunk_count=100,
        )
        
        assert repo.name == "owner/repo"
        assert repo.url == "https://github.com/owner/repo"
        assert repo.current_branch == "main"
        assert repo.last_commit == "abc123"
        assert repo.document_count == 10
        assert repo.chunk_count == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
