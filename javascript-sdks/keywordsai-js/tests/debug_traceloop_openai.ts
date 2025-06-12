import { KeywordsAITelemetry } from "../src/main";
import { trace } from "@opentelemetry/api";

async function debugTraceloopOpenAI() {
  console.log("=== Testing Traceloop OpenAI instrumentation ===");
  
  console.log("1. Creating KeywordsAI instance...");
  const keywordsai = new KeywordsAITelemetry({
    apiKey: "test-api-key",
    baseUrl: "https://api.keywordsai.co",
  });

  console.log("2. Initializing KeywordsAI tracing...");
  await keywordsai.initialize();

  console.log("3. Waiting for instrumentation setup...");
  await new Promise(resolve => setTimeout(resolve, 1000));

  console.log("4. Importing OpenAI AFTER instrumentation setup...");
  const OpenAI = (await import("openai")).default;

  console.log("5. Creating OpenAI client...");
  const openai = new OpenAI({
    apiKey: "sk-test-key-not-real",
    baseURL: "https://api.openai.com/v1",
  });

  console.log("6. Checking if OpenAI methods are wrapped:");
  console.log("create method has __original:", !!(openai.chat.completions.create as any).__original);
  console.log("create method has __wrapped:", !!(openai.chat.completions.create as any).__wrapped);

  console.log("7. Creating manual span to test context...");
  const tracer = trace.getTracer('test-tracer');
  const span = tracer.startSpan('test-openai-call');
  
  try {
    console.log("8. Making OpenAI request...");
    const response = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [{ role: "user", content: "Say hello" }],
      max_tokens: 10,
    });
    console.log("9. Response received:", response.choices[0]?.message?.content || "No content");
  } catch (error) {
    console.log("9. Expected error (invalid API key):", (error as any).message?.substring(0, 100));
  } finally {
    span.end();
  }

  console.log("10. Waiting for traces to be sent...");
  await new Promise(resolve => setTimeout(resolve, 2000));

  console.log("11. Shutting down...");
  await keywordsai.shutdown();
  
  console.log("=== Test complete ===");
}

debugTraceloopOpenAI().catch(console.error); 