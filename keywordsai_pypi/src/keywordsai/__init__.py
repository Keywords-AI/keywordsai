from os import getenv
DEBUG = getenv("KEYWORDS_AI_DEBUG", "False") == "True" # Whether to print debug messages or not
SINGLETON = getenv("KEYWORDS_AI_IS_SINGLETON", "True") == "True" # Whether KeywordsAI instance should be a singleton or not