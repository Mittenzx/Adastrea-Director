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

    constructor(config: ConnectionConfig) {
        this.config = {
            host: config.host,
            port: config.port,
            reconnectInterval: config.reconnectInterval ?? 5000,
            maxReconnectAttempts: config.maxReconnectAttempts ?? 3
        };
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
            return;
        }

        this.setState('connecting');

        return new Promise((resolve, reject) => {
            this.socket = new net.Socket();

            this.socket.on('connect', () => {
                this.setState('connected');
                this.reconnectAttempts = 0;
                this.clearReconnectTimer();
                resolve();
            });

            this.socket.on('data', (data) => {
                this.handleData(data);
            });

            this.socket.on('error', (error) => {
                this.handleError(error);
                if (this.state === 'connecting') {
                    reject(error);
                }
            });

            this.socket.on('close', () => {
                this.handleClose();
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
            throw new Error('Not connected to Director IPC server');
        }

        const requestObj: IPCRequest = { type, data };
        const requestStr = JSON.stringify(requestObj) + '\n';

        return new Promise((resolve, reject) => {
            const id = this.requestId++;
            this.pendingRequests.set(id, { resolve, reject });

            // Set timeout for request
            const timeout = setTimeout(() => {
                this.pendingRequests.delete(id);
                reject(new Error('Request timeout'));
            }, 30000); // 30 second timeout

            try {
                this.socket!.write(requestStr, (error) => {
                    if (error) {
                        clearTimeout(timeout);
                        this.pendingRequests.delete(id);
                        reject(error);
                    }
                });
            } catch (error) {
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
     */
    private handleResponse(response: IPCResponse): void {
        // For now, resolve the oldest pending request
        // In a production version, you might want request IDs in the protocol
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
        console.error('IPC Client error:', error);
        
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
            console.log('Max reconnection attempts reached');
            return;
        }

        this.reconnectAttempts++;
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})...`);

        this.reconnectTimer = setTimeout(() => {
            this.connect().catch((error) => {
                console.error('Reconnection failed:', error);
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
