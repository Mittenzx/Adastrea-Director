#!/usr/bin/env python3
"""
IPC Server for Adastrea Director Plugin

This server provides socket-based IPC communication between the Unreal Engine
plugin (C++) and the Python backend (RAG system, planning agents, etc.).

Usage:
    python ipc_server.py --port 5555
"""

import socket
import json
import sys
import argparse
import logging
import threading
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AdastreaIPCServer')


class IPCServer:
    """IPC server for handling requests from the UE plugin."""

    def __init__(self, host: str = '127.0.0.1', port: int = 5555):
        """
        Initialize the IPC server.
        
        Args:
            host: Host address to bind to (default: localhost)
            port: Port to listen on
        """
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.handlers = {}
        
        # Register default handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default request handlers."""
        self.register_handler('ping', self._handle_ping)
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
        Process a request and return a response.
        
        Args:
            request: Request dictionary with 'type' and 'data' fields
            
        Returns:
            Response dictionary
        """
        request_type = request.get('type', '')
        request_data = request.get('data', '')
        
        if not request_type:
            return {
                'status': 'error',
                'error': 'Missing request type'
            }
        
        # Find and call appropriate handler
        handler = self.handlers.get(request_type)
        
        if handler:
            try:
                return handler(request_data)
            except Exception as e:
                logger.error(f"Handler error for '{request_type}': {e}")
                return {
                    'status': 'error',
                    'error': f"Handler error: {str(e)}"
                }
        else:
            return {
                'status': 'error',
                'error': f"Unknown request type: {request_type}"
            }

    # Default handlers

    def _handle_ping(self, data: str) -> Dict[str, Any]:
        """Handle ping request."""
        logger.debug("Ping received")
        return {
            'status': 'success',
            'message': 'pong'
        }

    def _handle_query(self, data: str) -> Dict[str, Any]:
        """
        Handle documentation query request.
        
        TODO: Integrate with actual RAG system
        """
        logger.info(f"Query received: {data}")
        
        # Placeholder response
        return {
            'status': 'success',
            'response': f"Query processed: {data}",
            'sources': []
        }

    def _handle_plan(self, data: str) -> Dict[str, Any]:
        """
        Handle planning request.
        
        TODO: Integrate with planning agents
        """
        logger.info(f"Plan request received: {data}")
        
        # Placeholder response
        return {
            'status': 'success',
            'plan': {
                'goal': data,
                'tasks': [],
                'dependencies': []
            }
        }

    def _handle_analyze(self, data: str) -> Dict[str, Any]:
        """
        Handle goal analysis request.
        
        TODO: Integrate with goal analysis agent
        """
        logger.info(f"Analyze request received: {data}")
        
        # Placeholder response
        return {
            'status': 'success',
            'analysis': {
                'goal': data,
                'complexity': 'medium',
                'estimated_tasks': 5
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
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Create and start server
    server = IPCServer(host=args.host, port=args.port)
    
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
