/**
 * Respan Dataset APIs
 *
 * This module provides functionality for managing datasets, including:
 * - Creating and managing datasets
 * - Adding/removing logs from datasets
 * - Running evaluations on datasets
 * - Listing and retrieving dataset information
 */

import { BaseAPI } from "../utils/base.js";
import type {
  Dataset,
  DatasetCreate,
  DatasetUpdate,
  DatasetList,
  LogManagementRequest,
  EvalReport,
  EvalReportList,
} from "../types/datasetTypes.js";
import {
  DATASET_BASE_PATH,
  DATASET_CREATION_PATH,
  DATASET_LIST_PATH,
  DATASET_GET_PATH,
  DATASET_UPDATE_PATH,
} from "../constants/datasetConstants.js";

/**
 * Unified Dataset API client for Respan with async methods.
 *
 * This class provides comprehensive functionality for managing datasets in Respan,
 * including creating datasets, managing logs within datasets, running evaluations,
 * and retrieving results.
 *
 * Features:
 *     - Create and manage datasets with various filtering options
 *     - Add/remove logs from datasets based on time ranges and filters
 *     - Run evaluations on datasets using available evaluators
 *     - Retrieve evaluation reports and results
 *     - Full CRUD operations for dataset management
 *
 * Args:
 *     apiKey (string): Your Respan API key. Required for authentication.
 *     baseUrl (string, optional): Base URL for the Respan API.
 *         Defaults to the standard Respan API endpoint.
 *
 * Example:
 *     ```typescript
 *     import { DatasetAPI } from './datasets/api.js';
 *     import type { DatasetCreate } from './types/datasetTypes.js';
 *     
 *     // Initialize the client
 *     const client = new DatasetAPI({ apiKey: "your-api-key" });
 *     
 *     // Create a new dataset
 *     const datasetData: DatasetCreate = {
 *       name: "My Test Dataset",
 *       description: "Dataset for testing purposes",
 *       type: "sampling",
 *       sampling: 100
 *     };
 *     const dataset = await client.create(datasetData);
 *     console.log(`Created dataset: ${dataset.name}`);
 *     ```
 */
export class DatasetAPI extends BaseAPI<Dataset, DatasetList, DatasetCreate, DatasetUpdate> {
  /**
   * Initialize the Dataset API client.
   *
   * @param options - Configuration options
   * @param options.apiKey - Your Respan API key for authentication
   * @param options.baseUrl - Custom base URL for the API. If not provided,
   *     uses the default Respan API endpoint.
   */
  constructor(options: { apiKey: string; baseUrl?: string }) {
    super(options);
  }

  /**
   * Create a new dataset with specified parameters.
   *
   * This method creates a new dataset in Respan with the provided configuration.
   * The dataset can be configured for different types of log collection and filtering.
   *
   * @param createData - Dataset creation parameters including:
   *     - name (string): Name of the dataset
   *     - description (string): Description of the dataset's purpose
   *     - type (string): Dataset type ("sampling" or "llm")
   *     - sampling (number, optional): Number of logs to sample (for sampling type)
   *     - start_time (string, optional): Start time for log collection (ISO format)
   *     - end_time (string, optional): End time for log collection (ISO format)
   *     - initial_log_filters (object, optional): Filters to apply when collecting logs
   *
   * @returns The created dataset object containing:
   *     - id (string): Unique identifier for the dataset
   *     - name (string): Dataset name
   *     - description (string): Dataset description
   *     - type (string): Dataset type
   *     - status (string): Current status of the dataset
   *     - created_at (string): Creation timestamp
   *
   * @throws Error if the dataset creation fails due to invalid parameters or API errors
   *
   * @example
   *     ```typescript
   *     const endTime = new Date();
   *     const startTime = new Date(endTime.getTime() - 24 * 60 * 60 * 1000);
   *     
   *     const datasetData: DatasetCreate = {
   *       name: "Success Logs Analysis",
   *       description: "Dataset containing successful API calls from last 24h",
   *       type: "sampling",
   *       sampling: 500,
   *       start_time: startTime.toISOString(),
   *       end_time: endTime.toISOString(),
   *       initial_log_filters: {
   *         status: { value: "success", operator: "equals" }
   *       }
   *     };
   *     const dataset = await client.create(datasetData);
   *     ```
   */
  async create(createData: DatasetCreate): Promise<Dataset> {
    const validatedData = this.validateInput(createData);
    const response = await this.client.post(
      DATASET_CREATION_PATH,
      this.prepareJsonData(validatedData)
    );
    return response as Dataset;
  }

  /**
   * List datasets with optional filtering and pagination.
   *
   * Retrieve a paginated list of datasets, optionally filtered by various criteria.
   * This method supports filtering by dataset properties and provides pagination
   * for handling large numbers of datasets.
   *
   * @param options - List options including:
   *     - page (number, optional): Page number for pagination (1-based)
   *     - pageSize (number, optional): Number of datasets per page
   *     - Additional filter parameters such as:
   *       - name (string): Filter by dataset name (partial match)
   *       - type (string): Filter by dataset type ("sampling", "llm")
   *       - status (string): Filter by dataset status
   *       - created_after (string): Filter datasets created after this date
   *       - created_before (string): Filter datasets created before this date
   *
   * @returns A paginated list containing:
   *     - results (Array): List of dataset objects
   *     - count (number): Total number of datasets matching filters
   *     - next (string, optional): URL for next page if available
   *     - previous (string, optional): URL for previous page if available
   *
   * @example
   *     ```typescript
   *     // List all datasets
   *     const datasets = await client.list();
   *     console.log(`Found ${datasets.count} datasets`);
   *     
   *     // List with pagination
   *     const page1 = await client.list({ page: 1, pageSize: 10 });
   *     
   *     // List with filters
   *     const samplingDatasets = await client.list({ type: "sampling" });
   *     const recentDatasets = await client.list({
   *       created_after: "2024-01-01T00:00:00Z"
   *     });
   *     ```
   */
  async list(options: {
    page?: number;
    pageSize?: number;
    [key: string]: any;
  } = {}): Promise<DatasetList> {
    const { page, pageSize, ...filters } = options;
    const params: Record<string, any> = {};
    
    if (page !== undefined) params.page = page;
    if (pageSize !== undefined) params.page_size = pageSize;
    Object.assign(params, filters);

    const response = await this.client.get(DATASET_LIST_PATH, { params });
    return response as DatasetList;
  }

  /**
   * Retrieve a specific dataset by its unique identifier.
   *
   * Fetch detailed information about a dataset including its current status,
   * configuration, and metadata. This is useful for checking dataset readiness
   * before performing operations like adding logs or running evaluations.
   *
   * @param resourceId - The unique identifier of the dataset to retrieve.
   *     This is typically returned when creating a dataset or listing datasets.
   *
   * @returns Complete dataset information including:
   *     - id (string): Unique dataset identifier
   *     - name (string): Dataset name
   *     - description (string): Dataset description
   *     - type (string): Dataset type ("sampling" or "llm")
   *     - status (string): Current status ("initializing", "ready", "running", etc.)
   *     - created_at (string): Creation timestamp
   *     - updated_at (string): Last update timestamp
   *     - log_count (number, optional): Number of logs in the dataset
   *
   * @throws Error if the dataset is not found or access is denied
   *
   * @example
   *     ```typescript
   *     // Get dataset details
   *     const dataset = await client.get("dataset-123");
   *     console.log(`Dataset '${dataset.name}' status: ${dataset.status}`);
   *     
   *     // Check if dataset is ready for operations
   *     if (dataset.status === "ready") {
   *       console.log("Dataset is ready for log management and evaluations");
   *     } else {
   *       console.log(`Dataset is still ${dataset.status}, please wait...`);
   *     }
   *     ```
   */
  async get(resourceId: string): Promise<Dataset> {
    const response = await this.client.get(`${DATASET_GET_PATH}/${resourceId}`);
    return response as Dataset;
  }

  /**
   * Update an existing dataset's properties.
   *
   * Modify dataset metadata such as name and description. Note that core
   * dataset properties like type and initial filters cannot be changed
   * after creation.
   *
   * @param resourceId - The unique identifier of the dataset to update
   * @param updateData - Update parameters containing:
   *     - name (string, optional): New name for the dataset
   *     - description (string, optional): New description for the dataset
   *
   * @returns The updated dataset object with new properties applied
   *
   * @throws Error if the dataset is not found, update fails, or
   *     invalid parameters are provided
   *
   * @example
   *     ```typescript
   *     // Update dataset name and description
   *     const updateData: DatasetUpdate = {
   *       name: "Updated Dataset Name",
   *       description: "Updated description with more details"
   *     };
   *     const updatedDataset = await client.update("dataset-123", updateData);
   *     console.log(`Updated dataset: ${updatedDataset.name}`);
   *     ```
   */
  async update(resourceId: string, updateData: DatasetUpdate): Promise<Dataset> {
    const validatedData = this.validateInput(updateData);
    const response = await this.client.patch(
      `${DATASET_UPDATE_PATH}/${resourceId}`,
      this.prepareJsonData(validatedData)
    );
    return response as Dataset;
  }

  /**
   * Delete a dataset permanently.
   *
   * WARNING: This operation is irreversible. The dataset and all its associated
   * logs and evaluation reports will be permanently deleted.
   *
   * @param resourceId - The unique identifier of the dataset to delete
   *
   * @returns API response confirming deletion, typically containing:
   *     - success (boolean): Whether deletion was successful
   *     - message (string): Confirmation message
   *
   * @throws Error if the dataset is not found or deletion fails
   *
   * @example
   *     ```typescript
   *     // Delete a dataset (be careful!)
   *     const response = await client.delete("dataset-123");
   *     console.log(response.message); // "Dataset deleted successfully"
   *     ```
   *
   * @note Consider exporting important data before deletion as this operation cannot be undone.
   */
  async delete(resourceId: string): Promise<{ success: boolean; message?: string }> {
    const response = await this.client.delete(`${DATASET_BASE_PATH}/${resourceId}`);
    return response as { success: boolean; message?: string };
  }

  // Dataset-specific methods

  /**
   * Add logs to an existing dataset based on filters and time range.
   *
   * This method allows you to expand a dataset by adding more logs that match
   * specific criteria. This is useful for creating comprehensive datasets that
   * include different types of logs or extending the time range of analysis.
   *
   * @param datasetId - The unique identifier of the target dataset
   * @param logRequest - Log selection criteria containing:
   *     - start_time (string): Start time for log collection (format: "YYYY-MM-DD HH:MM:SS")
   *     - end_time (string): End time for log collection (format: "YYYY-MM-DD HH:MM:SS")
   *     - filters (object): Log filters such as:
   *       - status: { value: "success|error|pending", operator: "equals" }
   *       - model: { value: "model-name", operator: "equals" }
   *       - user_id: { value: "user-123", operator: "equals" }
   *       - Custom filters based on your log structure
   *
   * @returns Response containing:
   *     - message (string): Success message
   *     - count (number): Number of logs added
   *     - dataset_id (string): ID of the updated dataset
   *
   * @throws Error if the dataset is not found, request is invalid,
   *     or no logs match the criteria
   *
   * @example
   *     ```typescript
   *     const endTime = new Date();
   *     const startTime = new Date(endTime.getTime() - 7 * 24 * 60 * 60 * 1000);
   *     
   *     const logRequest: LogManagementRequest = {
   *       start_time: startTime.toISOString().replace('T', ' ').slice(0, -5),
   *       end_time: endTime.toISOString().replace('T', ' ').slice(0, -5),
   *       filters: {
   *         status: { value: "error", operator: "equals" }
   *       }
   *     };
   *     const result = await client.addLogsToDataset("dataset-123", logRequest);
   *     console.log(`Added ${result.count} error logs to dataset`);
   *     ```
   */
  async addLogsToDataset(
    datasetId: string,
    logRequest: LogManagementRequest
  ): Promise<{ message: string; count: number; dataset_id: string }> {
    const validatedData = this.validateInput(logRequest);
    const response = await this.client.post(
      `${DATASET_BASE_PATH}/${datasetId}/logs/create`,
      this.prepareJsonData(validatedData)
    );
    return response as { message: string; count: number; dataset_id: string };
  }

  /**
   * Remove logs from a dataset based on filters and time range.
   *
   * @param datasetId - The unique identifier of the target dataset
   * @param logRequest - Log selection criteria for removal
   *
   * @returns Response containing removal confirmation
   */
  async removeLogsFromDataset(
    datasetId: string,
    logRequest: LogManagementRequest
  ): Promise<{ message: string; count: number }> {
    const validatedData = this.validateInput(logRequest);
    const response = await this.client.delete(
      `${DATASET_BASE_PATH}/${datasetId}/logs/delete`,
      this.prepareJsonData(validatedData)
    );
    return response as { message: string; count: number };
  }

  /**
   * List logs contained within a specific dataset.
   *
   * Retrieve a paginated list of all logs currently in the dataset.
   * This is useful for inspecting dataset contents, verifying log quality,
   * or sampling data for analysis.
   *
   * @param datasetId - The unique identifier of the dataset
   * @param options - List options including pagination
   *
   * @returns Paginated response containing:
   *     - results (Array): List of log objects, each containing:
   *       - id (string): Unique log identifier
   *       - timestamp (string): When the log was created
   *       - status (string): Log status (success, error, etc.)
   *       - model (string): Model used for the request
   *       - input (string): Input text or prompt
   *       - output (string): Generated output
   *       - metadata (object): Additional log metadata
   *     - count (number): Total number of logs in the dataset
   *     - next (string, optional): URL for next page
   *     - previous (string, optional): URL for previous page
   *
   * @throws Error if the dataset is not found or access is denied
   *
   * @example
   *     ```typescript
   *     // List first 10 logs in a dataset
   *     const logs = await client.listDatasetLogs("dataset-123", { pageSize: 10 });
   *     console.log(`Dataset contains ${logs.count} logs`);
   *     
   *     // Inspect log structure
   *     for (const log of logs.results.slice(0, 3)) {
   *       console.log(`Log ${log.id}: ${log.status} - ${log.timestamp}`);
   *     }
   *     ```
   */
  async listDatasetLogs(
    datasetId: string,
    options: { page?: number; pageSize?: number } = {}
  ): Promise<{ results: any[]; count: number; next?: string; previous?: string }> {
    const { page, pageSize } = options;
    const params: Record<string, any> = {};
    
    if (page !== undefined) params.page = page;
    if (pageSize !== undefined) params.page_size = pageSize;

    const response = await this.client.get(
      `${DATASET_BASE_PATH}/${datasetId}/logs`,
      { params }
    );
    return response as { results: any[]; count: number; next?: string; previous?: string };
  }

  /**
   * Run evaluation on a dataset using specified evaluators.
   *
   * Start an evaluation process that will analyze the logs in the dataset
   * using the specified evaluators. This is an asynchronous process that
   * generates evaluation reports which can be retrieved later.
   *
   * @param datasetId - The unique identifier of the dataset to evaluate
   * @param evaluatorSlugs - Array of evaluator slugs to use for evaluation.
   *     Use the EvaluatorAPI to list available evaluators and their slugs.
   * @param options - Additional evaluation parameters such as:
   *     - custom_prompt (string): Custom evaluation prompt
   *     - evaluation_config (object): Specific configuration for evaluators
   *
   * @returns Response containing:
   *     - message (string): Confirmation message
   *     - evaluation_id (string): Unique identifier for this evaluation run
   *     - dataset_id (string): ID of the evaluated dataset
   *     - evaluators (Array): List of evaluators being used
   *     - status (string): Initial status of the evaluation
   *
   * @throws Error if the dataset is not found, evaluators are invalid,
   *     or the evaluation cannot be started
   *
   * @example
   *     ```typescript
   *     // Run evaluation with specific evaluators
   *     const result = await client.runDatasetEvaluation(
   *       "dataset-123",
   *       ["accuracy-evaluator", "relevance-evaluator"]
   *     );
   *     console.log(`Started evaluation: ${result.evaluation_id}`);
   *     ```
   *
   * @note Evaluations run asynchronously. Use `listEvaluationReports()` to
   *     check the status and retrieve results when complete.
   */
  async runDatasetEvaluation(
    datasetId: string,
    evaluatorSlugs: string[],
    options: Record<string, any> = {}
  ): Promise<{
    message: string;
    evaluation_id: string;
    dataset_id: string;
    evaluators: string[];
    status: string;
  }> {
    const requestData = { evaluator_slugs: evaluatorSlugs, ...options };

    const response = await this.client.post(
      `${DATASET_BASE_PATH}/${datasetId}/eval-reports/create`,
      requestData
    );
    return response as {
      message: string;
      evaluation_id: string;
      dataset_id: string;
      evaluators: string[];
      status: string;
    };
  }

  /**
   * Retrieve a specific evaluation report by ID.
   *
   * @param datasetId - The unique identifier of the dataset
   * @param reportId - The unique identifier of the evaluation report
   *
   * @returns Complete evaluation report information
   */
  async getEvaluationReport(datasetId: string, reportId: string): Promise<EvalReport> {
    const response = await this.client.get(
      `${DATASET_BASE_PATH}/${datasetId}/eval-reports/${reportId}`
    );
    return response as EvalReport;
  }

  /**
   * List evaluation reports for a dataset.
   *
   * @param datasetId - The unique identifier of the dataset
   * @param options - List options including pagination and filters
   *
   * @returns Paginated list of evaluation reports
   */
  async listEvaluationReports(
    datasetId: string,
    options: {
      page?: number;
      pageSize?: number;
      [key: string]: any;
    } = {}
  ): Promise<EvalReportList> {
    const { page, pageSize, ...filters } = options;
    const params: Record<string, any> = {};
    
    if (page !== undefined) params.page = page;
    if (pageSize !== undefined) params.page_size = pageSize;
    Object.assign(params, filters);

    const response = await this.client.get(
      `${DATASET_BASE_PATH}/${datasetId}/eval-reports/list/`,
      { params }
    );
    return response as EvalReportList;
  }
}

/**
 * Create a unified dataset API client
 *
 * @param apiKey - Respan API key
 * @param baseUrl - Base URL for the API (default: RESPAN_DEFAULT_BASE_URL)
 *
 * @returns DatasetAPI client instance
 */
export function createDatasetClient(apiKey: string, baseUrl?: string): DatasetAPI {
  return new DatasetAPI({ apiKey, baseUrl });
}

// For backward compatibility, create aliases
export const SyncDatasetAPI = DatasetAPI; // Same class, just different name for clarity in imports
