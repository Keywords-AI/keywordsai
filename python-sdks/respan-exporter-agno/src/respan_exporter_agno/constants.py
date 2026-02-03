"""Constants for Respan Agno exporter."""
from typing import Dict

DEFAULT_ENDPOINT = "https://api.respan.ai/api/v1/traces/ingest"

LOG_TYPE_MAP: Dict[str, str] = {
    "workflow": "workflow",
    "trace": "workflow",
    "agent": "agent",
    "task": "task",
    "step": "task",
    "tool": "tool",
    "function": "tool",
    "llm": "generation",
    "generation": "generation",
    "model": "generation",
    "chat": "chat",
    "prompt": "prompt",
}

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
}
