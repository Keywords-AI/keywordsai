import { updateCurrentSpan } from "../src/utils/tracing";
import { withAgent } from "../src/decorators/base";
import { SpanStatusCode } from "@opentelemetry/api";

// Example 5: Advanced span updating with KeywordsAI parameters
async function advancedSpanUpdating() {
  console.log("\n=== Example 5: Advanced Span Updating ===");

  return withAgent(
    {
      name: "advancedAgent",
      associationProperties: {
        userId: "user123",
        sessionId: "session456",
      },
    },
    async () => {
      // Update span with KeywordsAI-specific parameters
      updateCurrentSpan({
        keywordsaiParams: {
          model: "gpt-4",
          provider: "openai",
          temperature: 0.7,
          max_tokens: 1000,
          user_id: "user123",
          metadata: {
            experiment: "A/B-test-v1",
            feature_flag: "new_ui_enabled",
          },
        },
        attributes: {
          "custom.operation": "llm_call",
          "custom.priority": "high",
        },
      });

      // Simulate some processing
      await new Promise((resolve) => setTimeout(resolve, 100));

      // Update span name and status during processing
      updateCurrentSpan({
        name: "advancedAgent.processing",
        attributes: {
          "processing.stage": "analysis",
        },
      });

      // Simulate successful completion
      updateCurrentSpan({
        status: SpanStatusCode.OK,
        statusDescription: "Processing completed successfully",
        attributes: {
          "processing.stage": "completed",
          "result.count": 42,
        },
      });

      return {
        result: "Advanced processing completed",
        processed_items: 42,
        model_used: "gpt-4",
      };
    }
  );
}

async function main() {
  // ... existing examples ...

  // Run the new advanced span updating example
  try {
    const result5 = await advancedSpanUpdating();
    console.log("Advanced span updating result:", result5);
  } catch (error) {
    console.error("Advanced span updating failed:", error);
  }

  // ... existing code ...
}
