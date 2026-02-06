import { z } from 'zod';
import { Agent, run, tool } from '@openai/agents';
import { openai } from '@ai-sdk/openai';
import { aisdk } from '@openai/agents-extensions';

const model = aisdk(openai('gpt-4.1-nano'));

const getWeatherTool = tool({
  name: 'get_weather',
  description: 'Get the weather for a given city',
  parameters: z.object({ city: z.string() }),
  async execute({ city }) {
    return `The weather in ${city} is sunny`;
  },
});

const agent = new Agent({
  name: 'Weather agent',
  instructions: 'You provide weather information.',
  tools: [getWeatherTool],
  model,
});

async function main() {
  const stream = await run(agent, 'What is the weather in San Francisco?', {
    stream: true,
  });

  for await (const text of stream.toTextStream()) {
    process.stdout.write(text);
  }
  console.log();
}

if (require.main === module) {
  main().catch(console.error);
}
