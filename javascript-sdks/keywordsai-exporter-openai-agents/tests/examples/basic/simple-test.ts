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
import { KeywordsAIOpenAIAgentsTracingExporter } from '../../../dist';

dotenv.config(
    {
        path: '../../../.env',
        override: true
    }
);

console.log("KEYWORDSAI_API_KEY", process.env.KEYWORDSAI_API_KEY, "ENV", process.env);

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
const exporter = new KeywordsAIOpenAIAgentsTracingExporter();
console.log('📡 KeywordsAI Exporter Configuration:');
console.log('  API Key:', process.env.KEYWORDSAI_API_KEY ? '***' + process.env.KEYWORDSAI_API_KEY.slice(-4) : 'Not set');
console.log('  Base URL:', process.env.KEYWORDSAI_BASE_URL || 'Using default');
console.log('  Expected Endpoint:', process.env.KEYWORDSAI_BASE_URL ? 
  `${process.env.KEYWORDSAI_BASE_URL}/v1/traces/ingest` : 
  'https://api.keywordsai.co/api/v1/traces/ingest');

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
  console.log('Testing KeywordsAI OpenAI Agents Exporter...');
  
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