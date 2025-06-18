import { Agent, run, JsonSchemaDefinition, BatchTraceProcessor, setTraceProcessors, withTrace } from '@openai/agents';
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
const WeatherSchema: JsonSchemaDefinition = {
  type: 'json_schema',
  name: 'Weather',
  strict: true,
  schema: {
    type: 'object',
    properties: { city: { type: 'string' }, forecast: { type: 'string' } },
    required: ['city', 'forecast'],
    additionalProperties: false,
  },
};

async function main() {
  const agent = new Agent({
    name: 'Weather reporter',
    instructions: 'Return the city and a short weather forecast.',
    outputType: WeatherSchema,
  });

  const result = await withTrace('JSON Schema Output Type', async () => {
    return run(agent, 'What is the weather in London?');
  });
  console.log(result.finalOutput);
  // { city: 'London', forecast: '...'}
}

main().catch(console.error);
