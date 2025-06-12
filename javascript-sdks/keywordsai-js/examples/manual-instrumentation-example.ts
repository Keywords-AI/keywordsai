import { KeywordsAITelemetry } from '../src/main';
import OpenAI from 'openai';
import Anthropic from '@anthropic-ai/sdk';

// Manual instrumentation approach - similar to Traceloop
// This is especially useful for Next.js and other environments where
// dynamic imports might not work properly

const keywordsAI = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDS_AI_API_KEY || "test-key",
    baseUrl: process.env.KEYWORDS_AI_BASE_URL || "https://api.keywordsai.co",
    appName: 'manual-instrumentation-example',
    disableBatch: true, // For development
    logLevel: 'info',
    traceContent: true,
    // Manual instrumentation - pass the actual imported modules
    instrumentModules: {
        openAI: OpenAI,
        anthropic: Anthropic,
        // Add other modules as needed:
        // azureOpenAI: AzureOpenAI,
        // cohere: Cohere,
        // bedrock: BedrockRuntime,
        // etc.
    }
});

// Wait for initialization to complete (optional but recommended)
await keywordsAI.initialize();

// Now create your clients - they will be automatically instrumented
const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

const anthropic = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY,
});

// Example workflow using both providers
const multiProviderWorkflow = async () => {
    return await keywordsAI.withWorkflow(
        { name: 'multi_provider_workflow', version: 1 },
        async () => {
            // OpenAI task
            const openaiResult = await keywordsAI.withTask(
                { name: 'openai_completion' },
                async () => {
                    const completion = await openai.chat.completions.create({
                        messages: [{ role: 'user', content: 'What is the capital of France?' }],
                        model: 'gpt-3.5-turbo',
                        temperature: 0.1
                    });
                    return completion.choices[0].message.content;
                }
            );

            // Anthropic task
            const anthropicResult = await keywordsAI.withTask(
                { name: 'anthropic_completion' },
                async () => {
                    const message = await anthropic.messages.create({
                        model: 'claude-3-sonnet-20240229',
                        max_tokens: 100,
                        messages: [{ role: 'user', content: 'What is the capital of Germany?' }]
                    });
                    return message.content[0].type === 'text' ? message.content[0].text : '';
                }
            );

            return {
                openai: openaiResult,
                anthropic: anthropicResult
            };
        }
    );
};

// Run the example
multiProviderWorkflow()
    .then(result => {
        console.log('Workflow completed:', result);
    })
    .catch(error => {
        console.error('Workflow failed:', error);
    });

export { keywordsAI, multiProviderWorkflow }; 