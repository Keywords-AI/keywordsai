import { Agent, run } from '@openai/agents';

async function main() {
  const agent = new Agent({
    name: 'Assistant',
    instructions: 'You only respond in haikus.',
  });

  const result = await run(agent, 'Tell me about recursion in programming.');
  console.log(result.finalOutput);
  // Example output:
  // Function calls itself,
  // Looping in smaller pieces,
  // Endless by design.
}

if (require.main === module) {
  main().catch(console.error);
}
