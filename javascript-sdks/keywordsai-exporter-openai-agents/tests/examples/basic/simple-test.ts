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
        path: '.env',
        override: true
    }
);

console.log("KEYWORDSAI_API_KEY", process.env.KEYWORDSAI_API_KEY, "ENV", process.env);

// Set up our custom exporter
setTraceProcessors([
  new BatchTraceProcessor(
    new KeywordsAIOpenAIAgentsTracingExporter(),
  ),
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