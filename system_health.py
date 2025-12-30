#!/usr/bin/env python3
"""
System Health Checker

Provides health check functionality for critical system components:
- LLM API connectivity and configuration
- Vector database status and document count
- Remote Control API connectivity (if configured)
- File system access and permissions
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health status for a component."""
    component: str
    healthy: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    checked_at: datetime = None
    
    def __post_init__(self):
        if self.checked_at is None:
            self.checked_at = datetime.now()


class SystemHealthChecker:
    """
    Checks the health of critical system components.
    
    Provides diagnostic information about:
    - LLM API configuration and connectivity
    - Vector database status
    - Remote Control API (optional)
    - File system access
    """
    
    def __init__(self):
        """Initialize the health checker."""
        self._last_checks: Dict[str, HealthStatus] = {}
    
    def check_llm_api(self) -> HealthStatus:
        """
        Check LLM API configuration and availability.
        
        Returns:
            HealthStatus for LLM API
        """
        try:
            from llm_config import get_api_key_env_var, get_provider_name
            
            provider = get_provider_name()
            api_key_var = get_api_key_env_var()
            
            # Check if API key is set
            api_key = os.getenv(api_key_var)
            
            if not api_key:
                status = HealthStatus(
                    component="LLM API",
                    healthy=False,
                    message=f"API key not configured ({api_key_var})",
                    details={
                        'provider': provider,
                        'env_var': api_key_var,
                        'configured': False
                    }
                )
            else:
                # API key exists, but we won't test connectivity (to avoid costs)
                status = HealthStatus(
                    component="LLM API",
                    healthy=True,
                    message=f"{provider} API key configured",
                    details={
                        'provider': provider,
                        'env_var': api_key_var,
                        'configured': True,
                        'key_length': len(api_key)
                    }
                )
            
            self._last_checks['llm_api'] = status
            return status
            
        except Exception as e:
            logger.error(f"Error checking LLM API: {e}", exc_info=True)
            status = HealthStatus(
                component="LLM API",
                healthy=False,
                message=f"Error checking LLM API: {str(e)}",
                details={'error': str(e)}
            )
            self._last_checks['llm_api'] = status
            return status
    
    def check_vector_database(self, persist_directory: str = "./chroma_db",
                              collection_name: str = "adastrea_docs") -> HealthStatus:
        """
        Check vector database status and document count.
        
        Args:
            persist_directory: Path to vector database
            collection_name: Name of the collection to check
            
        Returns:
            HealthStatus for vector database
        """
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Check if directory exists
            if not os.path.exists(persist_directory):
                status = HealthStatus(
                    component="Vector Database",
                    healthy=False,
                    message=f"Database directory not found: {persist_directory}",
                    details={
                        'path': persist_directory,
                        'exists': False
                    }
                )
                self._last_checks['vector_db'] = status
                return status
            
            # Try to connect to database
            client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=True)
            )
            
            # Try to get collection
            try:
                collection = client.get_collection(name=collection_name)
                doc_count = collection.count()
                
                if doc_count == 0:
                    status = HealthStatus(
                        component="Vector Database",
                        healthy=False,
                        message="Database is empty - no documents ingested",
                        details={
                            'path': persist_directory,
                            'collection': collection_name,
                            'document_count': doc_count,
                            'exists': True
                        }
                    )
                else:
                    status = HealthStatus(
                        component="Vector Database",
                        healthy=True,
                        message=f"Database operational with {doc_count} documents",
                        details={
                            'path': persist_directory,
                            'collection': collection_name,
                            'document_count': doc_count,
                            'exists': True
                        }
                    )
            except Exception as e:
                # Collection doesn't exist
                status = HealthStatus(
                    component="Vector Database",
                    healthy=False,
                    message=f"Collection '{collection_name}' not found",
                    details={
                        'path': persist_directory,
                        'collection': collection_name,
                        'error': str(e)
                    }
                )
            
            self._last_checks['vector_db'] = status
            return status
            
        except Exception as e:
            logger.error(f"Error checking vector database: {e}", exc_info=True)
            status = HealthStatus(
                component="Vector Database",
                healthy=False,
                message=f"Error accessing database: {str(e)}",
                details={
                    'path': persist_directory,
                    'error': str(e)
                }
            )
            self._last_checks['vector_db'] = status
            return status
    
    def check_remote_control(self, host: str = "localhost", 
                            port: int = 30010) -> HealthStatus:
        """
        Check Remote Control API connectivity (optional).
        
        Args:
            host: Remote Control API host
            port: Remote Control API port
            
        Returns:
            HealthStatus for Remote Control API
        """
        try:
            import socket
            
            # Try to connect to the Remote Control API
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                status = HealthStatus(
                    component="Remote Control API",
                    healthy=True,
                    message=f"Connected to {host}:{port}",
                    details={
                        'host': host,
                        'port': port,
                        'connected': True
                    }
                )
            else:
                status = HealthStatus(
                    component="Remote Control API",
                    healthy=False,
                    message=f"Cannot connect to {host}:{port} (Unreal Editor may not be running)",
                    details={
                        'host': host,
                        'port': port,
                        'connected': False,
                        'note': 'This is optional - only needed for UE integration'
                    }
                )
            
            self._last_checks['remote_control'] = status
            return status
            
        except Exception as e:
            logger.error(f"Error checking Remote Control API: {e}", exc_info=True)
            status = HealthStatus(
                component="Remote Control API",
                healthy=False,
                message=f"Error checking connection: {str(e)}",
                details={
                    'host': host,
                    'port': port,
                    'error': str(e),
                    'note': 'This is optional - only needed for UE integration'
                }
            )
            self._last_checks['remote_control'] = status
            return status
    
    def check_file_system(self, paths: list = None) -> HealthStatus:
        """
        Check file system access and permissions.
        
        Args:
            paths: List of paths to check (default: common directories)
            
        Returns:
            HealthStatus for file system
        """
        if paths is None:
            paths = ['./chroma_db', './logs', '.']
        
        try:
            issues = []
            details = {}
            
            for path in paths:
                if not os.path.exists(path):
                    issues.append(f"{path} does not exist")
                    details[path] = 'not_found'
                elif not os.access(path, os.R_OK):
                    issues.append(f"{path} is not readable")
                    details[path] = 'not_readable'
                elif not os.access(path, os.W_OK):
                    issues.append(f"{path} is not writable")
                    details[path] = 'not_writable'
                else:
                    details[path] = 'ok'
            
            if issues:
                status = HealthStatus(
                    component="File System",
                    healthy=False,
                    message=f"File system issues: {', '.join(issues)}",
                    details=details
                )
            else:
                status = HealthStatus(
                    component="File System",
                    healthy=True,
                    message="All paths accessible",
                    details=details
                )
            
            self._last_checks['file_system'] = status
            return status
            
        except Exception as e:
            logger.error(f"Error checking file system: {e}", exc_info=True)
            status = HealthStatus(
                component="File System",
                healthy=False,
                message=f"Error checking file system: {str(e)}",
                details={'error': str(e)}
            )
            self._last_checks['file_system'] = status
            return status
    
    def check_all(self) -> Dict[str, HealthStatus]:
        """
        Run all health checks.
        
        Returns:
            Dictionary of component name to HealthStatus
        """
        results = {
            'llm_api': self.check_llm_api(),
            'vector_db': self.check_vector_database(),
            'file_system': self.check_file_system(),
        }
        
        # Remote Control is optional, only check if it's likely to be used
        # (don't include by default to avoid noise)
        
        return results
    
    def get_last_check(self, component: str) -> Optional[HealthStatus]:
        """
        Get the last health check result for a component.
        
        Args:
            component: Component name
            
        Returns:
            Last HealthStatus or None if not checked yet
        """
        return self._last_checks.get(component)
    
    def is_system_healthy(self) -> bool:
        """
        Check if all critical components are healthy.
        
        Returns:
            True if all critical components are healthy
        """
        critical_components = ['llm_api', 'vector_db']
        
        for component in critical_components:
            status = self._last_checks.get(component)
            if not status or not status.healthy:
                return False
        
        return True
