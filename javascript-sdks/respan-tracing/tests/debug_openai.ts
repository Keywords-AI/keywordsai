import { RespanTelemetry } from '../src/main';
import OpenAI from 'openai';

async function debugOpenAI() {
  console.log('=== OpenAI Instrumentation Debug ===');
  
  // Initialize Respan
  const respan = new RespanTelemetry({
    respanApiKey: 'test-key',
    respanBaseUrl: 'http://localhost:8000',
  });
  
  await respan.initialize();
  console.log('Respan initialized');
  
  // Create OpenAI client AFTER initialization
  const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY || 'test-key',
  });
  
  console.log('OpenAI client created');
  
  // Check if OpenAI is instrumented by looking at its prototype
  console.log('OpenAI prototype methods:', Object.getOwnPropertyNames(OpenAI.prototype));
  console.log('OpenAI chat completions create method:', typeof openai.chat.completions.create);
  
  // Try to make a request (this will fail with fake key but should still create spans)
  try {
    console.log('Making OpenAI request...');
    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [{ role: 'user', content: 'Hello' }],
      max_tokens: 10,
    });
    console.log('Response received:', response.choices[0]?.message?.content);
  } catch (error) {
    console.log('Expected error (fake API key):', error.message);
  }
  
  // Wait for traces to be sent
  console.log('Waiting for traces to be sent...');
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  await respan.shutdown();
  console.log('Respan shutdown complete');
}

debugOpenAI().catch(console.error); 