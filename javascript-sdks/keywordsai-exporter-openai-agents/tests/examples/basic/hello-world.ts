import { Agent, BatchTraceProcessor, run, setTraceProcessors, withTrace } from '@openai/agents';
import * as dotenv from 'dotenv';
import { KeywordsAIOpenAIAgentsTracingExporter } from '../../../dist';

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
    name: 'Assistant',
    instructions: 'You only respond in haikus.',
  });

  const result = await withTrace('Hello World', async () => {
    return run(agent, 'Tell me about recursion in programming.');
  });
  console.log(result.finalOutput);
  // Example output:
  // Function calls itself,
  // Looping in smaller pieces,
  // Endless by design.
}

if (require.main === module) {
  main().catch(console.error);
}
