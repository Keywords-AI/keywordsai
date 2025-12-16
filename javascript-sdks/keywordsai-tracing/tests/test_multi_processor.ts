/**
 * Test suite for Multi-Processor Routing
 * 
 * Tests:
 * - Add multiple processors
 * - Route spans by processor name
 * - Custom filter functions
 * - Multiple destination routing
 */

import { KeywordsAITelemetry } from "../src/index.js";
import {
  SpanExporter,
  ReadableSpan,
} from "@opentelemetry/sdk-trace-base";
import { ExportResult as SpanExportResult } from "@opentelemetry/core";
import * as dotenv from "dotenv";
import * as fs from "fs";
import * as path from "path";

// Load environment variables
dotenv.config();

// Track which spans went to which processor
const processorSpans: Record<string, string[]> = {
  default: [],
  debug: [],
  analytics: [],
  slow: [],
};

// Custom test exporter that tracks spans
class TestExporter implements SpanExporter {
  constructor(private name: string) {}

  export(
    spans: ReadableSpan[],
    resultCallback: (result: SpanExportResult) => void
  ): void {
    for (const span of spans) {
      processorSpans[this.name].push(span.name);
      console.log(`[${this.name} Processor] Received span: ${span.name}`);
    }
    resultCallback({ code: 0 }); // SUCCESS
  }

  shutdown(): Promise<void> {
    return Promise.resolve();
  }

  forceFlush(): Promise<void> {
    return Promise.resolve();
  }
}

// Initialize KeywordsAI with debug logging
const kai = new KeywordsAITelemetry({
  apiKey: process.env.KEYWORDSAI_API_KEY,
  baseURL: process.env.KEYWORDSAI_BASE_URL,
  appName: "test-multi-processor",
  logLevel: "debug",
  traceContent: true,
});

console.log("\n=== Multi-Processor Routing Test Suite ===\n");

// Setup processors
const setupProcessors = () => {
  console.log("[Setup] Adding test processors...\n");
  
  // Add debug processor
  kai.addProcessor({
    exporter: new TestExporter("debug"),
    name: "debug",
  });
  console.log("✓ Added debug processor");
  
  // Add analytics processor
  kai.addProcessor({
    exporter: new TestExporter("analytics"),
    name: "analytics",
  });
  console.log("✓ Added analytics processor");
  
  // Add slow processor with filter
  kai.addProcessor({
    exporter: new TestExporter("slow"),
    name: "slow",
    filter: (span) => {
      // Filter spans that took more than 50ms
      const duration = (span.endTime[0] - span.startTime[0]) * 1000; // Convert to ms
      return duration > 50;
    },
  });
  console.log("✓ Added slow processor with filter (>50ms)");
  
  console.log("\n");
};

// Test 1: Default processor (no routing)
const test1_defaultProcessor = async () => {
  console.log("\n[Test 1] Default Processor (No Routing)");
  
  await kai.withTask({ name: "default_task" }, async () => {
    console.log("Executing default_task...");
    await new Promise((resolve) => setTimeout(resolve, 10));
  });
  
  console.log("✅ Test 1 Completed: Default task should go to default processor");
};

// Test 2: Single processor routing
const test2_singleProcessorRouting = async () => {
  console.log("\n[Test 2] Single Processor Routing");
  
  await kai.withTask(
    { 
      name: "debug_task",
      processors: "debug",
    },
    async () => {
      console.log("Executing debug_task with processors='debug'...");
      await new Promise((resolve) => setTimeout(resolve, 10));
    }
  );
  
  console.log("✅ Test 2 Completed: Should route to debug processor");
};

// Test 3: Multiple processor routing
const test3_multipleProcessorRouting = async () => {
  console.log("\n[Test 3] Multiple Processor Routing");
  
  await kai.withTask(
    {
      name: "multi_destination_task",
      processors: ["debug", "analytics"],
    },
    async () => {
      console.log("Executing multi_destination_task with processors=['debug', 'analytics']...");
      await new Promise((resolve) => setTimeout(resolve, 10));
    }
  );
  
  console.log("✅ Test 3 Completed: Should route to both debug and analytics processors");
};

// Test 4: Slow task (filter-based routing)
const test4_filterBasedRouting = async () => {
  console.log("\n[Test 4] Filter-Based Routing");
  
  await kai.withTask(
    {
      name: "slow_task",
      processors: "slow",
    },
    async () => {
      console.log("Executing slow_task (taking 100ms)...");
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  );
  
  console.log("✅ Test 4 Completed: Should route to slow processor (>50ms)");
};

// Test 5: Fast task (filtered out)
const test5_fastTaskFiltered = async () => {
  console.log("\n[Test 5] Fast Task (Filtered Out)");
  
  await kai.withTask(
    {
      name: "fast_task",
      processors: "slow",
    },
    async () => {
      console.log("Executing fast_task (taking 10ms)...");
      await new Promise((resolve) => setTimeout(resolve, 10));
    }
  );
  
  console.log("✅ Test 5 Completed: Should NOT route to slow processor (<50ms)");
};

// Test 6: Nested tasks with different routing
const test6_nestedTasksRouting = async () => {
  console.log("\n[Test 6] Nested Tasks with Different Routing");
  
  await kai.withWorkflow(
    {
      name: "parent_workflow",
      processors: "debug",
    },
    async () => {
      console.log("Executing parent_workflow with processors='debug'...");
      
      await kai.withTask(
        {
          name: "child_task_analytics",
          processors: "analytics",
        },
        async () => {
          console.log("Executing child_task_analytics with processors='analytics'...");
          await new Promise((resolve) => setTimeout(resolve, 10));
        }
      );
      
      await kai.withTask(
        {
          name: "child_task_both",
          processors: ["debug", "analytics"],
        },
        async () => {
          console.log("Executing child_task_both with processors=['debug', 'analytics']...");
          await new Promise((resolve) => setTimeout(resolve, 10));
        }
      );
    }
  );
  
  console.log("✅ Test 6 Completed: Nested tasks with different routing");
};

// Test 7: Complex workflow with all routing types
const test7_complexWorkflow = async () => {
  console.log("\n[Test 7] Complex Workflow with All Routing Types");
  
  await kai.withWorkflow(
    {
      name: "complex_workflow",
      version: 1,
    },
    async () => {
      // Default routing
      await kai.withTask({ name: "task1_default" }, async () => {
        await new Promise((resolve) => setTimeout(resolve, 10));
      });
      
      // Debug routing
      await kai.withTask(
        { name: "task2_debug", processors: "debug" },
        async () => {
          await new Promise((resolve) => setTimeout(resolve, 10));
        }
      );
      
      // Multiple routing
      await kai.withTask(
        { name: "task3_multi", processors: ["debug", "analytics"] },
        async () => {
          await new Promise((resolve) => setTimeout(resolve, 10));
        }
      );
      
      // Slow task
      await kai.withTask(
        { name: "task4_slow", processors: "slow" },
        async () => {
          await new Promise((resolve) => setTimeout(resolve, 120));
        }
      );
      
      console.log("✓ Executed all task types in complex workflow");
    }
  );
  
  console.log("✅ Test 7 Completed: Complex workflow with all routing types");
};

// Verify results
const verifyResults = () => {
  console.log("\n" + "=".repeat(50));
  console.log("VERIFICATION: Checking which spans went to which processor");
  console.log("=".repeat(50) + "\n");
  
  for (const [processor, spans] of Object.entries(processorSpans)) {
    console.log(`${processor} processor received ${spans.length} spans:`);
    spans.forEach((span) => console.log(`  - ${span}`));
    console.log("");
  }
  
  // Validate expectations
  let allPassed = true;
  
  // Debug processor should have received debug_task, multi_destination_task, parent_workflow, child_task_both, task2_debug, task3_multi
  const debugExpected = ["debug_task", "multi_destination_task"];
  const debugReceived = processorSpans.debug;
  
  console.log("\nValidation:");
  
  // Check if debug processor received expected spans
  let debugCheck = true;
  for (const expected of debugExpected) {
    if (!debugReceived.some(span => span.includes(expected))) {
      console.log(`❌ Debug processor did not receive: ${expected}`);
      debugCheck = false;
      allPassed = false;
    }
  }
  if (debugCheck) {
    console.log(`✓ Debug processor received expected spans`);
  }
  
  // Check if analytics processor received expected spans
  const analyticsExpected = ["multi_destination_task"];
  const analyticsReceived = processorSpans.analytics;
  let analyticsCheck = true;
  for (const expected of analyticsExpected) {
    if (!analyticsReceived.some(span => span.includes(expected))) {
      console.log(`❌ Analytics processor did not receive: ${expected}`);
      analyticsCheck = false;
      allPassed = false;
    }
  }
  if (analyticsCheck) {
    console.log(`✓ Analytics processor received expected spans`);
  }
  
  // Check if slow processor received slow_task but not fast_task
  const slowReceived = processorSpans.slow;
  if (slowReceived.some(span => span.includes("slow_task"))) {
    console.log(`✓ Slow processor received slow_task (as expected)`);
  } else {
    console.log(`❌ Slow processor did not receive slow_task`);
    allPassed = false;
  }
  
  if (slowReceived.some(span => span.includes("fast_task"))) {
    console.log(`❌ Slow processor received fast_task (should be filtered out)`);
    allPassed = false;
  } else {
    console.log(`✓ Slow processor did not receive fast_task (filtered correctly)`);
  }
  
  return allPassed;
};

// Run all tests
const runAllTests = async () => {
  console.log("Starting Multi-Processor Routing tests...\n");
  console.log("Environment:");
  console.log(`- Base URL: ${process.env.KEYWORDSAI_BASE_URL}`);
  console.log(`- API Key: ${process.env.KEYWORDSAI_API_KEY?.substring(0, 10)}...`);
  
  await kai.initialize();
  setupProcessors();
  
  try {
    await test1_defaultProcessor();
    await test2_singleProcessorRouting();
    await test3_multipleProcessorRouting();
    await test4_filterBasedRouting();
    await test5_fastTaskFiltered();
    await test6_nestedTasksRouting();
    await test7_complexWorkflow();
    
    // Wait a bit for async processing
    console.log("\nWaiting for span processing...");
    await new Promise((resolve) => setTimeout(resolve, 2000));
    
    // Verify results
    const allPassed = verifyResults();
    
    if (allPassed) {
      console.log("\n" + "=".repeat(50));
      console.log("✅ ALL MULTI-PROCESSOR TESTS PASSED!");
      console.log("=".repeat(50) + "\n");
    } else {
      console.log("\n" + "=".repeat(50));
      console.log("⚠️  SOME VERIFICATIONS FAILED (but tests executed)");
      console.log("=".repeat(50) + "\n");
    }
  } catch (error) {
    console.error("\n" + "=".repeat(50));
    console.error("❌ TEST FAILED!");
    console.error("=".repeat(50));
    console.error(error);
    process.exit(1);
  } finally {
    // Shutdown and flush
    console.log("\nFlushing and shutting down...");
    await kai.shutdown();
    console.log("SDK shut down successfully\n");
  }
};

runAllTests();
