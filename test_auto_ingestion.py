#!/usr/bin/env python3
"""
Tests for auto-ingestion module.
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from auto_ingestion import ProjectDetector, AutoIngestion


class TestProjectDetector:
    """Tests for ProjectDetector class."""
    
    def test_detect_project_dirs(self, tmp_path):
        """Test detection of project directories."""
        # Create test directory structure
        (tmp_path / "Source").mkdir()
        (tmp_path / "Content").mkdir()
        (tmp_path / "Docs").mkdir()
        (tmp_path / "NotAProjectDir").mkdir()
        
        detector = ProjectDetector(str(tmp_path))
        dirs = detector.detect_project_dirs()
        
        # Should find Source, Content, and Docs
        assert len(dirs) == 3
        dir_names = [d.name for d in dirs]
        assert "Source" in dir_names
        assert "Content" in dir_names
        assert "Docs" in dir_names
        assert "NotAProjectDir" not in dir_names
    
    def test_should_include_file(self, tmp_path):
        """Test file inclusion logic."""
        detector = ProjectDetector(str(tmp_path))
        
        # C++ files should be included
        assert detector.should_include_file(Path("test.cpp"))
        assert detector.should_include_file(Path("test.h"))
        
        # Python files should be included
        assert detector.should_include_file(Path("test.py"))
        
        # Documentation files should be included
        assert detector.should_include_file(Path("test.md"))
        assert detector.should_include_file(Path("test.txt"))
        
        # Other files should be excluded
        assert not detector.should_include_file(Path("test.exe"))
        assert not detector.should_include_file(Path("test.dll"))
    
    def test_exclude_dirs(self, tmp_path):
        """Test directory exclusion logic."""
        detector = ProjectDetector(str(tmp_path))
        
        # Files in excluded directories should not be included
        assert not detector.should_include_file(Path(".git/config"))
        assert not detector.should_include_file(Path("node_modules/package.json"))
        assert not detector.should_include_file(Path("__pycache__/test.pyc"))
    
    def test_scan_project_files(self, tmp_path):
        """Test scanning of project files."""
        # Create test files
        source_dir = tmp_path / "Source"
        source_dir.mkdir()
        
        (source_dir / "main.cpp").write_text("int main() {}")
        (source_dir / "main.h").write_text("#pragma once")
        (source_dir / "readme.md").write_text("# README")
        (source_dir / "test.exe").write_text("binary")
        
        # Create excluded directory
        cache_dir = source_dir / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "test.pyc").write_text("bytecode")
        
        detector = ProjectDetector(str(tmp_path))
        detector.detect_project_dirs()
        files = detector.scan_project_files()
        
        # Should find 3 files (not .exe or .pyc)
        assert len(files) == 3
        file_names = [f.name for f in files]
        assert "main.cpp" in file_names
        assert "main.h" in file_names
        assert "readme.md" in file_names
        assert "test.exe" not in file_names
        assert "test.pyc" not in file_names


class TestAutoIngestion:
    """Tests for AutoIngestion class."""
    
    def test_init(self, tmp_path):
        """Test initialization."""
        auto_ingest = AutoIngestion(
            project_root=str(tmp_path),
            collection_name="test_collection",
            persist_directory=str(tmp_path / "db"),
        )
        
        assert auto_ingest.project_root == tmp_path
        assert auto_ingest.collection_name == "test_collection"
        assert auto_ingest.persist_directory == str(tmp_path / "db")
        assert not auto_ingest.file_watch_enabled
        assert not auto_ingest.scheduled_ingestion_enabled
    
    def test_detect_project(self, tmp_path):
        """Test project detection."""
        # Create test directories
        (tmp_path / "Source").mkdir()
        (tmp_path / "Content").mkdir()
        
        auto_ingest = AutoIngestion(str(tmp_path))
        dirs = auto_ingest.detect_project()
        
        assert len(dirs) == 2
        dir_names = [d.name for d in dirs]
        assert "Source" in dir_names
        assert "Content" in dir_names
    
    def test_queue_file_for_ingestion(self, tmp_path):
        """Test file queuing."""
        auto_ingest = AutoIngestion(str(tmp_path))
        
        file1 = Path("test1.cpp")
        file2 = Path("test2.cpp")
        
        auto_ingest.queue_file_for_ingestion(file1)
        auto_ingest.queue_file_for_ingestion(file2)
        
        assert len(auto_ingest.file_queue) == 2
        assert file1 in auto_ingest.file_queue
        assert file2 in auto_ingest.file_queue
    
    def test_progress_callback(self, tmp_path):
        """Test progress callback."""
        callback_data = []
        
        def callback(data):
            callback_data.append(data)
        
        auto_ingest = AutoIngestion(
            str(tmp_path),
            progress_callback=callback,
        )
        
        auto_ingest._notify_progress("Test message", 50, "Test details")
        
        assert len(callback_data) == 1
        assert callback_data[0]["message"] == "Test message"
        assert callback_data[0]["percent"] == 50
        assert callback_data[0]["details"] == "Test details"
    
    @patch('auto_ingestion.WATCHDOG_AVAILABLE', False)
    def test_file_watching_unavailable(self, tmp_path):
        """Test file watching when watchdog is unavailable."""
        auto_ingest = AutoIngestion(str(tmp_path))
        
        result = auto_ingest.start_file_watching()
        
        assert not result
        assert not auto_ingest.file_watch_enabled
    
    @patch('auto_ingestion.WATCHDOG_AVAILABLE', True)
    @patch('auto_ingestion.Observer')
    def test_start_file_watching(self, mock_observer_class, tmp_path):
        """Test starting file watching."""
        # Create test directory
        (tmp_path / "Source").mkdir()
        
        # Mock observer
        mock_observer = MagicMock()
        mock_observer_class.return_value = mock_observer
        
        auto_ingest = AutoIngestion(str(tmp_path))
        auto_ingest.detect_project()
        
        result = auto_ingest.start_file_watching()
        
        assert result
        assert auto_ingest.file_watch_enabled
        mock_observer.start.assert_called_once()
    
    @patch('auto_ingestion.WATCHDOG_AVAILABLE', True)
    @patch('auto_ingestion.Observer')
    def test_stop_file_watching(self, mock_observer_class, tmp_path):
        """Test stopping file watching."""
        # Mock observer
        mock_observer = MagicMock()
        mock_observer_class.return_value = mock_observer
        
        auto_ingest = AutoIngestion(str(tmp_path))
        auto_ingest.file_watch_enabled = True
        auto_ingest.observer = mock_observer
        
        auto_ingest.stop_file_watching()
        
        assert not auto_ingest.file_watch_enabled
        mock_observer.stop.assert_called_once()
        mock_observer.join.assert_called_once()
    
    def test_scheduled_ingestion(self, tmp_path):
        """Test scheduled ingestion start/stop."""
        auto_ingest = AutoIngestion(str(tmp_path))
        
        # Start scheduled ingestion
        auto_ingest.start_scheduled_ingestion(interval_hours=0.001)  # Very short interval for testing
        
        assert auto_ingest.scheduled_ingestion_enabled
        assert auto_ingest.schedule_thread is not None
        assert auto_ingest.schedule_thread.is_alive()
        
        # Stop scheduled ingestion
        auto_ingest.stop_scheduled_ingestion()
        
        assert not auto_ingest.scheduled_ingestion_enabled
        time.sleep(0.1)  # Give thread time to stop
        assert not auto_ingest.schedule_thread.is_alive()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
