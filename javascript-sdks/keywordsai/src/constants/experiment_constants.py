"""
Keywords AI Experiment API Constants

This module defines the API endpoints and constants used for experiment operations.
"""

# Base paths
EXPERIMENT_BASE_PATH = "/api/experiments"

# Specific endpoints
EXPERIMENT_CREATION_PATH = f"{EXPERIMENT_BASE_PATH}/create"
EXPERIMENT_LIST_PATH = f"{EXPERIMENT_BASE_PATH}/list"
EXPERIMENT_GET_PATH = f"{EXPERIMENT_BASE_PATH}"
EXPERIMENT_UPDATE_PATH = f"{EXPERIMENT_BASE_PATH}"
EXPERIMENT_DELETE_PATH = f"{EXPERIMENT_BASE_PATH}"

# Row management endpoints
EXPERIMENT_ADD_ROWS_PATH = lambda experiment_id: f"{EXPERIMENT_BASE_PATH}/{experiment_id}/rows"
EXPERIMENT_REMOVE_ROWS_PATH = lambda experiment_id: f"{EXPERIMENT_BASE_PATH}/{experiment_id}/rows"
EXPERIMENT_UPDATE_ROWS_PATH = lambda experiment_id: f"{EXPERIMENT_BASE_PATH}/{experiment_id}/rows"

# Column management endpoints
EXPERIMENT_ADD_COLUMNS_PATH = lambda experiment_id: f"{EXPERIMENT_BASE_PATH}/{experiment_id}/columns"
EXPERIMENT_REMOVE_COLUMNS_PATH = lambda experiment_id: f"{EXPERIMENT_BASE_PATH}/{experiment_id}/columns"
EXPERIMENT_UPDATE_COLUMNS_PATH = lambda experiment_id: f"{EXPERIMENT_BASE_PATH}/{experiment_id}/columns"

# Experiment execution endpoints
EXPERIMENT_RUN_PATH = lambda experiment_id: f"{EXPERIMENT_BASE_PATH}/{experiment_id}/run"
EXPERIMENT_RUN_EVALS_PATH = lambda experiment_id: f"{EXPERIMENT_BASE_PATH}/{experiment_id}/run-evals"
