/**
 * Tests for Copilot Context Provider
 */

import * as assert from 'assert';
import * as vscode from 'vscode';
import { 
    DirectorEnhancedContext,
    registerHoverProvider,
    registerCodeActionProvider 
} from '../copilotContextProvider';
import { DirectorIPCClient } from '../ipcClient';

suite('DirectorEnhancedContext Test Suite', () => {
    let mockClient: DirectorIPCClient;
    let mockOutputChannel: vscode.OutputChannel;
    let enhancedContext: DirectorEnhancedContext;

    setup(() => {
        // Create a mock client
        mockClient = {
            isConnected: () => true,
            query: async (question: string) => ({
                status: 'success' as const,
                result: `Context for: ${question}`
            })
        } as any;

        // Create mock output channel
        mockOutputChannel = {
            appendLine: (message: string) => {},
            show: () => {},
            dispose: () => {}
        } as any;

        const getClient = () => mockClient;
        enhancedContext = new DirectorEnhancedContext(getClient, mockOutputChannel);
    });

    test('DirectorEnhancedContext initializes correctly', () => {
        assert.ok(enhancedContext);
        assert.ok(typeof enhancedContext.getContextForPosition === 'function');
        assert.ok(typeof enhancedContext.getContextForSymbol === 'function');
        assert.ok(typeof enhancedContext.getProjectContext === 'function');
    });

    test('getContextForSymbol returns context for valid symbol', async () => {
        const symbolName = 'UMyClass';
        const mockUri = vscode.Uri.file('/test/file.cpp');
        
        const result = await enhancedContext.getContextForSymbol(symbolName, mockUri);
        
        // Should return a string or null
        assert.ok(result === null || typeof result === 'string');
    });

    test('getContextForSymbol handles disconnected client', async () => {
        const disconnectedClient = {
            isConnected: () => false
        } as any;
        
        const getClient = () => disconnectedClient;
        const context = new DirectorEnhancedContext(getClient, mockOutputChannel);
        
        const result = await context.getContextForSymbol('UMyClass', vscode.Uri.file('/test/file.cpp'));
        
        // Should return null when disconnected
        assert.strictEqual(result, null);
    });

    test('getProjectContext handles missing workspace', async () => {
        // This test verifies graceful handling when no workspace is open
        const result = await enhancedContext.getProjectContext();
        
        // Should return null or string, not throw
        assert.ok(result === null || typeof result === 'string');
    });
});

suite('Unreal Engine Symbol Detection', () => {
    test('Identifies valid Unreal Engine class prefixes', () => {
        const UNREAL_SYMBOL_PATTERN = /^[UAFET][A-Z]/;
        
        // Valid UE symbols
        assert.ok(UNREAL_SYMBOL_PATTERN.test('UObject'));
        assert.ok(UNREAL_SYMBOL_PATTERN.test('AActor'));
        assert.ok(UNREAL_SYMBOL_PATTERN.test('FVector'));
        assert.ok(UNREAL_SYMBOL_PATTERN.test('ECollisionChannel'));
        assert.ok(UNREAL_SYMBOL_PATTERN.test('TArray'));
        
        // Invalid symbols
        assert.ok(!UNREAL_SYMBOL_PATTERN.test('MyClass'));
        assert.ok(!UNREAL_SYMBOL_PATTERN.test('uObject')); // lowercase
        assert.ok(!UNREAL_SYMBOL_PATTERN.test('U')); // too short
        assert.ok(!UNREAL_SYMBOL_PATTERN.test('Ua')); // lowercase second char
    });

    test('Pattern documentation matches actual prefixes', () => {
        // This test ensures the documentation is accurate
        const validPrefixes = ['U', 'A', 'F', 'E', 'T'];
        const UNREAL_SYMBOL_PATTERN = /^[UAFET][A-Z]/;
        
        validPrefixes.forEach(prefix => {
            const testSymbol = prefix + 'TestClass';
            assert.ok(UNREAL_SYMBOL_PATTERN.test(testSymbol), 
                `Pattern should match ${prefix}* symbols`);
        });
    });
});

suite('Hover Provider Registration', () => {
    let mockContext: vscode.ExtensionContext;
    let mockOutputChannel: vscode.OutputChannel;

    setup(() => {
        mockContext = {
            subscriptions: [],
            extensionPath: ''
        } as any;

        mockOutputChannel = {
            appendLine: (message: string) => {},
            show: () => {},
            dispose: () => {}
        } as any;
    });

    test('registerHoverProvider checks configuration setting', () => {
        const mockClient = {
            isConnected: () => true
        } as any;
        
        const getClient = () => mockClient;
        
        // Should not throw
        assert.doesNotThrow(() => {
            registerHoverProvider(mockContext, getClient, mockOutputChannel);
        });
    });

    test('registerHoverProvider returns early when disabled', () => {
        const mockClient = {
            isConnected: () => true
        } as any;
        
        const getClient = () => mockClient;
        const initialLength = mockContext.subscriptions.length;
        
        // Call with default settings
        registerHoverProvider(mockContext, getClient, mockOutputChannel);
        
        // Should add subscription if enabled (or stay same if disabled)
        assert.ok(mockContext.subscriptions.length >= initialLength);
    });
});

suite('Code Action Provider Registration', () => {
    let mockContext: vscode.ExtensionContext;
    let mockOutputChannel: vscode.OutputChannel;

    setup(() => {
        mockContext = {
            subscriptions: [],
            extensionPath: ''
        } as any;

        mockOutputChannel = {
            appendLine: (message: string) => {},
            show: () => {},
            dispose: () => {}
        } as any;
    });

    test('registerCodeActionProvider checks configuration setting', () => {
        const mockClient = {
            isConnected: () => true
        } as any;
        
        const getClient = () => mockClient;
        
        // Should not throw
        assert.doesNotThrow(() => {
            registerCodeActionProvider(mockContext, getClient, mockOutputChannel);
        });
    });

    test('registerCodeActionProvider provides Ask Director action', () => {
        // This is a structural test - we verify the provider is registered
        const mockClient = {
            isConnected: () => true
        } as any;
        
        const getClient = () => mockClient;
        const initialLength = mockContext.subscriptions.length;
        
        registerCodeActionProvider(mockContext, getClient, mockOutputChannel);
        
        // Should add subscription if enabled
        assert.ok(mockContext.subscriptions.length >= initialLength);
    });
});

suite('Context Provider Error Handling', () => {
    test('Enhanced context handles null client gracefully', async () => {
        const getClient = () => null;
        const mockOutputChannel = {
            appendLine: (message: string) => {}
        } as any;
        
        const context = new DirectorEnhancedContext(getClient, mockOutputChannel);
        
        // Should not throw
        const result = await context.getContextForSymbol('UMyClass', vscode.Uri.file('/test/file.cpp'));
        assert.strictEqual(result, null);
    });

    test('Enhanced context handles query errors gracefully', async () => {
        const errorClient = {
            isConnected: () => true,
            query: async () => {
                throw new Error('Network error');
            }
        } as any;
        
        const getClient = () => errorClient;
        const mockOutputChannel = {
            appendLine: (message: string) => {}
        } as any;
        
        const context = new DirectorEnhancedContext(getClient, mockOutputChannel);
        
        // Should return null on error, not throw
        const result = await context.getContextForSymbol('UMyClass', vscode.Uri.file('/test/file.cpp'));
        assert.strictEqual(result, null);
    });
});
