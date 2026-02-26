import {
  startTracing,
  getClient,
  getCurrentSpan,
  updateCurrentSpan,
  addSpanEvent,
  recordSpanException,
  setSpanStatus,
  withManualSpan,
} from "../src/utils/tracing";
import {
  withWorkflow,
  withTask,
  withTool,
  withAgent,
} from "../src/decorators/base";

// Initialize tracing
startTracing({
  appName: "my-ai-app",
  apiKey: "your-api-key",
  baseURL: "https://api.respan.ai",
  traceContent: true,
  logLevel: "info",
});

// Example 1: Using decorators for automatic tracing
async function processDocument(document: string) {
  return withWorkflow(
    { name: "document-processing" },
    async (doc: string) => {
      console.log("Processing document:", doc);

      // This will create a child span under the workflow
      const summary = await withTask(
        { name: "summarize" },
        async (text: string) => {
          // Update current span with custom attributes
          updateCurrentSpan({
            attributes: {
              "document.length": text.length,
              "document.type": "text",
            },
          });

          // Add an event to track progress
          addSpanEvent("summarization.started", {
            model: "gpt-4",
            max_tokens: 150,
          });

          // Simulate AI processing
          await new Promise((resolve) => setTimeout(resolve, 1000));

          return `Summary of: ${text.substring(0, 50)}...`;
        },
        doc
      );

      // Use a tool to validate the summary
      const isValid = await withTool(
        { name: "validate-summary" },
        async (summary: string) => {
          // Simulate validation logic
          if (summary.length < 10) {
            const error = new Error("Summary too short");
            recordSpanException(error);
            setSpanStatus("ERROR", "Summary validation failed");
            throw error;
          }

          setSpanStatus("OK", "Summary validated successfully");
          return true;
        },
        summary
      );

      return { summary, isValid };
    },
    document
  );
}

// Example 2: Using manual spans for custom operations
async function customOperation() {
  return withManualSpan(
    "custom-database-query",
    async (span) => {
      span.setAttribute("db.operation", "SELECT");
      span.setAttribute("db.table", "documents");

      // Simulate database query
      await new Promise((resolve) => setTimeout(resolve, 500));

      span.addEvent("query.executed", {
        "rows.returned": 42,
      });

      return { count: 42, data: ["doc1", "doc2"] };
    },
    {
      "service.name": "document-service",
      "service.version": "1.0.0",
    }
  );
}

// Example 3: Agent-based processing
async function aiAgent(userQuery: string) {
  return withAgent(
    {
      name: "customer-support-agent",
      version: 1,
      associationProperties: {
        "user.id": "user123",
        "session.id": "session456",
      },
    },
    async (query: string) => {
      // Agent can use multiple tools
      const context = await withTool(
        { name: "retrieve-context" },
        async (q: string) => {
          updateCurrentSpan({
            attributes: {
              "search.query": q,
              "search.type": "semantic",
            },
          });

          return `Context for: ${q}`;
        },
        query
      );

      const response = await withTool(
        { name: "generate-response" },
        async (ctx: string) => {
          addSpanEvent("llm.call.started", {
            model: "gpt-4",
            temperature: 0.7,
          });

          // Simulate LLM call
          await new Promise((resolve) => setTimeout(resolve, 2000));

          addSpanEvent("llm.call.completed", {
            "tokens.used": 150,
            "cost.usd": 0.003,
          });

          return `AI Response based on: ${ctx}`;
        },
        context
      );

      return response;
    },
    userQuery
  );
}

// Example 4: Error handling and span management
async function errorProneOperation() {
  try {
    return withWorkflow({ name: "risky-operation" }, async () => {
      // Get current span for manual manipulation
      const currentSpan = getCurrentSpan();
      console.log("Current span:", currentSpan?.spanContext().spanId);

      // Check if SDK is initialized
      const client = getClient();
      console.log("SDK initialized:", !!client);

      // Simulate an operation that might fail
      const random = Math.random();
      if (random < 0.3) {
        throw new Error("Random failure occurred");
      }

      updateCurrentSpan({
        attributes: {
          "operation.success": true,
          "random.value": random,
        },
      });

      return { success: true, value: random };
    });
  } catch (error) {
    console.error("Operation failed:", error);
    throw error; // Re-throw to maintain error propagation
  }
}

// Example usage
async function main() {
  try {
    console.log("=== Document Processing Example ===");
    const result1 = await processDocument(
      "This is a sample document that needs to be processed and summarized."
    );
    console.log("Result:", result1);

    console.log("\n=== Custom Operation Example ===");
    const result2 = await customOperation();
    console.log("Result:", result2);

    console.log("\n=== AI Agent Example ===");
    const result3 = await aiAgent("How can I reset my password?");
    console.log("Result:", result3);

    console.log("\n=== Error Handling Example ===");
    for (let i = 0; i < 3; i++) {
      try {
        const result4 = await errorProneOperation();
        console.log(`Attempt ${i + 1} succeeded:`, result4);
        break;
      } catch (error) {
        console.log(`Attempt ${i + 1} failed:`, (error as Error).message);
      }
    }
  } catch (error) {
    console.error("Main execution failed:", error);
  }
}

// Run the example
if (require.main === module) {
  main()
    .then(() => {
      console.log(
        "\nExample completed. Check your Respan dashboard for traces!"
      );
      process.exit(0);
    })
    .catch((error) => {
      console.error("Example failed:", error);
      process.exit(1);
    });
}

export { processDocument, customOperation, aiAgent, errorProneOperation };
