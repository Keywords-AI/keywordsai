import { KeywordsAITelemetry } from '../src/main';

async function debugOpenAITiming() {
  console.log('=== OpenAI Instrumentation Timing Debug ===');
  
  // Initialize KeywordsAI FIRST
  const keywordsAI = new KeywordsAITelemetry({
    keywordsaiApiKey: 'test-key',
    keywordsaiBaseUrl: 'http://localhost:8000',
  });
  
  await keywordsAI.initialize();
  console.log('KeywordsAI initialized');
  
  // Import OpenAI AFTER initialization
  console.log('Importing OpenAI module...');
  const { default: OpenAI } = await import('openai');
  
  // Create OpenAI client
  const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY || 'test-key',
  });
  
  console.log('OpenAI client created');
  
  // Try to make a request
  try {
    console.log('Making OpenAI request...');
    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [{ role: 'user', content: 'Hello' }],
      max_tokens: 10,
    });
    console.log('Response received:', response.choices[0]?.message?.content);
  } catch (error) {
    console.log('Error:', error.message);
  }
  
  // Wait for traces to be sent
  console.log('Waiting for traces to be sent...');
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  await keywordsAI.shutdown();
  console.log('KeywordsAI shutdown complete');
}

debugOpenAITiming().catch(console.error); 