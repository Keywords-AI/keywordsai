/**
 * Dataset Type Definitions for Keywords AI SDK
 *
 * This module provides comprehensive type definitions for dataset operations in Keywords AI.
 * All types provide validation, serialization, and clear structure for API interactions.
 *
 * 🏗️ CORE TYPES:
 *
 * Dataset: Complete dataset information returned by the API
 * DatasetCreate: Parameters for creating new datasets
 * DatasetUpdate: Parameters for updating existing datasets
 * DatasetList: Paginated list of datasets with metadata
 * LogManagementRequest: Parameters for adding/removing logs from datasets
 *
 * 💡 USAGE PATTERNS:
 *
 * 1. CREATING DATASETS:
 *    Use DatasetCreate to specify dataset configuration, including time ranges,
 *    filtering criteria, and sampling parameters.
 *
 * 2. UPDATING DATASETS:
 *    Use DatasetUpdate to modify dataset metadata like name and description.
 *    Core properties like type and filters cannot be changed after creation.
 *
 * 3. LOG MANAGEMENT:
 *    Use LogManagementRequest to add or remove logs based on time ranges and filters.
 *    Supports complex filtering with various operators.
 *
 * 4. LISTING DATASETS:
 *    DatasetList provides paginated results with navigation metadata.
 *
 * 📖 EXAMPLES:
 *
 * Basic dataset creation:
 *    ```typescript
 *    import { DatasetCreate } from './datasetTypes.js';
 *    
 *    // Create a sampling dataset for recent logs
 *    const endTime = new Date();
 *    const startTime = new Date(endTime.getTime() - 24 * 60 * 60 * 1000); // 24 hours ago
 *    
 *    const datasetConfig: DatasetCreate = {
 *      name: "Daily Analysis Dataset",
 *      description: "Analysis of API calls from the last 24 hours",
 *      type: "sampling",
 *      sampling: 1000,
 *      start_time: startTime.toISOString(),
 *      end_time: endTime.toISOString(),
 *      initial_log_filters: {
 *        status: { value: "success", operator: "equals" }
 *      }
 *    };
 *    ```
 *
 * Advanced filtering example:
 *    ```typescript
 *    // Complex filtering with multiple criteria
 *    const datasetConfig: DatasetCreate = {
 *      name: "Error Analysis Dataset",
 *      description: "Failed API calls for debugging",
 *      type: "sampling",
 *      sampling: 500,
 *      start_time: "2024-01-01T00:00:00Z",
 *      end_time: "2024-01-02T00:00:00Z",
 *      initial_log_filters: {
 *        status: { value: "error", operator: "equals" },
 *        model: { value: "gpt-4", operator: "equals" },
 *        response_time: { value: 5000, operator: "greater_than" }
 *      }
 *    };
 *    ```
 *
 * Log management example:
 *    ```typescript
 *    import { LogManagementRequest } from './datasetTypes.js';
 *    
 *    // Add logs with specific criteria
 *    const logRequest: LogManagementRequest = {
 *      start_time: "2024-01-01 00:00:00",
 *      end_time: "2024-01-01 23:59:59",
 *      filters: {
 *        user_id: { value: "user123", operator: "equals" },
 *        tokens: { value: 1000, operator: "less_than" }
 *      }
 *    };
 *    ```
 *
 * 🔧 FIELD REFERENCE:
 *
 * DatasetCreate Fields:
 * - name (string): Human-readable dataset name
 * - description (string): Detailed description of dataset purpose
 * - type (string): "sampling" or "llm" - determines collection strategy
 * - sampling (number, optional): Max number of logs for sampling type
 * - start_time (string, optional): ISO format timestamp for log collection start
 * - end_time (string, optional): ISO format timestamp for log collection end
 * - initial_log_filters (object, optional): Filters to apply during collection
 *
 * DatasetUpdate Fields:
 * - name (string, optional): New dataset name
 * - description (string, optional): New dataset description
 *
 * LogManagementRequest Fields:
 * - start_time (string): Start time in "YYYY-MM-DD HH:MM:SS" format
 * - end_time (string): End time in "YYYY-MM-DD HH:MM:SS" format
 * - filters (object): Filter criteria with operator-based matching
 *
 * Filter Operators:
 * - "equals": Exact match
 * - "not_equals": Exclude exact matches
 * - "contains": Substring match (for text fields)
 * - "greater_than": Numeric comparison >
 * - "less_than": Numeric comparison <
 * - "greater_than_or_equal": Numeric comparison >=
 * - "less_than_or_equal": Numeric comparison <=
 * - "in": Match any value in provided list
 * - "not_in": Exclude values in provided list
 *
 * ⚠️ IMPORTANT NOTES:
 * - All datetime strings should be in UTC timezone
 * - Sampling limits depend on your plan and available logs
 * - Complex filters may impact dataset creation performance
 * - Some fields are immutable after dataset creation
 */

// Re-export all dataset types from respan-sdk
export type {
  Dataset,
  DatasetCreate,
  DatasetUpdate,
  LogManagementRequest,
  EvalReport,
  EvalRunRequest,
} from "@respan/respan-sdk";

// Import generic types
import type { PaginatedResponseType, Dataset, EvalReport } from "@respan/respan-sdk";

// Type aliases for list responses using the generic paginated type
export type DatasetList = PaginatedResponseType<Dataset>;
export type EvalReportList = PaginatedResponseType<EvalReport>;
