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

/**
 * Extension activation
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('Adastrea Director extension is now active');

    // Create output channel
    outputChannel = vscode.window.createOutputChannel('Adastrea Director');
    
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

    outputChannel.appendLine(`Connecting to Director IPC server at ${host}:${port}...`);
    updateStatusBar('connecting');

    try {
        client = new DirectorIPCClient({
            host,
            port,
            reconnectInterval,
            maxReconnectAttempts,
            requestTimeout
        });

        // Set up event handlers
        client.onStateChange = (state: ConnectionState) => {
            updateStatusBar(state);
            outputChannel.appendLine(`Connection state changed: ${state}`);
        };

        client.onError = (error: Error) => {
            outputChannel.appendLine(`Error: ${error.message}`);
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
