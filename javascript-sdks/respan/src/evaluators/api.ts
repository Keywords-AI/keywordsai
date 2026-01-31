/**
 * Keywords AI Evaluator APIs
 *
 * This module provides functionality for managing evaluators, including:
 * - Listing available evaluators
 * - Getting evaluator details
 * - Running evaluations
 * - Managing evaluation reports
 */

import { BaseAPI } from "../utils/base.js";
import type {
  Evaluator,
  EvaluatorList,
} from "../types/evaluatorTypes.js";
import {
  EVALUATOR_LIST_PATH,
  EVALUATOR_GET_PATH,
} from "../constants/evaluatorConstants.js";

/**
 * Unified Evaluator API client for Keywords AI with async methods.
 * 
 * This class provides functionality for discovering and working with evaluators
 * in Keywords AI. Evaluators are pre-built or custom tools that analyze and
 * score your AI model outputs based on various criteria such as accuracy,
 * relevance, toxicity, and more.
 * 
 * Features:
 *     - List available evaluators with filtering and pagination
 *     - Get detailed information about specific evaluators
 *     - Discover evaluator capabilities and configuration options
 * 
 * Args:
 *     apiKey (string): Your Keywords AI API key. Required for authentication.
 *     baseUrl (string, optional): Base URL for the Keywords AI API.
 *         Defaults to the standard Keywords AI API endpoint.
 * 
 * Example:
 *     ```typescript
 *     import { EvaluatorAPI } from './evaluators/api.js';
 *     
 *     // Initialize the client
 *     const client = new EvaluatorAPI({ apiKey: "your-api-key" });
 *     
 *     // List all available evaluators
 *     const evaluators = await client.list();
 *     console.log(`Found ${evaluators.count} evaluators`);
 *     
 *     // Get details of a specific evaluator
 *     const evaluator = await client.get("accuracy-evaluator");
 *     console.log(`Evaluator: ${evaluator.name}`);
 *     ```
 * 
 * Note:
 *     Evaluators are read-only resources. You cannot create, update, or delete
 *     evaluators through this API. Use the web interface to manage custom evaluators.
 */
export class EvaluatorAPI extends BaseAPI<Evaluator, EvaluatorList, never, never> {
  /**
   * Initialize the Evaluator API client.
   * 
   * @param options - Configuration options
   * @param options.apiKey - Your Keywords AI API key for authentication
   * @param options.baseUrl - Custom base URL for the API. If not provided,
   *     uses the default Keywords AI API endpoint.
   */
  constructor(options: { apiKey: string; baseUrl?: string }) {
    super(options);
  }

  /**
   * List available evaluators with optional filtering and pagination.
   * 
   * Retrieve a paginated list of evaluators available in your Keywords AI
   * account. This includes both built-in evaluators and any custom evaluators
   * you've created.
   *
   * @param options - List options including:
   *     - page (number, optional): Page number for pagination (1-based)
   *     - pageSize (number, optional): Number of evaluators per page
   *     - Additional filter parameters such as:
   *       - category (string): Filter by evaluator category
   *       - name (string): Filter by evaluator name (partial match)
   *       - type (string): Filter by evaluator type ("built-in", "custom")
   *
   * @returns A paginated list containing:
   *     - results (Array): List of evaluator objects
   *     - count (number): Total number of evaluators matching filters
   *     - next (string, optional): URL for next page if available
   *     - previous (string, optional): URL for previous page if available
   *
   * @example
   *     ```typescript
   *     // List all evaluators
   *     const evaluators = await client.list();
   *     console.log(`Found ${evaluators.count} evaluators`);
   *     
   *     // List with pagination
   *     const page1 = await client.list({ page: 1, pageSize: 5 });
   *     
   *     // List with filters
   *     const accuracyEvaluators = await client.list({ category: "accuracy" });
   *     const customEvaluators = await client.list({ type: "custom" });
   *     ```
   */
  async list(options: {
    page?: number;
    pageSize?: number;
    [key: string]: any;
  } = {}): Promise<EvaluatorList> {
    const { page, pageSize, ...filters } = options;
    const params: Record<string, any> = {};
    
    if (page !== undefined) params.page = page;
    if (pageSize !== undefined) params.page_size = pageSize;
    Object.assign(params, filters);

    const response = await this.client.get(EVALUATOR_LIST_PATH, { params });
    return response as EvaluatorList;
  }

  /**
   * Retrieve detailed information about a specific evaluator.
   *
   * Fetch complete information about an evaluator, including its configuration,
   * capabilities, supported parameters, and usage examples.
   *
   * @param resourceId - The unique identifier or slug of the evaluator to retrieve.
   *     This can be either the evaluator's ID or its human-readable slug.
   *
   * @returns Complete evaluator information including:
   *     - id (string): Unique evaluator identifier
   *     - slug (string): Human-readable evaluator slug
   *     - name (string): Display name of the evaluator
   *     - description (string): Detailed description of what the evaluator does
   *     - category (string): Category the evaluator belongs to
   *     - type (string): Type of evaluator ("built-in" or "custom")
   *     - parameters (object): Configuration parameters the evaluator accepts
   *     - examples (Array): Usage examples and expected outputs
   *
   * @throws Error if the evaluator is not found or access is denied
   *
   * @example
   *     ```typescript
   *     // Get evaluator by slug (recommended)
   *     const evaluator = await client.get("accuracy-evaluator");
   *     console.log(`Evaluator: ${evaluator.name}`);
   *     console.log(`Description: ${evaluator.description}`);
   *     console.log(`Category: ${evaluator.category}`);
   *     
   *     // Get evaluator by ID
   *     const evaluator = await client.get("eval-123");
   *     ```
   */
  async get(resourceId: string): Promise<Evaluator> {
    const response = await this.client.get(`${EVALUATOR_GET_PATH}/${resourceId}`);
    return response as Evaluator;
  }

  /**
   * Create operation is not supported for evaluators.
   *
   * @param createData - Create data (ignored)
   *
   * @throws Error - Always thrown as evaluators cannot be created via API
   */
  async create(createData: never): Promise<Evaluator> {
    throw new Error(
      "Evaluators cannot be created through the API. Use the Keywords AI web interface to create custom evaluators."
    );
  }

  /**
   * Update operation is not supported for evaluators.
   *
   * @param resourceId - The evaluator ID (ignored)
   * @param updateData - Update data (ignored)
   *
   * @throws Error - Always thrown as evaluators cannot be updated via API
   */
  async update(resourceId: string, updateData: never): Promise<Evaluator> {
    throw new Error(
      "Evaluators cannot be updated through the API. Use the Keywords AI web interface to modify custom evaluators."
    );
  }

  /**
   * Delete operation is not supported for evaluators.
   *
   * @param resourceId - The evaluator ID (ignored)
   *
   * @throws Error - Always thrown as evaluators cannot be deleted via API
   */
  async delete(resourceId: string): Promise<{ success: boolean; message?: string }> {
    throw new Error(
      "Evaluators cannot be deleted through the API. Use the Keywords AI web interface to delete custom evaluators."
    );
  }
}

/**
 * Create a unified evaluator API client
 * 
 * @param apiKey - Keywords AI API key
 * @param baseUrl - Base URL for the API (default: KEYWORDS_AI_DEFAULT_BASE_URL)
 * 
 * @returns EvaluatorAPI client instance
 */
export function createEvaluatorClient(apiKey: string, baseUrl?: string): EvaluatorAPI {
  return new EvaluatorAPI({ apiKey, baseUrl });
}

// For backward compatibility, create aliases
export const SyncEvaluatorAPI = EvaluatorAPI; // Same class, just different name for clarity in imports
