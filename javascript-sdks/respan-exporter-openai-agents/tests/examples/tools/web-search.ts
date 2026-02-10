import { Agent, BatchTraceProcessor, run, setTraceProcessors, webSearchTool, withTrace } from '@openai/agents';
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
async function main() {
  const agent = new Agent({
    name: 'Web searcher',
    instructions: 'You are a helpful agent.',
    tools: [
      webSearchTool({
        userLocation: { type: 'approximate', city: 'New York' },
      }),
    ],
  });

  await withTrace('Web search example', async () => {
    const result = await run(
      agent,
      "search the web for 'local sports news' and give me 1 interesting update in a sentence.",
    );
    console.log(result.finalOutput);
    // The New York Giants are reportedly pursuing quarterback Aaron Rodgers after his ...
  });
}

main().catch(console.error);
