# keywordsai-exporter-aisdk

Keywords AI exporter for the [Vercel AI SDK](https://ai-sdk.dev/) OpenTelemetry
spans. This package mirrors the AI SDK observability provider pattern (e.g.
Langfuse) and ships a SpanExporter that sends AI SDK traces to the Keywords AI
ingest endpoint.

## Install

```bash
npm i @keywordsai/exporter-aisdk
# or
yarn add @keywordsai/exporter-aisdk
# or
pnpm add @keywordsai/exporter-aisdk
```

## Usage (Node / Next.js)

Register an OpenTelemetry exporter (similar to the Langfuse AI SDK
observability setup):

```ts
import { registerOTel } from "@vercel/otel";
import { KeywordsAIExporter } from "@keywordsai/exporter-aisdk";

export function register() {
  registerOTel({
    serviceName: "my-ai-app",
    traceExporter: new KeywordsAIExporter({
      apiKey: process.env.KEYWORDSAI_API_KEY,
      baseUrl: "https://api.keywordsai.co/api",
      debug: true,
    }),
  });
}
```

Enable telemetry for AI SDK calls:

```ts
import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";

const result = await generateText({
  model: openai("gpt-4o-mini"),
  prompt: "Hello from AI SDK!",
  experimental_telemetry: {
    isEnabled: true,
  },
});
```

## Configuration

- `apiKey`: Keywords AI API key. Defaults to `process.env.KEYWORDSAI_API_KEY`.
- `baseUrl`: Base Keywords AI API URL. Defaults to
  `https://api.keywordsai.co/api`.
- `debug`: Log exporter activity to stdout.

## Notes

- The exporter filters for AI SDK spans (instrumentation scope `ai` or
  `ai.*`/`gen_ai.*` attributes).
- Spans are converted into Keywords AI payloads and sent in a single batch
  request to the integration ingest endpoint.
