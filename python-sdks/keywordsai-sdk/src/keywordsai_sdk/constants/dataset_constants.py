from typing import Literal

# Dataset Types
DATASET_TYPE_LLM = "llm"
DATASET_TYPE_SAMPLING = "sampling"

DatasetType = Literal[DATASET_TYPE_LLM, DATASET_TYPE_SAMPLING]

# Dataset Status
DATASET_STATUS_INITIALIZING = "initializing"
DATASET_STATUS_READY = "ready"
DATASET_STATUS_RUNNING = "running"
DATASET_STATUS_COMPLETED = "completed"
DATASET_STATUS_FAILED = "failed"
DATASET_STATUS_LOADING = "loading"

DatasetStatus = Literal[
    DATASET_STATUS_INITIALIZING,
    DATASET_STATUS_READY,
    DATASET_STATUS_RUNNING,
    DATASET_STATUS_COMPLETED,
    DATASET_STATUS_FAILED,
    DATASET_STATUS_LOADING,
]

# Eval Set LLM Run Status
DATASET_LLM_RUN_STATUS_PENDING = "pending"
DATASET_LLM_RUN_STATUS_RUNNING = "running"
DATASET_LLM_RUN_STATUS_COMPLETED = "completed"
DATASET_LLM_RUN_STATUS_FAILED = "failed"
DATASET_LLM_RUN_STATUS_CANCELLED = "cancelled"

DatasetLLMRunStatus = Literal[
    DATASET_LLM_RUN_STATUS_PENDING,
    DATASET_LLM_RUN_STATUS_RUNNING,
    DATASET_LLM_RUN_STATUS_COMPLETED,
    DATASET_LLM_RUN_STATUS_FAILED,
    DATASET_LLM_RUN_STATUS_CANCELLED,
]

# Filter types are imported from the centralized filter system
# Use the existing filter types and operators from filter_types.py and filter_mixin.py
