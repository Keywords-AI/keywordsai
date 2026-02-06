import {
  Agent,
  run,
  user,
  withTrace,
  setTraceProcessors,
  BatchTraceProcessor,
  TracingExporter,
  Trace,
  Span
} from '@openai/agents';
import * as dotenv from 'dotenv';
import { KeywordsAISpanExporter } from '../../../dist';

dotenv.config({
  path: '../../../.env',
  override: true
});

// Create a custom exporter that logs the payload
class PayloadDebugExporter implements TracingExporter {
  private realExporter: KeywordsAISpanExporter;

  constructor() {
    this.realExporter = new KeywordsAISpanExporter();
  }

  async export(items: (Trace | Span<any>)[], signal?: AbortSignal): Promise<void> {
    console.log('=== INTERCEPTED EXPORT CALL ===');
    console.log('Number of items:', items.length);
    
    // Create a mock fetch to intercept the API call
    const originalFetch = global.fetch;
    global.fetch = async (url: string | URL | Request, init?: RequestInit) => {
      console.log('=== API CALL INTERCEPTED ===');
      console.log('URL:', url);
      console.log('Method:', init?.method || 'GET');
      console.log('Headers:', JSON.stringify(init?.headers, null, 2));
      console.log('Body:', init?.body);
      console.log('=== END API CALL ===');
      
      // Restore original fetch and make the real call
      global.fetch = originalFetch;
      return originalFetch(url, init);
    };

    // Call the real exporter
    return this.realExporter.export(items, signal);
  }
}

// Set up debug exporter
setTraceProcessors([
  new BatchTraceProcessor(
    new PayloadDebugExporter(),
  ),
]);

const simpleAgent = new Agent({
  name: 'Payload Test Agent',
  instructions: 'You are a helpful assistant for testing payload format.',
});

async function payloadTest() {
  console.log('Starting payload debug test...');
  
  try {
    await withTrace('Payload Test', async () => {
      const result = await run(simpleAgent, [
        user('What is 2+2?')
      ]);
      
      console.log('Agent response:', result.finalOutput);
    });
  } catch (error) {
    console.error('Test failed:', error);
  }
}

payloadTest(); 