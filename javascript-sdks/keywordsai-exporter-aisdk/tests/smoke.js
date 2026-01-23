import { BasicTracerProvider, SimpleSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { KeywordsAIExporter } from "../dist/index.js";

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

  const provider = new BasicTracerProvider();
  provider.addSpanProcessor(new SimpleSpanProcessor(exporter));
  provider.register();

  const tracer = provider.getTracer("ai");
  const span = tracer.startSpan("ai.generateText.doGenerate", {
    attributes: {
      "ai.sdk": true,
      "ai.prompt": "Hello from AI SDK exporter smoke test",
      "ai.prompt.messages": JSON.stringify([
        { role: "user", content: "Hello from AI SDK exporter smoke test" },
      ]),
      "ai.response.text": "Hello from KeywordsAI!",
      "ai.model.id": "gpt-4o-mini",
      "gen_ai.usage.input_tokens": 5,
      "gen_ai.usage.output_tokens": 7,
      "ai.response.msToFinish": 500,
      "ai.telemetry.metadata.userId": "smoke-test-user",
    },
  });

  span.end();

  await provider.forceFlush();
  await provider.shutdown();

  console.log("Smoke test span exported.");
}

main().catch((error) => {
  console.error("Smoke test failed:", error);
  process.exit(1);
});
