import { KeywordsAITelemetry } from '../src/main';

async function debugOpenAIFinal() {
  console.log('=== Final OpenAI Instrumentation Debug ===');
  
  // Initialize KeywordsAI first
  const keywordsAI = new KeywordsAITelemetry({
    keywordsaiApiKey: 'test-key',
    keywordsaiBaseUrl: 'http://localhost:8000',
  });
  
  await keywordsAI.initialize();
  console.log('KeywordsAI initialized');
  
  // Wait a bit to ensure instrumentation is fully set up
  await new Promise(resolve => setTimeout(resolve, 100));
  
  // Import OpenAI AFTER initialization
  console.log('Importing OpenAI module...');
  const { default: OpenAI } = await import('openai');
  
  // Create OpenAI client
  const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY || 'test-key',
  });
  
  console.log('OpenAI client created');
  
  // Check if we can get the current span before making the request
  const { getCurrentSpan } = await import('../src/utils/tracing');
  console.log('Current span before request:', getCurrentSpan()?.spanContext().spanId);
  
  // Try to make a request
  try {
    console.log('Making OpenAI request...');
    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [{ role: 'user', content: 'Hello' }],
      max_tokens: 10,
    });
    console.log('Response received:', response.choices[0]?.message?.content);
    
    // Check if we have a span after the request
    console.log('Current span after request:', getCurrentSpan()?.spanContext().spanId);
  } catch (error) {
    console.log('Error:', error.message);
  }
  
  // Wait for traces to be sent
  console.log('Waiting for traces to be sent...');
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  await keywordsAI.shutdown();
  console.log('KeywordsAI shutdown complete');
}

debugOpenAIFinal().catch(console.error); 