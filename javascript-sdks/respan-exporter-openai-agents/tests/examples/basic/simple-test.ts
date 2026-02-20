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

dotenv.config(
    {
        path: '../../../.env',
        override: true
    }
);

// Add debug logging for API calls
const originalFetch = global.fetch;
global.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
  const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
  
  console.log('🚀 API Call Details:');
  console.log('  URL:', url);
  console.log('  Method:', init?.method || 'GET');
  console.log('  Headers:', init?.headers);
  
  if (init?.body) {
    console.log('  Body:', init.body);
  }
  
  const response = await originalFetch(input, init);
  console.log('  Response Status:', response.status);
  
  // Log response headers
  const responseHeaders: Record<string, string> = {};
  response.headers.forEach((value, key) => {
    responseHeaders[key] = value;
  });
  console.log('  Response Headers:', responseHeaders);
  
  return response;
};

// Create exporter with debug info
const exporter = new RespanOpenAIAgentsTracingExporter();
console.log('📡 Respan Exporter Configuration:');
console.log('  API Key:', process.env.RESPAN_API_KEY ? '***' + process.env.RESPAN_API_KEY.slice(-4) : 'Not set');
console.log('  Base URL:', process.env.RESPAN_BASE_URL || 'Using default');
const expectedEndpoint = process.env.RESPAN_BASE_URL
  ? (process.env.RESPAN_BASE_URL.endsWith('/api')
      ? `${process.env.RESPAN_BASE_URL}/v1/traces/ingest`
      : `${process.env.RESPAN_BASE_URL}/api/v1/traces/ingest`)
  : 'https://api.respan.ai/api/v1/traces/ingest';
console.log('  Expected Endpoint:', expectedEndpoint);

// Set up our custom exporter
setTraceProcessors([
  new BatchTraceProcessor(exporter),
]);

const getWeatherTool = tool({
  name: 'get_weather',
  description: 'Get the weather for a given city',
  parameters: z.object({
    city: z.string(),
  }),
  execute: async (input) => {
    return `The weather in ${input.city} is sunny and 72°F`;
  },
});

const agent = new Agent({
  name: 'Weather Agent',
  instructions: 'You are a helpful weather assistant. Use the get_weather tool to provide weather information.',
  tools: [getWeatherTool],
});

async function testAgent() {
  console.log('Testing Respan OpenAI Agents Exporter...');
  
  try {
    await withTrace('Weather Test', async () => {
      const result = await run(agent, [
        user('What is the weather like in San Francisco?')
      ]);
      
      console.log('Agent response:', result.finalOutput);
      console.log('Test completed successfully!');
    });
  } catch (error) {
    console.error('Test failed:', error);
  }
}

testAgent(); 