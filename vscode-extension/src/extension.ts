/**
 * Adastrea Director VS Code Extension
 * 
 * This extension provides integration with the Adastrea Director
 * AI-powered game development assistant for Unreal Engine.
 * 
 * Phase 2: Semi-Autonomous Development features included.
 */

import * as vscode from 'vscode';
import { DirectorIPCClient, ConnectionState } from './ipcClient';
import { CodeApplicator, CodeModification } from './codeApplicator';
import { TestExecutor } from './testExecutor';
import { FeedbackService } from './feedbackService';
import { initializeCopilotParticipant } from './copilotParticipant';
import { 
    registerContextProvider, 
    registerHoverProvider, 
    registerCodeActionProvider,
    DirectorEnhancedContext 
} from './copilotContextProvider';

let client: DirectorIPCClient | null = null;
let codeApplicator: CodeApplicator | null = null;
let testExecutor: TestExecutor | null = null;
let feedbackService: FeedbackService | null = null;
let copilotParticipant: vscode.ChatParticipant | null = null;
let enhancedContext: DirectorEnhancedContext | null = null;
let statusBarItem: vscode.StatusBarItem;
let outputChannel: vscode.OutputChannel;
let debugOutputChannel: vscode.OutputChannel;
let extensionContext: vscode.ExtensionContext;

/**
 * Extension activation
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('Adastrea Director extension is now active');

    // Store context globally
    extensionContext = context;

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

    // Initialize Phase 2 services (will be initialized after connection)
    codeApplicator = new CodeApplicator(outputChannel);
    
    // Register Phase 1 commands
    context.subscriptions.push(
        vscode.commands.registerCommand('director.connect', () => connectToDirector(context))
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

    // Register Phase 2 commands
    context.subscriptions.push(
        vscode.commands.registerCommand('director.generateAndApplyCode', generateAndApplyCode)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('director.runTests', runTests)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('director.reviewPendingChanges', reviewPendingChanges)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('director.viewApprovalHistory', viewApprovalHistory)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('director.showFeedbackStats', showFeedbackStats)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('director.setApprovalThreshold', setApprovalThreshold)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('director.provideFeedback', provideFeedback)
    );

    // Register Copilot integration commands
    context.subscriptions.push(
        vscode.commands.registerCommand('director.askAboutSelection', askAboutSelection)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('director.getContextForSelection', getContextForSelection)
    );

    // Initialize Copilot Chat participant
    const getClientFunc = () => client;
    const config = vscode.workspace.getConfiguration('director');
    
    // Only initialize Copilot features if enabled
    if (config.get('copilot.enabled', true)) {
        copilotParticipant = initializeCopilotParticipant(context, getClientFunc, outputChannel);
        
        // Register context providers
        registerContextProvider(context, getClientFunc, outputChannel);
        registerHoverProvider(context, getClientFunc, outputChannel);
        registerCodeActionProvider(context, getClientFunc, outputChannel);
        
        // Initialize enhanced context
        enhancedContext = new DirectorEnhancedContext(getClientFunc, outputChannel);
    } else {
        outputChannel.appendLine('ℹ️ Copilot integration disabled in settings');
    }

    // Auto-connect if configured
    if (config.get('autoConnect')) {
        connectToDirector(context);
    }

    outputChannel.appendLine('Adastrea Director extension activated');
    if (copilotParticipant) {
        outputChannel.appendLine('✓ GitHub Copilot integration enabled - use @director in chat');
    }
}

/**
 * Extension deactivation
 */
export function deactivate() {
    if (client) {
        client.disconnect();
        client = null;
    }
    
    if (testExecutor) {
        testExecutor.dispose();
        testExecutor = null;
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
async function connectToDirector(context?: vscode.ExtensionContext) {
    // Use provided context or global context
    const ctx = context || extensionContext;
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
        
        // Initialize Phase 2 services with connected client
        testExecutor = new TestExecutor(client);
        feedbackService = new FeedbackService(client, outputChannel, ctx);
        
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

/**
 * ============================================================
 * Phase 2: Semi-Autonomous Development Commands
 * ============================================================
 */

/**
 * Generate and apply code automatically
 */
async function generateAndApplyCode() {
    if (!client || !client.isConnected()) {
        vscode.window.showWarningMessage('Not connected to Director');
        return;
    }

    if (!codeApplicator) {
        vscode.window.showErrorMessage('Code applicator not initialized');
        return;
    }

    // Get the goal/task from user
    const goal = await vscode.window.showInputBox({
        prompt: 'What would you like to implement?',
        placeHolder: 'e.g., Add a new player health system'
    });

    if (!goal) {
        return;
    }

    outputChannel.appendLine(`\nGenerating code for: ${goal}`);
    outputChannel.show(true);

    try {
        vscode.window.setStatusBarMessage('$(sync~spin) Generating code...', 60000);

        // Request code generation from server
        const response = await client.request('generate_code', goal);

        if (response.status === 'error') {
            throw new Error(response.error || 'Code generation failed');
        }

        // Parse modifications from response
        const modifications: CodeModification[] = response.file_modifications || [];
        
        if (modifications.length === 0) {
            vscode.window.showInformationMessage('No code modifications generated');
            return;
        }

        outputChannel.appendLine(`Generated ${modifications.length} modification(s)`);

        // Queue modifications for review and application
        await codeApplicator.queueModifications(modifications);

        vscode.window.showInformationMessage(
            `Generated ${modifications.length} code modification(s)`
        );

    } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        outputChannel.appendLine(`\n✗ Error: ${errorMsg}`);
        vscode.window.showErrorMessage(`Code generation failed: ${errorMsg}`);
    } finally {
        vscode.window.setStatusBarMessage('', 0);
    }
}

/**
 * Run tests via UE Python API
 */
async function runTests() {
    if (!client || !client.isConnected()) {
        vscode.window.showWarningMessage('Not connected to Director');
        return;
    }

    if (!testExecutor) {
        vscode.window.showErrorMessage('Test executor not initialized');
        return;
    }

    // Ask which tests to run
    const testType = await vscode.window.showQuickPick(
        [
            { label: 'All Tests', value: 'all' },
            { label: 'IPC Tests', value: 'ipc' },
            { label: 'Plugin Tests', value: 'plugin' },
            { label: 'Unit Tests', value: 'unit' },
            { label: 'Integration Tests', value: 'integration' },
            { label: 'Remote Control Tests', value: 'remote' }
        ],
        {
            placeHolder: 'Select test suite to run',
            title: 'Run Tests'
        }
    );

    if (!testType) {
        return;
    }

    try {
        const result = await testExecutor.executeTests(testType.value);
        
        // Ask for feedback if there are failures
        if (result.failed > 0 && feedbackService) {
            const provideFeedback = await vscode.window.showQuickPick(
                ['Yes', 'No'],
                {
                    placeHolder: 'Would you like to provide feedback on the test failures?',
                    title: 'Provide Feedback'
                }
            );

            if (provideFeedback === 'Yes') {
                await feedbackService.requestUserFeedback('Test Execution', testType.value);
            }
        }

    } catch (error) {
        // Error already handled by testExecutor
    }
}

/**
 * Review pending code changes
 */
async function reviewPendingChanges() {
    if (!codeApplicator) {
        vscode.window.showErrorMessage('Code applicator not initialized');
        return;
    }

    const pending = codeApplicator.getPendingModifications();

    if (pending.length === 0) {
        vscode.window.showInformationMessage('No pending changes to review');
        return;
    }

    // Show list of pending modifications
    const items = pending.map((mod, index) => ({
        label: `${mod.modificationType.toUpperCase()}: ${mod.filePath}`,
        description: mod.description,
        detail: `Confidence: ${mod.confidence ? (mod.confidence * 100).toFixed(1) : 'N/A'}%`,
        modification: mod,
        index
    }));

    const selected = await vscode.window.showQuickPick(items, {
        placeHolder: `${pending.length} pending modification(s)`,
        title: 'Review Pending Changes',
        canPickMany: false
    });

    if (selected) {
        // Show options for this modification
        const action = await vscode.window.showQuickPick(
            [
                { label: '✓ Approve', value: 'approve' },
                { label: '✗ Reject', value: 'reject' },
                { label: '👁 Preview', value: 'preview' },
                { label: '🗑 Clear All', value: 'clear' }
            ],
            {
                placeHolder: selected.label,
                title: 'Choose Action'
            }
        );

        if (action) {
            switch (action.value) {
                case 'approve':
                    await codeApplicator.applyModifications([selected.modification]);
                    break;
                case 'reject':
                    // Remove only this modification from queue
                    const pending = codeApplicator.getPendingModifications();
                    const filtered = pending.filter(m => m !== selected.modification);
                    codeApplicator.clearPendingModifications();
                    if (filtered.length > 0) {
                        await codeApplicator.queueModifications(filtered);
                    }
                    vscode.window.showInformationMessage('Change rejected');
                    break;
                case 'preview':
                    // Preview will be handled by the applicator
                    break;
                case 'clear':
                    codeApplicator.clearPendingModifications();
                    vscode.window.showInformationMessage('Cleared all pending changes');
                    break;
            }
        }
    }
}

/**
 * View approval history
 */
async function viewApprovalHistory() {
    if (!codeApplicator) {
        vscode.window.showErrorMessage('Code applicator not initialized');
        return;
    }

    const stats = codeApplicator.getApprovalStats();
    const history = codeApplicator.getApprovalHistory();

    if (history.length === 0) {
        vscode.window.showInformationMessage('No approval history available');
        return;
    }

    const message = `
Approval Statistics:
- Total Decisions: ${stats.total}
- Approved: ${stats.approved}
- Rejected: ${stats.rejected}
- Auto-Approved: ${stats.autoApproved}
- Approval Rate: ${(stats.approvalRate * 100).toFixed(1)}%
    `.trim();

    const action = await vscode.window.showInformationMessage(
        message,
        'View Details',
        'Clear History'
    );

    if (action === 'View Details') {
        outputChannel.clear();
        outputChannel.appendLine('='.repeat(60));
        outputChannel.appendLine('Approval History');
        outputChannel.appendLine('='.repeat(60));
        outputChannel.appendLine('');

        for (const decision of history.slice(-20)) {  // Show last 20
            const status = decision.approved ? '✓ Approved' : '✗ Rejected';
            outputChannel.appendLine(`${status} - ${decision.modification.filePath}`);
            outputChannel.appendLine(`  Time: ${decision.timestamp.toISOString()}`);
            if (decision.reason) {
                outputChannel.appendLine(`  Reason: ${decision.reason}`);
            }
            outputChannel.appendLine('');
        }

        outputChannel.show(true);
    } else if (action === 'Clear History') {
        codeApplicator.clearApprovalHistory();
    }
}

/**
 * Show feedback statistics
 */
async function showFeedbackStats() {
    if (!feedbackService) {
        vscode.window.showErrorMessage('Feedback service not initialized');
        return;
    }

    await feedbackService.showFeedbackStats();
}

/**
 * Set auto-approval threshold
 */
async function setApprovalThreshold() {
    if (!codeApplicator) {
        vscode.window.showErrorMessage('Code applicator not initialized');
        return;
    }

    const currentThreshold = codeApplicator.getAutoApprovalThreshold();
    
    const input = await vscode.window.showInputBox({
        prompt: 'Set auto-approval confidence threshold (0.0 - 1.0)',
        value: currentThreshold.toString(),
        placeHolder: '0.9',
        validateInput: (value) => {
            const num = parseFloat(value);
            if (isNaN(num) || num < 0 || num > 1) {
                return 'Please enter a number between 0.0 and 1.0';
            }
            return null;
        }
    });

    if (input) {
        const threshold = parseFloat(input);
        codeApplicator.setAutoApprovalThreshold(threshold);
        
        // Save to settings
        const config = vscode.workspace.getConfiguration('director');
        await config.update('autoApprovalThreshold', threshold, vscode.ConfigurationTarget.Global);
        
        vscode.window.showInformationMessage(
            `Auto-approval threshold set to ${(threshold * 100).toFixed(0)}%`
        );
    }
}

/**
 * Provide feedback on a suggestion
 */
async function provideFeedback() {
    if (!feedbackService) {
        vscode.window.showErrorMessage('Feedback service not initialized');
        return;
    }

    const goal = await vscode.window.showInputBox({
        prompt: 'What was the goal/task?',
        placeHolder: 'e.g., Implement player health system'
    });

    if (!goal) {
        return;
    }

    await feedbackService.requestUserFeedback(goal, 'Manual Feedback');
}

/**
 * ============================================================
 * Copilot Integration Commands
 * ============================================================
 */

/**
 * Ask Director about selected code
 */
async function askAboutSelection(document: vscode.TextDocument, range: vscode.Range) {
    if (!client || !client.isConnected()) {
        vscode.window.showWarningMessage('Not connected to Director');
        return;
    }

    const selectedText = document.getText(range);
    if (!selectedText) {
        vscode.window.showInformationMessage('No code selected');
        return;
    }

    const question = await vscode.window.showInputBox({
        prompt: 'What would you like to know about this code?',
        placeHolder: 'e.g., What does this function do? How can I improve it?'
    });

    if (!question) {
        return;
    }

    outputChannel.appendLine(`\nAsking about selected code: ${question}`);
    outputChannel.show(true);

    try {
        const query = `
Question: ${question}

Code context:
File: ${document.fileName}
Language: ${document.languageId}

\`\`\`${document.languageId}
${selectedText}
\`\`\`
`;

        const response = await client.query(query);
        
        if (response.status === 'success' && response.result) {
            outputChannel.appendLine(`\nAnswer:\n${response.result}`);
            vscode.window.showInformationMessage('See answer in Output panel');
        } else {
            const error = response.error || 'Unknown error';
            outputChannel.appendLine(`\nError: ${error}`);
            vscode.window.showErrorMessage(`Query failed: ${error}`);
        }
    } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        outputChannel.appendLine(`\nError: ${errorMsg}`);
        vscode.window.showErrorMessage(`Query failed: ${errorMsg}`);
    }
}

/**
 * Get Director context for selected code
 */
async function getContextForSelection(document: vscode.TextDocument, range: vscode.Range) {
    if (!client || !client.isConnected()) {
        vscode.window.showWarningMessage('Not connected to Director');
        return;
    }

    if (!enhancedContext) {
        vscode.window.showErrorMessage('Enhanced context not initialized');
        return;
    }

    const selectedText = document.getText(range);
    if (!selectedText) {
        vscode.window.showInformationMessage('No code selected');
        return;
    }

    outputChannel.appendLine(`\nGetting context for selected code...`);
    outputChannel.show(true);

    try {
        const query = `
Provide relevant context and documentation for this code:

File: ${document.fileName}
Language: ${document.languageId}

\`\`\`${document.languageId}
${selectedText}
\`\`\`

Include:
- API documentation
- Usage examples
- Best practices
- Common pitfalls
`;

        const response = await client.query(query);
        
        if (response.status === 'success' && response.result) {
            outputChannel.appendLine(`\nContext:\n${response.result}`);
            
            // Also show in a webview for better formatting
            const panel = vscode.window.createWebviewPanel(
                'directorContext',
                'Director Context',
                vscode.ViewColumn.Beside,
                { enableScripts: true }
            );

            panel.webview.html = getContextWebviewContent(response.result, selectedText);
        } else {
            const error = response.error || 'Unknown error';
            outputChannel.appendLine(`\nError: ${error}`);
            vscode.window.showErrorMessage(`Failed to get context: ${error}`);
        }
    } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        outputChannel.appendLine(`\nError: ${errorMsg}`);
        vscode.window.showErrorMessage(`Failed to get context: ${errorMsg}`);
    }
}

/**
 * Generate HTML content for context webview
 */
function getContextWebviewContent(context: string, code: string): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline';">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Director Context</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            padding: 20px;
            line-height: 1.6;
        }
        h1, h2, h3 {
            color: var(--vscode-textLink-foreground);
        }
        pre {
            background-color: var(--vscode-textCodeBlock-background);
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
        code {
            font-family: var(--vscode-editor-font-family);
            background-color: var(--vscode-textCodeBlock-background);
            padding: 2px 4px;
            border-radius: 3px;
        }
        .code-block {
            margin: 20px 0;
        }
        .context-section {
            margin: 20px 0;
            padding: 15px;
            background-color: var(--vscode-editorWidget-background);
            border-left: 4px solid var(--vscode-textLink-foreground);
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>🤖 Director Context</h1>
    
    <div class="code-block">
        <h2>Your Code</h2>
        <pre><code>${escapeHtml(code)}</code></pre>
    </div>

    <div class="context-section">
        <h2>Context & Documentation</h2>
        ${markdownToHtml(context)}
    </div>
</body>
</html>`;
}

/**
 * Escape HTML to prevent XSS attacks
 * Handles all common HTML special characters
 */
function escapeHtml(text: string): string {
    const escapeMap: { [key: string]: string } = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;',
        '`': '&#x60;',
        '=': '&#x3D;'
    };
    return text.replace(/[&<>"'`=/]/g, char => escapeMap[char]);
}

/**
 * Simple markdown to HTML conversion
 * Note: This is a basic implementation for simple formatting.
 * For production use, consider using a dedicated markdown library like 'marked' or 'markdown-it'.
 */
function markdownToHtml(markdown: string): string {
    // Escape HTML first to prevent XSS
    let html = escapeHtml(markdown);
    
    // Apply markdown formatting (in order of specificity)
    html = html
        // Headers (must be done before other patterns)
        .replace(/^### (.*)$/gm, '<h3>$1</h3>')
        .replace(/^## (.*)$/gm, '<h2>$1</h2>')
        .replace(/^# (.*)$/gm, '<h1>$1</h1>')
        // Bold (must be before italic)
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Italic
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Inline code
        .replace(/`(.*?)`/g, '<code>$1</code>')
        // Line breaks
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
    
    return html;
}
