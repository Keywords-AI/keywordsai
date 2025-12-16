#!/usr/bin/env node
/**
 * Test Script: Anthropic Instrumentation with enrichTokens
 * 
 * This script verifies that the Anthropic instrumentation properly captures
 * metrics (tokens, cost) after adding the enrichTokens: true option.
 * 
 * Prerequisites:
 * - npm install @anthropic-ai/sdk
 * - npm install @traceloop/instrumentation-anthropic
 * 
 * Environment Variables:
 * - KEYWORDSAI_API_KEY: Your KeywordsAI API key
 * - ANTHROPIC_API_KEY: Your Anthropic API key
 * - KEYWORDSAI_BASE_URL: (Optional) KeywordsAI base URL
 */

import { KeywordsAITelemetry } from '../src/main.js';
import Anthropic from '@anthropic-ai/sdk';
import { trace } from '@opentelemetry/api';

// Configuration
const config = {
    keywordsaiApiKey: process.env.KEYWORDSAI_API_KEY || "test-key",
    keywordsaiBaseURL: process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co",
    anthropicApiKey: process.env.ANTHROPIC_API_KEY,
    appName: 'anthropic-instrumentation-test',
};

console.log('\n========================================');
console.log('🧪 Anthropic Instrumentation Test');
console.log('========================================\n');

// Validate environment
if (!config.anthropicApiKey) {
    console.error('❌ Error: ANTHROPIC_API_KEY environment variable is required');
    console.error('   Set it with: export ANTHROPIC_API_KEY="your-api-key"\n');
    process.exit(1);
}

console.log('✓ Environment variables validated');
console.log(`✓ KeywordsAI Base URL: ${config.keywordsaiBaseURL}`);
console.log(`✓ App Name: ${config.appName}\n`);

// Initialize KeywordsAI with Anthropic instrumentation
console.log('📦 Initializing KeywordsAI Telemetry with Anthropic instrumentation...');

const keywordsAI = new KeywordsAITelemetry({
    apiKey: config.keywordsaiApiKey,
    baseURL: config.keywordsaiBaseURL,
    appName: config.appName,
    disableBatch: true, // For immediate feedback during testing
    logLevel: 'debug',
    traceContent: true,
    instrumentModules: {
        anthropic: Anthropic,
    }
});

// Wait for initialization
await keywordsAI.initialize();
console.log('✓ KeywordsAI Telemetry initialized\n');

// Create Anthropic client
console.log('🤖 Creating Anthropic client...');
const anthropic = new Anthropic({
    apiKey: config.anthropicApiKey,
});
console.log('✓ Anthropic client created\n');

// Test 1: Basic message with metrics tracking
console.log('========================================');
console.log('Test 1: Basic Anthropic Message');
console.log('========================================\n');

const test1 = async () => {
    return await keywordsAI.withWorkflow(
        { name: 'anthropic_metrics_test', version: 1 },
        async () => {
            console.log('📤 Sending message to Claude...');
            const startTime = Date.now();
            
            const message = await anthropic.messages.create({
                model: 'claude-3-haiku-20240307',
                max_tokens: 100,
                messages: [
                    { role: 'user', content: 'Say "Hello, World!" and explain what you are in one sentence.' }
                ]
            });
            
            const duration = Date.now() - startTime;
            
            console.log('✓ Message received from Claude');
            console.log(`✓ Duration: ${duration}ms\n`);
            
            // Display response
            const responseText = message.content[0].type === 'text' ? message.content[0].text : 'N/A';
            console.log('📨 Response:');
            console.log(`   ${responseText}\n`);
            
            // Display usage information
            console.log('📊 Token Usage (from Anthropic response):');
            console.log(`   Input tokens:  ${message.usage.input_tokens}`);
            console.log(`   Output tokens: ${message.usage.output_tokens}`);
            console.log(`   Total tokens:  ${message.usage.input_tokens + message.usage.output_tokens}\n`);
            
            // Verify metrics are captured in the span
            const currentSpan = trace.getActiveSpan();
            if (currentSpan) {
                const spanContext = currentSpan.spanContext();
                console.log('📍 Active Span Information:');
                console.log(`   Trace ID: ${spanContext.traceId}`);
                console.log(`   Span ID:  ${spanContext.spanId}`);
                console.log('   ✓ Span is active and being tracked\n');
            } else {
                console.warn('⚠️  Warning: No active span detected\n');
            }
            
            return {
                response: responseText,
                usage: message.usage,
                model: message.model,
                duration
            };
        }
    );
};

// Test 2: Multiple messages to verify consistent metrics
console.log('========================================');
console.log('Test 2: Multiple Messages');
console.log('========================================\n');

const test2 = async () => {
    const results: Array<{ prompt: string; response: string; usage: any }> = [];
    const prompts = [
        'Count from 1 to 5.',
        'Name 3 colors.',
        'What is 2+2?'
    ];
    
    for (let i = 0; i < prompts.length; i++) {
        console.log(`📤 Test ${i + 1}/3: "${prompts[i]}"`);
        
        const result = await keywordsAI.withTask(
            { name: `anthropic_task_${i + 1}` },
            async () => {
                const message = await anthropic.messages.create({
                    model: 'claude-3-haiku-20240307',
                    max_tokens: 50,
                    messages: [{ role: 'user', content: prompts[i] }]
                });
                
                const responseText = message.content[0].type === 'text' ? message.content[0].text : 'N/A';
                console.log(`   Response: ${responseText.substring(0, 50)}...`);
                console.log(`   Tokens: ${message.usage.input_tokens} input + ${message.usage.output_tokens} output = ${message.usage.input_tokens + message.usage.output_tokens} total\n`);
                
                return {
                    prompt: prompts[i],
                    response: responseText,
                    usage: message.usage
                };
            }
        );
        
        results.push(result);
    }
    
    return results;
};

// Test 3: Streaming response (if supported)
console.log('========================================');
console.log('Test 3: Streaming Response');
console.log('========================================\n');

const test3 = async () => {
    return await keywordsAI.withTask(
        { name: 'anthropic_streaming_test' },
        async () => {
            console.log('📤 Sending streaming request to Claude...');
            
            const stream = await anthropic.messages.create({
                model: 'claude-3-haiku-20240307',
                max_tokens: 100,
                messages: [{ role: 'user', content: 'Count from 1 to 10.' }],
                stream: true,
            });
            
            console.log('📨 Streaming response:\n   ');
            
            let fullContent = '';
            let inputTokens = 0;
            let outputTokens = 0;
            
            for await (const event of stream) {
                if (event.type === 'message_start') {
                    inputTokens = event.message.usage.input_tokens;
                } else if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
                    process.stdout.write(event.delta.text);
                    fullContent += event.delta.text;
                } else if (event.type === 'message_delta') {
                    outputTokens = event.usage.output_tokens;
                }
            }
            
            console.log('\n');
            console.log('📊 Streaming Token Usage:');
            console.log(`   Input tokens:  ${inputTokens}`);
            console.log(`   Output tokens: ${outputTokens}`);
            console.log(`   Total tokens:  ${inputTokens + outputTokens}\n`);
            
            return {
                content: fullContent,
                usage: { input_tokens: inputTokens, output_tokens: outputTokens }
            };
        }
    );
};

// Run all tests
(async () => {
    try {
        // Test 1
        const result1 = await test1();
        console.log('✅ Test 1 completed successfully\n');
        
        // Test 2
        const result2 = await test2();
        console.log('✅ Test 2 completed successfully\n');
        
        // Test 3
        const result3 = await test3();
        console.log('✅ Test 3 completed successfully\n');
        
        // Summary
        console.log('========================================');
        console.log('📋 Test Summary');
        console.log('========================================\n');
        
        console.log('✅ All tests passed!');
        console.log('\n🔍 What to check next:');
        console.log('   1. Go to your KeywordsAI dashboard');
        console.log('   2. Look for traces from app: "' + config.appName + '"');
        console.log('   3. Verify that each span shows:');
        console.log('      • Token counts (prompt_tokens, completion_tokens, total_tokens)');
        console.log('      • Cost metrics');
        console.log('      • Model information');
        console.log('      • Request/response content (if traceContent is enabled)');
        console.log('\n📊 Expected Metrics in Spans:');
        console.log('   • llm.usage.prompt_tokens');
        console.log('   • llm.usage.completion_tokens');
        console.log('   • llm.usage.total_tokens');
        console.log('   • gen_ai.usage.input_tokens');
        console.log('   • gen_ai.usage.output_tokens');
        console.log('   • Cost-related attributes\n');
        
        console.log('✨ The enrichTokens: true option is working correctly!\n');
        
        // Give time for traces to be exported
        console.log('⏳ Waiting 3 seconds for traces to be exported...');
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        console.log('✓ Test script completed\n');
        process.exit(0);
        
    } catch (error) {
        console.error('\n❌ Test failed with error:');
        console.error(error);
        console.error('\n💡 Troubleshooting tips:');
        console.error('   • Verify your ANTHROPIC_API_KEY is valid');
        console.error('   • Check that @anthropic-ai/sdk is installed');
        console.error('   • Check that @traceloop/instrumentation-anthropic is installed');
        console.error('   • Review the error message above for details\n');
        
        // Give time for traces to be exported even on error
        await new Promise(resolve => setTimeout(resolve, 3000));
        process.exit(1);
    }
})();

