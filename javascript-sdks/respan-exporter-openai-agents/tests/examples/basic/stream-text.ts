import { Agent, BatchTraceProcessor, run, setTraceProcessors } from '@openai/agents';
import { withTrace } from '@openai/agents';
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
async function main() {
  const agent = new Agent({
    name: 'Joker',
    instructions: 'You are a helpful assistant.',
  });

  const stream = await withTrace('Stream Text', async () => {
    return run(agent, 'Please tell me 5 jokes.', {
    stream: true,
    });
  });
  for await (const event of stream.toTextStream()) {
    process.stdout.write(event);
  }
  console.log();
}

if (require.main === module) {
  main().catch(console.error);
}
