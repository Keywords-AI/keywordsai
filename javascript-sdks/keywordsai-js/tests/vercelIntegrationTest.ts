import { KeywordsAIExporter } from "@keywordsai/tracing";
import { registerOTel } from "@vercel/otel";
import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";

export function register() {
  registerOTel({
    serviceName: "keywords-ai-nextjs-example",
    traceExporter: new KeywordsAIExporter({
      debug: true,
      url: "http://localhost:8000/api/integrations/v1/traces/ingest",
      apiKey: process.env.KEYWORDSAI_API_KEY_TEST,
    }),
  });
}

async function main() {
  register();
  const result = await generateText({
    model: openai("gpt-4o-mini"),
    prompt: "Hello, world!",
    experimental_telemetry: {
      isEnabled: true,
    },
  });
  console.log(result);
}

main();

