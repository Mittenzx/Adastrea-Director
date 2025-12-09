/**
 * Test Executor Service
 * 
 * Handles automated test execution via UE Python API and displays results.
 * Part of Phase 2: Semi-Autonomous Development
 */

import * as vscode from 'vscode';
import { DirectorIPCClient, IPCResponse } from './ipcClient';

export interface TestResult {
    name: string;
    status: 'passed' | 'failed' | 'skipped';
    duration?: number;
    message?: string;
    stackTrace?: string;
    filePath?: string;
    lineNumber?: number;
}

export interface TestExecutionResult {
    success: boolean;
    totalTests: number;
    passed: number;
    failed: number;
    skipped: number;
    duration: number;
    tests: TestResult[];
}

export class TestExecutor {
    private testOutputChannel: vscode.OutputChannel;
    private lastTestResults: TestExecutionResult | null = null;

    constructor(
        private client: DirectorIPCClient,
        outputChannelName: string = 'Adastrea Director - Tests'
    ) {
        this.testOutputChannel = vscode.window.createOutputChannel(outputChannelName);
    }

    /**
     * Execute tests via the IPC server
     */
    public async executeTests(testType: string = 'all'): Promise<TestExecutionResult> {
        this.testOutputChannel.clear();
        this.testOutputChannel.appendLine('='.repeat(60));
        this.testOutputChannel.appendLine('Starting Test Execution');
        this.testOutputChannel.appendLine('='.repeat(60));
        this.testOutputChannel.appendLine(`Test Type: ${testType}`);
        this.testOutputChannel.appendLine(`Time: ${new Date().toISOString()}`);
        this.testOutputChannel.appendLine('');
        this.testOutputChannel.show(true);

        try {
            if (!this.client.isConnected()) {
                throw new Error('Not connected to Director IPC server');
            }

            // Send test execution request
            vscode.window.setStatusBarMessage('$(sync~spin) Running tests...', 60000);
            
            const response: IPCResponse = await this.client.request('run_tests', testType);

            if (response.status === 'error') {
                throw new Error(response.error || 'Test execution failed');
            }

            // Parse test results
            const result = this.parseTestResults(response);
            this.lastTestResults = result;

            // Display results
            this.displayTestResults(result);

            // Show summary notification
            if (result.failed === 0) {
                vscode.window.showInformationMessage(
                    `✓ All tests passed (${result.passed}/${result.totalTests})`
                );
            } else {
                vscode.window.showWarningMessage(
                    `✗ ${result.failed} test(s) failed (${result.passed}/${result.totalTests} passed)`
                );
            }

            return result;

        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : String(error);
            this.testOutputChannel.appendLine(`\n✗ Error: ${errorMsg}`);
            vscode.window.showErrorMessage(`Test execution failed: ${errorMsg}`);
            
            throw error;
        } finally {
            vscode.window.setStatusBarMessage('', 0);
        }
    }

    /**
     * Parse test results from IPC response
     */
    private parseTestResults(response: IPCResponse): TestExecutionResult {
        const passed = response.passed || 0;
        const failed = response.failed || 0;
        const output = response.result || '';

        // Parse individual test results from output
        const tests = this.parseTestOutput(output);

        return {
            success: failed === 0,
            totalTests: passed + failed,
            passed,
            failed,
            skipped: 0,
            duration: response.processing_time_ms || 0,
            tests
        };
    }

    /**
     * Parse individual test results from pytest output
     */
    private parseTestOutput(output: string): TestResult[] {
        const tests: TestResult[] = [];
        const lines = output.split('\n');

        // Simple parser for pytest output
        // Format: tests/test_file.py::test_name PASSED [XX%]
        const testLineRegex = /^(.*?)::(.*?)\s+(PASSED|FAILED|SKIPPED)/;
        
        for (const line of lines) {
            const match = line.match(testLineRegex);
            if (match) {
                const [, filePath, testName, status] = match;
                tests.push({
                    name: testName,
                    status: status.toLowerCase() as 'passed' | 'failed' | 'skipped',
                    filePath: filePath.trim()
                });
            }
        }

        return tests;
    }

    /**
     * Display test results in output channel
     */
    private displayTestResults(result: TestExecutionResult): void {
        this.testOutputChannel.appendLine('');
        this.testOutputChannel.appendLine('='.repeat(60));
        this.testOutputChannel.appendLine('Test Results Summary');
        this.testOutputChannel.appendLine('='.repeat(60));
        this.testOutputChannel.appendLine(`Total Tests: ${result.totalTests}`);
        this.testOutputChannel.appendLine(`✓ Passed:    ${result.passed}`);
        this.testOutputChannel.appendLine(`✗ Failed:    ${result.failed}`);
        this.testOutputChannel.appendLine(`⊘ Skipped:   ${result.skipped}`);
        this.testOutputChannel.appendLine(`Duration:    ${(result.duration / 1000).toFixed(2)}s`);
        this.testOutputChannel.appendLine('');

        // Display individual test results
        if (result.tests.length > 0) {
            this.testOutputChannel.appendLine('Individual Test Results:');
            this.testOutputChannel.appendLine('-'.repeat(60));
            
            for (const test of result.tests) {
                const statusIcon = test.status === 'passed' ? '✓' : 
                                  test.status === 'failed' ? '✗' : '⊘';
                this.testOutputChannel.appendLine(`${statusIcon} ${test.name}`);
                
                if (test.filePath) {
                    this.testOutputChannel.appendLine(`  File: ${test.filePath}`);
                }
                
                if (test.message) {
                    this.testOutputChannel.appendLine(`  Message: ${test.message}`);
                }
                
                if (test.stackTrace) {
                    this.testOutputChannel.appendLine(`  Stack:\n${test.stackTrace}`);
                }
                
                this.testOutputChannel.appendLine('');
            }
        }

        this.testOutputChannel.appendLine('='.repeat(60));
    }

    /**
     * Get last test results
     */
    public getLastTestResults(): TestExecutionResult | null {
        return this.lastTestResults;
    }

    /**
     * Navigate to test failure location
     */
    public async navigateToTestFailure(test: TestResult): Promise<void> {
        if (!test.filePath) {
            vscode.window.showWarningMessage('No file path available for this test');
            return;
        }

        try {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder open');
                return;
            }

            const uri = vscode.Uri.joinPath(workspaceFolder.uri, test.filePath);
            const document = await vscode.workspace.openTextDocument(uri);
            const editor = await vscode.window.showTextDocument(document);

            // Navigate to line if available
            if (test.lineNumber !== undefined) {
                const position = new vscode.Position(test.lineNumber - 1, 0);
                editor.selection = new vscode.Selection(position, position);
                editor.revealRange(new vscode.Range(position, position), vscode.TextEditorRevealType.InCenter);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to open test file: ${error}`);
        }
    }

    /**
     * Show test results panel
     */
    public showTestResults(): void {
        if (!this.lastTestResults) {
            vscode.window.showInformationMessage('No test results available. Run tests first.');
            return;
        }

        this.testOutputChannel.show(true);
    }

    /**
     * Create test results webview panel
     */
    public async showTestResultsWebview(): Promise<void> {
        if (!this.lastTestResults) {
            vscode.window.showInformationMessage('No test results available. Run tests first.');
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'testResults',
            'Test Results',
            vscode.ViewColumn.Two,
            {
                enableScripts: true
            }
        );

        panel.webview.html = this.getTestResultsHtml(this.lastTestResults);
    }

    /**
     * Generate HTML for test results webview
     */
    private getTestResultsHtml(result: TestExecutionResult): string {
        const testRows = result.tests.map(test => {
            const statusClass = test.status === 'passed' ? 'passed' : 
                               test.status === 'failed' ? 'failed' : 'skipped';
            const statusIcon = test.status === 'passed' ? '✓' : 
                              test.status === 'failed' ? '✗' : '⊘';
            
            return `
                <tr class="${statusClass}">
                    <td>${statusIcon} ${test.name}</td>
                    <td>${test.status.toUpperCase()}</td>
                    <td>${test.filePath || 'N/A'}</td>
                    <td>${test.duration !== undefined ? `${test.duration}ms` : 'N/A'}</td>
                </tr>
            `;
        }).join('');

        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Test Results</title>
                <style>
                    body {
                        font-family: var(--vscode-font-family);
                        color: var(--vscode-foreground);
                        background-color: var(--vscode-editor-background);
                        padding: 20px;
                    }
                    .summary {
                        margin-bottom: 20px;
                        padding: 15px;
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 4px;
                    }
                    .summary h2 {
                        margin-top: 0;
                    }
                    .stats {
                        display: flex;
                        gap: 20px;
                        margin: 10px 0;
                    }
                    .stat {
                        padding: 10px;
                        border-radius: 4px;
                    }
                    .stat.passed {
                        background-color: rgba(0, 255, 0, 0.1);
                    }
                    .stat.failed {
                        background-color: rgba(255, 0, 0, 0.1);
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }
                    th, td {
                        text-align: left;
                        padding: 10px;
                        border-bottom: 1px solid var(--vscode-panel-border);
                    }
                    th {
                        font-weight: bold;
                        background-color: var(--vscode-editor-background);
                    }
                    tr.passed td {
                        background-color: rgba(0, 255, 0, 0.05);
                    }
                    tr.failed td {
                        background-color: rgba(255, 0, 0, 0.05);
                    }
                    tr.skipped td {
                        background-color: rgba(128, 128, 128, 0.05);
                    }
                </style>
            </head>
            <body>
                <div class="summary">
                    <h2>Test Execution Summary</h2>
                    <div class="stats">
                        <div class="stat">
                            <strong>Total:</strong> ${result.totalTests}
                        </div>
                        <div class="stat passed">
                            <strong>Passed:</strong> ${result.passed}
                        </div>
                        <div class="stat failed">
                            <strong>Failed:</strong> ${result.failed}
                        </div>
                        <div class="stat">
                            <strong>Duration:</strong> ${(result.duration / 1000).toFixed(2)}s
                        </div>
                    </div>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Test Name</th>
                            <th>Status</th>
                            <th>File</th>
                            <th>Duration</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${testRows}
                    </tbody>
                </table>
            </body>
            </html>
        `;
    }

    /**
     * Dispose resources
     */
    public dispose(): void {
        this.testOutputChannel.dispose();
    }
}
