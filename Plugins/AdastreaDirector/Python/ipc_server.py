#!/usr/bin/env python3
"""
IPC Server for Adastrea Director Plugin

This server provides socket-based IPC communication between the Unreal Engine
plugin (C++) and the Python backend (RAG system, planning agents, etc.).

Week 3 Enhancements:
- Performance monitoring and metrics
- Optimized request routing
- Response serialization with timing
- Integration hooks for RAG system

Usage:
    python ipc_server.py --port 5555
"""

import os
import socket
import json
import sys
import argparse
import logging
import threading
import time
from typing import Dict, Any
from collections import defaultdict
from textwrap import dedent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AdastreaIPCServer')


class PerformanceMetrics:
    """Track performance metrics for the IPC server."""
    
    def __init__(self):
        """Initialize metrics tracking."""
        self.request_count = defaultdict(int)
        self.request_times = defaultdict(list)
        self.error_count = defaultdict(int)
        self.total_requests = 0
        self.total_errors = 0
        self._lock = threading.Lock()
    
    def record_request(self, request_type: str, duration: float, success: bool = True):
        """
        Record a request's performance metrics.
        
        Args:
            request_type: Type of request
            duration: Time taken in seconds
            success: Whether request succeeded
        """
        with self._lock:
            self.request_count[request_type] += 1
            self.request_times[request_type].append(duration)
            self.total_requests += 1
            
            if not success:
                self.error_count[request_type] += 1
                self.total_errors += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        with self._lock:
            stats = {
                'total_requests': self.total_requests,
                'total_errors': self.total_errors,
                'by_type': {}
            }
            
            for req_type in self.request_count:
                times = self.request_times[req_type]
                if times:
                    avg_time = sum(times) / len(times)
                    max_time = max(times)
                    min_time = min(times)
                else:
                    avg_time = max_time = min_time = 0
                
                stats['by_type'][req_type] = {
                    'count': self.request_count[req_type],
                    'errors': self.error_count[req_type],
                    'avg_time_ms': avg_time * 1000,
                    'min_time_ms': min_time * 1000,
                    'max_time_ms': max_time * 1000
                }
            
            return stats
    
    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self.request_count.clear()
            self.request_times.clear()
            self.error_count.clear()
            self.total_requests = 0
            self.total_errors = 0


class IPCServer:
    """IPC server for handling requests from the UE plugin with performance monitoring."""

    def __init__(self, host: str = '127.0.0.1', port: int = 5555, enable_metrics: bool = True):
        """
        Initialize the IPC server.
        
        Args:
            host: Host address to bind to (default: localhost)
            port: Port to listen on
            enable_metrics: Enable performance metrics tracking
        """
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.handlers = {}
        self.metrics = PerformanceMetrics() if enable_metrics else None
        
        # Register default handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default request handlers."""
        self.register_handler('ping', self._handle_ping)
        self.register_handler('metrics', self._handle_metrics)
        self.register_handler('query', self._handle_query)
        self.register_handler('plan', self._handle_plan)
        self.register_handler('analyze', self._handle_analyze)

    def register_handler(self, request_type: str, handler_func):
        """
        Register a handler function for a request type.
        
        Args:
            request_type: Type of request (e.g., 'query', 'plan')
            handler_func: Function to handle the request
        """
        self.handlers[request_type] = handler_func
        logger.info(f"Registered handler for '{request_type}'")

    def start(self):
        """Start the IPC server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            logger.info(f"IPC Server started on {self.host}:{self.port}")
            logger.info("Waiting for connections from Unreal Engine plugin...")
            
            self._accept_connections()
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise
        finally:
            self.stop()

    def stop(self):
        """Stop the IPC server."""
        self.running = False
        if self.socket:
            logger.info("Shutting down IPC server...")
            self.socket.close()
            self.socket = None

    def _accept_connections(self):
        """Accept and handle client connections."""
        while self.running:
            try:
                client_socket, client_address = self.socket.accept()
                logger.info(f"Client connected from {client_address}")
                
                # Handle client in a separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"Error accepting connection: {e}")

    def _handle_client(self, client_socket: socket.socket, client_address):
        """
        Handle a client connection.
        
        Args:
            client_socket: Client socket
            client_address: Client address tuple
        """
        try:
            while self.running:
                # Receive data (up to 4KB)
                data = client_socket.recv(4096)
                
                if not data:
                    logger.info(f"Client {client_address} disconnected")
                    break
                
                # Decode and parse request
                try:
                    request_str = data.decode('utf-8').strip()
                    request = json.loads(request_str)
                    
                    logger.debug(f"Received request: {request}")
                    
                    # Process request
                    response = self._process_request(request)
                    
                    # Send response
                    response_str = json.dumps(response) + '\n'
                    client_socket.sendall(response_str.encode('utf-8'))
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    error_response = {
                        'status': 'error',
                        'error': 'Invalid JSON format'
                    }
                    client_socket.sendall(
                        (json.dumps(error_response) + '\n').encode('utf-8')
                    )
                except Exception as e:
                    logger.error(f"Error processing request: {e}")
                    error_response = {
                        'status': 'error',
                        'error': str(e)
                    }
                    client_socket.sendall(
                        (json.dumps(error_response) + '\n').encode('utf-8')
                    )
                
        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()

    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request and return a response with performance tracking.
        
        Args:
            request: Request dictionary with 'type' and 'data' fields
            
        Returns:
            Response dictionary with timing information
        """
        start_time = time.perf_counter()
        request_type = request.get('type', '')
        request_data = request.get('data', '')
        success = False
        
        if not request_type:
            response = {
                'status': 'error',
                'error': 'Missing request type'
            }
            if self.metrics:
                self.metrics.record_request('invalid', time.perf_counter() - start_time, False)
            return response
        
        # Find and call appropriate handler
        handler = self.handlers.get(request_type)
        
        if handler:
            try:
                response = handler(request_data)
                success = response.get('status') == 'success'
            except Exception as e:
                logger.error(f"Handler error for '{request_type}': {e}")
                response = {
                    'status': 'error',
                    'error': f"Handler error: {str(e)}"
                }
                success = False
        else:
            response = {
                'status': 'error',
                'error': f"Unknown request type: {request_type}"
            }
            success = False
        
        # Record metrics
        duration = time.perf_counter() - start_time
        if self.metrics:
            self.metrics.record_request(request_type, duration, success)
        
        # Add timing information to response for performance monitoring
        response['processing_time_ms'] = round(duration * 1000, 2)
        
        return response

    # Helper methods
    
    @staticmethod
    def _extract_code_block_content(text: str) -> str:
        """
        Extract content from markdown code blocks in an LLM response.
        
        Handles markdown code blocks (```json ... ``` or ``` ... ```).
        Falls back to original text if no valid code block is found or extracted content is empty.
        
        Args:
            text: Raw LLM response text
            
        Returns:
            Extracted content from code block, or original text if no valid code block found
        """
        try:
            if '```json' in text:
                parts = text.split('```json')
                if len(parts) > 1:
                    inner_parts = parts[1].split('```')
                    if len(inner_parts) > 0:
                        content = inner_parts[0].strip()
                        if content:  # Only return if non-empty
                            return content
            elif '```' in text:
                parts = text.split('```')
                if len(parts) > 2:  # Need at least 3 parts: before, content, after
                    content = parts[1].strip()
                    if content:  # Only return if non-empty
                        return content
        except (IndexError, AttributeError):
            pass
        return text

    # Default handlers

    def _handle_ping(self, data: str) -> Dict[str, Any]:
        """Handle ping request for health checks."""
        logger.debug("Ping received")
        return {
            'status': 'success',
            'message': 'pong',
            'timestamp': time.time()
        }
    
    def _handle_metrics(self, data: str) -> Dict[str, Any]:
        """
        Handle metrics request to get performance statistics.
        
        Args:
            data: Optional parameter ('reset' to reset metrics)
        """
        if not self.metrics:
            return {
                'status': 'error',
                'error': 'Metrics not enabled'
            }
        
        if data == 'reset':
            self.metrics.reset()
            logger.info("Metrics reset")
            return {
                'status': 'success',
                'message': 'Metrics reset'
            }
        
        stats = self.metrics.get_stats()
        return {
            'status': 'success',
            'metrics': stats
        }

    def _handle_query(self, data: str) -> Dict[str, Any]:
        """
        Handle documentation query request using the RAG system.
        
        Attempts to use the RAG system if available. Falls back to LLM-only
        response if RAG database is not initialized.
        
        Environment Variables:
            CHROMA_PERSIST_DIRECTORY: Override the default persist directory path
        """
        logger.info(f"Query received: {data}")
        
        # Try to use the RAG system
        try:
            from rag_query import RAGQueryAgent
            
            # Check for persist directory - environment variable takes precedence
            env_persist_dir = os.environ.get('CHROMA_PERSIST_DIRECTORY')
            if env_persist_dir and os.path.exists(env_persist_dir):
                persist_directory = env_persist_dir
            else:
                # Check for common persist directory locations
                persist_dirs = [
                    './chroma_db',
                    '../../../chroma_db',
                    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'chroma_db'),
                ]
                
                persist_directory = None
                for pd in persist_dirs:
                    if os.path.exists(pd):
                        persist_directory = pd
                        break
            
            if persist_directory:
                logger.info(f"Using RAG database at: {persist_directory}")
                query_agent = RAGQueryAgent(
                    collection_name='adastrea_docs',
                    persist_directory=persist_directory
                )
                
                response = query_agent.process_query(data)
                
                return {
                    'status': 'success',
                    'result': response.get('answer', ''),
                    'sources': response.get('source_documents', []),
                    'processing_time': response.get('processing_time', 0),
                    'cached': response.get('cached', False)
                }
            else:
                logger.warning("RAG database not found, using LLM-only mode")
                
        except ImportError as e:
            logger.warning(f"RAG module not available: {e}")
        except ValueError as e:
            # Database is empty or not initialized
            logger.warning(f"RAG database issue: {e}")
        except Exception as e:
            logger.error(f"RAG query error: {e}")
        
        # Fallback: Try direct LLM query if RAG is not available
        try:
            from llm_config import get_llm
            
            llm = get_llm()
            
            prompt = f"""You are the Adastrea Director, an AI assistant specialized in helping with game development in Unreal Engine.

Answer the following question to the best of your ability. Be concise but thorough.

Question: {data}

Answer:"""
            
            response = llm.invoke(prompt)
            result_text = response.content if hasattr(response, 'content') else str(response)
            
            return {
                'status': 'success',
                'result': result_text,
                'sources': [],
                'note': 'Response generated without RAG context. For context-aware answers, please ingest documents first.'
            }
            
        except Exception as e:
            logger.error(f"LLM query error: {e}")
            # Final fallback with helpful message
            result_text = dedent(f"""
                I received your query: "{data}"

                However, I'm unable to provide a meaningful response at this time because:
                
                1. The RAG (Retrieval-Augmented Generation) system is not initialized. 
                   Please run the ingestion process to load your project documents.
                
                2. No LLM API key is configured. Please set up your API key:
                   - For Gemini (recommended): Set GEMINI_KEY environment variable
                   - For OpenAI: Set OPENAI_API_KEY environment variable
                
                To set up the system:
                1. Create a .env file with your API key
                2. Run: python ingest.py --docs-dir <your_docs_folder>
                3. Restart the IPC server
                
                For more information, see the README.md file.
            """).strip()
            
            return {
                'status': 'success',
                'result': result_text,
                'sources': [],
                'setup_required': True
            }

    def _handle_plan(self, data: str) -> Dict[str, Any]:
        """
        Handle planning request using the task decomposition agent.
        
        Attempts to use the planning agents if available.
        """
        logger.info(f"Plan request received: {data}")
        
        # Try to use actual planning agents
        try:
            from task_decomposition_agent import TaskDecompositionAgent
            from goal_analysis_agent import GoalAnalysisAgent
            
            # First analyze the goal
            goal_agent = GoalAnalysisAgent()
            analysis = goal_agent.analyze_goal(data)
            
            # Then decompose into tasks
            task_agent = TaskDecompositionAgent()
            plan = task_agent.decompose_goal(analysis)
            
            return {
                'status': 'success',
                'plan': {
                    'goal': data,
                    'tasks': plan.get('tasks', []),
                    'dependencies': plan.get('dependencies', []),
                    'estimated_duration': plan.get('estimated_duration', 'unknown')
                }
            }
            
        except ImportError as e:
            logger.warning(f"Planning agents not available: {e}")
        except Exception as e:
            logger.error(f"Planning error: {e}")
        
        # Fallback: Try direct LLM planning
        try:
            from llm_config import get_llm
            
            llm = get_llm()
            
            prompt = f"""You are the Adastrea Director, an AI assistant specialized in game development planning.

Break down the following goal into a list of actionable tasks for Unreal Engine development.

Goal: {data}

Respond in JSON format with this structure:
{{
    "tasks": [
        {{"id": 1, "name": "Task name", "description": "Brief description", "priority": "high/medium/low"}},
        ...
    ],
    "dependencies": [
        {{"from": 1, "to": 2}}
    ],
    "estimated_duration": "X hours/days"
}}

JSON Response:"""
            
            response = llm.invoke(prompt)
            result_text = response.content if hasattr(response, 'content') else str(response)
            
            # Try to parse as JSON
            try:
                json_str = self._extract_code_block_content(result_text)
                plan_data = json.loads(json_str.strip())
                return {
                    'status': 'success',
                    'plan': {
                        'goal': data,
                        'tasks': plan_data.get('tasks', []),
                        'dependencies': plan_data.get('dependencies', []),
                        'estimated_duration': plan_data.get('estimated_duration', 'unknown')
                    }
                }
            except json.JSONDecodeError:
                # Return raw response if JSON parsing fails
                return {
                    'status': 'success',
                    'plan': {
                        'goal': data,
                        'tasks': [{'id': 1, 'name': 'Generated Plan', 'description': result_text, 'priority': 'medium'}],
                        'dependencies': [],
                        'estimated_duration': 'unknown'
                    }
                }
                
        except Exception as e:
            logger.error(f"LLM planning error: {e}")
        
        # Final fallback
        return {
            'status': 'success',
            'plan': {
                'goal': data,
                'tasks': [],
                'dependencies': [],
                'note': 'Planning agents not available. Please configure an LLM API key.'
            }
        }

    def _handle_analyze(self, data: str) -> Dict[str, Any]:
        """
        Handle goal analysis request using the goal analysis agent.
        
        Attempts to use the goal analysis agent if available.
        """
        logger.info(f"Analyze request received: {data}")
        
        # Try to use actual goal analysis agent
        try:
            from goal_analysis_agent import GoalAnalysisAgent
            
            agent = GoalAnalysisAgent()
            analysis = agent.analyze_goal(data)
            
            return {
                'status': 'success',
                'analysis': {
                    'goal': data,
                    'goal_type': analysis.get('goal_type', 'unknown'),
                    'complexity': analysis.get('complexity', 'medium'),
                    'scope': analysis.get('scope', []),
                    'constraints': analysis.get('constraints', []),
                    'estimated_tasks': analysis.get('estimated_tasks', 0)
                }
            }
            
        except ImportError as e:
            logger.warning(f"Goal analysis agent not available: {e}")
        except Exception as e:
            logger.error(f"Goal analysis error: {e}")
        
        # Fallback: Try direct LLM analysis
        try:
            from llm_config import get_llm
            
            llm = get_llm()
            
            prompt = f"""You are the Adastrea Director, an AI assistant specialized in analyzing game development goals.

Analyze the following goal and provide a structured assessment for Unreal Engine development.

Goal: {data}

Respond in JSON format with this structure:
{{
    "goal_type": "feature/bugfix/optimization/refactor/documentation",
    "complexity": "low/medium/high",
    "scope": ["list", "of", "affected", "areas"],
    "constraints": ["list", "of", "potential", "constraints"],
    "estimated_tasks": <number>
}}

JSON Response:"""
            
            response = llm.invoke(prompt)
            result_text = response.content if hasattr(response, 'content') else str(response)
            
            # Try to parse as JSON
            try:
                json_str = self._extract_code_block_content(result_text)
                analysis_data = json.loads(json_str.strip())
                return {
                    'status': 'success',
                    'analysis': {
                        'goal': data,
                        'goal_type': analysis_data.get('goal_type', 'unknown'),
                        'complexity': analysis_data.get('complexity', 'medium'),
                        'scope': analysis_data.get('scope', []),
                        'constraints': analysis_data.get('constraints', []),
                        'estimated_tasks': analysis_data.get('estimated_tasks', 5)
                    }
                }
            except json.JSONDecodeError:
                # Return basic analysis if JSON parsing fails
                return {
                    'status': 'success',
                    'analysis': {
                        'goal': data,
                        'goal_type': 'feature',
                        'complexity': 'medium',
                        'scope': [],
                        'constraints': [],
                        'estimated_tasks': 5,
                        'raw_analysis': result_text
                    }
                }
                
        except Exception as e:
            logger.error(f"LLM analysis error: {e}")
        
        # Final fallback
        return {
            'status': 'success',
            'analysis': {
                'goal': data,
                'complexity': 'medium',
                'estimated_tasks': 5,
                'note': 'Analysis agent not available. Please configure an LLM API key.'
            }
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Adastrea Director IPC Server'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5555,
        help='Port to listen on (default: 5555)'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--enable-ue-python',
        action='store_true',
        help='Enable UE Python API integration (requires running in UE)'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Create and start server
    server = IPCServer(host=args.host, port=args.port)
    
    # Register UE Python API handlers if enabled
    if args.enable_ue_python:
        try:
            from ue_python_integration import register_ue_python_handlers
            register_ue_python_handlers(server)
            logger.info("UE Python API integration enabled")
        except ImportError as e:
            logger.warning(f"Could not enable UE Python API: {e}")
        except Exception as e:
            logger.error(f"Error enabling UE Python API: {e}")
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        server.stop()
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
