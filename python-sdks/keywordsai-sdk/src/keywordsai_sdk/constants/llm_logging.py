from enum import Enum

class LogMethodChoices(Enum):
    INFERENCE = "inference"  # Log from a generation api call postprocessing
    LOGGING_API = "logging_api"  # Log from a direct logging API call
    BATCH = "batch"  # Log from a batch create api call
    PYTHON_TRACING = "python_tracing"  # Log from a python tracing call
    TS_TRACING = "ts_tracing"  # Log from a typescript tracing call

class LogTypeChoices(Enum):
    TEXT = "text"
    RESPONSE = "response" # OpenAI Response API
    EMBEDDING = "embedding"
    TRANSCRIPTION = "transcription"
    SPEECH = "speech"
    WORKFLOW = "workflow"
    TASK = "task"
    TOOL = "tool" # Same as task
    AGENT = "agent" # Same as workflow
    HANDOFF = "handoff" # OpenAI Agent
    GUARDRAIL = "guardrail" # OpenAI Agent
    FUNCTION = "function" # OpenAI Agent
    CUSTOM = "custom" # OpenAI Agent
    GENERATION = "generation" # OpenAI Agent
    UNKNOWN = "unknown"