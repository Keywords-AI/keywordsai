/**
 * Respan Logs APIs
 *
 * This module provides functionality for managing logs, including:
 * - Creating logs 
 * - Retrieving individual logs
 * - Listing logs with filtering and pagination
 *
 * Note: Logs do not support update or delete operations.
 */

import { BaseAPI } from "../utils/base.js";
import type {
  RespanLogParams,
  RespanFullLogParams,
  LogList,
} from "../types/logTypes.js";
import {
  LOG_CREATION_PATH,
  LOG_LIST_PATH,
  LOG_GET_PATH,
} from "../constants/logConstants.js";

/**
 * Unified Log API client for Respan with async methods.
 *
 * This class provides functionality for managing logs in Respan,
 * including creating logs, retrieving individual logs, and listing logs
 * with filtering and pagination.
 *
 * Features:
 *     - Create logs with comprehensive parameters
 *     - Retrieve individual logs by ID
 *     - List logs with filtering and pagination
 *     - Full log details in responses
 *
 * Args:
 *     apiKey (string): Your Respan API key. Required for authentication.
 *     baseUrl (string, optional): Base URL for the Respan API.
 *         Defaults to the standard Respan API endpoint.
 *
 * Example:
 *     ```typescript
 *     import { LogAPI } from './logs/api.js';
 *     import type { RespanLogParams } from './types/logTypes.js';
 *     
 *     // Initialize the client
 *     const client = new LogAPI({ apiKey: "your-api-key" });
 *     
 *     // Create a new log
 *     const logData: RespanLogParams = {
 *       model: "gpt-4",
 *       input: "Hello, world!",
 *       output: "Hi there! How can I help you today?",
 *       status_code: 200
 *     };
 *     const response = await client.create(logData);
 *     console.log(`Log created: ${response.message}`);
 *     ```
 *
 * Note:
 *     Logs do not support update or delete operations - these methods will throw
 *     errors if called.
 */
export class LogAPI extends BaseAPI<RespanFullLogParams, LogList, RespanLogParams, never> {
  /**
   * Initialize the Log API client.
   *
   * @param options - Configuration options
   * @param options.apiKey - Your Respan API key for authentication.
   *     If not provided, reads from RESPAN_API_KEY environment variable.
   * @param options.baseUrl - Custom base URL for the API. If not provided,
   *     reads from RESPAN_BASE_URL environment variable or uses default.
   */
  constructor(options: { apiKey?: string; baseUrl?: string } = {}) {
    super({
      apiKey: options.apiKey || '',
      baseUrl: options.baseUrl
    });
  }

  /**
   * Create a new log with specified parameters.
   *
   * This method creates a new log entry in Respan with the provided data.
   * The log can include various parameters like model, input/output, status,
   * and metadata.
   *
   * @param createData - Log creation parameters including:
   *     - model (string, optional): Model used for the request
   *     - input (string, optional): Input text or prompt
   *     - output (string, optional): Generated output
   *     - status_code (number, optional): HTTP status code
   *     - error_message (string, optional): Error message if any
   *     - custom_identifier (string, optional): Custom identifier for grouping
   *     - And many other optional fields for comprehensive logging
   *
   * @returns The created log data (note: actual API returns success message,
   *     but this method returns the input data for consistency with base class)
   *     
   * Note:
   *     The log create endpoint is designed for high throughput and returns
   *     only a success message, not the full log object. Use the list() or get()
   *     methods to retrieve detailed log information.
   *
   * @throws Error if the log creation fails due to invalid parameters or API errors
   *
   * @example
   *     ```typescript
   *     // Create a log for a successful API call
   *     const logData: RespanLogParams = {
   *       model: "gpt-4",
   *       input: "What is the capital of France?",
   *       output: "The capital of France is Paris.",
   *       status_code: 200,
   *       custom_identifier: "geography_qa_001",
   *       timestamp: new Date()
   *     };
   *     const response = await client.create(logData);
   *     console.log(`Log created successfully`);
   *     ```
   */
  async create(createData: RespanLogParams): Promise<RespanFullLogParams> {
    const validatedData = this.validateInput(createData);
    await this.client.post(
      LOG_CREATION_PATH,
      this.prepareJsonData(validatedData)
    );
    // Since the API only returns a success message, we return the input data
    // cast to the full log params type for consistency with the base class
    return validatedData as RespanFullLogParams;
  }

  /**
   * Create a new log and return the API response message.
   *
   * This method provides direct access to the API response for log creation,
   * which includes the success message.
   *
   * @param createData - Log creation parameters
   * @returns Response from the API containing success message
   */
  async createLog(createData: RespanLogParams): Promise<{ message: string }> {
    const validatedData = this.validateInput(createData);
    const response = await this.client.post(
      LOG_CREATION_PATH,
      this.prepareJsonData(validatedData)
    );
    return response as { message: string };
  }

  /**
   * List logs with optional filtering and pagination.
   *
   * Retrieve a paginated list of logs, optionally filtered by various criteria.
   * This method supports filtering by log properties and provides pagination
   * for handling large numbers of logs.
   *
   * @param options - List options including:
   *     - page (number, optional): Page number for pagination (1-based)
   *     - pageSize (number, optional): Number of logs per page
   *     - Additional filter parameters such as:
   *       - model (string): Filter by model name
   *       - status (string): Filter by log status
   *       - user_id (string): Filter by user ID
   *       - start_time (string): Filter logs after this timestamp (ISO format)
   *       - end_time (string): Filter logs before this timestamp (ISO format)
   *       - custom_identifier (string): Filter by custom identifier
   *       - error_bit (number): Filter by error status (0=success, 1=error)
   *
   * @returns A paginated list containing:
   *     - results (Array): List of log objects
   *     - count (number): Total number of logs matching filters
   *     - next (string, optional): URL for next page if available
   *     - previous (string, optional): URL for previous page if available
   *
   * @example
   *     ```typescript
   *     // List all logs
   *     const logs = await client.list();
   *     console.log(`Found ${logs.count} logs`);
   *     
   *     // List with pagination
   *     const page1 = await client.list({ page: 1, pageSize: 10 });
   *     
   *     // List with filters
   *     const errorLogs = await client.list({ error_bit: 1 });
   *     const recentLogs = await client.list({
   *       start_time: "2024-01-01T00:00:00Z",
   *       model: "gpt-4"
   *     });
   *     ```
   */
  async list(options: {
    page?: number;
    pageSize?: number;
    [key: string]: any;
  } = {}): Promise<LogList> {
    const { page, pageSize, ...filters } = options;
    const params: Record<string, any> = {};
    
    if (page !== undefined) params.page = page;
    if (pageSize !== undefined) params.page_size = pageSize;
    Object.assign(params, filters);

    const response = await this.client.get(LOG_LIST_PATH, { params });
    return response as LogList;
  }

  /**
   * Retrieve a specific log by its unique identifier.
   *
   * Fetch detailed information about a log including all its parameters
   * and metadata. This is useful for inspecting individual logs or
   * retrieving logs for analysis.
   *
   * @param resourceId - The unique identifier of the log to retrieve.
   *     This can be either the 'id' or 'unique_id' field from the log.
   *
   * @returns Complete log information including:
   *     - All user-provided parameters (input, output, model, etc.)
   *     - System-generated metadata (timestamps, IDs, etc.)
   *     - Authentication information (user_id, organization_id, etc.)
   *     - Status and error information
   *     - Usage statistics and performance metrics
   *
   * @throws Error if the log is not found or access is denied
   *
   * @example
   *     ```typescript
   *     // Get log details
   *     const log = await client.get("log-123");
   *     console.log(`Log '${log.id}' - Model: ${log.model}`);
   *     console.log(`Input: ${log.input}`);
   *     console.log(`Output: ${log.output}`);
   *     console.log(`Status: ${log.status_code}`);
   *     ```
   */
  async get(resourceId: string): Promise<RespanFullLogParams> {
    const response = await this.client.get(`${LOG_GET_PATH}/${resourceId}`);
    return response as RespanFullLogParams;
  }

  /**
   * Update operation is not supported for logs.
   *
   * @param resourceId - The log ID (ignored)
   * @param updateData - Update data (ignored)
   *
   * @throws Error - Always thrown as logs cannot be updated
   */
  async update(resourceId: string, updateData: never): Promise<RespanFullLogParams> {
    throw new Error(
      "Logs do not support update operations. Logs are immutable once created."
    );
  }

  /**
   * Delete operation is not supported for logs.
   *
   * @param resourceId - The log ID (ignored)
   *
   * @throws Error - Always thrown as logs cannot be deleted
   */
  async delete(resourceId: string): Promise<{ success: boolean; message?: string }> {
    throw new Error(
      "Logs do not support delete operations. Logs are immutable for audit purposes."
    );
  }
}

/**
 * Create a log API client
 *
 * @param apiKey - Respan API key (optional, reads from RESPAN_API_KEY env var if not provided)
 * @param baseUrl - Base URL for the API (optional, reads from RESPAN_BASE_URL env var or uses default)
 *
 * @returns LogAPI client instance
 */
export function createLogClient(apiKey?: string, baseUrl?: string): LogAPI {
  return new LogAPI({ apiKey, baseUrl });
}
