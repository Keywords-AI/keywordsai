# Model Providers Examples

This directory contains small scripts showing how to integrate custom model providers. Run them with `pnpm` using the commands shown below.

- `custom-example-agent.ts` – Pass a model instance directly to an `Agent`.
  ```bash
  pnpm -F model-providers start:custom-example-agent
  ```
- `custom-example-global.ts` – Configure a global model provider. Requires environment variables `EXAMPLE_BASE_URL`, `EXAMPLE_API_KEY`, and `EXAMPLE_MODEL_NAME`.
  ```bash
  pnpm -F model-providers start:custom-example-global
  ```
- `custom-example-provider.ts` – Create a custom `ModelProvider` for a single run (same environment variables as above).
  ```bash
  pnpm -F model-providers start:custom-example-provider
  ```
