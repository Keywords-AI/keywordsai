import { Message } from "./promptTypes.js";
import { ToolChoiceType } from "../constants/promptConstants.js";

// Status types
export type StatusTypes = "ready" | "running" | "error" | "stopped" | "completed";

// Tool interfaces
export interface FunctionTool {
    type: "function";
    function: {
        name: string;
        description?: string;
        parameters?: Record<string, any>;
    };
}

export type ToolChoice = ToolChoiceType | { type: "function"; function: { name: string } };

// Constants
export const UTC_EPOCH = "1970-01-01T00:00:00Z";


export interface ExperimentColumnType {
    id?: string;
    model: string;
    name: string;
    temperature: number;
    max_completion_tokens: number;
    top_p: number;
    frequency_penalty: number;
    presence_penalty: number;
    tools?: FunctionTool[];
    prompt_messages?: Message[];
    reasoning_effort?: string;
    stream?: boolean;
    tool_choice?: string | ToolChoice;
    response_format?: string | Record<string, any>;
}


export interface ExperimentLLMInferenceMetrics {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
    prompt_tokens_details?: Record<string, any>;
    completion_tokens_details?: Record<string, any>;
    latency?: number;
}


export interface ExperimentResultItemType {
    id?: string;
    column_id?: string;
    output?: Record<string, any>;
    error?: string;
    ran_at?: string;
    status?: StatusTypes;
    evaluation_result?: Record<string, any>;
    llm_inference_metrics?: ExperimentLLMInferenceMetrics;
}


export interface ExperimentRowType {
    id?: string;
    input?: Record<string, any>;
    status?: StatusTypes;
    results?: (ExperimentResultItemType | null)[];
    ideal_output?: string;
}


export interface ExperimentRowV2Type {
    id?: string;
    inputs?: Record<string, any>;
    items?: Record<string, ExperimentResultItemType>;
    ideal_output?: string;
}


export interface ExperimentType {
    id?: string;
    column_count?: number;
    columns?: ExperimentColumnType[];
    created_at?: string;
    created_by?: Record<string, any> | number | string; // APIUser reference
    name: string;
    organization?: Record<string, any> | number | string; // Organization reference
    row_count?: number;
    rows?: ExperimentRowType[];
    status?: string;
    test_id?: string;
    updated_at?: string;
    updated_by?: Record<string, any> | number | string; // APIUser reference
    variables?: string[];
    variable_definitions?: Record<string, any>[];
    starred?: boolean;
    tags?: (Record<string, any> | number | string)[]; // ExperimentTag references
    description?: string;
}


// Request/Response types for API endpoints
export interface CreateExperimentRequest {
    columns: ExperimentColumnType[];
    rows?: ExperimentRowType[];
    name: string;
    description?: string;
}

export interface ListExperimentsResponse {
    experiments: ExperimentType[];
    total?: number;
    page?: number;
    page_size?: number;
}

export interface AddExperimentRowsRequest {
    rows: ExperimentRowType[];
}

export interface RemoveExperimentRowsRequest {
    rows: string[]; // List of row IDs
}

export interface UpdateExperimentRowsRequest {
    rows: ExperimentRowType[];
}

export interface AddExperimentColumnsRequest {
    columns: ExperimentColumnType[];
}

export interface RemoveExperimentColumnsRequest {
    columns: string[]; // List of column IDs
}

export interface UpdateExperimentColumnsRequest {
    columns: ExperimentColumnType[];
}

export interface RunExperimentRequest {
    columns?: ExperimentColumnType[];
}

export interface RunExperimentEvalsRequest {
    evaluator_slugs: string[];
}


// Legacy types for backward compatibility
export interface Columns {
    columns: ExperimentColumnType[];
}

export interface Rows {
    rows: ExperimentRowType[];
}

export interface EditorType {
    id: number;
    name: string;
}


export interface TestCaseType {
    description?: string;
    name?: string;
    headers?: string[];
    rows?: Record<string, string | number | null>[];
}


export interface TestsetColumnDefinition {
    field: string;
    width?: number;
    mapped_name?: string;
    is_hidden?: boolean;
    type?: "text" | "image_url" | "note";
}

export enum TestsetOperationType {
    INSERT_ROWS = "insert_rows",
    UPDATE_ROWS = "update_rows",
    DELETE_ROWS = "delete_rows",
    REORDER_ROWS = "reorder_rows",
}

export interface TestsetRowData {
    row_index?: number;
    height?: number;
    row_data?: Record<string, string | number | null | boolean>;
}

export interface TestsetRowOperationsPayload {
    testset_rows: TestsetRowData[];
}
