import { RespanTelemetry } from '../src/main';
import { trace, context } from '@opentelemetry/api';

async function debugSpanCreation() {
  console.log('=== Span Creation Debug ===');
  
  const respan = new RespanTelemetry({
    apiKey: 'test-key',
    baseURL: 'http://localhost:3000/api/otel/v1/traces'
  });

  await respan.initialize();
  console.log('Respan initialized');

  // Get the tracer
  const tracer = trace.getTracer('test-tracer');
  console.log('Tracer obtained:', !!tracer);

  // Create a manual span
  const span = tracer.startSpan('test-span');
  console.log('Manual span created:', !!span);
  console.log('Span context:', span.spanContext());

  // Set the span as active
  context.with(trace.setSpan(context.active(), span), async () => {
    console.log('Current active span:', trace.getActiveSpan()?.spanContext());
    
    // Now import and use OpenAI within the span context
    console.log('Importing OpenAI module...');
    const OpenAI = (await import('openai')).default;
    
    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY || 'test-key'
    });
    console.log('OpenAI client created');

    try {
      console.log('Current span before OpenAI request:', trace.getActiveSpan()?.spanContext());
      
      const response = await openai.chat.completions.create({
        model: 'gpt-3.5-turbo',
        messages: [{ role: 'user', content: 'Say hello' }],
        max_tokens: 10
      });

      console.log('Response received:', response.choices[0]?.message?.content);
      console.log('Current span after OpenAI request:', trace.getActiveSpan()?.spanContext());
      
    } catch (error) {
      console.error('OpenAI request failed:', error);
    }
  });

  // End the manual span
  span.end();
  console.log('Manual span ended');

  // Wait for traces to be sent
  console.log('Waiting for traces to be sent...');
  await new Promise(resolve => setTimeout(resolve, 2000));

  await respan.shutdown();
  console.log('Respan shutdown complete');
}

debugSpanCreation().catch(console.error); 