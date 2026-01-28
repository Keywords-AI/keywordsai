from enum import Enum
from typing import Dict, Literal


class LogMethodChoices(Enum):
    INFERENCE = "inference"  # Log from a generation api call postprocessing
    LOGGING_API = "logging_api"  # Log from a direct logging API call
    BATCH = "batch"  # Log from a batch create api call
    PYTHON_TRACING = "python_tracing"  # Log from a python tracing call
    TS_TRACING = "ts_tracing"  # Log from a typescript tracing call
    TRACING_INTEGRATION = "tracing_integration"  # Log from a tracing integration call


LOG_TYPE_TEXT = "text"
LOG_TYPE_CHAT = "chat"
LOG_TYPE_COMPLETION = "completion"
LOG_TYPE_RESPONSE = "response"
LOG_TYPE_EMBEDDING = "embedding"
LOG_TYPE_TRANSCRIPTION = "transcription"
LOG_TYPE_SPEECH = "speech"
LOG_TYPE_WORKFLOW = "workflow"
LOG_TYPE_TASK = "task"
LOG_TYPE_TOOL = "tool"
LOG_TYPE_AGENT = "agent"
LOG_TYPE_HANDOFF = "handoff"
LOG_TYPE_GUARDRAIL = "guardrail"
LOG_TYPE_FUNCTION = "function"
LOG_TYPE_CUSTOM = "custom"
LOG_TYPE_GENERATION = "generation"
LOG_TYPE_UNKNOWN = "unknown"
LOG_TYPE_SCORE = "score"


class LogTypeChoices(Enum):
    TEXT = LOG_TYPE_TEXT
    CHAT = LOG_TYPE_CHAT
    COMPLETION = LOG_TYPE_COMPLETION
    RESPONSE = LOG_TYPE_RESPONSE  # OpenAI Response API
    EMBEDDING = LOG_TYPE_EMBEDDING
    TRANSCRIPTION = LOG_TYPE_TRANSCRIPTION
    SPEECH = LOG_TYPE_SPEECH
    WORKFLOW = LOG_TYPE_WORKFLOW
    TASK = LOG_TYPE_TASK
    TOOL = LOG_TYPE_TOOL  # Same as task
    AGENT = LOG_TYPE_AGENT  # Same as workflow
    HANDOFF = LOG_TYPE_HANDOFF  # OpenAI Agent
    GUARDRAIL = LOG_TYPE_GUARDRAIL  # OpenAI Agent
    FUNCTION = LOG_TYPE_FUNCTION  # OpenAI Agent
    CUSTOM = LOG_TYPE_CUSTOM  # OpenAI Agent
    GENERATION = LOG_TYPE_GENERATION  # OpenAI Agent
    UNKNOWN = LOG_TYPE_UNKNOWN
    SCORE = LOG_TYPE_SCORE


LogType = Literal[
    "text",
    "chat",
    "completion",
    "response",
    "embedding",
    "transcription",
    "speech",
    "workflow",
    "task",
    "tool",
    "agent",
    "handoff",
    "guardrail",
    "function",
    "custom",
    "generation",
    "unknown",
    "score",
]


# Maps span kind strings (from tracing frameworks) to Keywords AI log types
# Used by tracing exporters (Agno, LangFuse, etc.) to normalize span types
SPAN_KIND_TO_LOG_TYPE_MAP: Dict[str, LogType] = {
    "workflow": LOG_TYPE_WORKFLOW,
    "trace": LOG_TYPE_WORKFLOW,
    "agent": LOG_TYPE_AGENT,
    "task": LOG_TYPE_TASK,
    "step": LOG_TYPE_TASK,
    "tool": LOG_TYPE_TOOL,
    "function": LOG_TYPE_TOOL,
    "llm": LOG_TYPE_GENERATION,
    "generation": LOG_TYPE_GENERATION,
    "model": LOG_TYPE_GENERATION,
    "chat": LOG_TYPE_CHAT,
    "prompt": LOG_TYPE_GENERATION,
    "embedding": LOG_TYPE_EMBEDDING,
    "retriever": LOG_TYPE_TASK,
    "chain": LOG_TYPE_WORKFLOW,
    "reranker": LOG_TYPE_TASK,
    "guardrail": LOG_TYPE_GUARDRAIL,
    "handoff": LOG_TYPE_HANDOFF,
}


# Default model pricing per million tokens (fallback when provider doesn't return cost)
# Format: {model_name: {"prompt": cost_per_million, "completion": cost_per_million}}
MODEL_PRICING_PER_MILLION: Dict[str, Dict[str, float]] = {
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
    "gpt-4o-mini": {"prompt": 0.150, "completion": 0.600},
    "gpt-4o-2024-11-20": {"prompt": 2.50, "completion": 10.00},
    "gpt-4o-2024-08-06": {"prompt": 2.50, "completion": 10.00},
    "gpt-4o-2024-05-13": {"prompt": 5.00, "completion": 15.00},
    "gpt-4o-mini-2024-07-18": {"prompt": 0.150, "completion": 0.600},
    "gpt-4-turbo": {"prompt": 10.00, "completion": 30.00},
    "gpt-4": {"prompt": 30.00, "completion": 60.00},
    "gpt-3.5-turbo": {"prompt": 0.50, "completion": 1.50},
    "gpt-3.5-turbo-0125": {"prompt": 0.50, "completion": 1.50},
    "claude-3-5-sonnet-20241022": {"prompt": 3.00, "completion": 15.00},
    "claude-3-5-sonnet-20240620": {"prompt": 3.00, "completion": 15.00},
    "claude-3-opus-20240229": {"prompt": 15.00, "completion": 75.00},
    "claude-3-sonnet-20240229": {"prompt": 3.00, "completion": 15.00},
    "claude-3-haiku-20240307": {"prompt": 0.25, "completion": 1.25},
}
