import { Agent, BatchTraceProcessor, run, setTraceProcessors, tool, withTrace } from '@openai/agents';
import { z } from 'zod';
import { KeywordsAIOpenAIAgentsTracingExporter } from '../../../dist';
import * as dotenv from 'dotenv';

dotenv.config(
  {
      path: '../../../.env',
      override: true
  }
);

setTraceProcessors([
new BatchTraceProcessor(
  new KeywordsAIOpenAIAgentsTracingExporter(),
),
]);     
type Weather = {
  city: string;
  temperatureRange: string;
  conditions: string;
};

const getWeather = tool({
  name: 'get_weather',
  description: 'Get the weather for a city.',
  parameters: z.object({ city: z.string() }),
  execute: async ({ city }): Promise<Weather> => {
    return {
      city,
      temperatureRange: '14-20C',
      conditions: 'Sunny with wind.',
    };
  },
});

const agent = new Agent({
  name: 'Hello world',
  instructions: 'You are a helpful agent.',
  tools: [getWeather],
});

async function main() {
  const result = await withTrace('Tools', async () => {
    return run(agent, "What's the weather in Tokyo?");
  });
  console.log(result.finalOutput);
  // The weather in Tokyo is sunny with some wind, and the temperature ranges between 14°C and 20°C.
}

if (require.main === module) {
  main();
}
