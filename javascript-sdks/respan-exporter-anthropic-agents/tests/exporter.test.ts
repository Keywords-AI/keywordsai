import assert from "node:assert/strict";
import test from "node:test";

import { RespanAnthropicAgentsExporter } from "../src/respan-anthropic-agents-exporter.ts";

test("exports result payload via fetch", async () => {
  const originalFetch = globalThis.fetch;
  const capturedBodies: string[] = [];

  globalThis.fetch = (async (_input: unknown, init?: RequestInit) => {
    capturedBodies.push(String(init?.body || ""));
    return {
      status: 200,
      text: async () => "",
    } as Response;
  }) as typeof fetch;

  try {
    const exporter = new RespanAnthropicAgentsExporter({
      apiKey: "test-api-key",
      endpoint: "https://example.com/ingest",
    });

    await exporter.trackMessage({
      message: {
        type: "result",
        subtype: "success",
        duration_ms: 120,
        duration_api_ms: 45,
        is_error: false,
        num_turns: 2,
        session_id: "session-1",
        result: "done",
        usage: {
          input_tokens: 3,
          output_tokens: 2,
          total_tokens: 5,
        },
      },
      sessionId: "session-1",
    });

    await new Promise((resolve) => setTimeout(resolve, 10));

    assert.ok(capturedBodies.length > 0);
    const payloadItems = capturedBodies.flatMap((body) => {
      const parsedBody = JSON.parse(body) as { data: Array<Record<string, unknown>> };
      return parsedBody.data;
    });

    const resultPayload = payloadItems.find((item) => {
      return item.span_name === "result:success";
    });
    assert.ok(resultPayload);
    assert.equal(resultPayload?.trace_unique_id, "session-1");
    assert.equal(resultPayload?.log_type, "agent");
    assert.equal(resultPayload?.total_request_tokens, 5);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("creates expected hook map", async () => {
  const exporter = new RespanAnthropicAgentsExporter({
    apiKey: "test-api-key",
    endpoint: "https://example.com/ingest",
  });

  const hooks = exporter.createHooks({});
  assert.ok(hooks.UserPromptSubmit);
  assert.ok(hooks.PreToolUse);
  assert.ok(hooks.PostToolUse);
  assert.ok(hooks.SubagentStop);
  assert.ok(hooks.Stop);
});
