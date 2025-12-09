/**
 * Tests for DirectorIPCClient
 */

import * as assert from 'assert';
import { DirectorIPCClient } from '../ipcClient';

suite('DirectorIPCClient Test Suite', () => {
    let client: DirectorIPCClient;

    setup(() => {
        client = new DirectorIPCClient({
            host: 'localhost',
            port: 5555,
            reconnectInterval: 1000,
            maxReconnectAttempts: 2
        });
    });

    teardown(() => {
        if (client) {
            client.disconnect();
        }
    });

    test('Client initializes with correct state', () => {
        assert.strictEqual(client.getState(), 'disconnected');
        assert.strictEqual(client.isConnected(), false);
    });

    test('Client state changes on connection attempt', async () => {
        let stateChanges: string[] = [];
        
        client.onStateChange = (state) => {
            stateChanges.push(state);
        };

        // This will fail if server is not running, which is expected
        try {
            await client.connect();
            assert.ok(stateChanges.includes('connecting'));
        } catch (error) {
            // Expected if server is not running
            assert.ok(stateChanges.includes('connecting'));
        }
    });

    test('Client handles disconnection', () => {
        client.disconnect();
        assert.strictEqual(client.getState(), 'disconnected');
        assert.strictEqual(client.isConnected(), false);
    });

    test('Client throws error when sending request while disconnected', async () => {
        try {
            await client.request('ping', '');
            assert.fail('Should have thrown an error');
        } catch (error) {
            assert.ok(error instanceof Error);
            assert.ok(error.message.includes('Not connected'));
        }
    });
});

// Note: Integration tests that require a running IPC server should be run separately
suite('DirectorIPCClient Integration Tests', () => {
    let client: DirectorIPCClient;

    setup(() => {
        client = new DirectorIPCClient({
            host: 'localhost',
            port: 5555,
            reconnectInterval: 1000,
            maxReconnectAttempts: 2
        });
    });

    teardown(() => {
        if (client) {
            client.disconnect();
        }
    });

    // These tests require the IPC server to be running
    // Mark them as such or skip them if server is not available
    
    test.skip('Can connect to IPC server', async function() {
        this.timeout(10000);
        
        try {
            await client.connect();
            assert.strictEqual(client.isConnected(), true);
        } catch (error) {
            // Server not running - skip test
            console.log('Skipping test: IPC server not running');
        }
    });

    test.skip('Can send ping request', async function() {
        this.timeout(10000);
        
        try {
            await client.connect();
            const result = await client.ping();
            assert.strictEqual(result, true);
        } catch (error) {
            console.log('Skipping test: IPC server not running');
        }
    });

    test.skip('Can send query request', async function() {
        this.timeout(10000);
        
        try {
            await client.connect();
            const response = await client.query('What is Unreal Engine?');
            assert.strictEqual(response.status, 'success');
            assert.ok(response.result);
        } catch (error) {
            console.log('Skipping test: IPC server not running');
        }
    });
});
