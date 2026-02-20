/**
 * Quickstart: send one trace (root + child span) to Respan.
 *
 * Usage:
 *   export RESPAN_API_KEY="..."
 *   # optional:
 *   # export RESPAN_BASE_URL="https://api.respan.ai/api"
 *   node examples/quickstart.js
 *
 * Notes:
 * - This uses OpenTelemetry directly and sets the same `ai.*` / `gen_ai.*` attributes
 *   that the Vercel AI SDK emits, so the exporter can transform them into Respan payloads.
 */

import { context, trace } from '@opentelemetry/api';
import {
  BasicTracerProvider,
  SimpleSpanProcessor,
} from '@opentelemetry/sdk-trace-base';

// In this repo we import from dist (built output).
// In a consuming app, you'd do: `import { RespanExporter } from '@respan/exporter-vercel'`
import { RespanExporter } from '../dist/index.js';

async function main() {
  const apiKey = process.env.RESPAN_API_KEY;
  if (!apiKey) {
    console.error('Missing RESPAN_API_KEY');
    process.exit(1);
  }

  const baseUrl = process.env.RESPAN_BASE_URL; // optional

  const exporter = new RespanExporter({
    apiKey,
    ...(baseUrl ? { baseUrl } : {}),
    debug: true,
  });

  const provider = new BasicTracerProvider({
    spanProcessors: [new SimpleSpanProcessor(exporter)],
  });

  const tracer = provider.getTracer('ai');

  const runId = `quickstart-${Date.now()}`;
  const userId = process.env.RESPAN_TEST_USER_ID || runId;

  const promptText = `Respan quickstart (${runId})`;
  const responseText = `Respan quickstart response (${runId})`;

  const rootSpan = tracer.startSpan('ai.generateText.doGenerate', {
    attributes: {
      'ai.sdk': true,
      'ai.prompt': promptText,
      'ai.prompt.messages': JSON.stringify([{ role: 'user', content: promptText }]),
      'ai.response.text': responseText,
      'ai.model.id': 'gpt-4o-mini',
      'gen_ai.usage.input_tokens': 5,
      'gen_ai.usage.output_tokens': 7,
      'ai.response.msToFinish': 2000,
      // Helps you find the log in the platform
      'ai.telemetry.metadata.userId': userId,
      'ai.telemetry.metadata.quickstart_run_id': runId,
      'ai.telemetry.metadata.source':
        'respan-exporter-vercel/examples/quickstart.js',
    },
  });

  const childSpan = tracer.startSpan(
    'ai.toolCall',
    {
      attributes: {
        'ai.sdk': true,
        'ai.toolCall.id': `tool_${runId}`,
        'ai.toolCall.name': 'healthCheck',
        'ai.toolCall.args': JSON.stringify({ runId }),
        'ai.toolCall.result': JSON.stringify({ ok: true }),
        'ai.telemetry.metadata.userId': userId,
        'ai.telemetry.metadata.quickstart_run_id': runId,
      },
    },
    trace.setSpan(context.active(), rootSpan)
  );

  childSpan.end();
  rootSpan.end();

  await provider.forceFlush();
  await provider.shutdown();

  console.log(
    `Done. runId=${runId} traceId=${rootSpan.spanContext().traceId} userId=${userId}`
  );
}

main().catch((err) => {
  console.error('Quickstart failed:', err);
  process.exit(1);
});

