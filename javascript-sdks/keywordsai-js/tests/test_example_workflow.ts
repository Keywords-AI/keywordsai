import { KeywordsAITelemetry } from '@keywordsai/tracing';
import OpenAI from 'openai';
import * as dotenv from 'dotenv';

const result = dotenv.config({ override: true, path: '.env' });
console.log(result);

// Initialize clients
// Make sure to set these environment variables or pass them directly
const keywordsAI = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY || "",
    baseUrl: process.env.KEYWORDSAI_BASE_URL || "",
    appName: 'test-app',
    disableBatch: true  // For testing, disable batching
});

const openai = new OpenAI();

// Step 1: Basic Task
// This demonstrates a simple LLM call wrapped in a task
async function createJoke() {
    return await keywordsAI.withTask(
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

// Step 2: Task with Parameters
// Shows how to add custom identifiers and metadata to spans
async function translateJoke(joke: string) {
    return await keywordsAI.withTask(
        { 
            name: 'joke_translation',
        },
        async () => {
            const completion = await openai.chat.completions.create({
                messages: [
                    { 
                        role: 'user', 
                        content: `Translate this joke to pirate speak: ${joke}` 
                    }
                ],
                model: 'gpt-3.5-turbo'
            });
            return completion.choices[0].message.content;
        }
    );
}

// Step 3: Simple Workflow
// Demonstrates how to combine multiple tasks into a workflow
async function jokeWorkflow() {
    return await keywordsAI.withWorkflow(
        { name: 'pirate_joke_workflow' },
        async () => {
            const joke = await createJoke();
            const pirateJoke = await translateJoke(joke as string);
            return pirateJoke;
        }
    );
}

// Step 4: Complex Workflow with Multiple Tasks
// Shows parallel execution and error handling
async function audienceReaction(joke: string) {
    return await keywordsAI.withWorkflow(
        { name: 'audience_reaction' },
        async () => {
            // Run reactions in parallel
            const [laughs, applause] = await Promise.all([
                keywordsAI.withTask(
                    { name: 'audience_laughs' },
                    async () => {
                        const completion = await openai.chat.completions.create({
                            messages: [{ 
                                role: 'user', 
                                content: `React to this joke with laughter: ${joke}` 
                            }],
                            model: 'gpt-3.5-turbo'
                        });
                        return completion.choices[0].message.content;
                    }
                ),
                keywordsAI.withTask(
                    { name: 'audience_applause' },
                    async () => {
                        const completion = await openai.chat.completions.create({
                            messages: [{ 
                                role: 'user', 
                                content: 'Generate applause sounds' 
                            }],
                            model: 'gpt-3.5-turbo'
                        });
                        return completion.choices[0].message.content;
                    }
                )
            ]);

            return `${laughs}\n${applause}`;
        }
    );
}

// Step 5: Complete Example
// Combines everything into a final workflow
async function completeJokeExperience() {
    return await keywordsAI.withWorkflow(
        { 
            name: 'complete_joke_experience',
        },
        async () => {
            const pirateJoke = await jokeWorkflow();
            const reaction = await audienceReaction(pirateJoke as string);
            
            // Add non-LLM task
            await keywordsAI.withTask(
                { name: 'logging' },
                async () => {
                    console.log('Joke:', pirateJoke);
                    console.log('Reaction:', reaction);
                }
            );

            return {
                joke: pirateJoke,
                reaction: reaction
            };
        }
    );
}

// Run the example
async function main() {
    try {
        const result = await completeJokeExperience();
        console.log('Final result:', result);
    } catch (error) {
        console.error('Error:', error);
    }
}

main();