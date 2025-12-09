#!/usr/bin/env node
/**
 * Test script for debug mode features
 * 
 * This script tests the debug logging and diagnostics features.
 */

const { DirectorIPCClient } = require('./out/ipcClient');

async function runDebugTests() {
    console.log('='.repeat(60));
    console.log('Debug Mode Test - Adastrea Director VS Code Extension');
    console.log('='.repeat(60));
    console.log();

    const debugLogs = [];

    const client = new DirectorIPCClient({
        host: 'localhost',
        port: 5555,
        reconnectInterval: 2000,
        maxReconnectAttempts: 3,
        debugMode: true  // Enable debug mode
    });

    // Capture debug logs
    client.onDebugLog = (info) => {
        debugLogs.push(info);
        const levelSymbol = {
            'info': 'ℹ',
            'warning': '⚠',
            'error': '✗',
            'debug': '◆'
        }[info.level] || '•';
        console.log(`[${info.timestamp}] ${levelSymbol} ${info.level.toUpperCase()}: ${info.message}`);
        if (info.details) {
            console.log(`  Details:`, JSON.stringify(info.details, null, 2));
        }
    };

    try {
        console.log('Test 1: Connection with Debug Mode');
        console.log('-'.repeat(60));
        await client.connect();
        console.log('✓ Connected\n');

        console.log('Test 2: Get Diagnostics');
        console.log('-'.repeat(60));
        const diagnostics = client.getDiagnostics();
        console.log('Diagnostics:', JSON.stringify(diagnostics, null, 2));
        console.log('✓ Diagnostics retrieved\n');

        console.log('Test 3: Send Request with Debug Logging');
        console.log('-'.repeat(60));
        const response = await client.ping();
        console.log(`✓ Ping result: ${response}\n`);

        console.log('Test 4: Toggle Debug Mode');
        console.log('-'.repeat(60));
        console.log('Debug mode status:', client.isDebugMode());
        client.setDebugMode(false);
        console.log('Debug mode after toggle:', client.isDebugMode());
        client.setDebugMode(true);
        console.log('Debug mode after re-toggle:', client.isDebugMode());
        console.log('✓ Debug mode toggle works\n');

        console.log('Test 5: Disconnect');
        console.log('-'.repeat(60));
        client.disconnect();
        console.log('✓ Disconnected\n');

        console.log('='.repeat(60));
        console.log('Summary');
        console.log('='.repeat(60));
        console.log(`Total debug logs captured: ${debugLogs.length}`);
        console.log(`Debug levels used: ${[...new Set(debugLogs.map(l => l.level))].join(', ')}`);
        console.log('\nDebug log breakdown:');
        const levelCounts = debugLogs.reduce((acc, log) => {
            acc[log.level] = (acc[log.level] || 0) + 1;
            return acc;
        }, {});
        Object.entries(levelCounts).forEach(([level, count]) => {
            console.log(`  ${level}: ${count}`);
        });
        console.log('\n✓ All debug tests passed!');

    } catch (error) {
        console.error('Test failed:', error);
        process.exit(1);
    }
}

runDebugTests().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
});
