import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
import { Resource } from "@opentelemetry/resources";
import { ATTR_SERVICE_NAME } from "@opentelemetry/semantic-conventions";
import { registerInstrumentations } from "@opentelemetry/instrumentation";
import { ConsoleSpanExporter, BatchSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { trace } from "@opentelemetry/api";

async function debugManualInstrumentation() {
  console.log("=== Testing Manual Instrumentation Pattern ===");
  
  try {
    console.log("1. Setting up OpenTelemetry provider...");
    
    // Create provider
    const provider = new NodeTracerProvider({
      resource: new Resource({
        [ATTR_SERVICE_NAME]: "test-service",
      }),
    });
    
    // Add console exporter for debugging
    provider.addSpanProcessor(new BatchSpanProcessor(new ConsoleSpanExporter()));
    
    // Register the provider
    provider.register();
    
    console.log("2. Loading instrumentations...");
    
    // Load instrumentations
    const { OpenAIInstrumentation } = await import("@traceloop/instrumentation-openai");
    const { HttpInstrumentation } = await import("@opentelemetry/instrumentation-http");
    
    console.log("3. Registering instrumentations...");
    
    // Register instrumentations
    registerInstrumentations({
      instrumentations: [
        new HttpInstrumentation({
          ignoreIncomingRequestHook: () => true, // Ignore incoming requests
          ignoreOutgoingRequestHook: (options) => {
            const url = typeof options === 'string' ? options : (options as any).hostname || (options as any).host;

            return false; // Don't ignore any requests
          }
        }),
        new OpenAIInstrumentation({
          enrichTokens: true,
        }),
      ],
    });
    
    console.log("4. Waiting for instrumentation setup...");
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    console.log("5. Importing OpenAI AFTER instrumentation setup...");
    const OpenAI = (await import("openai")).default;
    
    console.log("6. Creating OpenAI client...");
    const openai = new OpenAI({
      apiKey: "sk-test-invalid-key-for-testing",
    });
    
    console.log("7. Checking if OpenAI methods are wrapped:");
    console.log("create method has __original:", !!(openai.chat.completions.create as any).__original);
    console.log("create method has __wrapped:", !!(openai.chat.completions.create as any).__wrapped);
    
    console.log("8. Creating manual span to test context...");
    const tracer = trace.getTracer("test-tracer");
    
    await tracer.startActiveSpan("test-span", async (span) => {
      console.log("9. Making OpenAI request...");
      try {
        const response = await openai.chat.completions.create({
          model: "gpt-3.5-turbo",
          messages: [{ role: "user", content: "Say hello" }],
        });
        console.log("10. Response:", response.choices[0]?.message?.content);
      } catch (error: any) {
        console.log("10. Expected error (invalid API key):", error.message);
      }
      
      span.end();
    });
    
    console.log("11. Waiting for traces to be sent...");
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    console.log("12. Shutting down...");
    await provider.shutdown();
    
  } catch (error) {
    console.error("Error during test:", error);
  }
  
  console.log("=== Test complete ===");
}

debugManualInstrumentation().catch(console.error); 