import {
  Agent,
  run,
  tool,
  user,
  withTrace,
  setTraceProcessors,
  BatchTraceProcessor
} from '@openai/agents';
import { z } from 'zod';
import * as dotenv from 'dotenv';
import { RespanOpenAIAgentsTracingExporter } from '../../../dist';

dotenv.config({
  path: '../../../.env',
  override: true
});

// Create a custom exporter that logs everything
class DebugRespanExporter extends RespanOpenAIAgentsTracingExporter {
  async export(items: any[], signal?: AbortSignal): Promise<void> {
    console.log('=== DEBUG: Items being exported ===');
    console.log('Number of items:', items.length);
    
    for (let i = 0; i < items.length; i++) {
      console.log(`\n--- Item ${i + 1} ---`);
      console.log('Type:', items[i].constructor.name);
      console.log('Keys:', Object.keys(items[i]));
      if (items[i].spanData) {
        console.log('Span Data Type:', items[i].spanData.type);
        console.log('Span Data:', JSON.stringify(items[i].spanData, null, 2));
      }
    }
    
    console.log('\n=== Calling parent export ===');
    return super.export(items, signal);
  }
}

// Set up debug exporter
setTraceProcessors([
  new BatchTraceProcessor(
    new DebugRespanExporter(),
  ),
]);

const simpleAgent = new Agent({
  name: 'Simple Agent',
  instructions: 'You are a helpful assistant.',
});

async function debugTest() {
  console.log('Starting debug test...');
  
  try {
    await withTrace('Debug Test', async () => {
      const result = await run(simpleAgent, [
        user('Hello, how are you?')
      ]);
      
      console.log('Agent response:', result.finalOutput);
    });
  } catch (error) {
    console.error('Test failed:', error);
  }
}

debugTest(); 