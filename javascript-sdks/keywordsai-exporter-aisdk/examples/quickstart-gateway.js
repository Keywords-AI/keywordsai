import { context, trace } from "@opentelemetry/api";
import { AsyncLocalStorageContextManager } from "@opentelemetry/context-async-hooks";
import {
  BasicTracerProvider,
  SimpleSpanProcessor,
} from "@opentelemetry/sdk-trace-base";
import { KeywordsAIExporter } from "../dist/index.js";
import { generateText } from "ai";
import { createOpenAI } from "@ai-sdk/openai";

/**
 * Quickstart (Gateway + AI SDK telemetry).
 *
 * This does a REAL AI SDK call routed through the KeywordsAI gateway (OpenAI-compatible),
 * with AI SDK telemetry enabled, and exports the resulting spans to KeywordsAI.
 *
 * Prereqs:
 * - npm install
 * - npm run build
 * - npm i ai @ai-sdk/openai
 *
 * Env:
 * - KEYWORDSAI_API_KEY (required)
 * - KEYWORDSAI_GATEWAY_BASE_URL (optional, defaults to https://api.keywordsai.co)
 * - KEYWORDSAI_INGEST_BASE_URL (optional, defaults to https://api.keywordsai.co/api)
 */
async function main() {
  const apiKey = process.env.KEYWORDSAI_API_KEY;
  if (!apiKey) {
    console.error("Missing KEYWORDSAI_API_KEY");
    process.exit(1);
  }

  // IMPORTANT: AI SDK telemetry uses async operations; without an async context manager,
  // nested spans can lose parent context and show up as separate traces.
  context.setGlobalContextManager(new AsyncLocalStorageContextManager().enable());

  // 1) Configure the exporter (this sends spans to KeywordsAI ingest).
  const ingestBaseUrl = process.env.KEYWORDSAI_INGEST_BASE_URL || "https://api.keywordsai.co/api";
  const exporter = new KeywordsAIExporter({
    apiKey,
    baseUrl: ingestBaseUrl,
    debug: true,
  });

  // 2) Register a global tracer provider so AI SDK telemetry has somewhere to export spans.
  const provider = new BasicTracerProvider({
    spanProcessors: [new SimpleSpanProcessor(exporter)],
  });
  trace.setGlobalTracerProvider(provider);

  // 3) Configure AI SDK OpenAI provider to route through KeywordsAI gateway.
  // KeywordsAI gateway is OpenAI-compatible and expects baseURL like: https://api.keywordsai.co/api/
  const gatewayBase =
    (process.env.KEYWORDSAI_GATEWAY_BASE_URL || "https://api.keywordsai.co").replace(/\/$/, "");
  const gatewayBaseURL = gatewayBase.endsWith("/api")
    ? `${gatewayBase}/`
    : `${gatewayBase}/api/`;

  const keywordsaiOpenAI = createOpenAI({
    apiKey,
    baseURL: gatewayBaseURL,
  });

  // 4) Make a real AI SDK call with telemetry enabled.
  const result = await generateText({
    model: keywordsaiOpenAI("gpt-4o-mini"),
    prompt: "Hello from AI SDK via KeywordsAI gateway!",
    experimental_telemetry: {
      isEnabled: true,
      metadata: {
        userId: "quickstart-user",
        integration: "keywordsai-exporter-aisdk",
      },
    },
  });

  console.log(result.text);

  // Ensure spans are exported before exiting.
  await provider.forceFlush();
  await provider.shutdown();

  console.log("Gateway quickstart completed (spans exported).");
}

main().catch((err) => {
  console.error("Gateway quickstart failed:", err);
  process.exit(1);
});

