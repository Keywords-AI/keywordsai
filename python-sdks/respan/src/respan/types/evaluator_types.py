"""
Evaluator Type Definitions for Keywords AI SDK

This module provides comprehensive type definitions for evaluator operations in Keywords AI.
Evaluators are tools that analyze and score AI model outputs based on various criteria
such as accuracy, relevance, toxicity, coherence, and custom metrics.

🏗️ CORE TYPES:

Evaluator: Complete evaluator information and configuration
EvaluatorList: Paginated list of available evaluators
EvalRunRequest: Parameters for running evaluations on datasets
EvalReport: Individual evaluation report with results and metrics
EvalReportList: Paginated list of evaluation reports

🎯 EVALUATOR CATEGORIES:

1. LLM-BASED EVALUATORS:
   Use large language models to assess output quality, relevance, and coherence.
   Examples: GPT-4 based relevance checker, Claude-based coherence evaluator.

2. RULE-BASED EVALUATORS:
   Apply deterministic rules and patterns for specific criteria.
   Examples: Profanity detection, format validation, length constraints.

3. ML MODEL EVALUATORS:
   Use trained machine learning models for specialized evaluation tasks.
   Examples: Sentiment analysis, topic classification, toxicity detection.

💡 USAGE PATTERNS:

1. DISCOVERING EVALUATORS:
   Use EvaluatorAPI.list() to find available evaluators and their capabilities.

2. RUNNING EVALUATIONS:
   Use DatasetAPI.run_dataset_evaluation() with evaluator slugs to analyze datasets.

3. RETRIEVING RESULTS:
   Use DatasetAPI.list_evaluation_reports() to get evaluation outcomes.

📖 EXAMPLES:

Discovering evaluators:
    >>> from respan.evaluators.api import EvaluatorAPI
    >>> 
    >>> client = EvaluatorAPI(api_key="your-key")
    >>> evaluators = await client.list(category="llm")
    >>> 
    >>> for evaluator in evaluators.results:
    ...     print(f"Name: {evaluator.name}")
    ...     print(f"Slug: {evaluator.slug}")  # Use this for evaluations
    ...     print(f"Description: {evaluator.description}")
    ...     print(f"Category: {evaluator.category}")

Running evaluations:
    >>> from respan.datasets.api import DatasetAPI
    >>> 
    >>> dataset_client = DatasetAPI(api_key="your-key")
    >>> 
    >>> # Run multiple evaluators on a dataset
    >>> result = await dataset_client.run_dataset_evaluation(
    ...     dataset_id="dataset-123",
    ...     evaluator_slugs=["accuracy-evaluator", "relevance-evaluator"]
    ... )
    >>> print(f"Evaluation started: {result['evaluation_id']}")

Checking evaluation results:
    >>> # Get evaluation reports for a dataset
    >>> reports = await dataset_client.list_evaluation_reports("dataset-123")
    >>> 
    >>> for report in reports.results:
    ...     print(f"Report ID: {report.id}")
    ...     print(f"Status: {report.status}")
    ...     print(f"Evaluator: {report.evaluator_slug}")
    ...     if report.status == "completed":
    ...         print(f"Score: {report.score}")
    ...         print(f"Results: {report.results}")

🔧 FIELD REFERENCE:

Evaluator Fields:
- id (str): Unique evaluator identifier
- name (str): Human-readable evaluator name
- slug (str): URL-safe identifier for API calls
- description (str): Detailed description of evaluation criteria
- category (str): "llm", "rule_based", or "ml"
- type (str): Specific evaluation type (e.g., "accuracy", "relevance")
- is_active (bool): Whether evaluator is currently available
- configuration (dict): Evaluator-specific settings and parameters
- input_schema (dict): Expected input format for evaluation
- output_schema (dict): Format of evaluation results
"""

# Re-export all evaluator types from respan-sdk
from respan_sdk.respan_types.evaluator_types import (
    Evaluator,
    EvaluatorList,
)

__all__ = [
    "Evaluator",
    "EvaluatorList",
]
