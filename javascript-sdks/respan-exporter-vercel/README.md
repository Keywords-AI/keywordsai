# respan-exporter-vercel

Respan integration with the [Vercel AI SDK (AI SDK)](https://ai-sdk.dev/docs/introduction).

This package provides an OpenTelemetry `SpanExporter` (`RespanExporter`) that converts AI SDK spans into Respan payloads and sends them to Respan's ingest endpoint.

## Usage

```ts
import { RespanExporter } from '@respan/exporter-vercel';
import { SimpleSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { registerOTel } from '@vercel/otel';

export function register() {
  registerOTel({
    serviceName: 'my-app',
    spanProcessors: [
      new SimpleSpanProcessor(
        new RespanExporter({
          apiKey: process.env.RESPAN_API_KEY,
          baseUrl: process.env.RESPAN_BASE_URL, // optional
          debug: false,
        })
      ),
    ],
  });
}
```

## Development

```bash
yarn build
yarn test
```

## Quickstart (simplest real send)

This sends **one trace** (root + child span) to Respan using your real API key.

```bash
export RESPAN_API_KEY="..."
# optional:
# export RESPAN_BASE_URL="https://api.respan.ai/api"

yarn quickstart
```

It prints a `runId` and `traceId` you can search for in the Respan UI.

## Live test (runs via `node --test`, sends real data)

This is an integration test that only runs when explicitly enabled:

```bash
export RESPAN_API_KEY="..."
# optional:
# export RESPAN_BASE_URL="https://api.respan.ai/api"

yarn test:live
```