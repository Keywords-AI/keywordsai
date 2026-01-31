// Re-export all evaluator constants from respan-sdk
// Note: Add more evaluator-specific constants as they become available in the SDK

// Evaluator API paths
export const EVALUATOR_BASE_PATH = "evaluators";
export const EVALUATOR_LIST_PATH = `${EVALUATOR_BASE_PATH}/`;
export const EVALUATOR_GET_PATH = `${EVALUATOR_BASE_PATH}`;

// Evaluation paths
export const EVALUATION_BASE_PATH = "evaluations";
export const EVALUATION_RUN_PATH = `${EVALUATION_BASE_PATH}/run`;
export const EVALUATION_REPORT_PATH = `${EVALUATION_BASE_PATH}/reports`;
