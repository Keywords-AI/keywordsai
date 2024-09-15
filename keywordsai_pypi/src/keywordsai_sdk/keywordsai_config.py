from os import getenv

# Package Config
DEBUG = getenv("KEYWORDSAI_DEBUG", "False") == "True" # Whether to print debug messages or not
SINGLETON = getenv("KEYWORDSAI_IS_SINGLETON", "True") == "True" # Whether KeywordsAI instance should be a singleton or not

# API Config
KEYWORDSAI_API_KEY = getenv("KEYWORDSAI_API_KEY")
KEYWORDSAI_BASE_URL = getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api") # slash at the end is important
KEYWORDSAI_LOGGING_PATH = getenv("KEYWORDSAI_LOGGING_PATH", "/request-logs/create")

KEYWORDSAI_NUM_THREADS = int(getenv("KEYWORDSAI_NUM_THREADS", 1))
KEYWORDSAI_QUEUE_TIMEOUT = int(getenv("KEYWORDSAI_QUEUE_TIMEOUT", 0.5))
KEYWORDSAI_BATCH_SIZE = int(getenv("KEYWORDSAI_BATCH_SIZE", 1))
MAX_PAYLOAD_SIZE = 100_000_000  # 100MB

