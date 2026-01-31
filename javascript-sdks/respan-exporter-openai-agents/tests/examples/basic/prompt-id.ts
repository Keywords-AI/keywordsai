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
async function main() {
  const agent = new Agent({
    name: 'Assistant',
    prompt: {
      promptId: 'pmpt_6852d4818a3881909718eab68030a8600bedfd507cb7b39e',
      version: '1',
      variables: {
       
      },
    },
  });

  const result = await withTrace('Prompt ID', async () => {
    return run(agent, 'Write about unrequited love.');
  });
  console.log(result.finalOutput);
}

if (require.main === module) {
  main().catch(console.error);
}
