# Re-export all evaluator constants from respan-sdk
# Note: Add more evaluator-specific constants as they become available in the SDK

# Evaluator API paths
EVALUATOR_BASE_PATH = "evaluators"
EVALUATOR_LIST_PATH = f"{EVALUATOR_BASE_PATH}/"
EVALUATOR_GET_PATH = f"{EVALUATOR_BASE_PATH}"

# Evaluation paths
EVALUATION_BASE_PATH = "evaluations"
EVALUATION_RUN_PATH = f"{EVALUATION_BASE_PATH}/run"
EVALUATION_REPORT_PATH = f"{EVALUATION_BASE_PATH}/reports"

__all__ = [
    # Evaluator Paths
    "EVALUATOR_BASE_PATH",
    "EVALUATOR_LIST_PATH", 
    "EVALUATOR_GET_PATH",
    # Evaluation Paths
    "EVALUATION_BASE_PATH",
    "EVALUATION_RUN_PATH",
    "EVALUATION_REPORT_PATH",
]
