/**
 * Gateway integration example for @respan/exporter-anthropic-agents.
 *
 * Routes Claude Agent SDK traffic through the Respan gateway instead of
 * hitting Anthropic directly. Only a Respan API key is needed.
 *
 * Prerequisites:
 *   yarn add @anthropic-ai/claude-agent-sdk @respan/respan-sdk @respan/exporter-anthropic-agents
 *
 * Environment variables (required):
 *   RESPAN_API_KEY   (or KEYWORDSAI_API_KEY) - your Respan key
 *
 * Environment variables (optional):
 *   RESPAN_BASE_URL  - gateway base URL (default: https://api.respan.ai)
 *
 * Run:
 *   npx tsx examples/gateway-integration.ts
 */

import { query } from "@anthropic-ai/claude-agent-sdk";
import { RespanAnthropicAgentsExporter } from "../src/index.js";

async function main(): Promise<void> {
  const apiKey = process.env.RESPAN_API_KEY || process.env.KEYWORDSAI_API_KEY;
  if (!apiKey) {
    console.error("ERROR: Set RESPAN_API_KEY (or KEYWORDSAI_API_KEY)");
    process.exit(1);
  }

  const baseUrl = (
    process.env.RESPAN_BASE_URL ||
    process.env.KEYWORDSAI_BASE_URL ||
    "https://api.respan.ai"
  ).replace(/\/+$/, "");

  console.log(`Gateway base URL: ${baseUrl}`);
  console.log(`API key: ${apiKey.slice(0, 8)}...`);

  const exporter = new RespanAnthropicAgentsExporter({
    apiKey,
    endpoint: `${baseUrl}/api/v1/traces/ingest`,
  });

  // Route Claude SDK through the Respan gateway
  const options = exporter.withOptions({
    permissionMode: "bypassPermissions",
    maxTurns: 1,
    env: {
      ANTHROPIC_BASE_URL: baseUrl,
      ANTHROPIC_AUTH_TOKEN: apiKey,
      ANTHROPIC_API_KEY: apiKey,
    },
  } as any);

  console.log("\nSending query through gateway...\n");

  let sessionId: string | undefined;

  for await (const message of query({ prompt: "Reply with exactly: gateway_ok", options })) {
    const msg = message as Record<string, unknown>;

    if (msg.type === "system") {
      const data = (msg.data ?? {}) as Record<string, unknown>;
      sessionId = (data.session_id ?? data.sessionId ?? sessionId) as string;
    }
    if (msg.type === "result") {
      sessionId = (msg.session_id ?? sessionId) as string;
      const usage = msg.usage as Record<string, unknown> | undefined;
      console.log(`  Result: subtype=${msg.subtype}, turns=${msg.num_turns}`);
      if (usage) {
        console.log(`  Usage: input_tokens=${usage.input_tokens}, output_tokens=${usage.output_tokens}`);
      }
    }

    await exporter.trackMessage({ message, sessionId });
    console.log(`  ${msg.type}`);
  }

  console.log(`\nTraces exported to Respan under session ${sessionId}`);
  console.log(`View at: https://platform.respan.ai/traces/${sessionId}`);
}

main().catch(console.error);
