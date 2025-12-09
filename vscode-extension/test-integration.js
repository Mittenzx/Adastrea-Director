#!/usr/bin/env node
/**
 * Integration test script for the VS Code extension IPC client
 * 
 * This script tests the IPC client against a running Director IPC server.
 * Run this script after starting the IPC server on port 5555.
 */

const { DirectorIPCClient } = require('./out/ipcClient');

async function runTests() {
    console.log('='.repeat(60));
    console.log('Adastrea Director VS Code Extension - Integration Tests');
    console.log('='.repeat(60));
    console.log();

    const client = new DirectorIPCClient({
        host: 'localhost',
        port: 5555,
        reconnectInterval: 2000,
        maxReconnectAttempts: 3
    });

    let passed = 0;
    let failed = 0;

    // Test 1: Connection
    console.log('Test 1: Connection');
    try {
        await client.connect();
        if (client.isConnected()) {
            console.log('  ✓ Connected successfully');
            passed++;
        } else {
            console.log('  ✗ Failed to connect');
            failed++;
            return;
        }
    } catch (error) {
        console.log('  ✗ Connection error:', error.message);
        console.log('  Make sure the IPC server is running:');
        console.log('  python Plugins/AdastreaDirector/Python/ipc_server.py --port 5555');
        failed++;
        return;
    }
    console.log();

    // Test 2: Ping
    console.log('Test 2: Health Check (Ping)');
    try {
        const result = await client.ping();
        if (result === true) {
            console.log('  ✓ Ping successful');
            passed++;
        } else {
            console.log('  ✗ Ping failed');
            failed++;
        }
    } catch (error) {
        console.log('  ✗ Ping error:', error.message);
        failed++;
    }
    console.log();

    // Test 3: Query
    console.log('Test 3: Query Request');
    try {
        const response = await client.query('What is Unreal Engine?');
        if (response.status === 'success' && response.result) {
            console.log('  ✓ Query successful');
            console.log('  Response:', response.result.substring(0, 100) + '...');
            passed++;
        } else {
            console.log('  ✗ Query failed:', response.error || 'Unknown error');
            failed++;
        }
    } catch (error) {
        console.log('  ✗ Query error:', error.message);
        failed++;
    }
    console.log();

    // Test 4: Plan
    console.log('Test 4: Plan Request');
    try {
        const response = await client.plan('Create a player movement system');
        if (response.status === 'success' && response.plan) {
            console.log('  ✓ Plan generation successful');
            passed++;
        } else {
            console.log('  ✗ Plan failed:', response.error || 'Unknown error');
            failed++;
        }
    } catch (error) {
        console.log('  ✗ Plan error:', error.message);
        failed++;
    }
    console.log();

    // Test 5: Metrics
    console.log('Test 5: Metrics Request');
    try {
        const response = await client.getMetrics();
        if (response.status === 'success') {
            console.log('  ✓ Metrics retrieved successfully');
            if (response.total_requests !== undefined) {
                console.log(`  Total requests: ${response.total_requests}`);
            }
            passed++;
        } else {
            console.log('  ✗ Metrics failed:', response.error || 'Unknown error');
            failed++;
        }
    } catch (error) {
        console.log('  ✗ Metrics error:', error.message);
        failed++;
    }
    console.log();

    // Disconnect
    console.log('Disconnecting...');
    client.disconnect();
    console.log();

    // Summary
    console.log('='.repeat(60));
    console.log('Test Results');
    console.log('='.repeat(60));
    console.log(`Passed: ${passed}`);
    console.log(`Failed: ${failed}`);
    console.log(`Total:  ${passed + failed}`);
    console.log('='.repeat(60));

    process.exit(failed > 0 ? 1 : 0);
}

runTests().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
});
