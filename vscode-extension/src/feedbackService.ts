/**
 * Feedback Service
 * 
 * Handles collection and transmission of user feedback for continuous learning.
 * Part of Phase 2: Semi-Autonomous Development
 */

import * as vscode from 'vscode';
import { DirectorIPCClient, IPCResponse } from './ipcClient';
import { ApprovalDecision } from './codeApplicator';

export interface FeedbackItem {
    id: string;
    type: 'approval' | 'rejection' | 'modification' | 'rating';
    timestamp: Date;
    context: {
        goal?: string;
        task?: string;
        modificationType?: string;
        filePath?: string;
    };
    feedback: {
        approved?: boolean;
        reason?: string;
        rating?: number; // 1-5
        suggestions?: string;
    };
    metadata?: {
        confidence?: number;
        autoApproved?: boolean;
        timeToDecision?: number; // ms
    };
}

export interface FeedbackStats {
    totalFeedback: number;
    approvalRate: number;
    averageRating: number;
    commonReasons: { reason: string; count: number }[];
    preferredPatterns: string[];
}

export class FeedbackService {
    private feedbackHistory: FeedbackItem[] = [];
    private feedbackId = 0;
    
    constructor(
        private client: DirectorIPCClient,
        private outputChannel: vscode.OutputChannel,
        private context: vscode.ExtensionContext
    ) {
        // Load feedback history from workspace state
        this.loadFeedbackHistory();
    }

    /**
     * Record approval/rejection feedback
     */
    public async recordApprovalFeedback(decision: ApprovalDecision): Promise<void> {
        const feedback: FeedbackItem = {
            id: this.generateFeedbackId(),
            type: decision.approved ? 'approval' : 'rejection',
            timestamp: decision.timestamp,
            context: {
                modificationType: decision.modification.modificationType,
                filePath: decision.modification.filePath
            },
            feedback: {
                approved: decision.approved,
                reason: decision.reason
            },
            metadata: {
                confidence: decision.modification.confidence,
                autoApproved: decision.autoApproved
            }
        };

        await this.storeFeedback(feedback);
    }

    /**
     * Record user rating feedback
     */
    public async recordRatingFeedback(
        rating: number,
        context: { goal?: string; task?: string },
        suggestions?: string
    ): Promise<void> {
        const feedback: FeedbackItem = {
            id: this.generateFeedbackId(),
            type: 'rating',
            timestamp: new Date(),
            context,
            feedback: {
                rating,
                suggestions
            }
        };

        await this.storeFeedback(feedback);
    }

    /**
     * Store feedback item
     */
    private async storeFeedback(feedback: FeedbackItem): Promise<void> {
        this.feedbackHistory.push(feedback);
        
        // Save to workspace state
        await this.saveFeedbackHistory();
        
        // Send to server for learning
        await this.sendFeedbackToServer(feedback);
        
        this.outputChannel.appendLine(
            `Recorded feedback: ${feedback.type} (ID: ${feedback.id})`
        );
    }

    /**
     * Send feedback to IPC server for learning
     */
    private async sendFeedbackToServer(feedback: FeedbackItem): Promise<void> {
        try {
            if (!this.client.isConnected()) {
                this.outputChannel.appendLine('Warning: Not connected, feedback will be sent later');
                return;
            }

            const response: IPCResponse = await this.client.request(
                'apply_feedback',
                JSON.stringify(feedback)
            );

            if (response.status === 'success') {
                this.outputChannel.appendLine(`Feedback sent to server: ${feedback.id}`);
            } else {
                this.outputChannel.appendLine(
                    `Failed to send feedback: ${response.error || 'Unknown error'}`
                );
            }
        } catch (error) {
            this.outputChannel.appendLine(
                `Error sending feedback: ${error instanceof Error ? error.message : String(error)}`
            );
        }
    }

    /**
     * Get feedback statistics
     */
    public getFeedbackStats(): FeedbackStats {
        const total = this.feedbackHistory.length;
        
        // Calculate approval rate
        const approvalFeedback = this.feedbackHistory.filter(
            f => f.type === 'approval' || f.type === 'rejection'
        );
        const approved = approvalFeedback.filter(f => f.feedback.approved).length;
        const approvalRate = approvalFeedback.length > 0 ? approved / approvalFeedback.length : 0;

        // Calculate average rating
        const ratings = this.feedbackHistory
            .filter(f => f.feedback.rating !== undefined)
            .map(f => f.feedback.rating!);
        const averageRating = ratings.length > 0
            ? ratings.reduce((a, b) => a + b, 0) / ratings.length
            : 0;

        // Find common rejection reasons
        const reasons = this.feedbackHistory
            .filter(f => !f.feedback.approved && f.feedback.reason)
            .map(f => f.feedback.reason!);
        
        const reasonCounts = new Map<string, number>();
        reasons.forEach(reason => {
            reasonCounts.set(reason, (reasonCounts.get(reason) || 0) + 1);
        });
        
        const commonReasons = Array.from(reasonCounts.entries())
            .map(([reason, count]) => ({ reason, count }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 5);

        // Identify preferred patterns (files frequently approved)
        const fileApprovals = new Map<string, number>();
        this.feedbackHistory
            .filter(f => f.feedback.approved && f.context.filePath)
            .forEach(f => {
                const path = f.context.filePath!;
                fileApprovals.set(path, (fileApprovals.get(path) || 0) + 1);
            });
        
        const preferredPatterns = Array.from(fileApprovals.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([path]) => path);

        return {
            totalFeedback: total,
            approvalRate,
            averageRating,
            commonReasons,
            preferredPatterns
        };
    }

    /**
     * Display feedback statistics
     */
    public async showFeedbackStats(): Promise<void> {
        const stats = this.getFeedbackStats();

        const panel = vscode.window.createWebviewPanel(
            'feedbackStats',
            'Feedback Statistics',
            vscode.ViewColumn.Two,
            {
                enableScripts: true
            }
        );

        panel.webview.html = this.getFeedbackStatsHtml(stats);
    }

    /**
     * Generate HTML for feedback statistics
     */
    private getFeedbackStatsHtml(stats: FeedbackStats): string {
        const reasonRows = stats.commonReasons.map(r => `
            <tr>
                <td>${r.reason}</td>
                <td>${r.count}</td>
            </tr>
        `).join('');

        const patternRows = stats.preferredPatterns.map(p => `
            <li><code>${p}</code></li>
        `).join('');

        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Feedback Statistics</title>
                <style>
                    body {
                        font-family: var(--vscode-font-family);
                        color: var(--vscode-foreground);
                        background-color: var(--vscode-editor-background);
                        padding: 20px;
                    }
                    .stat-card {
                        margin-bottom: 20px;
                        padding: 15px;
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 4px;
                    }
                    .stat-card h2 {
                        margin-top: 0;
                        color: var(--vscode-textLink-foreground);
                    }
                    .stat-value {
                        font-size: 2em;
                        font-weight: bold;
                        color: var(--vscode-textLink-activeForeground);
                    }
                    .progress-bar {
                        width: 100%;
                        height: 20px;
                        background-color: var(--vscode-input-background);
                        border-radius: 10px;
                        overflow: hidden;
                        margin: 10px 0;
                    }
                    .progress-fill {
                        height: 100%;
                        background-color: var(--vscode-progressBar-background);
                        transition: width 0.3s ease;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 10px;
                    }
                    th, td {
                        text-align: left;
                        padding: 8px;
                        border-bottom: 1px solid var(--vscode-panel-border);
                    }
                    th {
                        font-weight: bold;
                    }
                    code {
                        background-color: var(--vscode-textCodeBlock-background);
                        padding: 2px 6px;
                        border-radius: 3px;
                    }
                    ul {
                        margin: 10px 0;
                        padding-left: 20px;
                    }
                </style>
            </head>
            <body>
                <h1>Feedback Statistics</h1>

                <div class="stat-card">
                    <h2>Total Feedback Items</h2>
                    <div class="stat-value">${stats.totalFeedback}</div>
                </div>

                <div class="stat-card">
                    <h2>Approval Rate</h2>
                    <div class="stat-value">${(stats.approvalRate * 100).toFixed(1)}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${stats.approvalRate * 100}%"></div>
                    </div>
                </div>

                <div class="stat-card">
                    <h2>Average Rating</h2>
                    <div class="stat-value">${stats.averageRating.toFixed(1)} / 5.0</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${(stats.averageRating / 5) * 100}%"></div>
                    </div>
                </div>

                ${stats.commonReasons.length > 0 ? `
                    <div class="stat-card">
                        <h2>Common Rejection Reasons</h2>
                        <table>
                            <thead>
                                <tr>
                                    <th>Reason</th>
                                    <th>Count</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${reasonRows}
                            </tbody>
                        </table>
                    </div>
                ` : ''}

                ${stats.preferredPatterns.length > 0 ? `
                    <div class="stat-card">
                        <h2>Frequently Approved Files</h2>
                        <ul>
                            ${patternRows}
                        </ul>
                    </div>
                ` : ''}
            </body>
            </html>
        `;
    }

    /**
     * Request user feedback on a suggestion
     */
    public async requestUserFeedback(goal: string, task: string): Promise<void> {
        const rating = await vscode.window.showQuickPick(
            [
                { label: '⭐⭐⭐⭐⭐ Excellent', value: 5 },
                { label: '⭐⭐⭐⭐ Good', value: 4 },
                { label: '⭐⭐⭐ Average', value: 3 },
                { label: '⭐⭐ Poor', value: 2 },
                { label: '⭐ Very Poor', value: 1 }
            ],
            {
                placeHolder: 'How would you rate this suggestion?',
                title: 'Provide Feedback'
            }
        );

        if (!rating) {
            return;
        }

        const suggestions = await vscode.window.showInputBox({
            prompt: 'Any suggestions for improvement? (Optional)',
            placeHolder: 'Your feedback helps improve future suggestions...'
        });

        await this.recordRatingFeedback(
            rating.value,
            { goal, task },
            suggestions
        );

        vscode.window.showInformationMessage('Thank you for your feedback!');
    }

    /**
     * Sync all pending feedback to server
     */
    public async syncFeedbackToServer(): Promise<void> {
        if (!this.client.isConnected()) {
            vscode.window.showWarningMessage('Not connected to Director. Cannot sync feedback.');
            return;
        }

        this.outputChannel.appendLine('Syncing feedback to server...');
        
        let synced = 0;
        for (const feedback of this.feedbackHistory) {
            try {
                await this.sendFeedbackToServer(feedback);
                synced++;
            } catch (error) {
                this.outputChannel.appendLine(
                    `Failed to sync feedback ${feedback.id}: ${error}`
                );
            }
        }

        this.outputChannel.appendLine(`Synced ${synced}/${this.feedbackHistory.length} feedback items`);
        vscode.window.showInformationMessage(`Synced ${synced} feedback item(s) to server`);
    }

    /**
     * Clear feedback history
     */
    public async clearFeedbackHistory(): Promise<void> {
        const confirm = await vscode.window.showWarningMessage(
            'Are you sure you want to clear all feedback history?',
            { modal: true },
            'Clear',
            'Cancel'
        );

        if (confirm === 'Clear') {
            this.feedbackHistory = [];
            await this.saveFeedbackHistory();
            this.outputChannel.appendLine('Cleared feedback history');
            vscode.window.showInformationMessage('Feedback history cleared');
        }
    }

    /**
     * Export feedback history
     */
    public async exportFeedbackHistory(): Promise<void> {
        const uri = await vscode.window.showSaveDialog({
            defaultUri: vscode.Uri.file('feedback-history.json'),
            filters: {
                'JSON': ['json']
            }
        });

        if (!uri) {
            return;
        }

        try {
            const content = JSON.stringify(this.feedbackHistory, null, 2);
            await vscode.workspace.fs.writeFile(uri, Buffer.from(content, 'utf8'));
            vscode.window.showInformationMessage('Feedback history exported successfully');
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to export feedback: ${error}`);
        }
    }

    /**
     * Load feedback history from workspace state
     */
    private loadFeedbackHistory(): void {
        const saved = this.context.workspaceState.get<FeedbackItem[]>('feedbackHistory');
        if (saved) {
            this.feedbackHistory = saved.map(item => ({
                ...item,
                timestamp: new Date(item.timestamp)
            }));
            this.outputChannel.appendLine(
                `Loaded ${this.feedbackHistory.length} feedback item(s) from history`
            );
        }
    }

    /**
     * Save feedback history to workspace state
     */
    private async saveFeedbackHistory(): Promise<void> {
        await this.context.workspaceState.update('feedbackHistory', this.feedbackHistory);
    }

    /**
     * Generate unique feedback ID using timestamp and counter
     * Counter is persisted to avoid duplicates across restarts
     */
    private generateFeedbackId(): string {
        // Use a more robust ID generation with random component to avoid collisions
        const timestamp = Date.now();
        const counter = this.feedbackId++;
        const random = Math.floor(Math.random() * 10000);
        return `fb_${timestamp}_${counter}_${random}`;
    }

    /**
     * Get feedback history
     */
    public getFeedbackHistory(): FeedbackItem[] {
        return [...this.feedbackHistory];
    }
}
