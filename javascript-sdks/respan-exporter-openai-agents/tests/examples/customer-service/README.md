# Customer Service Agent

This example demonstrates a multi-agent customer service workflow for an airline. The `index.ts` script sets up a triage agent that can delegate to specialized FAQ and seat booking agents. Tools are used to look up common questions and to update a passenger's seat. Interaction occurs through a simple CLI loop, showing how agents can hand off between each other and call tools.

Run the demo with:

```bash
pnpm examples:customer-service
```

