import { Agent, RunContext, run } from '@openai/agents';
import * as dotenv from 'dotenv';

dotenv.config(
  {
      path: '../../../.env',
      override: true
  }
);
type Style = 'haiku' | 'pirate' | 'robot';

interface CustomContext {
  style: Style;
}

function customInstructions(
  runContext: RunContext<CustomContext>,
  _agent: Agent<CustomContext>,
): string {
  const context = runContext.context;
  if (context.style === 'haiku') {
    return 'Only respond in haikus.';
  } else if (context.style === 'pirate') {
    return 'Respond as a pirate.';
  } else {
    return "Respond as a robot and say 'beep boop' a lot.";
  }
}

const agent = new Agent<CustomContext>({
  name: 'Chat agent',
  instructions: customInstructions,
});

async function main() {
  const choices: Style[] = ['haiku', 'pirate', 'robot'];
  const choice = choices[Math.floor(Math.random() * choices.length)];
  const context: CustomContext = { style: choice };
  console.log(`Using style: ${choice}\n`);

  const userMessage = 'Tell me a joke.';
  console.log(`User: ${userMessage}`);
  const result = await run(agent, userMessage, { context });

  console.log(`Assistant: ${result.finalOutput}`);
}

if (require.main === module) {
  main().catch(console.error);
}
