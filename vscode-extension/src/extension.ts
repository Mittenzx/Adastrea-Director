/**
 * Adastrea Director VS Code Extension
 * 
 * This extension provides integration with the Adastrea Director
 * AI-powered game development assistant for Unreal Engine.
 */

import * as vscode from 'vscode';
import { DirectorIPCClient, ConnectionState } from './ipcClient';

let client: DirectorIPCClient | null = null;
let statusBarItem: vscode.StatusBarItem;
let outputChannel: vscode.OutputChannel;
let debugOutputChannel: vscode.OutputChannel;

/**
 * Extension activation
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('Adastrea Director extension is now active');

    // Create output channels
    outputChannel = vscode.window.createOutputChannel('Adastrea Director');
    debugOutputChannel = vscode.window.createOutputChannel('Adastrea Director - Debug');
    
    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left,
        100
    );
    statusBarItem.command = 'director.checkStatus';
    context.subscriptions.push(statusBarItem);
    
    updateStatusBar('disconnected');
    statusBarItem.show();

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('director.connect', connectToDirector)
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('director.disconnect', disconnectFromDirector)
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('director.askQuestion', askQuestion)
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('director.checkStatus', checkStatus)
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('director.toggleDebugMode', toggleDebugMode)
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('director.runDiagnostics', runDiagnostics)
    );

    // Auto-connect if configured
    const config = vscode.workspace.getConfiguration('director');
    if (config.get('autoConnect')) {
        connectToDirector();
    }

    outputChannel.appendLine('Adastrea Director extension activated');
}

/**
 * Extension deactivation
 */
export function deactivate() {
    if (client) {
        client.disconnect();
        client = null;
    }
    
    if (statusBarItem) {
        statusBarItem.dispose();
    }
    
    if (outputChannel) {
        outputChannel.dispose();
    }
    
    if (debugOutputChannel) {
        debugOutputChannel.dispose();
    }
}

/**
 * Connect to Director IPC server
 */
async function connectToDirector() {
    if (client && client.isConnected()) {
        vscode.window.showInformationMessage('Already connected to Director');
        return;
    }

    const config = vscode.workspace.getConfiguration('director');
    const host = config.get<string>('ipc.host', 'localhost');
    const port = config.get<number>('ipc.port', 5555);
    const reconnectInterval = config.get<number>('reconnectInterval', 5000);
    const maxReconnectAttempts = config.get<number>('maxReconnectAttempts', 3);
    const requestTimeout = config.get<number>('requestTimeout', 30000);
    const debugMode = config.get<boolean>('debugMode', false);

    outputChannel.appendLine(`Connecting to Director IPC server at ${host}:${port}...`);
    if (debugMode) {
        debugOutputChannel.appendLine('='.repeat(60));
        debugOutputChannel.appendLine(`Connection attempt started at ${new Date().toISOString()}`);
        debugOutputChannel.appendLine(`Configuration: host=${host}, port=${port}`);
        debugOutputChannel.appendLine('='.repeat(60));
    }
    updateStatusBar('connecting');

    try {
        client = new DirectorIPCClient({
            host,
            port,
            reconnectInterval,
            maxReconnectAttempts,
            requestTimeout,
            debugMode
        });

        // Set up event handlers
        client.onStateChange = (state: ConnectionState) => {
            updateStatusBar(state);
            outputChannel.appendLine(`Connection state changed: ${state}`);
            if (debugMode) {
                debugOutputChannel.appendLine(`[${new Date().toISOString()}] State changed to: ${state}`);
            }
        };

        client.onError = (error: Error) => {
            outputChannel.appendLine(`Error: ${error.message}`);
            if (debugMode) {
                debugOutputChannel.appendLine(`[${new Date().toISOString()}] Error: ${error.message}`);
                if (error.stack) {
                    debugOutputChannel.appendLine(`Stack trace:\n${error.stack}`);
                }
            }
        };

        client.onDebugLog = (info) => {
            const levelSymbol = {
                'info': 'ℹ',
                'warning': '⚠',
                'error': '✗',
                'debug': '◆'
            }[info.level] || '•';
            
            debugOutputChannel.appendLine(`[${info.timestamp}] ${levelSymbol} ${info.level.toUpperCase()}: ${info.message}`);
            if (info.details) {
                debugOutputChannel.appendLine(`  Details: ${JSON.stringify(info.details, null, 2)}`);
            }
        };

        await client.connect();
        
        vscode.window.showInformationMessage('Connected to Adastrea Director');
        outputChannel.appendLine('Successfully connected to Director IPC server');

        // Perform initial health check
        const pongResult = await client.ping();
        if (pongResult) {
            outputChannel.appendLine('Health check passed (ping successful)');
        } else {
            outputChannel.appendLine('Warning: Health check failed (ping unsuccessful)');
        }

    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        vscode.window.showErrorMessage(`Failed to connect to Director: ${errorMessage}`);
        outputChannel.appendLine(`Connection failed: ${errorMessage}`);
        updateStatusBar('error');
        client = null;
    }
}

/**
 * Disconnect from Director IPC server
 */
function disconnectFromDirector() {
    if (!client) {
        vscode.window.showInformationMessage('Not connected to Director');
        return;
    }

    client.disconnect();
    client = null;
    
    vscode.window.showInformationMessage('Disconnected from Adastrea Director');
    outputChannel.appendLine('Disconnected from Director IPC server');
    updateStatusBar('disconnected');
}

/**
 * Ask a question to Director AI
 */
async function askQuestion() {
    if (!client || !client.isConnected()) {
        const shouldConnect = await vscode.window.showWarningMessage(
            'Not connected to Director. Would you like to connect?',
            'Connect',
            'Cancel'
        );
        
        if (shouldConnect === 'Connect') {
            await connectToDirector();
            
            // Check if connection succeeded
            if (!client || !client.isConnected()) {
                return;
            }
        } else {
            return;
        }
    }

    const question = await vscode.window.showInputBox({
        prompt: 'Ask a question to Adastrea Director',
        placeHolder: 'e.g., How do I create a player character in Unreal Engine?'
    });

    if (!question) {
        return;
    }

    outputChannel.appendLine(`\nQuestion: ${question}`);
    outputChannel.show(true);

    try {
        const config = vscode.workspace.getConfiguration('director');
        const requestTimeout = config.get<number>('requestTimeout', 30000);
        vscode.window.setStatusBarMessage('$(sync~spin) Querying Director...', requestTimeout);
        
        const response = await client!.query(question);
        
        if (response.status === 'success') {
            const result = response.result || 'No result returned';
            outputChannel.appendLine(`\nAnswer:\n${result}`);
            
            vscode.window.showInformationMessage('Query completed successfully');
        } else {
            const error = response.error || 'Unknown error';
            outputChannel.appendLine(`\nError: ${error}`);
            vscode.window.showErrorMessage(`Query failed: ${error}`);
        }
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        outputChannel.appendLine(`\nError: ${errorMessage}`);
        vscode.window.showErrorMessage(`Query failed: ${errorMessage}`);
    }
}

/**
 * Check connection status
 */
function checkStatus() {
    if (!client) {
        vscode.window.showInformationMessage('Not connected to Director');
        return;
    }

    const state = client.getState();
    const stateEmoji = {
        'disconnected': '⚫',
        'connecting': '🟡',
        'connected': '🟢',
        'error': '🔴'
    }[state] || '⚪';

    vscode.window.showInformationMessage(
        `Director Status: ${stateEmoji} ${state.toUpperCase()}`
    );
}

/**
 * Toggle debug mode
 */
async function toggleDebugMode() {
    const config = vscode.workspace.getConfiguration('director');
    const currentDebugMode = config.get<boolean>('debugMode', false);
    const newDebugMode = !currentDebugMode;

    await config.update('debugMode', newDebugMode, vscode.ConfigurationTarget.Global);

    if (client) {
        client.setDebugMode(newDebugMode);
    }

    const statusMessage = newDebugMode ? 'enabled' : 'disabled';
    vscode.window.showInformationMessage(`Director debug mode ${statusMessage}`);
    outputChannel.appendLine(`Debug mode ${statusMessage}`);

    if (newDebugMode) {
        debugOutputChannel.show(true);
        debugOutputChannel.appendLine('='.repeat(60));
        debugOutputChannel.appendLine(`Debug mode enabled at ${new Date().toISOString()}`);
        debugOutputChannel.appendLine('='.repeat(60));
    }
}

/**
 * Run connection diagnostics
 */
async function runDiagnostics() {
    outputChannel.appendLine('\n' + '='.repeat(60));
    outputChannel.appendLine('CONNECTION DIAGNOSTICS');
    outputChannel.appendLine('='.repeat(60));

    const config = vscode.workspace.getConfiguration('director');
    const host = config.get<string>('ipc.host', 'localhost');
    const port = config.get<number>('ipc.port', 5555);

    // System Information
    outputChannel.appendLine('\n1. System Information:');
    outputChannel.appendLine(`   Platform: ${process.platform}`);
    outputChannel.appendLine(`   Node Version: ${process.version}`);
    outputChannel.appendLine(`   VS Code Version: ${vscode.version}`);

    // Configuration
    outputChannel.appendLine('\n2. Extension Configuration:');
    outputChannel.appendLine(`   Host: ${host}`);
    outputChannel.appendLine(`   Port: ${port}`);
    outputChannel.appendLine(`   Reconnect Interval: ${config.get('reconnectInterval')}ms`);
    outputChannel.appendLine(`   Max Reconnect Attempts: ${config.get('maxReconnectAttempts')}`);
    outputChannel.appendLine(`   Request Timeout: ${config.get('requestTimeout')}ms`);
    outputChannel.appendLine(`   Debug Mode: ${config.get('debugMode')}`);
    outputChannel.appendLine(`   Auto Connect: ${config.get('autoConnect')}`);

    // Client State
    outputChannel.appendLine('\n3. Client State:');
    if (client) {
        const diagnostics = client.getDiagnostics();
        outputChannel.appendLine(`   Current State: ${diagnostics.state.currentState}`);
        outputChannel.appendLine(`   Is Connected: ${diagnostics.state.isConnected}`);
        outputChannel.appendLine(`   Reconnect Attempts: ${diagnostics.state.reconnectAttempts}`);
        outputChannel.appendLine(`   Pending Requests: ${diagnostics.state.pendingRequestsCount}`);
        outputChannel.appendLine(`   Has Socket: ${diagnostics.state.hasSocket}`);

        if (diagnostics.socket) {
            outputChannel.appendLine('\n4. Socket Information:');
            outputChannel.appendLine(`   Local Address: ${diagnostics.socket.localAddress || 'N/A'}`);
            outputChannel.appendLine(`   Local Port: ${diagnostics.socket.localPort || 'N/A'}`);
            outputChannel.appendLine(`   Remote Address: ${diagnostics.socket.remoteAddress || 'N/A'}`);
            outputChannel.appendLine(`   Remote Port: ${diagnostics.socket.remotePort || 'N/A'}`);
            outputChannel.appendLine(`   Ready State: ${diagnostics.socket.readyState}`);
            outputChannel.appendLine(`   Bytes Read: ${diagnostics.socket.bytesRead}`);
            outputChannel.appendLine(`   Bytes Written: ${diagnostics.socket.bytesWritten}`);
            outputChannel.appendLine(`   Destroyed: ${diagnostics.socket.destroyed}`);
        }
    } else {
        outputChannel.appendLine('   Client not initialized');
    }

    // Network Test
    outputChannel.appendLine('\n5. Network Connectivity:');
    outputChannel.appendLine(`   Testing connection to ${host}:${port}...`);

    try {
        const net = require('net');
        const testSocket = new net.Socket();
        
        const testResult = await new Promise<string>((resolve) => {
            const timeout = setTimeout(() => {
                testSocket.destroy();
                resolve(`   ✗ Connection timeout (server may not be running)`);
            }, 5000);

            testSocket.on('connect', () => {
                clearTimeout(timeout);
                testSocket.destroy();
                resolve(`   ✓ Port ${port} is reachable`);
            });

            testSocket.on('error', (error: any) => {
                clearTimeout(timeout);
                resolve(`   ✗ Connection failed: ${error.message} (code: ${error.code})`);
            });

            testSocket.connect(port, host);
        });

        outputChannel.appendLine(testResult);
    } catch (error) {
        outputChannel.appendLine(`   ✗ Error during connectivity test: ${error}`);
    }

    // Connection Test
    if (client && client.isConnected()) {
        outputChannel.appendLine('\n6. Health Check:');
        try {
            const pingStart = Date.now();
            const pingResult = await client.ping();
            const pingDuration = Date.now() - pingStart;
            
            if (pingResult) {
                outputChannel.appendLine(`   ✓ Ping successful (${pingDuration}ms)`);
            } else {
                outputChannel.appendLine(`   ✗ Ping failed`);
            }
        } catch (error) {
            outputChannel.appendLine(`   ✗ Ping error: ${error}`);
        }
    }

    // Recommendations
    outputChannel.appendLine('\n7. Troubleshooting Steps:');
    if (!client || !client.isConnected()) {
        outputChannel.appendLine('   → Start the IPC server:');
        outputChannel.appendLine('     python Plugins/AdastreaDirector/Python/ipc_server.py --port 5555');
        outputChannel.appendLine('   → Check if port 5555 is available');
        outputChannel.appendLine('   → Verify firewall settings');
        outputChannel.appendLine('   → Enable debug mode for detailed logs');
    } else {
        outputChannel.appendLine('   ✓ Connection appears healthy');
    }

    outputChannel.appendLine('\n' + '='.repeat(60));
    outputChannel.show(true);

    vscode.window.showInformationMessage('Diagnostics completed - check output panel');
}

/**
 * Update status bar item based on connection state
 */
function updateStatusBar(state: ConnectionState) {
    const stateConfig = {
        'disconnected': {
            text: '$(circle-slash) Director: Disconnected',
            tooltip: 'Click to check status',
            color: undefined
        },
        'connecting': {
            text: '$(sync~spin) Director: Connecting...',
            tooltip: 'Connecting to Director IPC server',
            color: new vscode.ThemeColor('statusBarItem.warningBackground')
        },
        'connected': {
            text: '$(check) Director: Connected',
            tooltip: 'Connected to Director IPC server',
            color: undefined
        },
        'error': {
            text: '$(error) Director: Error',
            tooltip: 'Connection error - click for details',
            color: new vscode.ThemeColor('statusBarItem.errorBackground')
        }
    }[state];

    if (stateConfig) {
        statusBarItem.text = stateConfig.text;
        statusBarItem.tooltip = stateConfig.tooltip;
        statusBarItem.backgroundColor = stateConfig.color;
    }
}
