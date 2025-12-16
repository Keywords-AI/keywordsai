#!/usr/bin/env node
/**
 * Anthropic (Claude) Integration Example
 * 
 * This example shows how to trace Anthropic API calls with KeywordsAI.
 * Use case: Building a content summarization tool with Claude
 * 
 * Setup:
 * 1. npm install @anthropic-ai/sdk @traceloop/instrumentation-anthropic
 * 2. Set ANTHROPIC_API_KEY and KEYWORDSAI_API_KEY environment variables
 * 3. Run: tsx tests/test_anthropic_instrumentation.ts
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

// Initialize tracing
const kai = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY,
    appName: 'content-summarizer',
    instrumentModules: {
        anthropic: Anthropic  // Enable Anthropic tracing
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
    return await kai.withTask(
        { name: 'summarize_content' },
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
    return await kai.withTask(
        { name: 'generate_ideas' },
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

        // Example 3: Streaming response
        console.log('📨 Example 3: Streaming Response');
        await kai.withTask(
            { name: 'stream_story' },
            async () => {
                const stream = await anthropic.messages.create({
                    model: 'claude-3-haiku-20240307',
                    max_tokens: 150,
                    messages: [{ 
                        role: 'user', 
                        content: 'Write a haiku about coding' 
                    }],
                    stream: true
                });

                process.stdout.write('Haiku: ');
                for await (const event of stream) {
                    if (event.type === 'content_block_delta' && 
                        event.delta.type === 'text_delta') {
                        process.stdout.write(event.delta.text);
                    }
                }
                console.log('\n✓ Streaming complete\n');
            }
        );

        console.log('✅ All examples completed!');
        console.log('\n📊 View traces at: https://platform.keywordsai.co/');
        
        // Allow time for trace export
        await new Promise(resolve => setTimeout(resolve, 2000));
        
    } catch (error) {
        console.error('\n❌ Error:', error instanceof Error ? error.message : error);
        console.error('\n💡 Make sure you have installed the Anthropic instrumentation:');
        console.error('   npm install @traceloop/instrumentation-anthropic\n');
        process.exit(1);
    }
})();
