import { RespanTelemetry } from "../src/main";
import { trace } from "@opentelemetry/api";

async function debugHttpInstrumentation() {
  console.log("1. Creating Respan instance...");
  const respan = new RespanTelemetry({
    apiKey: "test-api-key",
    baseURL: "https://api.respan.ai",
  });

  console.log("2. Initializing Respan tracing...");
  await respan.initialize();

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

  console.log("7. Shutting down Respan...");
  await respan.shutdown();
}

debugHttpInstrumentation().catch(console.error); 