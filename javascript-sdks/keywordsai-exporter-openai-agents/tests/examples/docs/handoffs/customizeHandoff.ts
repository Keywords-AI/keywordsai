import { Agent, handoff, RunContext } from '@openai/agents';

function onHandoff(ctx: RunContext) {
  console.log('Handoff called');
}

const agent = new Agent({ name: 'My agent' });

const handoffObj = handoff(agent, {
  onHandoff,
  toolNameOverride: 'custom_handoff_tool',
  toolDescriptionOverride: 'Custom description',
});
