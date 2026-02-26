import { RespanTelemetry } from '../src/main';

async function debugTimingOrder() {
  console.log("=== Testing proper initialization order ===");
  
  // Initialize Respan tracing FIRST
  console.log("1. Creating Respan instance...");
  const respan = new RespanTelemetry({
    apiKey: "test-api-key",
    baseURL: "http://localhost:3000",
  });
  
  console.log("2. Initializing Respan tracing...");
  await respan.initialize();
  
  // Wait a bit to ensure initialization is complete
  console.log("3. Waiting for instrumentation setup...");
  await new Promise(resolve => setTimeout(resolve, 100));
  
  // NOW import OpenAI - this should be instrumented
  console.log("4. Importing OpenAI AFTER instrumentation setup...");
  const OpenAI = (await import('openai')).default;
  
  console.log("5. Creating OpenAI client...");
  const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY || 'test-key',
  });
  
  // Check if methods are wrapped
  console.log("6. Checking if OpenAI methods are wrapped:");
  console.log("create method has __original:", '__original' in openai.chat.completions.create);
  console.log("create method has __wrapped:", '__wrapped' in openai.chat.completions.create);
  
  try {
    console.log("7. Making OpenAI request...");
    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [{ role: 'user', content: 'Hello!' }],
      max_tokens: 10,
    });
    
    console.log("8. Response received:", response.choices[0]?.message?.content);
  } catch (error) {
    console.log("8. Request failed (expected):", error.message);
  }
  
  console.log("9. Waiting for traces to be sent...");
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  console.log("10. Shutting down...");
  await respan.shutdown();
  
  console.log("=== Test complete ===");
}

debugTimingOrder().catch(console.error); 