/**
 * Test suite for Client API (getClient())
 * 
 * Tests:
 * - Get current trace and span IDs
 * - Update span with KeywordsAI parameters
 * - Add events
 * - Record exceptions
 * - Check recording status
 */

import { KeywordsAITelemetry, getClient } from "../src/index.js";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

// Initialize with debug logging
const kai = new KeywordsAITelemetry({
  apiKey: process.env.KEYWORDSAI_API_KEY,
  baseURL: process.env.KEYWORDSAI_BASE_URL,
  appName: "test-client-api",
  logLevel: "debug",
  traceContent: true,
  resourceAttributes: {
    test_suite: "client_api",
    environment: "test",
  },
});

console.log("\n=== Client API Test Suite ===\n");

// Test 1: Get trace and span IDs
const test1_getTraceAndSpanIds = async () => {
  console.log("\n[Test 1] Get Trace and Span IDs");
  
  await kai.withWorkflow({ name: "test_get_ids" }, async () => {
    const client = getClient();
    
    const traceId = client.getCurrentTraceId();
    const spanId = client.getCurrentSpanId();
    
    console.log(`✓ Trace ID: ${traceId}`);
    console.log(`✓ Span ID: ${spanId}`);
    
    if (!traceId || !spanId) {
      throw new Error("❌ Failed to get trace/span IDs");
    }
    
    console.log("✅ Test 1 Passed: Got trace and span IDs");
  });
};

// Test 2: Update span with KeywordsAI parameters
const test2_updateSpanWithKeywordsAIParams = async () => {
  console.log("\n[Test 2] Update Span with KeywordsAI Parameters");
  
  await kai.withTask({ name: "test_keywordsai_params" }, async () => {
    const client = getClient();
    
    // Update with all KeywordsAI parameters
    client.updateCurrentSpan({
      keywordsaiParams: {
        customerIdentifier: "test-user-123",
        traceGroupIdentifier: "test-experiment-456",
        metadata: {
          test_name: "client_api_test",
          version: "1.0.0",
          environment: "test",
        },
      },
    });
    
    console.log("✓ Updated span with customer_identifier: test-user-123");
    console.log("✓ Updated span with trace_group_identifier: test-experiment-456");
    console.log("✓ Updated span with metadata");
    
    console.log("✅ Test 2 Passed: Updated span with KeywordsAI params");
  });
};

// Test 3: Add events to span
const test3_addEvents = async () => {
  console.log("\n[Test 3] Add Events to Span");
  
  await kai.withTask({ name: "test_add_events" }, async () => {
    const client = getClient();
    
    // Add multiple events
    client.addEvent("validation_started", { records: 100 });
    console.log("✓ Added event: validation_started");
    
    await new Promise((resolve) => setTimeout(resolve, 50));
    
    client.addEvent("validation_completed", { 
      status: "success",
      duration_ms: 50,
    });
    console.log("✓ Added event: validation_completed");
    
    client.addEvent("processing_started");
    console.log("✓ Added event: processing_started (no attributes)");
    
    console.log("✅ Test 3 Passed: Added events to span");
  });
};

// Test 4: Record exceptions
const test4_recordExceptions = async () => {
  console.log("\n[Test 4] Record Exceptions");
  
  await kai.withTask({ name: "test_record_exception" }, async () => {
    const client = getClient();
    
    try {
      // Simulate an error
      throw new Error("Simulated test error");
    } catch (error) {
      client.recordException(error as Error);
      console.log("✓ Recorded exception: Simulated test error");
    }
    
    console.log("✅ Test 4 Passed: Recorded exception");
  });
};

// Test 5: Check recording status
const test5_isRecording = async () => {
  console.log("\n[Test 5] Check Recording Status");
  
  await kai.withWorkflow({ name: "test_is_recording" }, async () => {
    const client = getClient();
    
    const isRecording = client.isRecording();
    console.log(`✓ Is recording: ${isRecording}`);
    
    if (!isRecording) {
      throw new Error("❌ Expected span to be recording");
    }
    
    console.log("✅ Test 5 Passed: Span is recording");
  });
};

// Test 6: Update span name and attributes
const test6_updateSpanNameAndAttributes = async () => {
  console.log("\n[Test 6] Update Span Name and Attributes");
  
  await kai.withTask({ name: "test_update_attributes" }, async () => {
    const client = getClient();
    
    // Update span name
    client.updateCurrentSpan({
      name: "updated_task_name",
    });
    console.log("✓ Updated span name to: updated_task_name");
    
    // Add custom attributes
    client.updateCurrentSpan({
      attributes: {
        "custom.field1": "value1",
        "custom.field2": 42,
        "custom.field3": true,
      },
    });
    console.log("✓ Added custom attributes");
    
    console.log("✅ Test 6 Passed: Updated span name and attributes");
  });
};

// Test 7: Get tracer for manual spans
const test7_getTracer = async () => {
  console.log("\n[Test 7] Get Tracer for Manual Spans");
  
  await kai.withWorkflow({ name: "test_manual_spans" }, async () => {
    const client = getClient();
    const tracer = client.getTracer();
    
    console.log("✓ Got tracer instance");
    
    // Create a manual span
    tracer.startActiveSpan("manual_child_span", (span) => {
      span.setAttribute("manual.test", true);
      console.log("✓ Created manual child span");
      span.end();
    });
    
    console.log("✅ Test 7 Passed: Got tracer and created manual span");
  });
};

// Test 8: Combined workflow with all features
const test8_combinedWorkflow = async () => {
  console.log("\n[Test 8] Combined Workflow with All Features");
  
  await kai.withWorkflow(
    { 
      name: "test_combined_workflow",
      version: 1,
    },
    async () => {
      const client = getClient();
      
      // Get IDs
      const traceId = client.getCurrentTraceId();
      console.log(`✓ Trace ID: ${traceId}`);
      
      // Update with KeywordsAI params
      client.updateCurrentSpan({
        keywordsaiParams: {
          customerIdentifier: "combined-user",
          traceGroupIdentifier: "combined-test",
        },
      });
      console.log("✓ Set KeywordsAI params");
      
      // Add event
      client.addEvent("workflow_started");
      console.log("✓ Added start event");
      
      // Run a nested task
      await kai.withTask({ name: "nested_task" }, async () => {
        const nestedClient = getClient();
        nestedClient.addEvent("nested_task_executing");
        console.log("✓ Nested task executed");
        
        // Simulate some work
        await new Promise((resolve) => setTimeout(resolve, 100));
      });
      
      // Add completion event
      client.addEvent("workflow_completed", {
        duration_ms: 100,
        status: "success",
      });
      console.log("✓ Added completion event");
      
      console.log("✅ Test 8 Passed: Combined workflow with all features");
    }
  );
};

// Run all tests
const runAllTests = async () => {
  console.log("Starting Client API tests...\n");
  console.log("Environment:");
  console.log(`- Base URL: ${process.env.KEYWORDSAI_BASE_URL}`);
  console.log(`- API Key: ${process.env.KEYWORDSAI_API_KEY?.substring(0, 10)}...`);
  
  await kai.initialize();
  
  try {
    await test1_getTraceAndSpanIds();
    await test2_updateSpanWithKeywordsAIParams();
    await test3_addEvents();
    await test4_recordExceptions();
    await test5_isRecording();
    await test6_updateSpanNameAndAttributes();
    await test7_getTracer();
    await test8_combinedWorkflow();
    
    console.log("\n" + "=".repeat(50));
    console.log("✅ ALL CLIENT API TESTS PASSED!");
    console.log("=".repeat(50) + "\n");
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
