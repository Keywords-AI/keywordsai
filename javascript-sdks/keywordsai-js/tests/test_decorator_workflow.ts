import { KeywordsAITelemetry } from '../src/index';
import OpenAI from 'openai';
import * as dotenv from 'dotenv';

const result = dotenv.config({ override: true, path: '.env' });
console.log(result);

// Initialize clients
const keywordsAi = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY || "",
    baseUrl: process.env.KEYWORDSAI_BASE_URL || "",
    appName: 'test-decorator-app',
    disableBatch: true  // For testing, disable batching
});

// Enable OpenAI instrumentation
await keywordsAi.enableInstrumentation('openai');

const openai = new OpenAI();

// Step 1: Basic Task using decorator pattern
const createJoke = async () => {
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
};

// Step 2: Task with Parameters using decorator pattern
const translateJoke = async (joke: string) => {
    return await keywordsAi.withTask(
        { 
            name: 'joke_translation',
            version: 1,
            associationProperties: { 'joke_type': 'pirate' }
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
};

// Step 3: Simple Workflow using decorator pattern
const jokeWorkflow = async () => {
    return await keywordsAi.withWorkflow(
        { name: 'pirate_joke_workflow', version: 1 },
        async () => {
            const joke = await createJoke();
            const pirateJoke = await translateJoke(joke);
            return pirateJoke;
        }
    );
};

// Step 4: Complex Workflow with Multiple Tasks using decorator pattern
const audienceReaction = async (joke: string) => {
    return await keywordsAi.withWorkflow(
        { name: 'audience_reaction', version: 1 },
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
};

// Step 5: Complete Example using decorator pattern
const completeJokeExperience = async () => {
    return await keywordsAi.withWorkflow(
        { 
            name: 'complete_joke_experience',
            version: 1,
            associationProperties: { 'experiment': 'decorator_test' }
        },
        async () => {
            const pirateJoke = await jokeWorkflow();
            const reaction = await audienceReaction(pirateJoke);
            
            // Add non-LLM task using decorator pattern
            await keywordsAi.withTask(
                { name: 'logging', suppressTracing: false },
                async () => {
                    console.log('Joke:', pirateJoke);
                    console.log('Reaction:', reaction);
                    return 'logged';
                }
            );

            return {
                joke: pirateJoke,
                reaction: reaction
            };
        }
    );
};

// Step 6: Agent example using decorator pattern
const jokeAgent = async (topic: string) => {
    return await keywordsAi.withAgent(
        { 
            name: 'joke_agent',
            version: 1,
            associationProperties: { 'agent_type': 'comedian' }
        },
        async () => {
            // Agent can use tools
            const research = await keywordsAi.withTool(
                { name: 'topic_research' },
                async () => {
                    const completion = await openai.chat.completions.create({
                        messages: [{ 
                            role: 'user', 
                            content: `Research interesting facts about ${topic} for joke material` 
                        }],
                        model: 'gpt-3.5-turbo'
                    });
                    return completion.choices[0].message.content;
                }
            );

            const joke = await keywordsAi.withTool(
                { name: 'joke_generator' },
                async () => {
                    const completion = await openai.chat.completions.create({
                        messages: [{ 
                            role: 'user', 
                            content: `Create a funny joke about ${topic} using this research: ${research}` 
                        }],
                        model: 'gpt-3.5-turbo'
                    });
                    return completion.choices[0].message.content;
                }
            );

            return joke;
        }
    );
};

// Run the example
async function main() {
    try {
        console.log('=== Running Decorator Pattern Tests ===');
        
        // Test basic workflow
        console.log('\n1. Testing basic workflow...');
        const result = await completeJokeExperience();
        console.log('Basic workflow result:', result);
        
        // Test agent pattern
        console.log('\n2. Testing agent pattern...');
        const agentJoke = await jokeAgent('programming');
        console.log('Agent joke result:', agentJoke);
        
        console.log('\n=== All tests completed ===');
        
        // Shutdown tracing
        await keywordsAi.shutdown();
        
    } catch (error) {
        console.error('Error:', error);
        await keywordsAi.shutdown();
    }
}

main(); 