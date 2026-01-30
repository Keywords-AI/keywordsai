import { context, trace } from "@opentelemetry/api";
import {
  BasicTracerProvider,
  SimpleSpanProcessor,
} from "@opentelemetry/sdk-trace-base";
import { KeywordsAIExporter } from "../dist/index.js";

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Quickstart script (local).
 *
 * Prereqs:
 * - npm install
 * - npm run build
 *
 * Env:
 * - KEYWORDSAI_API_KEY (required)
 * - KEYWORDSAI_BASE_URL (optional, defaults to https://api.keywordsai.co/api)
 */
async function main() {
  const apiKey = process.env.KEYWORDSAI_API_KEY;
  if (!apiKey) {
    console.error("Missing KEYWORDSAI_API_KEY");
    process.exit(1);
  }

  const exporter = new KeywordsAIExporter({
    apiKey,
    baseUrl: process.env.KEYWORDSAI_BASE_URL,
    debug: true,
  });

  const provider = new BasicTracerProvider({
    spanProcessors: [new SimpleSpanProcessor(exporter)],
  });

  const tracer = provider.getTracer("ai");

  // Example 1: a generation span (will infer log_type: "generation")
  const rootPromptText = "Hello from AI SDK exporter quickstart";
  const rootResponseText = "Hello from KeywordsAI!";

  const generationSpan = tracer.startSpan("ai.generateText.doGenerate", {
    attributes: {
      "ai.sdk": true,
      "ai.prompt": rootPromptText,
      "ai.prompt.messages": JSON.stringify([{ role: "user", content: rootPromptText }]),
      "ai.response.text": rootResponseText,
      "ai.model.id": "gpt-4o-mini",
      "gen_ai.usage.input_tokens": 5,
      "gen_ai.usage.output_tokens": 7,
      "ai.response.msToFinish": 1200,
      "ai.telemetry.metadata.userId": "quickstart-user",
      "ai.telemetry.metadata.customer_email": "quickstart-user@example.com",
      "ai.telemetry.metadata.customer_name": "Quickstart User",
    },
  });

  // Example 2: an explicit log_type override (e.g. "chat")
  const chatSpan = tracer.startSpan(
    "ai.chat",
    {
      attributes: {
        "ai.sdk": true,
        "ai.prompt": "Say hi",
        "ai.prompt.messages": JSON.stringify([{ role: "user", content: "Say hi" }]),
        "ai.response.text": "Hi!",
        "ai.model.id": "gpt-4o-mini",
        "gen_ai.usage.input_tokens": 2,
        "gen_ai.usage.output_tokens": 2,
        "ai.response.msToFinish": 200,
        "ai.telemetry.metadata.userId": "quickstart-user",
        "keywordsai.log_type": "chat",
      },
    },
    trace.setSpan(context.active(), generationSpan)
  );

  await delay(50);
  chatSpan.end();
  generationSpan.end();

  // Ensure everything is exported before exiting
  await provider.forceFlush();
  await provider.shutdown();

  console.log("Quickstart spans exported.");
}

main().catch((err) => {
  console.error("Quickstart failed:", err);
  process.exit(1);
});

