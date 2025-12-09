/**
 * Copilot Context Provider for Director
 * 
 * This module provides context from Director's RAG system to GitHub Copilot
 * for improved inline code suggestions and completions.
 * 
 * Features:
 * - Workspace context integration
 * - RAG-based documentation context
 * - Project-specific knowledge
 * - Unreal Engine API context
 */

import * as vscode from 'vscode';
import { DirectorIPCClient } from './ipcClient';

/**
 * Register Director as a language model context provider
 * 
 * Note: This functionality requires VS Code Proposed APIs that may not be available.
 * The extension will work without this - it's an optional enhancement.
 */
export function registerContextProvider(
    context: vscode.ExtensionContext,
    getClient: () => DirectorIPCClient | null,
    outputChannel: vscode.OutputChannel
): void {
    // The context provider API is part of proposed APIs and may not be available
    // We'll skip this for now - the chat participant provides the main functionality
    outputChannel.appendLine('ℹ️ Advanced context provider requires VS Code Proposed APIs (optional)');
}

// Context provider implementation removed - requires VS Code Proposed APIs
// The chat participant provides the main functionality for Director integration

/**
 * Enhanced context provider that can extract context from the current editor
 */
export class DirectorEnhancedContext {
    constructor(
        private getClient: () => DirectorIPCClient | null,
        private outputChannel: vscode.OutputChannel
    ) {}

    /**
     * Get context for the current editor position
     */
    async getContextForPosition(
        document: vscode.TextDocument,
        position: vscode.Position
    ): Promise<string | null> {
        const client = this.getClient();
        if (!client || !client.isConnected()) {
            return null;
        }

        try {
            // Extract context around the cursor
            const range = new vscode.Range(
                new vscode.Position(Math.max(0, position.line - 10), 0),
                new vscode.Position(Math.min(document.lineCount - 1, position.line + 10), 0)
            );
            const surroundingCode = document.getText(range);

            // Get the current line
            const currentLine = document.lineAt(position.line).text;

            // Build context query
            const query = `Provide context for code completion:
File: ${document.fileName}
Language: ${document.languageId}
Current line: ${currentLine}
Surrounding code:
${surroundingCode}`;

            // Query Director
            const response = await client.query(query);
            
            if (response.status === 'success' && response.result) {
                return response.result;
            }

            return null;

        } catch (error) {
            this.outputChannel.appendLine(
                `Enhanced context error: ${error instanceof Error ? error.message : String(error)}`
            );
            return null;
        }
    }

    /**
     * Get context for a specific code symbol
     */
    async getContextForSymbol(symbolName: string, documentUri: vscode.Uri): Promise<string | null> {
        const client = this.getClient();
        if (!client || !client.isConnected()) {
            return null;
        }

        try {
            const query = `Explain the symbol or API: ${symbolName} in context of Unreal Engine`;
            const response = await client.query(query);
            
            if (response.status === 'success' && response.result) {
                return response.result;
            }

            return null;

        } catch (error) {
            this.outputChannel.appendLine(
                `Symbol context error: ${error instanceof Error ? error.message : String(error)}`
            );
            return null;
        }
    }

    /**
     * Get project-specific context
     */
    async getProjectContext(): Promise<string | null> {
        const client = this.getClient();
        if (!client || !client.isConnected()) {
            return null;
        }

        try {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (!workspaceFolders || workspaceFolders.length === 0) {
                return null;
            }

            const projectPath = workspaceFolders[0].uri.fsPath;
            const query = `Provide overview of project at: ${projectPath}`;
            const response = await client.query(query);
            
            if (response.status === 'success' && response.result) {
                return response.result;
            }

            return null;

        } catch (error) {
            this.outputChannel.appendLine(
                `Project context error: ${error instanceof Error ? error.message : String(error)}`
            );
            return null;
        }
    }
}

/**
 * Hover provider that shows Director context on hover
 */
export function registerHoverProvider(
    context: vscode.ExtensionContext,
    getClient: () => DirectorIPCClient | null,
    outputChannel: vscode.OutputChannel
): void {
    const config = vscode.workspace.getConfiguration('director');
    if (!config.get('copilot.enableHoverContext', true)) {
        outputChannel.appendLine('ℹ️ Hover context disabled in settings');
        return;
    }
    
    const enhancedContext = new DirectorEnhancedContext(getClient, outputChannel);

    // Register for C++ files (Unreal Engine)
    const cppHoverProvider = vscode.languages.registerHoverProvider(
        ['cpp', 'c'],
        {
            async provideHover(document, position, token) {
                // Get the word at the current position
                const wordRange = document.getWordRangeAtPosition(position);
                if (!wordRange) {
                    return null;
                }

                const word = document.getText(wordRange);
                
                // Unreal Engine naming convention regex
                // U* = UObject-derived classes (UMyClass)
                // A* = AActor-derived classes (AMyActor)
                // F* = Structs (FVector, FString)
                // E* = Enums (ECollisionChannel)
                // T* = Templates (TArray, TMap)
                const UNREAL_SYMBOL_PATTERN = /^[UAFET][A-Z]/;
                
                // Only provide hover for Unreal Engine symbols
                if (!UNREAL_SYMBOL_PATTERN.test(word)) {
                    return null;
                }

                try {
                    const contextInfo = await enhancedContext.getContextForSymbol(word, document.uri);
                    if (contextInfo) {
                        const markdown = new vscode.MarkdownString();
                        markdown.appendMarkdown('### Director Context\n\n');
                        markdown.appendMarkdown(contextInfo);
                        return new vscode.Hover(markdown);
                    }
                } catch (error) {
                    // Silent fail - don't show errors in hover
                }

                return null;
            }
        }
    );

    context.subscriptions.push(cppHoverProvider);
    outputChannel.appendLine('✓ Director hover provider registered for C++ files');
}

/**
 * Code action provider for Director suggestions
 */
export function registerCodeActionProvider(
    context: vscode.ExtensionContext,
    getClient: () => DirectorIPCClient | null,
    outputChannel: vscode.OutputChannel
): void {
    const config = vscode.workspace.getConfiguration('director');
    if (!config.get('copilot.enableCodeActions', true)) {
        outputChannel.appendLine('ℹ️ Code actions disabled in settings');
        return;
    }
    
    const codeActionProvider = vscode.languages.registerCodeActionsProvider(
        ['cpp', 'c', 'typescript', 'javascript'],
        {
            async provideCodeActions(document, range, codeContext, token) {
                const actions: vscode.CodeAction[] = [];

                // Add "Ask Director" action
                const askDirectorAction = new vscode.CodeAction(
                    'Ask Director about this code',
                    vscode.CodeActionKind.Empty
                );
                askDirectorAction.command = {
                    command: 'director.askAboutSelection',
                    title: 'Ask Director',
                    arguments: [document, range]
                };
                actions.push(askDirectorAction);

                // Add "Get Context" action
                const getContextAction = new vscode.CodeAction(
                    'Get Director context',
                    vscode.CodeActionKind.Empty
                );
                getContextAction.command = {
                    command: 'director.getContextForSelection',
                    title: 'Get Context',
                    arguments: [document, range]
                };
                actions.push(getContextAction);

                return actions;
            }
        }
    );

    context.subscriptions.push(codeActionProvider);
    outputChannel.appendLine('✓ Director code action provider registered');
}
