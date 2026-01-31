import { styleText } from 'node:util';
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
const ASSISTANT_PREFIX = 'Assistant';
const THINKING_PREFIX = 'Thought';

async function main() {
  const agent = new Agent({
    name: 'Agent',
    model: 'o3',
    modelSettings: {
      providerData: {
        reasoning: {
          effort: 'high',
          summary: 'auto',
        },
      },
    },
  });

  const result = await withTrace('Reasoning', async () => {
    return run(agent, 'How many r are in strawberry?');
  });

  for (const item of result.newItems) {
    if (item.type === 'reasoning_item') {
      for (const entry of item.rawItem.content) {
        if (entry.type === 'input_text') {
          console.log(`${THINKING_PREFIX}: ${entry.text}`);
        }
      }
    }
  }

  console.log(`${ASSISTANT_PREFIX}: ${result.finalOutput}`);
}

main().catch(console.error);
