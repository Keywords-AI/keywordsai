import { z } from 'zod';
import { Agent, BatchTraceProcessor, run, setTraceProcessors, tool, withTrace } from '@openai/agents';
import { RespanOpenAIAgentsTracingExporter } from '../../../dist';
import * as dotenv from 'dotenv';

dotenv.config(
  {
      path: '../../../.env',
      override: true
  }
);
setTraceProcessors([
  new BatchTraceProcessor(
    new RespanOpenAIAgentsTracingExporter(),
  ),
]);
const getWeatherTool = tool({
  name: 'get_weather',
  description: 'Get the weather for a given city',
  parameters: z.object({ city: z.string() }),
  execute: async (input) => {
    return `The weather in ${input.city} is sunny`;
  },
});

const dataAgentTwo = new Agent({
  name: 'Data agent',
  instructions: 'You are a data agent',
  handoffDescription: 'You know everything about the weather',
  tools: [getWeatherTool],
});

const agent = new Agent({
  name: 'Basic test agent',
  instructions: 'You are a basic agent',
  handoffs: [dataAgentTwo],
});

async function main() {
  const result = await withTrace('Basic test agent', async () => {
    return run(agent, 'What is the weather in San Francisco?');
  });

  console.log(result.finalOutput);
}

main();
