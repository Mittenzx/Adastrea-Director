/**
 * Copilot Chat Participant for Adastrea Director
 * 
 * This module implements a GitHub Copilot Chat participant (@director) that
 * integrates the Director RAG system with VS Code's Copilot Chat interface.
 * 
 * Features:
 * - Natural language queries to Director AI
 * - Context-aware code suggestions using Director's RAG system
 * - Slash commands for specific operations
 * - Integration with Director's planning and analysis capabilities
 */

import * as vscode from 'vscode';
import { DirectorIPCClient, IPCResponse } from './ipcClient';

/**
 * Slash command types supported by the Director participant
 */
export enum DirectorSlashCommand {
    Ask = 'ask',
    Plan = 'plan',
    Analyze = 'analyze',
    Context = 'context',
    Help = 'help'
}

/**
 * Initialize the Director Copilot Chat participant
 */
export function initializeCopilotParticipant(
    context: vscode.ExtensionContext,
    getClient: () => DirectorIPCClient | null,
    outputChannel: vscode.OutputChannel
): vscode.ChatParticipant | null {
    try {
        // Create the chat participant
        const participant = vscode.chat.createChatParticipant(
            'director.chat',
            createChatHandler(getClient, outputChannel)
        );

        // Configure participant metadata
        participant.iconPath = new vscode.ThemeIcon('robot');

        // Note: Slash commands are defined in package.json under chatParticipants.commands
        
        // Add to subscriptions
        context.subscriptions.push(participant);

        outputChannel.appendLine('✓ Director Copilot Chat participant initialized');
        return participant;

    } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        outputChannel.appendLine(`✗ Failed to initialize Copilot Chat participant: ${errorMsg}`);
        vscode.window.showErrorMessage(
            'Failed to initialize Director Copilot integration. The Chat API may not be available in your VS Code version.',
            'View Output'
        ).then(selection => {
            if (selection === 'View Output') {
                outputChannel.show();
            }
        });
        return null;
    }
}

/**
 * Create the chat request handler
 */
function createChatHandler(
    getClient: () => DirectorIPCClient | null,
    outputChannel: vscode.OutputChannel
): vscode.ChatRequestHandler {
    return async (
        request: vscode.ChatRequest,
        context: vscode.ChatContext,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<vscode.ChatResult> => {
        // Check if client is connected
        const client = getClient();
        if (!client || !client.isConnected()) {
            stream.markdown(
                '⚠️ Not connected to Director. Please connect using the command:\n\n' +
                '`Director: Connect to Unreal Engine`\n\n' +
                'Then try your request again.'
            );
            return { metadata: { command: 'error' } };
        }

        try {
            // Handle cancellation
            if (token.isCancellationRequested) {
                return { metadata: { command: 'cancelled' } };
            }

            // Determine command type
            const command = request.command || DirectorSlashCommand.Ask;
            const prompt = request.prompt.trim();

            // Show progress
            stream.progress('Querying Director...');

            // Route to appropriate handler
            let response: IPCResponse;
            let resultMetadata: any = { command };

            switch (command) {
                case DirectorSlashCommand.Help:
                    return handleHelpCommand(stream);

                case DirectorSlashCommand.Plan:
                    response = await client.plan(prompt);
                    resultMetadata.type = 'plan';
                    break;

                case DirectorSlashCommand.Analyze:
                    response = await client.analyze(prompt);
                    resultMetadata.type = 'analysis';
                    break;

                case DirectorSlashCommand.Context:
                    response = await client.query(`Get relevant context for: ${prompt}`);
                    resultMetadata.type = 'context';
                    break;

                case DirectorSlashCommand.Ask:
                default:
                    response = await client.query(prompt);
                    resultMetadata.type = 'query';
                    break;
            }

            // Check for cancellation again
            if (token.isCancellationRequested) {
                return { metadata: { command: 'cancelled' } };
            }

            // Handle response
            if (response.status === 'success') {
                await formatSuccessResponse(stream, response, command);
            } else {
                await formatErrorResponse(stream, response);
            }

            return { metadata: resultMetadata };

        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : String(error);
            outputChannel.appendLine(`Copilot Chat error: ${errorMsg}`);
            
            stream.markdown(`❌ **Error**: ${errorMsg}\n\n`);
            stream.markdown('Please try again or check the Director connection.');

            return { 
                metadata: { 
                    command: 'error',
                    error: errorMsg 
                } 
            };
        }
    };
}

/**
 * Handle the help command
 */
function handleHelpCommand(stream: vscode.ChatResponseStream): vscode.ChatResult {
    stream.markdown('# Director Copilot Integration\n\n');
    stream.markdown('Ask me anything about Unreal Engine development or your project!\n\n');
    
    stream.markdown('## Available Commands\n\n');
    stream.markdown('- `/ask` - Ask a question (default)\n');
    stream.markdown('- `/plan` - Generate a development plan\n');
    stream.markdown('- `/analyze` - Analyze a goal or task\n');
    stream.markdown('- `/context` - Get relevant context from RAG\n');
    stream.markdown('- `/help` - Show this help\n\n');
    
    stream.markdown('## Example Usage\n\n');
    stream.markdown('```\n');
    stream.markdown('@director How do I create a player character?\n');
    stream.markdown('@director /plan Create a health system\n');
    stream.markdown('@director /analyze Implement AI pathfinding\n');
    stream.markdown('@director /context Blueprint event graph\n');
    stream.markdown('```\n\n');
    
    stream.markdown('## Features\n\n');
    stream.markdown('- 🤖 AI-powered answers from Director\'s RAG system\n');
    stream.markdown('- 📋 Development plan generation\n');
    stream.markdown('- 🔍 Goal analysis and task breakdown\n');
    stream.markdown('- 📚 Context-aware suggestions\n');
    stream.markdown('- 🎮 Unreal Engine expertise\n\n');

    return { metadata: { command: 'help' } };
}

/**
 * Format a successful response
 */
async function formatSuccessResponse(
    stream: vscode.ChatResponseStream,
    response: IPCResponse,
    command: string
): Promise<void> {
    // Handle different response types
    if (command === DirectorSlashCommand.Plan && response.plan) {
        await formatPlanResponse(stream, response.plan);
    } else if (command === DirectorSlashCommand.Analyze && response.analysis) {
        await formatAnalysisResponse(stream, response.analysis);
    } else if (response.result) {
        // General result formatting
        stream.markdown(response.result);
    } else if (response.message) {
        stream.markdown(response.message);
    } else {
        stream.markdown('✓ Request completed successfully.');
    }

    // Add follow-up suggestions
    addFollowUpPrompts(stream, command);
}

/**
 * Format a plan response
 */
async function formatPlanResponse(stream: vscode.ChatResponseStream, plan: any): Promise<void> {
    stream.markdown('## Development Plan\n\n');
    
    if (plan.goal) {
        stream.markdown(`**Goal:** ${plan.goal}\n\n`);
    }

    if (plan.tasks && Array.isArray(plan.tasks)) {
        stream.markdown('### Tasks\n\n');
        plan.tasks.forEach((task: any, index: number) => {
            const taskNum = index + 1;
            const taskTitle = typeof task === 'string' ? task : (task.title || task.description || `Task ${taskNum}`);
            stream.markdown(`${taskNum}. ${taskTitle}\n`);
        });
        stream.markdown('\n');
    }

    if (plan.steps && Array.isArray(plan.steps)) {
        stream.markdown('### Steps\n\n');
        plan.steps.forEach((step: any, index: number) => {
            const stepNum = index + 1;
            const stepDesc = typeof step === 'string' ? step : (step.description || `Step ${stepNum}`);
            stream.markdown(`${stepNum}. ${stepDesc}\n`);
        });
        stream.markdown('\n');
    }

    if (plan.considerations) {
        stream.markdown('### Considerations\n\n');
        stream.markdown(plan.considerations + '\n\n');
    }
}

/**
 * Format an analysis response
 */
async function formatAnalysisResponse(stream: vscode.ChatResponseStream, analysis: any): Promise<void> {
    stream.markdown('## Goal Analysis\n\n');
    
    if (analysis.summary) {
        stream.markdown(`**Summary:** ${analysis.summary}\n\n`);
    }

    if (analysis.complexity) {
        stream.markdown(`**Complexity:** ${analysis.complexity}\n\n`);
    }

    if (analysis.requirements && Array.isArray(analysis.requirements)) {
        stream.markdown('### Requirements\n\n');
        analysis.requirements.forEach((req: string) => {
            stream.markdown(`- ${req}\n`);
        });
        stream.markdown('\n');
    }

    if (analysis.risks && Array.isArray(analysis.risks)) {
        stream.markdown('### Risks\n\n');
        analysis.risks.forEach((risk: string) => {
            stream.markdown(`- ${risk}\n`);
        });
        stream.markdown('\n');
    }

    if (analysis.recommendations && Array.isArray(analysis.recommendations)) {
        stream.markdown('### Recommendations\n\n');
        analysis.recommendations.forEach((rec: string) => {
            stream.markdown(`- ${rec}\n`);
        });
        stream.markdown('\n');
    }
}

/**
 * Format an error response
 */
async function formatErrorResponse(stream: vscode.ChatResponseStream, response: IPCResponse): Promise<void> {
    const errorMsg = response.error || 'Unknown error occurred';
    stream.markdown(`❌ **Error**: ${errorMsg}\n\n`);
    
    if (response.message && response.message !== errorMsg) {
        stream.markdown(`*Additional info*: ${response.message}\n\n`);
    }

    stream.markdown('Please try again or rephrase your request.');
}

/**
 * Add follow-up prompt suggestions
 */
function addFollowUpPrompts(stream: vscode.ChatResponseStream, command: string): void {
    const followUps: vscode.ChatFollowup[] = [];

    switch (command) {
        case DirectorSlashCommand.Plan:
            followUps.push(
                { prompt: 'Generate code for this plan', label: '🔨 Generate Code' },
                { prompt: 'Analyze the plan complexity', label: '🔍 Analyze' }
            );
            break;

        case DirectorSlashCommand.Analyze:
            followUps.push(
                { prompt: 'Create a plan for this', label: '📋 Create Plan' },
                { prompt: 'Get more context', label: '📚 More Context' }
            );
            break;

        case DirectorSlashCommand.Ask:
        default:
            followUps.push(
                { prompt: 'Explain in more detail', label: '📖 More Details' },
                { prompt: 'Show me an example', label: '💡 Example' }
            );
            break;
    }

    // Generic follow-ups
    followUps.push(
        { prompt: '/help', label: '❓ Help' }
    );

    // Add to stream (feature detection for API compatibility)
    // The followup method may not exist in all VS Code versions
    const streamWithFollowup = stream as unknown as { followup?: (followup: vscode.ChatFollowup) => void };
    if (streamWithFollowup.followup && typeof streamWithFollowup.followup === 'function') {
        followUps.forEach(followUp => streamWithFollowup.followup!(followUp));
    }
}
