// Re-export all dataset constants from respan-sdk
export type {
  // Dataset Types
  DatasetType,
  // Dataset Status
  DatasetStatus,
  // Dataset LLM Run Status
  DatasetLLMRunStatus,
} from "@respan/respan-sdk";

export {
  // Dataset Type constants
  DATASET_TYPE_LLM,
  DATASET_TYPE_SAMPLING,
  // Dataset Status constants
  DATASET_STATUS_INITIALIZING,
  DATASET_STATUS_READY,
  DATASET_STATUS_RUNNING,
  DATASET_STATUS_COMPLETED,
  DATASET_STATUS_FAILED,
  DATASET_STATUS_LOADING,
  // Dataset LLM Run Status constants
  DATASET_LLM_RUN_STATUS_PENDING,
  DATASET_LLM_RUN_STATUS_RUNNING,
  DATASET_LLM_RUN_STATUS_COMPLETED,
  DATASET_LLM_RUN_STATUS_FAILED,
  DATASET_LLM_RUN_STATUS_CANCELLED,
} from "@respan/respan-sdk";

export const DATASET_BASE_PATH = "datasets";
export const DATASET_CREATION_PATH = `${DATASET_BASE_PATH}/create`;
export const DATASET_LIST_PATH = `${DATASET_BASE_PATH}/list`;
export const DATASET_GET_PATH = `${DATASET_BASE_PATH}`;
export const DATASET_UPDATE_PATH = `${DATASET_BASE_PATH}`;
export const DATASET_DELETE_PATH = `${DATASET_BASE_PATH}/delete`;
