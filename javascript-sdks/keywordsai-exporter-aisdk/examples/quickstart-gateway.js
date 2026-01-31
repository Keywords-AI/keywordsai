import { context, trace } from "@opentelemetry/api";
import { AsyncLocalStorageContextManager } from "@opentelemetry/context-async-hooks";
import {
  BasicTracerProvider,
  SimpleSpanProcessor,
} from "@opentelemetry/sdk-trace-base";
import { KeywordsAIExporter } from "../dist/index.js";
import { generateText } from "ai";
import { createOpenAI } from "@ai-sdk/openai";

async function main() {
  const apiKey = process.env.KEYWORDSAI_API_KEY;
  if (!apiKey) {
    console.error("Missing KEYWORDSAI_API_KEY");
    process.exit(1);
  }

  context.setGlobalContextManager(new AsyncLocalStorageContextManager().enable());

  const ingestBaseUrl =
    process.env.KEYWORDSAI_INGEST_BASE_URL || "https://api.keywordsai.co/api";
  const exporter = new KeywordsAIExporter({
    apiKey,
    baseUrl: ingestBaseUrl,
    debug: true,
  });

  const provider = new BasicTracerProvider({
    spanProcessors: [new SimpleSpanProcessor(exporter)],
  });
  trace.setGlobalTracerProvider(provider);

  const gatewayBase =
    (process.env.KEYWORDSAI_GATEWAY_BASE_URL || "https://api.keywordsai.co").replace(
      /\/$/,
      ""
    );
  const gatewayBaseURL = gatewayBase.endsWith("/api")
    ? `${gatewayBase}/`
    : `${gatewayBase}/api/`;

  const keywordsaiOpenAI = createOpenAI({
    apiKey,
    baseURL: gatewayBaseURL,
  });

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

  await provider.forceFlush();
  await provider.shutdown();

  console.log("Gateway quickstart completed (spans exported).");
}

main().catch((err) => {
  console.error("Gateway quickstart failed:", err);
  process.exit(1);
});

