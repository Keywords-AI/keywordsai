import assert from "node:assert/strict";
import test from "node:test";

import { RespanAnthropicAgentsExporter } from "../src/respan-anthropic-agents-exporter.ts";

function captureFetch(capturedBodies: string[]) {
  return (async (_input: unknown, init?: RequestInit) => {
    capturedBodies.push(String(init?.body || ""));
    return {
      status: 200,
      text: async () => "",
    } as Response;
  }) as typeof fetch;
}

function parsePayloads(capturedBodies: string[]): Record<string, unknown>[] {
  return capturedBodies.flatMap((body) => {
    const parsedBody = JSON.parse(body) as {
      data: Array<Record<string, unknown>>;
    };
    return parsedBody.data;
  });
}

test("exports result payload via fetch", async () => {
  const originalFetch = globalThis.fetch;
  const capturedBodies: string[] = [];
  globalThis.fetch = captureFetch(capturedBodies);

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
    const payloadItems = parsePayloads(capturedBodies);
    const resultPayload = payloadItems.find(
      (item) => item.span_name === "result:success"
    );
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

test("hook lifecycle - UserPromptSubmit sends user_prompt payload", async () => {
  const originalFetch = globalThis.fetch;
  const capturedBodies: string[] = [];
  globalThis.fetch = captureFetch(capturedBodies);

  try {
    const exporter = new RespanAnthropicAgentsExporter({
      apiKey: "key",
      endpoint: "https://example.com/ingest",
    });
    const hooks = exporter.createHooks({});

    const userPromptHooks = hooks.UserPromptSubmit as Array<{
      hooks?: Array<(input: Record<string, unknown>) => Promise<Record<string, unknown>>>;
    }>;
    assert.ok(Array.isArray(userPromptHooks) && userPromptHooks.length > 0);
    const firstHook = userPromptHooks[0];
    const callback = Array.isArray(firstHook?.hooks) ? firstHook.hooks![0] : null;
    assert.ok(typeof callback === "function");

    await callback({
      session_id: "sess-123",
      prompt: "Hello, run the tool",
    });

    await new Promise((resolve) => setTimeout(resolve, 10));
    const payloadItems = parsePayloads(capturedBodies);
    const userPromptPayload = payloadItems.find(
      (p) => p.span_name === "user_prompt"
    );
    assert.ok(userPromptPayload);
    assert.equal(userPromptPayload?.trace_unique_id, "sess-123");
    assert.equal(userPromptPayload?.log_type, "task");
    assert.equal(userPromptPayload?.input, "Hello, run the tool");
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("hook lifecycle - PreToolUse and PostToolUse send tool span", async () => {
  const originalFetch = globalThis.fetch;
  const capturedBodies: string[] = [];
  globalThis.fetch = captureFetch(capturedBodies);

  try {
    const exporter = new RespanAnthropicAgentsExporter({
      apiKey: "key",
      endpoint: "https://example.com/ingest",
    });
    const hooks = exporter.createHooks({});

    const preToolHooks = hooks.PreToolUse as Array<{
      hooks?: Array<(input: Record<string, unknown>) => Promise<Record<string, unknown>>>;
    }>;
    const postToolHooks = hooks.PostToolUse as Array<{
      hooks?: Array<(input: Record<string, unknown>) => Promise<Record<string, unknown>>>;
    }>;
    const preCb = preToolHooks[0]?.hooks?.[0];
    const postCb = postToolHooks[0]?.hooks?.[0];
    assert.ok(typeof preCb === "function" && typeof postCb === "function");

    await preCb({
      session_id: "sess-tool",
      tool_use_id: "tool-1",
      tool_name: "get_weather",
      tool_input: { location: "NYC" },
    });
    await postCb({
      session_id: "sess-tool",
      tool_use_id: "tool-1",
      tool_name: "get_weather",
      tool_response: { temp: 72 },
    });

    await new Promise((resolve) => setTimeout(resolve, 10));
    const payloadItems = parsePayloads(capturedBodies);
    const toolPayload = payloadItems.find(
      (p) => p.span_name === "get_weather" && p.log_type === "tool"
    );
    assert.ok(toolPayload);
    assert.equal(toolPayload?.trace_unique_id, "sess-tool");
    assert.deepEqual(toolPayload?.input, { location: "NYC" });
    assert.deepEqual(toolPayload?.output, { temp: 72 });
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("hook lifecycle - SubagentStop sends subagent_stop payload", async () => {
  const originalFetch = globalThis.fetch;
  const capturedBodies: string[] = [];
  globalThis.fetch = captureFetch(capturedBodies);

  try {
    const exporter = new RespanAnthropicAgentsExporter({
      apiKey: "key",
      endpoint: "https://example.com/ingest",
    });
    const hooks = exporter.createHooks({});
    const subagentHooks = hooks.SubagentStop as Array<{
      hooks?: Array<(input: Record<string, unknown>) => Promise<Record<string, unknown>>>;
    }>;
    const cb = subagentHooks[0]?.hooks?.[0];
    assert.ok(typeof cb === "function");

    await cb({
      session_id: "sess-sub",
      agent_id: "agent-1",
      agent_type: "subagent",
    });

    await new Promise((resolve) => setTimeout(resolve, 10));
    const payloadItems = parsePayloads(capturedBodies);
    const subPayload = payloadItems.find(
      (p) => p.span_name === "subagent_stop"
    );
    assert.ok(subPayload);
    assert.equal(subPayload?.trace_unique_id, "sess-sub");
    assert.ok(
      subPayload?.metadata &&
        typeof subPayload.metadata === "object" &&
        (subPayload.metadata as Record<string, unknown>).agent_id === "agent-1"
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("payload serialization - dates and metadata are JSON-serializable", async () => {
  const originalFetch = globalThis.fetch;
  const capturedBodies: string[] = [];
  globalThis.fetch = captureFetch(capturedBodies);

  try {
    const exporter = new RespanAnthropicAgentsExporter({
      apiKey: "key",
      endpoint: "https://example.com/ingest",
    });

    await exporter.trackMessage({
      message: {
        type: "result",
        subtype: "success",
        session_id: "ser-1",
        usage: {},
      },
      sessionId: "ser-1",
    });

    await new Promise((resolve) => setTimeout(resolve, 10));
    assert.ok(capturedBodies.length > 0);
    const raw = capturedBodies[0];
    const parsed = JSON.parse(raw) as { data: Record<string, unknown>[] };
    assert.ok(Array.isArray(parsed.data));
    const first = parsed.data[0] as Record<string, unknown>;
    assert.ok(first);
    assert.ok(typeof first.start_time === "string" || typeof first.start_time === "number");
    assert.ok(typeof first.timestamp === "string" || typeof first.timestamp === "number");
    assert.ok(first.metadata === undefined || typeof first.metadata === "object");
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("payload serialization - assistant message with tool_calls and reasoning", async () => {
  const originalFetch = globalThis.fetch;
  const capturedBodies: string[] = [];
  globalThis.fetch = captureFetch(capturedBodies);

  try {
    const exporter = new RespanAnthropicAgentsExporter({
      apiKey: "key",
      endpoint: "https://example.com/ingest",
    });

    await exporter.trackMessage({
      message: {
        type: "assistant",
        content: [
          { type: "text", text: "Done." },
          {
            type: "tool_use",
            id: "tc-1",
            name: "my_tool",
            input: { x: 1 },
          },
        ],
        model: "claude-3-5-sonnet",
        reasoning: [{ type: "reasoning", thinking: "Consider..." }],
      },
      sessionId: "sess-ast",
    });

    await new Promise((resolve) => setTimeout(resolve, 10));
    const payloadItems = parsePayloads(capturedBodies);
    const genPayload = payloadItems.find(
      (p) => p.span_name === "assistant_message"
    );
    assert.ok(genPayload, "expected assistant_message payload");
    assert.equal(genPayload?.model, "claude-3-5-sonnet");
    assert.ok(Array.isArray(genPayload?.tool_calls));
    assert.ok(genPayload?.metadata && typeof genPayload.metadata === "object", "expected metadata object");
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("retry behavior - uses fetchWithRetry and retries on 5xx then succeeds", async () => {
  const originalFetch = globalThis.fetch;
  let callCount = 0;
  globalThis.fetch = (async (_input: unknown, _init?: RequestInit) => {
    callCount += 1;
    if (callCount === 1) {
      return { status: 503, text: async () => "Unavailable" } as Response;
    }
    return { status: 200, text: async () => "" } as Response;
  }) as typeof fetch;

  try {
    const exporter = new RespanAnthropicAgentsExporter({
      apiKey: "key",
      endpoint: "https://example.com/ingest",
      maxRetries: 3,
      baseDelaySeconds: 0.01,
      maxDelaySeconds: 0.05,
    });

    await exporter.trackMessage({
      message: {
        type: "result",
        subtype: "success",
        session_id: "retry-sess",
        usage: {},
      },
      sessionId: "retry-sess",
    });

    await new Promise((resolve) => setTimeout(resolve, 100));
    assert.ok(callCount >= 2, "fetch should be called at least twice (retry on 5xx then success)");
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("retry behavior - does not retry on 4xx", async () => {
  const originalFetch = globalThis.fetch;
  let callCount = 0;
  globalThis.fetch = (async () => {
    callCount += 1;
    return {
      status: 400,
      text: async () => "Bad Request",
    } as Response;
  }) as typeof fetch;

  try {
    const exporter = new RespanAnthropicAgentsExporter({
      apiKey: "key",
      endpoint: "https://example.com/ingest",
      maxRetries: 3,
    });

    await exporter.trackMessage({
      message: {
        type: "result",
        subtype: "success",
        session_id: "no-retry-sess",
        usage: {},
      },
      sessionId: "no-retry-sess",
    });

    await new Promise((resolve) => setTimeout(resolve, 50));
    assert.equal(callCount, 2, "fetch called once per batch (root + result), no retries on 4xx");
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("withOptions merges hooks into provided options", () => {
  const exporter = new RespanAnthropicAgentsExporter({
    apiKey: "key",
    endpoint: "https://example.com/ingest",
  });
  const options = { someOption: "value" };
  const merged = exporter.withOptions(options);
  assert.equal(merged.someOption, "value");
  assert.ok(merged.hooks);
  assert.ok((merged.hooks as Record<string, unknown[]>).UserPromptSubmit);
});
