import { KeywordsAITelemetry } from "../src/main";
import { trace } from "@opentelemetry/api";

async function debugHttpInstrumentation() {
  console.log("1. Creating KeywordsAI instance...");
  const keywordsai = new KeywordsAITelemetry({
    apiKey: "test-api-key",
    baseURL: "https://api.keywordsai.co",
  });

  console.log("2. Initializing KeywordsAI tracing...");
  await keywordsai.initialize();

  console.log("3. Creating manual span...");
  const tracer = trace.getTracer('test-tracer');
  const span = tracer.startSpan('test-http-request');
  
  try {
    console.log("4. Making HTTP request...");
    const response = await fetch('https://httpbin.org/json');
    const data = await response.json();
    console.log("5. HTTP response received:", data.slideshow?.title || 'No title');
    
    span.setAttributes({
      'http.method': 'GET',
      'http.url': 'https://httpbin.org/json',
      'http.status_code': response.status
    });
    
  } catch (error) {
    console.error("Error making HTTP request:", error);
    span.recordException(error as Error);
  } finally {
    span.end();
  }

  console.log("6. Waiting for traces to be sent...");
  await new Promise(resolve => setTimeout(resolve, 2000));

  console.log("7. Shutting down KeywordsAI...");
  await keywordsai.shutdown();
}

debugHttpInstrumentation().catch(console.error); 