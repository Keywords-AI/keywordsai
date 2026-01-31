/**
 * Evaluator Type Definitions for Keywords AI SDK
 *
 * This module provides comprehensive type definitions for evaluator operations in Keywords AI.
 * Evaluators are tools that analyze and score AI model outputs based on various criteria
 * such as accuracy, relevance, toxicity, coherence, and custom metrics.
 *
 * 🏗️ CORE TYPES:
 *
 * Evaluator: Complete evaluator information and configuration
 * EvaluatorList: Paginated list of available evaluators
 * EvalRunRequest: Parameters for running evaluations on datasets
 * EvalReport: Individual evaluation report with results and metrics
 * EvalReportList: Paginated list of evaluation reports
 *
 * 🎯 EVALUATOR CATEGORIES:
 *
 * 1. LLM-BASED EVALUATORS:
 *    Use large language models to assess output quality, relevance, and coherence.
 *    Examples: GPT-4 based relevance checker, Claude-based coherence evaluator.
 *
 * 2. RULE-BASED EVALUATORS:
 *    Apply deterministic rules and patterns for specific criteria.
 *    Examples: Profanity detection, format validation, length constraints.
 *
 * 3. ML MODEL EVALUATORS:
 *    Use trained machine learning models for specialized evaluation tasks.
 *    Examples: Sentiment analysis, topic classification, toxicity detection.
 *
 * 💡 USAGE PATTERNS:
 *
 * 1. DISCOVERING EVALUATORS:
 *    Use EvaluatorAPI.list() to find available evaluators and their capabilities.
 *
 * 2. RUNNING EVALUATIONS:
 *    Use DatasetAPI.run_dataset_evaluation() with evaluator slugs to analyze datasets.
 *
 * 3. RETRIEVING RESULTS:
 *    Use DatasetAPI.list_evaluation_reports() to get evaluation outcomes.
 *
 * 📖 EXAMPLES:
 *
 * Discovering evaluators:
 *    ```typescript
 *    import { EvaluatorAPI } from '../evaluators/api.js';
 *    
 *    const client = new EvaluatorAPI({ apiKey: "your-key" });
 *    const evaluators = await client.list({ category: "llm" });
 *    
 *    for (const evaluator of evaluators.results) {
 *      console.log(`Name: ${evaluator.name}`);
 *      console.log(`Slug: ${evaluator.slug}`);  // Use this for evaluations
 *      console.log(`Description: ${evaluator.description}`);
 *      console.log(`Category: ${evaluator.category}`);
 *    }
 *    ```
 *
 * Running evaluations:
 *    ```typescript
 *    import { DatasetAPI } from '../datasets/api.js';
 *    
 *    const datasetClient = new DatasetAPI({ apiKey: "your-key" });
 *    
 *    // Run multiple evaluators on a dataset
 *    const result = await datasetClient.runDatasetEvaluation({
 *      datasetId: "dataset-123",
 *      evaluatorSlugs: ["accuracy-evaluator", "relevance-evaluator"]
 *    });
 *    console.log(`Evaluation started: ${result.evaluation_id}`);
 *    ```
 *
 * Checking evaluation results:
 *    ```typescript
 *    // Get evaluation reports for a dataset
 *    const reports = await datasetClient.listEvaluationReports("dataset-123");
 *    
 *    for (const report of reports.results) {
 *      console.log(`Report ID: ${report.id}`);
 *      console.log(`Status: ${report.status}`);
 *      console.log(`Evaluator: ${report.evaluator_slug}`);
 *      if (report.status === "completed") {
 *        console.log(`Score: ${report.score}`);
 *        console.log(`Results: ${JSON.stringify(report.results)}`);
 *      }
 *    }
 *    ```
 *
 * 🔧 FIELD REFERENCE:
 *
 * Evaluator Fields:
 * - id (string): Unique evaluator identifier
 * - name (string): Human-readable evaluator name
 * - slug (string): URL-safe identifier for API calls
 * - description (string): Detailed description of evaluation criteria
 * - category (string): "llm", "rule_based", or "ml"
 * - type (string): Specific evaluation type (e.g., "accuracy", "relevance")
 * - is_active (boolean): Whether evaluator is currently available
 * - configuration (object): Evaluator-specific settings and parameters
 * - input_schema (object): Expected input format for evaluation
 * - output_schema (object): Format of evaluation results
 */

// Re-export all evaluator types from respan-sdk
export type {
  Evaluator,
  EvaluatorList,
} from "@respan/respan-sdk";
