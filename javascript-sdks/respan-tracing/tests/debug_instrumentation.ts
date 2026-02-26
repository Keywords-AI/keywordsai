import { RespanTelemetry } from '../src/main';

async function debugInstrumentation() {
  console.log('=== Instrumentation Debug ===');
  
  // Initialize Respan
  const respan = new RespanTelemetry({
    respanApiKey: 'test-key',
    respanBaseUrl: 'http://localhost:8000',
  });
  
  await respan.initialize();
  console.log('Respan initialized');
  
  // Import OpenAI after initialization
  const { default: OpenAI } = await import('openai');
  
  // Check the OpenAI structure
  console.log('\n=== OpenAI Structure ===');
  console.log('OpenAI.Chat:', typeof OpenAI.Chat);
  console.log('OpenAI.Completions:', typeof OpenAI.Completions);
  console.log('OpenAI.Chat.Completions:', typeof OpenAI.Chat?.Completions);
  
  // Create client and check instance structure
  const client = new OpenAI({ apiKey: 'test-key' });
  console.log('\n=== Client Instance Structure ===');
  console.log('client.chat:', typeof client.chat);
  console.log('client.chat.completions:', typeof client.chat.completions);
  console.log('client.chat.completions.create:', typeof client.chat.completions.create);
  console.log('client.completions:', typeof client.completions);
  console.log('client.completions.create:', typeof client.completions.create);
  
  // Check if methods have been wrapped (they should have additional properties if instrumented)
  console.log('\n=== Method Instrumentation Check ===');
  const createMethod = client.chat.completions.create;
  console.log('create method name:', createMethod.name);
  console.log('create method length:', createMethod.length);
  console.log('create method toString preview:', createMethod.toString().substring(0, 100));
  
  // Check for OpenTelemetry wrapper properties
  console.log('Has __original property:', '__original' in createMethod);
  console.log('Has __wrapped property:', '__wrapped' in createMethod);
  
  await respan.shutdown();
  console.log('\nRespan shutdown complete');
}

debugInstrumentation().catch(console.error); 