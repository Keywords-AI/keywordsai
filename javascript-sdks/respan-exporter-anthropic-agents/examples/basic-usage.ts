/**
 * Basic usage example for @respan/exporter-anthropic-agents.
 *
 * Demonstrates three ways to use the exporter:
 *   1. Hooks-based (automatic) - exporter attaches to SDK hooks
 *   2. Manual tracking          - you call trackMessage() on each event
 *   3. Wrapped query            - exporter.query() does both
 *
 * Prerequisites:
 *   yarn add @anthropic-ai/claude-agent-sdk @respan/respan-sdk @respan/exporter-anthropic-agents
 *
 * Environment variables:
 *   RESPAN_API_KEY   (or KEYWORDSAI_API_KEY) - your Respan ingest key
 *   ANTHROPIC_API_KEY                        - your Anthropic API key
 *
 * Run:
 *   npx tsx examples/basic-usage.ts
 */

import { query } from "@anthropic-ai/claude-agent-sdk";
import { RespanAnthropicAgentsExporter } from "../src/index.js";

async function exampleHooksBased(): Promise<void> {
  console.log("\n=== Example 1: Hooks-based (automatic) ===\n");

  const exporter = new RespanAnthropicAgentsExporter(); // reads RESPAN_API_KEY from env

  const options = exporter.withOptions({
    permissionMode: "bypassPermissions",
    maxTurns: 1,
  });

  for await (const message of query({ prompt: "What is 2 + 2?", options })) {
    const msg = message as Record<string, unknown>;
    console.log(`  ${msg.type ?? "unknown"}`);
  }

  console.log("\n  Traces exported to Respan automatically via hooks");
}

async function exampleManualTracking(): Promise<void> {
  console.log("\n=== Example 2: Manual tracking ===\n");

  const exporter = new RespanAnthropicAgentsExporter();
  let sessionId: string | undefined;

  for await (const message of query({
    prompt: "Say hello",
    options: { permissionMode: "bypassPermissions", maxTurns: 1 } as any,
  })) {
    const msg = message as Record<string, unknown>;

    // Extract session ID
    if (msg.type === "system") {
      const data = (msg.data ?? {}) as Record<string, unknown>;
      sessionId = (data.session_id ?? data.sessionId ?? sessionId) as string;
    }
    if (msg.type === "result") {
      sessionId = (msg.session_id ?? sessionId) as string;
    }

    // Export every message
    await exporter.trackMessage({ message, sessionId });
    console.log(`  Tracked: ${msg.type}`);
  }

  console.log(`\n  All messages exported under session ${sessionId}`);
}

async function exampleWrappedQuery(): Promise<void> {
  console.log("\n=== Example 3: Wrapped query (simplest) ===\n");

  const exporter = new RespanAnthropicAgentsExporter();

  for await (const message of exporter.query({
    prompt: "What day is today?",
    options: { permissionMode: "bypassPermissions", maxTurns: 1 } as any,
  })) {
    const msg = message as Record<string, unknown>;
    console.log(`  ${msg.type ?? "unknown"}`);
  }

  console.log("\n  Done - all traces exported automatically");
}

async function main(): Promise<void> {
  const apiKey = process.env.RESPAN_API_KEY || process.env.KEYWORDSAI_API_KEY;
  if (!apiKey) {
    console.log("Set RESPAN_API_KEY (or KEYWORDSAI_API_KEY) to export traces.");
    console.log("Running anyway - exporter will warn and skip uploads.\n");
  }

  await exampleHooksBased();
  await exampleManualTracking();
  await exampleWrappedQuery();
}

main().catch(console.error);
