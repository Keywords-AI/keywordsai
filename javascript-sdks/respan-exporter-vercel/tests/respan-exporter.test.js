import test from 'node:test';

import { context, trace } from '@opentelemetry/api';
import {
  BasicTracerProvider,
  SimpleSpanProcessor,
} from '@opentelemetry/sdk-trace-base';

import { RespanExporter } from '../dist/index.js';

test(
  'LIVE: sends an AI SDK span to Respan (real network)',
  {
    skip: !(
      process.env.RESPAN_RUN_LIVE_TESTS === '1' && process.env.RESPAN_API_KEY
    ),
  },
  async () => {
    const apiKey = process.env.RESPAN_API_KEY;
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

    const runId = `live-test-${Date.now()}`;
    const promptText = `Respan LIVE test (${runId})`;
    const responseText = `Respan LIVE test response (${runId})`;

    const rootSpan = tracer.startSpan('ai.generateText.doGenerate', {
      attributes: {
        'ai.sdk': true,
        'ai.prompt': promptText,
        'ai.prompt.messages': JSON.stringify([
          { role: 'user', content: promptText },
        ]),
        'ai.response.text': responseText,
        'ai.model.id': 'gpt-4o-mini',
        'gen_ai.usage.input_tokens': 5,
        'gen_ai.usage.output_tokens': 7,
        'ai.response.msToFinish': 2000,
        // Helps you find the log in the platform
        'ai.telemetry.metadata.userId':
          process.env.RESPAN_TEST_USER_ID || runId,
        'ai.telemetry.metadata.smoke_test_run_id': runId,
        'ai.telemetry.metadata.source':
          'respan-exporter-vercel/tests/respan-exporter.test.js',
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
          'ai.telemetry.metadata.userId':
            process.env.RESPAN_TEST_USER_ID || runId,
          'ai.telemetry.metadata.smoke_test_run_id': runId,
        },
      },
      trace.setSpan(context.active(), rootSpan)
    );

    childSpan.end();
    rootSpan.end();

    try {
      await provider.forceFlush();
      await provider.shutdown();
    } catch (err) {
      // Add a little context (common failure: DNS / network / 401)
      throw new Error(
        `LIVE send failed (baseUrl=${baseUrl || '(default)'}) - ${String(err)}`
      );
    }
  }
);

