/**
 * Test suite for Span Buffering
 * 
 * Tests:
 * - Create span buffer
 * - Buffer spans without auto-export
 * - Get buffered spans (transportable)
 * - Process spans conditionally
 * - Clear spans
 */

import { KeywordsAITelemetry } from "../src/index.js";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

// Initialize KeywordsAI with debug logging
const kai = new KeywordsAITelemetry({
  apiKey: process.env.KEYWORDSAI_API_KEY,
  baseURL: process.env.KEYWORDSAI_BASE_URL,
  appName: "test-span-buffer",
  logLevel: "debug",
  traceContent: true,
});

console.log("\n=== Span Buffer Test Suite ===\n");

// Test 1: Create buffer and add spans
const test1_createBufferAndAddSpans = async () => {
  console.log("\n[Test 1] Create Buffer and Add Spans");
  
  const manager = kai.getSpanBufferManager();
  const buffer = manager.createBuffer("test-trace-1");
  
  console.log("✓ Created span buffer");
  
  // Add multiple spans
  buffer.createSpan("step1", {
    status: "completed",
    duration_ms: 100,
  });
  console.log("✓ Created span: step1");
  
  buffer.createSpan("step2", {
    status: "completed",
    duration_ms: 200,
  });
  console.log("✓ Created span: step2");
  
  buffer.createSpan("step3", {
    status: "completed",
    duration_ms: 150,
  });
  console.log("✓ Created span: step3");
  
  // Check count
  const count = buffer.getSpanCount();
  console.log(`✓ Buffer contains ${count} spans`);
  
  if (count !== 3) {
    throw new Error(`❌ Expected 3 spans, got ${count}`);
  }
  
  console.log("✅ Test 1 Passed: Created buffer and added 3 spans");
};

// Test 2: Get buffered spans (transportable)
const test2_getBufferedSpans = async () => {
  console.log("\n[Test 2] Get Buffered Spans (Transportable)");
  
  const manager = kai.getSpanBufferManager();
  const buffer = manager.createBuffer("test-trace-2");
  
  // Add spans
  buffer.createSpan("task1", { result: "success" });
  buffer.createSpan("task2", { result: "success" });
  
  // Get spans (transportable)
  const spans = buffer.getAllSpans();
  console.log(`✓ Retrieved ${spans.length} spans from buffer`);
  
  if (spans.length !== 2) {
    throw new Error(`❌ Expected 2 spans, got ${spans.length}`);
  }
  
  // Verify spans are transportable (can be stored and used later)
  console.log("✓ Spans are transportable:");
  spans.forEach((span, i) => {
    console.log(`  Span ${i + 1}: ${span.name}`);
  });
  
  console.log("✅ Test 2 Passed: Got transportable spans");
};

// Test 3: Process spans through pipeline
const test3_processSpans = async () => {
  console.log("\n[Test 3] Process Spans Through Pipeline");
  
  const manager = kai.getSpanBufferManager();
  const buffer = manager.createBuffer("test-trace-3");
  
  // Add spans
  buffer.createSpan("processing_step1", {
    status: "completed",
    data_processed: 1000,
  });
  
  buffer.createSpan("processing_step2", {
    status: "completed",
    data_processed: 2000,
  });
  
  // Get spans
  const spans = buffer.getAllSpans();
  console.log(`✓ Created ${spans.length} spans`);
  
  // Process spans
  const success = await manager.processSpans(spans);
  
  if (success) {
    console.log("✓ Successfully processed spans through pipeline");
  } else {
    throw new Error("❌ Failed to process spans");
  }
  
  console.log("✅ Test 3 Passed: Processed spans successfully");
};

// Test 4: Conditional processing
const test4_conditionalProcessing = async () => {
  console.log("\n[Test 4] Conditional Processing");
  
  const manager = kai.getSpanBufferManager();
  
  // Scenario 1: Success - should process
  console.log("\n  Scenario 1: Successful workflow (should process)");
  const buffer1 = manager.createBuffer("test-trace-4a");
  buffer1.createSpan("workflow1_step1", { status: "success", score: 0.95 });
  buffer1.createSpan("workflow1_step2", { status: "success", score: 0.92 });
  
  const spans1 = buffer1.getAllSpans();
  const allSuccessful = true; // Simulate success check
  const avgScore = 0.935;
  
  if (allSuccessful && avgScore > 0.9) {
    console.log("  ✓ Conditions met - processing spans");
    await manager.processSpans(spans1);
  } else {
    console.log("  ✗ Conditions not met - skipping");
  }
  
  // Scenario 2: Failure - should skip
  console.log("\n  Scenario 2: Failed workflow (should skip)");
  const buffer2 = manager.createBuffer("test-trace-4b");
  buffer2.createSpan("workflow2_step1", { status: "failed", score: 0.45 });
  
  const spans2 = buffer2.getAllSpans();
  const hasFailed = true; // Simulate failure check
  
  if (!hasFailed) {
    console.log("  ✓ Processing spans");
    await manager.processSpans(spans2);
  } else {
    console.log("  ✓ Skipping failed workflow (not processing)");
    buffer2.clearSpans();
    console.log("  ✓ Cleared buffer");
  }
  
  console.log("\n✅ Test 4 Passed: Conditional processing works");
};

// Test 5: Clear spans
const test5_clearSpans = async () => {
  console.log("\n[Test 5] Clear Spans");
  
  const manager = kai.getSpanBufferManager();
  const buffer = manager.createBuffer("test-trace-5");
  
  // Add spans
  buffer.createSpan("temp1", {});
  buffer.createSpan("temp2", {});
  buffer.createSpan("temp3", {});
  
  let count = buffer.getSpanCount();
  console.log(`✓ Buffer contains ${count} spans`);
  
  if (count !== 3) {
    throw new Error(`❌ Expected 3 spans, got ${count}`);
  }
  
  // Clear buffer
  buffer.clearSpans();
  console.log("✓ Cleared buffer");
  
  count = buffer.getSpanCount();
  console.log(`✓ Buffer now contains ${count} spans`);
  
  if (count !== 0) {
    throw new Error(`❌ Expected 0 spans after clear, got ${count}`);
  }
  
  console.log("✅ Test 5 Passed: Cleared spans successfully");
};

// Test 6: Transportable spans pattern (collect in one place, process in another)
const test6_transportableSpansPattern = async () => {
  console.log("\n[Test 6] Transportable Spans Pattern");
  
  const manager = kai.getSpanBufferManager();
  
  // Phase 1: Collect spans (simulate workflow execution)
  console.log("\n  Phase 1: Collecting spans...");
  const collectWorkflowSpans = (workflowId: string) => {
    const buffer = manager.createBuffer(`workflow-${workflowId}`);
    
    buffer.createSpan(`${workflowId}_step1`, { result: "data1" });
    buffer.createSpan(`${workflowId}_step2`, { result: "data2" });
    buffer.createSpan(`${workflowId}_step3`, { result: "data3" });
    
    return buffer.getAllSpans();
  };
  
  const workflow1Spans = collectWorkflowSpans("wf1");
  const workflow2Spans = collectWorkflowSpans("wf2");
  
  console.log(`  ✓ Collected ${workflow1Spans.length} spans from workflow 1`);
  console.log(`  ✓ Collected ${workflow2Spans.length} spans from workflow 2`);
  
  // Phase 2: Process based on business logic (in a different context)
  console.log("\n  Phase 2: Processing based on business logic...");
  
  const processWorkflow = async (workflowId: string, spans: any[]) => {
    // Simulate business logic decision
    const shouldProcess = workflowId === "wf1";
    
    if (shouldProcess) {
      console.log(`  ✓ Processing ${workflowId} (${spans.length} spans)`);
      await manager.processSpans(spans);
    } else {
      console.log(`  ✗ Skipping ${workflowId} (${spans.length} spans)`);
    }
  };
  
  await processWorkflow("wf1", workflow1Spans);
  await processWorkflow("wf2", workflow2Spans);
  
  console.log("\n✅ Test 6 Passed: Transportable spans pattern works");
};

// Test 7: Backend workflow ingestion pattern
const test7_backendIngestionPattern = async () => {
  console.log("\n[Test 7] Backend Workflow Ingestion Pattern");
  
  const manager = kai.getSpanBufferManager();
  
  // Simulate backend receiving workflow results
  const ingestWorkflowResults = async (
    workflowData: any,
    traceId: string,
    orgId: string
  ) => {
    const buffer = manager.createBuffer(traceId);
    
    // Create parent span
    buffer.createSpan("workflow_execution", {
      organization_id: orgId,
      input: workflowData.input,
      output: workflowData.output,
    });
    
    // Create child spans for steps
    for (const step of workflowData.steps) {
      buffer.createSpan(`step_${step.name}`, {
        input: step.input,
        output: step.output,
        duration_ms: step.duration,
      });
    }
    
    const spans = buffer.getAllSpans();
    
    // Business logic: only process for premium orgs
    const isPremium = orgId.includes("premium");
    
    if (isPremium) {
      console.log(`  ✓ Processing workflow for ${orgId} (premium)`);
      await manager.processSpans(spans);
      return true;
    } else {
      console.log(`  ✗ Not processing workflow for ${orgId} (not premium)`);
      buffer.clearSpans();
      return false;
    }
  };
  
  const workflowData = {
    input: "test data",
    output: "processed data",
    steps: [
      { name: "validate", input: "raw", output: "valid", duration: 10 },
      { name: "transform", input: "valid", output: "transformed", duration: 50 },
      { name: "store", input: "transformed", output: "stored", duration: 20 },
    ],
  };
  
  console.log("\n  Testing premium organization:");
  await ingestWorkflowResults(workflowData, "trace-premium-1", "org-premium-123");
  
  console.log("\n  Testing free organization:");
  await ingestWorkflowResults(workflowData, "trace-free-1", "org-free-456");
  
  console.log("\n✅ Test 7 Passed: Backend ingestion pattern works");
};

// Test 8: Multiple buffers simultaneously
const test8_multipleBuffers = async () => {
  console.log("\n[Test 8] Multiple Buffers Simultaneously");
  
  const manager = kai.getSpanBufferManager();
  
  // Create multiple buffers
  const buffer1 = manager.createBuffer("trace-multi-1");
  const buffer2 = manager.createBuffer("trace-multi-2");
  const buffer3 = manager.createBuffer("trace-multi-3");
  
  console.log("✓ Created 3 separate buffers");
  
  // Add spans to each
  buffer1.createSpan("buffer1_span1", {});
  buffer1.createSpan("buffer1_span2", {});
  
  buffer2.createSpan("buffer2_span1", {});
  buffer2.createSpan("buffer2_span2", {});
  buffer2.createSpan("buffer2_span3", {});
  
  buffer3.createSpan("buffer3_span1", {});
  
  console.log(`✓ Buffer 1: ${buffer1.getSpanCount()} spans`);
  console.log(`✓ Buffer 2: ${buffer2.getSpanCount()} spans`);
  console.log(`✓ Buffer 3: ${buffer3.getSpanCount()} spans`);
  
  // Verify isolation
  if (buffer1.getSpanCount() !== 2 || buffer2.getSpanCount() !== 3 || buffer3.getSpanCount() !== 1) {
    throw new Error("❌ Buffers are not properly isolated");
  }
  
  console.log("✓ Buffers are properly isolated");
  
  // Process selectively
  await manager.processSpans(buffer1.getAllSpans());
  console.log("✓ Processed buffer 1");
  
  await manager.processSpans(buffer3.getAllSpans());
  console.log("✓ Processed buffer 3");
  
  buffer2.clearSpans();
  console.log("✓ Cleared buffer 2 (not processed)");
  
  console.log("✅ Test 8 Passed: Multiple buffers work independently");
};

// Run all tests
const runAllTests = async () => {
  console.log("Starting Span Buffer tests...\n");
  console.log("Environment:");
  console.log(`- Base URL: ${process.env.KEYWORDSAI_BASE_URL}`);
  console.log(`- API Key: ${process.env.KEYWORDSAI_API_KEY?.substring(0, 10)}...`);
  
  await kai.initialize();
  
  try {
    await test1_createBufferAndAddSpans();
    await test2_getBufferedSpans();
    await test3_processSpans();
    await test4_conditionalProcessing();
    await test5_clearSpans();
    await test6_transportableSpansPattern();
    await test7_backendIngestionPattern();
    await test8_multipleBuffers();
    
    console.log("\n" + "=".repeat(50));
    console.log("✅ ALL SPAN BUFFER TESTS PASSED!");
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
