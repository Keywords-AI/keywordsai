import { KeywordsAITelemetry } from '@keywordsai/tracing';
import OpenAI from 'openai';

// Initialize the SDK
const keywordsAi = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDS_AI_API_KEY,
    baseUrl: process.env.KEYWORDS_AI_BASE_URL,
    appName: 'basic-example',
    disableBatch: true, // For development
    logLevel: 'info'
});

// Enable OpenAI instrumentation (only if installed)
async function enableInstrumentations() {
    try {
        await keywordsAi.enableInstrumentation('openai');
        console.log('OpenAI instrumentation enabled');
    } catch (error) {
        console.log('OpenAI instrumentation not available:', error.message);
    }
}

const openai = new OpenAI();

// Basic task example
const generateResponse = async (prompt: string) => {
    return await keywordsAi.withTask(
        { name: 'generate_response', version: 1 },
        async () => {
            const completion = await openai.chat.completions.create({
                messages: [{ role: 'user', content: prompt }],
                model: 'gpt-3.5-turbo'
            });
            return completion.choices[0].message.content;
        }
    );
};

// Workflow example
const chatWorkflow = async (userMessage: string) => {
    return await keywordsAi.withWorkflow(
        { 
            name: 'chat_workflow', 
            version: 1,
            associationProperties: { 'user_type': 'demo' }
        },
        async () => {
            // Process the message
            const response = await generateResponse(userMessage);
            
            // Log the interaction (non-LLM task)
            await keywordsAi.withTask(
                { name: 'log_interaction' },
                async () => {
                    console.log(`User: ${userMessage}`);
                    console.log(`Assistant: ${response}`);
                    return 'logged';
                }
            );
            
            return response;
        }
    );
};

// Agent example with tools
const assistantAgent = async (query: string) => {
    return await keywordsAi.withAgent(
        { 
            name: 'assistant_agent',
            associationProperties: { 'agent_type': 'general' }
        },
        async () => {
            // Use a tool to analyze the query
            const analysis = await keywordsAi.withTool(
                { name: 'query_analyzer' },
                async () => {
                    // Simple analysis tool
                    return {
                        intent: query.includes('?') ? 'question' : 'statement',
                        length: query.length,
                        complexity: query.split(' ').length > 10 ? 'high' : 'low'
                    };
                }
            );
            
            // Generate response based on analysis
            const response = await keywordsAi.withTool(
                { name: 'response_generator' },
                async () => {
                    const systemPrompt = analysis.intent === 'question' 
                        ? 'You are a helpful assistant answering questions.'
                        : 'You are a helpful assistant responding to statements.';
                    
                    const completion = await openai.chat.completions.create({
                        messages: [
                            { role: 'system', content: systemPrompt },
                            { role: 'user', content: query }
                        ],
                        model: 'gpt-3.5-turbo'
                    });
                    return completion.choices[0].message.content;
                }
            );
            
            return {
                analysis,
                response
            };
        }
    );
};

// Main execution
async function main() {
    try {
        // Enable instrumentations
        await enableInstrumentations();
        
        console.log('=== Basic Task Example ===');
        const basicResponse = await generateResponse('Hello, how are you?');
        console.log('Response:', basicResponse);
        
        console.log('\n=== Workflow Example ===');
        const workflowResponse = await chatWorkflow('What is the weather like?');
        console.log('Workflow Response:', workflowResponse);
        
        console.log('\n=== Agent Example ===');
        const agentResponse = await assistantAgent('Can you explain quantum computing?');
        console.log('Agent Response:', agentResponse);
        
        console.log('\n=== All examples completed ===');
        
        // Shutdown tracing
        await keywordsAi.shutdown();
        
    } catch (error) {
        console.error('Error:', error);
        await keywordsAi.shutdown();
    }
}

// Run if this file is executed directly
if (require.main === module) {
    main();
}

export { keywordsAi, generateResponse, chatWorkflow, assistantAgent }; 