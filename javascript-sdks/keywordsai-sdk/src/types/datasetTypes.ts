import { PaginatedResponseType } from "./genericTypes.js";
import { 
    DatasetType, 
    DatasetStatus, 
    DatasetLLMRunStatus,
    DATASET_TYPE_LLM,
    DATASET_STATUS_INITIALIZING,
    DATASET_LLM_RUN_STATUS_PENDING
} from "../constants/datasetConstants.js";

// Filter types
export type FilterParamDict = Record<string, any>;

export interface Dataset {
    id: string;
    name: string;
    type?: DatasetType;
    description?: string;
    created_at: string;
    running_progress?: number;
    running_status?: DatasetLLMRunStatus;
    running_at?: string;
    updated_at: string;
    updated_by?: Record<string, any> | number | string; // APIUser reference
    organization: Record<string, any> | number | string; // Organization reference
    initial_log_filters?: FilterParamDict;
    log_ids?: string[];
    unique_organization_ids?: string[];
    timestamps?: string[];
    log_count?: number;
    evaluator?: string; // Evaluator ID
    status?: DatasetStatus;
    completed_annotation_count?: number; // Read-only field
}

export interface DatasetCreate {
    name: string;
    description?: string;
    type?: DatasetType;
    sampling?: number;
    start_time?: string;
    end_time?: string;
    initial_log_filters?: FilterParamDict;
}

export interface DatasetUpdate {
    name?: string;
    description?: string;
}

export interface DatasetList {
    results: Dataset[];
    count?: number;
    next?: string;
    previous?: string;
}

export interface LogManagementRequest {
    start_time?: string;
    end_time?: string;
    filters: FilterParamDict;
}

export interface EvalRunRequest {
    evaluator_slugs: string[];
}

export interface EvalReport {
    id: string;
    dataset_id: string;
    evaluator_slugs: string[];
    status: string;
    created_at: string;
    updated_at: string;
    results?: Record<string, any>;
}

export interface EvalReportList {
    results: EvalReport[];
    count?: number;
    next?: string;
    previous?: string;
}
