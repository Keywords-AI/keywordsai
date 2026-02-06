/**
 * Example demonstrating multi-processor routing
 * 
 * This example shows how to:
 * - Add multiple processors with different destinations
 * - Route spans to specific processors by name
 * - Use custom filter functions
 * - Send spans to multiple destinations
 */

import { KeywordsAITelemetry } from "../src/index.js";
import {
  SpanExporter,
  SpanExportResult,
  ReadableSpan,
} from "@opentelemetry/sdk-trace-base";
import * as fs from "fs";
import * as path from "path";

// Custom file exporter that writes spans to a JSON file
class FileExporter implements SpanExporter {
  private filepath: string;

  constructor(filepath: string) {
    this.filepath = filepath;
    // Ensure directory exists
    const dir = path.dirname(filepath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  export(
    spans: ReadableSpan[],
    resultCallback: (result: SpanExportResult) => void
  ): void {
    try {
      const spanData = spans.map((span) => ({
        name: span.name,
        traceId: span.spanContext().traceId,
        spanId: span.spanContext().spanId,
        attributes: Object.fromEntries(
          Object.entries(span.attributes).map(([k, v]) => [k, String(v)])
        ),
        timestamp: new Date().toISOString(),
      }));

      // Append to file
      fs.appendFileSync(
        this.filepath,
        spanData.map((s) => JSON.stringify(s)).join("\n") + "\n"
      );

      console.log(`[FileExporter] Wrote ${spans.length} spans to ${this.filepath}`);
      resultCallback({ code: SpanExportResult.SUCCESS });
    } catch (error) {
      console.error("[FileExporter] Error:", error);
      resultCallback({ code: SpanExportResult.FAILED });
    }
  }

  shutdown(): Promise<void> {
    return Promise.resolve();
  }

  forceFlush(): Promise<void> {
    return Promise.resolve();
  }
}

// Custom console exporter that prints spans to console
class ConsoleExporter implements SpanExporter {
  private prefix: string;

  constructor(prefix: string = "ConsoleExporter") {
    this.prefix = prefix;
  }

  export(
    spans: ReadableSpan[],
    resultCallback: (result: SpanExportResult) => void
  ): void {
    for (const span of spans) {
      console.log(`[${this.prefix}] Span: ${span.name}`);
      console.log(`  Trace ID: ${span.spanContext().traceId}`);
      console.log(`  Attributes:`, span.attributes);
    }
    resultCallback({ code: SpanExportResult.SUCCESS });
  }

  shutdown(): Promise<void> {
    return Promise.resolve();
  }

  forceFlush(): Promise<void> {
    return Promise.resolve();
  }
}

// Initialize KeywordsAI with default processor
const keywordsAi = new KeywordsAITelemetry({
  apiKey: process.env.KEYWORDSAI_API_KEY,
  baseURL: process.env.KEYWORDSAI_BASE_URL,
  appName: "multi-processor-example",
  logLevel: "info",
});

await keywordsAi.initialize();

// Add debug processor - only receives spans with processors="debug"
keywordsAi.addProcessor({
  exporter: new FileExporter("./debug-spans.jsonl"),
  name: "debug",
});

// Add analytics processor - only receives spans with processors="analytics"
keywordsAi.addProcessor({
  exporter: new ConsoleExporter("Analytics"),
  name: "analytics",
});

// Add slow span processor - uses custom filter
keywordsAi.addProcessor({
  exporter: new ConsoleExporter("SlowSpans"),
  name: "slow",
  filter: (span) => {
    // Only process spans that took more than 100ms
    const duration = span.endTime[0] - span.startTime[0];
    return duration > 0.1; // seconds
  },
});

// Example workflows demonstrating processor routing

// This goes to default KeywordsAI processor only
const normalTask = async () => {
  return await keywordsAi.withTask({ name: "normal_task" }, async () => {
    console.log("Executing normal task (default processor)");
    await new Promise((resolve) => setTimeout(resolve, 50));
    return "normal result";
  });
};

// This goes to debug processor only
const debugTask = async () => {
  return await keywordsAi.withTask(
    {
      name: "debug_task",
      processors: "debug", // Route to debug processor
    },
    async () => {
      console.log("Executing debug task (debug processor)");
      await new Promise((resolve) => setTimeout(resolve, 50));
      return "debug result";
    }
  );
};

// This goes to both debug and analytics processors
const multiTask = async () => {
  return await keywordsAi.withTask(
    {
      name: "multi_task",
      processors: ["debug", "analytics"], // Route to multiple processors
    },
    async () => {
      console.log("Executing multi task (debug + analytics processors)");
      await new Promise((resolve) => setTimeout(resolve, 50));
      return "multi result";
    }
  );
};

// This is slow and goes to slow processor (via filter)
const slowTask = async () => {
  return await keywordsAi.withTask(
    {
      name: "slow_task",
      processors: "slow", // Route to slow processor
    },
    async () => {
      console.log("Executing slow task (slow processor with filter)");
      await new Promise((resolve) => setTimeout(resolve, 200)); // Takes 200ms
      return "slow result";
    }
  );
};

// Main workflow that combines all tasks
const mainWorkflow = async () => {
  return await keywordsAi.withWorkflow(
    {
      name: "multi_processor_demo",
      version: 1,
    },
    async () => {
      console.log("\n=== Multi-Processor Routing Demo ===\n");

      // Execute tasks with different routing
      const result1 = await normalTask();
      console.log("Normal task result:", result1);

      const result2 = await debugTask();
      console.log("Debug task result:", result2);

      const result3 = await multiTask();
      console.log("Multi task result:", result3);

      const result4 = await slowTask();
      console.log("Slow task result:", result4);

      console.log("\n=== All tasks completed ===\n");

      return {
        normal: result1,
        debug: result2,
        multi: result3,
        slow: result4,
      };
    }
  );
};

// Execute the workflow
mainWorkflow()
  .then((results) => {
    console.log("Workflow results:", results);
  })
  .catch((error) => {
    console.error("Workflow error:", error);
  })
  .finally(async () => {
    // Shutdown and flush
    await keywordsAi.shutdown();
    console.log("\n SDK shut down");
    console.log("Check debug-spans.jsonl for debug spans");
  });


