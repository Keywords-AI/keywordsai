#!/usr/bin/env node
/**
 * Anthropic (Claude) Integration Example
 * 
 * ⚠️  VERSION REQUIREMENT: This example requires @anthropic-ai/sdk@^0.20.0
 * 
 * Compatibility:
 * ✅ @anthropic-ai/sdk@^0.20.0 - Fully working with all metrics
 * ❌ @anthropic-ai/sdk@0.71+ - Not compatible (spans won't be created)
 * 
 * The @traceloop/instrumentation-anthropic package officially supports SDK 0.9.1+,
 * but SDK v0.71+ introduced breaking changes that prevent instrumentation from working.
 * 
 * This example shows how to trace Anthropic API calls with KeywordsAI.
 * Use case: Building a content summarization tool with Claude
 * 
 * Setup:
 * 1. Use compatible SDK version (already in package.json):
 *    yarn add -D @anthropic-ai/sdk@^0.20.0 @traceloop/instrumentation-anthropic
 * 2. Set ANTHROPIC_API_KEY and KEYWORDSAI_API_KEY environment variables
 * 3. Run: tsx tests/test_anthropic_instrumentation.ts
 * 
 * Alternative:
 * - Use OpenAI instead (fully supported with latest SDK versions)
 * - See examples/openai-integration-test.ts
 */

import { KeywordsAITelemetry } from '../src/main.js';
import Anthropic from '@anthropic-ai/sdk';
import * as dotenv from 'dotenv';

dotenv.config({ override: true });

// Validate environment
if (!process.env.ANTHROPIC_API_KEY) {
    console.error('❌ Missing ANTHROPIC_API_KEY');
    console.error('   Set it with: export ANTHROPIC_API_KEY="your-key"');
    process.exit(1);
}

console.log('\n🚀 Content Summarization with Claude\n');

// Initialize tracing with MANUAL instrumentation
const kai = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY,
    baseURL: process.env.KEYWORDSAI_BASE_URL,
    appName: 'content-summarizer',
    traceContent: true,
    logLevel: 'debug',  // Enable debug logging to see spans
    disableBatch: true,  // Immediate export for testing
    instrumentModules: {
        anthropic: Anthropic  // Manual instrumentation
    }
});

await kai.initialize();
console.log('✓ Tracing initialized\n');

// Create Anthropic client
const anthropic = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY
});

// Example: Summarize content with tracing
async function summarizeContent(text: string): Promise<string> {
    // Call Anthropic directly inside workflow (no intermediate task)
    return await kai.withWorkflow(
        { name: 'summarize_workflow', version: 1 },
        async () => {
            const response = await anthropic.messages.create({
                model: 'claude-3-haiku-20240307',
                max_tokens: 200,
                messages: [{
                    role: 'user',
                    content: `Summarize this in 2-3 sentences:\n\n${text}`
                }]
            });

            return response.content[0].type === 'text' 
                ? response.content[0].text 
                : '';
        }
    );
}

// Example: Generate creative content
async function generateIdeas(topic: string): Promise<string[]> {
    // Call Anthropic directly inside workflow (no intermediate task)
    return await kai.withWorkflow(
        { name: 'ideas_workflow', version: 1 },
        async () => {
            const response = await anthropic.messages.create({
                model: 'claude-3-haiku-20240307',
                max_tokens: 300,
                messages: [{
                    role: 'user',
                    content: `Generate 3 creative ideas about: ${topic}`
                }]
            });

            const text = response.content[0].type === 'text' 
                ? response.content[0].text 
                : '';
            
            return text.split('\n').filter(line => line.trim());
        }
    );
}

// Run examples
(async () => {
    try {
        // Example 1: Summarization
        console.log('📝 Example 1: Content Summarization');
        const article = `
            Artificial intelligence has transformed how we interact with technology.
            Machine learning models can now understand context, generate creative content,
            and assist with complex problem-solving tasks. The impact spans industries
            from healthcare to finance, education to entertainment.
        `;
        
        const summary = await summarizeContent(article);
        console.log('Summary:', summary);
        console.log('✓ Summarization complete\n');

        // Example 2: Idea generation
        console.log('💡 Example 2: Creative Ideas');
        const ideas = await generateIdeas('sustainable urban transportation');
        console.log('Ideas:');
        ideas.slice(0, 3).forEach(idea => console.log(`  • ${idea}`));
        console.log('✓ Ideas generated\n');

        // Example 3: Streaming response (skip due to known instrumentation issue)
        console.log('📨 Example 3: Streaming Response (skipped - known issue)');
        console.log('⚠️  Streaming is not fully supported by Anthropic instrumentation\n');

        console.log('✅ All examples completed!');
        console.log('\n📊 Check your backend for:');
        console.log('   - Workflow: summarize_workflow (with token metrics)');
        console.log('   - Workflow: ideas_workflow (with token metrics)');
        console.log('   - Each should have anthropic.chat spans with full usage data\n');
        
        // Shutdown to flush all traces
        await kai.shutdown();
        console.log('✓ Traces flushed to backend\n');
        
    } catch (error) {
        console.error('\n❌ Error:', error instanceof Error ? error.message : error);
        console.error('\n💡 Make sure you have installed the Anthropic instrumentation:');
        console.error('   npm install @traceloop/instrumentation-anthropic\n');
        process.exit(1);
    }
})();
