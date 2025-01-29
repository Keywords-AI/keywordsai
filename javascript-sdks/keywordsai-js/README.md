# Keywords AI JS Tracing
This tutorial demonstrates how to build and trace complex LLM workflows using KeywordsAI Tracing. We'll create an example that generates jokes, translates them to pirate language, and simulates audience reactions - all while capturing detailed telemetry of our LLM calls.

## Installation

Using npm:  
```bash
npm install @keywordsai/tracing
```

Using yarn:
```bash
yarn add @keywordsai/tracing
```

## Tutorial

### Step 1: Initialize KeywordsAI Telemetry
```typescript
import { KeywordsAITelemetry } from '@keywordsai/tracing';
import OpenAI from 'openai';

// Initialize clients
// Make sure to set these environment variables or pass them directly
const keywordsAi = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY || "",
    appName: 'test-app',
    disableBatch: true  // For testing, disable batching
});

const openai = new OpenAI();
```

### Step 2: Basic Task
This demonstrates a simple LLM call wrapped in a task
```typescript
async function createJoke() {
    return await keywordsAi.withTask(
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

// One more task
async function translateJoke(joke: string) {
    return await keywordsAi.withTask(
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
```

### Step 3: Simple Workflow combines multiple tasks
Demonstrates how to combine multiple tasks into a workflow
```typescript
async function jokeWorkflow() {
    return await keywordsAi.withWorkflow(
        { name: 'pirate_joke_workflow' },
        async () => {
            const joke = await createJoke();
            const pirateJoke = await translateJoke(joke);
            return pirateJoke;
        }
    );
}
```

### Step 4: Create a separate workflow for audience reaction
Shows parallel execution and error handling
```typescript
async function audienceReaction(joke: string) {
    return await keywordsAi.withWorkflow(
        { name: 'audience_reaction' },
        async () => {
            // Run reactions in parallel
            const [laughs, applause] = await Promise.all([
                keywordsAi.withTask(
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
                keywordsAi.withTask(
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
```

### Step 5: Complete Example
Combines everything into a final workflow
```typescript
async function completeJokeExperience() {
    return await keywordsAi.withWorkflow(
        { 
            name: 'complete_joke_experience',
        },
        async () => {
            const pirateJoke = await jokeWorkflow();
            const reaction = await audienceReaction(pirateJoke);
            
            // Add non-LLM task
            await keywordsAi.withTask(
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
```

### Step 6: Run the example
```typescript
async function main() {
    try {
        const result = await completeJokeExperience();
        console.log('Final result:', result);
    } catch (error) {
        console.error('Error:', error);
    }
}

main();
```

