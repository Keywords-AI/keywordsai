import { Agent, handoff } from '@openai/agents';
import { removeAllTools } from '@openai/agents-core/extensions';

const agent = new Agent({ name: 'FAQ agent' });

const handoffObj = handoff(agent, {
  inputFilter: removeAllTools,
});
