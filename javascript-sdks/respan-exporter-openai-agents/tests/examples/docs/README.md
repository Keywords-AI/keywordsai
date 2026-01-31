# Documentation Snippets

This directory contains small scripts used throughout the documentation. Run them with `pnpm` using the commands shown below.

- `agents-basic-configuration.ts` – Configure a weather agent with a tool and model.
  ```bash
  pnpm -F docs start:agents-basic-configuration
  ```
- `agents-cloning.ts` – Clone an agent and reuse its configuration.
  ```bash
  pnpm -F docs start:agents-cloning
  ```
- `agents-context.ts` – Access user context from tools during execution.
  ```bash
  pnpm -F docs start:agents-context
  ```
- `agents-dynamic-instructions.ts` – Build instructions dynamically from context.
  ```bash
  pnpm -F docs start:agents-dynamic-instructions
  ```
- `agents-forcing-tool-use.ts` – Require specific tools before producing output.
  ```bash
  pnpm -F docs start:agents-forcing-tool-use
  ```
- `agents-handoffs.ts` – Route requests to specialized agents using handoffs.
  ```bash
  pnpm -F docs start:agents-handoffs
  ```
- `agents-lifecycle-hooks.ts` – Log agent lifecycle events as they run.
  ```bash
  pnpm -F docs start:agents-lifecycle-hooks
  ```
- `agents-output-types.ts` – Return structured data using a Zod schema.
  ```bash
  pnpm -F docs start:agents-output-types
  ```
- `guardrails-input.ts` – Block unwanted requests using input guardrails.
  ```bash
  pnpm -F docs start:guardrails-input
  ```
- `guardrails-output.ts` – Check responses with output guardrails.
  ```bash
  pnpm -F docs start:guardrails-output
  ```
- `models-custom-providers.ts` – Create and use a custom model provider.
  ```bash
  pnpm -F docs start:models-custom-providers
  ```
- `models-openai-provider.ts` – Run agents with the OpenAI provider.
  ```bash
  pnpm -F docs start:models-openai-provider
  ```
- `quickstart.ts` – Simple triage agent that hands off questions to tutors.
  ```bash
  pnpm -F docs start:quickstart
  ```
- `readme-functions.ts` – README example showing how to call functions as tools.
  ```bash
  pnpm -F docs start:readme-functions
  ```
- `readme-handoffs.ts` – README example that demonstrates handoffs.
  ```bash
  pnpm -F docs start:readme-handoffs
  ```
- `readme-hello-world.ts` – The hello world snippet from the README.
  ```bash
  pnpm -F docs start:readme-hello-world
  ```
- `readme-voice-agent.ts` – Browser-based realtime voice agent example.
  ```bash
  pnpm -F docs start:readme-voice-agent
  ```
- `running-agents-exceptions1.ts` – Retry after a guardrail execution error.
  ```bash
  pnpm -F docs start:running-agents-exceptions1
  ```
- `running-agents-exceptions2.ts` – Retry after a failed tool call.
  ```bash
  pnpm -F docs start:running-agents-exceptions2
  ```
