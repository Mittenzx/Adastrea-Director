/**
 * Code Applicator Service
 * 
 * Handles automated code application via VS Code API with approval workflow.
 * Part of Phase 2: Semi-Autonomous Development
 */

import * as vscode from 'vscode';
import * as path from 'path';

export interface CodeModification {
    filePath: string;
    modificationType: 'create' | 'modify' | 'delete';
    description: string;
    codeSnippet?: string;
    lineStart?: number;
    lineEnd?: number;
    confidence?: number; // 0-1 confidence score from AI
}

export interface CodeApplicationResult {
    success: boolean;
    appliedModifications: CodeModification[];
    failedModifications: CodeModification[];
    errors: string[];
}

export interface ApprovalDecision {
    approved: boolean;
    reason?: string;
    timestamp: Date;
    modification: CodeModification;
    autoApproved?: boolean; // Explicit flag for auto-approval
}

export class CodeApplicator {
    private pendingModifications: CodeModification[] = [];
    private approvalHistory: ApprovalDecision[] = [];
    private autoApprovalThreshold: number = 0.9; // Default threshold for auto-approval
    
    constructor(
        private outputChannel: vscode.OutputChannel
    ) {}

    /**
     * Set the auto-approval confidence threshold
     */
    public setAutoApprovalThreshold(threshold: number): void {
        if (threshold < 0 || threshold > 1) {
            throw new Error('Threshold must be between 0 and 1');
        }
        this.autoApprovalThreshold = threshold;
        this.outputChannel.appendLine(`Auto-approval threshold set to: ${threshold}`);
    }

    /**
     * Get the current auto-approval threshold
     */
    public getAutoApprovalThreshold(): number {
        return this.autoApprovalThreshold;
    }

    /**
     * Add modifications to the pending queue
     */
    public async queueModifications(modifications: CodeModification[]): Promise<void> {
        this.pendingModifications.push(...modifications);
        this.outputChannel.appendLine(`Queued ${modifications.length} modification(s)`);
        
        // Process modifications based on confidence
        await this.processQueue();
    }

    /**
     * Get pending modifications
     */
    public getPendingModifications(): CodeModification[] {
        return [...this.pendingModifications];
    }

    /**
     * Clear pending modifications
     */
    public clearPendingModifications(): void {
        this.pendingModifications = [];
        this.outputChannel.appendLine('Cleared pending modifications');
    }

    /**
     * Process pending modifications queue
     */
    private async processQueue(): Promise<void> {
        const highConfidence: CodeModification[] = [];
        const lowConfidence: CodeModification[] = [];

        // Separate by confidence
        for (const mod of this.pendingModifications) {
            if (mod.confidence !== undefined && mod.confidence >= this.autoApprovalThreshold) {
                highConfidence.push(mod);
            } else {
                lowConfidence.push(mod);
            }
        }

        // Auto-apply high confidence modifications
        if (highConfidence.length > 0) {
            this.outputChannel.appendLine(`Auto-applying ${highConfidence.length} high-confidence modification(s)...`);
            for (const mod of highConfidence) {
                await this.recordApproval(mod, true, 'Auto-approved (high confidence)', true);
            }
            await this.applyModifications(highConfidence);
        }

        // Request approval for low confidence modifications
        if (lowConfidence.length > 0) {
            this.outputChannel.appendLine(`${lowConfidence.length} modification(s) require approval`);
            await this.requestApproval(lowConfidence);
        }

        // Clear processed modifications
        this.pendingModifications = [];
    }

    /**
     * Request user approval for modifications
     */
    private async requestApproval(modifications: CodeModification[]): Promise<void> {
        for (const mod of modifications) {
            const choice = await vscode.window.showQuickPick(
                [
                    { label: '✓ Approve', value: 'approve' },
                    { label: '✗ Reject', value: 'reject' },
                    { label: '👁 Preview Diff', value: 'preview' },
                    { label: '✎ Edit', value: 'edit' }
                ],
                {
                    placeHolder: `${mod.modificationType.toUpperCase()}: ${mod.filePath}`,
                    title: `Approve Code Change? (Confidence: ${(mod.confidence || 0) * 100}%)`,
                    ignoreFocusOut: true
                }
            );

            if (!choice) {
                await this.recordApproval(mod, false, 'User cancelled');
                continue;
            }

            switch (choice.value) {
                case 'approve':
                    await this.recordApproval(mod, true, 'User approved', false);
                    await this.applyModifications([mod]);
                    break;
                case 'reject':
                    const reason = await vscode.window.showInputBox({
                        prompt: 'Why are you rejecting this change? (Optional)',
                        placeHolder: 'Reason for rejection...'
                    });
                    await this.recordApproval(mod, false, reason || 'User rejected', false);
                    break;
                case 'preview':
                    await this.showDiffPreview(mod);
                    // After preview, just return to exit the workflow
                    return;
                case 'edit':
                    await this.openForEditing(mod);
                    await this.recordApproval(mod, false, 'User chose to edit manually', false);
                    return;
            }
        }
    }

    /**
     * Apply approved modifications
     */
    public async applyModifications(modifications: CodeModification[]): Promise<CodeApplicationResult> {
        const result: CodeApplicationResult = {
            success: true,
            appliedModifications: [],
            failedModifications: [],
            errors: []
        };

        for (const mod of modifications) {
            try {
                await this.applyModification(mod);
                result.appliedModifications.push(mod);
                this.outputChannel.appendLine(`✓ Applied: ${mod.filePath}`);
            } catch (error) {
                result.success = false;
                result.failedModifications.push(mod);
                const errorMsg = error instanceof Error ? error.message : String(error);
                result.errors.push(`${mod.filePath}: ${errorMsg}`);
                this.outputChannel.appendLine(`✗ Failed: ${mod.filePath} - ${errorMsg}`);
            }
        }

        // Show summary
        if (result.appliedModifications.length > 0) {
            vscode.window.showInformationMessage(
                `Applied ${result.appliedModifications.length} code modification(s)`
            );
        }

        if (result.failedModifications.length > 0) {
            vscode.window.showWarningMessage(
                `Failed to apply ${result.failedModifications.length} modification(s)`
            );
        }

        return result;
    }

    /**
     * Apply a single modification
     */
    private async applyModification(mod: CodeModification): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }

        // Validate and normalize the file path to prevent directory traversal attacks
        const fullPath = this.validateAndNormalizePath(mod.filePath, workspaceFolder.uri.fsPath);
        
        const fileUri = vscode.Uri.file(fullPath);

        switch (mod.modificationType) {
            case 'create':
                await this.createFile(fileUri, mod.codeSnippet || '');
                break;
            case 'modify':
                await this.modifyFile(fileUri, mod);
                break;
            case 'delete':
                await this.deleteFile(fileUri);
                break;
        }
    }

    /**
     * Validate and normalize file path to ensure it's within workspace
     * Prevents directory traversal attacks
     */
    private validateAndNormalizePath(filePath: string, workspaceRoot: string): string {
        // Resolve the full path
        const fullPath = path.isAbsolute(filePath)
            ? path.resolve(filePath)
            : path.resolve(workspaceRoot, filePath);
        
        // Normalize to remove .. and . segments
        const normalizedPath = path.normalize(fullPath);
        const normalizedWorkspace = path.normalize(workspaceRoot);
        
        // Ensure the path is within the workspace
        if (!normalizedPath.startsWith(normalizedWorkspace + path.sep) && 
            normalizedPath !== normalizedWorkspace) {
            throw new Error(
                `Security: File path "${filePath}" is outside workspace. ` +
                `All modifications must be within the workspace directory.`
            );
        }
        
        return normalizedPath;
    }

    /**
     * Create a new file
     */
    private async createFile(uri: vscode.Uri, content: string): Promise<void> {
        const edit = new vscode.WorkspaceEdit();
        edit.createFile(uri, { overwrite: false, ignoreIfExists: false });
        await vscode.workspace.applyEdit(edit);

        // Write content
        const textEdit = new vscode.WorkspaceEdit();
        textEdit.insert(uri, new vscode.Position(0, 0), content);
        await vscode.workspace.applyEdit(textEdit);
    }

    /**
     * Modify an existing file
     */
    private async modifyFile(uri: vscode.Uri, mod: CodeModification): Promise<void> {
        const document = await vscode.workspace.openTextDocument(uri);
        const edit = new vscode.WorkspaceEdit();

        if (mod.lineStart !== undefined && mod.lineEnd !== undefined) {
            // Replace specific lines (line numbers are 0-indexed in VS Code)
            const start = new vscode.Position(mod.lineStart - 1, 0);
            const end = new vscode.Position(mod.lineEnd - 1, document.lineAt(mod.lineEnd - 1).text.length);
            const range = new vscode.Range(start, end);
            // Ensure code snippet is properly formatted for replacement
            const codeToInsert = mod.codeSnippet || '';
            edit.replace(uri, range, codeToInsert);
        } else {
            // Append to end of file
            const lastLine = document.lineCount - 1;
            const lastLineText = document.lineAt(lastLine).text;
            const position = new vscode.Position(lastLine, lastLineText.length);
            edit.insert(uri, position, '\n' + (mod.codeSnippet || ''));
        }

        await vscode.workspace.applyEdit(edit);
    }

    /**
     * Delete a file
     */
    private async deleteFile(uri: vscode.Uri): Promise<void> {
        const edit = new vscode.WorkspaceEdit();
        edit.deleteFile(uri);
        await vscode.workspace.applyEdit(edit);
    }

    /**
     * Generate a preview of the modification
     */
    private async generatePreview(mod: CodeModification): Promise<string> {
        const preview = `
File: ${mod.filePath}
Type: ${mod.modificationType.toUpperCase()}
Description: ${mod.description}
Confidence: ${mod.confidence ? (mod.confidence * 100).toFixed(1) : 'N/A'}%

Code:
${mod.codeSnippet || '(No code snippet)'}
        `.trim();

        return preview;
    }

    /**
     * Show diff preview for a modification
     */
    private async showDiffPreview(mod: CodeModification): Promise<void> {
        if (mod.modificationType === 'create') {
            // For new files, show the content in a new editor
            const doc = await vscode.workspace.openTextDocument({
                content: mod.codeSnippet || '',
                language: this.getLanguageFromPath(mod.filePath)
            });
            await vscode.window.showTextDocument(doc, { preview: true });
            return;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        const fullPath = path.isAbsolute(mod.filePath)
            ? mod.filePath
            : path.join(workspaceFolder.uri.fsPath, mod.filePath);
        
        const fileUri = vscode.Uri.file(fullPath);

        try {
            // Open the original file
            const document = await vscode.workspace.openTextDocument(fileUri);
            
            // Create a modified version in memory
            let modifiedContent = document.getText();
            if (mod.lineStart !== undefined && mod.lineEnd !== undefined && mod.codeSnippet) {
                const lines = modifiedContent.split('\n');
                const newLines = mod.codeSnippet.split('\n');
                // Lines are 1-indexed from server, but splice uses 0-indexed
                lines.splice(mod.lineStart - 1, mod.lineEnd - mod.lineStart + 1, ...newLines);
                modifiedContent = lines.join('\n');
            }

            // Create a temporary document with the modified content
            const modifiedDoc = await vscode.workspace.openTextDocument({
                content: modifiedContent,
                language: document.languageId
            });

            // Show diff
            await vscode.commands.executeCommand(
                'vscode.diff',
                document.uri,
                modifiedDoc.uri,
                `${path.basename(mod.filePath)} (Original ↔ Proposed)`
            );
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to show diff: ${error}`);
        }
    }

    /**
     * Open file for manual editing
     */
    private async openForEditing(mod: CodeModification): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        const fullPath = path.isAbsolute(mod.filePath)
            ? mod.filePath
            : path.join(workspaceFolder.uri.fsPath, mod.filePath);
        
        const fileUri = vscode.Uri.file(fullPath);

        try {
            const document = await vscode.workspace.openTextDocument(fileUri);
            const editor = await vscode.window.showTextDocument(document);

            // If line numbers specified, navigate to that location
            if (mod.lineStart !== undefined) {
                const position = new vscode.Position(mod.lineStart, 0);
                editor.selection = new vscode.Selection(position, position);
                editor.revealRange(new vscode.Range(position, position));
            }

            // Show the proposed code in output channel for reference
            this.outputChannel.appendLine('\n--- Proposed Code ---');
            this.outputChannel.appendLine(mod.codeSnippet || '(No code snippet)');
            this.outputChannel.appendLine('--- End ---\n');
            this.outputChannel.show(true);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to open file: ${error}`);
        }
    }

    /**
     * Record approval decision
     */
    private async recordApproval(mod: CodeModification, approved: boolean, reason?: string, autoApproved?: boolean): Promise<void> {
        const decision: ApprovalDecision = {
            approved,
            reason,
            timestamp: new Date(),
            modification: mod,
            autoApproved
        };

        this.approvalHistory.push(decision);
        
        this.outputChannel.appendLine(
            `Recorded: ${approved ? 'Approved' : 'Rejected'} - ${mod.filePath}${reason ? ` (${reason})` : ''}`
        );
    }

    /**
     * Get approval history
     */
    public getApprovalHistory(): ApprovalDecision[] {
        return [...this.approvalHistory];
    }

    /**
     * Get approval statistics
     */
    public getApprovalStats(): {
        total: number;
        approved: number;
        rejected: number;
        autoApproved: number;
        approvalRate: number;
    } {
        const total = this.approvalHistory.length;
        const approved = this.approvalHistory.filter(d => d.approved).length;
        const rejected = total - approved;
        const autoApproved = this.approvalHistory.filter(
            d => d.approved && d.autoApproved === true
        ).length;
        const approvalRate = total > 0 ? approved / total : 0;

        return {
            total,
            approved,
            rejected,
            autoApproved,
            approvalRate
        };
    }

    /**
     * Clear approval history
     */
    public clearApprovalHistory(): void {
        this.approvalHistory = [];
        this.outputChannel.appendLine('Cleared approval history');
    }

    /**
     * Get language ID from file path
     */
    private getLanguageFromPath(filePath: string): string {
        const ext = path.extname(filePath).toLowerCase();
        const languageMap: { [key: string]: string } = {
            '.ts': 'typescript',
            '.js': 'javascript',
            '.py': 'python',
            '.cpp': 'cpp',
            '.h': 'cpp',
            '.cs': 'csharp',
            '.json': 'json',
            '.md': 'markdown',
            '.yaml': 'yaml',
            '.yml': 'yaml'
        };
        return languageMap[ext] || 'plaintext';
    }
}
