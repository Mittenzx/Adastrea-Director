/**
 * IPC Client for Adastrea Director
 * 
 * This client communicates with the Director IPC server (Python backend)
 * running on port 5555 using TCP sockets with JSON protocol.
 * 
 * Protocol:
 * - Request: JSON object with 'type' and 'data' fields, terminated with newline
 * - Response: JSON object with 'status' field, terminated with newline
 */

import * as net from 'net';

export interface IPCRequest {
    type: string;
    data: string;
}

export interface IPCResponse {
    status: 'success' | 'error';
    message?: string;
    error?: string;
    result?: string;
    plan?: any;
    analysis?: any;
    [key: string]: any;
}

export interface ConnectionConfig {
    host: string;
    port: number;
    reconnectInterval?: number;
    maxReconnectAttempts?: number;
    requestTimeout?: number;  // Request timeout in milliseconds (default: 30000)
    debugMode?: boolean;  // Enable debug logging (default: false)
}

export interface DebugInfo {
    timestamp: string;
    level: 'info' | 'warning' | 'error' | 'debug';
    message: string;
    details?: any;
}

export interface DiagnosticsInfo {
    timestamp: string;
    config: {
        host: string;
        port: number;
        reconnectInterval: number;
        maxReconnectAttempts: number;
        requestTimeout: number;
        debugMode: boolean;
    };
    state: {
        currentState: ConnectionState;
        isConnected: boolean;
        reconnectAttempts: number;
        pendingRequestsCount: number;
        hasSocket: boolean;
    };
    socket?: {
        localAddress?: string;
        localPort?: number;
        remoteAddress?: string;
        remotePort?: number;
        readyState: string;
        bytesRead: number;
        bytesWritten: number;
        pending: boolean;
        destroyed: boolean;
    };
}

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

export class DirectorIPCClient {
    private socket: net.Socket | null = null;
    private config: Required<ConnectionConfig>;
    private state: ConnectionState = 'disconnected';
    private reconnectAttempts = 0;
    private reconnectTimer: NodeJS.Timeout | null = null;
    private pendingRequests: Map<number, {
        resolve: (response: IPCResponse) => void;
        reject: (error: Error) => void;
    }> = new Map();
    private requestId = 0;
    private buffer = '';

    // Event handlers
    public onStateChange: ((state: ConnectionState) => void) | null = null;
    public onError: ((error: Error) => void) | null = null;
    public onDebugLog: ((info: DebugInfo) => void) | null = null;

    constructor(config: ConnectionConfig) {
        this.config = {
            host: config.host,
            port: config.port,
            reconnectInterval: config.reconnectInterval ?? 5000,
            maxReconnectAttempts: config.maxReconnectAttempts ?? 3,
            requestTimeout: config.requestTimeout ?? 30000,
            debugMode: config.debugMode ?? false
        };
    }

    /**
     * Enable or disable debug mode
     */
    public setDebugMode(enabled: boolean): void {
        this.config.debugMode = enabled;
        this.debugLog('info', `Debug mode ${enabled ? 'enabled' : 'disabled'}`);
    }

    /**
     * Get debug mode status
     */
    public isDebugMode(): boolean {
        return this.config.debugMode;
    }

    /**
     * Log debug information
     */
    private debugLog(level: 'info' | 'warning' | 'error' | 'debug', message: string, details?: any): void {
        if (this.config.debugMode && this.onDebugLog) {
            this.onDebugLog({
                timestamp: new Date().toISOString(),
                level,
                message,
                details
            });
        }
    }

    /**
     * Get current connection state
     */
    public getState(): ConnectionState {
        return this.state;
    }

    /**
     * Check if client is connected
     */
    public isConnected(): boolean {
        return this.state === 'connected' && this.socket !== null;
    }

    /**
     * Connect to the Director IPC server
     */
    public async connect(): Promise<void> {
        if (this.state === 'connected' || this.state === 'connecting') {
            this.debugLog('warning', 'Connect called but already connected or connecting', {
                currentState: this.state
            });
            return;
        }

        this.debugLog('info', 'Starting connection attempt', {
            host: this.config.host,
            port: this.config.port,
            reconnectInterval: this.config.reconnectInterval,
            maxReconnectAttempts: this.config.maxReconnectAttempts,
            requestTimeout: this.config.requestTimeout
        });

        this.setState('connecting');

        return new Promise((resolve, reject) => {
            this.socket = new net.Socket();

            // Set socket options for better debugging
            this.socket.setKeepAlive(true, 5000);
            this.socket.setTimeout(this.config.requestTimeout);

            this.socket.on('connect', () => {
                this.debugLog('info', 'Socket connected successfully', {
                    localAddress: this.socket?.localAddress,
                    localPort: this.socket?.localPort,
                    remoteAddress: this.socket?.remoteAddress,
                    remotePort: this.socket?.remotePort
                });
                this.setState('connected');
                this.reconnectAttempts = 0;
                this.clearReconnectTimer();
                resolve();
            });

            this.socket.on('data', (data) => {
                this.debugLog('debug', 'Received data from server', {
                    length: data.length,
                    preview: data.toString('utf-8').substring(0, 100)
                });
                this.handleData(data);
            });

            this.socket.on('error', (error) => {
                this.debugLog('error', 'Socket error occurred', {
                    errorCode: (error as any).code,
                    errorMessage: error.message,
                    errorStack: error.stack
                });
                this.handleError(error);
                if (this.state === 'connecting') {
                    reject(error);
                }
            });

            this.socket.on('close', () => {
                this.debugLog('info', 'Socket closed');
                this.handleClose();
            });

            this.socket.on('timeout', () => {
                this.debugLog('warning', 'Socket timeout occurred');
            });

            this.debugLog('debug', 'Attempting to connect socket', {
                host: this.config.host,
                port: this.config.port
            });

            this.socket.connect(this.config.port, this.config.host);
        });
    }

    /**
     * Disconnect from the Director IPC server
     */
    public disconnect(): void {
        this.clearReconnectTimer();
        
        if (this.socket) {
            this.socket.destroy();
            this.socket = null;
        }

        // Reject all pending requests
        this.pendingRequests.forEach((request) => {
            request.reject(new Error('Connection closed'));
        });
        this.pendingRequests.clear();

        this.setState('disconnected');
    }

    /**
     * Send a request to the Director IPC server
     */
    public async request(type: string, data: string = ''): Promise<IPCResponse> {
        if (!this.isConnected()) {
            this.debugLog('error', 'Request attempted while not connected', {
                type,
                currentState: this.state
            });
            throw new Error('Not connected to Director IPC server');
        }

        const requestObj: IPCRequest = { type, data };
        const requestStr = JSON.stringify(requestObj) + '\n';

        this.debugLog('debug', 'Sending request', {
            type,
            dataLength: data.length,
            requestId: this.requestId,
            pendingRequestsCount: this.pendingRequests.size
        });

        return new Promise((resolve, reject) => {
            const id = this.requestId++;
            this.pendingRequests.set(id, { resolve, reject });

            // Set timeout for request
            const timeout = setTimeout(() => {
                this.debugLog('warning', 'Request timeout', {
                    type,
                    requestId: id,
                    timeout: this.config.requestTimeout
                });
                this.pendingRequests.delete(id);
                reject(new Error('Request timeout'));
            }, this.config.requestTimeout);

            try {
                this.socket!.write(requestStr, (error) => {
                    if (error) {
                        this.debugLog('error', 'Failed to write request', {
                            type,
                            requestId: id,
                            error: error.message
                        });
                        clearTimeout(timeout);
                        this.pendingRequests.delete(id);
                        reject(error);
                    } else {
                        this.debugLog('debug', 'Request sent successfully', {
                            type,
                            requestId: id
                        });
                    }
                });
            } catch (error) {
                this.debugLog('error', 'Exception while sending request', {
                    type,
                    requestId: id,
                    error: error instanceof Error ? error.message : String(error)
                });
                clearTimeout(timeout);
                this.pendingRequests.delete(id);
                reject(error);
            }
        });
    }

    /**
     * Send a ping to check server health
     */
    public async ping(): Promise<boolean> {
        try {
            const response = await this.request('ping', '');
            return response.status === 'success' && response.message === 'pong';
        } catch (error) {
            return false;
        }
    }

    /**
     * Query the Director AI
     */
    public async query(question: string): Promise<IPCResponse> {
        return this.request('query', question);
    }

    /**
     * Generate a plan for a goal
     */
    public async plan(goal: string): Promise<IPCResponse> {
        return this.request('plan', goal);
    }

    /**
     * Analyze a goal
     */
    public async analyze(goal: string): Promise<IPCResponse> {
        return this.request('analyze', goal);
    }

    /**
     * Get performance metrics
     */
    public async getMetrics(): Promise<IPCResponse> {
        return this.request('metrics', '');
    }

    /**
     * Get diagnostic information about the connection
     */
    public getDiagnostics(): DiagnosticsInfo {
        const diagnostics: DiagnosticsInfo = {
            timestamp: new Date().toISOString(),
            config: {
                host: this.config.host,
                port: this.config.port,
                reconnectInterval: this.config.reconnectInterval,
                maxReconnectAttempts: this.config.maxReconnectAttempts,
                requestTimeout: this.config.requestTimeout,
                debugMode: this.config.debugMode
            },
            state: {
                currentState: this.state,
                isConnected: this.isConnected(),
                reconnectAttempts: this.reconnectAttempts,
                pendingRequestsCount: this.pendingRequests.size,
                hasSocket: this.socket !== null
            }
        };

        if (this.socket) {
            diagnostics.socket = {
                localAddress: this.socket.localAddress,
                localPort: this.socket.localPort,
                remoteAddress: this.socket.remoteAddress,
                remotePort: this.socket.remotePort,
                readyState: this.socket.readyState,
                bytesRead: this.socket.bytesRead,
                bytesWritten: this.socket.bytesWritten,
                pending: this.socket.pending,
                destroyed: this.socket.destroyed
            };
        }

        return diagnostics;
    }

    /**
     * Handle incoming data from socket
     */
    private handleData(data: Buffer): void {
        this.buffer += data.toString('utf-8');

        // Process complete messages (terminated with newline)
        let newlineIndex: number;
        while ((newlineIndex = this.buffer.indexOf('\n')) !== -1) {
            const message = this.buffer.substring(0, newlineIndex).trim();
            this.buffer = this.buffer.substring(newlineIndex + 1);

            if (message) {
                try {
                    const response: IPCResponse = JSON.parse(message);
                    this.handleResponse(response);
                } catch (error) {
                    console.error('Failed to parse response:', error);
                }
            }
        }
    }

    /**
     * Handle a parsed response
     * 
     * IMPORTANT LIMITATION: This implementation assumes FIFO (First-In-First-Out) order
     * for request-response correlation. The IPC protocol does not include request IDs,
     * so responses are matched to the oldest pending request. This means:
     * - Requests are processed sequentially
     * - Out-of-order responses could cause incorrect correlation
     * - Multiple concurrent requests should be avoided
     * 
     * Future improvement: Add request ID field to the IPC protocol
     */
    private handleResponse(response: IPCResponse): void {
        const firstRequest = this.pendingRequests.entries().next();
        if (!firstRequest.done) {
            const [id, request] = firstRequest.value;
            this.pendingRequests.delete(id);
            request.resolve(response);
        }
    }

    /**
     * Handle socket errors
     */
    private handleError(error: Error): void {
        // Notify error handler (typically logs to output channel)
        if (this.onError) {
            this.onError(error);
        }

        this.setState('error');
    }

    /**
     * Handle socket close
     */
    private handleClose(): void {
        this.socket = null;

        if (this.state !== 'disconnected') {
            this.setState('disconnected');
            this.attemptReconnect();
        }
    }

    /**
     * Attempt to reconnect to the server
     */
    private attemptReconnect(): void {
        if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
            // Max attempts reached - notify via error handler
            if (this.onError) {
                this.onError(new Error('Max reconnection attempts reached'));
            }
            return;
        }

        this.reconnectAttempts++;
        
        // Notify via error handler for logging
        if (this.onError) {
            this.onError(new Error(`Attempting to reconnect (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})...`));
        }

        this.reconnectTimer = setTimeout(() => {
            this.connect().catch((error) => {
                if (this.onError) {
                    this.onError(new Error(`Reconnection failed: ${error.message}`));
                }
            });
        }, this.config.reconnectInterval);
    }

    /**
     * Clear reconnection timer
     */
    private clearReconnectTimer(): void {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    }

    /**
     * Set connection state and notify listeners
     */
    private setState(newState: ConnectionState): void {
        if (this.state !== newState) {
            this.state = newState;
            
            if (this.onStateChange) {
                this.onStateChange(newState);
            }
        }
    }
}
