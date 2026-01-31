// Dataset Types
export const DATASET_TYPE_LLM = "llm" as const;
export const DATASET_TYPE_SAMPLING = "sampling" as const;

export type DatasetType = typeof DATASET_TYPE_LLM | typeof DATASET_TYPE_SAMPLING;

// Dataset Status
export const DATASET_STATUS_INITIALIZING = "initializing" as const;
export const DATASET_STATUS_READY = "ready" as const;
export const DATASET_STATUS_RUNNING = "running" as const;
export const DATASET_STATUS_COMPLETED = "completed" as const;
export const DATASET_STATUS_FAILED = "failed" as const;
export const DATASET_STATUS_LOADING = "loading" as const;

export type DatasetStatus = 
    | typeof DATASET_STATUS_INITIALIZING
    | typeof DATASET_STATUS_READY
    | typeof DATASET_STATUS_RUNNING
    | typeof DATASET_STATUS_COMPLETED
    | typeof DATASET_STATUS_FAILED
    | typeof DATASET_STATUS_LOADING;

// Eval Set LLM Run Status
export const DATASET_LLM_RUN_STATUS_PENDING = "pending" as const;
export const DATASET_LLM_RUN_STATUS_RUNNING = "running" as const;
export const DATASET_LLM_RUN_STATUS_COMPLETED = "completed" as const;
export const DATASET_LLM_RUN_STATUS_FAILED = "failed" as const;
export const DATASET_LLM_RUN_STATUS_CANCELLED = "cancelled" as const;

export type DatasetLLMRunStatus = 
    | typeof DATASET_LLM_RUN_STATUS_PENDING
    | typeof DATASET_LLM_RUN_STATUS_RUNNING
    | typeof DATASET_LLM_RUN_STATUS_COMPLETED
    | typeof DATASET_LLM_RUN_STATUS_FAILED
    | typeof DATASET_LLM_RUN_STATUS_CANCELLED;
