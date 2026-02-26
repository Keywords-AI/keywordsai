/**
 * Example demonstrating manual span buffering
 * 
 * This example shows how to:
 * - Create a span buffer for manual control
 * - Buffer spans without automatic export
 * - Inspect buffered spans before processing
 * - Conditionally process spans based on business logic
 * - Use transportable spans pattern
 */

import { RespanTelemetry, getClient } from "../src/index.js";

// Initialize Respan
const respan = new RespanTelemetry({
  apiKey: process.env.RESPAN_API_KEY,
  baseURL: process.env.RESPAN_BASE_URL,
  appName: "span-buffer-example",
  logLevel: "info",
});

await respan.initialize();

// Example 1: Basic span buffering
console.log("\n=== Example 1: Basic Span Buffering ===\n");

const example1 = async () => {
  const manager = respan.getSpanBufferManager();
  const buffer = manager.createBuffer("trace-example-1");

  // Create multiple spans
  buffer.createSpan("step1", {
    status: "completed",
    duration_ms: 100,
  });

  buffer.createSpan("step2", {
    status: "completed",
    duration_ms: 200,
  });

  buffer.createSpan("step3", {
    status: "completed",
    duration_ms: 150,
  });

  // Inspect buffered spans
  console.log(`Buffered ${buffer.getSpanCount()} spans`);
  const spans = buffer.getAllSpans();
  console.log(
    "Span names:",
    spans.map((s) => s.name)
  );

  // Process spans through the pipeline
  const success = await manager.processSpans(spans);
  console.log(`Processing ${success ? "succeeded" : "failed"}`);
};

await example1();

// Example 2: Conditional processing based on results
console.log("\n=== Example 2: Conditional Processing ===\n");

const example2 = async () => {
  const manager = respan.getSpanBufferManager();

  // Simulate workflow execution
  const workflowResults = [
    { id: 1, status: "success", score: 0.95 },
    { id: 2, status: "success", score: 0.88 },
    { id: 3, status: "success", score: 0.92 },
  ];

  // Create spans for workflow results
  const buffer = manager.createBuffer("trace-example-2");

  for (const result of workflowResults) {
    buffer.createSpan(`workflow_${result.id}`, {
      status: result.status,
      score: result.score,
    });
  }

  // Get buffered spans
  const spans = buffer.getAllSpans();

  // Decide whether to process based on business logic
  const allSuccessful = workflowResults.every((r) => r.status === "success");
  const avgScore =
    workflowResults.reduce((sum, r) => sum + r.score, 0) /
    workflowResults.length;

  console.log(`All workflows successful: ${allSuccessful}`);
  console.log(`Average score: ${avgScore.toFixed(2)}`);

  if (allSuccessful && avgScore > 0.9) {
    console.log("✓ Processing high-quality workflow spans");
    await manager.processSpans(spans);
  } else {
    console.log("✗ Skipping low-quality workflow spans");
    buffer.clearSpans();
  }
};

await example2();

// Example 3: Transportable spans pattern
console.log("\n=== Example 3: Transportable Spans ===\n");

const collectWorkflowSpans = (experimentId: string) => {
  const manager = respan.getSpanBufferManager();
  const buffer = manager.createBuffer(`experiment-${experimentId}`);

  // Simulate multiple workflow runs
  for (let i = 1; i <= 3; i++) {
    buffer.createSpan(`run_${i}`, {
      experiment_id: experimentId,
      input: `test input ${i}`,
      output: `test output ${i}`,
      latency_ms: 100 + i * 50,
    });
  }

  // Return transportable spans
  return buffer.getAllSpans();
};

const processBasedOnExperiment = async (experimentId: string, spans: any[]) => {
  const manager = respan.getSpanBufferManager();

  console.log(`Processing experiment ${experimentId} with ${spans.length} spans`);

  // Business logic to decide processing
  if (experimentId === "exp-123") {
    console.log("✓ Experiment approved - processing spans");
    await manager.processSpans(spans);
  } else {
    console.log("✗ Experiment not approved - discarding spans");
    // Just don't process (spans will be garbage collected)
  }
};

// Collect spans in one place
const exp1Spans = collectWorkflowSpans("exp-123");
const exp2Spans = collectWorkflowSpans("exp-456");

// Process in another place based on business logic
await processBasedOnExperiment("exp-123", exp1Spans); // Will process
await processBasedOnExperiment("exp-456", exp2Spans); // Will discard

// Example 4: Backend workflow ingestion
console.log("\n=== Example 4: Backend Workflow Ingestion ===\n");

const ingestWorkflowOutput = async (
  workflowResult: any,
  traceId: string,
  orgId: string,
  experimentId: string
) => {
  const manager = respan.getSpanBufferManager();
  const buffer = manager.createBuffer(traceId);

  // Create parent span for workflow
  buffer.createSpan("workflow_execution", {
    input: workflowResult.input,
    output: workflowResult.output,
    experiment_id: experimentId,
    organization_id: orgId,
  });

  // Create child spans for each step
  for (const step of workflowResult.steps) {
    buffer.createSpan(`step_${step.name}`, {
      input: step.input,
      output: step.output,
      latency_ms: step.latency,
      cost_usd: step.cost,
    });
  }

  // Get buffered spans
  const spans = buffer.getAllSpans();

  // Decide whether to export based on organization settings
  const shouldExport = orgId === "org-premium"; // Example business logic

  if (shouldExport) {
    console.log(`✓ Exporting workflow for ${orgId} (${spans.length} spans)`);
    const success = await manager.processSpans(spans);
    return success;
  } else {
    console.log(`✗ Not exporting workflow for ${orgId} (not premium)`);
    buffer.clearSpans();
    return false;
  }
};

// Simulate backend ingestion
const workflowResult = {
  input: "process this data",
  output: "processed data",
  steps: [
    { name: "validate", input: "data", output: "valid", latency: 10, cost: 0.001 },
    { name: "transform", input: "valid", output: "transformed", latency: 50, cost: 0.005 },
    { name: "store", input: "transformed", output: "stored", latency: 20, cost: 0.002 },
  ],
};

await ingestWorkflowOutput(
  workflowResult,
  "trace-backend-1",
  "org-premium",
  "exp-789"
);

await ingestWorkflowOutput(
  workflowResult,
  "trace-backend-2",
  "org-free",
  "exp-790"
);

console.log("\n=== All examples completed ===\n");

// Shutdown
await respan.shutdown();
console.log("SDK shut down");


