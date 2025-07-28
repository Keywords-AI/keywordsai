import { KeywordsAITelemetry  } from '../src/main';
import OpenAI from 'openai';
import * as dotenv from 'dotenv';

dotenv.config({ override: true, path: '.env' });

// Initialize KeywordsAI first
const keywordsAI = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY || "",
    // baseURL: process.env.KEYWORDSAI_BASE_URL || "",
    baseURL: "https://webhook.site/5d2f431e-1ed6-4639-bd6c-dc19de391a50/chat/completions",
    appName: 'test-app',
    disableBatch: true,  // For testing, disable batching
});

// Wait for initialization to complete before creating OpenAI client
await keywordsAI.initialize();

// Now create the OpenAI client - it should be instrumented
const openai = new OpenAI();

// Step 1: Basic Task
// This demonstrates a simple LLM call wrapped in a task
async function createJoke() {
    return await keywordsAI.withWorkflow(
        { name: 'joke_creation' },
        async () => {
            const completion = await openai.chat.completions.create({
                messages: [{ role: 'user', content: 'Tell me a joke about TypeScript' }],
                model: 'gpt-3.5-turbo',
                temperature: 0.7
            });
            return completion.choices[0].message.content;
        }
    );
}

async function main() {
    console.log("🚀 Starting KeywordsAI tracing test...");
    
    const joke = await createJoke();
    console.log("🎭 Generated joke:", joke);
    
    // Wait a moment for traces to be sent
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    console.log("✅ Test completed successfully!");
    await keywordsAI.shutdown();
}

main().catch(console.error);