import { Agent, BatchTraceProcessor, run, setTraceProcessors, withTrace } from '@openai/agents';
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
const URL =
  'https://upload.wikimedia.org/wikipedia/commons/0/0c/GoldenGateBridge-001.jpg';

async function main() {
  const agent = new Agent({
    name: 'Assistant',
    instructions: 'You are a helpful assistant.',
  });

  const result = await withTrace('Remote Image', async () => {
    return run(agent, [
    {
      role: 'user',
      content: [
        {
          type: 'input_image',
          image: URL,
          providerData: {
            detail: 'auto',
          },
        },
      ],
    },
    {
      role: 'user',
      content: 'What do you see in this image?',
    },
  ]);
  });
  console.log(result.finalOutput);
  // This image shows the Golden Gate Bridge, a famous suspension bridge located in San Francisco, California. The bridge is painted in its signature "International Orange" color and spans the Golden Gate Strait, connecting San Francisco to Marin County. The photo is taken during daylight, with the city and hills visible in the background and water beneath the bridge. The bridge is an iconic landmark and a symbol of San Francisco.
}

if (require.main === module) {
  main().catch(console.error);
}
