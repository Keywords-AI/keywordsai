from os import getenv

# Package Config
DEBUG = getenv("KEYWORDSAI_DEBUG", "False") == "True" # Whether to print debug messages or not

# API Config
KEYWORDSAI_API_KEY = getenv("KEYWORDSAI_API_KEY")
KEYWORDSAI_BASE_URL: str = getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api") # slash at the end is important
KEYWORDSAI_DISABLE_BATCH: bool = getenv("KEYWORDSAI_DISABLE_BATCH", "False") == "True"

