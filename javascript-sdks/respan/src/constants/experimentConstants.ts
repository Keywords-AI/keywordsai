/**
 * Keywords AI Experiment API Constants
 *
 * This module defines the API endpoints and constants used for experiment operations.
 */

// Base paths
export const EXPERIMENT_BASE_PATH = "/api/experiments";

// Specific endpoints
export const EXPERIMENT_CREATION_PATH = `${EXPERIMENT_BASE_PATH}/create`;
export const EXPERIMENT_LIST_PATH = `${EXPERIMENT_BASE_PATH}/list`;
export const EXPERIMENT_GET_PATH = `${EXPERIMENT_BASE_PATH}`;
export const EXPERIMENT_UPDATE_PATH = `${EXPERIMENT_BASE_PATH}`;
export const EXPERIMENT_DELETE_PATH = `${EXPERIMENT_BASE_PATH}`;

// Row management endpoints
export const EXPERIMENT_ADD_ROWS_PATH = (experimentId: string) => 
  `${EXPERIMENT_BASE_PATH}/${experimentId}/rows`;
export const EXPERIMENT_REMOVE_ROWS_PATH = (experimentId: string) => 
  `${EXPERIMENT_BASE_PATH}/${experimentId}/rows`;
export const EXPERIMENT_UPDATE_ROWS_PATH = (experimentId: string) => 
  `${EXPERIMENT_BASE_PATH}/${experimentId}/rows`;

// Column management endpoints
export const EXPERIMENT_ADD_COLUMNS_PATH = (experimentId: string) => 
  `${EXPERIMENT_BASE_PATH}/${experimentId}/columns`;
export const EXPERIMENT_REMOVE_COLUMNS_PATH = (experimentId: string) => 
  `${EXPERIMENT_BASE_PATH}/${experimentId}/columns`;
export const EXPERIMENT_UPDATE_COLUMNS_PATH = (experimentId: string) => 
  `${EXPERIMENT_BASE_PATH}/${experimentId}/columns`;

// Experiment execution endpoints
export const EXPERIMENT_RUN_PATH = (experimentId: string) => 
  `${EXPERIMENT_BASE_PATH}/${experimentId}/run`;
export const EXPERIMENT_RUN_EVALS_PATH = (experimentId: string) => 
  `${EXPERIMENT_BASE_PATH}/${experimentId}/run-evals`;
