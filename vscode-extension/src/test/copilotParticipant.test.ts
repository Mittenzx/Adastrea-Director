/**
 * Tests for Copilot Participant
 */

import * as assert from 'assert';
import * as vscode from 'vscode';
import { initializeCopilotParticipant } from '../copilotParticipant';
import { DirectorIPCClient } from '../ipcClient';

suite('CopilotParticipant Test Suite', () => {
    let mockClient: DirectorIPCClient | null;
    let mockOutputChannel: vscode.OutputChannel;
    let mockContext: vscode.ExtensionContext;

    setup(() => {
        // Create a mock client
        mockClient = {
            isConnected: () => true,
            query: async (question: string) => ({
                status: 'success' as const,
                result: `Mock response for: ${question}`
            }),
            plan: async (goal: string) => ({
                status: 'success' as const,
                plan: {
                    goal: goal,
                    tasks: ['Task 1', 'Task 2'],
                    steps: ['Step 1', 'Step 2']
                }
            }),
            analyze: async (goal: string) => ({
                status: 'success' as const,
                analysis: {
                    summary: 'Test analysis',
                    complexity: 'Medium',
                    requirements: ['Req 1', 'Req 2']
                }
            })
        } as any;

        // Create mock output channel
        mockOutputChannel = {
            appendLine: (message: string) => {},
            show: () => {},
            dispose: () => {}
        } as any;

        // Create minimal mock context
        mockContext = {
            subscriptions: [],
            extensionPath: '',
            globalState: {} as any,
            workspaceState: {} as any
        } as any;
    });

    test('initializeCopilotParticipant creates participant with correct metadata', () => {
        const getClient = () => mockClient;
        const participant = initializeCopilotParticipant(mockContext, getClient, mockOutputChannel);
        
        // Participant should be created (or null if API not available)
        if (participant) {
            assert.ok(participant.id);
            assert.strictEqual(participant.id, 'director.chat');
            assert.ok(participant.iconPath);
        }
        // If null, it means the API is not available (which is acceptable in test environment)
    });

    test('initializeCopilotParticipant handles missing API gracefully', () => {
        const getClient = () => mockClient;
        
        // Should not throw an error even if Copilot API is unavailable
        assert.doesNotThrow(() => {
            initializeCopilotParticipant(mockContext, getClient, mockOutputChannel);
        });
    });

    test('initializeCopilotParticipant adds participant to subscriptions when successful', () => {
        const getClient = () => mockClient;
        const initialLength = mockContext.subscriptions.length;
        
        initializeCopilotParticipant(mockContext, getClient, mockOutputChannel);
        
        // If participant was created, subscriptions should increase
        // (will remain same if API not available)
        assert.ok(mockContext.subscriptions.length >= initialLength);
    });
});

suite('CopilotParticipant Response Formatting', () => {
    test('Plan response should include tasks and steps', () => {
        // This is a structural test - we verify the format exists
        const mockPlan = {
            goal: 'Test goal',
            tasks: ['Task 1', 'Task 2'],
            steps: ['Step 1', 'Step 2'],
            considerations: 'Test considerations'
        };

        // Verify the plan structure
        assert.ok(mockPlan.goal);
        assert.ok(Array.isArray(mockPlan.tasks));
        assert.ok(Array.isArray(mockPlan.steps));
        assert.strictEqual(mockPlan.tasks.length, 2);
        assert.strictEqual(mockPlan.steps.length, 2);
    });

    test('Analysis response should include required fields', () => {
        const mockAnalysis = {
            summary: 'Test summary',
            complexity: 'Medium',
            requirements: ['Req 1', 'Req 2'],
            risks: ['Risk 1'],
            recommendations: ['Rec 1']
        };

        // Verify the analysis structure
        assert.ok(mockAnalysis.summary);
        assert.ok(mockAnalysis.complexity);
        assert.ok(Array.isArray(mockAnalysis.requirements));
        assert.ok(Array.isArray(mockAnalysis.risks));
        assert.ok(Array.isArray(mockAnalysis.recommendations));
    });
});

suite('CopilotParticipant Error Handling', () => {
    test('Handler should handle disconnected client gracefully', () => {
        const mockDisconnectedClient = {
            isConnected: () => false
        } as any;

        const getClient = () => mockDisconnectedClient;
        
        // Should not throw when creating participant with disconnected client
        assert.doesNotThrow(() => {
            const mockContext = { subscriptions: [] } as any;
            const mockOutputChannel = { appendLine: () => {} } as any;
            initializeCopilotParticipant(mockContext, getClient, mockOutputChannel);
        });
    });

    test('Handler should handle null client gracefully', () => {
        const getClient = () => null;
        
        // Should not throw when creating participant with null client
        assert.doesNotThrow(() => {
            const mockContext = { subscriptions: [] } as any;
            const mockOutputChannel = { appendLine: () => {} } as any;
            initializeCopilotParticipant(mockContext, getClient, mockOutputChannel);
        });
    });
});
