# Respan Exporter for Vercel AI SDK

**[respan.ai](https://respan.ai)** | **[Documentation](https://docs.respan.ai)**

Respan's integration with [Vercel AI SDK](https://github.com/vercel/ai)
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