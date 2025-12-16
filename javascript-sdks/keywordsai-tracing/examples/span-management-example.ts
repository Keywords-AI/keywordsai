/**
 * Example demonstrating span management with getClient() API
 * 
 * This example shows how to:
 * - Get current trace and span IDs
 * - Update spans with KeywordsAI parameters
 * - Add events to track progress
 * - Record exceptions
 */

import { KeywordsAITelemetry, getClient } from "../src/index.js";
import OpenAI from "openai";

// Initialize KeywordsAI
const keywordsAi = new KeywordsAITelemetry({
  apiKey: process.env.KEYWORDSAI_API_KEY,
  baseURL: process.env.KEYWORDSAI_BASE_URL,
  appName: "span-management-example",
  logLevel: "info",
});

await keywordsAi.initialize();

// Initialize OpenAI
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Example workflow that uses span management
const processUserRequest = async (userId: string, query: string) => {
  return await keywordsAi.withWorkflow(
    { name: "process_user_request", version: 1 },
    async () => {
      // Get the client for span management
      const client = getClient();

      // Get current trace information
      const traceId = client.getCurrentTraceId();
      const spanId = client.getCurrentSpanId();

      console.log(`Processing request in trace: ${traceId}`);
      console.log(`Current span: ${spanId}`);

      // Update span with KeywordsAI parameters
      client.updateCurrentSpan({
        keywordsaiParams: {
          customerIdentifier: userId,
          traceGroupIdentifier: "user-queries",
          metadata: {
            query_type: "ai-powered",
            environment: "production",
            version: "1.0.0",
          },
        },
      });

      // Add event to track progress
      client.addEvent("validation_started", {
        user_id: userId,
        query_length: query.length,
      });

      // Validate input
      if (!query || query.length === 0) {
        const error = new Error("Empty query provided");
        client.recordException(error);
        throw error;
      }

      client.addEvent("validation_completed", {
        status: "success",
      });

      // Process with AI
      try {
        client.addEvent("ai_processing_started", {
          model: "gpt-3.5-turbo",
        });

        const response = await openai.chat.completions.create({
          model: "gpt-3.5-turbo",
          messages: [
            {
              role: "user",
              content: query,
            },
          ],
          max_tokens: 150,
        });

        const result = response.choices[0].message.content;

        // Update span with results
        client.updateCurrentSpan({
          attributes: {
            "result.length": result?.length || 0,
            "result.tokens": response.usage?.total_tokens || 0,
          },
        });

        client.addEvent("ai_processing_completed", {
          status: "success",
          tokens_used: response.usage?.total_tokens,
        });

        return {
          traceId,
          userId,
          query,
          result,
          tokensUsed: response.usage?.total_tokens,
        };
      } catch (error) {
        client.addEvent("ai_processing_failed", {
          error: (error as Error).message,
        });

        // Record the exception on the span
        client.recordException(error as Error);
        throw error;
      }
    }
  );
};

// Example usage
const main = async () => {
  try {
    console.log("\n=== Span Management Example ===\n");

    // Example 1: Successful request
    console.log("Example 1: Successful request");
    const result1 = await processUserRequest(
      "user-123",
      "What is OpenTelemetry?"
    );
    console.log("Result:", result1);

    // Example 2: Request with error
    console.log("\nExample 2: Request with error (empty query)");
    try {
      await processUserRequest("user-456", "");
    } catch (error) {
      console.log("Caught expected error:", (error as Error).message);
    }

    // Example 3: Multiple requests showing different trace IDs
    console.log("\nExample 3: Multiple requests with different trace IDs");
    const result3a = await processUserRequest(
      "user-789",
      "Explain tracing in simple terms"
    );
    const result3b = await processUserRequest(
      "user-789",
      "What are spans in OpenTelemetry?"
    );
    console.log("Result 3a trace:", result3a.traceId);
    console.log("Result 3b trace:", result3b.traceId);

    console.log("\n=== All examples completed ===\n");
  } catch (error) {
    console.error("Unexpected error:", error);
  } finally {
    // Flush and shutdown
    await keywordsAi.shutdown();
    console.log("SDK shut down");
  }
};

main();


