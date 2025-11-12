from os import getenv

# Package Config
DEBUG = getenv("KEYWORDSAI_DEBUG", "False") == "True" # Whether to print debug messages or not

# API Config
KEYWORDSAI_API_KEY = getenv("KEYWORDSAI_API_KEY")
KEYWORDSAI_BASE_URL: str = getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api") # slash at the end is important
KEYWORDSAI_BATCHING_ENABLED: bool = getenv("KEYWORDSAI_BATCHING_ENABLED", "True") == "True"

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

