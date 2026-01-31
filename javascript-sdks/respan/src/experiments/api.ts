/**
 * Respan Experiment APIs
 *
 * This module provides functionality for managing experiments, including:
 * - Creating and managing experiments with columns and rows
 * - Adding/removing/updating experiment rows and columns
 * - Running experiments and evaluations
 * - Listing and retrieving experiment information
 */

import { BaseAPI } from "../utils/base.js";
import type {
  Experiment,
  ExperimentList,
  ExperimentCreate,
  ExperimentUpdate,
  AddExperimentRowsRequest,
  RemoveExperimentRowsRequest,
  UpdateExperimentRowsRequest,
  AddExperimentColumnsRequest,
  RemoveExperimentColumnsRequest,
  UpdateExperimentColumnsRequest,
  RunExperimentRequest,
  RunExperimentEvalsRequest,
} from "../types/experimentTypes.js";
import {
  EXPERIMENT_BASE_PATH,
  EXPERIMENT_CREATION_PATH,
  EXPERIMENT_LIST_PATH,
  EXPERIMENT_GET_PATH,
  EXPERIMENT_UPDATE_PATH,
  EXPERIMENT_ADD_ROWS_PATH,
  EXPERIMENT_REMOVE_ROWS_PATH,
  EXPERIMENT_UPDATE_ROWS_PATH,
  EXPERIMENT_ADD_COLUMNS_PATH,
  EXPERIMENT_REMOVE_COLUMNS_PATH,
  EXPERIMENT_UPDATE_COLUMNS_PATH,
  EXPERIMENT_RUN_PATH,
  EXPERIMENT_RUN_EVALS_PATH,
} from "../constants/experimentConstants.js";

/**
 * Unified Experiment API client for Respan with async methods.
 *
 * This class provides comprehensive functionality for managing experiments in Respan,
 * including creating experiments, managing columns and rows, running experiments,
 * and running evaluations.
 *
 * Features:
 *     - Create and manage experiments with custom configurations
 *     - Add/remove/update experiment rows (test cases)
 *     - Add/remove/update experiment columns (model configurations)
 *     - Run experiments to generate outputs
 *     - Run evaluations on experiment results
 *     - Full CRUD operations for experiment management
 *
 * Args:
 *     apiKey (string): Your Respan API key. Required for authentication.
 *     baseUrl (string, optional): Base URL for the Respan API.
 *         Defaults to the standard Respan API endpoint.
 *
 * Example:
 *     ```typescript
 *     import { ExperimentAPI } from './experiments/api.js';
 *     import type { ExperimentCreate, ExperimentColumnType, ExperimentRowType } from './types/experimentTypes.js';
 *     
 *     // Initialize the client
 *     const client = new ExperimentAPI({ apiKey: "your-api-key" });
 *     
 *     // Create a new experiment
 *     const experimentData: ExperimentCreate = {
 *       name: "My Test Experiment",
 *       description: "Experiment for testing different prompts",
 *       columns: [
 *         {
 *           model: "gpt-3.5-turbo",
 *           name: "Version A",
 *           temperature: 0.7,
 *           max_completion_tokens: 256,
 *           top_p: 1.0,
 *           frequency_penalty: 0.0,
 *           presence_penalty: 0.0,
 *           prompt_messages: [
 *             { role: "system", content: "You are a helpful assistant." },
 *             { role: "user", content: "{{user_input}}" }
 *           ]
 *         }
 *       ],
 *       rows: [
 *         {
 *           input: { user_input: "What is the weather like?" }
 *         }
 *       ]
 *     };
 *     const experiment = await client.create(experimentData);
 *     console.log(`Created experiment: ${experiment.name}`);
 *     ```
 */
export class ExperimentAPI extends BaseAPI<Experiment, ExperimentList, ExperimentCreate, ExperimentUpdate> {
  /**
   * Initialize the Experiment API client.
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
   * Create a new experiment with specified parameters.
   *
   * This method creates a new experiment in Respan with the provided configuration.
   * The experiment includes columns (model configurations) and rows (test cases).
   *
   * @param createData - Experiment creation parameters including:
   *     - name (string): Name of the experiment
   *     - description (string): Description of the experiment's purpose
   *     - columns (Array): List of column configurations
   *     - rows (Array, optional): List of test cases
   *
   * @returns The created experiment object containing:
   *     - id (string): Unique identifier for the experiment
   *     - name (string): Experiment name
   *     - description (string): Experiment description
   *     - columns (Array): Column configurations
   *     - rows (Array): Test cases
   *     - status (string): Current status of the experiment
   *     - created_at (string): Creation timestamp
   *
   * @throws Error if the experiment creation fails due to invalid parameters or API errors
   *
   * @example
   *     ```typescript
   *     const experimentData: ExperimentCreate = {
   *       name: "Prompt Comparison Test",
   *       description: "Compare different system prompts",
   *       columns: [
   *         {
   *           model: "gpt-3.5-turbo",
   *           name: "Formal Assistant",
   *           temperature: 0.3,
   *           max_completion_tokens: 200,
   *           top_p: 1.0,
   *           frequency_penalty: 0.0,
   *           presence_penalty: 0.0,
   *           prompt_messages: [
   *             { role: "system", content: "You are a formal, professional assistant." }
   *           ]
   *         }
   *       ]
   *     };
   *     const experiment = await client.create(experimentData);
   *     ```
   */
  async create(createData: ExperimentCreate): Promise<Experiment> {
    const validatedData = this.validateInput(createData);
    const response = await this.client.post(
      EXPERIMENT_CREATION_PATH,
      this.prepareJsonData(validatedData)
    );
    return response as Experiment;
  }

  /**
   * List experiments with optional filtering and pagination.
   *
   * Retrieve a paginated list of experiments, optionally filtered by various criteria.
   * This method supports filtering by experiment properties and provides pagination
   * for handling large numbers of experiments.
   *
   * @param options - List options including:
   *     - page (number, optional): Page number for pagination (1-based)
   *     - pageSize (number, optional): Number of experiments per page
   *     - Additional filter parameters such as:
   *       - name (string): Filter by experiment name (partial match)
   *       - status (string): Filter by experiment status
   *       - created_after (string): Filter experiments created after this date
   *       - created_before (string): Filter experiments created before this date
   *
   * @returns A paginated list containing:
   *     - experiments (Array): List of experiment objects
   *     - total (number): Total number of experiments matching filters
   *     - page (number): Current page number
   *     - page_size (number): Number of items per page
   *
   * @example
   *     ```typescript
   *     // List all experiments
   *     const experiments = await client.list();
   *     console.log(`Found ${experiments.total} experiments`);
   *     
   *     // List with pagination
   *     const page1 = await client.list({ page: 1, pageSize: 10 });
   *     
   *     // List with filters
   *     const recentExperiments = await client.list({
   *       created_after: "2024-01-01T00:00:00Z"
   *     });
   *     ```
   */
  async list(options: {
    page?: number;
    pageSize?: number;
    [key: string]: any;
  } = {}): Promise<ExperimentList> {
    const { page, pageSize, ...filters } = options;
    const params: Record<string, any> = {};
    
    if (page !== undefined) params.page = page;
    if (pageSize !== undefined) params.page_size = pageSize;
    Object.assign(params, filters);

    const response = await this.client.get(EXPERIMENT_LIST_PATH, { params });
    return response as ExperimentList;
  }

  /**
   * Retrieve a specific experiment by its unique identifier.
   *
   * Fetch detailed information about an experiment including its current status,
   * columns, rows, and results. This is useful for checking experiment progress
   * and retrieving results.
   *
   * @param resourceId - The unique identifier of the experiment to retrieve.
   *     This is typically returned when creating an experiment or listing experiments.
   *
   * @returns Complete experiment information including:
   *     - id (string): Unique experiment identifier
   *     - name (string): Experiment name
   *     - description (string): Experiment description
   *     - columns (Array): Column configurations
   *     - rows (Array): Test cases with results
   *     - status (string): Current status ("ready", "running", "completed", etc.)
   *     - created_at (string): Creation timestamp
   *     - updated_at (string): Last update timestamp
   *
   * @throws Error if the experiment is not found or access is denied
   *
   * @example
   *     ```typescript
   *     // Get experiment details
   *     const experiment = await client.get("experiment-123");
   *     console.log(`Experiment '${experiment.name}' status: ${experiment.status}`);
   *     
   *     // Check if experiment has results
   *     for (const row of experiment.rows) {
   *       if (row.results) {
   *         console.log(`Row ${row.id} has ${row.results.length} results`);
   *       }
   *     }
   *     ```
   */
  async get(resourceId: string): Promise<Experiment> {
    const response = await this.client.get(`${EXPERIMENT_GET_PATH}/${resourceId}`);
    return response as Experiment;
  }

  /**
   * Update an existing experiment's metadata.
   *
   * Modify experiment properties such as name and description. Note that core
   * experiment structure (columns and rows) should be updated using the specific
   * row and column management methods.
   *
   * @param resourceId - The unique identifier of the experiment to update
   * @param updateData - Update parameters containing:
   *     - name (string, optional): New name for the experiment
   *     - description (string, optional): New description for the experiment
   *
   * @returns The updated experiment object with new properties applied
   *
   * @throws Error if the experiment is not found, update fails, or
   *     invalid parameters are provided
   *
   * @example
   *     ```typescript
   *     // Update experiment name and description
   *     const updateData: ExperimentUpdate = {
   *       name: "Updated Experiment Name",
   *       description: "Updated description with more details"
   *     };
   *     const updatedExperiment = await client.update("experiment-123", updateData);
   *     console.log(`Updated experiment: ${updatedExperiment.name}`);
   *     ```
   */
  async update(resourceId: string, updateData: ExperimentUpdate): Promise<Experiment> {
    const validatedData = this.validateInput(updateData);
    const response = await this.client.patch(
      `${EXPERIMENT_UPDATE_PATH}/${resourceId}`,
      this.prepareJsonData(validatedData)
    );
    return response as Experiment;
  }

  /**
   * Delete an experiment permanently.
   *
   * WARNING: This operation is irreversible. The experiment and all its associated
   * data will be permanently deleted.
   *
   * @param resourceId - The unique identifier of the experiment to delete
   *
   * @returns API response confirming deletion, typically containing:
   *     - success (boolean): Whether deletion was successful
   *     - message (string): Confirmation message
   *
   * @throws Error if the experiment is not found or deletion fails
   *
   * @example
   *     ```typescript
   *     // Delete an experiment (be careful!)
   *     const response = await client.delete("experiment-123");
   *     console.log(response.message); // "Experiment deleted successfully"
   *     ```
   *
   * @note Consider exporting important results before deletion as this operation cannot be undone.
   */
  async delete(resourceId: string): Promise<{ success: boolean; message?: string }> {
    const response = await this.client.delete(`${EXPERIMENT_BASE_PATH}/${resourceId}`);
    return response as { success: boolean; message?: string };
  }

  // Row management methods

  /**
   * Add rows to an existing experiment.
   *
   * This method allows you to add new test cases to an experiment. Each row
   * represents a different input scenario that will be tested against all columns.
   *
   * @param experimentId - The unique identifier of the target experiment
   * @param rowsRequest - Request containing:
   *     - rows (Array): List of rows to add, each containing:
   *       - input (object): Input variables for the test case
   *       - ideal_output (string, optional): Expected output for evaluation
   *
   * @returns Response containing:
   *     - message (string): Success message
   *     - added_rows (number): Number of rows added
   *     - experiment_id (string): ID of the updated experiment
   *
   * @throws Error if the experiment is not found or request is invalid
   *
   * @example
   *     ```typescript
   *     const rowsRequest: AddExperimentRowsRequest = {
   *       rows: [
   *         {
   *           input: { user_question: "What is machine learning?" }
   *         },
   *         {
   *           input: { user_question: "Explain neural networks" },
   *           ideal_output: "A neural network is..."
   *         }
   *       ]
   *     };
   *     const result = await client.addRows("experiment-123", rowsRequest);
   *     console.log(`Added ${result.added_rows} rows to experiment`);
   *     ```
   */
  async addRows(
    experimentId: string,
    rowsRequest: AddExperimentRowsRequest
  ): Promise<{ message: string; added_rows: number; experiment_id: string }> {
    const validatedData = this.validateInput(rowsRequest);
    const response = await this.client.post(
      EXPERIMENT_ADD_ROWS_PATH(experimentId),
      this.prepareJsonData(validatedData)
    );
    return response as { message: string; added_rows: number; experiment_id: string };
  }

  /**
   * Remove rows from an experiment.
   *
   * Remove specific test cases from an experiment by their IDs.
   *
   * @param experimentId - The unique identifier of the target experiment
   * @param rowsRequest - Request containing:
   *     - rows (Array): List of row IDs to remove
   *
   * @returns Response containing:
   *     - message (string): Success message
   *     - removed_rows (number): Number of rows removed
   *
   * @example
   *     ```typescript
   *     const removeRequest: RemoveExperimentRowsRequest = {
   *       rows: ["row-id-1", "row-id-2"]
   *     };
   *     const result = await client.removeRows("experiment-123", removeRequest);
   *     ```
   */
  async removeRows(
    experimentId: string,
    rowsRequest: RemoveExperimentRowsRequest
  ): Promise<{ message: string; removed_rows: number }> {
    const validatedData = this.validateInput(rowsRequest);
    const response = await this.client.delete(
      EXPERIMENT_REMOVE_ROWS_PATH(experimentId),
      this.prepareJsonData(validatedData)
    );
    return response as { message: string; removed_rows: number };
  }

  /**
   * Update existing rows in an experiment.
   *
   * Modify the input data or ideal outputs for existing test cases.
   *
   * @param experimentId - The unique identifier of the target experiment
   * @param rowsRequest - Request containing:
   *     - rows (Array): List of rows to update with their IDs
   *
   * @returns Response containing:
   *     - message (string): Success message
   *     - updated_rows (number): Number of rows updated
   *
   * @example
   *     ```typescript
   *     const updateRequest: UpdateExperimentRowsRequest = {
   *       rows: [
   *         {
   *           id: "existing-row-id",
   *           input: { user_question: "Updated question" }
   *         }
   *       ]
   *     };
   *     const result = await client.updateRows("experiment-123", updateRequest);
   *     ```
   */
  async updateRows(
    experimentId: string,
    rowsRequest: UpdateExperimentRowsRequest
  ): Promise<{ message: string; updated_rows: number }> {
    const validatedData = this.validateInput(rowsRequest);
    const response = await this.client.patch(
      EXPERIMENT_UPDATE_ROWS_PATH(experimentId),
      this.prepareJsonData(validatedData)
    );
    return response as { message: string; updated_rows: number };
  }

  // Column management methods

  /**
   * Add columns to an existing experiment.
   *
   * Add new model configurations to test against existing rows.
   *
   * @param experimentId - The unique identifier of the target experiment
   * @param columnsRequest - Request containing:
   *     - columns (Array): List of column configurations to add
   *
   * @returns Response containing:
   *     - message (string): Success message
   *     - added_columns (number): Number of columns added
   *
   * @example
   *     ```typescript
   *     const columnsRequest: AddExperimentColumnsRequest = {
   *       columns: [
   *         {
   *           model: "gpt-4",
   *           name: "GPT-4 Version",
   *           temperature: 0.5,
   *           max_completion_tokens: 300,
   *           top_p: 1.0,
   *           frequency_penalty: 0.0,
   *           presence_penalty: 0.0,
   *           prompt_messages: [
   *             { role: "system", content: "You are an expert assistant." }
   *           ]
   *         }
   *       ]
   *     };
   *     const result = await client.addColumns("experiment-123", columnsRequest);
   *     ```
   */
  async addColumns(
    experimentId: string,
    columnsRequest: AddExperimentColumnsRequest
  ): Promise<{ message: string; added_columns: number }> {
    const validatedData = this.validateInput(columnsRequest);
    const response = await this.client.post(
      EXPERIMENT_ADD_COLUMNS_PATH(experimentId),
      this.prepareJsonData(validatedData)
    );
    return response as { message: string; added_columns: number };
  }

  /**
   * Remove columns from an experiment.
   *
   * Remove specific model configurations from an experiment by their IDs.
   *
   * @param experimentId - The unique identifier of the target experiment
   * @param columnsRequest - Request containing:
   *     - columns (Array): List of column IDs to remove
   *
   * @returns Response containing:
   *     - message (string): Success message
   *     - removed_columns (number): Number of columns removed
   *
   * @example
   *     ```typescript
   *     const removeRequest: RemoveExperimentColumnsRequest = {
   *       columns: ["column-id-1", "column-id-2"]
   *     };
   *     const result = await client.removeColumns("experiment-123", removeRequest);
   *     ```
   */
  async removeColumns(
    experimentId: string,
    columnsRequest: RemoveExperimentColumnsRequest
  ): Promise<{ message: string; removed_columns: number }> {
    const validatedData = this.validateInput(columnsRequest);
    const response = await this.client.delete(
      EXPERIMENT_REMOVE_COLUMNS_PATH(experimentId),
      this.prepareJsonData(validatedData)
    );
    return response as { message: string; removed_columns: number };
  }

  /**
   * Update existing columns in an experiment.
   *
   * Modify the configuration of existing model columns.
   *
   * @param experimentId - The unique identifier of the target experiment
   * @param columnsRequest - Request containing:
   *     - columns (Array): List of columns to update
   *
   * @returns Response containing:
   *     - message (string): Success message
   *     - updated_columns (number): Number of columns updated
   *
   * @example
   *     ```typescript
   *     const updateRequest: UpdateExperimentColumnsRequest = {
   *       columns: [
   *         {
   *           id: "existing-column-id",
   *           model: "gpt-4",
   *           name: "Updated GPT-4 Config",
   *           temperature: 0.3,
   *           max_completion_tokens: 400,
   *           top_p: 1.0,
   *           frequency_penalty: 0.0,
   *           presence_penalty: 0.0
   *         }
   *       ]
   *     };
   *     const result = await client.updateColumns("experiment-123", updateRequest);
   *     ```
   */
  async updateColumns(
    experimentId: string,
    columnsRequest: UpdateExperimentColumnsRequest
  ): Promise<{ message: string; updated_columns: number }> {
    const validatedData = this.validateInput(columnsRequest);
    const response = await this.client.patch(
      EXPERIMENT_UPDATE_COLUMNS_PATH(experimentId),
      this.prepareJsonData(validatedData)
    );
    return response as { message: string; updated_columns: number };
  }

  // Experiment execution methods

  /**
   * Run an experiment to generate outputs.
   *
   * Execute the experiment by running all rows against all columns (or specified columns)
   * to generate model outputs. This is an asynchronous process.
   *
   * @param experimentId - The unique identifier of the experiment to run
   * @param runRequest - Optional request containing:
   *     - columns (Array, optional): Specific columns to run.
   *       If not provided, runs all columns in the experiment.
   *
   * @returns Response containing:
   *     - message (string): Confirmation message
   *     - experiment_id (string): ID of the experiment being run
   *     - status (string): Status of the run ("started", "running", etc.)
   *     - run_id (string, optional): Unique identifier for this run
   *
   * @throws Error if the experiment is not found or cannot be run
   *
   * @example
   *     ```typescript
   *     // Run entire experiment
   *     const result = await client.runExperiment("experiment-123");
   *     console.log(`Started experiment run: ${result.status}`);
   *     
   *     // Run specific columns only
   *     const runRequest: RunExperimentRequest = {
   *       columns: [specificColumnConfig]
   *     };
   *     const result = await client.runExperiment("experiment-123", runRequest);
   *     ```
   *
   * @note Experiment runs are asynchronous. Use `get()` to check the status
   *     and retrieve results when complete.
   */
  async runExperiment(
    experimentId: string,
    runRequest?: RunExperimentRequest
  ): Promise<{
    message: string;
    experiment_id: string;
    status: string;
    run_id?: string;
  }> {
    const requestData = runRequest ? this.prepareJsonData(this.validateInput(runRequest)) : {};

    const response = await this.client.post(
      EXPERIMENT_RUN_PATH(experimentId),
      requestData
    );
    return response as {
      message: string;
      experiment_id: string;
      status: string;
      run_id?: string;
    };
  }

  /**
   * Run evaluations on experiment results.
   *
   * Execute evaluators on the experiment outputs to generate evaluation scores
   * and metrics. This requires that the experiment has been run and has outputs.
   *
   * @param experimentId - The unique identifier of the experiment to evaluate
   * @param evalsRequest - Request containing:
   *     - evaluator_slugs (Array): List of evaluator slugs to use
   *
   * @returns Response containing:
   *     - message (string): Confirmation message
   *     - experiment_id (string): ID of the experiment being evaluated
   *     - evaluators (Array): List of evaluators being used
   *     - status (string): Status of the evaluation
   *
   * @throws Error if the experiment is not found, has no outputs,
   *     or evaluators are invalid
   *
   * @example
   *     ```typescript
   *     const evalsRequest: RunExperimentEvalsRequest = {
   *       evaluator_slugs: ["is_english", "relevance_score"]
   *     };
   *     const result = await client.runExperimentEvals("experiment-123", evalsRequest);
   *     console.log(`Started evaluation with ${evalsRequest.evaluator_slugs.length} evaluators`);
   *     ```
   *
   * @note Evaluations run asynchronously. Use `get()` to check the status
   *     and retrieve results when complete.
   */
  async runExperimentEvals(
    experimentId: string,
    evalsRequest: RunExperimentEvalsRequest
  ): Promise<{
    message: string;
    experiment_id: string;
    evaluators: string[];
    status: string;
  }> {
    const validatedData = this.validateInput(evalsRequest);
    const response = await this.client.post(
      EXPERIMENT_RUN_EVALS_PATH(experimentId),
      this.prepareJsonData(validatedData)
    );
    return response as {
      message: string;
      experiment_id: string;
      evaluators: string[];
      status: string;
    };
  }
}

/**
 * Create a unified experiment API client
 *
 * @param apiKey - Respan API key
 * @param baseUrl - Base URL for the API (default: RESPAN_DEFAULT_BASE_URL)
 *
 * @returns ExperimentAPI client instance
 */
export function createExperimentClient(apiKey: string, baseUrl?: string): ExperimentAPI {
  return new ExperimentAPI({ apiKey, baseUrl });
}
