import { Agent, run, fileSearchTool, withTrace } from '@openai/agents';

async function main() {
  const agent = new Agent({
    name: 'File searcher',
    instructions: 'You are a helpful agent.',
    tools: [
      fileSearchTool(['vs_67bf88953f748191be42b462090e53e7'], {
        maxNumResults: 3,
        includeSearchResults: true,
      }),
    ],
  });

  await withTrace('File search example', async () => {
    const result = await run(
      agent,
      'Be concise, and tell me 1 sentence about Arrakis I might not know.',
    );
    console.log(result.finalOutput);
    /*
    Arrakis, the desert planet in Frank Herbert's "Dune," was inspired by the scarcity of water
    as a metaphor for oil and other finite resources.
    */

    console.log(
      '\n' +
        result.newItems.map((out: unknown) => JSON.stringify(out)).join('\n'),
    );
    /*
    {"id":"...", "queries":["Arrakis"], "results":[...]}
    */
  });
}

main().catch(console.error);
