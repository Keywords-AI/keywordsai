from os import getenv

# Package Config
DEBUG = getenv("RESPAN_DEBUG", "False") == "True" # Whether to print debug messages or not

# API Config
RESPAN_API_KEY = getenv("RESPAN_API_KEY")
RESPAN_BASE_URL: str = getenv("RESPAN_BASE_URL", "https://api.respan.ai/api") # slash at the end is important
RESPAN_BATCHING_ENABLED: bool = getenv("RESPAN_BATCHING_ENABLED", "True") == "True"

HIGHLIGHTED_ATTRIBUTE_KEY_SUBSTRINGS = [
    # General prompt/message fields
    "prompt",
    "message",
    "messages",
    "input",
    "content",
    # Tracing entity input/output
    "entity_input",
    "entity_output",
    # Common vendor identifiers
    "ai.",
    "openai",
    "anthropic",
    # Request bodies
    "request.body",
]

