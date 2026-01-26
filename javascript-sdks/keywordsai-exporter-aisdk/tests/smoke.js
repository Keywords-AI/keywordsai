import { context, trace } from "@opentelemetry/api";
import { BasicTracerProvider, SimpleSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { KeywordsAIExporter } from "../dist/index.js";

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

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
  const rootPromptText = "Hello from AI SDK exporter smoke test";
  const rootResponseText = "Hello from KeywordsAI!";

  const span = tracer.startSpan("ai.generateText.doGenerate", {
    attributes: {
      "ai.sdk": true,
      "ai.prompt": rootPromptText,
      "ai.prompt.messages": JSON.stringify([
        { role: "user", content: rootPromptText },
      ]),
      "ai.response.text": rootResponseText,
      "ai.model.id": "gpt-4o-mini",
      "gen_ai.usage.input_tokens": 5,
      "gen_ai.usage.output_tokens": 7,
      "ai.response.msToFinish": 2000,
      "ai.telemetry.metadata.userId": "smoke-test-user",
      "ai.telemetry.metadata.customer_email": "smoke-test-user@example.com",
      "ai.telemetry.metadata.customer_name": "Smoke Test User",
    },
  });

  const childPromptText = "Hello from AI SDK exporter child span";
  const childResponseText = "Hello from KeywordsAI child span!";

  const childSpan = tracer.startSpan(
    "ai.chat",
    {
      attributes: {
        "ai.sdk": true,
        "ai.prompt": childPromptText,
        "ai.response.text": childResponseText,
        "ai.prompt.messages": JSON.stringify([
          { role: "user", content: childPromptText },
        ]),
        "ai.model.id": "gpt-4o-mini",
        "gen_ai.usage.input_tokens": 5,
        "gen_ai.usage.output_tokens": 7,
        "ai.response.msToFinish": 2000,
        "ai.telemetry.metadata.userId": "smoke-test-user",
        "ai.telemetry.metadata.customer_email": "smoke-test-user@example.com",
        "ai.telemetry.metadata.customer_name": "Smoke Test User",
        "keywordsai.log_type": "chat",
      },
    },
    trace.setSpan(context.active(), span)
  );

  await delay(500);
  childSpan.end();
  span.end();

  await provider.forceFlush();
  await provider.shutdown();

  console.log("Smoke test span exported.");
}

main().catch((error) => {
  console.error("Smoke test failed:", error);
  process.exit(1);
});
