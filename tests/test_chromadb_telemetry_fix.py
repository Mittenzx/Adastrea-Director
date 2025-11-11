#!/usr/bin/env python3
"""
Test to verify ChromaDB telemetry is properly disabled.

This test ensures that the ANONYMIZED_TELEMETRY environment variable
is set before ChromaDB is imported, preventing telemetry errors.
"""

import pytest
import os
import sys
import subprocess
from pathlib import Path


class TestChromaDBTelemetryFix:
    """Test that ChromaDB telemetry is properly disabled."""
    
    @pytest.mark.unit
    def test_ingest_py_sets_telemetry_env_before_import(self):
        """Test that ingest.py sets ANONYMIZED_TELEMETRY before importing chromadb."""
        # Read the ingest.py file
        ingest_file = Path(__file__).parent.parent / "ingest.py"
        content = ingest_file.read_text()
        
        # Find the position of telemetry setting
        telemetry_pos = content.find('os.environ["ANONYMIZED_TELEMETRY"]')
        assert telemetry_pos > 0, "ANONYMIZED_TELEMETRY setting not found in ingest.py"
        
        # Find the position of langchain_community import
        langchain_import_pos = content.find('from langchain_community')
        assert langchain_import_pos > 0, "langchain_community import not found"
        
        # Verify telemetry is set BEFORE the import
        assert telemetry_pos < langchain_import_pos, (
            "ANONYMIZED_TELEMETRY must be set BEFORE importing langchain_community"
        )
    
    @pytest.mark.unit
    def test_main_py_sets_telemetry_env_before_import(self):
        """Test that main.py sets ANONYMIZED_TELEMETRY before importing chromadb."""
        main_file = Path(__file__).parent.parent / "main.py"
        content = main_file.read_text()
        
        telemetry_pos = content.find('os.environ["ANONYMIZED_TELEMETRY"]')
        assert telemetry_pos > 0, "ANONYMIZED_TELEMETRY setting not found in main.py"
        
        langchain_import_pos = content.find('from langchain_community')
        assert langchain_import_pos > 0, "langchain_community import not found"
        
        assert telemetry_pos < langchain_import_pos, (
            "ANONYMIZED_TELEMETRY must be set BEFORE importing langchain_community"
        )
    
    @pytest.mark.unit
    def test_telemetry_env_var_is_set(self):
        """Test that importing ingest module sets the telemetry env var."""
        # Import ingest (which should have already set the env var at module level)
        import ingest
        
        # The env var should be set by the time we import
        # Since ingest.py sets it at the module level before any other imports
        assert os.environ.get('ANONYMIZED_TELEMETRY') == 'False', (
            "ANONYMIZED_TELEMETRY should be set to 'False' by ingest module"
        )
    
    @pytest.mark.unit
    def test_chromadb_import_without_telemetry_errors(self):
        """Test that ChromaDB can be imported without telemetry errors."""
        # This test verifies that importing chromadb doesn't produce telemetry errors
        # when ANONYMIZED_TELEMETRY is set to False
        
        # Set the environment variable
        os.environ['ANONYMIZED_TELEMETRY'] = 'False'
        
        # Try to import chromadb and use it
        try:
            import chromadb
            
            # Create a client (this would trigger telemetry if not disabled)
            client = chromadb.Client()
            
            # Try to get or create a collection (this also triggers telemetry events)
            _ = client.get_or_create_collection(
                name=f"test_telemetry_{os.getpid()}"
            )
            
        except Exception as e:
            error_msg = str(e)
            # Check if it's a telemetry-related error
            if "capture()" in error_msg or "posthog" in error_msg.lower():
                pytest.fail(f"ChromaDB telemetry error occurred: {error_msg}")
            else:
                # Some other error - re-raise it
                raise
    
    @pytest.mark.unit
    def test_validate_requirements_sets_telemetry_env(self):
        """Test that validate_requirements.py sets ANONYMIZED_TELEMETRY."""
        validate_file = Path(__file__).parent.parent / "validate_requirements.py"
        content = validate_file.read_text()
        
        assert 'os.environ["ANONYMIZED_TELEMETRY"]' in content, (
            "validate_requirements.py should set ANONYMIZED_TELEMETRY"
        )
    
    @pytest.mark.unit
    def test_gui_director_sets_telemetry_env(self):
        """Test that gui_director.py sets ANONYMIZED_TELEMETRY."""
        gui_file = Path(__file__).parent.parent / "gui_director.py"
        content = gui_file.read_text()
        
        assert 'os.environ["ANONYMIZED_TELEMETRY"]' in content, (
            "gui_director.py should set ANONYMIZED_TELEMETRY"
        )
    
    @pytest.mark.unit
    def test_test_ingest_list_sets_telemetry_env(self):
        """Test that test_ingest_list.py sets ANONYMIZED_TELEMETRY."""
        test_file = Path(__file__).parent.parent / "test_ingest_list.py"
        content = test_file.read_text()
        
        assert 'os.environ["ANONYMIZED_TELEMETRY"]' in content, (
            "test_ingest_list.py should set ANONYMIZED_TELEMETRY"
        )
    
    @pytest.mark.integration
    def test_ingest_script_runs_without_telemetry_errors(self, tmp_path):
        """Integration test: Run ingest.py and check for telemetry errors."""
        # Create a temporary directory with a simple file
        test_dir = tmp_path / "test_docs"
        test_dir.mkdir()
        (test_dir / "test.txt").write_text("Test content for ingestion")
        
        # Get the path to ingest.py
        ingest_script = Path(__file__).parent.parent / "ingest.py"
        
        # Run the script with --stats flag (doesn't require API key)
        result = subprocess.run(
            [sys.executable, str(ingest_script), "--stats"],
            cwd=str(ingest_script.parent),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # Replace invalid UTF-8 sequences instead of failing
            timeout=30
        )
        
        # Check for telemetry errors in stderr
        stderr_lower = result.stderr.lower()
        
        assert "capture() takes 1 positional argument" not in result.stderr, (
            f"Telemetry signature error found in stderr:\n{result.stderr}"
        )
        
        assert not ("posthog" in stderr_lower and "failed to send telemetry" in stderr_lower), (
            f"Posthog telemetry error found in stderr:\n{result.stderr}"
        )


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])
